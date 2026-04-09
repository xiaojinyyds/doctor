"""
乳腺超声图像识别服务
"""
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class BreastCancerCNN(nn.Module):
    """乳腺癌图像分类CNN模型"""
    
    def __init__(self, num_classes=3):
        super(BreastCancerCNN, self).__init__()
        
        # 使用预训练的ResNet18作为基础模型
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


class ImageRecognitionService:
    """图像识别服务"""
    
    def __init__(self):
        """初始化服务"""
        self.model_path = Path(__file__).parent.parent.parent / 'ml_models' / 'saved_models' / 'breast_ultrasound_best.pth'
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 类别映射
        self.classes = ['normal', 'benign', 'malignant']
        self.class_names_cn = {
            'normal': '正常',
            'benign': '良性肿瘤',
            'malignant': '恶性肿瘤'
        }
        
        # 风险等级
        self.risk_levels = {
            'normal': '低风险',
            'benign': '中风险',
            'malignant': '高风险'
        }
        
        # 建议
        self.recommendations = {
            'normal': '图像显示正常，建议继续定期体检。',
            'benign': '检测到良性病变，建议咨询医生进行进一步检查和随访。',
            'malignant': '检测到疑似恶性病变，强烈建议尽快就医进行专业诊断。'
        }
        
        # 模型和转换器
        self.model = None
        self.transform = None
        
        # 加载模型
        self._load_model()
    
    def _load_model(self):
        """加载训练好的模型"""
        try:
            if not self.model_path.exists():
                logger.error(f"模型文件不存在: {self.model_path}")
                raise FileNotFoundError(f"模型文件不存在: {self.model_path}")
            
            # 创建模型
            self.model = BreastCancerCNN(num_classes=len(self.classes))
            
            # 加载权重
            checkpoint = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            
            # 设置为评估模式
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # 定义图像预处理
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            logger.info("图像识别模型加载成功")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        预处理图像
        
        Args:
            image: PIL图像对象
            
        Returns:
            预处理后的张量
        """
        # 转换为RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 应用变换
        image_tensor = self.transform(image)
        
        # 添加batch维度
        image_tensor = image_tensor.unsqueeze(0)
        
        return image_tensor
    
    def predict(self, image: Image.Image) -> Dict:
        """
        对单张图像进行预测
        
        Args:
            image: PIL图像对象
            
        Returns:
            预测结果字典，包含类别、概率、风险等级等信息
        """
        try:
            # 预处理图像
            image_tensor = self.preprocess_image(image)
            image_tensor = image_tensor.to(self.device)
            
            # 预测
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted_idx = torch.max(probabilities, 1)
            
            # 获取预测结果
            predicted_class = self.classes[predicted_idx.item()]
            confidence_value = confidence.item()
            
            # 获取所有类别的概率
            all_probabilities = probabilities[0].cpu().numpy()
            class_probabilities = {
                self.class_names_cn[cls]: float(prob) 
                for cls, prob in zip(self.classes, all_probabilities)
            }
            
            # 构建结果
            result = {
                'success': True,
                'predicted_class': predicted_class,
                'predicted_class_cn': self.class_names_cn[predicted_class],
                'confidence': float(confidence_value),
                'risk_level': self.risk_levels[predicted_class],
                'recommendation': self.recommendations[predicted_class],
                'class_probabilities': class_probabilities,
                'all_classes': {
                    cls: {
                        'name_cn': self.class_names_cn[cls],
                        'probability': float(prob),
                        'percentage': f"{float(prob)*100:.2f}%"
                    }
                    for cls, prob in zip(self.classes, all_probabilities)
                }
            }
            
            logger.info(f"预测完成: {predicted_class} (置信度: {confidence_value:.4f})")
            
            return result
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '图像识别失败，请稍后重试'
            }
    
    def predict_from_file(self, image_path: str) -> Dict:
        """
        从文件路径预测
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            预测结果字典
        """
        try:
            # 打开图像
            image = Image.open(image_path)
            
            # 预测
            return self.predict(image)
            
        except Exception as e:
            logger.error(f"从文件预测失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '无法读取图像文件'
            }
    
    def predict_from_bytes(self, image_bytes: bytes) -> Dict:
        """
        从字节数据预测
        
        Args:
            image_bytes: 图像字节数据
            
        Returns:
            预测结果字典
        """
        try:
            from io import BytesIO
            
            # 从字节创建图像
            image = Image.open(BytesIO(image_bytes))
            
            # 预测
            return self.predict(image)
            
        except Exception as e:
            logger.error(f"从字节数据预测失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '无法解析图像数据'
            }
    
    def get_model_info(self) -> Dict:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            'model_name': '乳腺超声图像识别模型',
            'model_type': 'ResNet18',
            'num_classes': len(self.classes),
            'classes': self.classes,
            'class_names_cn': self.class_names_cn,
            'device': str(self.device),
            'model_path': str(self.model_path),
            'status': 'loaded' if self.model is not None else 'not_loaded'
        }


# 创建全局服务实例
_service_instance = None

def get_image_recognition_service() -> ImageRecognitionService:
    """
    获取图像识别服务单例
    
    Returns:
        ImageRecognitionService实例
    """
    global _service_instance
    
    if _service_instance is None:
        _service_instance = ImageRecognitionService()
    
    return _service_instance


# 测试函数
def test_service():
    """测试服务"""
    print("=" * 60)
    print("测试图像识别服务")
    print("=" * 60)
    
    # 获取服务
    service = get_image_recognition_service()
    
    # 打印模型信息
    info = service.get_model_info()
    print("\n模型信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 测试预测（如果有测试图像）
    test_image_dir = Path(__file__).parent.parent.parent / 'ml_models' / 'breast_ultrasound_data' / 'test'
    
    if test_image_dir.exists():
        # 获取第一张测试图像
        for category in ['normal', 'benign', 'malignant']:
            category_dir = test_image_dir / category
            if category_dir.exists():
                images = list(category_dir.glob('*.png'))
                if images:
                    test_image = images[0]
                    print(f"\n测试图像: {test_image.name} (真实类别: {category})")
                    
                    result = service.predict_from_file(str(test_image))
                    
                    if result['success']:
                        print(f"预测类别: {result['predicted_class_cn']}")
                        print(f"置信度: {result['confidence']:.4f}")
                        print(f"风险等级: {result['risk_level']}")
                        print(f"建议: {result['recommendation']}")
                        print("\n各类别概率:")
                        for cls_info in result['all_classes'].values():
                            print(f"  {cls_info['name_cn']}: {cls_info['percentage']}")
                    else:
                        print(f"预测失败: {result['message']}")
                    
                    break
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_service()

