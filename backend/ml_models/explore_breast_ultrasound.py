"""
探索乳腺超声数据集
"""
import os
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# 数据集路径
DATA_ROOT = Path(__file__).parent.parent.parent / "data" / "archive (2)" / "Dataset_BUSI_with_GT"

def explore_dataset():
    """探索数据集结构和统计信息"""
    
    categories = ['normal', 'benign', 'malignant']
    
    print("=" * 50)
    print("📊 数据集统计")
    print("=" * 50)
    
    total_images = 0
    for category in categories:
        category_path = DATA_ROOT / category
        
        if not category_path.exists():
            print(f"⚠️  警告: 文件夹不存在 {category_path}")
            continue
        
        # 获取所有图像文件
        images = list(category_path.glob("*.png"))
        # 过滤掉mask文件（通常带_mask后缀）
        images = [img for img in images if '_mask' not in img.name]
        
        count = len(images)
        total_images += count
        
        print(f"{category.upper():12s}: {count:4d} 张图像")
    
    print("-" * 50)
    print(f"{'总计':12s}: {total_images:4d} 张图像")
    print("=" * 50)
    
    # 显示样例图像
    if total_images > 0:
        visualize_samples()
        analyze_image_sizes()
    else:
        print("❌ 未找到图像数据，请检查数据集路径！")

def visualize_samples():
    """可视化每类的样例图像"""
    
    try:
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式后端
        
        categories = ['normal', 'benign', 'malignant']
        category_labels = {
            'normal': '正常',
            'benign': '良性',
            'malignant': '恶性'
        }
        
        # 设置中文字体
        try:
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
        except:
            pass
        
        fig, axes = plt.subplots(3, 3, figsize=(12, 12))
        fig.suptitle('Breast Ultrasound Image Samples', fontsize=16)
        
        for row, category in enumerate(categories):
            category_path = DATA_ROOT / category
            
            if not category_path.exists():
                continue
                
            images = [img for img in category_path.glob("*.png") if '_mask' not in img.name]
            
            if len(images) == 0:
                continue
            
            # 随机选3张图
            samples = np.random.choice(images, min(3, len(images)), replace=False)
            
            for col, img_path in enumerate(samples):
                try:
                    img = Image.open(img_path)
                    axes[row, col].imshow(img, cmap='gray')
                    axes[row, col].set_title(f"{category_labels.get(category, category)}", fontsize=10)
                    axes[row, col].axis('off')
                except Exception as e:
                    print(f"⚠️  无法加载图像 {img_path.name}: {e}")
        
        plt.tight_layout()
        
        # 保存到当前目录
        output_path = Path(__file__).parent / 'dataset_samples.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\n✅ 样本图像已保存到: {output_path}")
        plt.close()
        
    except Exception as e:
        print(f"⚠️  可视化失败: {e}")
        print("   这不影响后续训练，可以继续。")

def analyze_image_sizes():
    """分析图像尺寸分布"""
    
    categories = ['normal', 'benign', 'malignant']
    sizes = []
    
    for category in categories:
        category_path = DATA_ROOT / category
        
        if not category_path.exists():
            continue
            
        images = [img for img in category_path.glob("*.png") if '_mask' not in img.name]
        
        for img_path in images[:50]:  # 采样50张
            try:
                img = Image.open(img_path)
                sizes.append(img.size)
            except:
                continue
    
    if len(sizes) == 0:
        print("\n⚠️  未能读取图像尺寸信息")
        return
    
    widths = [s[0] for s in sizes]
    heights = [s[1] for s in sizes]
    
    print(f"\n📐 图像尺寸分析（采样{len(sizes)}张）")
    print(f"宽度范围: {min(widths)} - {max(widths)} 像素")
    print(f"高度范围: {min(heights)} - {max(heights)} 像素")
    
    # 找出最常见的尺寸
    from collections import Counter
    size_counter = Counter(sizes)
    most_common = size_counter.most_common(1)
    if most_common:
        print(f"最常见尺寸: {most_common[0][0]} (出现{most_common[0][1]}次)")

if __name__ == "__main__":
    print("\n🔍 开始探索乳腺超声数据集...\n")
    explore_dataset()
    print("\n✨ 数据探索完成！")
    print("\n💡 下一步: 运行 prepare_dataset.py 来划分训练集、验证集、测试集")

