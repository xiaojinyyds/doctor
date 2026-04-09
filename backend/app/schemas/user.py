#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""用户Pydantic模型"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    email: EmailStr = Field(..., description="邮箱地址")


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    email: EmailStr = Field(..., description="邮箱")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")
    password: str = Field(..., min_length=8, max_length=20, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    account: str = Field(..., description="账号（邮箱或手机号）")
    password: str = Field(..., description="密码")


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求（发送验证码）"""
    email: EmailStr = Field(..., description="注册邮箱")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    email: EmailStr = Field(..., description="邮箱")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")
    new_password: str = Field(..., min_length=8, max_length=20, description="新密码")


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    email: str
    nickname: Optional[str]
    role: str
    status: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="页码")
    size: int = Field(..., description="每页数量")
    items: List[UserResponse] = Field(..., description="用户列表")


class UpdateUserStatusRequest(BaseModel):
    """更新用户状态请求"""
    status: str = Field(..., pattern="^(active|disabled)$", description="状态：active/disabled")


class UpdateUserRoleRequest(BaseModel):
    """更新用户角色请求"""
    role: str = Field(..., pattern="^(user|doctor|admin)$", description="角色：user/doctor/admin")


class AdminResetPasswordRequest(BaseModel):
    """管理员重置密码请求"""
    new_password: str = Field(..., min_length=8, max_length=20, description="新密码")

