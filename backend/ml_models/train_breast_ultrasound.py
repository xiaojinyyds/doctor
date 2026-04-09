"""
乳腺超声图像识别模型训练
使用深度学习（CNN）进行图像分类：正常、良性、恶性
"""
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

# 设置随机种子
torch.manual_seed(42)
np.random.seed(42)

class BreastUltrasoundDataset(Dataset):
    """乳腺超声图像数据集"""
    
    def __init__(self, data_dir, split='train', transform=None):
        """
        Args:
            data_dir: 数据根目录
            split: 'train', 'val', 或 'test'
            transform: 图像变换
        """
        self.data_dir = Path(data_dir) / split
        self.transform = transform
        self.classes = ['normal', 'benign', 'malignant']
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        
        # 加载所有图像路径
        self.samples = []
        for class_name in self.classes:
            class_dir = self.data_dir / class_name
            if class_dir.exists():
                for img_path in class_dir.glob('*.png'):
                    self.samples.append((img_path, self.class_to_idx[class_name]))
        
        print(f"  {split.upper():5s} 数据集: {len(self.samples)} 张图像")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        # 读取图像
        image = Image.open(img_path).convert('RGB')
        
        # 应用变换
        if self.transform:
            image = self.transform(image)
        
        return image, label


class BreastCancerCNN(nn.Module):
    """乳腺癌图像分类CNN模型"""
    
    def __init__(self, num_classes=3, pretrained=True):
        """
        Args:
            num_classes: 分类数量（正常、良性、恶性）
            pretrained: 是否使用预训练权重
        """
        super(BreastCancerCNN, self).__init__()
        
        # 使用预训练的ResNet18作为基础模型
        self.model = models.resnet18(pretrained=pretrained)
        
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


