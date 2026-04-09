#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阿里云OSS客户端工具"""
import oss2
from typing import Optional
from datetime import datetime
import uuid
from pathlib import Path
from app.core.config import settings


class OSSClient:
    """阿里云OSS客户端"""
    
    def __init__(self):
        """初始化OSS客户端"""
        auth = oss2.Auth(settings.OSS_ACCESS_KEY, settings.OSS_SECRET_KEY)
        self.bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
        self.domain = settings.OSS_DOMAIN or f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}"
    
    def upload_file(
        self, 
        file_content: bytes, 
        filename: str,
        folder: str = "medical-images"
    ) -> dict:
        """
        上传文件到OSS
        
        Args:
            file_content: 文件内容（字节流）
            filename: 原始文件名
            folder: 存储文件夹
            
        Returns:
            {
                'url': 'https://xxx.oss-cn-shanghai.aliyuncs.com/medical-images/xxx.jpg',
                'key': 'medical-images/xxx.jpg',
                'size': 12345
            }
        """
        # 生成唯一文件名
        file_ext = Path(filename).suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        # OSS对象键（路径）
        object_key = f"{folder}/{datetime.now().strftime('%Y%m%d')}/{unique_filename}"
        
        # 上传到OSS
        result = self.bucket.put_object(object_key, file_content)
        
        if result.status != 200:
            raise Exception(f"上传失败: {result.status}")
        
        # 构建访问URL
        file_url = f"{self.domain}/{object_key}"
        
        return {
            'url': file_url,
            'key': object_key,
            'size': len(file_content)
        }
    
    def delete_file(self, object_key: str) -> bool:
        """
        删除OSS文件
        
        Args:
            object_key: 文件键（如 'medical-images/20240101/xxx.jpg'）
            
        Returns:
            是否成功
        """
        try:
            result = self.bucket.delete_object(object_key)
            return result.status == 204
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
    
    def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """
        获取文件的临时访问URL（带签名）
        
        Args:
            object_key: 文件键
            expires: 过期时间（秒），默认1小时
            
        Returns:
            临时访问URL
        """
        return self.bucket.sign_url('GET', object_key, expires)
    
    def download_file(self, object_key: str) -> bytes:
        """
        下载OSS文件
        
        Args:
            object_key: 文件键
            
        Returns:
            文件内容（字节流）
        """
        result = self.bucket.get_object(object_key)
        return result.read()


# 全局OSS客户端实例
oss_client = OSSClient()

