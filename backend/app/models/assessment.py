#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""风险评估结果模型"""
from sqlalchemy import Column, String, Integer, DECIMAL, JSON, TIMESTAMP, ForeignKey, Text, func
from app.core.database import Base


class Assessment(Base):
    """风险评估结果表（B2B升级）"""
    __tablename__ = "assessments"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=True, index=True)  # B2B升级
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    questionnaire_id = Column(String(36), ForeignKey('questionnaires.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 综合风险
    overall_risk_score = Column(DECIMAL(5, 4), nullable=False)
    overall_risk_level = Column(String(20), nullable=False, index=True)
    risk_percentile = Column(Integer, nullable=True)
    
    # B2B升级：审核相关字段
    status = Column(String(20), default='pending', nullable=False, index=True, comment='审核状态')
    reviewed_by = Column(String(36), nullable=True, index=True, comment='审核医生ID')
    reviewed_at = Column(TIMESTAMP, nullable=True, comment='审核时间')
    doctor_comment = Column(Text, nullable=True, comment='医生意见')
    doctor_risk_level = Column(String(20), nullable=True, comment='医生判断的风险等级')
    is_batch = Column(String(1), default='0', nullable=False, comment='是否批量筛查')
    batch_task_id = Column(String(36), nullable=True, index=True, comment='批量任务ID')
    
    # 分类风险（JSON）
    category_risks = Column(JSON, nullable=False)
    
    # 关键因素（JSON）
    key_factors = Column(JSON, nullable=False)
    shap_values = Column(JSON, nullable=True)
    
    # 模型信息
    model_version = Column(String(50), default='v1.0')
    inference_time_ms = Column(Integer, nullable=True)
    
    # AI生成的个性化建议（GLM-4.6）
    ai_recommendation = Column(Text, nullable=True, comment='AI生成的个性化健康建议')
    
    # 元数据
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "questionnaire_id": self.questionnaire_id,
            "overall_risk": {
                "score": float(self.overall_risk_score) if self.overall_risk_score else None,
                "level": self.overall_risk_level,
                "percentile": self.risk_percentile
            },
            "category_risks": self.category_risks,
            "key_factors": self.key_factors,
            "shap_values": self.shap_values,
            "model_version": self.model_version,
            "inference_time_ms": self.inference_time_ms,
            "ai_recommendation": self.ai_recommendation,  # AI生成的建议
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Recommendation(Base):
    """健康建议表"""
    __tablename__ = "recommendations"
    
    id = Column(String(36), primary_key=True)
    assessment_id = Column(String(36), ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False, index=True)
    
    category = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(String(2000), nullable=False)
    priority = Column(Integer, default=1, index=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "category": self.category,
            "title": self.title,
            "content": self.content,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Report(Base):
    """报告记录表"""
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    assessment_id = Column(String(36), ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False, index=True)
    
    report_type = Column(String(20), default='web')
    pdf_url = Column(String(255), nullable=True)
    
    # 分享功能
    share_token = Column(String(100), unique=True, nullable=True, index=True)
    share_password = Column(String(100), nullable=True)
    share_expire_at = Column(TIMESTAMP, nullable=True, index=True)
    view_count = Column(Integer, default=0)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "assessment_id": self.assessment_id,
            "report_type": self.report_type,
            "pdf_url": self.pdf_url,
            "share_token": self.share_token,
            "share_expire_at": self.share_expire_at.isoformat() if self.share_expire_at else None,
            "view_count": self.view_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
