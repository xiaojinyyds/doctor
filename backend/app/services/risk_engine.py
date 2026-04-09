"""
肿瘤风险评估引擎
使用训练好的XGBoost模型进行风险预测，并提供SHAP可解释性分析
"""

import joblib
import numpy as np
import pandas as pd
import shap
from pathlib import Path
from typing import Dict, List, Tuple
import json


class RiskAssessmentEngine:
    """风险评估引擎"""
    
    def __init__(self):
        """初始化模型和解释器"""
        self.model_dir = Path(__file__).parent.parent.parent / 'ml_models' / 'saved_models'
        
        # 加载模型
        model_path = self.model_dir / 'xgboost_model.pkl'
        scaler_path = self.model_dir / 'scaler.pkl'
        config_path = self.model_dir / 'feature_config.json'
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"模型文件不存在: {model_path}\n"
                f"请先运行 python ml_models/train_model.py 训练模型"
            )
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        # 加载特征配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.feature_names = config['feature_names']
        
        # 初始化SHAP解释器
        self.explainer = shap.TreeExplainer(self.model)
        
        print(f"✅ 风险评估引擎已初始化")
        print(f"   - 模型版本: v1.0")
        print(f"   - 特征数量: {len(self.feature_names)}")
    
    def predict(self, user_data: dict) -> dict:
        """
        风险预测主函数
        
        Args:
            user_data: 用户问卷数据字典，包含以下字段：
                - age: 年龄 (int)
                - gender: 性别 (str: '男'/'女' 或 int: 0/1)
                - height: 身高 cm (float)
                - weight: 体重 kg (float)
                - smoking: 吸烟 (int: 0=否, 1=是)
                - genetic_risk: 遗传风险 (int: 0=低, 1=中, 2=高)
                - physical_activity: 运动量 (float: 0-10小时/周)
                - alcohol_intake: 饮酒量 (float: 0-5单位/周)
                - cancer_history: 癌症史 (int: 0=否, 1=是)
                
        Returns:
            dict: 评估结果，包含：
                - overall_risk: 综合风险 {score, level, percentile}
                - category_risks: 分类风险
                - key_factors: 关键因素（SHAP值）
                - recommendations: 健康建议
        """
        try:
            # 1. 数据预处理
            processed_data = self._preprocess_user_data(user_data)
            
            # 2. 特征工程
            features_df = self._extract_features(processed_data)
            
            # 3. 标准化
            features_scaled = self.scaler.transform(features_df)
            
            # 4. 模型预测
            risk_prob = self.model.predict_proba(features_scaled)[0][1]
            risk_level = self._classify_risk_level(risk_prob)
            
            # 5. SHAP解释
            shap_values = self.explainer.shap_values(features_scaled)[0]
            key_factors = self._get_key_factors(shap_values, features_df, user_data)
            
            # 6. 分类风险计算
            category_risks = self._calculate_category_risks(processed_data, risk_prob)
            
            # 7. 生成建议
            recommendations = self._generate_recommendations(
                processed_data, risk_level, key_factors
            )
            
            # 8. 组装结果
            result = {
                'overall_risk': {
                    'score': float(risk_prob),
                    'level': risk_level,
                    'percentile': self._calculate_percentile(risk_prob)
                },
                'category_risks': category_risks,
                'key_factors': key_factors,
                'recommendations': recommendations,
                'shap_values': shap_values.tolist(),  # 用于前端可视化
                'feature_values': features_df.iloc[0].to_dict()
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"风险评估失败: {str(e)}")
    
    def _preprocess_user_data(self, user_data: dict) -> dict:
        """预处理用户输入数据"""
        processed = {}
        
        # 年龄
        processed['Age'] = int(user_data.get('age', 50))
        
        # 性别：统一转换为数值
        gender = user_data.get('gender', 0)
        if isinstance(gender, str):
            processed['Gender'] = 1 if gender == '女' else 0
        else:
            processed['Gender'] = int(gender)
        
        # BMI：如果提供身高体重则计算，否则使用直接值
        if 'bmi' in user_data:
            processed['BMI'] = float(user_data['bmi'])
        elif 'height' in user_data and 'weight' in user_data:
            height_m = float(user_data['height']) / 100
            weight_kg = float(user_data['weight'])
            processed['BMI'] = weight_kg / (height_m ** 2)
        else:
            processed['BMI'] = 25.0  # 默认值
        
        # 其他特征
        processed['Smoking'] = int(user_data.get('smoking', 0))
        processed['GeneticRisk'] = int(user_data.get('genetic_risk', 0))
        processed['PhysicalActivity'] = float(user_data.get('physical_activity', 5.0))
        processed['AlcoholIntake'] = float(user_data.get('alcohol_intake', 0.0))
        processed['CancerHistory'] = int(user_data.get('cancer_history', 0))
        
        return processed
    
    def _extract_features(self, data: dict) -> pd.DataFrame:
        """特征工程（与训练时保持一致）"""
        df = pd.DataFrame([data])
        
        # 派生特征1: BMI分类
        df['BMI_Category'] = pd.cut(
            df['BMI'], 
            bins=[0, 18.5, 24, 28, 100],
            labels=[0, 1, 2, 3]
        ).astype(int)
        
        # 派生特征2: 年龄分组
        df['Age_Group'] = pd.cut(
            df['Age'],
            bins=[0, 30, 45, 60, 100],
            labels=[0, 1, 2, 3]
        ).astype(int)
        
        # 派生特征3: 高风险标志
        df['HighRisk_Flag'] = (
            (df['Smoking'] == 1) & 
            (df['GeneticRisk'] >= 1) & 
            (df['Age'] > 50)
        ).astype(int)
        
        # 派生特征4: 健康评分
        df['Health_Score'] = (
            df['PhysicalActivity'] / 10 - 
            df['AlcoholIntake'] / 5 - 
            df['Smoking'] * 0.5
        )
        
        # 派生特征5-7: 交互特征
        df['Age_x_Smoking'] = df['Age'] * df['Smoking']
        df['BMI_x_Activity'] = df['BMI'] * df['PhysicalActivity']
        df['Genetic_x_History'] = df['GeneticRisk'] * df['CancerHistory']
        
        # 确保列顺序与训练时一致
        df = df[self.feature_names]
        
        return df
    
    def _classify_risk_level(self, score: float) -> str:
        """风险分级"""
        if score < 0.3:
            return "低风险"
        elif score < 0.5:
            return "中低风险"
        elif score < 0.7:
            return "中高风险"
        else:
            return "高风险"
    
    def _calculate_percentile(self, score: float) -> int:
        """计算风险百分位"""
        return int(score * 100)
    
    def _get_key_factors(self, shap_values: np.ndarray, features_df: pd.DataFrame, 
                         user_data: dict) -> List[Dict]:
        """获取关键风险因素（基于SHAP值）"""
        # 创建特征-SHAP值对
        factor_impacts = []
        
        for i, (feature_name, shap_value) in enumerate(zip(self.feature_names, shap_values)):
            feature_value = features_df.iloc[0, i]
            
            factor_impacts.append({
                'feature': feature_name,
                'shap_value': float(shap_value),
                'feature_value': float(feature_value),
                'abs_shap': abs(float(shap_value))
            })
        
        # 按SHAP绝对值排序
        factor_impacts.sort(key=lambda x: x['abs_shap'], reverse=True)
        
        # 取Top 10，添加描述
        top_factors = []
        for factor in factor_impacts[:10]:
            description = self._generate_factor_description(
                factor['feature'], 
                factor['shap_value'],
                factor['feature_value'],
                user_data
            )
            
            top_factors.append({
                'factor': self._translate_feature_name(factor['feature']),
                'contribution': float(factor['shap_value']),
                'direction': 'increase' if factor['shap_value'] > 0 else 'decrease',
                'description': description,
                'importance': float(factor['abs_shap'])
            })
        
        return top_factors
    
    def _translate_feature_name(self, feature: str) -> str:
        """翻译特征名称"""
        translations = {
            'Age': '年龄',
            'Gender': '性别',
            'BMI': '体重指数',
            'Smoking': '吸烟史',
            'GeneticRisk': '遗传风险',
            'PhysicalActivity': '运动量',
            'AlcoholIntake': '饮酒量',
            'CancerHistory': '癌症病史',
            'BMI_Category': 'BMI分类',
            'Age_Group': '年龄组',
            'HighRisk_Flag': '高风险标志',
            'Health_Score': '健康评分',
            'Age_x_Smoking': '年龄与吸烟交互',
            'BMI_x_Activity': 'BMI与运动交互',
            'Genetic_x_History': '遗传与病史交互'
        }
        return translations.get(feature, feature)
    
    def _generate_factor_description(self, feature: str, shap_value: float, 
                                     feature_value: float, user_data: dict) -> str:
        """生成因素描述"""
        impact = "增加" if shap_value > 0 else "降低"
        
        descriptions = {
            'Age': f"您的年龄{user_data.get('age', '未知')}岁，{impact}了癌症风险",
            'Gender': f"性别因素对风险有影响",
            'BMI': f"BMI指数{feature_value:.1f}，{impact}了风险",
            'Smoking': f"{'吸烟' if user_data.get('smoking', 0) == 1 else '不吸烟'}显著{impact}风险",
            'GeneticRisk': f"遗传风险等级{'低中高'[user_data.get('genetic_risk', 0)]}，{impact}了风险",
            'PhysicalActivity': f"运动量{feature_value:.1f}小时/周，{impact}风险",
            'AlcoholIntake': f"饮酒量{feature_value:.1f}单位/周，{impact}了风险",
            'CancerHistory': f"{'有' if user_data.get('cancer_history', 0) == 1 else '无'}癌症病史，{impact}风险",
            'HighRisk_Flag': f"{'存在' if feature_value > 0 else '不存在'}多重高危因素"
        }
        
        return descriptions.get(feature, f"{feature}{impact}了风险")
    
    def _calculate_category_risks(self, data: dict, overall_risk: float) -> Dict:
        """计算各类肿瘤风险"""
        # 基于不同因素计算各类肿瘤风险
        
        # 1. 肺癌风险（主要因素：吸烟、年龄）
        lung_risk = overall_risk * 0.8
        if data['Smoking'] == 1:
            lung_risk = min(lung_risk + 0.2, 0.95)
        if data['Age'] > 55:
            lung_risk = min(lung_risk + 0.1, 0.95)
        
        # 2. 胃癌风险（主要因素：饮食、年龄）
        stomach_risk = overall_risk * 0.6
        if data['AlcoholIntake'] > 3:
            stomach_risk = min(stomach_risk + 0.15, 0.9)
        
        # 3. 肝癌风险（主要因素：饮酒、病史）
        liver_risk = overall_risk * 0.5
        if data['AlcoholIntake'] > 3:
            liver_risk = min(liver_risk + 0.2, 0.9)
        if data['CancerHistory'] == 1:
            liver_risk = min(liver_risk + 0.15, 0.9)
        
        # 4. 结直肠癌风险
        colorectal_risk = overall_risk * 0.55
        if data['Age'] > 50:
            colorectal_risk = min(colorectal_risk + 0.1, 0.85)
        if data['PhysicalActivity'] < 3:
            colorectal_risk = min(colorectal_risk + 0.1, 0.85)
        
        # 5. 乳腺癌/前列腺癌风险
        gender_specific_risk = overall_risk * 0.6
        if data['Gender'] == 1:  # 女性
            risk_type = "乳腺癌"
            if data['Age'] > 40:
                gender_specific_risk = min(gender_specific_risk + 0.1, 0.85)
        else:  # 男性
            risk_type = "前列腺癌"
            if data['Age'] > 60:
                gender_specific_risk = min(gender_specific_risk + 0.1, 0.85)
        
        return {
            "肺癌": {
                "score": float(lung_risk),
                "level": self._classify_risk_level(lung_risk)
            },
            "胃癌": {
                "score": float(stomach_risk),
                "level": self._classify_risk_level(stomach_risk)
            },
            "肝癌": {
                "score": float(liver_risk),
                "level": self._classify_risk_level(liver_risk)
            },
            "结直肠癌": {
                "score": float(colorectal_risk),
                "level": self._classify_risk_level(colorectal_risk)
            },
            risk_type: {
                "score": float(gender_specific_risk),
                "level": self._classify_risk_level(gender_specific_risk)
            }
        }
    
    def _generate_recommendations(self, data: dict, risk_level: str, 
                                  key_factors: List[Dict]) -> List[Dict]:
        """生成个性化健康建议"""
        recommendations = []
        priority = 1
        
        # 1. 吸烟建议
        if data['Smoking'] == 1:
            recommendations.append({
                'category': 'lifestyle',
                'title': '立即戒烟',
                'content': '吸烟是癌症的首要危险因素，特别是肺癌、喉癌、食管癌等。戒烟可显著降低患癌风险，戒烟5年后风险可下降50%以上。建议寻求专业戒烟帮助。',
                'priority': priority,
                'icon': '🚭'
            })
            priority += 1
        
        # 2. 体重建议
        if data['BMI'] > 28:
            recommendations.append({
                'category': 'lifestyle',
                'title': '控制体重至正常范围',
                'content': f'您的BMI指数为{data["BMI"]:.1f}，属于超重/肥胖。肥胖与多种癌症相关，建议将BMI控制在18.5-24之间。推荐适度饮食控制和规律运动。',
                'priority': priority,
                'icon': '⚖️'
            })
            priority += 1
        elif data['BMI'] < 18.5:
            recommendations.append({
                'category': 'lifestyle',
                'title': '适当增加体重',
                'content': f'您的BMI指数为{data["BMI"]:.1f}，偏瘦可能影响免疫功能。建议均衡饮食，适当增加营养摄入。',
                'priority': priority,
                'icon': '🍽️'
            })
            priority += 1
        
        # 3. 运动建议
        if data['PhysicalActivity'] < 3:
            recommendations.append({
                'category': 'lifestyle',
                'title': '增加体育锻炼',
                'content': '规律运动可降低30%以上的癌症风险。建议每周至少进行150分钟中等强度有氧运动，如快走、游泳、骑车等。',
                'priority': priority,
                'icon': '🏃'
            })
            priority += 1
        
        # 4. 饮酒建议
        if data['AlcoholIntake'] > 2:
            recommendations.append({
                'category': 'diet',
                'title': '减少饮酒',
                'content': '过量饮酒与肝癌、食管癌、结直肠癌等多种癌症相关。建议男性每日饮酒量不超过25克纯酒精，女性不超过15克，最好不饮酒。',
                'priority': priority,
                'icon': '🍷'
            })
            priority += 1
        
        # 5. 饮食建议
        recommendations.append({
            'category': 'diet',
            'title': '均衡饮食，多吃蔬果',
            'content': '建议每天摄入400-800克新鲜蔬菜和水果，减少红肉和加工肉类摄入，避免腌制、熏制食品。多吃全谷物、豆类和富含纤维的食物。',
            'priority': priority,
            'icon': '🥗'
        })
        priority += 1
        
        # 6. 筛查建议（基于年龄和风险）
        screening_recs = []
        
        if data['Age'] >= 40:
            if data['Smoking'] == 1 or risk_level in ['中高风险', '高风险']:
                screening_recs.append({
                    'name': '低剂量螺旋CT',
                    'purpose': '肺癌筛查',
                    'frequency': '每年1次',
                    'suitable_for': '40岁以上吸烟者或高风险人群'
                })
        
        if data['Age'] >= 45:
            screening_recs.append({
                'name': '胃镜检查',
                'purpose': '胃癌筛查',
                'frequency': '每2-3年1次',
                'suitable_for': '45岁以上人群'
            })
            
            screening_recs.append({
                'name': '肠镜检查',
                'purpose': '结直肠癌筛查',
                'frequency': '每5年1次或每年粪便潜血',
                'suitable_for': '45岁以上人群'
            })
        
        if data['GeneticRisk'] >= 1 or data['CancerHistory'] == 1:
            screening_recs.append({
                'name': '肿瘤标志物检测',
                'purpose': '多种癌症筛查',
                'frequency': '每年1次',
                'suitable_for': '有家族史或病史的人群'
            })
        
        if screening_recs:
            recommendations.append({
                'category': 'screening',
                'title': '推荐定期筛查',
                'content': '基于您的风险评估，建议进行以下筛查：\n' + 
                          '\n'.join([f"• {rec['name']}（{rec['purpose']}）- {rec['frequency']}" 
                                    for rec in screening_recs]),
                'priority': priority,
                'icon': '🏥',
                'screening_items': screening_recs
            })
            priority += 1
        
        # 7. 就医建议（高风险人群）
        if risk_level in ['中高风险', '高风险']:
            urgency = '高' if risk_level == '高风险' else '中'
            recommendations.append({
                'category': 'medical',
                'title': '建议医院全面体检',
                'content': f'您的综合风险评估为{risk_level}，建议尽快到正规医院进行全面体检。推荐科室：肿瘤科、内科。请携带本报告咨询专业医生。',
                'priority': priority,
                'icon': '⚠️',
                'urgency': urgency
            })
        
        return recommendations


