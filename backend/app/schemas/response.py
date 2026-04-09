#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""统一响应模型"""
from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar

DataT = TypeVar('DataT')


class ResponseModel(BaseModel, Generic[DataT]):
    """统一响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[DataT] = None


class SuccessResponse(ResponseModel):
    """成功响应"""
    code: int = 200
    message: str = "操作成功"


class ErrorResponse(ResponseModel):
    """错误响应"""
    code: int = 400
    message: str = "操作失败"
    data: None = None


class StandardResponse(ResponseModel):
    """标准响应格式（兼容新接口）"""
    pass


# 别名：保持兼容性
ApiResponseModel = ResponseModel


class ApiResponse:
    """API响应工具类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 200):
        """成功响应"""
        return {
            "code": code,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error(message: str = "操作失败", code: int = 400, data: Any = None):
        """错误响应"""
        return {
            "code": code,
            "message": message,
            "data": data
        }

