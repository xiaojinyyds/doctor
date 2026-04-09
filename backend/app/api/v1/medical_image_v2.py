"""
医学影像API V2 - 包含历史记录、统计、可视化等完整功能
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date
import uuid
import logging
from PIL import Image
import io

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.medical_image_service import MedicalImageService
from app.models.medical_image import ImageAnalysisResult
from app.schemas.medical_image import (
    MedicalImageCreate, MedicalImageResponse,
    ImageAnalysisResultResponse, ImageAnalysisResultDetail,
    ImageAnalysisStats, DoctorReviewRequest
)
from app.utils.oss_client import oss_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload-and-analyze", summary="上传并分析医学影像")
async def upload_and_analyze_image(
    file: UploadFile = File(..., description="医学影像文件"),
    image_type: str = Query("breast_ultrasound", description="影像类型"),
    body_part: str = Query("breast", description="检查部位"),
    acquisition_date: Optional[date] = Query(None, description="影像采集日期"),
    institution: Optional[str] = Query(None, description="检查机构"),
    generate_heatmap: bool = Query(False, description="是否生成热力图"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    上传医学影像并进行AI分析
    
    完整流程：
    1. 验证文件格式和大小
    2. 上传到阿里云OSS
    3. 保存影像记录到数据库
    4. 执行AI分析
    5. 保存分析结果到数据库
    6. （可选）生成热力图
    
    返回影像记录和分析结果（包含OSS URL）
    """
    try:
        # 1. 验证文件
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件类型错误，请上传图像文件")
        
        # 读取文件
        image_bytes = await file.read()
        
        # 验证文件大小（最大10MB）
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="文件大小超过限制（最大10MB）")
        
        # 验证是否为有效图像
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
            img = Image.open(io.BytesIO(image_bytes))  # 重新打开（verify后需要重新打开）
            img_width, img_height = img.size
        except Exception:
            raise HTTPException(status_code=400, detail="无效的图像文件")
        
        # 2. 上传到阿里云OSS
        try:
            oss_result = oss_client.upload_file(
                file_content=image_bytes,
                filename=file.filename,
                folder=f"medical-images/{image_type}/{user_id}"
            )
            file_url = oss_result['url']
            logger.info(f"图像已上传到OSS: {file_url}")
        except Exception as e:
            logger.error(f"OSS上传失败: {e}")
            raise HTTPException(status_code=500, detail=f"图像上传失败: {str(e)}")
        
        # 3. 保存影像记录到数据库
        image_data = MedicalImageCreate(
            original_filename=file.filename,
            file_url=file_url,
            file_size=len(image_bytes),
            file_format=file.filename.split('.')[-1].lower(),
            image_type=image_type,
            body_part=body_part,
            image_width=img_width,
            image_height=img_height,
            acquisition_date=acquisition_date,
            institution=institution
        )
        
        medical_image = MedicalImageService.create_medical_image(db, user_id, image_data)
        
        # 4. 执行AI分析
        analysis_result = MedicalImageService.analyze_image(
            db=db,
            image_id=medical_image.id,
            user_id=user_id,
            image_bytes=image_bytes,
            generate_heatmap=generate_heatmap
        )
        
        # 5. 构建响应
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '上传并分析成功',
                'data': {
                    'image': {
                        'id': medical_image.id,
                        'filename': medical_image.original_filename,
                        'file_url': medical_image.file_url,
                        'image_type': medical_image.image_type,
                        'size': f"{img_width}x{img_height}",
                        'upload_time': medical_image.created_at.isoformat()
                    },
                    'analysis': {
                        'id': analysis_result.id,
                        'predicted_class': analysis_result.predicted_class_cn,
                        'confidence': float(analysis_result.confidence),
                        'confidence_percentage': f"{float(analysis_result.confidence) * 100:.2f}%",
                        'risk_level': analysis_result.risk_level,
                        'recommendation': analysis_result.ai_recommendation,
                        'probabilities': {
                            '正常': float(analysis_result.prob_normal or 0),
                            '良性肿瘤': float(analysis_result.prob_benign or 0),
                            '恶性肿瘤': float(analysis_result.prob_malignant or 0)
                        },
                        'annotated_image_url': analysis_result.heatmap_url,  # 标注图URL
                        'heatmap_url': analysis_result.heatmap_url,  # 保持兼容
                        'inference_time_ms': analysis_result.inference_time_ms,
                        'analyzed_at': analysis_result.created_at.isoformat()
                    }
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传并分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/history", summary="获取用户的影像分析历史")
async def get_user_image_history(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="限制数量"),
    image_type: Optional[str] = Query(None, description="影像类型过滤"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户的医学影像历史记录
    
    支持分页和类型过滤
    """
    try:
        # 获取影像列表
        images = MedicalImageService.get_user_images(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit,
            image_type=image_type
        )
        
        # 构建响应数据
        history_data = []
        for img in images:
            # 获取该影像的最新分析结果
            analysis_results = MedicalImageService.get_image_analysis_results(db, img.id)
            latest_result = analysis_results[0] if analysis_results else None
            
            history_data.append({
                'image': {
                    'id': img.id,
                    'filename': img.original_filename,
                    'file_url': img.file_url,
                    'image_type': img.image_type,
                    'upload_time': img.created_at.isoformat(),
                    'analysis_status': img.analysis_status
                },
                'latest_analysis': {
                    'id': latest_result.id,
                    'predicted_class': latest_result.predicted_class_cn,
                    'confidence': float(latest_result.confidence),
                    'risk_level': latest_result.risk_level,
                    'analyzed_at': latest_result.created_at.isoformat()
                } if latest_result else None
            })
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '获取成功',
                'data': {
                    'total': len(history_data),
                    'skip': skip,
                    'limit': limit,
                    'items': history_data
                }
            }
        )
        
    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/statistics", summary="获取影像分析统计")
async def get_analysis_statistics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户的影像分析统计信息
    
    包括：
    - 总影像数、已分析数、待分析数
    - 各类别分布
    - 平均置信度
    - 高风险数量
    """
    try:
        start_date = datetime.now() - __import__('datetime').timedelta(days=days)
        
        stats = MedicalImageService.get_analysis_statistics(
            db=db,
            user_id=user_id,
            start_date=start_date
        )
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '获取成功',
                'data': {
                    'period_days': days,
                    'statistics': {
                        'total_images': stats.total_images,
                        'analyzed_images': stats.analyzed_images,
                        'pending_images': stats.pending_images,
                        'distribution': {
                            '正常': stats.normal_count,
                            '良性肿瘤': stats.benign_count,
                            '恶性肿瘤': stats.malignant_count
                        },
                        'average_confidence': stats.average_confidence,
                        'high_risk_count': stats.high_risk_count
                    }
                }
            }
        )
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/risk-trend", summary="获取风险趋势")
async def get_risk_trend(
    days: int = Query(30, ge=7, le=365, description="趋势天数"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户的风险趋势数据
    
    用于绘制风险趋势图表
    """
    try:
        trend_data = MedicalImageService.get_risk_trend(
            db=db,
            user_id=user_id,
            days=days
        )
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '获取成功',
                'data': {
                    'period_days': days,
                    'trend': trend_data
                }
            }
        )
        
    except Exception as e:
        logger.error(f"获取风险趋势失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/compare", summary="对比两张影像的分析结果")
async def compare_images(
    image_id_1: str = Body(..., description="第一张影像ID"),
    image_id_2: str = Body(..., description="第二张影像ID"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    对比两张影像的分析结果
    
    用于观察病情变化趋势
    """
    try:
        comparison = MedicalImageService.compare_images(
            db=db,
            image_id_1=image_id_1,
            image_id_2=image_id_2,
            user_id=user_id
        )
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '对比成功',
                'data': comparison
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"影像对比失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/result/{result_id}", summary="获取分析结果详情")
async def get_analysis_result_detail(
    result_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取影像分析结果的详细信息
    """
    try:
        result = MedicalImageService.get_analysis_result_by_id(db, result_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="分析结果不存在")
        
        # 验证权限
        if result.user_id != user_id:
            raise HTTPException(status_code=403, detail="无权访问此分析结果")
        
        # 获取关联的影像信息
        image = MedicalImageService.get_image_by_id(db, result.image_id)
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '获取成功',
                'data': {
                    'result': {
                        'id': result.id,
                        'predicted_class': result.predicted_class_cn,
                        'confidence': float(result.confidence),
                        'risk_level': result.risk_level,
                        'recommendation': result.ai_recommendation,
                        'probabilities': {
                            '正常': float(result.prob_normal or 0),
                            '良性肿瘤': float(result.prob_benign or 0),
                            '恶性肿瘤': float(result.prob_malignant or 0)
                        },
                        'model_info': {
                            'name': result.model_name,
                            'version': result.model_version,
                            'inference_time_ms': result.inference_time_ms
                        },
                        'annotated_image_url': result.heatmap_url,  # 标注图URL
                        'heatmap_url': result.heatmap_url,
                        'reviewed_by_doctor': result.reviewed_by_doctor,
                        'doctor_opinion': result.doctor_opinion,
                        'analyzed_at': result.created_at.isoformat()
                    },
                    'image': {
                        'id': image.id,
                        'filename': image.original_filename,
                        'file_url': image.file_url,
                        'size': f"{image.image_width}x{image.image_height}" if image.image_width else None,
                        'uploaded_at': image.created_at.isoformat()
                    } if image else None
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分析结果详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/pending-review", summary="获取待审核影像列表")
async def get_pending_review_list(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="限制数量"),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取待审核的影像分析结果列表（医生专用）
    
    返回所有未经医生审核的分析结果
    """
    try:
        from sqlalchemy import desc
        
        # 查询未审核的分析结果
        query = db.query(ImageAnalysisResult)\
            .filter(ImageAnalysisResult.reviewed_by_doctor == False)\
            .order_by(desc(ImageAnalysisResult.created_at))
        
        total = query.count()
        results = query.offset(skip).limit(limit).all()
        
        # 构建返回数据
        items = []
        for result in results:
            try:
                image = MedicalImageService.get_image_by_id(db, result.image_id)
                
                # 只返回有OSS URL的记录（跳过本地路径的旧数据）
                if image and image.file_url and (image.file_url.startswith('http://') or image.file_url.startswith('https://')):
                    items.append({
                        'result': {
                            'id': result.id,
                            'image_id': result.image_id,
                            'user_id': result.user_id,
                            'predicted_class': result.predicted_class_cn,
                            'confidence': float(result.confidence),
                            'risk_level': result.risk_level,
                            'probabilities': {
                                '正常': float(result.prob_normal or 0),
                                '良性肿瘤': float(result.prob_benign or 0),
                                '恶性肿瘤': float(result.prob_malignant or 0)
                            },
                            'ai_recommendation': result.ai_recommendation,
                            'annotated_image_url': result.heatmap_url,
                            'analyzed_at': result.created_at.isoformat()
                        },
                        'image': {
                            'id': image.id,
                            'filename': image.original_filename,
                            'file_url': image.file_url,
                            'uploaded_at': image.created_at.isoformat()
                        }
                    })
            except Exception as e:
                logger.warning(f"跳过无效记录: {result.id}, 错误: {e}")
                continue
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '获取成功',
                'data': {
                    'total': len(items),  # 返回实际有效项数
                    'skip': skip,
                    'limit': limit,
                    'items': items
                }
            }
        )
        
    except Exception as e:
        logger.error(f"获取待审核列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/result/{result_id}/review", summary="医生审核分析结果")