class BreastUltrasoundTrainer:
    """乳腺超声图像识别训练器"""
    
    def __init__(self, data_dir, model_dir='saved_models'):
        """
        Args:
            data_dir: 准备好的数据目录
            model_dir: 模型保存目录
        """
        self.data_dir = Path(data_dir)
        self.model_dir = Path(__file__).parent / model_dir
        self.model_dir.mkdir(exist_ok=True)
        
        # 检查数据目录
        if not self.data_dir.exists():
            raise FileNotFoundError(f"数据目录不存在: {self.data_dir}")
        
        # 设置设备
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🖥️  使用设备: {self.device}")
        
        # 类别名称
        self.classes = ['normal', 'benign', 'malignant']
        self.class_names_cn = ['正常', '良性', '恶性']
        
        # 训练历史
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
    
    def get_transforms(self):
        """获取数据增强和预处理变换"""
        
        # 训练集数据增强
        train_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # 验证集和测试集（无增强）
        val_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        return train_transform, val_transform
    
    def prepare_data(self, batch_size=16):
        """准备数据加载器"""
        
        print("\n📂 加载数据集...")
        
        train_transform, val_transform = self.get_transforms()
        
        # 创建数据集
        train_dataset = BreastUltrasoundDataset(
            self.data_dir, 
            split='train', 
            transform=train_transform
        )
        val_dataset = BreastUltrasoundDataset(
            self.data_dir, 
            split='val', 
            transform=val_transform
        )
        test_dataset = BreastUltrasoundDataset(
            self.data_dir, 
            split='test', 
            transform=val_transform
        )
        
        # 创建数据加载器
        self.train_loader = DataLoader(
            train_dataset, 
            batch_size=batch_size, 
            shuffle=True, 
            num_workers=0
        )
        self.val_loader = DataLoader(
            val_dataset, 
            batch_size=batch_size, 
            shuffle=False, 
            num_workers=0
        )
        self.test_loader = DataLoader(
            test_dataset, 
            batch_size=batch_size, 
            shuffle=False, 
            num_workers=0
        )
        
        print(f"✅ 数据加载完成")
        print(f"   训练批次: {len(self.train_loader)}")
        print(f"   验证批次: {len(self.val_loader)}")
        print(f"   测试批次: {len(self.test_loader)}")
    
    def train_epoch(self, model, criterion, optimizer):
        """训练一个epoch"""
        
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in self.train_loader:
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # 前向传播
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # 反向传播
            loss.backward()
            optimizer.step()
            
            # 统计
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        epoch_loss = running_loss / len(self.train_loader)
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate(self, model, criterion):
        """验证模型"""
        
        model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in self.val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        epoch_loss = running_loss / len(self.val_loader)
        epoch_acc = 100 * correct / total
        
        return epoch_loss, epoch_acc
    
    def train(self, epochs=30, batch_size=16, learning_rate=0.001):
        """训练模型"""
        
        print("\n" + "=" * 70)
        print("🚀 开始训练乳腺超声图像识别模型")
        print("=" * 70)
        
        # 准备数据
        self.prepare_data(batch_size)
        
        # 创建模型
        print(f"\n🏗️  构建模型...")
        model = BreastCancerCNN(num_classes=len(self.classes), pretrained=True)
        model = model.to(self.device)
        print(f"✅ 模型构建完成（使用预训练ResNet18）")
        
        # 定义损失函数和优化器
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5, verbose=True
        )
        
        # 训练循环
        print(f"\n🔄 开始训练 (总共 {epochs} 轮)")
        print("-" * 70)
        
        best_val_acc = 0.0
        patience = 10
        patience_counter = 0
        
        for epoch in range(epochs):
            # 训练
            train_loss, train_acc = self.train_epoch(model, criterion, optimizer)
            
            # 验证
            val_loss, val_acc = self.validate(model, criterion)
            
            # 学习率调整
            scheduler.step(val_loss)
            
            # 记录历史
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            
            # 打印进度
            print(f"Epoch [{epoch+1:2d}/{epochs}] "
                  f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | "
                  f"Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}%")
            
            # 保存最佳模型
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                patience_counter = 0
                
                # 保存模型
                model_path = self.model_dir / 'breast_ultrasound_best.pth'
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_acc': val_acc,
                    'classes': self.classes
                }, model_path)
                print(f"   ✨ 保存最佳模型 (验证准确率: {val_acc:.2f}%)")
            else:
                patience_counter += 1
            
            # 早停
            if patience_counter >= patience:
                print(f"\n⏹️  早停：验证准确率在 {patience} 轮内没有改善")
                break
        
        print("\n" + "=" * 70)
        print(f"✅ 训练完成！最佳验证准确率: {best_val_acc:.2f}%")
        print("=" * 70)
        
        # 加载最佳模型进行测试
        self.model = model
        self.load_best_model()
        
        # 在测试集上评估
        self.evaluate()
        
        # 保存训练历史
        self.save_training_history()
        
        # 绘制训练曲线
        self.plot_training_curves()
        
        return self.model
    
    def load_best_model(self):
        """加载最佳模型"""
        
        model_path = self.model_dir / 'breast_ultrasound_best.pth'
        if model_path.exists():
            checkpoint = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            print(f"\n✅ 已加载最佳模型")
    
    def evaluate(self):
        """在测试集上评估模型"""
        
        print("\n" + "=" * 70)
        print("📊 在测试集上评估模型")
        print("=" * 70)
        
        self.model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for images, labels in self.test_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                _, predicted = torch.max(outputs.data, 1)
                
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        # 计算准确率
        accuracy = 100 * np.sum(np.array(all_preds) == np.array(all_labels)) / len(all_labels)
        print(f"\n🎯 测试集准确率: {accuracy:.2f}%\n")
        
        # 分类报告
        print("📋 分类报告:")
        print(classification_report(
            all_labels, 
            all_preds, 
            target_names=self.class_names_cn,
            digits=4
        ))
        
        # 混淆矩阵
        self.plot_confusion_matrix(all_labels, all_preds)
        
        # 保存评估结果
        eval_results = {
            'test_accuracy': float(accuracy),
            'classification_report': classification_report(
                all_labels, all_preds, 
                target_names=self.class_names_cn,
                output_dict=True
            )
        }
        
        results_path = self.model_dir / 'evaluation_results.json'
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(eval_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 评估结果已保存到: {results_path}")
    
    def plot_confusion_matrix(self, y_true, y_pred):
        """绘制混淆矩阵"""
        
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm, 
            annot=True, 
            fmt='d', 
            cmap='Blues',
            xticklabels=self.class_names_cn,
            yticklabels=self.class_names_cn,
            cbar_kws={'label': '数量'}
        )
        plt.title('混淆矩阵', fontsize=16, pad=20)
        plt.xlabel('预测类别', fontsize=12)
        plt.ylabel('真实类别', fontsize=12)
        plt.tight_layout()
        
        # 保存图像
        cm_path = self.model_dir / 'confusion_matrix.png'
        plt.savefig(cm_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 混淆矩阵已保存到: {cm_path}")
    
    def plot_training_curves(self):
        """绘制训练曲线"""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        epochs = range(1, len(self.history['train_loss']) + 1)
        
        # 损失曲线
        ax1.plot(epochs, self.history['train_loss'], 'b-', label='训练集', linewidth=2)
        ax1.plot(epochs, self.history['val_loss'], 'r-', label='验证集', linewidth=2)
        ax1.set_title('训练和验证损失', fontsize=14)
        ax1.set_xlabel('Epoch', fontsize=12)
        ax1.set_ylabel('Loss', fontsize=12)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # 准确率曲线
        ax2.plot(epochs, self.history['train_acc'], 'b-', label='训练集', linewidth=2)
        ax2.plot(epochs, self.history['val_acc'], 'r-', label='验证集', linewidth=2)
        ax2.set_title('训练和验证准确率', fontsize=14)
        ax2.set_xlabel('Epoch', fontsize=12)
        ax2.set_ylabel('Accuracy (%)', fontsize=12)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图像
        curves_path = self.model_dir / 'training_curves.png'
        plt.savefig(curves_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ 训练曲线已保存到: {curves_path}")
    
    def save_training_history(self):
        """保存训练历史"""
        
        history_path = self.model_dir / 'training_history.json'
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)
        
        print(f"✅ 训练历史已保存到: {history_path}")


def main():
    """主函数"""
    
    print("\n" + "🏥" * 35)
    print("       乳腺超声图像识别模型训练系统")
    print("🏥" * 35)
    
    # 数据目录
    data_dir = Path(__file__).parent / 'breast_ultrasound_data'
    
    # 检查数据是否准备好
    if not data_dir.exists():
        print("\n❌ 错误：数据集未准备")
        print(f"   数据目录不存在: {data_dir}")
        print("\n💡 请先运行以下命令准备数据集：")
        print("   python prepare_dataset.py")
        return
    
    # 创建训练器
    try:
        trainer = BreastUltrasoundTrainer(data_dir)
        
        # 开始训练
        model = trainer.train(
            epochs=30,
            batch_size=16,
            learning_rate=0.001
        )
        
        print("\n" + "🎉" * 35)
        print("       训练完成！模型已保存")
        print("🎉" * 35)
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误: {e}")
        print("\n💡 请确保已运行 prepare_dataset.py 准备数据集")
    except Exception as e:
        print(f"\n❌ 训练过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

