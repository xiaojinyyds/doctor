"""
医学影像分类服务 - 乳腺超声图像分类
"""
import torch
from torchvision import transforms, models
from PIL import Image
import torch.nn as nn
from pathlib import Path
import io
from typing import Dict, Optional, Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)

# 模型路径
MODEL_PATH = Path(__file__).parent.parent.parent / "ml_models" / "saved_models" / "breast_ultrasound_best.pth"


class BreastCancerCNN(nn.Module):
    """乳腺癌图像分类CNN模型（与训练时结构一致）"""
    
    def __init__(self, num_classes=3):
        super(BreastCancerCNN, self).__init__()
        
        # 使用ResNet18作为基础模型
        self.model = models.resnet18(pretrained=False)
        
        # 修改最后的全连接层
        num_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)


class ImageClassifier:
    """医学影像分类器"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        # 类别映射（与训练时的顺序一致：normal=0, benign=1, malignant=2）
        self.class_names = ['正常', '良性肿瘤', '恶性肿瘤']
        self.class_to_idx = {'normal': 0, 'benign': 1, 'malignant': 2}
        self.idx_to_class = {0: 'normal', 1: 'benign', 2: 'malignant'}
        self.transform = self._get_transform()
        
        # 尝试加载模型
        self._load_model()
    
    def _get_transform(self):
        """获取图像预处理流程"""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def _load_model(self):
        """加载训练好的模型"""
        try:
            print(f"🔍 检查模型路径: {MODEL_PATH}")
            print(f"   文件存在: {MODEL_PATH.exists()}")
            
            if not MODEL_PATH.exists():
                logger.warning(f"模型文件不存在: {MODEL_PATH}")
                logger.info("影像分析功能将返回模拟结果，请先训练模型")
                print("⚠️  模型文件不存在，将使用模拟结果")
                return
            
            print(f"   文件大小: {MODEL_PATH.stat().st_size / (1024*1024):.2f} MB")
            print(f"📦 加载checkpoint...")
            
            # 加载checkpoint
            checkpoint = torch.load(MODEL_PATH, map_location=self.device)
            print(f"✅ Checkpoint加载成功")
            
            print(f"🏗️  创建模型结构（使用BreastCancerCNN包装类）...")
            # 使用与训练时相同的包装类
            self.model = BreastCancerCNN(num_classes=3)
            
            print(f"📥 加载模型权重...")
            # 加载权重
            self.model.load_state_dict(checkpoint['model_state_dict'])
            
            self.model = self.model.to(self.device)
            self.model.eval()
            
            print(f"✅ 影像分类模型加载成功！")
            logger.info("✅ 影像分类模型加载成功")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            logger.error(f"❌ 模型加载失败: {e}")
            import traceback
            traceback.print_exc()
            self.model = None
    
    def predict(self, image_bytes: bytes, generate_annotation: bool = True) -> Dict:
        """
        预测图像类别
        
        Args:
            image_bytes: 图像字节流
            
        Returns:
            {
                'prediction': '良性肿瘤',
                'confidence': 0.923,
                'probabilities': {
                    '正常': 0.032,
                    '良性肿瘤': 0.923,
                    '恶性肿瘤': 0.045
                },
                'recommendation': '建议6个月后复查'
            }
        """
        # 如果模型未加载，返回模拟结果
        if self.model is None:
            logger.warning("模型未加载，返回模拟结果")
            return self._mock_prediction()
        
        try:
            # 加载图像
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # 预处理
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # 推理
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)[0]
                confidence, predicted_idx = probabilities.max(0)
            
            # 结果
            predicted_class = self.idx_to_class[predicted_idx.item()]
            confidence_value = confidence.item()
            
            # 概率分布
            prob_dict = {
                self.class_names[i]: float(probabilities[i])
                for i in range(len(self.class_names))
            }
            
            # 生成建议
            recommendation = self._generate_recommendation(
                predicted_class, confidence_value
            )
            
            logger.info(f"预测完成: {self.class_names[predicted_idx.item()]} (置信度: {confidence_value:.3f})")
            
            result = {
                'prediction': self.class_names[predicted_idx.item()],
                'prediction_en': predicted_class,
                'confidence': float(confidence_value),
                'probabilities': prob_dict,
                'recommendation': recommendation
            }
            
            # 如果需要生成标注图
            if generate_annotation and predicted_class != 'normal':
                try:
                    annotated_image_bytes = self._generate_annotated_image(
                        image_bytes, image_tensor, predicted_class, confidence_value
                    )
                    result['annotated_image_bytes'] = annotated_image_bytes
                    logger.info("✅ 已生成病灶标注图")
                except Exception as e:
                    logger.warning(f"生成标注图失败: {e}")
            
            return result
        
        except Exception as e:
            logger.error(f"预测失败: {e}")
            raise RuntimeError(f"图像分析失败: {str(e)}")
    
    def _generate_annotated_image(
        self, 
        image_bytes: bytes, 
        image_tensor: torch.Tensor,
        predicted_class: str,
        confidence: float
    ) -> bytes:
        """
        生成带病灶标注的图像
        
        Args:
            image_bytes: 原始图像字节
            image_tensor: 预处理后的图像张量
            predicted_class: 预测类别
            confidence: 置信度
            
        Returns:
            标注后的图像字节
        """
        from app.utils.gradcam import generate_gradcam, annotate_image_with_lesions
        
        try:
            # 生成Grad-CAM热力图
            cam = generate_gradcam(
                model=self.model,
                image_bytes=image_bytes,
                transform=self.transform,
                device=self.device,
                output_size=(224, 224)
            )
            
            if cam is None:
                logger.warning("Grad-CAM生成失败")
                return image_bytes
            
            # 在图像上标注病灶位置
            annotated_bytes = annotate_image_with_lesions(
                image_bytes=image_bytes,
                heatmap=cam,
                predicted_class=predicted_class,
                confidence=confidence,
                threshold=0.7  # 更高阈值，更精确的标注
            )
            
            return annotated_bytes
            
        except Exception as e:
            logger.error(f"生成标注图失败: {e}")
            import traceback
            traceback.print_exc()
            return image_bytes
    
    def _generate_recommendation(self, prediction: str, confidence: float) -> str:
        """生成医疗建议"""
        
        if prediction == 'normal':
            if confidence > 0.9:
                return "未发现异常，建议每年常规体检。"
            else:
                return "初步未见明显异常，建议3-6个月后复查。"
        
        elif prediction == 'benign':
            if confidence > 0.9:
                return "检测到良性肿瘤，建议就医进一步确认，定期随访观察。"
            else:
                return "疑似良性病变，建议尽快就医进行详细检查。"
        
        else:  # malignant
            if confidence > 0.8:
                return "⚠️ 检测到恶性肿瘤风险，强烈建议立即就医进行全面检查和活检。"
            else:
                return "检测到可疑病灶，建议立即就医进行进一步检查（如活检）。"
    
    def _mock_prediction(self) -> Dict:
        """模拟预测结果（模型未训练时使用）"""
        import random
        
        # 随机生成一个结果用于演示
        predictions = [
            {
                'prediction': '正常',
                'prediction_en': 'normal',
                'confidence': 0.92,
                'probabilities': {
                    '良性肿瘤': 0.05,
                    '恶性肿瘤': 0.03,
                    '正常': 0.92
                },
                'recommendation': '未发现异常，建议每年常规体检。',
                'is_mock': True
            },
            {
                'prediction': '良性肿瘤',
                'prediction_en': 'benign',
                'confidence': 0.88,
                'probabilities': {
                    '良性肿瘤': 0.88,
                    '恶性肿瘤': 0.07,
                    '正常': 0.05
                },
                'recommendation': '检测到良性肿瘤，建议就医进一步确认，定期随访观察。',
                'is_mock': True
            }
        ]
        
        result = random.choice(predictions)
        logger.info("⚠️ 返回模拟结果（模型未训练）")
        return result


# 全局实例
image_classifier = ImageClassifier()

