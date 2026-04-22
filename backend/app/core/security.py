#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""安全相关：JWT、密码加密"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    # bcrypt限制密码最长72字节，截断处理
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    data应包含:
    - sub: 用户ID
    - tenant_id: 租户ID (B2B升级新增)
    - role: 用户角色 (B2B升级新增)
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


security_scheme = HTTPBearer(auto_error=False)


class CurrentUser:
    """当前用户信息（B2B升级）"""
    def __init__(self, user_id: str, tenant_id: str, role: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role
    
    def is_admin(self) -> bool:
        """是否管理员"""
        return self.role == "admin"
    
    def is_doctor(self) -> bool:
        """是否医生"""
        return self.role == "doctor"
    
    def is_patient(self) -> bool:
        """是否患者"""
        return self.role == "user"


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> CurrentUser:
    """
    获取当前认证用户信息（B2B升级版本）
    
    返回: CurrentUser对象，包含user_id, tenant_id, role
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return CurrentUser(
        user_id=payload["sub"],
        tenant_id=payload.get("tenant_id", "tenant-default"),  # 兼容旧Token
        role=payload.get("role", "user")  # 兼容旧Token
    )


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    """获取当前认证用户的ID（保留兼容性）"""
    current_user = get_current_user(credentials)
    return current_user.user_id


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> CurrentUser:
    """
    要求管理员权限（B2B升级）
    
    返回: CurrentUser对象
    """
    current_user = get_current_user(credentials)
    
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    return current_user


def require_doctor_or_admin(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> CurrentUser:
    """
    要求医生或管理员权限（B2B升级新增）
    
    返回: CurrentUser对象
    """
    current_user = get_current_user(credentials)
    
    if not (current_user.is_admin() or current_user.is_doctor()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要医生或管理员权限"
        )
    
    return current_user
