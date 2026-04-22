#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""风险评估API"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.questionnaire import Questionnaire
from app.models.assessment import Assessment, Recommendation, Report
from app.models.user import User
from app.schemas.assessment import (
    QuestionnaireRequest,
    AssessmentResultResponse,
    AssessmentRecordResponse,
    AssessmentRecordSummaryResponse,
    AssessmentHistoryResponse,
    ComparisonResponse,
    CategoryRiskComparison,
    KeyFactorChange
)
from app.services.risk_engine_v2 import assess_risk_v2
from app.utils.helpers import generate_uuid
import time
from decimal import Decimal

router = APIRouter()


@router.post("/submit", response_model=dict, summary="提交问卷并获取风险评估")
async def submit_assessment(
    questionnaire: QuestionnaireRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    提交问卷数据，进行风险评估并保存记录
    """
    try:
        start_time = time.time()
        
        # 1. 保存问卷数据（BMI会由数据库自动计算，无需手动设置）
        questionnaire_id = generate_uuid()
        questionnaire_record = Questionnaire(
            id=questionnaire_id,
            user_id=user_id,
            age=questionnaire.age,
            gender=questionnaire.gender,
            height=Decimal(str(questionnaire.height)),
            weight=Decimal(str(questionnaire.weight)),
            # bmi 字段是数据库生成列，会自动计算，不要手动设置
            smoking_history={'is_smoking': questionnaire.smoking == 1},
            alcohol_history={'intake_level': questionnaire.alcohol_intake},
            exercise_habit=f"{questionnaire.physical_activity}小时/周",
            chronic_diseases=questionnaire.chronic_diseases,
            family_cancer_history=questionnaire.family_history,
            symptoms=questionnaire.symptoms,
            status='completed'
        )
        db.add(questionnaire_record)
        # 先刷新以确保问卷记录在数据库中存在（解决外键约束问题）
        db.flush()
        
        # 2. 准备评估数据（转换为V2格式，缺失字段使用默认值）
        assessment_data = {
            # 基础信息
            'age': questionnaire.age,
            'gender': questionnaire.gender,
            'height': questionnaire.height,
            'weight': questionnaire.weight,
            
            # 生活习惯（从V1映射）
            'smoking_status': questionnaire.smoking,
            'alcohol_frequency': '从不' if questionnaire.alcohol_intake == 0 else ('偶尔' if questionnaire.alcohol_intake < 3 else '经常'),
            'exercise_hours_per_week': questionnaire.physical_activity,
            'exercise_intensity': '中',
            'sleep_hours': 7,
            'sleep_quality': '一般',
            
            # 疾病史
            'chronic_diseases': questionnaire.chronic_diseases or [],
            'family_cancer_history': {
                'has_history': bool(questionnaire.family_history and len(questionnaire.family_history) > 0),
                'relation': '',
                'cancer_types': questionnaire.family_history or []
            },
            'personal_cancer_history': questionnaire.cancer_history,
            'surgery_history': [],
            'medication_history': [],
            
            # 环境与职业（默认值）
            'occupational_exposure': {'has_exposure': False, 'types': []},
            'environmental_factors': {'air_quality': '良好', 'pollution_exposure': False},
            'living_environment': '城市',
            
            # 饮食习惯（默认值）
            'vegetable_fruit_intake': '经常',
            'red_meat_intake': '每周2-3次',
            'processed_food_intake': '偶尔',
            'pickled_food_intake': '偶尔',
            'dairy_intake': '经常',
            
            # 女性特有（根据性别）
            'menstrual_status': None if questionnaire.gender == '男' else '正常',
            'pregnancy_history': None,
            'breastfeeding_history': None,
            'hormone_therapy': None,
            
            # 压力作息（默认值）
            'stress_level': '中',
            'work_rest_pattern': '规律',
            'mental_health': '良好',
            
            # 筛查历史（默认值）
            'screening_history': {'last_checkup': '1年内', 'tumor_markers': False, 'imaging': False, 'endoscopy': False},
            'abnormal_results_history': [],
            'last_checkup': '1年内',
            
            # 症状
            'symptoms': questionnaire.symptoms or [],
            'recent_abnormalities': [],
            'notes': questionnaire.notes or ''
        }
        
        # 3. 调用V2风险评估引擎（V1接口自动转换为V2格式）
        result = assess_risk_v2(assessment_data)
        
        # 4. 保存评估结果
        assessment_id = generate_uuid()
        assessment_record = Assessment(
            id=assessment_id,
            user_id=user_id,
            questionnaire_id=questionnaire_id,
            overall_risk_score=Decimal(str(round(result['overall_risk']['score'], 4))),
            overall_risk_level=result['overall_risk']['level'],
            risk_percentile=result['overall_risk']['percentile'],
            category_risks=result['category_risks'],
            key_factors=result['key_factors'],
            shap_values=result.get('shap_values'),
            model_version='v2.0_enhanced',  # 现在使用V2引擎
            inference_time_ms=int((time.time() - start_time) * 1000)
        )
        db.add(assessment_record)
        
        # 5. 保存健康建议
        recommendations = []
        for idx, rec in enumerate(result['recommendations']):
            rec_id = generate_uuid()
            recommendation = Recommendation(
                id=rec_id,
                assessment_id=assessment_id,
                category=rec.get('category', 'general'),
                title=rec['title'],
                content=rec['content'],
                priority=rec.get('priority', idx + 1)
            )
            db.add(recommendation)
            recommendations.append(recommendation)
        
        # 6. 提交数据库
        db.commit()
        db.refresh(assessment_record)
        
        # 7. 返回结果
        return {
            "code": 200,
            "message": "评估完成",
            "data": {
                "questionnaire_id": questionnaire_id,
                "assessment_id": assessment_id,
                "assessment_result": {
                    "overall_risk": {
                        "score": float(assessment_record.overall_risk_score),
                        "level": assessment_record.overall_risk_level,
                        "percentile": assessment_record.risk_percentile
                    },
                    "category_risks": assessment_record.category_risks,
                    "key_factors": assessment_record.key_factors,
                    "recommendations": [rec.to_dict() for rec in recommendations]
                },
                "created_at": assessment_record.created_at.isoformat()
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"风险评估失败: {str(e)}"
        )


@router.get("/history", response_model=dict, summary="获取评估历史")
async def get_assessment_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的评估历史记录（分页）
    """
    # 查询总数
    total = db.query(Assessment).filter(
        Assessment.user_id == user_id
    ).count()
    
    # 查询分页数据
    assessments = db.query(Assessment).join(
        Questionnaire, Assessment.questionnaire_id == Questionnaire.id
    ).filter(
        Assessment.user_id == user_id
    ).order_by(
        Assessment.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    # 转换为摘要格式
    record_summaries = []
    for assessment in assessments:
        questionnaire = db.query(Questionnaire).filter(
            Questionnaire.id == assessment.questionnaire_id
        ).first()
        
        # 查询分享信息
        report = db.query(Report).filter(
            Report.assessment_id == assessment.id,
            Report.share_token.isnot(None)  # 只查询有分享token的记录
        ).first()
        
        # 构建分享信息
        share_info = None
        if report:
            # 判断是否过期
            is_expired = False
            if report.share_expire_at and datetime.now() > report.share_expire_at:
                is_expired = True
            
            share_info = {
                "share_token": report.share_token,
                "expire_at": report.share_expire_at.isoformat() if report.share_expire_at else None,
                "is_expired": is_expired,
                "has_password": report.share_password is not None,
                "view_count": report.view_count or 0
            }
        
        record_summaries.append({
            "id": assessment.id,
            "questionnaire_id": assessment.questionnaire_id,
            "age": questionnaire.age if questionnaire else None,
            "gender": questionnaire.gender if questionnaire else None,
            "overall_risk_score": float(assessment.overall_risk_score),
            "overall_risk_level": assessment.overall_risk_level,
            "created_at": assessment.created_at.isoformat(),
            "share_info": share_info  # 新增：分享信息
        })
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "records": record_summaries
        }
    }


@router.get("/record/{record_id}", response_model=dict, summary="获取评估记录详情")
async def get_assessment_record(
    record_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取指定评估记录的详细信息
    """
    # 查询评估记录
    assessment = db.query(Assessment).filter(
        Assessment.id == record_id,
        Assessment.user_id == user_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评估记录不存在"
        )
    
    # 查询问卷数据
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == assessment.questionnaire_id
    ).first()
    
    # 查询健康建议
    recommendations = db.query(Recommendation).filter(
        Recommendation.assessment_id == record_id
    ).order_by(Recommendation.priority).all()
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "assessment": assessment.to_dict(),
            "questionnaire": questionnaire.to_dict() if questionnaire else None,
            "recommendations": [rec.to_dict() for rec in recommendations]
        }
    }


@router.delete("/record/{record_id}", summary="删除评估记录")
async def delete_assessment_record(
    record_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除指定的评估记录（级联删除问卷和建议）
    """
    # 查询评估记录
    assessment = db.query(Assessment).filter(
        Assessment.id == record_id,
        Assessment.user_id == user_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评估记录不存在"
        )
    
    # 删除记录（会级联删除recommendations）
    db.delete(assessment)
    db.commit()
    
    return {
        "code": 200,
        "message": "删除成功"
    }


@router.get("/statistics", summary="获取评估统计")
async def get_assessment_statistics(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的评估统计信息
    """
    # 查询所有评估记录
    assessments = db.query(Assessment).filter(
        Assessment.user_id == user_id
    ).order_by(Assessment.created_at.desc()).all()
    
    if not assessments:
        return {
            "code": 200,
            "message": "暂无评估记录",
            "data": {
                "total_assessments": 0,
                "latest_assessment": None,
                "risk_trend": []
            }
        }
    
    # 统计信息
    total_assessments = len(assessments)
    latest_assessment = assessments[0]
    
    # 风险趋势（最近10次）
    risk_trend = []
    for assessment in assessments[:10]:
        risk_trend.append({
            "date": assessment.created_at.isoformat(),
            "score": float(assessment.overall_risk_score),
            "level": assessment.overall_risk_level
        })
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "total_assessments": total_assessments,
            "latest_assessment": {
                "id": latest_assessment.id,
                "score": float(latest_assessment.overall_risk_score),
                "level": latest_assessment.overall_risk_level,
                "date": latest_assessment.created_at.isoformat()
            },
            "risk_trend": risk_trend
        }
    }


@router.get("/export/{record_id}", summary="导出评估报告")
async def export_assessment_report(
    record_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    导出评估报告（返回JSON格式，前端可用于生成PDF）
    """
    # 查询评估记录
    assessment = db.query(Assessment).filter(
        Assessment.id == record_id,
        Assessment.user_id == user_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评估记录不存在"
        )
    
    # 查询问卷数据
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == assessment.questionnaire_id
    ).first()
    
    # 查询健康建议
    recommendations = db.query(Recommendation).filter(
        Recommendation.assessment_id == record_id
    ).order_by(Recommendation.priority).all()
    
    # 获取用户信息
    user = db.query(User).filter(User.id == user_id).first()
    
    # 组装完整报告数据
    report_data = {
        "report_info": {
            "report_id": assessment.id,
            "generated_at": datetime.now().isoformat(),
            "assessment_date": assessment.created_at.isoformat()
        },
        "user_info": {
            "name": user.nickname or "用户",
            "age": questionnaire.age if questionnaire else None,
            "gender": questionnaire.gender if questionnaire else None,
            "bmi": float(questionnaire.bmi) if questionnaire and questionnaire.bmi else None
        },
        "questionnaire_data": questionnaire.to_dict() if questionnaire else {},
        "assessment_result": {
            "overall_risk": {
                "score": float(assessment.overall_risk_score),
                "level": assessment.overall_risk_level,
                "percentile": assessment.risk_percentile
            },
            "category_risks": assessment.category_risks,
            "key_factors": assessment.key_factors,
            "recommendations": [rec.to_dict() for rec in recommendations]
        }
    }
    
    return {
        "code": 200,
        "message": "导出成功",
        "data": report_data
    }


@router.get("/compare", response_model=dict, summary="对比两次评估")
async def compare_assessments(
    id1: str = Query(..., description="第一次评估ID"),
    id2: str = Query(..., description="第二次评估ID"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    对比两次风险评估结果，分析变化趋势
    """
    # 1. 查询两条评估记录
    assessment_1 = db.query(Assessment).filter(
        Assessment.id == id1,
        Assessment.user_id == user_id
    ).first()
    
    assessment_2 = db.query(Assessment).filter(
        Assessment.id == id2,
        Assessment.user_id == user_id
    ).first()
    
    if not assessment_1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"评估记录 {id1} 不存在"
        )
    
    if not assessment_2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"评估记录 {id2} 不存在"
        )
    
    # 2. 确保按时间顺序排列（assessment_1 是早期的）
    if assessment_1.created_at > assessment_2.created_at:
        assessment_1, assessment_2 = assessment_2, assessment_1
    
    # 3. 计算时间差
    time_diff = assessment_2.created_at - assessment_1.created_at
    time_diff_days = time_diff.days
    
    # 4. 计算风险分数变化
    score_1 = float(assessment_1.overall_risk_score)
    score_2 = float(assessment_2.overall_risk_score)
    risk_score_change = score_2 - score_1
    risk_score_change_percentage = (risk_score_change / score_1 * 100) if score_1 != 0 else 0
    risk_level_changed = assessment_1.overall_risk_level != assessment_2.overall_risk_level
    
    # 5. 对比分类风险
    category_risks_comparison = []
    category_risks_1 = assessment_1.category_risks or {}
    category_risks_2 = assessment_2.category_risks or {}
    
    all_categories = set(category_risks_1.keys()) | set(category_risks_2.keys())
    
    for category in all_categories:
        risk_1 = category_risks_1.get(category, {})
        risk_2 = category_risks_2.get(category, {})
        
        score_1_cat = risk_1.get('score', 0)
        score_2_cat = risk_2.get('score', 0)
        change = score_2_cat - score_1_cat
        change_pct = (change / score_1_cat * 100) if score_1_cat != 0 else 0
        
        category_risks_comparison.append({
            "category": category,
            "score_1": score_1_cat,
            "score_2": score_2_cat,
            "change": round(change, 4),
            "change_percentage": round(change_pct, 2)
        })
    
    # 6. 对比关键因素
    key_factors_changes = []
    factors_1 = {f['factor']: f for f in (assessment_1.key_factors or [])}
    factors_2 = {f['factor']: f for f in (assessment_2.key_factors or [])}
    
    all_factors = set(factors_1.keys()) | set(factors_2.keys())
    
    for factor_name in all_factors:
        f1 = factors_1.get(factor_name, {})
        f2 = factors_2.get(factor_name, {})
        
        contrib_1 = f1.get('contribution', 0)
        contrib_2 = f2.get('contribution', 0)
        change = contrib_2 - contrib_1
        
        # 判断改善/恶化/稳定
        if abs(change) < 0.01:
            status_text = "stable"
        elif change > 0:
            status_text = "worsened"  # 贡献度增加意味着风险增加
        else:
            status_text = "improved"  # 贡献度减少意味着风险降低
        
        key_factors_changes.append({
            "factor": factor_name,
            "contribution_1": round(contrib_1, 4),
            "contribution_2": round(contrib_2, 4),
            "change": round(change, 4),
            "status": status_text
        })
    
    # 按变化绝对值排序，取前10个
    key_factors_changes.sort(key=lambda x: abs(x['change']), reverse=True)
    key_factors_changes = key_factors_changes[:10]
    
    # 7. 生成变化总结
    summary_parts = []
    
    if risk_score_change > 0:
        summary_parts.append(f"风险分数上升了 {abs(risk_score_change):.2f} 分（{abs(risk_score_change_percentage):.1f}%）")
    elif risk_score_change < 0:
        summary_parts.append(f"风险分数下降了 {abs(risk_score_change):.2f} 分（{abs(risk_score_change_percentage):.1f}%）")
    else:
        summary_parts.append("风险分数保持不变")
    
    if risk_level_changed:
        summary_parts.append(f"风险等级从「{assessment_1.overall_risk_level}」变为「{assessment_2.overall_risk_level}」")
    
    summary = "。".join(summary_parts) + "。"
    
    # 8. 生成改进建议
    improvement_suggestions = []
    
    # 根据恶化的因素生成建议
    worsened_factors = [f for f in key_factors_changes if f['status'] == 'worsened']
    for factor in worsened_factors[:3]:  # 取前3个恶化因素
        factor_name = factor['factor']
        if '吸烟' in factor_name:
            improvement_suggestions.append("建议戒烟或减少吸烟量")
        elif 'BMI' in factor_name or '体重' in factor_name:
            improvement_suggestions.append("建议控制体重，保持健康的BMI指数")
        elif '运动' in factor_name:
            improvement_suggestions.append("建议增加体育锻炼，每周至少150分钟中等强度运动")
        elif '饮酒' in factor_name:
            improvement_suggestions.append("建议减少饮酒量或戒酒")
        elif '年龄' in factor_name:
            improvement_suggestions.append("建议定期体检，关注年龄相关的健康风险")
    
    # 根据改善的因素给予鼓励
    improved_factors = [f for f in key_factors_changes if f['status'] == 'improved']
    if improved_factors:
        improvement_suggestions.append(f"您在 {improved_factors[0]['factor']} 方面有所改善，请继续保持良好习惯")
    
    if not improvement_suggestions:
        improvement_suggestions.append("请继续保持健康的生活方式，定期进行风险评估")
    
    # 9. 组装返回数据
    return {
        "code": 200,
        "message": "对比分析成功",
        "data": {
            "assessment_1": assessment_1.to_dict(),
            "assessment_2": assessment_2.to_dict(),
            "time_diff_days": time_diff_days,
            "risk_score_change": round(risk_score_change, 4),
            "risk_score_change_percentage": round(risk_score_change_percentage, 2),
            "risk_level_changed": risk_level_changed,
            "category_risks_comparison": category_risks_comparison,
            "key_factors_changes": key_factors_changes,
            "summary": summary,
            "improvement_suggestions": improvement_suggestions
        }
    }


@router.post("/{assessment_id}/ai-recommendation", summary="生成AI个性化建议（SSE流式）")
async def generate_ai_recommendation_stream(
    assessment_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    基于评估结果生成AI个性化健康建议（SSE流式输出）
    
    - 从数据库读取评估和问卷数据
    - 调用DeepSeek生成个性化建议
    - 实时流式返回生成内容
    - 生成完成后保存到数据库
    """
    from app.services.llm_service import llm_service
    
    # 1. 验证评估记录是否存在且属于当前用户
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == user_id
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评估记录不存在"
        )
    
    # 2. 获取问卷数据
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == assessment.questionnaire_id
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="问卷数据不存在"
        )
    
    # 3. 准备数据
    user_data = {
        "age": questionnaire.age,
        "gender": questionnaire.gender,
        "height": float(questionnaire.height),
        "weight": float(questionnaire.weight),
        "smoking_history": questionnaire.smoking_history,
        "exercise_habit": questionnaire.exercise_habit,
        "chronic_diseases": questionnaire.chronic_diseases,
        "family_cancer_history": questionnaire.family_cancer_history,
        "symptoms": questionnaire.symptoms
    }
    
    risk_result = {
        "overall_risk": {
            "score": float(assessment.overall_risk_score),
            "level": assessment.overall_risk_level,
            "percentile": assessment.risk_percentile
        },
        "key_factors": assessment.key_factors or []
    }
    
    # 4. 定义SSE生成器
    async def generate():
        """SSE事件生成器"""
        full_text = []
        
        try:
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'message': '开始生成AI建议...'}, ensure_ascii=False)}\n\n"
            
            # 流式生成内容
            for chunk in llm_service.generate_personalized_recommendations_stream(
                user_data, 
                risk_result
            ):
                full_text.append(chunk)
                # 发送文本块
                yield f"data: {json.dumps({'type': 'text', 'content': chunk}, ensure_ascii=False)}\n\n"
            
            # 生成完整文本
            complete_text = ''.join(full_text)
            
            # 5. 保存到数据库
            assessment.ai_recommendation = complete_text
            db.commit()
            
            # 发送完成事件
            yield f"data: {json.dumps({'type': 'done', 'message': '生成完成', 'total_length': len(complete_text)}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            # 发送错误事件
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
    
    # 6. 返回SSE流
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用nginx缓冲
        }
    )


