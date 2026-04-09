# 肿瘤数智化筛查系统

## 项目简介

肿瘤数智化筛查系统是一个集健康问卷、风险评估、医学影像分析于一体的智能化健康管理平台。系统采用先进的人工智能技术，为用户提供专业、便捷的健康筛查服务。

## 技术栈

### 前端
- **框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **构建工具**: Vite
- **样式**: SCSS

### 后端
- **框架**: FastAPI (Python)
- **数据库**: MySQL
- **缓存**: Redis
- **AI模型**: PyTorch
- **邮件服务**: SMTP
- **文件存储**: 阿里云OSS

## 主要功能

### 1. 健康问卷
- 多步骤问卷填写（基本信息、生活方式、病史、症状）
- 问卷数据验证和保存
- 自动生成评估报告

### 2. 风险评估
- AI智能风险评估算法
- 多维度健康风险分析
- 风险等级可视化展示
- 历史记录对比分析

### 3. 医学影像分析
- 支持乳腺超声影像上传
- 深度学习模型自动分析
- Grad-CAM热力图可视化
- 预测结果置信度展示

### 4. 筛查历史
- 查看所有历史筛查记录
- 问卷、评估、影像记录管理
- 数据导出和报告下载
- 历史趋势分析

### 5. 医生工作台（医生角色）
- 查看患者筛查数据
- 评估报告审核
- 影像分析结果查看
- 诊疗建议记录

### 6. 系统管理（管理员角色）
- 用户管理
- 角色权限管理
- 筛查记录管理
- 系统统计分析

## 项目结构

```
shensibei/
├── art-design-pro/          # 前端项目
│   ├── src/
│   │   ├── api/            # API接口
│   │   ├── components/     # 组件
│   │   ├── router/         # 路由配置
│   │   ├── store/          # 状态管理
│   │   ├── views/          # 页面视图
│   │   ├── utils/          # 工具函数
│   │   └── assets/         # 静态资源
│   ├── public/             # 公共资源
│   └── package.json
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # 数据模式
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── ml_models/          # AI模型
│   └── requirements.txt
├── data/                    # 数据文件
└── README.md
```

## 快速开始

### 前端启动

```bash
# 进入前端目录
cd art-design-pro

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建生产版本
pnpm build
```

访问地址：http://localhost:5173

### 后端启动

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate      # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
# 或
uvicorn app.main:app --reload --port 8000
```

访问地址：
- API服务：http://localhost:8000
- API文档：http://localhost:8000/docs

### 环境配置

在 `backend/` 目录下创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/tumor_screening
DB_PASSWORD=your_password

# 邮件配置
MAIL_HOST=smtp.qq.com
MAIL_PORT=465
MAIL_USERNAME=your_email@qq.com
MAIL_PASSWORD=your_auth_code
MAIL_FROM=your_email@qq.com
MAIL_FROM_NAME=肿瘤筛查系统

# JWT密钥
SECRET_KEY=your-secret-key-here

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# 阿里云OSS配置（可选）
OSS_ACCESS_KEY_ID=your_access_key
OSS_ACCESS_KEY_SECRET=your_access_secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your_bucket_name

# 调试模式
DEBUG=True
```

## 用户角色

系统支持三种用户角色：

1. **普通用户（user）**
   - 填写健康问卷
   - 查看风险评估结果
   - 上传医学影像
   - 查看个人筛查历史

2. **医生（doctor）**
   - 普通用户的所有权限
   - 查看患者筛查数据
   - 访问医生工作台
   - 提供诊疗建议

3. **管理员（admin）**
   - 医生的所有权限
   - 用户管理
   - 角色管理
   - 系统统计
   - 筛查记录管理

## 最近更新

### 2025-11-04
- ✅ 修复头像区域名字过长导致的UI溢出问题
- ✅ 创建内部使用文档页面，替代外部链接
- ✅ 优化使用文档页面配色，改用淡雅的浅蓝灰色渐变，与系统整体风格协调
- ✅ 将所有图标替换为系统iconfont图标，提升视觉一致性和美观度
- ✅ 添加使用文档路由配置
- ✅ 使用文档包含系统介绍、功能说明、使用流程、常见问题等
- ✅ 优化影像分析统计页面：
  - 统计卡片图标改为系统iconfont图标，统一大小和样式
  - 表格新增序号列和影像ID列
  - 置信度改为进度条展示，更直观
  - 为各列添加图标，提升可读性
  - 优化表格列宽，解决右侧空白问题
