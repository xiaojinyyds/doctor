# API v1版本


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""API v1路由"""

# 导出所有路由模块，包括v2评估接口
from . import auth, assessment, admin, share, knowledge, assessment_v2

__all__ = ['auth', 'assessment', 'admin', 'share', 'knowledge', 'assessment_v2']