@router.get("/trend", response_model=dict, summary="获取风险趋势分析")
async def get_risk_trend(
    months: int = Query(12, ge=1, le=60, description="查询近N个月的数据"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户风险趋势分析数据，包含各分类风险历史走势和AI洞察
    """
    from datetime import timedelta
    
    # 查询时间范围内的评估记录
    start_date = datetime.now() - timedelta(days=30 * months)
    
    assessments = db.query(Assessment).filter(
        Assessment.user_id == user_id,
        Assessment.created_at >= start_date
    ).order_by(Assessment.created_at.asc()).all()
    
    if not assessments or len(assessments) < 1:
        return {
            "code": 200,
            "message": "暂无评估记录",
            "data": {
                "has_data": False,
                "insights": "暂无评估数据，建议完成首次风险评估",
                "trend_data": []
            }
        }
    
    # 构建趋势数据
    trend_data = []
    for assessment in assessments:
        # 解析分类风险数据
        category_risks = assessment.category_risks or {}
        
        trend_data.append({
            "assessment_id": assessment.id,
            "date": assessment.created_at.strftime("%Y-%m-%d"),
            "month": assessment.created_at.strftime("%Y-%m"),
            "overall_score": float(assessment.overall_risk_score),
            "overall_level": assessment.overall_risk_level,
            "risk_percentile": assessment.risk_percentile,
            "category_scores": {
                "lung": float(category_risks.get("lung", {}).get("score", 0)),
                "liver": float(category_risks.get("liver", {}).get("score", 0)),
                "stomach": float(category_risks.get("stomach", {}).get("score", 0)),
                "colorectal": float(category_risks.get("colorectal", {}).get("score", 0)),
                "breast": float(category_risks.get("breast", {}).get("score", 0)),
                "esophageal": float(category_risks.get("esophageal", {}).get("score", 0))
            },
            "key_factors": [
                {
                    "factor": factor.get("factor", ""),
                    "importance": float(factor.get("importance", 0)),
                    "contribution": float(factor.get("contribution", 0))
                }
                for factor in (assessment.key_factors or [])[:3]
            ]
        })
    
    # 计算改善指标
    improvements = []
    risk_changes = []
    
    for i in range(1, len(trend_data)):
        prev = trend_data[i - 1]
        curr = trend_data[i]
        
        # 综合风险变化
        overall_change = curr["overall_score"] - prev["overall_score"]
        risk_changes.append({
            "period": f"{prev['month']} -> {curr['month']}",
            "change": round(overall_change, 4),
            "direction": "下降" if overall_change < 0 else "上升" if overall_change > 0 else "持平"
        })
        
        # 各分类风险变化
        for category in ["lung", "liver", "stomach", "colorectal", "breast", "esophageal"]:
            cat_change = curr["category_scores"][category] - prev["category_scores"][category]
            if abs(cat_change) >= 0.05:  # 变化超过5%才记录
                improvements.append({
                    "period": f"{prev['month']} -> {curr['month']}",
                    "category": category,
                    "change": round(cat_change, 4),
                    "direction": "改善" if cat_change < 0 else "上升"
                })
    
    # 生成趋势洞察文案
    first_record = trend_data[0]
    latest_record = trend_data[-1]
    total_change = latest_record["overall_score"] - first_record["overall_score"]
    
    # 根据变化趋势生成不同的洞察
    if len(trend_data) == 1:
        insights = "您已完成首次风险评估，建议保持健康生活方式并定期复查。"
    elif total_change < -0.1:
        insights = f"恭喜！您的风险评分较 {len(trend_data)} 个月前下降了 {abs(total_change)*100:.1f}%，健康管理效果显著。请继续保持良好的生活习惯。"
    elif total_change > 0.1:
        insights = f"注意：您的风险评分较 {len(trend_data)} 个月前上升了 {total_change*100:.1f}%。建议加强健康管理，如有疑虑请咨询专业医生。"
    else:
        insights = f"您的风险水平在 {len(trend_data)} 个月内保持稳定，风险评分波动在 {(abs(total_change)*100):.1f}% 以内。继续保持现有的健康管理措施。"
    
    # 添加具体改善建议
    if improvements:
        recent_improvements = [imp for imp in improvements if imp["direction"] == "改善"][-3:]
        if recent_improvements:
            insights += f" 其中，{'、'.join([get_category_name(imp['category']) for imp in recent_improvements])}风险有所改善。"
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "has_data": True,
            "total_records": len(trend_data),
            "time_range": {
                "start": trend_data[0]["date"],
                "end": trend_data[-1]["date"]
            },
            "latest_score": latest_record["overall_score"],
            "latest_level": latest_record["overall_level"],
            "first_score": first_record["overall_score"],
            "total_change": round(total_change, 4),
            "change_percentage": round(total_change * 100, 2),
            "trend_direction": "下降" if total_change < 0 else "上升" if total_change > 0 else "持平",
            "insights": insights,
            "improvements": improvements,
            "risk_changes": risk_changes,
            "trend_data": trend_data
        }
    }


def get_category_name(category_code: str) -> str:
    """获取分类风险的中文名称"""
    category_names = {
        "lung": "肺癌",
        "liver": "肝癌",
        "stomach": "胃癌",
        "colorectal": "肠癌",
        "breast": "乳腺癌",
        "esophageal": "食管癌"
    }
    return category_names.get(category_code, category_code)

