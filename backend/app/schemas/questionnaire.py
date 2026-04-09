#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
问卷数据Schema - 适配v2.0模型的完整问卷
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class QuestionnaireV2Request(BaseModel):
    """问卷数据请求 - V2.0完整版"""
    
    # ==================== 基础信息 ====================
    age: int = Field(..., ge=1, le=120, description="年龄")
    gender: str = Field(..., pattern="^(男|女)$", description="性别：男/女")
    height: float = Field(..., gt=0, le=300, description="身高(cm)")
    weight: float = Field(..., gt=0, le=500, description="体重(kg)")
    
    # ==================== 生活习惯 ====================
    smoking_status: int = Field(0, ge=0, le=2, description="吸烟状态：0=从不, 1=曾经吸烟, 2=目前吸烟")
    smoking_years: Optional[int] = Field(None, ge=0, description="吸烟年数")
    smoking_amount: Optional[int] = Field(None, ge=0, description="每天吸烟量(支)")
    
    alcohol_frequency: str = Field("从不", description="饮酒频率：从不/偶尔/经常/每天")
    alcohol_amount: Optional[float] = Field(None, ge=0, description="每次饮酒量(标准杯)")
    
    exercise_hours_per_week: float = Field(0, ge=0, le=168, description="每周运动时长(小时)")
    exercise_intensity: str = Field("低", description="运动强度：低/中/高")
    
    sleep_hours: float = Field(7, ge=0, le=24, description="每日睡眠时长(小时)")
    sleep_quality: str = Field("一般", description="睡眠质量：差/一般/良好")
    
    # ==================== 疾病史 ====================
    chronic_diseases: Optional[List[str]] = Field(default_factory=list, description="慢性病史")
    
    family_cancer_history: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="家族肿瘤史：{has_history: bool, relation: str, cancer_types: List[str]}"
    )
    
    personal_cancer_history: int = Field(0, ge=0, le=1, description="个人癌症病史：0=否, 1=是")
    
    surgery_history: Optional[List[str]] = Field(default_factory=list, description="手术史")
    medication_history: Optional[List[str]] = Field(default_factory=list, description="长期用药史")
    
    # ==================== 环境与职业暴露 ====================
    occupational_exposure: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="职业暴露：{has_exposure: bool, types: List[str]}"
    )
    
    environmental_factors: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="环境因素：{air_quality: str, pollution_exposure: bool}"
    )
    
    living_environment: str = Field("城市", description="居住环境：城市/农村/工业区")
    
    # ==================== 详细饮食习惯 ====================
    vegetable_fruit_intake: str = Field("每天", description="蔬菜水果摄入：很少/偶尔/经常/每天")
    red_meat_intake: str = Field("每周2-3次", description="红肉摄入：很少/每周1-2次/每周2-3次/每天")
    processed_food_intake: str = Field("偶尔", description="加工食品摄入：很少/偶尔/经常/每天")
    pickled_food_intake: str = Field("很少", description="腌制食品摄入：很少/偶尔/经常/每天")
    dairy_intake: str = Field("每天", description="乳制品摄入：很少/偶尔/经常/每天")
    
    # ==================== 女性特有因素 ====================
    menstrual_status: Optional[str] = Field(None, description="月经状况：正常/异常/绝经/未绝经")
    
    pregnancy_history: Optional[Dict[str, Any]] = Field(
        None,
        description="妊娠史：{pregnancy_count: int, first_pregnancy_age: int}"
    )
    
    breastfeeding_history: Optional[Dict[str, Any]] = Field(
        None,
        description="哺乳史：{has_breastfed: bool, total_months: int}"
    )
    
    hormone_therapy: Optional[Dict[str, Any]] = Field(
        None,
        description="激素治疗史：{contraceptive_use: bool, hrt_use: bool, duration_years: int}"
    )
    
    # ==================== 精神压力与作息 ====================
    stress_level: str = Field("中", description="压力水平：低/中/高")
    work_rest_pattern: str = Field("规律", description="作息规律性：规律/一般/不规律/经常熬夜")
    mental_health: str = Field("良好", description="心理健康：良好/一般/焦虑/抑郁")
    
    # ==================== 体检与筛查历史 ====================
    screening_history: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="筛查历史：{last_checkup: str, tumor_markers: bool, imaging: bool, endoscopy: bool}"
    )
    
    abnormal_results_history: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="异常结果历史：[{type: str, date: str, description: str}]"
    )
    
    last_checkup: str = Field("1年内", description="上次体检时间：从未/3年以上/1-3年/1年内/半年内")
    
    # ==================== 症状自查 ====================
    symptoms: Optional[List[str]] = Field(default_factory=list, description="近期症状列表")
    recent_abnormalities: Optional[List[str]] = Field(default_factory=list, description="近期检查异常")
    
    # ==================== 备注 ====================
    notes: Optional[str] = Field(None, max_length=1000, description="其他补充信息")
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in ['男', '女']:
            raise ValueError('性别必须是"男"或"女"')
        return v
    
    @validator('family_cancer_history', pre=True)
    def validate_family_history(cls, v):
        if v is None:
            return {"has_history": False, "relation": "", "cancer_types": []}
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 45,
                "gender": "女",
                "height": 165,
                "weight": 60,
                "smoking_status": 0,
                "alcohol_frequency": "偶尔",
                "exercise_hours_per_week": 3.5,
                "exercise_intensity": "中",
                "sleep_hours": 7,
                "sleep_quality": "良好",
                "chronic_diseases": ["高血压"],
                "family_cancer_history": {
                    "has_history": True,
                    "relation": "母亲",
                    "cancer_types": ["乳腺癌"]
                },
                "personal_cancer_history": 0,
                "occupational_exposure": {
                    "has_exposure": False,
                    "types": []
                },
                "environmental_factors": {
                    "air_quality": "良好",
                    "pollution_exposure": False
                },
                "living_environment": "城市",
                "vegetable_fruit_intake": "每天",
                "red_meat_intake": "每周2-3次",
                "processed_food_intake": "偶尔",
                "pickled_food_intake": "很少",
                "dairy_intake": "每天",
                "menstrual_status": "正常",
                "pregnancy_history": {
                    "pregnancy_count": 2,
                    "first_pregnancy_age": 28
                },
                "breastfeeding_history": {
                    "has_breastfed": True,
                    "total_months": 12
                },
                "hormone_therapy": {
                    "contraceptive_use": True,
                    "hrt_use": False,
                    "duration_years": 5
                },
                "stress_level": "中",
                "work_rest_pattern": "规律",
                "mental_health": "良好",
                "screening_history": {
                    "last_checkup": "1年内",
                    "tumor_markers": True,
                    "imaging": False,
                    "endoscopy": False
                },
                "abnormal_results_history": [],
                "last_checkup": "1年内",
                "symptoms": [],
                "recent_abnormalities": [],
                "notes": "定期体检"
            }
        }


class QuestionnaireSimpleRequest(BaseModel):
    """简化版问卷请求（向后兼容）"""
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., pattern="^(男|女)$")
    height: float = Field(..., gt=0, le=300)
    weight: float = Field(..., gt=0, le=500)
    smoking: int = Field(..., ge=0, le=1)
    genetic_risk: int = Field(..., ge=0, le=2)
    physical_activity: float = Field(..., ge=0, le=168)
    alcohol_intake: float = Field(..., ge=0, le=50)
    cancer_history: int = Field(..., ge=0, le=1)
    family_history: Optional[List[str]] = None
    symptoms: Optional[List[str]] = None
    chronic_diseases: Optional[List[str]] = None
