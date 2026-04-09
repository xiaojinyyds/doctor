#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""医学影像分析API"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Body
from app.services.image_classifier import image_classifier
from app.utils.oss_client import oss_client
from app.core.security import get_current_user_id
from app.schemas.response import StandardResponse
from typing import Optional
import io
from PIL import Image
import requests

router = APIRouter()


@router.post("/analyze", summary="分析医学影像")
async def analyze_medical_image(
    file: Optional[UploadFile] = File(None, description="医学影像文件（PNG/JPG）"),
    image_url: Optional[str] = Body(None, description="图片OSS URL"),
    user_id: str = Depends(get_current_user_id)
):
    """
    分析医学影像（乳腺超声图像）
    
    支持两种方式：
    1. 直接上传文件（file参数）
    2. 提供OSS URL（image_url参数）
    
    Args:
        file: 图像文件（可选）
        image_url: 图片URL（可选）
        
    Returns:
        {
            "prediction": "良性肿瘤",
            "confidence": 0.923,
            "probabilities": {...},
            "recommendation": "建议..."
        }
    """
    # 验证至少提供一种输入
    if not file and not image_url:
        raise HTTPException(
            status_code=400,
            detail="请提供图片文件或图片URL"
        )
    
    # 获取图片内容
    try:
        if file:
            # 方式1：直接上传
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="只支持图像文件（PNG、JPG、JPEG）"
                )
            
            contents = await file.read()
            
            # 验证大小
            if len(contents) > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="图像文件不能超过10MB"
                )
        
        elif image_url:
            # 方式2：从URL下载
            if image_url.startswith(oss_client.domain):
                # 如果是OSS URL，可以直接从OSS下载
                # 提取object_key
                object_key = image_url.replace(f"{oss_client.domain}/", "")
                contents = oss_client.download_file(object_key)
            else:
                # 其他URL，通过HTTP下载
                response = requests.get(image_url, timeout=10)
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=400,
                        detail="无法下载图片"
                    )
                contents = response.content
    
    except requests.RequestException:
        raise HTTPException(
            status_code=400,
            detail="图片URL无效或无法访问"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"获取图片失败: {str(e)}"
        )
    
    # 验证是否为有效图像
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="无效的图像文件"
        )
    
    # AI分析
    try:
        result = image_classifier.predict(contents)
        
        return StandardResponse(
            code=200,
            message="分析成功",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/model/info", summary="获取模型信息")
async def get_model_info():
    """获取AI模型信息"""
    
    return StandardResponse(
        code=200,
        message="success",
        data={
            "model_name": "ResNet18",
            "task": "乳腺超声图像分类",
            "classes": ["正常", "良性肿瘤", "恶性肿瘤"],
            "input_size": "224x224",
            "accuracy": "~90%",
            "description": "基于深度学习的乳腺超声图像智能分析系统"
        }
    )

