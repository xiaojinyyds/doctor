"""
准备数据集：划分训练集、验证集、测试集
"""
import os
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split
import json

# 路径配置
DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "archive (2)" / "Dataset_BUSI_with_GT"
PREPARED_DATA = Path(__file__).parent / "breast_ultrasound_data"

def prepare_dataset(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
    """
    划分数据集
    
    Args:
        train_ratio: 训练集比例 (70%)
        val_ratio: 验证集比例 (15%)
        test_ratio: 测试集比例 (15%)
    """
    
    print("🚀 开始准备数据集...")
    print("=" * 60)
    
    # 检查数据集是否存在
    if not DATA_ROOT.exists():
        print(f"❌ 错误：数据集路径不存在")
        print(f"   路径：{DATA_ROOT}")
        return False
    
    # 创建目标文件夹
    for split in ['train', 'val', 'test']:
        for category in ['normal', 'benign', 'malignant']:
            (PREPARED_DATA / split / category).mkdir(parents=True, exist_ok=True)
    
    dataset_info = {
        'total': 0,
        'train': {},
        'val': {},
        'test': {}
    }
    
    # 处理每个类别
    for category in ['normal', 'benign', 'malignant']:
        print(f"\n📁 处理类别: {category}")
        
        # 获取所有图像（排除mask）
        category_path = DATA_ROOT / category
        
        if not category_path.exists():
            print(f"   ⚠️  警告：文件夹不存在 {category_path}")
            continue
        
        images = [img for img in category_path.glob("*.png") if '_mask' not in img.name]
        
        if len(images) == 0:
            print(f"   ⚠️  警告：未找到图像")
            continue
        
        print(f"   找到 {len(images)} 张图像")
        
        # 第一次划分：分出测试集
        train_val, test = train_test_split(
            images, 
            test_size=test_ratio, 
            random_state=42
        )
        
        # 第二次划分：从剩余数据分出验证集
        train, val = train_test_split(
            train_val,
            test_size=val_ratio / (train_ratio + val_ratio),
            random_state=42
        )
        
        # 复制文件
        for split_name, split_data in [('train', train), ('val', val), ('test', test)]:
            count = 0
            for img_path in split_data:
                dest = PREPARED_DATA / split_name / category / img_path.name
                shutil.copy2(img_path, dest)
                count += 1
            
            dataset_info[split_name][category] = count
            print(f"   {split_name:5s}: {count:4d} 张")
        
        dataset_info['total'] += len(images)
    
    # 保存数据集信息
    with open(PREPARED_DATA / 'dataset_info.json', 'w', encoding='utf-8') as f:
        json.dump(dataset_info, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("✅ 数据集准备完成！")
    print(f"📁 保存位置: {PREPARED_DATA}")
    print("=" * 60)
    print(f"\n📊 统计信息：")
    print(f"总计:   {dataset_info['total']:4d} 张图像")
    print(f"训练集: {sum(dataset_info['train'].values()):4d} 张 ({train_ratio*100:.0f}%)")
    print(f"验证集: {sum(dataset_info['val'].values()):4d} 张 ({val_ratio*100:.0f}%)")
    print(f"测试集: {sum(dataset_info['test'].values()):4d} 张 ({test_ratio*100:.0f}%)")
    
    print("\n💡 下一步：运行 train_breast_ultrasound.py 开始训练模型")
    
    return True

if __name__ == "__main__":
    success = prepare_dataset()
    if not success:
        print("\n❌ 数据集准备失败，请检查数据路径")

