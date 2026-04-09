#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""风险评估相关Pydantic模型"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class QuestionnaireRequest(BaseModel):
    """问卷数据请求"""
    # 基础信息
    age: int = Field(..., ge=1, le=120, description="年龄")
    gender: str = Field(..., pattern="^(男|女)$", description="性别：男/女")
    height: float = Field(..., gt=0, le=300, description="身高(cm)")
    weight: float = Field(..., gt=0, le=500, description="体重(kg)")
    
    # 健康因素
    smoking: int = Field(..., ge=0, le=1, description="吸烟：0=否, 1=是")
    genetic_risk: int = Field(..., ge=0, le=2, description="遗传风险：0=低, 1=中, 2=高")
    physical_activity: float = Field(..., ge=0, le=168, description="运动量(小时/周)")
    alcohol_intake: float = Field(..., ge=0, le=50, description="饮酒量(单位/周)")
    cancer_history: int = Field(..., ge=0, le=1, description="癌症病史：0=否, 1=是")
    
    # 可选信息
    family_history: Optional[List[str]] = Field(None, description="家族病史列表")
    symptoms: Optional[List[str]] = Field(None, description="症状列表")
    chronic_diseases: Optional[List[str]] = Field(None, description="慢性病列表")
    notes: Optional[str] = Field(None, max_length=500, description="备注")
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in ['男', '女']:
            raise ValueError('性别必须是"男"或"女"')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "age": 45,
                "gender": "男",
                "height": 175,
                "weight": 75,
                "smoking": 1,
                "genetic_risk": 1,
                "physical_activity": 3.5,
                "alcohol_intake": 2.0,
                "cancer_history": 0,
                "family_history": ["胃癌", "肺癌"],
                "symptoms": ["咳嗽"],
                "chronic_diseases": ["高血压"],
                "notes": "最近体检发现肺部有小结节"
            }
        }


class RiskFactorResponse(BaseModel):
    """风险因素响应"""
    factor: str = Field(..., description="因素名称")
    contribution: float = Field(..., description="贡献度")
    direction: str = Field(..., description="方向：increase/decrease")
    description: str = Field(..., description="描述")
    importance: float = Field(..., description="重要性")


class CategoryRiskResponse(BaseModel):
    """分类风险响应"""
    score: float = Field(..., description="风险分数")
    level: str = Field(..., description="风险等级")


class RecommendationResponse(BaseModel):
    """健康建议响应"""
    category: str = Field(..., description="类别：lifestyle/diet/screening/medical")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    priority: int = Field(..., description="优先级")
    icon: str = Field(..., description="图标")
    urgency: Optional[str] = Field(None, description="紧急程度")
    screening_items: Optional[List[Dict[str, str]]] = Field(None, description="筛查项目")


class OverallRiskResponse(BaseModel):
    """综合风险响应"""
    score: float = Field(..., description="风险分数 0-1")
    level: str = Field(..., description="风险等级")
    percentile: int = Field(..., description="百分位")


class AssessmentResultResponse(BaseModel):
    """评估结果响应"""
    overall_risk: OverallRiskResponse = Field(..., description="综合风险")
    category_risks: Dict[str, CategoryRiskResponse] = Field(..., description="分类风险")
    key_factors: List[RiskFactorResponse] = Field(..., description="关键因素")
    recommendations: List[RecommendationResponse] = Field(..., description="健康建议")


class AssessmentRecordResponse(BaseModel):
    """评估记录响应"""
    id: str
    user_id: str
    questionnaire_data: Dict[str, Any]
    assessment_result: Dict[str, Any]
    notes: Optional[str]
    created_at: str
    updated_at: Optional[str]
    
    class Config:
        from_attributes = True


class AssessmentRecordSummaryResponse(BaseModel):
    """评估记录摘要响应（用于列表）"""
    id: str
    age: int
    gender: str
    overall_risk_score: Optional[float]
    overall_risk_level: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class AssessmentHistoryResponse(BaseModel):
    """评估历史响应"""
    total: int = Field(..., description="总记录数")
    records: List[AssessmentRecordSummaryResponse] = Field(..., description="记录列表")


class CategoryRiskComparison(BaseModel):
    """分类风险对比"""
    category: str = Field(..., description="肿瘤类型")
    score_1: float = Field(..., description="第一次评估分数")
    score_2: float = Field(..., description="第二次评估分数")
    change: float = Field(..., description="分数变化")
    change_percentage: float = Field(..., description="变化百分比")


class KeyFactorChange(BaseModel):
    """关键因素变化"""
    factor: str = Field(..., description="因素名称")
    contribution_1: float = Field(..., description="第一次贡献度")
    contribution_2: float = Field(..., description="第二次贡献度")
    change: float = Field(..., description="贡献度变化")
    status: str = Field(..., description="状态：improved/worsened/stable")


class ComparisonResponse(BaseModel):
    """对比分析响应"""
    assessment_1: Dict[str, Any] = Field(..., description="第一次评估数据")
    assessment_2: Dict[str, Any] = Field(..., description="第二次评估数据")
    time_diff_days: int = Field(..., description="时间间隔（天）")
    
    # 风险分数对比
    risk_score_change: float = Field(..., description="风险分数变化")
    risk_score_change_percentage: float = Field(..., description="风险分数变化百分比")
    risk_level_changed: bool = Field(..., description="风险等级是否改变")
    
    # 分类风险对比
    category_risks_comparison: List[CategoryRiskComparison] = Field(..., description="各类肿瘤风险对比")
    
    # 关键因素变化
    key_factors_changes: List[KeyFactorChange] = Field(..., description="关键因素变化")
    
    # 总结
    summary: str = Field(..., description="变化总结")
    improvement_suggestions: List[str] = Field(..., description="改进建议")

