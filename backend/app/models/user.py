#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""用户模型"""
from sqlalchemy import Column, String, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色枚举（用于类型提示和验证）"""
    USER = "user"
    DOCTOR = "doctor"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    """用户状态枚举（用于类型提示和验证）"""
    ACTIVE = "active"
    DISABLED = "disabled"


class User(Base):
    """用户表模型（B2B升级）"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), nullable=True, index=True)  # B2B升级：租户ID
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(11), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    # 使用String类型，因为MySQL已经定义了ENUM约束
    role = Column(String(20), default='user', nullable=False, index=True)  # B2B升级：添加索引
    department = Column(String(50), nullable=True)  # B2B升级：科室
    title = Column(String(50), nullable=True)  # B2B升级：职称
    employee_id = Column(String(50), nullable=True)  # B2B升级：工号
    status = Column(String(20), default='active', nullable=False)
    is_active = Column(String(1), default='1', nullable=False)  # B2B升级：是否激活
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(TIMESTAMP, nullable=True)
    
    # 关系（需要在运行时才能访问，避免循环导入）
    # medical_images = relationship("MedicalImage", back_populates="user")
    
    def to_dict(self):
        """转换为字典（B2B升级）"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,  # B2B升级
            "email": self.email,
            "phone": self.phone,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "role": self.role,
            "department": self.department,  # B2B升级
            "title": self.title,  # B2B升级
            "employee_id": self.employee_id,  # B2B升级
            "status": self.status,
            "is_active": self.is_active == '1',  # B2B升级：转换为布尔值
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }

