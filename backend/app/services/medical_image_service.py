"""
医学影像服务 - 整合上传、分析、历史记录
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from pathlib import Path
import io
from PIL import Image
import logging

from app.models.medical_image import (
    MedicalImage, ImageAnalysisResult, ImageAnnotation, HealthRecord
)
from app.schemas.medical_image import (
    MedicalImageCreate, ImageAnalysisResultCreate, ImageAnalysisStats
)
from app.services.image_classifier import image_classifier
from app.utils.gradcam import generate_gradcam  # 热力图生成（稍后实现）
from app.utils.oss_client import oss_client

logger = logging.getLogger(__name__)


class MedicalImageService:
    """医学影像服务"""
    
    @staticmethod
    def create_medical_image(
        db: Session,
        user_id: str,
        image_data: MedicalImageCreate
    ) -> MedicalImage:
        """
        创建医学影像记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            image_data: 影像数据
            
        Returns:
            创建的医学影像记录
        """
        medical_image = MedicalImage(
            id=str(uuid.uuid4()),
            user_id=user_id,
            **image_data.dict()
        )
        
        db.add(medical_image)
        db.commit()
        db.refresh(medical_image)
        
        logger.info(f"创建医学影像记录: {medical_image.id}")
        return medical_image
    
    @staticmethod
    def analyze_image(
        db: Session,
        image_id: str,
        user_id: str,
        image_bytes: bytes,
        generate_heatmap: bool = False
    ) -> ImageAnalysisResult:
        """
        分析医学影像
        
        Args:
            db: 数据库会话
            image_id: 影像ID
            user_id: 用户ID
            image_bytes: 图像字节数据
            generate_heatmap: 是否生成热力图
            
        Returns:
            分析结果
        """
        # 更新影像状态为分析中
        medical_image = db.query(MedicalImage).filter(MedicalImage.id == image_id).first()
        if medical_image:
            medical_image.analysis_status = 'analyzing'
            db.commit()
        
        try:
            # 记录开始时间
            start_time = datetime.now()
            
            # AI分析（生成标注图）
            prediction_result = image_classifier.predict(image_bytes, generate_annotation=True)
            
            # 计算推理时间
            inference_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            if not prediction_result.get('success', True):
                # 分析失败
                if medical_image:
                    medical_image.analysis_status = 'failed'
                    db.commit()
                raise Exception(prediction_result.get('message', '分析失败'))
            
            # 提取概率
            probabilities = prediction_result.get('probabilities', {})
            
            # 上传标注图到OSS（如果有）
            annotated_image_url = None
            if 'annotated_image_bytes' in prediction_result:
                try:
                    annotated_bytes = prediction_result['annotated_image_bytes']
                    oss_result = oss_client.upload_file(
                        file_content=annotated_bytes,
                        filename=f'annotated_{image_id}.png',
                        folder=f'medical-images/annotated/{user_id}'
                    )
                    annotated_image_url = oss_result['url']
                    logger.info(f"标注图已上传到OSS: {annotated_image_url}")
                except Exception as e:
                    logger.warning(f"上传标注图失败: {e}")
            
            # 创建分析结果记录
            analysis_result = ImageAnalysisResult(
                id=str(uuid.uuid4()),
                image_id=image_id,
                user_id=user_id,
                predicted_class=prediction_result.get('prediction_en', 'unknown'),
                predicted_class_cn=prediction_result.get('prediction', '未知'),
                confidence=prediction_result.get('confidence', 0),
                prob_normal=probabilities.get('正常', 0),
                prob_benign=probabilities.get('良性肿瘤', 0),
                prob_malignant=probabilities.get('恶性肿瘤', 0),
                risk_level=MedicalImageService._get_risk_level(prediction_result.get('prediction_en', '')),
                risk_score=prediction_result.get('confidence', 0),
                ai_recommendation=prediction_result.get('recommendation', ''),
                model_name='ResNet18',
                model_version='v1.0',
                inference_time_ms=inference_time,
                heatmap_url=annotated_image_url  # 使用heatmap_url字段存储标注图
            )
            
            # 如果需要生成热力图
            if generate_heatmap:
                try:
                    heatmap_url = MedicalImageService._generate_visualization(
                        image_bytes, 
                        image_id
                    )
                    analysis_result.heatmap_url = heatmap_url
                except Exception as e:
                    logger.warning(f"生成热力图失败: {e}")
            
            db.add(analysis_result)
            
            # 更新影像状态为已完成
            if medical_image:
                medical_image.analysis_status = 'completed'
            
            db.commit()
            db.refresh(analysis_result)
            
            logger.info(f"影像分析完成: {image_id} -> {analysis_result.predicted_class_cn}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"影像分析失败: {e}")
            # 更新状态为失败
            if medical_image:
                medical_image.analysis_status = 'failed'
                db.commit()
            raise
    
    @staticmethod
    def _get_risk_level(predicted_class: str) -> str:
        """根据预测类别获取风险等级"""
        risk_mapping = {
            'normal': '低风险',
            'benign': '中风险',
            'malignant': '高风险'
        }
        return risk_mapping.get(predicted_class, '未知')
    
    @staticmethod
    def _generate_visualization(image_bytes: bytes, image_id: str) -> Optional[str]:
        """
        生成可视化图像（热力图）
        
        Args:
            image_bytes: 原始图像字节
            image_id: 影像ID
            
        Returns:
            热力图URL
        """
        # TODO: 实现Grad-CAM热力图生成
        # 暂时返回None，后续实现
        return None
    
    @staticmethod
    def get_user_images(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        image_type: Optional[str] = None
    ) -> List[MedicalImage]:
        """
        获取用户的医学影像列表
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量
            image_type: 影像类型过滤
            
        Returns:
            医学影像列表
        """
        query = db.query(MedicalImage).filter(MedicalImage.user_id == user_id)
        
        if image_type:
            query = query.filter(MedicalImage.image_type == image_type)
        
        images = query.order_by(desc(MedicalImage.created_at)).offset(skip).limit(limit).all()
        return images
    
    @staticmethod
    def get_image_analysis_results(
        db: Session,
        image_id: str
    ) -> List[ImageAnalysisResult]:
        """
        获取影像的所有分析结果
        
        Args:
            db: 数据库会话
            image_id: 影像ID
            
        Returns:
            分析结果列表
        """
        results = db.query(ImageAnalysisResult)\
            .filter(ImageAnalysisResult.image_id == image_id)\
            .order_by(desc(ImageAnalysisResult.created_at))\
            .all()
        return results
    
    @staticmethod
    def get_user_analysis_history(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[ImageAnalysisResult]:
        """
        获取用户的影像分析历史
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量
            
        Returns:
            分析结果列表
        """
        results = db.query(ImageAnalysisResult)\
            .filter(ImageAnalysisResult.user_id == user_id)\
            .order_by(desc(ImageAnalysisResult.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()
        return results
    
    @staticmethod
    def get_analysis_statistics(
        db: Session,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ImageAnalysisStats:
        """
        获取影像分析统计信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID（可选，为空则统计全部）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            统计信息
        """
        # 构建查询
        image_query = db.query(MedicalImage)
        result_query = db.query(ImageAnalysisResult)
        
        if user_id:
            image_query = image_query.filter(MedicalImage.user_id == user_id)
            result_query = result_query.filter(ImageAnalysisResult.user_id == user_id)
        
        if start_date:
            image_query = image_query.filter(MedicalImage.created_at >= start_date)
            result_query = result_query.filter(ImageAnalysisResult.created_at >= start_date)
        
        if end_date:
            image_query = image_query.filter(MedicalImage.created_at <= end_date)
            result_query = result_query.filter(ImageAnalysisResult.created_at <= end_date)
        
        # 统计
        total_images = image_query.count()
        analyzed_images = image_query.filter(MedicalImage.analysis_status == 'completed').count()
        pending_images = image_query.filter(MedicalImage.analysis_status == 'pending').count()
        
        # 各类别统计
        normal_count = result_query.filter(ImageAnalysisResult.predicted_class == 'normal').count()
        benign_count = result_query.filter(ImageAnalysisResult.predicted_class == 'benign').count()
        malignant_count = result_query.filter(ImageAnalysisResult.predicted_class == 'malignant').count()
        
        # 高风险数量
        high_risk_count = result_query.filter(ImageAnalysisResult.risk_level == '高风险').count()
        
        # 平均置信度
        from sqlalchemy import func as sql_func
        avg_confidence = db.query(sql_func.avg(ImageAnalysisResult.confidence))\
            .filter(ImageAnalysisResult.user_id == user_id if user_id else True)\
            .scalar()
        
        return ImageAnalysisStats(
            total_images=total_images,
            analyzed_images=analyzed_images,
            pending_images=pending_images,
            normal_count=normal_count,
            benign_count=benign_count,
            malignant_count=malignant_count,
            average_confidence=float(avg_confidence) if avg_confidence else None,
            high_risk_count=high_risk_count
        )
    
    @staticmethod
    def doctor_review(
        db: Session,
        result_id: str,
        doctor_id: str,
        doctor_opinion: str,
        true_label: Optional[str] = None
    ) -> ImageAnalysisResult:
        """
        医生审核分析结果
        
        Args:
            db: 数据库会话
            result_id: 分析结果ID
            doctor_id: 医生ID
            doctor_opinion: 医生意见
            true_label: 真实标签（用于模型改进）
            
        Returns:
            更新后的分析结果
        """
        result = db.query(ImageAnalysisResult)\
            .filter(ImageAnalysisResult.id == result_id)\
            .first()
        
        if not result:
            raise ValueError("分析结果不存在")
        
        # 更新审核信息
        result.reviewed_by_doctor = True
        result.doctor_id = doctor_id
        result.doctor_opinion = doctor_opinion
        result.reviewed_at = datetime.now()
        
        # 如果提供了真实标签，创建标注记录
        if true_label:
            annotation = ImageAnnotation(
                id=str(uuid.uuid4()),
                image_id=result.image_id,
                annotator_id=doctor_id,
                true_label=true_label,
                true_label_cn=MedicalImageService._get_label_cn(true_label),
                ai_prediction=result.predicted_class,
                ai_correct=(true_label == result.predicted_class),
                clinical_diagnosis=doctor_opinion
            )
            db.add(annotation)
        
        db.commit()
        db.refresh(result)
        
        logger.info(f"医生审核完成: {result_id}")
        return result
    
    @staticmethod
    def _get_label_cn(label: str) -> str:
        """获取标签的中文名称"""
        label_mapping = {
            'normal': '正常',
            'benign': '良性肿瘤',
            'malignant': '恶性肿瘤'
        }
        return label_mapping.get(label, label)
    
    @staticmethod
    def get_risk_trend(
        db: Session,
        user_id: str,
        days: int = 30
    ) -> List[Dict]:
        """
        获取用户的风险趋势
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 天数
            
        Returns:
            风险趋势数据
        """
        start_date = datetime.now() - timedelta(days=days)
        
        results = db.query(ImageAnalysisResult)\
            .filter(
                and_(
                    ImageAnalysisResult.user_id == user_id,
                    ImageAnalysisResult.created_at >= start_date
                )
            )\
            .order_by(ImageAnalysisResult.created_at)\
            .all()
        
        trend_data = []
        for result in results:
            trend_data.append({
                'date': result.created_at.strftime('%Y-%m-%d'),
                'risk_level': result.risk_level,
                'risk_score': float(result.risk_score) if result.risk_score else 0,
                'confidence': float(result.confidence),
                'predicted_class': result.predicted_class_cn
            })
        
        return trend_data
    
    @staticmethod
    def delete_image(
        db: Session,
        image_id: str,
        user_id: str
    ) -> bool:
        """
        删除医学影像（仅用户自己可删除）
        
        Args:
            db: 数据库会话
            image_id: 影像ID
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        image = db.query(MedicalImage)\
            .filter(
                and_(
                    MedicalImage.id == image_id,
                    MedicalImage.user_id == user_id
                )
            )\
            .first()
        
        if not image:
            return False
        
        # 从OSS删除文件（如果URL是OSS的）
        if image.file_url and oss_client.domain in image.file_url:
            try:
                # 提取object_key
                object_key = image.file_url.replace(f"{oss_client.domain}/", "")
                oss_client.delete_file(object_key)
                logger.info(f"已从OSS删除文件: {object_key}")
            except Exception as e:
                logger.warning(f"OSS文件删除失败: {e}")
        
        # 从数据库删除记录
        db.delete(image)
        db.commit()
        
        logger.info(f"删除医学影像: {image_id}")
        return True
    
    @staticmethod
    def compare_images(
        db: Session,
        image_id_1: str,
        image_id_2: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        对比两张影像的分析结果
        
        Args:
            db: 数据库会话
            image_id_1: 第一张影像ID
            image_id_2: 第二张影像ID
            user_id: 用户ID
            
        Returns:
            对比结果
        """
        # 获取两张影像的最新分析结果
        result_1 = db.query(ImageAnalysisResult)\
            .filter(ImageAnalysisResult.image_id == image_id_1)\
            .order_by(desc(ImageAnalysisResult.created_at))\
            .first()
        
        result_2 = db.query(ImageAnalysisResult)\
            .filter(ImageAnalysisResult.image_id == image_id_2)\
            .order_by(desc(ImageAnalysisResult.created_at))\
            .first()
        
        if not result_1 or not result_2:
            raise ValueError("影像分析结果不存在")
        
        # 构建对比数据
        comparison = {
            'image_1': {
                'id': image_id_1,
                'predicted_class': result_1.predicted_class_cn,
                'confidence': float(result_1.confidence),
                'risk_level': result_1.risk_level,
                'analyzed_at': result_1.created_at.isoformat(),
                'probabilities': {
                    '正常': float(result_1.prob_normal or 0),
                    '良性肿瘤': float(result_1.prob_benign or 0),
                    '恶性肿瘤': float(result_1.prob_malignant or 0)
                }
            },
            'image_2': {
                'id': image_id_2,
                'predicted_class': result_2.predicted_class_cn,
                'confidence': float(result_2.confidence),
                'risk_level': result_2.risk_level,
                'analyzed_at': result_2.created_at.isoformat(),
                'probabilities': {
                    '正常': float(result_2.prob_normal or 0),
                    '良性肿瘤': float(result_2.prob_benign or 0),
                    '恶性肿瘤': float(result_2.prob_malignant or 0)
                }
            },
            'differences': {
                'class_changed': result_1.predicted_class != result_2.predicted_class,
                'confidence_diff': float(result_2.confidence - result_1.confidence),
                'risk_level_changed': result_1.risk_level != result_2.risk_level
            },
            'time_interval_days': (result_2.created_at - result_1.created_at).days
        }
        
        return comparison
    
    @staticmethod
    def get_image_by_id(db: Session, image_id: str) -> Optional[MedicalImage]:
        """获取医学影像"""
        return db.query(MedicalImage).filter(MedicalImage.id == image_id).first()
    
    @staticmethod
    def get_analysis_result_by_id(db: Session, result_id: str) -> Optional[ImageAnalysisResult]:
        """获取分析结果"""
        return db.query(ImageAnalysisResult).filter(ImageAnalysisResult.id == result_id).first()

