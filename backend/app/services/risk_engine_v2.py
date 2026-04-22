"""
肿瘤风险评估引擎 V2.0
使用训练好的XGBoost v2.0模型（32个特征）
"""

import joblib
import numpy as np
import pandas as pd
# 延迟导入 shap，避免启动时加载 torch 导致 DLL 错误
# import shap
from pathlib import Path
from typing import Dict, List
import json


class RiskAssessmentEngineV2:
    """风险评估引擎 V2.0"""
    
    def __init__(self):
        """初始化模型"""
        self.model_dir = Path(__file__).parent.parent.parent / 'ml_models' / 'saved_models'
        
        model_path = self.model_dir / 'xgboost_model.pkl'
        scaler_path = self.model_dir / 'scaler.pkl'
        config_path = self.model_dir / 'feature_config.json'
        
        if not model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.feature_names = config['feature_names']
            self.model_version = config['model_version']
        
        # 延迟初始化 SHAP 解释器（避免启动时加载 torch）
        self.explainer = None
        self._shap_loaded = False
        
        print(f"✅ 风险评估引擎V2已初始化 - 模型版本: {self.model_version}")
    
    def predict(self, questionnaire_data: dict) -> dict:
        """风险预测"""
        try:
            features_df = self._extract_all_features(questionnaire_data)
            features_scaled = self.scaler.transform(features_df)
            
            risk_prob = self.model.predict_proba(features_scaled)[0][1]
            risk_level = self._classify_risk_level(risk_prob)
            
            # 延迟加载 SHAP
            if not self._shap_loaded:
                import shap
                self.explainer = shap.TreeExplainer(self.model)
                self._shap_loaded = True
            
            shap_values = self.explainer.shap_values(features_scaled)[0]
            key_factors = self._get_key_factors(shap_values, features_df, questionnaire_data)
            
            category_risks = self._calculate_category_risks(questionnaire_data, risk_prob)
            recommendations = self._generate_recommendations(questionnaire_data, risk_level, key_factors)
            
            result = {
                'overall_risk': {
                    'score': float(risk_prob),
                    'level': risk_level,
                    'percentile': int((1 - risk_prob) * 100)  # 修正：风险越低，百分位越高
                },
                'category_risks': category_risks,
                'key_factors': key_factors,
                'recommendations': recommendations,
                'shap_values': shap_values.tolist(),
                'feature_values': features_df.iloc[0].to_dict()
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"风险评估失败: {str(e)}")
    
    def _extract_all_features(self, data: dict) -> pd.DataFrame:
        """提取32个特征"""
        # 基础特征
        age = int(data.get('age', 50))
        gender = 1 if data.get('gender', '女') == '女' else 0
        height = float(data.get('height', 165))
        weight = float(data.get('weight', 60))
        bmi = weight / ((height / 100) ** 2)
        
        # 生活习惯
        smoking_status = min(int(data.get('smoking_status', 0)), 1)
        
        alcohol_freq = data.get('alcohol_frequency', '从不')
        alcohol_map = {'从不': 0, '偶尔': 1, '经常': 1, '每天': 2}
        alcohol_status = alcohol_map.get(alcohol_freq, 0)
        
        exercise_level = min(float(data.get('exercise_hours_per_week', 3.5)), 7.0)
        
        # 遗传与家族史
        family_history_data = data.get('family_cancer_history', {})
        if isinstance(family_history_data, dict):
            has_family_history = family_history_data.get('has_history', False)
            cancer_types = family_history_data.get('cancer_types', [])
            genetic_risk = 2 if (has_family_history and len(cancer_types) >= 2) else (1 if has_family_history else 0)
            family_history = 1 if has_family_history else 0
        else:
            genetic_risk = 0
            family_history = 0
        
        # 肿瘤标志物和组织异常
        screening_data = data.get('screening_history', {})
        tumor_marker_score = 0.3 if (isinstance(screening_data, dict) and screening_data.get('tumor_markers')) else 0.1
        
        abnormal_results = data.get('abnormal_results_history', [])
        tissue_abnormality = min(len(abnormal_results) * 0.2, 0.8) if isinstance(abnormal_results, list) else 0.1
        
        # 女性特有因素
        menstrual_abnormal = 0
        pregnancy_count = 0
        hormone_therapy = 0
        if gender == 1:
            menstrual_abnormal = 1 if data.get('menstrual_status') == '异常' else 0
            pregnancy_data = data.get('pregnancy_history')
            if isinstance(pregnancy_data, dict):
                pregnancy_count = pregnancy_data.get('pregnancy_count', 0)
            hormone_data = data.get('hormone_therapy')
            if isinstance(hormone_data, dict):
                hormone_therapy = 1 if (hormone_data.get('contraceptive_use') or hormone_data.get('hrt_use')) else 0
        
        # 环境与职业
        occupational_data = data.get('occupational_exposure', {})
        occupational_exposure_score = 0.1
        if isinstance(occupational_data, dict) and occupational_data.get('has_exposure'):
            exposure_types = occupational_data.get('types', [])
            occupational_exposure_score = min(len(exposure_types) * 0.2, 0.8)
        
        environmental_data = data.get('environmental_factors', {})
        environmental_risk_score = 0.2
        if isinstance(environmental_data, dict):
            air_quality = environmental_data.get('air_quality', '良好')
            pollution = environmental_data.get('pollution_exposure', False)
            env_score = 0.1 + (0.3 if air_quality in ['差', '很差'] else 0) + (0.2 if pollution else 0)
            environmental_risk_score = min(env_score, 0.8)
        
        # 饮食习惯
        veg_map = {'很少': 0.2, '偶尔': 0.4, '经常': 0.7, '每天': 0.9}
        vegetable_fruit_score = veg_map.get(data.get('vegetable_fruit_intake', '每天'), 0.7)
        
        meat_map = {'很少': 0.2, '每周1-2次': 0.4, '每周2-3次': 0.6, '每天': 0.9}
        red_meat_score = meat_map.get(data.get('red_meat_intake', '每周2-3次'), 0.5)
        
        processed_map = {'很少': 0.2, '偶尔': 0.4, '经常': 0.7, '每天': 0.9}
        processed_food_score = processed_map.get(data.get('processed_food_intake', '偶尔'), 0.4)
        
        diet_quality_score = vegetable_fruit_score * 0.5 + (1 - red_meat_score) * 0.3 + (1 - processed_food_score) * 0.2
        
        # 生育相关
        reproductive_risk_score = 0.0
        if gender == 1:
            reproductive_risk_score = menstrual_abnormal * 0.3 + (0.3 if pregnancy_count == 0 else 0) + hormone_therapy * 0.4
        
        # 压力与作息
        stress_map = {'低': 0.2, '中': 0.5, '高': 0.8}
        stress_level_score = stress_map.get(data.get('stress_level', '中'), 0.5)
        
        rest_map = {'规律': 0.2, '一般': 0.5, '不规律': 0.7, '经常熬夜': 0.9}
        work_rest_regularity = rest_map.get(data.get('work_rest_pattern', '规律'), 0.3)
        
        # 筛查历史
        checkup_map = {'从未': 0.1, '3年以上': 0.2, '1-3年': 0.4, '1年内': 0.6, '半年内': 0.8}
        checkup_score = checkup_map.get(data.get('last_checkup', '1年内'), 0.4)
        screening_history_score = (tumor_marker_score + checkup_score) / 2
        abnormal_results_count = len(abnormal_results) if isinstance(abnormal_results, list) else 0
        
        # 派生特征
        bmi_category = 0 if bmi < 18.5 else (1 if bmi < 24 else (2 if bmi < 28 else 3))
        age_group = 0 if age < 35 else (1 if age < 50 else (2 if age < 65 else 3))
        lifestyle_score = diet_quality_score * 0.3 + (1 - smoking_status) * 0.3 + (exercise_level / 7) * 0.2 + (1 - alcohol_status / 2) * 0.2
        comprehensive_risk = genetic_risk / 2 * 0.3 + family_history * 0.2 + stress_level_score * 0.2 + screening_history_score * 0.3
        
        # 交互特征
        age_x_smoking = age * smoking_status
        bmi_x_exercise = bmi * exercise_level
        age_x_genetic = age * genetic_risk
        age_x_bmi = age * bmi
        
        features = {
            'age': age, 'gender': gender, 'bmi': bmi, 'smoking_status': smoking_status,
            'alcohol_status': alcohol_status, 'exercise_level': exercise_level,
            'genetic_risk': genetic_risk, 'family_history': family_history,
            'tumor_marker_score': tumor_marker_score, 'tissue_abnormality': tissue_abnormality,
            'menstrual_abnormal': menstrual_abnormal, 'pregnancy_count': pregnancy_count,
            'hormone_therapy': hormone_therapy, 'occupational_exposure_score': occupational_exposure_score,
            'environmental_risk_score': environmental_risk_score, 'diet_quality_score': diet_quality_score,
            'vegetable_fruit_score': vegetable_fruit_score, 'red_meat_score': red_meat_score,
            'processed_food_score': processed_food_score, 'reproductive_risk_score': reproductive_risk_score,
            'stress_level_score': stress_level_score, 'work_rest_regularity': work_rest_regularity,
            'screening_history_score': screening_history_score, 'abnormal_results_count': abnormal_results_count,
            'bmi_category': bmi_category, 'age_group': age_group, 'lifestyle_score': lifestyle_score,
            'comprehensive_risk': comprehensive_risk, 'age_x_smoking': age_x_smoking,
            'bmi_x_exercise': bmi_x_exercise, 'age_x_genetic': age_x_genetic, 'age_x_bmi': age_x_bmi
        }
        
        df = pd.DataFrame([features])
        return df[self.feature_names]
    
    def _classify_risk_level(self, score: float) -> str:
        if score < 0.25: return "低风险"
        elif score < 0.5: return "中低风险"
        elif score < 0.75: return "中高风险"
        else: return "高风险"
    
    def _get_key_factors(self, shap_values: np.ndarray, features_df: pd.DataFrame, data: dict) -> List[Dict]:
        factor_impacts = []
        for i, (fname, sval) in enumerate(zip(self.feature_names, shap_values)):
            factor_impacts.append({
                'feature': fname, 'shap_value': float(sval),
                'feature_value': float(features_df.iloc[0, i]), 'abs_shap': abs(float(sval))
            })
        factor_impacts.sort(key=lambda x: x['abs_shap'], reverse=True)
        
        translations = {'age': '年龄', 'gender': '性别', 'bmi': 'BMI指数', 'smoking_status': '吸烟', 'family_history': '家族史'}
        top_factors = []
        for f in factor_impacts[:10]:
            top_factors.append({
                'factor': translations.get(f['feature'], f['feature']),
                'contribution': f['shap_value'],
                'direction': 'increase' if f['shap_value'] > 0 else 'decrease',
                'description': f"{translations.get(f['feature'], f['feature'])}{'增加' if f['shap_value']>0 else '降低'}了风险",
                'importance': f['abs_shap']
            })
        return top_factors
    
    def _calculate_category_risks(self, data: dict, overall_risk: float) -> Dict:
        age = data.get('age', 50)
        gender = 1 if data.get('gender') == '女' else 0
        smoking = data.get('smoking_status', 0)
        
        lung_risk = min(overall_risk * 0.7 + (0.25 if smoking else 0), 0.95)
        stomach_risk = overall_risk * 0.6
        liver_risk = overall_risk * 0.5
        colorectal_risk = overall_risk * 0.55
        gender_risk = overall_risk * 0.6
        
        return {
            "肺癌": {"score": float(lung_risk), "level": self._classify_risk_level(lung_risk)},
            "胃癌": {"score": float(stomach_risk), "level": self._classify_risk_level(stomach_risk)},
            "肝癌": {"score": float(liver_risk), "level": self._classify_risk_level(liver_risk)},
            "结直肠癌": {"score": float(colorectal_risk), "level": self._classify_risk_level(colorectal_risk)},
            ("乳腺癌" if gender == 1 else "前列腺癌"): {"score": float(gender_risk), "level": self._classify_risk_level(gender_risk)}
        }
    
    def _generate_recommendations(self, data: dict, risk_level: str, key_factors: List[Dict]) -> List[Dict]:
        recommendations = []
        if data.get('smoking_status', 0) > 0:
            recommendations.append({'category': 'lifestyle', 'title': '立即戒烟', 'content': '吸烟是癌症首要危险因素', 'priority': 1, 'icon': '🚭'})
        if risk_level in ['中高风险', '高风险']:
            recommendations.append({'category': 'medical', 'title': '建议全面体检', 'content': f'风险评估为{risk_level}', 'priority': 2, 'icon': '⚠️'})
        return recommendations


_engine_v2_instance = None

def get_risk_engine_v2() -> RiskAssessmentEngineV2:
    global _engine_v2_instance
    if _engine_v2_instance is None:
        _engine_v2_instance = RiskAssessmentEngineV2()
    return _engine_v2_instance

def assess_risk_v2(questionnaire_data: dict) -> dict:
    engine = get_risk_engine_v2()
    return engine.predict(questionnaire_data)
