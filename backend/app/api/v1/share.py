#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""报告分享API"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user_id
from app.models.assessment import Assessment, Report, Recommendation
from app.models.questionnaire import Questionnaire
from app.models.user import User
from app.schemas.share import (
    CreateShareRequest,
    ShareResponse,
    AccessShareRequest,
    SharedReportResponse
)
from app.utils.helpers import generate_uuid, generate_share_token, hash_share_password, verify_share_password

router = APIRouter()


@router.post("/create", response_model=dict, summary="创建分享链接")
async def create_share_link(
    request: CreateShareRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    为评估报告创建分享链接
    
    功能：
    - 生成唯一的分享token
    - 设置过期时间
    - 可选设置访问密码
    """
    # 1. 验证评估记录存在且属于当前用户
    assessment = db.query(Assessment).filter(
        Assessment.id == request.assessment_id,
        Assessment.user_id == user_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评估记录不存在"
        )
    
    # 2. 检查是否已存在Report记录
    report = db.query(Report).filter(
        Report.assessment_id == request.assessment_id
    ).first()
    
    # 3. 生成分享token
    share_token = generate_share_token()
    
    # 4. 计算过期时间
    expire_at = datetime.now() + timedelta(days=request.expire_days) if request.expire_days else None
    
    # 5. 处理密码
    share_password = None
    if request.password:
        share_password = hash_share_password(request.password)
    
    # 6. 创建或更新Report记录
    if report:
        # 更新现有记录
        report.share_token = share_token
        report.share_password = share_password
        report.share_expire_at = expire_at
        report.view_count = 0  # 重置访问计数
    else:
        # 创建新记录
        report = Report(
            id=generate_uuid(),
            user_id=user_id,
            assessment_id=request.assessment_id,
            report_type='web',
            share_token=share_token,
            share_password=share_password,
            share_expire_at=expire_at,
            view_count=0
        )
        db.add(report)
    
    db.commit()
    db.refresh(report)
    
    # 7. 返回分享信息（由前端拼接完整URL）
    return {
        "code": 200,
        "message": "分享链接创建成功",
        "data": {
            "share_token": share_token,
            "expire_at": expire_at.isoformat() if expire_at else None,
            "has_password": request.password is not None,
            "expire_days": request.expire_days
        }
    }


@router.get("/{token}", response_model=dict, summary="访问分享的报告")
async def access_shared_report(
    token: str,
    password: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    通过分享token访问报告（无需登录）
    
    功能：
    - 验证token有效性
    - 检查是否过期
    - 验证密码（如果设置了）
    - 返回脱敏后的报告数据
    - 增加访问计数
    """
    # 1. 查找分享记录
    report = db.query(Report).filter(Report.share_token == token).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享链接不存在或已失效"
        )
    
    # 2. 检查是否过期
    if report.share_expire_at and datetime.now() > report.share_expire_at:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="分享链接已过期"
        )
    
    # 3. 验证密码
    if report.share_password:
        if not password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="此报告需要密码访问"
            )
        if not verify_share_password(password, report.share_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="密码错误"
            )
    
    # 4. 查询评估数据
    assessment = db.query(Assessment).filter(
        Assessment.id == report.assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评估记录不存在"
        )
    
    # 5. 查询问卷数据
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == assessment.questionnaire_id
    ).first()
    
    # 6. 查询健康建议
    recommendations = db.query(Recommendation).filter(
        Recommendation.assessment_id == report.assessment_id
    ).order_by(Recommendation.priority).all()
    
    # 7. 增加访问计数
    report.view_count = (report.view_count or 0) + 1
    db.commit()
    
    # 8. 组装脱敏后的报告数据
    # 用户信息脱敏：只保留年龄、性别、BMI，不暴露邮箱、手机等
    user_info = {
        "age": questionnaire.age if questionnaire else None,
        "gender": questionnaire.gender if questionnaire else None,
        "bmi": float(questionnaire.bmi) if questionnaire and questionnaire.bmi else None
    }
    
    report_data = {
        "report_id": assessment.id,
        "generated_at": assessment.created_at.isoformat(),
        "user_info": user_info,
        "overall_risk": {
            "score": float(assessment.overall_risk_score),
            "level": assessment.overall_risk_level,
            "percentile": assessment.risk_percentile
        },
        "category_risks": assessment.category_risks,
        "key_factors": assessment.key_factors,
        "recommendations": [rec.to_dict() for rec in recommendations],
        "view_count": report.view_count
    }
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": report_data
    }


@router.delete("/{token}", response_model=dict, summary="取消分享")
async def cancel_share(
    token: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    取消分享链接（需要登录）
    
    只有报告的拥有者才能取消分享
    """
    # 1. 查找分享记录
    report = db.query(Report).filter(Report.share_token == token).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享链接不存在"
        )
    
    # 2. 验证是否为报告拥有者
    if report.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权取消此分享"
        )
    
    # 3. 清除分享信息（保留report记录，只清除分享字段）
    report.share_token = None
    report.share_password = None
    report.share_expire_at = None
    
    db.commit()
    
    return {
        "code": 200,
        "message": "分享已取消"
    }


@router.get("/list/my", response_model=dict, summary="获取我的分享列表")
async def get_my_shares(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户创建的所有分享链接
    """
    # 查询该用户的所有有效分享
    reports = db.query(Report).filter(
        Report.user_id == user_id,
        Report.share_token.isnot(None)  # 只查询有分享token的记录
    ).all()
    
    share_list = []
    for report in reports:
        # 判断是否过期
        is_expired = False
        if report.share_expire_at and datetime.now() > report.share_expire_at:
            is_expired = True
        
        # 获取评估信息
        assessment = db.query(Assessment).filter(
            Assessment.id == report.assessment_id
        ).first()
        
        share_list.append({
            "share_token": report.share_token,
            "assessment_id": report.assessment_id,
            "risk_level": assessment.overall_risk_level if assessment else None,
            "created_at": report.created_at.isoformat(),
            "expire_at": report.share_expire_at.isoformat() if report.share_expire_at else None,
            "is_expired": is_expired,
            "has_password": report.share_password is not None,
            "view_count": report.view_count or 0
        })
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "total": len(share_list),
            "shares": share_list
        }
    }
