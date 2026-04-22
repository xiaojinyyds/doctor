#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""应用配置"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用信息
    APP_NAME: str = Field(default="肿瘤数智化筛查系统")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=True)
    
    # 数据库配置
    DATABASE_URL: str
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=3306)
    DB_USER: str = Field(default="root")
    DB_PASSWORD: str
    DB_NAME: str = Field(default="tumor_screening")
    
    # Redis配置
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_PASSWORD: str = Field(default="")
    
    # JWT配置
    SECRET_KEY: str
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10080)
    
    # 邮件配置
    MAIL_HOST: str = Field(default="smtp.qq.com")
    MAIL_PORT: int = Field(default=465)
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str = Field(default="肿瘤筛查系统")
    
    # 验证码配置
    VERIFICATION_CODE_EXPIRE: int = Field(default=300)  # 5分钟
    VERIFICATION_CODE_LENGTH: int = Field(default=6)
    
    # CORS配置
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"
    )
    
    # 服务器地址配置
    BACKEND_URL: str = Field(default="http://localhost:8000", description="后端服务器地址")
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="前端服务器地址")
    DEFAULT_TENANT_ID: str = Field(default="tenant-default", description="默认租户ID")
    DEFAULT_TENANT_NAME: str = Field(default="默认机构", description="默认租户名称")
    
    @property
    def get_allowed_origins(self) -> List[str]:
        """获取CORS允许的源列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # 大模型配置
    ZHIPU_API_KEY: str = Field(default="", description="智谱AI API密钥")
    DEEPSEEK_API_KEY: str = Field(default="", description="DeepSeek API密钥")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com", description="DeepSeek API地址")
    DEEPSEEK_MODEL: str = Field(default="deepseek-chat", description="DeepSeek模型名称")
    
    # 阿里云OSS配置
    OSS_ENDPOINT: str = Field(default="oss-cn-shanghai.aliyuncs.com", description="OSS接入点")
    OSS_ACCESS_KEY: str = Field(default="", description="OSS访问密钥（仅从环境变量读取）")
    OSS_SECRET_KEY: str = Field(default="", description="OSS密钥（仅从环境变量读取）")
    OSS_BUCKET_NAME: str = Field(default="sky-itjin", description="OSS存储桶名称")
    OSS_DOMAIN: str = Field(default="", description="OSS自定义域名（可选）")
    
    # 其他配置
    UPLOAD_DIR: str = Field(default="uploads")
    MAX_UPLOAD_SIZE: int = Field(default=52428800)
    MODEL_DIR: str = Field(default="app/ml/models")
    MODEL_VERSION: str = Field(default="v1.0")
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/app.log")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局配置实例
settings = Settings()