# 全局实例（单例模式）
_engine_instance = None

def get_risk_engine() -> RiskAssessmentEngine:
    """获取风险评估引擎实例（单例）"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RiskAssessmentEngine()
    return _engine_instance


# 便捷函数
def assess_risk(user_data: dict) -> dict:
    """
    评估用户癌症风险
    
    Args:
        user_data: 用户数据字典
        
    Returns:
        评估结果字典
    """
    engine = get_risk_engine()
    return engine.predict(user_data)


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("🧪 测试风险评估引擎")
    print("=" * 60)
    
    # 测试用例1: 高风险
    test_case_1 = {
        'age': 65,
        'gender': '男',
        'height': 175,
        'weight': 85,
        'smoking': 1,
        'genetic_risk': 2,
        'physical_activity': 1.5,
        'alcohol_intake': 4.5,
        'cancer_history': 1
    }
    
    print("\n【测试用例1：高风险用户】")
    print(f"输入: {test_case_1}")
    
    result1 = assess_risk(test_case_1)
    print(f"\n综合风险:")
    print(f"  - 分数: {result1['overall_risk']['score']:.2%}")
    print(f"  - 等级: {result1['overall_risk']['level']}")
    
    print(f"\n关键因素 (Top 5):")
    for factor in result1['key_factors'][:5]:
        direction_icon = "↑" if factor['direction'] == 'increase' else "↓"
        print(f"  {direction_icon} {factor['factor']}: {factor['contribution']:.3f}")
    
    print(f"\n分类风险:")
    for cancer_type, risk_info in result1['category_risks'].items():
        print(f"  - {cancer_type}: {risk_info['score']:.2%} ({risk_info['level']})")
    
    print(f"\n健康建议 ({len(result1['recommendations'])}条):")
    for rec in result1['recommendations'][:3]:
        print(f"  {rec['icon']} {rec['title']}")
    
    # 测试用例2: 低风险
    test_case_2 = {
        'age': 28,
        'gender': '女',
        'height': 165,
        'weight': 55,
        'smoking': 0,
        'genetic_risk': 0,
        'physical_activity': 7.5,
        'alcohol_intake': 0,
        'cancer_history': 0
    }
    
    print("\n" + "=" * 60)
    print("【测试用例2：低风险用户】")
    print(f"输入: {test_case_2}")
    
    result2 = assess_risk(test_case_2)
    print(f"\n综合风险:")
    print(f"  - 分数: {result2['overall_risk']['score']:.2%}")
    print(f"  - 等级: {result2['overall_risk']['level']}")
    
    print("\n✅ 风险评估引擎测试完成！")

