#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""文件上传API"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.utils.oss_client import oss_client
from app.core.security import get_current_user_id
from app.schemas.response import StandardResponse
from typing import List
import io
from PIL import Image

router = APIRouter()

# 允许的图片格式
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/image", summary="上传图片")
async def upload_image(
    file: UploadFile = File(..., description="图片文件"),
    user_id: str = Depends(get_current_user_id)
):
    """
    上传图片到OSS
    
    支持格式：JPG、PNG、WEBP
    文件大小：不超过10MB
    
    Returns:
        {
            "url": "https://xxx.oss-cn-shanghai.aliyuncs.com/medical-images/20240101/xxx.jpg",
            "key": "medical-images/20240101/xxx.jpg",
            "size": 12345
        }
    """
    # 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型。仅支持: JPG, PNG, WEBP"
        )
    
    # 读取文件内容
    contents = await file.read()
    
    # 验证文件大小
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 {MAX_FILE_SIZE // 1024 // 1024}MB"
        )
    
    # 验证是否为有效图片
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="无效的图片文件"
        )
    
    # 上传到OSS
    try:
        result = oss_client.upload_file(
            file_content=contents,
            filename=file.filename,
            folder="medical-images"
        )
        
        return StandardResponse(
            code=200,
            message="上传成功",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"上传失败: {str(e)}"
        )


@router.post("/batch", summary="批量上传图片")
async def upload_images_batch(
    files: List[UploadFile] = File(..., description="图片文件列表"),
    user_id: str = Depends(get_current_user_id)
):
    """
    批量上传图片（最多5张）
    
    Returns:
        {
            "success": [{"url": "...", "key": "...", "filename": "..."}],
            "failed": [{"filename": "...", "error": "..."}]
        }
    """
    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail="最多同时上传5张图片"
        )
    
    success_list = []
    failed_list = []
    
    for file in files:
        try:
            # 验证文件类型
            if file.content_type not in ALLOWED_IMAGE_TYPES:
                failed_list.append({
                    "filename": file.filename,
                    "error": "不支持的文件类型"
                })
                continue
            
            # 读取文件
            contents = await file.read()
            
            # 验证大小
            if len(contents) > MAX_FILE_SIZE:
                failed_list.append({
                    "filename": file.filename,
                    "error": "文件过大"
                })
                continue
            
            # 验证是否为有效图片
            try:
                image = Image.open(io.BytesIO(contents))
                image.verify()
            except Exception:
                failed_list.append({
                    "filename": file.filename,
                    "error": "无效的图片文件"
                })
                continue
            
            # 上传
            result = oss_client.upload_file(
                file_content=contents,
                filename=file.filename,
                folder="medical-images"
            )
            
            success_list.append({
                **result,
                "filename": file.filename
            })
        
        except Exception as e:
            failed_list.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return StandardResponse(
        code=200,
        message=f"上传完成: 成功{len(success_list)}个，失败{len(failed_list)}个",
        data={
            "success": success_list,
            "failed": failed_list
        }
    )


@router.delete("/image", summary="删除图片")
async def delete_image(
    key: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    删除OSS上的图片
    
    Args:
        key: OSS对象键（如 'medical-images/20240101/xxx.jpg'）
    """
    try:
        success = oss_client.delete_file(key)
        
        if success:
            return StandardResponse(
                code=200,
                message="删除成功"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="删除失败"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除失败: {str(e)}"
        )

