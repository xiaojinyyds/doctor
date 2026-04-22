"""
医学影像相关数据模型
"""
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, Enum, JSON, DECIMAL, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class UploadStatus(str, enum.Enum):
    """上传状态"""
    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"


class AnalysisStatus(str, enum.Enum):
    """分析状态"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, enum.Enum):
    """风险等级"""
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"


class MedicalImage(Base):
    """医学影像上传记录"""
    __tablename__ = "medical_images"
    
    id = Column(String(36), primary_key=True, comment='影像ID')
    tenant_id = Column(String(36), nullable=True, index=True, comment='所属租户ID')
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户ID')
    
    # 文件信息
    original_filename = Column(String(255), nullable=False, comment='原始文件名')
    file_url = Column(String(500), nullable=False, comment='文件存储URL')
    file_size = Column(Integer, nullable=False, comment='文件大小(字节)')
    file_format = Column(String(20), nullable=False, comment='文件格式')
    
    # 影像类型
    image_type = Column(String(50), default='breast_ultrasound', comment='影像类型')
    body_part = Column(String(50), default='breast', comment='检查部位')
    
    # 影像信息
    image_width = Column(Integer, comment='图像宽度')
    image_height = Column(Integer, comment='图像高度')
    acquisition_date = Column(Date, comment='影像采集日期')
    institution = Column(String(200), comment='检查机构')
    
    # 状态
    upload_status = Column(String(20), default='uploaded', comment='上传状态')
    analysis_status = Column(String(20), default='pending', comment='分析状态')
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment='上传时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')


class ImageAnalysisResult(Base):
    """影像识别结果"""
    __tablename__ = "image_analysis_results"
    
    id = Column(String(36), primary_key=True, comment='分析结果ID')
    tenant_id = Column(String(36), nullable=True, index=True, comment='所属租户ID')
    image_id = Column(String(36), ForeignKey('medical_images.id', ondelete='CASCADE'), nullable=False, comment='影像ID')
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户ID')
    
    # AI预测结果
    predicted_class = Column(String(50), nullable=False, comment='预测类别')
    predicted_class_cn = Column(String(50), nullable=False, comment='预测类别中文')
    confidence = Column(DECIMAL(5, 4), nullable=False, comment='置信度')
    
    # 概率分布
    prob_normal = Column(DECIMAL(5, 4), comment='正常概率')
    prob_benign = Column(DECIMAL(5, 4), comment='良性概率')
    prob_malignant = Column(DECIMAL(5, 4), comment='恶性概率')
    
    # 风险评级
    risk_level = Column(String(20), nullable=False, comment='风险等级')
    risk_score = Column(DECIMAL(5, 4), comment='风险分数')
    
    # AI建议
    ai_recommendation = Column(Text, nullable=False, comment='AI生成的医疗建议')
    
    # 可视化数据
    heatmap_url = Column(String(500), comment='热力图URL')
    attention_map_url = Column(String(500), comment='注意力图URL')
    
    # 模型信息
    model_name = Column(String(100), default='ResNet18', comment='使用的模型名称')
    model_version = Column(String(50), default='v1.0', comment='模型版本')
    inference_time_ms = Column(Integer, comment='推理时间(毫秒)')
    
    # 医生审核
    reviewed_by_doctor = Column(Boolean, default=False, comment='是否经医生审核')
    doctor_id = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), comment='审核医生ID')
    doctor_opinion = Column(Text, comment='医生意见')
    reviewed_at = Column(DateTime, comment='审核时间')
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment='分析时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')


class ImageAnnotation(Base):
    """医学影像标注"""
    __tablename__ = "image_annotations"
    
    id = Column(String(36), primary_key=True, comment='标注ID')
    image_id = Column(String(36), ForeignKey('medical_images.id', ondelete='CASCADE'), nullable=False, comment='影像ID')
    annotator_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='标注人ID')
    
    # 标注结果
    true_label = Column(String(50), nullable=False, comment='真实标签')
    true_label_cn = Column(String(50), nullable=False, comment='真实标签中文')
    
    # 病灶信息
    lesion_count = Column(Integer, default=0, comment='病灶数量')
    lesion_locations = Column(JSON, comment='病灶位置信息')
    lesion_sizes = Column(JSON, comment='病灶大小信息')
    
    # 临床信息
    pathology_result = Column(String(100), comment='病理结果')
    clinical_diagnosis = Column(Text, comment='临床诊断')
    additional_notes = Column(Text, comment='补充说明')
    
    # 标注质量
    annotation_quality = Column(String(20), default='medium', comment='标注质量')
    confidence_level = Column(String(20), default='probable', comment='确信程度')
    
    # AI预测对比
    ai_prediction = Column(String(50), comment='AI预测结果')
    ai_correct = Column(Boolean, comment='AI预测是否正确')
    
    created_at = Column(DateTime, default=func.now(), comment='标注时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')


class HealthRecord(Base):
    """综合健康档案"""
    __tablename__ = "health_records"
    
    id = Column(String(36), primary_key=True, comment='档案ID')
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户ID')
    
    # 关联信息
    questionnaire_id = Column(String(36), ForeignKey('questionnaires.id', ondelete='SET NULL'), comment='问卷ID')
    assessment_id = Column(String(36), ForeignKey('assessments.id', ondelete='SET NULL'), comment='评估ID')
    
    # 影像记录
    image_ids = Column(JSON, comment='关联的影像ID列表')
    
    # 综合评估
    overall_health_score = Column(DECIMAL(5, 4), comment='综合健康分数')
    risk_summary = Column(JSON, comment='风险汇总')
    
    # 随访信息
    follow_up_required = Column(Boolean, default=False, comment='是否需要随访')
    follow_up_date = Column(Date, comment='建议随访日期')
    follow_up_items = Column(JSON, comment='随访项目')
    
    # 状态
    status = Column(String(20), default='active', comment='档案状态')
    
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
