#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""辅助函数"""
import random
import string
import uuid
import secrets


def generate_verification_code(length: int = 6) -> str:
    """
    生成验证码
    
    Args:
        length: 验证码长度
        
    Returns:
        str: 验证码字符串
    """
    return ''.join(random.choices(string.digits, k=length))


def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4())


def generate_share_token(length: int = 32) -> str:
    """
    生成安全的分享令牌
    
    Args:
        length: 令牌长度
        
    Returns:
        str: 随机令牌字符串
    """
    return secrets.token_urlsafe(length)[:length]


def hash_share_password(password: str) -> str:
    """
    对分享密码进行简单哈希
    
    Args:
        password: 原始密码
        
    Returns:
        str: 哈希后的密码
    """
    # 使用简单的哈希，因为分享密码不需要像用户密码那样安全
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def verify_share_password(password: str, hashed: str) -> bool:
    """
    验证分享密码
    
    Args:
        password: 用户输入的密码
        hashed: 存储的哈希值
        
    Returns:
        bool: 是否匹配
    """
    return hash_share_password(password) == hashed

