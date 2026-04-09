"""
图像识别API路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from datetime import datetime

from app.services.image_recognition import get_image_recognition_service
from app.core.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", summary="上传图像进行识别")
async def predict_image(
    file: UploadFile = File(..., description="乳腺超声图像文件"),
    db: Session = Depends(get_db)
):
    """
    上传乳腺超声图像进行识别
    
    - **file**: 图像文件（支持 PNG, JPG, JPEG格式）
    
    返回识别结果，包括预测类别、置信度、风险等级和建议
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="文件类型错误，请上传图像文件"
            )
        
        # 验证文件格式
        allowed_extensions = ['png', 'jpg', 'jpeg']
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式，请上传 {', '.join(allowed_extensions)} 格式的图像"
            )
        
        # 读取图像数据
        image_bytes = await file.read()
        
        # 验证文件大小（限制10MB）
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="文件大小超过限制（最大10MB）"
            )
        
        # 获取识别服务
        service = get_image_recognition_service()
        
        # 执行预测
        result = service.predict_from_bytes(image_bytes)
        
        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=result.get('message', '图像识别失败')
            )
        
        # 添加额外信息
        result['filename'] = file.filename
        result['timestamp'] = datetime.now().isoformat()
        
        logger.info(f"图像识别成功: {file.filename} -> {result['predicted_class_cn']}")
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '识别成功',
                'data': result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图像识别API错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器错误: {str(e)}"
        )


@router.get("/model-info", summary="获取模型信息")
async def get_model_info():
    """
    获取图像识别模型的信息
    
    返回模型名称、类型、支持的类别等信息
    """
    try:
        service = get_image_recognition_service()
        info = service.get_model_info()
        
        return JSONResponse(
            status_code=200,
            content={
                'code': 200,
                'message': '获取成功',
                'data': info
            }
        )
        
    except Exception as e:
        logger.error(f"获取模型信息失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器错误: {str(e)}"
        )


@router.get("/health", summary="健康检查")
async def health_check():
    """
    检查图像识别服务是否正常运行
    """
    try:
        service = get_image_recognition_service()
        info = service.get_model_info()
        
        is_healthy = info['status'] == 'loaded'
        
        return JSONResponse(
            status_code=200 if is_healthy else 503,
            content={
                'code': 200 if is_healthy else 503,
                'message': '服务正常' if is_healthy else '服务异常',
                'data': {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'model_loaded': is_healthy
                }
            }
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                'code': 503,
                'message': '服务异常',
                'data': {
                    'status': 'unhealthy',
                    'error': str(e)
                }
            }
        )

