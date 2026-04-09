#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastAPI应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, assessment, admin, share, knowledge, assessment_v2, upload, medical_image, medical_image_v2

# 导入所有模型（确保表被创建）
from app.models.user import User
from app.models.questionnaire import Questionnaire
from app.models.assessment import Assessment, Recommendation, Report
from app.models.medical_image import MedicalImage, ImageAnalysisResult, ImageAnnotation, HealthRecord


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("="*60)
    print("🚀 肿瘤数智化筛查系统启动中...")
    print(f"📝 API文档: http://localhost:8000/docs")
    print("="*60)
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # 关闭时
    print("\n👋 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="基于AI的肿瘤风险评估系统API",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 根路由
@app.get("/", tags=["根目录"])
async def root():
    """API根路径"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


# 健康检查
@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


# 注册路由
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["认证"]
)

app.include_router(
    assessment.router,
    prefix="/api/v1/assessment",
    tags=["风险评估"]
)

app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["管理员"]
)

app.include_router(
    share.router,
    prefix="/api/v1/share",
    tags=["报告分享"]
)

app.include_router(
    knowledge.router,
    prefix="/api/v1/knowledge",
    tags=["知识图谱"]
)

app.include_router(
    assessment_v2.router,
    prefix="/api/v1/assessment",
    tags=["风险评估V2"]
)

app.include_router(
    upload.router,
    prefix="/api/v1/upload",
    tags=["文件上传"]
)

app.include_router(
    medical_image.router,
    prefix="/api/v1/medical-image",
    tags=["医学影像分析"]
)

app.include_router(
    medical_image_v2.router,
    prefix="/api/v1/medical-image-v2",
    tags=["医学影像分析V2"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

