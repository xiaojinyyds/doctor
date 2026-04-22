#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""医生工作台API（B2B升级新增）"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user, require_doctor_or_admin, CurrentUser
from app.models.assessment import Assessment
from app.models.user import User
from app.models.questionnaire import Questionnaire
from app.utils.helpers import generate_uuid

router = APIRouter(prefix="/doctor", tags=["医生工作台"])


@router.get("/pending-assessments", summary="获取待审核评估列表")
async def get_pending_assessments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    risk_level: Optional[str] = Query(None, description="风险等级筛选"),
    current_user: CurrentUser = Depends(require_doctor_or_admin),
    db: Session = Depends(get_db)
):
    """
    获取待审核的评估列表
    
    - 只显示当前租户的数据
    - 按风险分数降序排序（高风险优先）
    - 支持按风险等级筛选
    """
    # 构建查询
    query = db.query(Assessment).filter(
        Assessment.tenant_id == current_user.tenant_id,
        Assessment.status == "pending"
    )
    
    # 风险等级筛选
    if risk_level:
        query = query.filter(Assessment.overall_risk_level == risk_level)
    
    # 按风险分数降序
    query = query.order_by(Assessment.overall_risk_score.desc())
    
    # 分页
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 获取关联的用户信息
    result_items = []
    for assessment in items:
        user = db.query(User).filter(User.id == assessment.user_id).first()
        questionnaire = db.query(Questionnaire).filter(
            Questionnaire.id == assessment.questionnaire_id
        ).first()
        
        result_items.append({
            "id": assessment.id,
            "user_id": assessment.user_id,
            "patient_name": user.nickname if user else "未知",
            "patient_email": user.email if user else "",
            "age": questionnaire.age if questionnaire else None,
            "gender": questionnaire.gender if questionnaire else None,
            "overall_risk_score": float(assessment.overall_risk_score),
            "overall_risk_level": assessment.overall_risk_level,
            "created_at": assessment.created_at.isoformat() if assessment.created_at else None
        })
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": result_items
        }
    }


@router.get("/assessments/{assessment_id}", summary="获取评估详情")
async def get_assessment_detail(
    assessment_id: str,
    current_user: CurrentUser = Depends(require_doctor_or_admin),
    db: Session = Depends(get_db)
):
    """获取评估详情（用于审核）"""
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.tenant_id == current_user.tenant_id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")
    
    # 获取关联信息
    user = db.query(User).filter(User.id == assessment.user_id).first()
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == assessment.questionnaire_id
    ).first()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "assessment": {
                "id": assessment.id,
                "overall_risk_score": float(assessment.overall_risk_score),
                "overall_risk_level": assessment.overall_risk_level,
                "category_risks": assessment.category_risks,
                "key_factors": assessment.key_factors,
                "ai_recommendation": assessment.ai_recommendation,
                "status": assessment.status,
                "created_at": assessment.created_at.isoformat() if assessment.created_at else None
            },
            "patient": {
                "id": user.id if user else None,
                "nickname": user.nickname if user else "未知",
                "email": user.email if user else "",
                "phone": user.phone if user else ""
            },
            "questionnaire": questionnaire.to_dict() if questionnaire and hasattr(questionnaire, 'to_dict') else None
        }
    }


@router.post("/assessments/{assessment_id}/approve", summary="审核通过")
async def approve_assessment(
    assessment_id: str,
    request: dict,
    current_user: CurrentUser = Depends(require_doctor_or_admin),
    db: Session = Depends(get_db)
):
    """
    审核通过评估结果
    
    参数:
    - doctor_comment: 医生意见（可选）
    - doctor_risk_level: 医生判断的风险等级（可选，如果与AI不同）
    """
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.tenant_id == current_user.tenant_id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")
    
    if assessment.status != "pending":
        raise HTTPException(status_code=400, detail="该评估已被审核")
    
    # 更新审核信息
    assessment.status = "approved"
    assessment.reviewed_by = current_user.user_id
    assessment.reviewed_at = datetime.utcnow()
    assessment.doctor_comment = request.get("doctor_comment")
    assessment.doctor_risk_level = request.get("doctor_risk_level")
    
    db.commit()
    
    return {
        "code": 200,
        "message": "审核通过",
        "data": {
            "assessment_id": assessment_id,
            "status": "approved"
        }
    }


@router.post("/assessments/{assessment_id}/reject", summary="驳回评估")
async def reject_assessment(
    assessment_id: str,
    request: dict,
    current_user: CurrentUser = Depends(require_doctor_or_admin),
    db: Session = Depends(get_db)
):
    """
    驳回评估结果
    
    参数:
    - reason: 驳回原因（必填）
    """
    if not request.get("reason"):
        raise HTTPException(status_code=400, detail="请填写驳回原因")
    
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.tenant_id == current_user.tenant_id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")
    
    if assessment.status != "pending":
        raise HTTPException(status_code=400, detail="该评估已被审核")
    
    # 更新审核信息
    assessment.status = "rejected"
    assessment.reviewed_by = current_user.user_id
    assessment.reviewed_at = datetime.utcnow()
    assessment.doctor_comment = f"驳回原因: {request.get('reason')}"
    
    db.commit()
    
    return {
        "code": 200,
        "message": "已驳回",
        "data": {
            "assessment_id": assessment_id,
            "status": "rejected"
        }
    }


@router.get("/statistics", summary="医生工作台统计")
async def get_doctor_statistics(
    current_user: CurrentUser = Depends(require_doctor_or_admin),
    db: Session = Depends(get_db)
):
    """
    获取医生工作台统计数据
    
    - 待审核数量
    - 今日已审核数量
    - 本月筛查总数
    """
    from datetime import date
    
    # 待审核数量
    pending_count = db.query(func.count(Assessment.id)).filter(
        Assessment.tenant_id == current_user.tenant_id,
        Assessment.status == "pending"
    ).scalar() or 0
    
    # 今日已审核数量
    today = date.today()
    today_reviewed = db.query(func.count(Assessment.id)).filter(
        Assessment.tenant_id == current_user.tenant_id,
        Assessment.reviewed_by == current_user.user_id,
        func.date(Assessment.reviewed_at) == today
    ).scalar() or 0
    
    # 本月筛查总数
    month_start = date.today().replace(day=1)
    month_total = db.query(func.count(Assessment.id)).filter(
        Assessment.tenant_id == current_user.tenant_id,
        Assessment.created_at >= month_start
    ).scalar() or 0
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "pending_count": pending_count,
            "today_reviewed": today_reviewed,
            "month_total": month_total
        }
    }