async def doctor_review_result(
    result_id: str,
    review_data: DoctorReviewRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    医生审核AI分析结果
    
    仅医生角色可以调用
    """
    try:
        # TODO: 验证用户是否为医生角色
        
        result = MedicalImageService.doctor_review(
            db=db,
            result_id=result_id,
            doctor_id=user_id,
            doctor_opinion=review_data.doctor_opinion,
            true_label=review_data.true_label
        )
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '审核成功',
                'data': {
                    'result_id': result.id,
                    'reviewed_at': result.reviewed_at.isoformat() if result.reviewed_at else None
                }
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"医生审核失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.delete("/image/{image_id}", summary="删除医学影像")
async def delete_image(
    image_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    删除医学影像（同时删除关联的分析结果）
    """
    try:
        success = MedicalImageService.delete_image(db, image_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="影像不存在或无权删除")
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '删除成功',
                'data': {'image_id': image_id}
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除影像失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/dashboard", summary="影像分析仪表板")
async def get_dashboard_data(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取用户的影像分析仪表板数据
    
    包括：
    - 统计信息
    - 最近分析记录
    - 风险趋势
    """
    try:
        # 统计信息（最近30天）
        stats = MedicalImageService.get_analysis_statistics(
            db=db,
            user_id=user_id,
            start_date=datetime.now() - __import__('datetime').timedelta(days=30)
        )
        
        # 最近5次分析
        recent_analyses = MedicalImageService.get_user_analysis_history(
            db=db,
            user_id=user_id,
            skip=0,
            limit=5
        )
        
        # 风险趋势（最近30天）
        risk_trend = MedicalImageService.get_risk_trend(
            db=db,
            user_id=user_id,
            days=30
        )
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '获取成功',
                'data': {
                    'statistics': {
                        'total_images': stats.total_images,
                        'analyzed_images': stats.analyzed_images,
                        'pending_images': stats.pending_images,
                        'distribution': {
                            '正常': stats.normal_count,
                            '良性肿瘤': stats.benign_count,
                            '恶性肿瘤': stats.malignant_count
                        },
                        'average_confidence': stats.average_confidence,
                        'high_risk_count': stats.high_risk_count
                    },
                    'recent_analyses': [
                        {
                            'id': r.id,
                            'image_id': r.image_id,
                            'predicted_class': r.predicted_class_cn,
                            'confidence': float(r.confidence),
                            'risk_level': r.risk_level,
                            'analyzed_at': r.created_at.isoformat()
                        }
                        for r in recent_analyses
                    ],
                    'risk_trend': risk_trend
                }
            }
        )
        
    except Exception as e:
        logger.error(f"获取仪表板数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

