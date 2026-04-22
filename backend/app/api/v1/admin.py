#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""管理员API"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.security import CurrentUser, get_password_hash, require_admin
from app.models.user import User, UserRole, UserStatus
from app.models.assessment import Assessment
from app.models.questionnaire import Questionnaire
from app.schemas.user import (
    UserResponse,
    UserListResponse,
    UpdateUserStatusRequest,
    UpdateUserRoleRequest,
    AdminResetPasswordRequest
)
from app.schemas.admin import (
    AssessmentAdminSummary,
    AssessmentAdminListResponse,
    DetailedStatisticsResponse
)
from datetime import date, timedelta
from collections import Counter

router = APIRouter()


@router.get(
    "/users",
    summary="获取用户列表",
    description="管理员获取系统所有用户列表，支持分页、搜索和筛选",
    response_model=UserListResponse
)
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（邮箱/手机/昵称）"),
    role: Optional[str] = Query(None, description="角色筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（仅管理员）
    
    功能：
    - 分页查询
    - 关键词搜索（邮箱/手机号/昵称）
    - 角色筛选
    - 状态筛选
    """
    
    # 构建查询
    query = db.query(User)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                User.email.like(f"%{keyword}%"),
                User.phone.like(f"%{keyword}%"),
                User.nickname.like(f"%{keyword}%")
            )
        )
    
    # 角色筛选
    if role and role in ['user', 'doctor', 'admin']:
        query = query.filter(User.role == role)
    
    # 状态筛选
    if status and status in ['active', 'disabled']:
        query = query.filter(User.status == status)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * size
    users = query.order_by(User.created_at.desc()).offset(offset).limit(size).all()
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": [user.to_dict() for user in users]
    }


@router.post(
    "/users",
    summary="新增用户",
    description="管理员创建新用户"
)
async def create_user(
    request: dict,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员新增用户
    
    必填字段：
    - email: 邮箱
    - nickname: 昵称
    - role: 角色 (user/doctor/admin)
    
    可选字段：
    - phone: 手机号
    
    密码规则：
    - admin: admin123
    - doctor: doctor123
    - user: user123
    """
    from app.utils.helpers import generate_uuid
    
    # 验证必填字段
    email = request.get('email')
    nickname = request.get('nickname')
    role = request.get('role', 'user')
    
    if not email or not nickname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱和昵称为必填项"
        )
    
    # 验证角色有效性
    if role not in ['user', 'doctor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色必须是 user、doctor 或 admin"
        )
    
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 检查手机号是否已存在（如果提供了）
    phone = request.get('phone')
    if phone:
        existing_phone = db.query(User).filter(User.phone == phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被使用"
            )
    
    # 根据角色设置默认密码
    default_passwords = {
        'admin': 'admin123',
        'doctor': 'doctor123',
        'user': 'user123'
    }
    default_password = default_passwords.get(role, 'user123')
    
    # 创建用户
    new_user = User(
        id=generate_uuid(),
        email=email,
        phone=phone,
        password_hash=get_password_hash(default_password),
        nickname=nickname,
        role=role,
        status='active'
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "code": 200,
        "message": f"用户创建成功，默认密码为：{default_password}",
        "data": {
            **new_user.to_dict(),
            "default_password": default_password  # 返回默认密码供管理员告知用户
        }
    }


