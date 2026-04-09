"""
数据集分析脚本
分析三个癌症数据集的特征、分布和可用性
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class DatasetAnalyzer:
    """数据集分析器"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.datasets = {}
        
    def load_datasets(self):
        """加载所有数据集"""
        print("=" * 60)
        print("📊 加载数据集...")
        print("=" * 60)
        
        # 1. 通用癌症数据
        self.datasets['cancer'] = pd.read_csv(
            self.data_dir / 'The_Cancer_data_1500_V2.csv'
        )
        print(f"✅ 加载 The_Cancer_data_1500_V2.csv: {len(self.datasets['cancer'])} 条记录")
        
        # 2. 肺癌数据
        self.datasets['lung'] = pd.read_csv(
            self.data_dir / 'survey lung cancer.csv'
        )
        print(f"✅ 加载 survey lung cancer.csv: {len(self.datasets['lung'])} 条记录")
        
        # 3. 乳腺癌数据
        self.datasets['breast'] = pd.read_csv(
            self.data_dir / 'wdbc.csv'
        )
        print(f"✅ 加载 wdbc.csv: {len(self.datasets['breast'])} 条记录")
        
        print(f"\n📈 总计: {sum(len(df) for df in self.datasets.values())} 条记录\n")
        
    def analyze_cancer_dataset(self):
        """分析通用癌症数据集"""
        print("=" * 60)
        print("🔍 分析数据集1: The_Cancer_data_1500_V2.csv")
        print("=" * 60)
        
        df = self.datasets['cancer']
        
        print(f"\n【基本信息】")
        print(f"- 样本数量: {len(df)}")
        print(f"- 特征数量: {len(df.columns) - 1}")
        print(f"- 特征列表: {list(df.columns)}")
        
        print(f"\n【标签分布】")
        print(df['Diagnosis'].value_counts())
        print(f"- 阳性率: {df['Diagnosis'].mean():.2%}")
        
        print(f"\n【数值特征统计】")
        print(df[['Age', 'BMI', 'PhysicalActivity', 'AlcoholIntake']].describe())
        
        print(f"\n【分类特征分布】")
        print(f"- 性别分布:\n{df['Gender'].value_counts()}")
        print(f"- 吸烟分布:\n{df['Smoking'].value_counts()}")
        print(f"- 遗传风险:\n{df['GeneticRisk'].value_counts()}")
        
        print(f"\n【缺失值检查】")
        missing = df.isnull().sum()
        if missing.sum() == 0:
            print("✅ 无缺失值")
        else:
            print(missing[missing > 0])
        
        return df
    
    def analyze_lung_dataset(self):
        """分析肺癌数据集"""
        print("\n" + "=" * 60)
        print("🔍 分析数据集2: survey lung cancer.csv")
        print("=" * 60)
        
        df = self.datasets['lung']
        
        print(f"\n【基本信息】")
        print(f"- 样本数量: {len(df)}")
        print(f"- 特征数量: {len(df.columns) - 1}")
        print(f"- 特征列表: {list(df.columns)}")
        
        print(f"\n【标签分布】")
        print(df['LUNG_CANCER'].value_counts())
        
        # 转换标签为数值
        df['LUNG_CANCER_NUM'] = df['LUNG_CANCER'].map({'YES': 1, 'NO': 0})
        print(f"- 肺癌阳性率: {df['LUNG_CANCER_NUM'].mean():.2%}")
        
        print(f"\n【年龄和性别统计】")
        print(f"- 年龄范围: {df['AGE'].min()} - {df['AGE'].max()}")
        print(f"- 平均年龄: {df['AGE'].mean():.1f}")
        print(f"- 性别分布:\n{df['GENDER'].value_counts()}")
        
        print(f"\n【症状特征编码】")
        print("注: 1=NO, 2=YES")
        symptom_cols = ['SMOKING', 'ANXIETY', 'COUGHING', 'CHEST PAIN']
        for col in symptom_cols:
            yes_count = (df[col] == 2).sum()
            print(f"- {col}: {yes_count}/{len(df)} = {yes_count/len(df):.1%}")
        
        return df
    
    def analyze_breast_dataset(self):
        """分析乳腺癌数据集"""
        print("\n" + "=" * 60)
        print("🔍 分析数据集3: wdbc.csv (乳腺癌)")
        print("=" * 60)
        
        df = self.datasets['breast']
        
        print(f"\n【基本信息】")
        print(f"- 样本数量: {len(df)}")
        print(f"- 特征数量: {len(df.columns) - 2}")  # 减去ID和Diagnosis
        
        print(f"\n【标签分布】")
        print(df['Diagnosis'].value_counts())
        
        # 转换标签
        df['Diagnosis_NUM'] = df['Diagnosis'].map({'M': 1, 'B': 0})
        print(f"- 恶性肿瘤率: {df['Diagnosis_NUM'].mean():.2%}")
        
        print(f"\n【特征统计（前10个特征）】")
        feature_cols = [col for col in df.columns if '_mean' in col][:5]
        print(df[feature_cols].describe())
        
        return df
    
    def feature_engineering_plan(self):
        """制定特征工程方案"""
        print("\n" + "=" * 60)
        print("🎯 特征工程方案")
        print("=" * 60)
        
        print("""
【数据集整合策略】

1️⃣ 通用癌症数据集 (1501条) - 主数据集
   ✅ 直接使用的特征:
      - Age (年龄)
      - Gender (性别: 0=男, 1=女)
      - BMI (体重指数)
      - Smoking (吸烟: 0=否, 1=是)
      - GeneticRisk (遗传风险: 0=低, 1=中, 2=高)
      - PhysicalActivity (运动量: 0-10小时/周)
      - AlcoholIntake (饮酒量: 0-5单位/周)
      - CancerHistory (癌症史: 0=否, 1=是)
   ✅ 目标变量: Diagnosis (0=无癌, 1=有癌)

2️⃣ 肺癌数据集 (309条) - 补充症状特征
   ✅ 可用特征:
      - AGE, GENDER (与主数据集对齐)
      - SMOKING (吸烟状态)
      - 症状特征(1=NO, 2=YES):
        * YELLOW_FINGERS (黄手指)
        * ANXIETY (焦虑)
        * CHRONIC DISEASE (慢性病)
        * FATIGUE (疲劳)
        * COUGHING (咳嗽)
        * SHORTNESS OF BREATH (呼吸急促)
        * CHEST PAIN (胸痛)
   ✅ 转换策略: 将2转为1(YES), 1转为0(NO)

3️⃣ 乳腺癌数据集 (569条) - 影像特征
   ✅ 特征: 30个细胞核特征
   ✅ 用途: 作为单独的乳腺癌预测模型
   ⚠️  暂不与主数据集合并(特征类型不同)

【最终训练方案】

方案A: 使用通用癌症数据集训练主模型 (推荐)
   - 数据量: 1501条
   - 特征: 8个基础特征 + 派生特征
   - 目标: 综合癌症风险评估

方案B: 合并癌症+肺癌数据 (如果需要更多数据)
   - 数据量: ~1800条
   - 需要特征对齐和归一化

方案C: 多模型集成
   - 通用癌症模型
   - 肺癌专项模型
   - 乳腺癌专项模型
   - 加权融合预测
        """)
        
    def generate_summary_report(self):
        """生成汇总报告"""
        print("\n" + "=" * 60)
        print("📋 数据集汇总报告")
        print("=" * 60)
        
        summary_data = []
        
        for name, df in self.datasets.items():
            summary_data.append({
                '数据集': name,
                '样本数': len(df),
                '特征数': len(df.columns) - 1,
                '目标变量': df.columns[-1] if name != 'breast' else 'Diagnosis',
                '阳性比例': self._get_positive_rate(name, df)
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(f"\n{summary_df.to_string(index=False)}")
        
        print(f"\n✅ 推荐使用: The_Cancer_data_1500_V2.csv 作为主训练数据")
        print(f"   - 样本量充足 (1501条)")
        print(f"   - 特征完整 (8个核心特征)")
        print(f"   - 标签清晰 (0/1二分类)")
        
    def _get_positive_rate(self, name, df):
        """获取阳性率"""
        if name == 'cancer':
            return f"{df['Diagnosis'].mean():.1%}"
        elif name == 'lung':
            return f"{(df['LUNG_CANCER'] == 'YES').mean():.1%}"
        elif name == 'breast':
            return f"{(df['Diagnosis'] == 'M').mean():.1%}"
        return "N/A"

def main():
    """主函数"""
    analyzer = DatasetAnalyzer()
    
    # 1. 加载数据
    analyzer.load_datasets()
    
    # 2. 分析各数据集
    analyzer.analyze_cancer_dataset()
    analyzer.analyze_lung_dataset()
    analyzer.analyze_breast_dataset()
    
    # 3. 特征工程方案
    analyzer.feature_engineering_plan()
    
    # 4. 生成汇总报告
    analyzer.generate_summary_report()
    
    print("\n" + "=" * 60)
    print("✅ 数据分析完成！")
    print("📝 下一步: 运行 train_model.py 开始训练")
    print("=" * 60)

if __name__ == '__main__':
    main()

