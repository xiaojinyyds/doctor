#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Redis客户端"""
import redis
import json
from typing import Optional, Any
from app.core.config import settings


class RedisClient:
    """Redis客户端封装"""
    
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = self.client.get(key)
            if value:
                # 尝试解析JSON，如果失败则返回原始字符串
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = 3600):
        """设置缓存"""
        try:
            # 如果value是字符串，直接存储；否则JSON序列化
            if isinstance(value, str):
                stored_value = value
            else:
                stored_value = json.dumps(value, ensure_ascii=False)
            
            self.client.setex(key, expire, stored_value)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str):
        """删除缓存"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            return False


# 全局Redis客户端
redis_client = RedisClient()

