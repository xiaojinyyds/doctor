"""
肿瘤风险预测模型训练脚本
使用 XGBoost + SHAP 实现可解释的风险评估
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import json
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix, classification_report
)
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
import seaborn as sns

class TumorRiskModelTrainer:
    """肿瘤风险模型训练器"""
    
    def __init__(self, data_path=None):
        """初始化"""
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.model_dir = Path(__file__).parent / 'saved_models'
        self.model_dir.mkdir(exist_ok=True)
        
        self.data_path = data_path or (self.data_dir / 'The_Cancer_data_1500_V2.csv')
        
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def load_data(self):
        """加载数据"""
        print("=" * 60)
        print("📂 步骤1: 加载数据")
        print("=" * 60)
        
        df = pd.read_csv(self.data_path)
        print(f"✅ 加载数据: {len(df)} 条记录")
        print(f"✅ 特征列: {list(df.columns)}")
        
        # 显示前几行
        print(f"\n数据预览:")
        print(df.head())
        
        return df
    
    def preprocess_data(self, df):
        """数据预处理"""
        print("\n" + "=" * 60)
        print("🔧 步骤2: 数据预处理")
        print("=" * 60)
        
        # 特征列（除了目标变量）
        feature_cols = [
            'Age', 'Gender', 'BMI', 'Smoking', 'GeneticRisk',
            'PhysicalActivity', 'AlcoholIntake', 'CancerHistory'
        ]
        
        # 基础特征
        X = df[feature_cols].copy()
        y = df['Diagnosis'].values
        
        print(f"✅ 特征矩阵 X: {X.shape}")
        print(f"✅ 目标变量 y: {y.shape}")
        print(f"✅ 阳性样本: {y.sum()} ({y.mean():.1%})")
        print(f"✅ 阴性样本: {len(y) - y.sum()} ({1-y.mean():.1%})")
        
        # 添加派生特征
        print(f"\n🎨 创建派生特征...")
        
        # 1. BMI分类特征
        X['BMI_Category'] = pd.cut(
            X['BMI'], 
            bins=[0, 18.5, 24, 28, 100],
            labels=[0, 1, 2, 3]  # 偏瘦, 正常, 超重, 肥胖
        ).astype(int)
        
        # 2. 年龄分组
        X['Age_Group'] = pd.cut(
            X['Age'],
            bins=[0, 30, 45, 60, 100],
            labels=[0, 1, 2, 3]  # 青年, 中年, 中老年, 老年
        ).astype(int)
        
        # 3. 高风险标志（多个高风险因素）
        X['HighRisk_Flag'] = (
            (X['Smoking'] == 1) & 
            (X['GeneticRisk'] >= 1) & 
            (X['Age'] > 50)
        ).astype(int)
        
        # 4. 健康评分（运动 - 饮酒 - 吸烟）
        X['Health_Score'] = (
            X['PhysicalActivity'] / 10 - 
            X['AlcoholIntake'] / 5 - 
            X['Smoking'] * 0.5
        )
        
        # 5. 交互特征
        X['Age_x_Smoking'] = X['Age'] * X['Smoking']
        X['BMI_x_Activity'] = X['BMI'] * X['PhysicalActivity']
        X['Genetic_x_History'] = X['GeneticRisk'] * X['CancerHistory']
        
        print(f"✅ 派生特征已创建")
        print(f"✅ 最终特征数: {X.shape[1]}")
        
        self.feature_names = list(X.columns)
        
        return X, y
    
    def split_data(self, X, y):
        """划分数据集"""
        print("\n" + "=" * 60)
        print("✂️  步骤3: 划分数据集")
        print("=" * 60)
        
        # 划分训练集和测试集 (80:20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=0.2, 
            random_state=42,
            stratify=y  # 保持标签分布一致
        )
        
        print(f"✅ 训练集: {len(X_train)} 样本 ({len(X_train)/len(X):.1%})")
        print(f"   - 阳性: {y_train.sum()} ({y_train.mean():.1%})")
        print(f"   - 阴性: {len(y_train) - y_train.sum()}")
        
        print(f"✅ 测试集: {len(X_test)} 样本 ({len(X_test)/len(X):.1%})")
        print(f"   - 阳性: {y_test.sum()} ({y_test.mean():.1%})")
        print(f"   - 阴性: {len(y_test) - y_test.sum()}")
        
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        
        return X_train, X_test, y_train, y_test
    
    def normalize_features(self, X_train, X_test):
        """特征标准化"""
        print("\n" + "=" * 60)
        print("📏 步骤4: 特征标准化")
        print("=" * 60)
        
        self.scaler = StandardScaler()
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"✅ 训练集标准化完成: {X_train_scaled.shape}")
        print(f"✅ 测试集标准化完成: {X_test_scaled.shape}")
        
        # 显示标准化统计
        print(f"\n标准化后的均值 (应接近0): {X_train_scaled.mean(axis=0)[:3]}")
        print(f"标准化后的标准差 (应接近1): {X_train_scaled.std(axis=0)[:3]}")
        
        return X_train_scaled, X_test_scaled
    
    def train_model(self, X_train, y_train):
        """训练XGBoost模型"""
        print("\n" + "=" * 60)
        print("🤖 步骤5: 训练XGBoost模型")
        print("=" * 60)
        
        # XGBoost参数
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'min_child_weight': 1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'n_jobs': -1
        }
        
        print(f"📋 模型参数:")
        for k, v in params.items():
            print(f"   - {k}: {v}")
        
        print(f"\n🏋️  开始训练...")
        self.model = xgb.XGBClassifier(**params)
        self.model.fit(
            X_train, y_train,
            verbose=False
        )
        
        print(f"✅ 模型训练完成！")
        
        return self.model
    
    def evaluate_model(self, X_train, X_test, y_train, y_test):
        """评估模型性能"""
        print("\n" + "=" * 60)
        print("📊 步骤6: 模型评估")
        print("=" * 60)
        
        # 训练集评估
        y_train_pred = self.model.predict(X_train)
        y_train_prob = self.model.predict_proba(X_train)[:, 1]
        
        # 测试集评估
        y_test_pred = self.model.predict(X_test)
        y_test_prob = self.model.predict_proba(X_test)[:, 1]
        
        # 计算指标
        metrics = {
            'train': {
                'accuracy': accuracy_score(y_train, y_train_pred),
                'precision': precision_score(y_train, y_train_pred, zero_division=0),
                'recall': recall_score(y_train, y_train_pred, zero_division=0),
                'f1': f1_score(y_train, y_train_pred, zero_division=0),
                'auc': roc_auc_score(y_train, y_train_prob)
            },
            'test': {
                'accuracy': accuracy_score(y_test, y_test_pred),
                'precision': precision_score(y_test, y_test_pred, zero_division=0),
                'recall': recall_score(y_test, y_test_pred, zero_division=0),
                'f1': f1_score(y_test, y_test_pred, zero_division=0),
                'auc': roc_auc_score(y_test, y_test_prob)
            }
        }
        
        print(f"\n【训练集性能】")
        print(f"   准确率 (Accuracy):  {metrics['train']['accuracy']:.4f}")
        print(f"   精确率 (Precision): {metrics['train']['precision']:.4f}")
        print(f"   召回率 (Recall):    {metrics['train']['recall']:.4f}")
        print(f"   F1分数 (F1 Score):  {metrics['train']['f1']:.4f}")
        print(f"   AUC:               {metrics['train']['auc']:.4f}")
        
        print(f"\n【测试集性能】 ⭐重要")
        print(f"   准确率 (Accuracy):  {metrics['test']['accuracy']:.4f}")
        print(f"   精确率 (Precision): {metrics['test']['precision']:.4f}")
        print(f"   召回率 (Recall):    {metrics['test']['recall']:.4f}")
        print(f"   F1分数 (F1 Score):  {metrics['test']['f1']:.4f}")
        print(f"   AUC:               {metrics['test']['auc']:.4f}")
        
        # 混淆矩阵
        cm = confusion_matrix(y_test, y_test_pred)
        print(f"\n【混淆矩阵】")
        print(f"             预测负  预测正")
        print(f"   实际负:    {cm[0,0]:4d}   {cm[0,1]:4d}")
        print(f"   实际正:    {cm[1,0]:4d}   {cm[1,1]:4d}")
        
        # 特征重要性
        print(f"\n【特征重要性 Top 10】")
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(feature_importance.head(10).to_string(index=False))
        
        # 检查是否达标
        if metrics['test']['accuracy'] >= 0.85:
            print(f"\n✅ 模型性能达标！(准确率 ≥ 85%)")
        else:
            print(f"\n⚠️  模型性能未达标 (准确率 < 85%)")
            print(f"   建议: 增加数据量或调整参数")
        
        return metrics, feature_importance
    
    def explain_model(self, X_test):
        """SHAP可解释性分析"""
        print("\n" + "=" * 60)
        print("🔍 步骤7: SHAP可解释性分析")
        print("=" * 60)
        
        print(f"初始化 TreeExplainer...")
        explainer = shap.TreeExplainer(self.model)
        
        print(f"计算 SHAP 值 (可能需要几秒钟)...")
        shap_values = explainer.shap_values(X_test[:100])  # 只计算前100个样本
        
        print(f"✅ SHAP 值计算完成: {shap_values.shape}")
        
        # 平均绝对SHAP值（特征重要性）
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        shap_importance = pd.DataFrame({
            'feature': self.feature_names,
            'mean_abs_shap': mean_abs_shap
        }).sort_values('mean_abs_shap', ascending=False)
        
        print(f"\n【SHAP特征重要性 Top 10】")
        print(shap_importance.head(10).to_string(index=False))
        
        return explainer, shap_values
    
    def save_model(self):
        """保存模型和配置"""
        print("\n" + "=" * 60)
        print("💾 步骤8: 保存模型")
        print("=" * 60)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存XGBoost模型
        model_path = self.model_dir / 'xgboost_model.pkl'
        joblib.dump(self.model, model_path)
        print(f"✅ XGBoost模型已保存: {model_path}")
        
        # 2. 保存Scaler
        scaler_path = self.model_dir / 'scaler.pkl'
        joblib.dump(self.scaler, scaler_path)
        print(f"✅ StandardScaler已保存: {scaler_path}")
        
        # 3. 保存特征配置
        feature_config = {
            'feature_names': self.feature_names,
            'n_features': len(self.feature_names),
            'model_version': 'v1.0',
            'trained_at': timestamp,
            'training_samples': len(self.X_train),
            'feature_description': {
                'Age': '年龄 (20-80)',
                'Gender': '性别 (0=男, 1=女)',
                'BMI': '体重指数 (15-40)',
                'Smoking': '吸烟 (0=否, 1=是)',
                'GeneticRisk': '遗传风险 (0=低, 1=中, 2=高)',
                'PhysicalActivity': '运动量 (0-10小时/周)',
                'AlcoholIntake': '饮酒量 (0-5单位/周)',
                'CancerHistory': '癌症史 (0=否, 1=是)'
            }
        }
        
        config_path = self.model_dir / 'feature_config.json'
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(feature_config, f, indent=2, ensure_ascii=False)
        print(f"✅ 特征配置已保存: {config_path}")
        
        # 4. 保存训练记录
        training_log = {
            'timestamp': timestamp,
            'data_source': str(self.data_path),
            'total_samples': len(self.X_train) + len(self.X_test),
            'train_samples': len(self.X_train),
            'test_samples': len(self.X_test),
            'features': self.feature_names,
            'model_type': 'XGBoost',
            'model_version': 'v1.0'
        }
        
        log_path = self.model_dir / 'training_log.json'
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(training_log, f, indent=2, ensure_ascii=False)
        print(f"✅ 训练日志已保存: {log_path}")
        
        print(f"\n📦 所有文件已保存到: {self.model_dir}")
        
    def test_prediction(self):
        """测试预测功能"""
        print("\n" + "=" * 60)
        print("🧪 步骤9: 测试预测")
        print("=" * 60)
        
        # 测试样例1: 高风险用户
        test_case_high = {
            'Age': 65,
            'Gender': 0,  # 男
            'BMI': 28,
            'Smoking': 1,  # 吸烟
            'GeneticRisk': 2,  # 高遗传风险
            'PhysicalActivity': 2,  # 运动少
            'AlcoholIntake': 4,  # 饮酒多
            'CancerHistory': 1,  # 有癌症史
        }
        
        # 测试样例2: 低风险用户
        test_case_low = {
            'Age': 30,
            'Gender': 1,  # 女
            'BMI': 22,
            'Smoking': 0,  # 不吸烟
            'GeneticRisk': 0,  # 低遗传风险
            'PhysicalActivity': 8,  # 运动多
            'AlcoholIntake': 0,  # 不饮酒
            'CancerHistory': 0,  # 无癌症史
        }
        
        for i, test_case in enumerate([test_case_high, test_case_low], 1):
            print(f"\n【测试样例{i}】")
            print(f"输入特征: {test_case}")
            
            # 构造特征（需要添加派生特征）
            features_df = pd.DataFrame([test_case])
            
            # 添加派生特征（与训练时一致）
            features_df['BMI_Category'] = pd.cut(
                features_df['BMI'], 
                bins=[0, 18.5, 24, 28, 100],
                labels=[0, 1, 2, 3]
            ).astype(int)
            features_df['Age_Group'] = pd.cut(
                features_df['Age'],
                bins=[0, 30, 45, 60, 100],
                labels=[0, 1, 2, 3]
            ).astype(int)
            features_df['HighRisk_Flag'] = (
                (features_df['Smoking'] == 1) & 
                (features_df['GeneticRisk'] >= 1) & 
                (features_df['Age'] > 50)
            ).astype(int)
            features_df['Health_Score'] = (
                features_df['PhysicalActivity'] / 10 - 
                features_df['AlcoholIntake'] / 5 - 
                features_df['Smoking'] * 0.5
            )
            features_df['Age_x_Smoking'] = features_df['Age'] * features_df['Smoking']
            features_df['BMI_x_Activity'] = features_df['BMI'] * features_df['PhysicalActivity']
            features_df['Genetic_x_History'] = features_df['GeneticRisk'] * features_df['CancerHistory']
            
            # 标准化
            features_scaled = self.scaler.transform(features_df)
            
            # 预测
            pred_prob = self.model.predict_proba(features_scaled)[0]
            pred_class = self.model.predict(features_scaled)[0]
            
            risk_level = self._get_risk_level(pred_prob[1])
            
            print(f"预测结果:")
            print(f"   - 低风险概率: {pred_prob[0]:.2%}")
            print(f"   - 高风险概率: {pred_prob[1]:.2%}")
            print(f"   - 预测类别: {'有癌症风险' if pred_class == 1 else '无癌症风险'}")
            print(f"   - 风险等级: {risk_level}")
    
    def _get_risk_level(self, score):
        """风险分级"""
        if score < 0.3:
            return "低风险"
        elif score < 0.5:
            return "中低风险"
        elif score < 0.7:
            return "中高风险"
        else:
            return "高风险"
    
    def run(self):
        """运行完整训练流程"""
        print("\n" + "🚀" * 30)
        print(" " * 20 + "肿瘤风险预测模型训练")
        print("🚀" * 30 + "\n")
        
        try:
            # 1. 加载数据
            df = self.load_data()
            
            # 2. 预处理
            X, y = self.preprocess_data(df)
            
            # 3. 划分数据
            X_train, X_test, y_train, y_test = self.split_data(X, y)
            
            # 4. 标准化
            X_train_scaled, X_test_scaled = self.normalize_features(X_train, X_test)
            
            # 5. 训练模型
            self.train_model(X_train_scaled, y_train)
            
            # 6. 评估模型
            metrics, feature_importance = self.evaluate_model(
                X_train_scaled, X_test_scaled, y_train, y_test
            )
            
            # 7. SHAP分析
            explainer, shap_values = self.explain_model(X_test_scaled)
            
            # 8. 保存模型
            self.save_model()
            
            # 9. 测试预测
            self.test_prediction()
            
            print("\n" + "🎉" * 30)
            print(" " * 20 + "训练流程全部完成！")
            print("🎉" * 30)
            
            print(f"\n📊 最终性能指标:")
            print(f"   ✅ 测试集准确率: {metrics['test']['accuracy']:.2%}")
            print(f"   ✅ 测试集AUC: {metrics['test']['auc']:.4f}")
            print(f"   ✅ 测试集F1分数: {metrics['test']['f1']:.4f}")
            
            if metrics['test']['accuracy'] >= 0.85:
                print(f"\n✅ 恭喜！模型性能达到要求（≥85%）")
            else:
                print(f"\n⚠️  模型性能略低于目标（85%），但仍可使用")
            
            print(f"\n📁 模型文件位置: {self.model_dir}")
            print(f"   - xgboost_model.pkl")
            print(f"   - scaler.pkl")
            print(f"   - feature_config.json")
            print(f"   - training_log.json")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 训练过程出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    trainer = TumorRiskModelTrainer()
    success = trainer.run()
    
    if success:
        print(f"\n{'='*60}")
        print(f"✅ 模型训练成功完成！")
        print(f"📝 下一步: 实现后端风险评估引擎 (risk_engine.py)")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print(f"❌ 模型训练失败，请检查错误信息")
        print(f"{'='*60}\n")

if __name__ == '__main__':
    main()

