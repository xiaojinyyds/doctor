#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""问卷数据模型"""
from sqlalchemy import Column, String, Integer, DECIMAL, JSON, TIMESTAMP, ForeignKey, func, Computed
from app.core.database import Base


class Questionnaire(Base):
    """问卷数据表（B2B升级）"""
    __tablename__ = "questionnaires"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=True, index=True)  # B2B升级
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 基本信息
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    height = Column(DECIMAL(5, 2), nullable=False)
    weight = Column(DECIMAL(5, 2), nullable=False)
    # BMI 是数据库生成列，由 weight / pow(height/100, 2) 自动计算
    bmi = Column(DECIMAL(4, 2), Computed("(`weight` / pow((`height` / 100), 2))"), nullable=True)
    
    # 生活习惯
    smoking_history = Column(JSON, nullable=True)
    alcohol_history = Column(JSON, nullable=True)
    exercise_habit = Column(String(50), nullable=True)
    diet_habits = Column(JSON, nullable=True)
    sleep_quality = Column(String(50), nullable=True)
    
    # 疾病史
    chronic_diseases = Column(JSON, nullable=True)
    family_cancer_history = Column(JSON, nullable=True)
    surgery_history = Column(JSON, nullable=True)
    medication_history = Column(JSON, nullable=True)
    
    # 症状自查
    symptoms = Column(JSON, nullable=True)
    recent_abnormalities = Column(JSON, nullable=True)
    last_checkup = Column(String(50), nullable=True)
    
    # ==================== V2.0 新增字段 ====================
    # 环境与职业暴露（3项）
    occupational_exposure = Column(JSON, nullable=True, comment='职业暴露(化学品/粉尘/辐射/生物因子等)')
    environmental_factors = Column(JSON, nullable=True, comment='环境因素(空气质量/污染暴露/居住环境等)')
    living_environment = Column(String(50), nullable=True, comment='居住环境类型(城市/农村/工业区等)')
    
    # 更详细的饮食习惯（5项）
    vegetable_fruit_intake = Column(String(50), nullable=True, comment='蔬菜水果摄入频率')
    red_meat_intake = Column(String(50), nullable=True, comment='红肉摄入频率')
    processed_food_intake = Column(String(50), nullable=True, comment='加工食品摄入频率')
    pickled_food_intake = Column(String(50), nullable=True, comment='腌制食品摄入频率')
    dairy_intake = Column(String(50), nullable=True, comment='乳制品摄入频率')
    
    # 女性特有因素（4项）
    menstrual_status = Column(String(50), nullable=True, comment='月经状况(正常/绝经/异常等)')
    pregnancy_history = Column(JSON, nullable=True, comment='妊娠史(次数/年龄/并发症等)')
    breastfeeding_history = Column(JSON, nullable=True, comment='哺乳史(时长/方式等)')
    hormone_therapy = Column(JSON, nullable=True, comment='激素治疗史(避孕药/激素替代疗法等)')
    
    # 精神压力与作息（3项）
    stress_level = Column(String(50), nullable=True, comment='压力水平(低/中/高)')
    work_rest_pattern = Column(String(50), nullable=True, comment='作息规律性(规律/一般/不规律/熬夜)')
    mental_health = Column(String(50), nullable=True, comment='心理健康状况(良好/焦虑/抑郁等)')
    
    # 体检与筛查历史（2项）
    screening_history = Column(JSON, nullable=True, comment='筛查历史(肿瘤标志物/影像学检查/内镜检查等)')
    abnormal_results_history = Column(JSON, nullable=True, comment='异常结果历史(具体异常项目及时间)')
    
    # 元数据
    status = Column(String(20), default='completed')
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "height": float(self.height) if self.height else None,
            "weight": float(self.weight) if self.weight else None,
            "bmi": float(self.bmi) if self.bmi else None,
            "smoking_history": self.smoking_history,
            "alcohol_history": self.alcohol_history,
            "exercise_habit": self.exercise_habit,
            "diet_habits": self.diet_habits,
            "sleep_quality": self.sleep_quality,
            "chronic_diseases": self.chronic_diseases,
            "family_cancer_history": self.family_cancer_history,
            "surgery_history": self.surgery_history,
            "medication_history": self.medication_history,
            "symptoms": self.symptoms,
            "recent_abnormalities": self.recent_abnormalities,
            "last_checkup": self.last_checkup,
            # V2.0 新增字段
            "occupational_exposure": self.occupational_exposure,
            "environmental_factors": self.environmental_factors,
            "living_environment": self.living_environment,
            "vegetable_fruit_intake": self.vegetable_fruit_intake,
            "red_meat_intake": self.red_meat_intake,
            "processed_food_intake": self.processed_food_intake,
            "pickled_food_intake": self.pickled_food_intake,
            "dairy_intake": self.dairy_intake,
            "menstrual_status": self.menstrual_status,
            "pregnancy_history": self.pregnancy_history,
            "breastfeeding_history": self.breastfeeding_history,
            "hormone_therapy": self.hormone_therapy,
            "stress_level": self.stress_level,
            "work_rest_pattern": self.work_rest_pattern,
            "mental_health": self.mental_health,
            "screening_history": self.screening_history,
            "abnormal_results_history": self.abnormal_results_history,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

