"""
医学影像相关的Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


# ============ 医学影像上传 ============

class MedicalImageBase(BaseModel):
    """医学影像基础信息"""
    original_filename: str = Field(..., description="原始文件名")
    image_type: str = Field(default="breast_ultrasound", description="影像类型")
    body_part: str = Field(default="breast", description="检查部位")
    acquisition_date: Optional[date] = Field(None, description="影像采集日期")
    institution: Optional[str] = Field(None, description="检查机构")


class MedicalImageCreate(MedicalImageBase):
    """创建医学影像记录"""
    file_url: str = Field(..., description="文件存储URL")
    file_size: int = Field(..., description="文件大小(字节)")
    file_format: str = Field(..., description="文件格式")
    image_width: Optional[int] = None
    image_height: Optional[int] = None


class MedicalImageResponse(MedicalImageBase):
    """医学影像响应"""
    id: str
    user_id: str
    file_url: str
    file_size: int
    file_format: str
    image_width: Optional[int]
    image_height: Optional[int]
    upload_status: str
    analysis_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ 影像识别结果 ============

class ImageAnalysisResultBase(BaseModel):
    """影像识别结果基础信息"""
    predicted_class: str = Field(..., description="预测类别")
    predicted_class_cn: str = Field(..., description="预测类别中文")
    confidence: Decimal = Field(..., description="置信度")
    risk_level: str = Field(..., description="风险等级")
    ai_recommendation: str = Field(..., description="AI建议")


class ImageAnalysisResultCreate(ImageAnalysisResultBase):
    """创建影像识别结果"""
    image_id: str
    user_id: str
    prob_normal: Optional[Decimal] = None
    prob_benign: Optional[Decimal] = None
    prob_malignant: Optional[Decimal] = None
    risk_score: Optional[Decimal] = None
    model_name: str = "ResNet18"
    model_version: str = "v1.0"
    inference_time_ms: Optional[int] = None
    heatmap_url: Optional[str] = None
    attention_map_url: Optional[str] = None


class ImageAnalysisResultResponse(ImageAnalysisResultBase):
    """影像识别结果响应"""
    id: str
    image_id: str
    user_id: str
    prob_normal: Optional[Decimal]
    prob_benign: Optional[Decimal]
    prob_malignant: Optional[Decimal]
    risk_score: Optional[Decimal]
    model_name: str
    model_version: str
    inference_time_ms: Optional[int]
    heatmap_url: Optional[str]
    attention_map_url: Optional[str]
    reviewed_by_doctor: bool
    doctor_opinion: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ImageAnalysisResultDetail(ImageAnalysisResultResponse):
    """影像识别结果详情（包含关联数据）"""
    image: Optional[MedicalImageResponse] = None
    probabilities: Dict[str, float] = Field(default_factory=dict, description="各类别概率")


# ============ 医生审核 ============

class DoctorReviewRequest(BaseModel):
    """医生审核请求"""
    doctor_opinion: str = Field(..., description="医生意见")
    true_label: Optional[str] = Field(None, description="真实标签（用于标注）")


# ============ 影像分析历史 ============

class ImageAnalysisHistoryCreate(BaseModel):
    """创建分析历史记录"""
    image_id: str
    analysis_result_id: str
    user_id: str
    analysis_type: str = "classification"
    parameters: Optional[Dict] = None
    result_snapshot: Dict
    compared_with: Optional[str] = None
    comparison_notes: Optional[str] = None


class ImageAnalysisHistoryResponse(BaseModel):
    """分析历史响应"""
    id: str
    image_id: str
    analysis_result_id: str
    user_id: str
    analysis_type: str
    parameters: Optional[Dict]
    result_snapshot: Dict
    compared_with: Optional[str]
    comparison_notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 影像标注 ============

class ImageAnnotationCreate(BaseModel):
    """创建影像标注"""
    image_id: str
    true_label: str = Field(..., description="真实标签")
    true_label_cn: str = Field(..., description="真实标签中文")
    lesion_count: int = Field(default=0, description="病灶数量")
    lesion_locations: Optional[List[Dict]] = Field(None, description="病灶位置")
    lesion_sizes: Optional[List[Dict]] = Field(None, description="病灶大小")
    pathology_result: Optional[str] = None
    clinical_diagnosis: Optional[str] = None
    additional_notes: Optional[str] = None
    annotation_quality: str = Field(default="medium", description="标注质量")
    confidence_level: str = Field(default="probable", description="确信程度")


class ImageAnnotationResponse(BaseModel):
    """影像标注响应"""
    id: str
    image_id: str
    annotator_id: str
    true_label: str
    true_label_cn: str
    lesion_count: int
    lesion_locations: Optional[List[Dict]]
    lesion_sizes: Optional[List[Dict]]
    pathology_result: Optional[str]
    clinical_diagnosis: Optional[str]
    additional_notes: Optional[str]
    annotation_quality: str
    confidence_level: str
    ai_prediction: Optional[str]
    ai_correct: Optional[bool]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ 综合健康档案 ============

class HealthRecordCreate(BaseModel):
    """创建健康档案"""
    user_id: str
    questionnaire_id: Optional[str] = None
    assessment_id: Optional[str] = None
    image_ids: Optional[List[str]] = None
    overall_health_score: Optional[Decimal] = None
    risk_summary: Optional[Dict] = None
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None
    follow_up_items: Optional[List[str]] = None


class HealthRecordResponse(BaseModel):
    """健康档案响应"""
    id: str
    user_id: str
    questionnaire_id: Optional[str]
    assessment_id: Optional[str]
    image_ids: Optional[List[str]]
    overall_health_score: Optional[Decimal]
    risk_summary: Optional[Dict]
    follow_up_required: bool
    follow_up_date: Optional[date]
    follow_up_items: Optional[List[str]]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HealthRecordDetail(HealthRecordResponse):
    """健康档案详情（包含关联数据）"""
    images: List[MedicalImageResponse] = Field(default_factory=list)
    analysis_results: List[ImageAnalysisResultResponse] = Field(default_factory=list)


# ============ 统计与查询 ============

class ImageAnalysisStats(BaseModel):
    """影像分析统计"""
    total_images: int = Field(..., description="总影像数")
    analyzed_images: int = Field(..., description="已分析影像数")
    pending_images: int = Field(..., description="待分析影像数")
    normal_count: int = Field(default=0, description="正常数量")
    benign_count: int = Field(default=0, description="良性数量")
    malignant_count: int = Field(default=0, description="恶性数量")
    average_confidence: Optional[float] = Field(None, description="平均置信度")
    high_risk_count: int = Field(default=0, description="高风险数量")


class UserImageHistory(BaseModel):
    """用户影像历史"""
    user_id: str
    total_uploads: int
    images: List[MedicalImageResponse]
    latest_analysis: Optional[ImageAnalysisResultResponse] = None
    risk_trend: Optional[List[Dict]] = None  # 风险趋势数据