@router.get(
    "/users/{user_id}",
    summary="获取用户详情",
    description="管理员获取指定用户的详细信息",
    response_model=UserResponse
)
async def get_user_detail(
    user_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户详细信息（仅管理员）"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user.to_dict()


@router.put(
    "/users/{user_id}/status",
    summary="更新用户状态",
    description="管理员禁用或启用用户账号"
)
async def update_user_status(
    user_id: str,
    request: UpdateUserStatusRequest,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    更新用户状态（仅管理员）
    
    - active: 正常
    - disabled: 禁用
    """
    
    # 不能修改自己的状态
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的账号状态"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新状态
    user.status = request.status
    user.updated_at = datetime.now()
    db.commit()
    
    action_text = "启用" if request.status == "active" else "禁用"
    
    return {
        "code": 200,
        "message": f"用户{action_text}成功",
        "data": user.to_dict()
    }


@router.put(
    "/users/{user_id}/role",
    summary="更新用户角色",
    description="管理员修改用户角色"
)
async def update_user_role(
    user_id: str,
    request: UpdateUserRoleRequest,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    更新用户角色（仅超级管理员）
    
    角色：
    - user: 普通用户
    - doctor: 医生
    - admin: 管理员
    """
    
    # 不能修改自己的角色
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的角色"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新角色
    old_role = user.role
    user.role = request.role
    user.updated_at = datetime.now()
    db.commit()
    
    return {
        "code": 200,
        "message": f"用户角色已从 {old_role} 修改为 {request.role}",
        "data": user.to_dict()
    }


@router.post(
    "/users/{user_id}/reset-password",
    summary="管理员重置用户密码",
    description="管理员直接重置用户密码（无需验证码）"
)
async def admin_reset_user_password(
    user_id: str,
    request: AdminResetPasswordRequest,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """管理员重置用户密码（仅管理员）"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新密码
    user.password_hash = get_password_hash(request.new_password)
    user.updated_at = datetime.now()
    db.commit()
    
    return {
        "code": 200,
        "message": "密码重置成功",
        "data": {
            "user_id": user.id,
            "email": user.email
        }
    }


@router.delete(
    "/users/{user_id}",
    summary="删除用户",
    description="管理员删除用户（软删除或硬删除）"
)
async def delete_user(
    user_id: str,
    hard_delete: bool = Query(False, description="是否硬删除（true:物理删除, false:标记为禁用）"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    删除用户（仅管理员）
    
    - hard_delete=false: 软删除（标记为禁用，保留数据）
    - hard_delete=true: 硬删除（物理删除，不可恢复）
    """
    
    # 不能删除自己
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if hard_delete:
        # 硬删除
        db.delete(user)
        db.commit()
        message = "用户已永久删除"
    else:
        # 软删除（标记为禁用）
        user.status = UserStatus.DISABLED.value
        user.updated_at = datetime.now()
        db.commit()
        message = "用户已禁用"
    
    return {
        "code": 200,
        "message": message,
        "data": {
            "user_id": user_id,
            "hard_delete": hard_delete
        }
    }


@router.get(
    "/statistics/overview",
    summary="获取统计概览",
    description="获取系统运营统计数据"
)
async def get_statistics_overview(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取统计概览（仅管理员）
    
    包括：
    - 总用户数
    - 各角色用户数
    - 活跃/禁用用户数
    - 今日新增用户
    """
    
    # 总用户数
    total_users = db.query(func.count(User.id)).scalar()
    
    # 各角色用户数
    role_stats = db.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()
    
    # 各状态用户数
    status_stats = db.query(
        User.status,
        func.count(User.id)
    ).group_by(User.status).all()
    
    # 今日新增用户
    from datetime import date
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_new_users = db.query(func.count(User.id)).filter(
        User.created_at >= today_start
    ).scalar()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "total_users": total_users,
            "today_new_users": today_new_users,
            "role_distribution": {role: count for role, count in role_stats},
            "status_distribution": {status: count for status, count in status_stats}
        }
    }


@router.get(
    "/assessments",
    summary="获取所有筛查记录",
    description="管理员查看系统所有筛查记录，支持分页、搜索和筛选"
)
async def get_all_assessments(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: Optional[str] = Query(None, description="筛选特定用户"),
    risk_level: Optional[str] = Query(None, description="筛选风险等级"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="搜索关键词（用户邮箱/昵称）"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取所有筛查记录（仅管理员）
    
    功能：
    - 分页查询
    - 按用户筛选
    - 按风险等级筛选
    - 按时间范围筛选
    - 关键词搜索用户
    """
    
    # 构建基础查询 - 关联用户和问卷
    query = db.query(
        Assessment,
        User.email,
        User.nickname,
        Questionnaire.age,
        Questionnaire.gender
    ).join(
        User, Assessment.user_id == User.id
    ).outerjoin(
        Questionnaire, Assessment.questionnaire_id == Questionnaire.id
    )
    
    # 按用户ID筛选
    if user_id:
        query = query.filter(Assessment.user_id == user_id)
    
    # 按风险等级筛选
    if risk_level:
        query = query.filter(Assessment.overall_risk_level == risk_level)
    
    # 按时间范围筛选
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Assessment.created_at >= start_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期格式错误，应为 YYYY-MM-DD"
            )
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Assessment.created_at < end_dt)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期格式错误，应为 YYYY-MM-DD"
            )
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                User.email.like(f"%{keyword}%"),
                User.nickname.like(f"%{keyword}%")
            )
        )
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * page_size
    results = query.order_by(Assessment.created_at.desc()).offset(offset).limit(page_size).all()
    
    # 组装返回数据
    records = []
    for assessment, email, nickname, age, gender in results:
        records.append({
            "id": assessment.id,
            "user_id": assessment.user_id,
            "user_email": email,
            "user_nickname": nickname,
            "age": age,
            "gender": gender,
            "overall_risk_score": float(assessment.overall_risk_score),
            "overall_risk_level": assessment.overall_risk_level,
            "risk_percentile": assessment.risk_percentile,
            "model_version": assessment.model_version,
            "inference_time_ms": assessment.inference_time_ms,
            "created_at": assessment.created_at.isoformat()
        })
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "records": records
        }
    }


