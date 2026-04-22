#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
风险评估API V2.0 - 适配新模型和扩展问卷
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import json
import time
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user_id, get_current_user
from app.models.questionnaire import Questionnaire
from app.models.assessment import Assessment, Recommendation, Report
from app.schemas.questionnaire import QuestionnaireV2Request
from app.schemas.response import ApiResponse
from app.services.risk_engine_v2 import assess_risk_v2
from app.services.llm_service import llm_service
from app.utils.helpers import generate_uuid

router = APIRouter()


@router.post("/submit-v2", summary="提交问卷并获取风险评估（V2.0完整版）")
async def submit_assessment_v2(
    questionnaire: QuestionnaireV2Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # B2B升级：获取完整用户信息
):
    """
    提交完整问卷数据，使用V2.0模型进行风险评估
    
    **新增字段：**
    - 环境与职业暴露（3项）
    - 详细饮食习惯（5项）
    - 女性特有因素（4项）
    - 精神压力与作息（3项）
    - 体检与筛查历史（2项）
    
    **B2B升级：**
    - 评估结果默认状态为 pending（待审核）
    - 自动关联租户ID
    """
    try:
        start_time = time.time()
        user_id = current_user.user_id  # B2B升级
        tenant_id = current_user.tenant_id  # B2B升级
        
        # 1. 保存问卷数据到数据库（B2B升级：增加租户ID）
        questionnaire_id = generate_uuid()
        questionnaire_record = Questionnaire(
            id=questionnaire_id,
            user_id=user_id,
            tenant_id=tenant_id,  # B2B升级
            
            # 基础信息
            age=questionnaire.age,
            gender=questionnaire.gender,
            height=Decimal(str(questionnaire.height)),
            weight=Decimal(str(questionnaire.weight)),
            # BMI由数据库自动计算
            
            # 生活习惯
            smoking_history={
                'status': questionnaire.smoking_status,
                'years': questionnaire.smoking_years,
                'amount': questionnaire.smoking_amount
            },
            alcohol_history={
                'frequency': questionnaire.alcohol_frequency,
                'amount': questionnaire.alcohol_amount
            },
            exercise_habit=f"{questionnaire.exercise_hours_per_week}小时/周，强度：{questionnaire.exercise_intensity}",
            diet_habits={
                'vegetable_fruit': questionnaire.vegetable_fruit_intake,
                'red_meat': questionnaire.red_meat_intake,
                'processed_food': questionnaire.processed_food_intake,
                'pickled_food': questionnaire.pickled_food_intake,
                'dairy': questionnaire.dairy_intake
            },
            sleep_quality=f"{questionnaire.sleep_hours}小时/天，{questionnaire.sleep_quality}",
            
            # 疾病史
            chronic_diseases=questionnaire.chronic_diseases,
            family_cancer_history=questionnaire.family_cancer_history,
            surgery_history=questionnaire.surgery_history,
            medication_history=questionnaire.medication_history,
            
            # 症状
            symptoms=questionnaire.symptoms,
            recent_abnormalities=questionnaire.recent_abnormalities,
            last_checkup=questionnaire.last_checkup,
            
            # 环境与职业暴露
            occupational_exposure=questionnaire.occupational_exposure,
            environmental_factors=questionnaire.environmental_factors,
            living_environment=questionnaire.living_environment,
            
            # 详细饮食
            vegetable_fruit_intake=questionnaire.vegetable_fruit_intake,
            red_meat_intake=questionnaire.red_meat_intake,
            processed_food_intake=questionnaire.processed_food_intake,
            pickled_food_intake=questionnaire.pickled_food_intake,
            dairy_intake=questionnaire.dairy_intake,
            
            # 女性特有
            menstrual_status=questionnaire.menstrual_status,
            pregnancy_history=questionnaire.pregnancy_history,
            breastfeeding_history=questionnaire.breastfeeding_history,
            hormone_therapy=questionnaire.hormone_therapy,
            
            # 压力作息
            stress_level=questionnaire.stress_level,
            work_rest_pattern=questionnaire.work_rest_pattern,
            mental_health=questionnaire.mental_health,
            
            # 筛查历史
            screening_history=questionnaire.screening_history,
            abnormal_results_history=questionnaire.abnormal_results_history,
            
            status='completed'
        )
        
        db.add(questionnaire_record)
        db.flush()  # 确保问卷记录存在
        
        # 2. 准备评估数据（转换为模型需要的格式）
        assessment_data = questionnaire.model_dump()
        
        # 3. 调用V2.0风险评估引擎
        print(f"🔍 开始V2.0风险评估...")
        result = assess_risk_v2(assessment_data)
        
        # 4. 调用DeepSeek生成AI个性化建议
        print(f"🤖 调用DeepSeek生成个性化建议...")
        ai_recommendation = llm_service.generate_personalized_recommendations(
            user_data=assessment_data,
            risk_result=result
        )
        
        # 5. 保存评估结果（B2B升级：默认状态为pending）
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
            model_version='v2.0_enhanced',
            inference_time_ms=int((time.time() - start_time) * 1000),
            ai_recommendation=ai_recommendation,
            # B2B升级：新增字段
            status='pending',  # 默认待审核
            tenant_id=tenant_id  # 租户ID
        )
        
        db.add(assessment_record)
        db.flush()  # 先flush确保assessment_id可用
        
        # 6. 保存健康建议到数据库
        recommendations_records = []
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
            recommendations_records.append(recommendation)
        
        # 7. 创建报告记录
        report_id = generate_uuid()
        report = Report(
            id=report_id,
            user_id=user_id,
            assessment_id=assessment_id,
            report_type='web'
        )
        db.add(report)
        
        # 提交所有更改
        db.commit()
        db.refresh(assessment_record)
        
        print(f"✅ 评估完成！风险等级: {result['overall_risk']['level']}")
        
        # 8. 返回完整详细结果
        return ApiResponse.success(
            data={
                'assessment_id': assessment_id,
                'questionnaire_id': questionnaire_id,
                'report_id': report_id,
                
                # 评估结果
                'assessment_result': {
                    'overall_risk': result['overall_risk'],
                    'category_risks': result['category_risks'],
                    'key_factors': result['key_factors'],
                    'recommendations': [rec.to_dict() for rec in recommendations_records],
                    'ai_recommendation': ai_recommendation,
                },
                
                # 用户画像分析
                'user_profile': {
                    'age': questionnaire.age,
                    'gender': questionnaire.gender,
                    'bmi': float(assessment_data.get('weight', 0)) / ((assessment_data.get('height', 165) / 100) ** 2),
                    'smoking_status': questionnaire.smoking_status,
                    'exercise_level': questionnaire.exercise_hours_per_week,
                    'stress_level': questionnaire.stress_level,
                },
                
                # 特征重要性（前10）
                'feature_importance': result['key_factors'][:10],
                
                # SHAP可视化数据
                'shap_analysis': {
                    'values': result.get('shap_values'),
                    'feature_values': result.get('feature_values')
                },
                
                # 模型信息
                'model_info': {
                    'version': 'v2.0_enhanced',
                    'feature_count': 32,
                    'inference_time_ms': assessment_record.inference_time_ms,
                    'accuracy': 0.8121,
                    'auc': 0.8014
                },
                
                'created_at': assessment_record.created_at.isoformat()
            },
            message="风险评估完成（V2.0增强版）"
        )
        
    except Exception as e:
        db.rollback()
        print(f"❌ 评估失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"风险评估失败: {str(e)}"
        )


@router.get("/detail-v2/{assessment_id}", summary="获取评估详情（V2.0）")
async def get_assessment_detail_v2(
    assessment_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取指定评估的完整详情
    
    Args:
        assessment_id: 评估记录ID
        
    Returns:
        完整的评估结果，包括问卷数据、风险评估、建议等
    """
    try:
        # 查询评估记录
        assessment = db.query(Assessment).filter(
            Assessment.id == assessment_id,
            Assessment.user_id == user_id
        ).first()
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评估记录不存在"
            )
        
        # 查询关联的问卷数据
        questionnaire = db.query(Questionnaire).filter(
            Questionnaire.id == assessment.questionnaire_id
        ).first()
        
        # 查询建议列表
        recommendations = db.query(Recommendation).filter(
            Recommendation.assessment_id == assessment_id
        ).all()
        
        # 查询报告记录
        report = db.query(Report).filter(
            Report.assessment_id == assessment_id
        ).first()
        
        # 构造返回数据
        return ApiResponse.success(
            data={
                'assessment_id': assessment.id,
                'questionnaire_id': assessment.questionnaire_id,
                'report_id': report.id if report else None,
                
                # 评估结果
                'assessment_result': {
                    'overall_risk': {
                        'score': float(assessment.overall_risk_score),
                        'level': assessment.overall_risk_level,
                        'percentile': float(assessment.risk_percentile) if assessment.risk_percentile else 50
                    },
                    'category_risks': assessment.category_risks or {},
                    'key_factors': assessment.key_factors or [],
                    'recommendations': [rec.to_dict() for rec in recommendations],
                    'ai_recommendation': assessment.ai_recommendation or '',
                },
                
                # 用户画像分析
                'user_profile': {
                    'age': questionnaire.age if questionnaire else 0,
                    'gender': questionnaire.gender if questionnaire else '未知',
                    'bmi': float(questionnaire.bmi) if questionnaire and questionnaire.bmi else 0,
                    'smoking_status': questionnaire.smoking_history.get('status', 0) if questionnaire and questionnaire.smoking_history else 0,
                    'exercise_level': 0,  # 从问卷数据中提取
                    'stress_level': questionnaire.stress_level if questionnaire else '未知',
                } if questionnaire else {},
                
                # 特征重要性
                'feature_importance': assessment.key_factors[:10] if assessment.key_factors else [],
                
                # SHAP分析
                'shap_analysis': {
                    'values': assessment.shap_values,
                    'feature_values': {}
                },
                
                # 模型信息
                'model_info': {
                    'version': assessment.model_version or 'v2.0_enhanced',
                    'feature_count': 32,
                    'inference_time_ms': assessment.inference_time_ms or 0,
                    'accuracy': 0.8121,
                    'auc': 0.8014
                },
                
                'created_at': assessment.created_at.isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 获取评估详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评估详情失败: {str(e)}"
        )


@router.get("/history-v2", summary="获取评估历史记录（V2.0）")
async def get_assessment_history_v2(
    page: int = 1,
    page_size: int = 10,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户的所有评估历史记录
    
    Args:
        page: 页码（从1开始）
        page_size: 每页数量
        
    Returns:
        评估历史记录列表（包含分页信息）
    """
    try:
        # 计算偏移量
        skip = (page - 1) * page_size
        
        # 查询总数
        total = db.query(Assessment).filter(
            Assessment.user_id == user_id
        ).count()
        
        # 查询记录列表
        assessments = db.query(Assessment).filter(
            Assessment.user_id == user_id
        ).order_by(Assessment.created_at.desc()).offset(skip).limit(page_size).all()
        
        # 构造返回数据
        records = []
        for assessment in assessments:
            # 查询关联的报告
            report = db.query(Report).filter(
                Report.assessment_id == assessment.id
            ).first()
            
            records.append({
                'id': assessment.id,
                'questionnaire_id': assessment.questionnaire_id,
                'report_id': report.id if report else None,
                'overall_risk_score': float(assessment.overall_risk_score),
                'overall_risk_level': assessment.overall_risk_level,
                'risk_percentile': float(assessment.risk_percentile) if assessment.risk_percentile else 50,
                'model_version': assessment.model_version,
                'created_at': assessment.created_at.isoformat(),
                'share_info': None  # 如果需要分享信息，可以关联查询
            })
        
        return ApiResponse.success(
            data={
                'records': records,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        )
        
    except Exception as e:
        print(f"❌ 获取历史记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史记录失败: {str(e)}"
        )
