#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""报告分享相关Pydantic模型"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateShareRequest(BaseModel):
    """创建分享请求"""
    assessment_id: str = Field(..., description="评估记录ID")
    expire_days: Optional[int] = Field(7, ge=1, le=365, description="有效期（天），默认7天")
    password: Optional[str] = Field(None, min_length=4, max_length=20, description="访问密码（可选）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "assessment_id": "uuid-xxx",
                "expire_days": 7,
                "password": "1234"
            }
        }


class ShareResponse(BaseModel):
    """分享响应"""
    share_token: str = Field(..., description="分享令牌")
    share_url: str = Field(..., description="完整分享URL")
    expire_at: Optional[datetime] = Field(None, description="过期时间")
    has_password: bool = Field(..., description="是否设置了密码")
    qr_code_url: Optional[str] = Field(None, description="二维码图片URL（可选）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "share_token": "abc123def456",
                "share_url": "http://localhost:3000/share/abc123def456",
                "expire_at": "2024-10-19T10:30:00Z",
                "has_password": True,
                "qr_code_url": None
            }
        }


class AccessShareRequest(BaseModel):
    """访问分享请求"""
    password: Optional[str] = Field(None, description="访问密码（如果设置了）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "1234"
            }
        }


class SharedReportResponse(BaseModel):
    """分享的报告响应（脱敏后）"""
    report_id: str = Field(..., description="报告ID")
    generated_at: str = Field(..., description="生成时间")
    
    # 用户信息（脱敏）
    user_info: dict = Field(..., description="用户信息（已脱敏）")
    
    # 评估结果
    overall_risk: dict = Field(..., description="综合风险")
    category_risks: dict = Field(..., description="分类风险")
    key_factors: list = Field(..., description="关键因素")
    recommendations: list = Field(..., description="健康建议")
    
    # 访问统计
    view_count: int = Field(..., description="查看次数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "uuid-xxx",
                "generated_at": "2024-10-12T10:30:00Z",
                "user_info": {
                    "age": 45,
                    "gender": "男",
                    "bmi": 24.5
                },
                "overall_risk": {
                    "score": 0.68,
                    "level": "高风险",
                    "percentile": 82
                },
                "view_count": 5
            }
        }
