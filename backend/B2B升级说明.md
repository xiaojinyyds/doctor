# B2B升级后端改造说明

## 已完成的改造

### 1. 认证系统升级 ✅
- **文件**: `app/core/security.py`
- **改动**:
  - JWT Token增加 `tenant_id` 和 `role` 字段
  - 新增 `CurrentUser` 类，封装用户信息
  - 新增 `get_current_user()` 方法，返回完整用户信息
  - 新增 `require_doctor_or_admin()` 权限装饰器

### 2. 用户模型升级 ✅
- **文件**: `app/models/user.py`
- **改动**:
  - 增加 `tenant_id` 字段（租户ID）
  - 增加 `department` 字段（科室）
  - 增加 `title` 字段（职称）
  - 增加 `employee_id` 字段（工号）
  - 增加 `is_active` 字段（是否激活）

### 3. 租户模型 ✅
- **文件**: `app/models/tenant.py`（新增）
- **功能**: 管理医院/机构信息

### 4. 评估模型升级 ✅
- **文件**: `app/models/assessment.py`
- **改动**:
  - 增加 `tenant_id` 字段
  - 增加 `status` 字段（审核状态）
  - 增加 `reviewed_by` 字段（审核医生）
  - 增加 `reviewed_at` 字段（审核时间）
  - 增加 `doctor_comment` 字段（医生意见）
  - 增加 `doctor_risk_level` 字段（医生判断的风险等级）
  - 增加 `is_batch` 字段（是否批量筛查）
  - 增加 `batch_task_id` 字段（批量任务ID）

### 5. 医生工作台API ✅
- **文件**: `app/api/v1/doctor.py`（新增）
- **接口**:
  - `GET /api/v1/doctor/pending-assessments` - 获取待审核列表
  - `GET /api/v1/doctor/assessments/{id}` - 获取评估详情
  - `POST /api/v1/doctor/assessments/{id}/approve` - 审核通过
  - `POST /api/v1/doctor/assessments/{id}/reject` - 驳回评估
  - `GET /api/v1/doctor/statistics` - 工作台统计

### 6. 登录注册升级 ✅
- **文件**: `app/api/v1/auth.py`
- **改动**:
  - 登录时Token包含 `tenant_id` 和 `role`
  - 注册时自动分配到默认租户

## 启动步骤

### 1. 确认数据库已迁移
```bash
# 确认 backend/my.sql 已经执行
mysql -u root -p tumor_screening < backend/my.sql
```

### 2. 启动后端服务
```bash
cd backend
python run.py
```

### 3. 访问API文档
打开浏览器访问: http://localhost:8000/docs

### 4. 运行测试脚本
```bash
cd backend
python test_b2b_upgrade.py
```

## 测试账号

数据库中已包含以下测试账号（密码均为 `admin123`）：

| 邮箱 | 角色 | 租户 | 说明 |
|------|------|------|------|
| admin@xiehe.com | admin | 北京协和医院 | 管理员 |
| doctor@xiehe.com | doctor | 北京协和医院 | 医生 |
| patient@xiehe.com | user | 北京协和医院 | 患者 |

## API使用示例

### 1. 登录获取Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "account": "doctor@xiehe.com",
    "password": "admin123"
  }'
```

### 2. 获取待审核列表
```bash
curl -X GET "http://localhost:8000/api/v1/doctor/pending-assessments?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 审核通过
```bash
curl -X POST "http://localhost:8000/api/v1/doctor/assessments/{assessment_id}/approve" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_comment": "AI评估结果准确，同意",
    "doctor_risk_level": "高风险"
  }'
```

## 下一步工作

### 后端待开发功能
- [ ] 批量筛查API（`app/api/v1/batch.py`）
- [ ] 机构统计API（`app/api/v1/statistics.py`）
- [ ] 租户管理API（`app/api/v1/tenant.py`）
- [ ] 操作日志记录

### 前端待开发功能
- [ ] 医生工作台页面
- [ ] 批量筛查页面
- [ ] 数据看板页面
- [ ] 机构管理页面

## 注意事项

1. **租户隔离**: 所有查询都会自动过滤 `tenant_id`，确保数据隔离
2. **权限控制**: 使用 `require_doctor_or_admin` 装饰器限制接口访问
3. **兼容性**: 旧的Token仍然可以使用（会自动分配默认租户）
4. **审核流程**: 新创建的评估默认状态为 `pending`，需要医生审核后才能查看

## 常见问题

### Q: 登录后提示权限不足？
A: 检查用户的 `role` 字段是否正确设置为 `doctor` 或 `admin`

### Q: 查询不到数据？
A: 检查用户的 `tenant_id` 是否与数据的 `tenant_id` 一致

### Q: Token解析失败？
A: 确认Token格式正确，且包含 `tenant_id` 和 `role` 字段

## 技术支持

如有问题，请查看：
- API文档: http://localhost:8000/docs
- 系统日志: 控制台输出
- 数据库日志: MySQL日志