- ✅ 隐藏左侧菜单中的"结果页面"和"异常页面"，优化菜单结构
- ✅ 优化登录和注册页面视觉效果：
  - 左侧图片替换为医生图（login.jpg），更贴合医疗健康主题
  - 文案区域采用毛玻璃卡片设计（backdrop-filter: blur）
  - 主标题："肿瘤数智化筛查系统"，使用系统主题色
  - 副标题："AI赋能精准筛查 · 守护您的健康"
  - 优化图片位置和大小，视觉层次更清晰
  - 添加柔和的蓝色阴影效果
  - 保留原有背景和几何装饰元素
  - 响应式优化，适配不同屏幕尺寸

### 主要改进点

#### 1. UI优化
在 `art-design-pro/src/components/core/layouts/art-header-bar/style.scss` 中：
- 添加名字最大宽度限制（100px）
- 使用省略号显示过长的用户名
- 优化名字和角色标签的布局

#### 2. 使用文档页面
新增 `art-design-pro/src/views/system/user-docs/index.vue`：
- 系统介绍模块
- 功能说明折叠面板
- 使用流程可视化展示
- 常见问题FAQ
- 快速链接导航
- 响应式设计，支持移动端
- 采用淡雅的浅蓝灰色渐变背景（#e8f4f8 → #f5f7fa），与系统整体UI风格保持一致
- 使用系统iconfont图标替代Element Plus图标，视觉效果更统一美观

#### 3. 路由配置
在 `art-design-pro/src/router/modules/system.ts` 中：
- 添加 `/system/user-docs` 路由
- 配置为隐藏路由（不在菜单中显示）
- 所有用户均可访问

#### 4. 头部菜单优化
在 `art-design-pro/src/components/core/layouts/art-header-bar/index.vue` 中：
- 将"使用文档"从外部链接改为内部路由
- 优化点击跳转逻辑

#### 5. 影像分析统计页面优化
在 `art-design-pro/src/views/medical-image/statistics.vue` 中：
- **统计卡片图标优化**：
  - 总影像数：`&#xe667;` 影像图标
  - 已分析：`&#xe621;` 完成图标
  - 高风险：`&#xe86e;` 警告图标
  - 平均置信度：`&#xe7a5;` 数据图标
- **表格布局优化**：
  - 新增序号列，方便查看
  - 新增影像ID列，显示记录标识
  - 置信度列改为进度条展示，颜色随值变化（绿色>90%，蓝色>70%，橙色>50%，红色<50%）
  - 为预测类别、分析时间等列添加图标
  - 使用 `min-width` 替代固定 `width`，让表格自适应填充空间
  - 优化hover效果，提升交互体验

#### 6. 登录和注册页面改造
在 `art-design-pro/src/components/core/views/login/LoginLeftView.vue` 中：
- **图片替换**：
  - 将原有的SVG图标替换为医生图片（`/login.jpg`）
  - 更贴合医疗健康系统的专业形象
  - 添加图片阴影效果，提升视觉层次
- **文案更新**：
  - 主标题："专业 · 智能 · 关爱"
  - 副标题："AI赋能健康筛查，守护您的生命健康"
  - 体现系统的核心价值：专业性、智能化、人文关怀
- **视觉优化**：
  - 保留原有的淡蓝色背景和几何装饰元素
  - 图片宽度从40%调整为45%，更突出
  - 优化图片居中对齐和动画效果

## 开发规范

### 代码规范
- 遵循SOLID原则
- 函数保持简短，单一职责
- 变量命名清晰明确
- 添加必要的注释
- 函数注释包含：@brief、@param、@retval

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建/工具链相关

## 常见问题

### Q1: 前端启动失败
- 检查Node.js版本（建议16+）
- 删除 `node_modules` 和 `pnpm-lock.yaml`，重新安装
- 确保端口5173未被占用

### Q2: 后端启动失败
- 检查Python版本（建议3.8+）
- 确保MySQL和Redis服务已启动
- 检查 `.env` 配置是否正确
- 确保端口8000未被占用

### Q3: 数据库连接失败
- 检查MySQL服务是否运行
- 验证数据库名称和密码
- 确保数据库已创建
- 检查防火墙设置

### Q4: 邮件发送失败
- 确认使用的是邮箱授权码，不是登录密码
- 检查QQ邮箱是否开启SMTP服务
- 验证邮箱配置是否正确

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 许可证

本项目仅供学习和研究使用。

## 联系方式

- 邮箱：3338170081@qq.com
- 项目地址：D:\桌面\shensibei

## 致谢

感谢所有为本项目做出贡献的开发者！

---

**注意**: 本系统的AI评估结果仅供参考，不能替代专业医生的诊断。如有健康问题，请及时就医。

