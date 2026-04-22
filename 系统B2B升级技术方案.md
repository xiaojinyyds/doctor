# 肿瘤筛查系统 - B2B升级技术实施方案

**文档版本**: v1.0  
**编制日期**: 2026年4月19日  
**实施周期**: 4-6周  
**技术负责人**: 待定

---

## 📋 目录

1. [升级总览](#1-升级总览)
2. [数据库架构升级](#2-数据库架构升级)
3. [后端API升级](#3-后端api升级)
4. [前端界面升级](#4-前端界面升级)
5. [部署架构升级](#5-部署架构升级)
6. [开发排期](#6-开发排期)

---

## 1. 升级总览

### 1.1 现状分析

**当前架构**:
```
用户 → 前端(Vue3) → 后端(FastAPI) → 数据库(MySQL)
                                    → Redis(缓存)
```

**存在问题**:
❌ 单租户设计，无法支持多家医院  
❌ 缺少权限管理，所有用户权限相同  
❌ 没有审核流程，AI结果直接给用户  
❌ 数据统计简单，无法满足机构需求  
❌ 无法批量处理，效率低

### 1.2 升级目标

**核心改造**:
✅ 多租户架构（支持多家医院独立使用）  
✅ 角色权限系统（管理员/医生/普通用户）  
✅ 医生审核流程（AI结果需医生确认）  
✅ 批量筛查功能（Excel导入/导出）  
✅ 机构数据看板（统计分析）



### 1.3 升级优先级

我建议分三个阶段实施：

#### 🔥 第一阶段（核心功能，2周）- 必须做
1. **多租户架构** - 最基础，影响所有功能
2. **角色权限系统** - 区分管理员/医生/用户
3. **医生工作台** - B2B的核心价值

#### ⭐ 第二阶段（增强功能，1.5周）- 重要
4. **批量筛查** - 提升效率的关键
5. **数据统计看板** - 机构决策依据

#### 💡 第三阶段（优化功能，1周）- 可选
6. **HIS对接接口** - 按需定制
7. **移动端适配** - 提升体验

**建议**: 先做第一阶段，验证可行性后再做第二阶段

---

## 2. 数据库架构升级

### 2.1 核心表结构变化

#### 变化1: 新增租户表

**目的**: 支持多家医院独立使用

```sql
-- 租户表（医院/机构）
CREATE TABLE tenants (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '机构名称',
    type VARCHAR(20) NOT NULL COMMENT '机构类型: hospital/clinic/checkup',
    contact_person VARCHAR(50) COMMENT '联系人',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    license_key VARCHAR(100) UNIQUE COMMENT '授权码',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/suspended/expired',
    expire_date DATE COMMENT '到期日期',
    max_users INT DEFAULT 100 COMMENT '最大用户数',
    max_assessments_per_month INT DEFAULT 1000 COMMENT '每月最大筛查数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 示例数据
INSERT INTO tenants VALUES 
('tenant-001', '北京协和医院', 'hospital', '张医生', '13800138000', 
 'LICENSE-XH-2026', 'active', '2027-04-19', 500, 5000, NOW(), NOW());
```



#### 变化2: 用户表增加租户和角色

**目的**: 用户归属某个机构，并有不同角色

```sql
-- 修改现有users表
ALTER TABLE users 
ADD COLUMN tenant_id VARCHAR(36) COMMENT '所属机构ID',
ADD COLUMN role VARCHAR(20) DEFAULT 'patient' COMMENT '角色: admin/doctor/patient',
ADD COLUMN department VARCHAR(50) COMMENT '科室（医生用）',
ADD COLUMN title VARCHAR(50) COMMENT '职称（医生用）',
ADD COLUMN is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
ADD FOREIGN KEY (tenant_id) REFERENCES tenants(id);

-- 创建索引
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_role ON users(role);

-- 角色说明
-- admin: 机构管理员（查看所有数据、管理用户）
-- doctor: 医生（审核评估结果、查看患者数据）
-- patient: 患者（只能查看自己的数据）
```

**数据迁移**:
```sql
-- 将现有用户设置为默认租户
UPDATE users SET tenant_id = 'tenant-default' WHERE tenant_id IS NULL;

-- 将管理员角色的用户设置为admin
UPDATE users SET role = 'admin' WHERE email IN ('admin@example.com');
```

#### 变化3: 评估表增加审核状态

**目的**: AI评估后需要医生审核

```sql
-- 修改assessments表
ALTER TABLE assessments
ADD COLUMN tenant_id VARCHAR(36) COMMENT '所属机构',
ADD COLUMN status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/approved/rejected',
ADD COLUMN reviewed_by VARCHAR(36) COMMENT '审核医生ID',
ADD COLUMN reviewed_at TIMESTAMP COMMENT '审核时间',
ADD COLUMN doctor_comment TEXT COMMENT '医生意见',
ADD COLUMN doctor_risk_level VARCHAR(20) COMMENT '医生判断的风险等级',
ADD FOREIGN KEY (tenant_id) REFERENCES tenants(id),
ADD FOREIGN KEY (reviewed_by) REFERENCES users(id);

-- 状态说明
-- pending: 待审核（AI刚生成）
-- approved: 已通过（医生确认AI结果）
-- rejected: 已驳回（医生认为AI结果有误）
```



#### 变化4: 新增批量任务表

**目的**: 支持批量导入患者进行筛查

```sql
-- 批量任务表
CREATE TABLE batch_tasks (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    created_by VARCHAR(36) NOT NULL COMMENT '创建人',
    task_name VARCHAR(100) COMMENT '任务名称',
    file_url VARCHAR(255) COMMENT '上传的Excel文件路径',
    total_count INT DEFAULT 0 COMMENT '总数',
    success_count INT DEFAULT 0 COMMENT '成功数',
    failed_count INT DEFAULT 0 COMMENT '失败数',
    status VARCHAR(20) DEFAULT 'processing' COMMENT '状态: processing/completed/failed',
    error_log TEXT COMMENT '错误日志',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 批量任务明细表
CREATE TABLE batch_task_items (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL,
    row_number INT COMMENT 'Excel行号',
    patient_name VARCHAR(50),
    patient_phone VARCHAR(20),
    questionnaire_data JSON COMMENT '问卷数据',
    assessment_id VARCHAR(36) COMMENT '生成的评估ID',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/success/failed',
    error_message TEXT COMMENT '错误信息',
    FOREIGN KEY (task_id) REFERENCES batch_tasks(id),
    FOREIGN KEY (assessment_id) REFERENCES assessments(id)
);
```

#### 变化5: 新增操作日志表

**目的**: 记录关键操作，便于审计

```sql
-- 操作日志表
CREATE TABLE operation_logs (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36),
    user_id VARCHAR(36),
    action VARCHAR(50) NOT NULL COMMENT '操作类型: login/create_assessment/approve/reject',
    resource_type VARCHAR(50) COMMENT '资源类型: assessment/user/tenant',
    resource_id VARCHAR(36) COMMENT '资源ID',
    details JSON COMMENT '详细信息',
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建索引
CREATE INDEX idx_logs_tenant ON operation_logs(tenant_id);
CREATE INDEX idx_logs_user ON operation_logs(user_id);
CREATE INDEX idx_logs_action ON operation_logs(action);
CREATE INDEX idx_logs_created ON operation_logs(created_at);
```



### 2.2 数据迁移脚本

**完整迁移SQL**（按顺序执行）:

```sql
-- ============================================
-- 肿瘤筛查系统 B2B升级 数据库迁移脚本
-- 版本: v2.0
-- 日期: 2026-04-19
-- ============================================

-- 步骤1: 创建租户表
CREATE TABLE IF NOT EXISTS tenants (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    contact_person VARCHAR(50),
    contact_phone VARCHAR(20),
    license_key VARCHAR(100) UNIQUE,
    status VARCHAR(20) DEFAULT 'active',
    expire_date DATE,
    max_users INT DEFAULT 100,
    max_assessments_per_month INT DEFAULT 1000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 步骤2: 创建默认租户（用于迁移现有数据）
INSERT INTO tenants (id, name, type, status) 
VALUES ('tenant-default', '默认机构', 'hospital', 'active');

-- 步骤3: 修改users表
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'tenant-default',
ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'patient',
ADD COLUMN IF NOT EXISTS department VARCHAR(50),
ADD COLUMN IF NOT EXISTS title VARCHAR(50),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 步骤4: 修改assessments表
ALTER TABLE assessments
ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'tenant-default',
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'approved',
ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(36),
ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS doctor_comment TEXT,
ADD COLUMN IF NOT EXISTS doctor_risk_level VARCHAR(20);

-- 步骤5: 修改questionnaires表
ALTER TABLE questionnaires
ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'tenant-default';

-- 步骤6: 创建批量任务表
CREATE TABLE IF NOT EXISTS batch_tasks (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    created_by VARCHAR(36) NOT NULL,
    task_name VARCHAR(100),
    file_url VARCHAR(255),
    total_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'processing',
    error_log TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS batch_task_items (
    id VARCHAR(36) PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL,
    row_number INT,
    patient_name VARCHAR(50),
    patient_phone VARCHAR(20),
    questionnaire_data JSON,
    assessment_id VARCHAR(36),
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT
);

-- 步骤7: 创建操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36),
    user_id VARCHAR(36),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(36),
    details JSON,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 步骤8: 创建索引
CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_assessments_tenant ON assessments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON assessments(status);
CREATE INDEX IF NOT EXISTS idx_logs_tenant ON operation_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_logs_created ON operation_logs(created_at);

-- 步骤9: 数据迁移（将现有用户关联到默认租户）
UPDATE users SET tenant_id = 'tenant-default' WHERE tenant_id IS NULL;
UPDATE assessments SET tenant_id = 'tenant-default' WHERE tenant_id IS NULL;
UPDATE questionnaires SET tenant_id = 'tenant-default' WHERE tenant_id IS NULL;

-- 步骤10: 将现有评估设置为已审核状态
UPDATE assessments SET status = 'approved', reviewed_at = created_at 
WHERE status IS NULL OR status = '';

COMMIT;
```

**执行方式**:
```bash
# 方式1: 直接执行SQL文件
mysql -u root -p tumor_screening < migration_v2.sql

# 方式2: 使用Alembic（推荐）
cd backend
alembic revision --autogenerate -m "B2B upgrade"
alembic upgrade head
```



---

## 3. 后端API升级

### 3.1 认证系统改造

#### 改造1: JWT Token增加租户和角色信息

**现状**: Token只包含user_id

**改造后**: Token包含 user_id + tenant_id + role

```python
# backend/app/core/security.py

from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def create_access_token(user_id: str, tenant_id: str, role: str) -> str:
    """创建JWT Token"""
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    payload = {
        "user_id": user_id,
        "tenant_id": tenant_id,  # ⭐ 新增
        "role": role,             # ⭐ 新增
        "exp": expire
    }
    
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def get_current_user(token: str) -> dict:
    """解析Token获取用户信息"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return {
            "user_id": payload["user_id"],
            "tenant_id": payload["tenant_id"],
            "role": payload["role"]
        }
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### 改造2: 权限装饰器

**目的**: 限制某些API只能特定角色访问

```python
# backend/app/core/permissions.py

from functools import wraps
from fastapi import HTTPException, Depends
from app.core.security import get_current_user

def require_role(*allowed_roles):
    """角色权限装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从依赖注入获取当前用户
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")
            
            if current_user['role'] not in allowed_roles:
                raise HTTPException(
                    status_code=403, 
                    detail=f"需要{allowed_roles}权限"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# 使用示例
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/admin/users")
@require_role("admin")  # ⭐ 只有管理员可以访问
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """获取所有用户（仅管理员）"""
    pass

@router.post("/assessments/{id}/approve")
@require_role("admin", "doctor")  # ⭐ 管理员和医生可以访问
async def approve_assessment(id: str, current_user: dict = Depends(get_current_user)):
    """审核评估结果"""
    pass
```



#### 改造3: 数据查询自动过滤租户

**目的**: 确保用户只能看到自己机构的数据

```python
# backend/app/core/tenant.py

from sqlalchemy.orm import Session
from fastapi import Depends

def get_tenant_filter(current_user: dict):
    """获取租户过滤条件"""
    return {"tenant_id": current_user["tenant_id"]}


# 使用示例
from app.models import Assessment

@router.get("/assessments")
async def get_assessments(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取评估列表（自动过滤租户）"""
    
    # ⭐ 自动添加租户过滤
    query = db.query(Assessment).filter(
        Assessment.tenant_id == current_user["tenant_id"]
    )
    
    # 如果是普通用户，只能看自己的
    if current_user["role"] == "patient":
        query = query.filter(Assessment.user_id == current_user["user_id"])
    
    return query.all()
```

### 3.2 新增核心API

#### API 1: 医生工作台

```python
# backend/app/api/v1/doctor.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.core.permissions import require_role
from app.models import Assessment, User

router = APIRouter(prefix="/api/v1/doctor", tags=["医生工作台"])

@router.get("/pending-assessments")
@require_role("doctor", "admin")
async def get_pending_assessments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    risk_level: str = Query(None),  # 筛选风险等级
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取待审核的评估列表
    
    返回: 按风险等级排序的待审核列表
    """
    query = db.query(Assessment).filter(
        Assessment.tenant_id == current_user["tenant_id"],
        Assessment.status == "pending"
    )
    
    # 风险等级筛选
    if risk_level:
        query = query.filter(Assessment.overall_risk_level == risk_level)
    
    # 按风险分数降序（高风险优先）
    query = query.order_by(Assessment.overall_risk_score.desc())
    
    # 分页
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [item.to_dict() for item in items]
    }


@router.post("/assessments/{assessment_id}/approve")
@require_role("doctor", "admin")
async def approve_assessment(
    assessment_id: str,
    doctor_comment: str = None,
    doctor_risk_level: str = None,  # 医生可以修改风险等级
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    审核通过评估结果
    """
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")
    
    # 更新审核信息
    assessment.status = "approved"
    assessment.reviewed_by = current_user["user_id"]
    assessment.reviewed_at = datetime.utcnow()
    assessment.doctor_comment = doctor_comment
    
    if doctor_risk_level:
        assessment.doctor_risk_level = doctor_risk_level
    
    db.commit()
    
    # 记录操作日志
    log_operation(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        action="approve_assessment",
        resource_id=assessment_id
    )
    
    return {"message": "审核通过", "assessment_id": assessment_id}


@router.post("/assessments/{assessment_id}/reject")
@require_role("doctor", "admin")
async def reject_assessment(
    assessment_id: str,
    reason: str,  # 驳回原因（必填）
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    驳回评估结果
    """
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")
    
    assessment.status = "rejected"
    assessment.reviewed_by = current_user["user_id"]
    assessment.reviewed_at = datetime.utcnow()
    assessment.doctor_comment = f"驳回原因: {reason}"
    
    db.commit()
    
    return {"message": "已驳回", "assessment_id": assessment_id}
```



#### API 2: 批量筛查

```python
# backend/app/api/v1/batch.py

from fastapi import APIRouter, UploadFile, File, BackgroundTasks
import pandas as pd
import uuid
from app.services.risk_engine import RiskEngine

router = APIRouter(prefix="/api/v1/batch", tags=["批量筛查"])

@router.post("/upload")
@require_role("admin", "doctor")
async def upload_batch_file(
    file: UploadFile = File(...),
    task_name: str = None,
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传Excel文件进行批量筛查
    
    Excel格式要求:
    | 姓名 | 手机号 | 年龄 | 性别 | 身高 | 体重 | ... |
    """
    
    # 1. 保存文件
    file_path = f"uploads/batch/{uuid.uuid4()}.xlsx"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 2. 读取Excel
    try:
        df = pd.read_excel(file_path)
        total_count = len(df)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel格式错误: {str(e)}")
    
    # 3. 创建批量任务
    task = BatchTask(
        id=str(uuid.uuid4()),
        tenant_id=current_user["tenant_id"],
        created_by=current_user["user_id"],
        task_name=task_name or f"批量筛查_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        file_url=file_path,
        total_count=total_count,
        status="processing"
    )
    db.add(task)
    db.commit()
    
    # 4. 后台异步处理
    background_tasks.add_task(
        process_batch_task,
        task_id=task.id,
        file_path=file_path,
        tenant_id=current_user["tenant_id"]
    )
    
    return {
        "message": "文件上传成功，正在后台处理",
        "task_id": task.id,
        "total_count": total_count
    }


async def process_batch_task(task_id: str, file_path: str, tenant_id: str):
    """
    后台处理批量任务
    """
    db = SessionLocal()
    task = db.query(BatchTask).filter(BatchTask.id == task_id).first()
    
    try:
        df = pd.read_excel(file_path)
        risk_engine = RiskEngine()
        
        for index, row in df.iterrows():
            try:
                # 1. 创建问卷
                questionnaire_data = {
                    "age": row["年龄"],
                    "gender": row["性别"],
                    "height": row["身高"],
                    "weight": row["体重"],
                    # ... 其他字段
                }
                
                # 2. 风险评估
                result = risk_engine.predict(questionnaire_data)
                
                # 3. 保存评估结果
                assessment = Assessment(
                    tenant_id=tenant_id,
                    overall_risk_score=result["overall_risk"]["score"],
                    overall_risk_level=result["overall_risk"]["level"],
                    status="pending"  # 待医生审核
                )
                db.add(assessment)
                db.flush()
                
                # 4. 记录明细
                item = BatchTaskItem(
                    task_id=task_id,
                    row_number=index + 2,  # Excel从第2行开始
                    patient_name=row.get("姓名"),
                    patient_phone=row.get("手机号"),
                    assessment_id=assessment.id,
                    status="success"
                )
                db.add(item)
                
                task.success_count += 1
                
            except Exception as e:
                # 记录失败
                item = BatchTaskItem(
                    task_id=task_id,
                    row_number=index + 2,
                    status="failed",
                    error_message=str(e)
                )
                db.add(item)
                task.failed_count += 1
        
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        task.status = "failed"
        task.error_log = str(e)
        db.commit()
    finally:
        db.close()


@router.get("/tasks/{task_id}")
async def get_batch_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询批量任务状态
    """
    task = db.query(BatchTask).filter(
        BatchTask.id == task_id,
        BatchTask.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "task_id": task.id,
        "task_name": task.task_name,
        "status": task.status,
        "total_count": task.total_count,
        "success_count": task.success_count,
        "failed_count": task.failed_count,
        "progress": round(
            (task.success_count + task.failed_count) / task.total_count * 100, 2
        ) if task.total_count > 0 else 0
    }
```



#### API 3: 机构数据统计

```python
# backend/app/api/v1/statistics.py

from fastapi import APIRouter
from sqlalchemy import func
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/statistics", tags=["数据统计"])

@router.get("/overview")
@require_role("admin", "doctor")
async def get_statistics_overview(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取机构统计概览
    """
    tenant_id = current_user["tenant_id"]
    
    # 总筛查数
    total_assessments = db.query(func.count(Assessment.id)).filter(
        Assessment.tenant_id == tenant_id
    ).scalar()
    
    # 本月筛查数
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    month_assessments = db.query(func.count(Assessment.id)).filter(
        Assessment.tenant_id == tenant_id,
        Assessment.created_at >= month_start
    ).scalar()
    
    # 风险分布
    risk_distribution = db.query(
        Assessment.overall_risk_level,
        func.count(Assessment.id)
    ).filter(
        Assessment.tenant_id == tenant_id
    ).group_by(Assessment.overall_risk_level).all()
    
    # 待审核数量
    pending_count = db.query(func.count(Assessment.id)).filter(
        Assessment.tenant_id == tenant_id,
        Assessment.status == "pending"
    ).scalar()
    
    return {
        "total_assessments": total_assessments,
        "month_assessments": month_assessments,
        "pending_count": pending_count,
        "risk_distribution": {
            level: count for level, count in risk_distribution
        }
    }


@router.get("/trend")
@require_role("admin")
async def get_assessment_trend(
    days: int = Query(30, ge=7, le=365),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取筛查趋势（按天统计）
    """
    tenant_id = current_user["tenant_id"]
    start_date = datetime.now() - timedelta(days=days)
    
    # 按日期分组统计
    trend_data = db.query(
        func.date(Assessment.created_at).label("date"),
        func.count(Assessment.id).label("count")
    ).filter(
        Assessment.tenant_id == tenant_id,
        Assessment.created_at >= start_date
    ).group_by(func.date(Assessment.created_at)).all()
    
    return {
        "dates": [str(item.date) for item in trend_data],
        "counts": [item.count for item in trend_data]
    }
```

---

## 4. 前端界面升级

### 4.1 新增页面结构

```
art-design-pro/src/views/
├── admin/                    # 机构管理（新增）
│   ├── dashboard.vue        # 数据看板
│   ├── users.vue            # 用户管理
│   ├── batch-screening.vue  # 批量筛查
│   └── settings.vue         # 机构设置
├── doctor/                   # 医生工作台（新增）
│   ├── pending-list.vue     # 待审核列表
│   ├── review-detail.vue    # 审核详情
│   └── my-patients.vue      # 我的患者
└── patient/                  # 患者端（现有）
    ├── questionnaire.vue
    ├── report.vue
    └── history.vue
```

### 4.2 核心页面设计

#### 页面1: 医生工作台

**路由**: `/doctor/pending`

**功能**: 
- 显示待审核评估列表
- 按风险等级排序（高风险优先）
- 点击进入审核详情

**界面原型**:
```
┌─────────────────────────────────────────────────┐
│ 医生工作台 - 待审核列表 (12)                     │
├─────────────────────────────────────────────────┤
│ [全部] [高风险] [中风险] [低风险]  🔍 搜索       │
├─────────────────────────────────────────────────┤
│ 🔴 高风险 | 张三 | 65岁男 | AI评分: 82 | [审核] │
│ 🔴 高风险 | 李四 | 58岁女 | AI评分: 78 | [审核] │
│ 🟡 中风险 | 王五 | 52岁男 | AI评分: 65 | [审核] │
│ 🟢 低风险 | 赵六 | 38岁女 | AI评分: 28 | [审核] │
└─────────────────────────────────────────────────┘
```



**代码示例**:

```vue
<!-- art-design-pro/src/views/doctor/pending-list.vue -->
<template>
  <div class="doctor-workspace">
    <el-card class="header-card">
      <div class="stats-row">
        <el-statistic title="待审核" :value="pendingCount" />
        <el-statistic title="今日已审" :value="todayReviewed" />
        <el-statistic title="本月筛查" :value="monthTotal" />
      </div>
    </el-card>

    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>待审核列表</span>
          <el-radio-group v-model="filterRisk" @change="loadData">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="高风险">高风险</el-radio-button>
            <el-radio-button label="中风险">中风险</el-radio-button>
            <el-radio-button label="低风险">低风险</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-table :data="assessmentList" v-loading="loading">
        <el-table-column label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="getRiskTagType(row.overall_risk_level)"
              effect="dark"
            >
              {{ row.overall_risk_level }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="patient_name" label="患者" width="120" />
        <el-table-column label="基本信息" width="150">
          <template #default="{ row }">
            {{ row.age }}岁 {{ row.gender }}
          </template>
        </el-table-column>
        
        <el-table-column label="AI评分" width="100">
          <template #default="{ row }">
            <span class="risk-score">
              {{ (row.overall_risk_score * 100).toFixed(0) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="提交时间" width="180" />
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small"
              @click="handleReview(row.id)"
            >
              审核
            </el-button>
            <el-button 
              size="small"
              @click="handleViewDetail(row.id)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        @current-change="loadData"
      />
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog v-model="showReviewDialog" title="审核评估结果" width="800px">
      <div class="review-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="AI风险等级">
            <el-tag :type="getRiskTagType(currentAssessment.overall_risk_level)">
              {{ currentAssessment.overall_risk_level }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="AI评分">
            {{ (currentAssessment.overall_risk_score * 100).toFixed(0) }}
          </el-descriptions-item>
        </el-descriptions>

        <el-form :model="reviewForm" label-width="120px" style="margin-top: 20px">
          <el-form-item label="医生判断">
            <el-radio-group v-model="reviewForm.action">
              <el-radio label="approve">同意AI判断</el-radio>
              <el-radio label="modify">修改风险等级</el-radio>
              <el-radio label="reject">驳回重评</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item 
            v-if="reviewForm.action === 'modify'" 
            label="修改为"
          >
            <el-select v-model="reviewForm.doctor_risk_level">
              <el-option label="低风险" value="低风险" />
              <el-option label="中风险" value="中风险" />
              <el-option label="高风险" value="高风险" />
              <el-option label="极高风险" value="极高风险" />
            </el-select>
          </el-form-item>

          <el-form-item label="医生意见">
            <el-input
              v-model="reviewForm.doctor_comment"
              type="textarea"
              :rows="4"
              placeholder="请输入您的专业意见..."
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="submitReview"
          :loading="submitting"
        >
          提交审核
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPendingAssessments, approveAssessment } from '@/api/doctor'

const loading = ref(false)
const assessmentList = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterRisk = ref('')

const showReviewDialog = ref(false)
const currentAssessment = ref({})
const reviewForm = ref({
  action: 'approve',
  doctor_risk_level: '',
  doctor_comment: ''
})
const submitting = ref(false)

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const res = await getPendingAssessments({
      page: page.value,
      page_size: pageSize.value,
      risk_level: filterRisk.value || undefined
    })
    assessmentList.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function handleReview(id) {
  currentAssessment.value = assessmentList.value.find(item => item.id === id)
  showReviewDialog.value = true
}

async function submitReview() {
  submitting.value = true
  try {
    if (reviewForm.value.action === 'approve') {
      await approveAssessment(currentAssessment.value.id, {
        doctor_comment: reviewForm.value.doctor_comment
      })
      ElMessage.success('审核通过')
    }
    // ... 其他逻辑
    
    showReviewDialog.value = false
    loadData()
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

function getRiskTagType(level) {
  const map = {
    '低风险': 'success',
    '中风险': 'warning',
    '高风险': 'danger',
    '极高风险': 'danger'
  }
  return map[level] || 'info'
}
</script>
```

---

## 6. 开发排期

### 6.1 详细时间表

#### 第一周（核心架构）

**Day 1-2: 数据库改造**
- [ ] 编写迁移SQL脚本
- [ ] 执行数据库迁移
- [ ] 验证数据完整性
- [ ] 创建测试租户和用户

**Day 3-4: 后端认证改造**
- [ ] 修改JWT Token结构
- [ ] 实现权限装饰器
- [ ] 改造现有API（添加租户过滤）
- [ ] 编写单元测试

**Day 5: 医生工作台API**
- [ ] 实现待审核列表API
- [ ] 实现审核通过/驳回API
- [ ] 测试API功能

#### 第二周（核心功能）

**Day 6-7: 批量筛查功能**
- [ ] 实现文件上传API
- [ ] 实现后台异步处理
- [ ] 实现进度查询API
- [ ] 测试批量处理

**Day 8-9: 前端医生工作台**
- [ ] 创建待审核列表页面
- [ ] 创建审核对话框
- [ ] 对接后端API
- [ ] 测试交互流程

**Day 10: 统计分析API**
- [ ] 实现概览统计API
- [ ] 实现趋势分析API
- [ ] 前端数据看板页面

#### 第三周（完善优化）

**Day 11-12: 批量筛查前端**
- [ ] 创建批量上传页面
- [ ] 实现进度显示
- [ ] 实现结果导出

**Day 13-14: 联调测试**
- [ ] 完整流程测试
- [ ] 修复Bug
- [ ] 性能优化

**Day 15: 文档和部署**
- [ ] 编写使用文档
- [ ] 准备演示环境
- [ ] 部署到测试服务器



### 6.2 人力配置建议

**最小团队**（3人）:
- 1名后端开发（负责API和数据库）
- 1名前端开发（负责界面）
- 1名测试（兼产品经理）

**理想团队**（5人）:
- 2名后端开发
- 2名前端开发
- 1名测试 + 1名产品经理

---

## 7. 风险控制

### 7.1 技术风险

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 数据迁移失败 | 高 | ✅ 提前备份数据库<br>✅ 在测试环境先验证 |
| 现有功能受影响 | 中 | ✅ 保持向后兼容<br>✅ 充分回归测试 |
| 性能下降 | 中 | ✅ 添加数据库索引<br>✅ 使用Redis缓存 |
| 批量处理超时 | 低 | ✅ 使用后台任务<br>✅ 分批处理 |

### 7.2 进度风险

**可能延期的环节**:
- 数据库迁移（如果数据量大）
- 批量筛查（异步处理复杂）
- 前端联调（接口对接）

**应对策略**:
- 预留1周缓冲时间
- 优先实现核心功能
- 非核心功能可以后续迭代

---

## 8. 验收标准

### 8.1 功能验收

**必须完成**:
- [x] 多租户架构（不同机构数据隔离）
- [x] 角色权限（管理员/医生/患者）
- [x] 医生审核流程（待审核→已审核）
- [x] 批量筛查（Excel导入/导出）
- [x] 数据统计看板（基础指标）

**可选完成**:
- [ ] HIS系统对接
- [ ] 移动端适配
- [ ] 高级统计分析

### 8.2 性能验收

- 响应时间: 90%请求<1秒
- 并发能力: 支持100+并发用户
- 批量处理: 1000条数据<5分钟
- 系统可用性: >99%

### 8.3 安全验收

- 数据隔离: 租户间数据完全隔离
- 权限控制: 角色权限正确生效
- 操作日志: 关键操作有记录
- 数据加密: 敏感数据加密存储

---

## 9. 总结与建议

### 9.1 核心改造点

1. **数据库**: 增加tenant_id字段，实现多租户
2. **认证**: JWT增加租户和角色信息
3. **权限**: 实现基于角色的访问控制
4. **审核**: 增加医生审核流程
5. **批量**: 支持Excel批量导入筛查

### 9.2 我的建议

**优先级排序**:
1. 🔥 **先做多租户+权限**（2周）- 这是基础
2. ⭐ **再做医生工作台**（1周）- 这是核心价值
3. 💡 **最后做批量筛查**（1周）- 这是效率提升

**为什么这样排序？**
- 多租户是基础，不做后面都没法做
- 医生工作台是B2B的核心卖点
- 批量筛查可以后续迭代

### 9.3 下一步行动

**立即可以开始**:
1. 创建数据库迁移脚本
2. 搭建测试环境
3. 创建测试租户和用户数据

**需要讨论的问题**:
1. 是否需要支持子账号？（一个机构多个管理员）
2. 医生审核是否必须？（还是可选）
3. 批量筛查的Excel模板格式？
4. 是否需要短信/邮件通知？

---

**文档结束**

**下一步**: 我可以帮你：
1. 生成完整的数据库迁移SQL
2. 编写具体的API代码
3. 创建前端页面模板
4. 准备测试数据

告诉我你想先做什么！🚀

