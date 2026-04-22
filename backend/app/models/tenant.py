#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""租户模型（B2B升级新增）"""
from sqlalchemy import Column, String, Integer, Date, JSON, TIMESTAMP, func
from app.core.database import Base


class Tenant(Base):
    """租户表模型"""
    __tablename__ = "tenants"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False, comment='机构名称')
    short_name = Column(String(50), nullable=True, comment='机构简称')
    type = Column(String(20), nullable=False, default='hospital', comment='机构类型')
    level = Column(String(20), nullable=True, comment='医院等级')
    contact_person = Column(String(50), nullable=True, comment='联系人')
    contact_phone = Column(String(20), nullable=True, comment='联系电话')
    contact_email = Column(String(100), nullable=True, comment='联系邮箱')
    address = Column(String(255), nullable=True, comment='机构地址')
    province = Column(String(50), nullable=True, comment='省份')
    city = Column(String(50), nullable=True, comment='城市')
    license_key = Column(String(100), unique=True, nullable=True, comment='授权码')
    status = Column(String(20), nullable=False, default='active', comment='状态')
    expire_date = Column(Date, nullable=True, comment='到期日期')
    max_users = Column(Integer, nullable=False, default=100, comment='最大用户数')
    max_assessments_per_month = Column(Integer, nullable=False, default=1000, comment='每月最大筛查数')
    current_month_assessments = Column(Integer, nullable=False, default=0, comment='本月已使用筛查数')
    logo_url = Column(String(255), nullable=True, comment='机构Logo')
    settings = Column(JSON, nullable=True, comment='机构配置')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "type": self.type,
            "level": self.level,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "address": self.address,
            "province": self.province,
            "city": self.city,
            "license_key": self.license_key,
            "status": self.status,
            "expire_date": self.expire_date.isoformat() if self.expire_date else None,
            "max_users": self.max_users,
            "max_assessments_per_month": self.max_assessments_per_month,
            "current_month_assessments": self.current_month_assessments,
            "logo_url": self.logo_url,
            "settings": self.settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
