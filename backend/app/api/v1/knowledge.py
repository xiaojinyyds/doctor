#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""知识图谱API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.assessment import Assessment
from app.models.questionnaire import Questionnaire
from app.services.knowledge_graph import knowledge_graph_service

router = APIRouter()


@router.get("/graph", summary="获取通用肿瘤知识图谱")
async def get_knowledge_graph():
    """
    获取完整的肿瘤知识图谱
    
    包含：
    - 疾病节点（肺癌、胃癌、肝癌等）
    - 风险因素节点（吸烟、年龄、遗传等）
    - 症状节点（咳嗽、胸痛等）
    - 筛查方法节点（CT、胃镜等）
    - 节点之间的关系边
    """
    try:
        graph_data = knowledge_graph_service.get_full_graph()
        
        return {
            "code": 200,
            "message": "获取知识图谱成功",
            "data": graph_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识图谱失败: {str(e)}"
        )


@router.get("/user-risk-graph/{assessment_id}", summary="获取用户个性化风险图谱")
async def get_user_risk_graph(
    assessment_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户个性化风险图谱
    
    基于用户的评估结果，生成专属的风险关系图：
    - 用户节点（中心）
    - 用户具有的风险因素
    - 高风险的疾病类型
    - 推荐的筛查方法
    """
    try:
        # 1. 查询评估记录
        assessment = db.query(Assessment).filter(
            Assessment.id == assessment_id,
            Assessment.user_id == user_id
        ).first()
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评估记录不存在"
            )
        
        # 2. 查询问卷数据
        questionnaire = db.query(Questionnaire).filter(
            Questionnaire.id == assessment.questionnaire_id
        ).first()
        
        if not questionnaire:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="问卷数据不存在"
            )
        
        # 3. 准备用户数据
        user_data = {
            'age': questionnaire.age,
            'gender': questionnaire.gender,
            'height': float(questionnaire.height),
            'weight': float(questionnaire.weight),
            'smoking': 1 if questionnaire.smoking_history.get('is_smoking') else 0,
            'genetic_risk': 1 if questionnaire.family_cancer_history else 0,
            'physical_activity': float(questionnaire.exercise_habit.split('小时')[0]) if '小时' in questionnaire.exercise_habit else 5.0,
            'alcohol_intake': questionnaire.alcohol_history.get('intake_level', 0)
        }
        
        # 4. 准备评估结果
        assessment_result = {
            'overall_risk': {
                'score': float(assessment.overall_risk_score),
                'level': assessment.overall_risk_level
            },
            'category_risks': assessment.category_risks,
            'key_factors': assessment.key_factors
        }
        
        # 5. 生成个性化图谱
        user_graph = knowledge_graph_service.get_user_risk_graph(
            user_data, 
            assessment_result
        )
        
        return {
            "code": 200,
            "message": "获取个性化风险图谱成功",
            "data": {
                "graph": user_graph,
                "assessment_info": {
                    "assessment_id": assessment_id,
                    "risk_level": assessment.overall_risk_level,
                    "risk_score": float(assessment.overall_risk_score),
                    "created_at": assessment.created_at.isoformat()
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成个性化风险图谱失败: {str(e)}"
        )


@router.get("/disease/{disease_id}", summary="获取疾病详细信息")
async def get_disease_info(disease_id: str):
    """
    获取特定疾病的详细信息
    
    包括：
    - 相关风险因素
    - 常见症状
    - 推荐筛查方法
    """
    try:
        graph_data = knowledge_graph_service.get_full_graph()
        
        # 查找疾病节点
        disease_node = next(
            (node for node in graph_data['nodes'] if node['id'] == disease_id),
            None
        )
        
        if not disease_node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="疾病信息不存在"
            )
        
        # 查找相关的边
        risk_factors = []
        symptoms = []
        screenings = []
        
        for edge in graph_data['edges']:
            # 风险因素 → 疾病
            if edge['target'] == disease_id:
                source_node = next(
                    (n for n in graph_data['nodes'] if n['id'] == edge['source']),
                    None
                )
                if source_node and source_node['type'] == 'risk_factor':
                    risk_factors.append({
                        **source_node,
                        'relation': edge['relation'],
                        'weight': edge['weight']
                    })
            
            # 疾病 → 症状
            if edge['source'] == disease_id:
                target_node = next(
                    (n for n in graph_data['nodes'] if n['id'] == edge['target']),
                    None
                )
                if target_node:
                    if target_node['type'] == 'symptom':
                        symptoms.append({
                            **target_node,
                            'relation': edge['relation'],
                            'weight': edge['weight']
                        })
                    elif target_node['type'] == 'screening':
                        screenings.append({
                            **target_node,
                            'relation': edge['relation'],
                            'weight': edge['weight']
                        })
        
        return {
            "code": 200,
            "message": "获取疾病信息成功",
            "data": {
                "disease": disease_node,
                "risk_factors": risk_factors,
                "symptoms": symptoms,
                "screenings": screenings
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取疾病信息失败: {str(e)}"
        )

