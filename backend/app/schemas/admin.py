#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""管理员相关Pydantic模型"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AssessmentAdminSummary(BaseModel):
    """管理员视角的评估记录摘要"""
    id: str = Field(..., description="评估ID")
    user_id: str = Field(..., description="用户ID")
    user_email: str = Field(..., description="用户邮箱")
    user_nickname: Optional[str] = Field(None, description="用户昵称")
    
    # 问卷信息
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")
    
    # 风险信息
    overall_risk_score: float = Field(..., description="综合风险分数")
    overall_risk_level: str = Field(..., description="风险等级")
    risk_percentile: Optional[int] = Field(None, description="风险百分位")
    
    # 元数据
    model_version: Optional[str] = Field(None, description="模型版本")
    inference_time_ms: Optional[int] = Field(None, description="推理时间(毫秒)")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class AssessmentAdminListResponse(BaseModel):
    """管理员评估列表响应"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    records: List[AssessmentAdminSummary] = Field(..., description="评估记录列表")


class RiskLevelDistribution(BaseModel):
    """风险等级分布"""
    level: str = Field(..., description="风险等级")
    count: int = Field(..., description="数量")
    percentage: float = Field(..., description="百分比")


class TrendDataPoint(BaseModel):
    """趋势数据点"""
    date: str = Field(..., description="日期")
    count: int = Field(..., description="筛查次数")
    avg_risk_score: Optional[float] = Field(None, description="平均风险分数")


class TopRiskFactor(BaseModel):
    """高危因素排行"""
    factor: str = Field(..., description="因素名称")
    frequency: int = Field(..., description="出现次数")
    avg_contribution: float = Field(..., description="平均贡献度")


class CategoryRiskDistribution(BaseModel):
    """分类风险分布"""
    category: str = Field(..., description="肿瘤类型")
    avg_score: float = Field(..., description="平均风险分数")
    high_risk_count: int = Field(..., description="高风险人数")


class DetailedStatisticsResponse(BaseModel):
    """详细统计分析响应"""
    # 基础统计
    total_assessments: int = Field(..., description="总筛查次数")
    total_users: int = Field(..., description="总用户数")
    avg_assessments_per_user: float = Field(..., description="人均筛查次数")
    
    # 风险分布
    risk_level_distribution: List[RiskLevelDistribution] = Field(..., description="风险等级分布")
    
    # 趋势数据
    daily_trend: List[TrendDataPoint] = Field(..., description="每日筛查趋势(最近30天)")
    weekly_trend: List[TrendDataPoint] = Field(..., description="每周筛查趋势(最近12周)")
    
    # 高危因素
    top_risk_factors: List[TopRiskFactor] = Field(..., description="TOP10高危因素")
    
    # 分类风险
    category_distribution: List[CategoryRiskDistribution] = Field(..., description="各类肿瘤风险分布")
    
    # 性能指标
    avg_inference_time_ms: Optional[float] = Field(None, description="平均推理时间(毫秒)")
    latest_model_version: Optional[str] = Field(None, description="最新模型版本")