@router.get(
    "/assessments/{assessment_id}",
    summary="查看任意评估详情",
    description="管理员查看任意用户的评估详情"
)
async def get_assessment_detail_admin(
    assessment_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取指定评估的完整详情（仅管理员）"""
    
    # 查询评估记录（不需要验证user_id）
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评估记录不存在"
        )
    
    # 查询关联数据
    user = db.query(User).filter(User.id == assessment.user_id).first()
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == assessment.questionnaire_id
    ).first()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "assessment": assessment.to_dict(),
            "user": user.to_dict() if user else None,
            "questionnaire": questionnaire.to_dict() if questionnaire else None
        }
    }


@router.delete(
    "/assessments/{assessment_id}",
    summary="删除评估记录",
    description="管理员删除指定的评估记录"
)
async def delete_assessment_admin(
    assessment_id: str,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """删除评估记录（仅管理员）"""
    
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评估记录不存在"
        )
    
    db.delete(assessment)
    db.commit()
    
    return {
        "code": 200,
        "message": "删除成功"
    }


@router.get(
    "/statistics/detail",
    summary="获取详细统计分析",
    description="获取系统详细的统计分析数据"
)
async def get_detailed_statistics(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    获取详细统计分析（仅管理员）
    
    包括：
    - 筛查趋势
    - 风险分布
    - 高危因素排行
    - 分类风险统计
    - 性能指标
    """
    
    # 1. 基础统计
    total_assessments = db.query(func.count(Assessment.id)).scalar() or 0
    total_users_with_assessment = db.query(func.count(func.distinct(Assessment.user_id))).scalar() or 0
    avg_assessments_per_user = total_assessments / total_users_with_assessment if total_users_with_assessment > 0 else 0
    
    # 2. 风险等级分布
    risk_level_stats = db.query(
        Assessment.overall_risk_level,
        func.count(Assessment.id)
    ).group_by(Assessment.overall_risk_level).all()
    
    risk_level_distribution = []
    for level, count in risk_level_stats:
        percentage = (count / total_assessments * 100) if total_assessments > 0 else 0
        risk_level_distribution.append({
            "level": level,
            "count": count,
            "percentage": round(percentage, 2)
        })
    
    # 3. 每日趋势（最近30天）
    thirty_days_ago = datetime.now() - timedelta(days=30)
    daily_assessments = db.query(
        func.date(Assessment.created_at).label('date'),
        func.count(Assessment.id).label('count'),
        func.avg(Assessment.overall_risk_score).label('avg_score')
    ).filter(
        Assessment.created_at >= thirty_days_ago
    ).group_by(
        func.date(Assessment.created_at)
    ).all()
    
    daily_trend = []
    for day_data in daily_assessments:
        daily_trend.append({
            "date": day_data.date.isoformat(),
            "count": day_data.count,
            "avg_risk_score": round(float(day_data.avg_score), 4) if day_data.avg_score else None
        })
    
    # 4. 每周趋势（最近12周）- MySQL兼容版本
    twelve_weeks_ago = datetime.now() - timedelta(weeks=12)
    weekly_assessments = db.query(
        func.yearweek(Assessment.created_at).label('yearweek'),
        func.count(Assessment.id).label('count'),
        func.avg(Assessment.overall_risk_score).label('avg_score')
    ).filter(
        Assessment.created_at >= twelve_weeks_ago
    ).group_by(
        func.yearweek(Assessment.created_at)
    ).all()
    
    weekly_trend = []
    for week_data in weekly_assessments:
        # yearweek返回格式如202543，转换为可读格式 "2025-W43"
        yearweek_str = str(week_data.yearweek)
        year = yearweek_str[:4]
        week = yearweek_str[4:]
        weekly_trend.append({
            "date": f"{year}-W{week}",  # 使用ISO周格式
            "count": week_data.count,
            "avg_risk_score": round(float(week_data.avg_score), 4) if week_data.avg_score else None
        })
    
    # 5. TOP10高危因素（从key_factors中统计）
    all_assessments = db.query(Assessment).all()
    factor_contributions = []
    
    for assessment in all_assessments:
        if assessment.key_factors:
            for factor in assessment.key_factors:
                factor_contributions.append({
                    'name': factor.get('factor', ''),
                    'contribution': abs(factor.get('contribution', 0))
                })
    
    # 按因素名称聚合
    factor_stats = {}
    for item in factor_contributions:
        name = item['name']
        if name not in factor_stats:
            factor_stats[name] = {'count': 0, 'total_contribution': 0}
        factor_stats[name]['count'] += 1
        factor_stats[name]['total_contribution'] += item['contribution']
    
    top_risk_factors = []
    for factor_name, stats in factor_stats.items():
        avg_contribution = stats['total_contribution'] / stats['count']
        top_risk_factors.append({
            "factor": factor_name,
            "frequency": stats['count'],
            "avg_contribution": round(avg_contribution, 4)
        })
    
    # 按频率排序，取前10
    top_risk_factors.sort(key=lambda x: x['frequency'], reverse=True)
    top_risk_factors = top_risk_factors[:10]
    
    # 6. 各类肿瘤风险分布
    category_stats = {}
    for assessment in all_assessments:
        if assessment.category_risks:
            for category, risk_data in assessment.category_risks.items():
                if category not in category_stats:
                    category_stats[category] = {'total_score': 0, 'count': 0, 'high_risk_count': 0}
                
                score = risk_data.get('score', 0)
                level = risk_data.get('level', '')
                
                category_stats[category]['total_score'] += score
                category_stats[category]['count'] += 1
                if '高' in level:
                    category_stats[category]['high_risk_count'] += 1
    
    category_distribution = []
    for category, stats in category_stats.items():
        avg_score = stats['total_score'] / stats['count'] if stats['count'] > 0 else 0
        category_distribution.append({
            "category": category,
            "avg_score": round(avg_score, 4),
            "high_risk_count": stats['high_risk_count']
        })
    
    # 7. 性能指标
    avg_inference_time = db.query(
        func.avg(Assessment.inference_time_ms)
    ).scalar()
    
    latest_model = db.query(Assessment.model_version).order_by(
        Assessment.created_at.desc()
    ).first()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "total_assessments": total_assessments,
            "total_users": total_users_with_assessment,
            "avg_assessments_per_user": round(avg_assessments_per_user, 2),
            "risk_level_distribution": risk_level_distribution,
            "daily_trend": daily_trend,
            "weekly_trend": weekly_trend,
            "top_risk_factors": top_risk_factors,
            "category_distribution": category_distribution,
            "avg_inference_time_ms": round(float(avg_inference_time), 2) if avg_inference_time else None,
            "latest_model_version": latest_model[0] if latest_model else None
        }
    }

