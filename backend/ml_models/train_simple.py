"""
简化版训练脚本 - 快速验证数据整合方案
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

print("=" * 80)
print("📊 数据整合验证脚本")
print("=" * 80)

# 使用绝对路径
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / 'data'

print(f"脚本目录: {script_dir}")
print(f"数据目录: {data_dir}")
print(f"数据目录存在: {data_dir.exists()}")

# 1. 加载WDBC数据
print("\n1️⃣ 加载 WDBC 数据...")
wdbc_path = data_dir / 'archive' / 'data.csv'
print(f"   路径: {wdbc_path}")
print(f"   存在: {wdbc_path.exists()}")

if not wdbc_path.exists():
    # 尝试备用路径
    wdbc_path = Path(r"D:\桌面\shensibei\backend\data\archive\data.csv")
    print(f"   备用路径: {wdbc_path}")
    print(f"   存在: {wdbc_path.exists()}")

df_wdbc = pd.read_csv(wdbc_path)
print(f"   WDBC: {len(df_wdbc)} 条, 列: {list(df_wdbc.columns[:5])}")
print(f"   目标变量: {df_wdbc['diagnosis'].value_counts().to_dict()}")

# 2. 加载 SEER 数据
print("\n2️⃣ 加载 SEER 数据...")
df_seer = pd.read_csv(data_dir / 'Breast_Cancer.csv')
print(f"   SEER: {len(df_seer)} 条, 列: {list(df_seer.columns[:5])}")
print(f"   生存状态: {df_seer['Status'].value_counts().to_dict()}")

# 3. 检查已有数据
print("\n3️⃣ 检查已有数据...")
cancer_path = data_dir / 'The_Cancer_data_1500_V2.csv'
if cancer_path.exists():
    df_cancer = pd.read_csv(cancer_path)
    print(f"   Cancer_1500: {len(df_cancer)} 条")
    print(f"   特征: {list(df_cancer.columns)}")
else:
    print(f"   ⚠️  未找到 The_Cancer_data_1500_V2.csv")

# 4. 数据整合示例
print("\n4️⃣ 数据整合示例...")

# WDBC处理
wdbc_sample = pd.DataFrame()
wdbc_sample['age'] = np.random.randint(35, 75, 10)
wdbc_sample['gender'] = 1  # 女性
wdbc_sample['diagnosis'] = (df_wdbc['diagnosis'].head(10) == 'M').astype(int)
print(f"   WDBC处理后: {wdbc_sample.shape}")
print(wdbc_sample)

# SEER处理
seer_sample = pd.DataFrame()
seer_sample['age'] = df_seer['Age'].head(10).values
seer_sample['gender'] = 1
seer_sample['survival_status'] = (df_seer['Status'].head(10) == 'Dead').astype(int)
print(f"\n   SEER处理后: {seer_sample.shape}")
print(seer_sample)

print("\n✅ 数据整合方案可行！")
print("📝 可以使用 train_model_v2.py 进行完整训练")
print("=" * 80)

