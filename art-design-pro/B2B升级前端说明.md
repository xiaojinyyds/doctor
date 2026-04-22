# B2B升级前端改造说明

## 已完成的改造

### 1. API层 ✅
- **新增文件**: `src/api/doctor.ts`
- **功能**: 医生工作台相关API
  - 获取待审核列表
  - 获取评估详情
  - 审核通过/驳回
  - 工作台统计

### 2. 类型定义 ✅
- **修改文件**: `src/typings/api.d.ts`
- **改动**: UserInfo增加B2B字段
  - `tenantId`: 租户ID
  - `role`: 角色（user/doctor/admin）
  - `department`: 科室
  - `title`: 职称
  - `employeeId`: 工号

### 3. 认证API升级 ✅
- **修改文件**: `src/api/auth.ts`
- **改动**: `fetchGetUserInfo` 返回租户和角色信息

### 4. 医生工作台页面 ✅
- **新增文件**: `src/views/doctor/pending-list.vue`
- **功能**:
  - 统计卡片（待审核/今日已审/本月筛查）
  - 待审核列表（支持风险等级筛选）
  - 审核对话框（同意/修改/驳回）
  - 分页功能

### 5. 路由配置 ✅
- **修改文件**: `src/router/modules/doctor.ts`
- **改动**: 增加待审核列表路由

## 使用说明

### 1. 启动前端
```bash
cd art-design-pro
pnpm install  # 如果还没安装依赖
pnpm dev
```

### 2. 访问地址
打开浏览器访问: http://localhost:5173

### 3. 测试账号
使用医生账号登录：
- 邮箱: `doctor@xiehe.com`
- 密码: `admin123`

### 4. 功能测试
登录后，左侧菜单会显示"医生工作台"，点击进入：
- 查看待审核列表
- 筛选不同风险等级
- 点击"审核"按钮进行审核
- 查看统计数据

## 页面截图说明

### 医生工作台 - 待审核列表
```
┌─────────────────────────────────────────────────┐
│ 统计卡片区域                                     │
│ [待审核: 12] [今日已审: 5] [本月筛查: 156]      │
├─────────────────────────────────────────────────┤
│ 待审核列表                                       │
│ [全部] [高风险] [中风险] [低风险]               │
├─────────────────────────────────────────────────┤
│ 风险等级 | 患者 | 基本信息 | AI评分 | 操作      │
│ 🔴高风险 | 张三 | 65岁男   | 82     | [审核]   │
│ 🟡中风险 | 李四 | 52岁女   | 65     | [审核]   │
│ 🟢低风险 | 王五 | 38岁男   | 28     | [审核]   │
└─────────────────────────────────────────────────┘
```

### 审核对话框
```
┌─────────────────────────────────────────────────┐
│ 审核评估结果                                     │
├─────────────────────────────────────────────────┤
│ 患者姓名: 张三                                   │
│ 基本信息: 65岁 男                                │
│ AI风险等级: 🔴 高风险                            │
│ AI评分: 82                                       │
├─────────────────────────────────────────────────┤
│ 审核决定:                                        │
│ ○ 同意AI判断                                     │
│ ○ 修改风险等级                                   │
│ ○ 驳回重评                                       │
│                                                  │
│ 医生意见:                                        │
│ [文本框]                                         │
│                                                  │
│ [取消] [提交审核]                                │
└─────────────────────────────────────────────────┘
```

## 待开发功能

### 前端页面
- [ ] 批量筛查页面（`src/views/admin/batch-screening.vue`）
- [ ] 数据看板页面（`src/views/admin/dashboard.vue`）
- [ ] 机构管理页面（`src/views/admin/tenant-manage.vue`）
- [ ] 用户管理页面（增强版，支持角色分配）

### API接口
- [ ] 批量筛查API（`src/api/batch.ts`）
- [ ] 机构统计API（`src/api/statistics.ts`）
- [ ] 租户管理API（`src/api/tenant.ts`）

### 功能增强
- [ ] 评估详情页面（显示完整的问卷和AI分析）
- [ ] 审核历史记录
- [ ] 医生工作量统计
- [ ] 导出功能（Excel/PDF）

## 技术要点

### 1. 权限控制
路由配置中使用 `roles` 字段控制访问权限：
```typescript
meta: {
  roles: ['doctor', 'admin']  // 只有医生和管理员可访问
}
```

### 2. API调用
所有API调用都会自动携带Token（在请求拦截器中处理）：
```typescript
import { fetchPendingAssessments } from '@/api/doctor'

const res = await fetchPendingAssessments({
  page: 1,
  page_size: 20
})
```

### 3. 状态管理
用户信息存储在Pinia Store中：
```typescript
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()
const userInfo = userStore.getUserInfo  // 包含租户和角色信息
```

### 4. 样式规范
- 使用Element Plus组件库
- 使用SCSS编写样式
- 遵循现有的设计风格

## 常见问题

### Q: 登录后看不到医生工作台菜单？
A: 检查用户角色是否为 `doctor` 或 `admin`

### Q: API调用失败？
A: 
1. 检查后端服务是否启动（http://localhost:8000）
2. 检查Token是否有效
3. 查看浏览器控制台的错误信息

### Q: 页面样式错乱？
A: 
1. 清除浏览器缓存
2. 重新运行 `pnpm dev`
3. 检查Element Plus是否正确引入

### Q: 如何调试？
A: 
1. 打开浏览器开发者工具（F12）
2. 查看Network标签页的API请求
3. 查看Console标签页的日志输出

## 下一步计划

### 短期（1周内）
1. 完善评估详情页面
2. 增加审核历史记录
3. 优化移动端适配

### 中期（2-4周）
1. 开发批量筛查功能
2. 开发数据看板
3. 增加导出功能

### 长期（1-3个月）
1. 开发机构管理功能
2. 增加更多统计图表
3. 优化用户体验

## 技术支持

如有问题，请查看：
- Element Plus文档: https://element-plus.org/
- Vue 3文档: https://cn.vuejs.org/
- TypeScript文档: https://www.typescriptlang.org/

## 贡献指南

1. 创建新分支: `git checkout -b feature/your-feature`
2. 提交代码: `git commit -m "feat: add your feature"`
3. 推送分支: `git push origin feature/your-feature`
4. 创建Pull Request

## 更新日志

### v2.0.0 (2026-04-19)
- ✅ 增加医生工作台功能
- ✅ 支持多租户架构
- ✅ 增加角色权限控制
- ✅ 优化用户信息管理
