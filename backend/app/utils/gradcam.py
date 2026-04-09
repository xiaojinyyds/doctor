"""
Grad-CAM (Gradient-weighted Class Activation Mapping)
用于生成深度学习模型的可视化热力图并标注病灶位置
"""
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
from typing import Optional, Tuple, List
import cv2
import logging

logger = logging.getLogger(__name__)


class GradCAM:
    """Grad-CAM可视化类"""
    
    def __init__(self, model, target_layer):
        """
        Args:
            model: PyTorch模型
            target_layer: 目标层（用于提取特征）
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # 注册钩子
        self._register_hooks()
    
    def _register_hooks(self):
        """注册前向和反向钩子"""
        def forward_hook(module, input, output):
            self.activations = output.detach()
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()
        
        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_backward_hook(backward_hook)
    
    def generate(self, input_image: torch.Tensor, target_class: Optional[int] = None) -> np.ndarray:
        """
        生成Grad-CAM热力图
        
        Args:
            input_image: 输入图像张量 (1, C, H, W)
            target_class: 目标类别索引（None则使用预测类别）
            
        Returns:
            热力图数组
        """
        # 前向传播
        output = self.model(input_image)
        
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        # 清零梯度
        self.model.zero_grad()
        
        # 反向传播
        class_score = output[0, target_class]
        class_score.backward()
        
        # 计算权重
        gradients = self.gradients[0]  # (C, H, W)
        activations = self.activations[0]  # (C, H, W)
        
        # 全局平均池化得到权重
        weights = torch.mean(gradients, dim=(1, 2))  # (C,)
        
        # 加权求和
        cam = torch.zeros(activations.shape[1:], dtype=torch.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
        
        # ReLU
        cam = F.relu(cam)
        
        # 归一化到0-1
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        
        return cam.cpu().numpy()


def generate_gradcam(
    model,
    image_bytes: bytes,
    transform,
    device: torch.device,
    output_size: Tuple[int, int] = (224, 224)
) -> Optional[np.ndarray]:
    """
    生成Grad-CAM热力图
    
    Args:
        model: 训练好的模型
        image_bytes: 图像字节数据
        transform: 图像预处理变换
        device: 计算设备
        output_size: 输出尺寸
        
    Returns:
        热力图数组（如果生成失败则返回None）
    """
    try:
        # 加载图像
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        original_size = image.size
        
        # 预处理
        image_tensor = transform(image).unsqueeze(0).to(device)
        
        # 找到目标层（ResNet18的最后一个卷积层）
        if hasattr(model, 'model'):
            # 如果是包装类
            target_layer = model.model.layer4[-1]
        else:
            target_layer = model.layer4[-1]
        
        # 创建Grad-CAM
        gradcam = GradCAM(model, target_layer)
        
        # 生成热力图
        cam = gradcam.generate(image_tensor)
        
        # 调整大小到原始图像尺寸
        from scipy.ndimage import zoom
        cam_resized = zoom(cam, (output_size[1] / cam.shape[0], output_size[0] / cam.shape[1]))
        
        return cam_resized
        
    except Exception as e:
        logger.error(f"生成Grad-CAM失败: {e}")
        return None


def overlay_heatmap_on_image(
    image_bytes: bytes,
    heatmap: np.ndarray,
    alpha: float = 0.4,
    colormap: str = 'jet'
) -> bytes:
    """
    将热力图叠加到原始图像上
    
    Args:
        image_bytes: 原始图像字节
        heatmap: 热力图数组
        alpha: 透明度
        colormap: 颜色映射
        
    Returns:
        叠加后的图像字节
    """
    try:
        # 加载原始图像
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image)
        
        # 调整热力图大小
        heatmap_resized = cv2.resize(heatmap, (image.width, image.height))
        
        # 应用颜色映射
        heatmap_colored = cv2.applyColorMap(
            np.uint8(255 * heatmap_resized), 
            cv2.COLORMAP_JET
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # 叠加
        overlayed = cv2.addWeighted(image_np, 1 - alpha, heatmap_colored, alpha, 0)
        
        # 转换回PIL图像
        result_image = Image.fromarray(overlayed)
        
        # 转换为字节
        output = io.BytesIO()
        result_image.save(output, format='PNG')
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"叠加热力图失败: {e}")
        return image_bytes


def detect_lesion_regions(
    heatmap: np.ndarray,
    threshold: float = 0.7  # 提高阈值到0.7，更精确
) -> List[Tuple[int, int, int, int]]:
    """
    从热力图中检测病灶区域
    
    Args:
        heatmap: 热力图数组 (H, W)，值范围0-1
        threshold: 阈值，高于此值的区域被认为是病灶
        
    Returns:
        病灶区域列表 [(x, y, w, h), ...]
    """
    try:
        # 二值化 - 使用更高阈值
        binary_mask = (heatmap > threshold).astype(np.uint8) * 255
        
        # 形态学操作，去除噪声，使用更小的kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 提取边界框，只保留最显著的区域
        regions = []
        contour_areas = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            # 过滤太小的区域（噪声）
            if area > 200:  # 提高最小面积阈值
                x, y, w, h = cv2.boundingRect(contour)
                regions.append((x, y, w, h))
                contour_areas.append(area)
        
        # 如果检测到多个区域，只保留最大的2-3个
        if len(regions) > 3:
            # 按面积排序，保留最大的3个
            sorted_indices = sorted(range(len(contour_areas)), key=lambda i: contour_areas[i], reverse=True)
            regions = [regions[i] for i in sorted_indices[:3]]
        
        return regions
        
    except Exception as e:
        logger.error(f"检测病灶区域失败: {e}")
        return []


def annotate_image_with_lesions(
    image_bytes: bytes,
    heatmap: np.ndarray,
    predicted_class: str,
    confidence: float,
    threshold: float = 0.6
) -> bytes:
    """
    在图像上标注病灶位置
    
    Args:
        image_bytes: 原始图像字节
        heatmap: 热力图数组
        predicted_class: 预测类别
        confidence: 置信度
        threshold: 病灶检测阈值
        
    Returns:
        标注后的图像字节
    """
    try:
        # 加载原始图像
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        width, height = image.size
        
        # 调整热力图大小
        heatmap_resized = cv2.resize(heatmap, (width, height))
        
        # 检测病灶区域
        regions = detect_lesion_regions(heatmap_resized, threshold)
        
        # 如果没有检测到病灶（正常情况）或置信度太低，直接返回原图
        if len(regions) == 0 or predicted_class == 'normal':
            return image_bytes
        
        # 在图像上绘制标注
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体
        try:
            # 尝试加载常见的TrueType字体
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            try:
                # 备用字体
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 16)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 14)
            except:
                # 使用默认字体
                font = None
                font_small = None
        
        # 根据预测类别选择颜色
        color_map = {
            'benign': '#FFA500',      # 橙色 - 良性
            'malignant': '#FF0000',   # 红色 - 恶性
            'normal': '#00FF00'       # 绿色 - 正常（一般不会标注）
        }
        color = color_map.get(predicted_class, '#FF0000')
        
        # 绘制所有病灶区域
        for i, (x, y, w, h) in enumerate(regions):
            # 计算中心和半径 - 更精确的尺寸
            center_x = x + w // 2
            center_y = y + h // 2
            # 使用边界框较小边的40%作为半径，紧贴病灶
            radius = int(min(w, h) * 0.3)
            
            # 绘制2层圆圈（醒目但不夸张）
            for offset in [2, 0]:
                draw.ellipse(
                    [
                        center_x - radius - offset,
                        center_y - radius - offset,
                        center_x + radius + offset,
                        center_y + radius + offset
                    ],
                    outline=color,
                    width=4
                )
            
            # 添加箭头指示（可选，指向病灶中心）
            # 绘制小十字标记病灶中心
            cross_size = 8
            draw.line(
                [(center_x - cross_size, center_y), (center_x + cross_size, center_y)],
                fill=color,
                width=2
            )
            draw.line(
                [(center_x, center_y - cross_size), (center_x, center_y + cross_size)],
                fill=color,
                width=2
            )
            
            # 添加标签（放在圆圈上方）
            label = f"{'良性' if predicted_class == 'benign' else '恶性'} #{i+1}"
            label_x = center_x - 30
            label_y = center_y - radius - 30
            
            # 确保标签不超出图像边界
            if label_y < 10:
                label_y = center_y + radius + 10
            
            # 绘制文字背景（使用估算大小或实际字体大小）
            if font and hasattr(font, 'getbbox'):
                # 如果字体支持getbbox，使用它
                text_bbox = draw.textbbox((label_x, label_y), label, font=font)
            else:
                # 否则估算文字大小
                text_width = len(label) * 10  # 中文字符约10-12像素
                text_height = 20
                text_bbox = (label_x, label_y, label_x + text_width, label_y + text_height)
            
            draw.rectangle(
                [text_bbox[0] - 5, text_bbox[1] - 2, text_bbox[2] + 5, text_bbox[3] + 2],
                fill=color
            )
            draw.text((label_x, label_y), label, fill='white', font=font)
        
        # 添加分析信息（右下角）
        info_text = f"{predicted_class.upper()} | {confidence*100:.1f}%"
        info_x = width - 200
        info_y = height - 40
        
        # 信息框背景（使用估算大小或实际字体大小）
        if font_small and hasattr(font_small, 'getbbox'):
            info_bbox = draw.textbbox((info_x, info_y), info_text, font=font_small)
        else:
            # 估算英文字符大小
            info_width = len(info_text) * 8  # 英文字符约8像素
            info_height = 18
            info_bbox = (info_x, info_y, info_x + info_width, info_y + info_height)
        
        draw.rectangle(
            [info_bbox[0] - 10, info_bbox[1] - 5, info_bbox[2] + 10, info_bbox[3] + 5],
            fill=(0, 0, 0)  # 黑色背景
        )
        draw.text((info_x, info_y), info_text, fill='white', font=font_small)
        
        # 转换为字节
        output = io.BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"标注图像失败: {e}")
        import traceback
        traceback.print_exc()
        return image_bytes

