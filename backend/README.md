# 肿瘤数智化筛查系统后端

## 🎯 当前功能

✅ 用户注册（邮箱验证码）  
✅ 用户登录（邮箱+密码）  
✅ JWT认证  

---

## 🚀 快速启动

### 1. 确保环境已就绪

- [x] Python 3.10+
- [x] MySQL 8.0+ (运行中)
- [x] Redis 7.0+ (运行中)
- [x] 虚拟环境已激活 `(venv)`
- [x] 依赖已安装
- [x] 数据库tumor_screening已创建
- [x] users表已创建
- [x] .env文件已配置

### 2. 启动服务

```bash
# 在backend目录，虚拟环境激活的情况下
python run.py
```

### 3. 访问API文档

浏览器打开：**http://localhost:8000/docs**

---

## 📡 API接口

### 发送验证码

```http
POST /api/v1/auth/send-code
Content-Type: application/json

{
  "email": "your@email.com"
}
```

**响应**：
```json
{
  "message": "验证码已发送到您的邮箱",
  "email": "your@email.com",
  "expire_seconds": 300
}
```

---

### 用户注册

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "your@email.com",
  "code": "123456",
  "password": "yourpassword",
  "nickname": "昵称"
}
```

**响应**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-xxx",
    "email": "your@email.com",
    "nickname": "昵称",
    "role": "user",
    "status": "active"
  }
}
```

---

### 用户登录

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "your@email.com",
  "password": "yourpassword"
}
```

**响应**：同注册接口

---

## 📁 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI主应用
│   ├── core/                # 核心模块
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库
│   │   ├── redis_client.py  # Redis
│   │   ├── security.py      # 安全（JWT、密码）
│   │   └── email.py         # 邮件服务
│   ├── models/              # SQLAlchemy模型
│   │   └── user.py
│   ├── schemas/             # Pydantic模型
│   │   └── user.py
│   ├── api/                 # API路由
│   │   └── v1/
│   │       └── auth.py      # 认证接口
│   └── utils/               # 工具函数
│       └── helpers.py
├── logs/                    # 日志目录（自动创建）
├── uploads/                 # 上传文件目录（自动创建）
├── venv/                    # 虚拟环境
├── .env                     # 环境变量配置
├── requirements.txt         # 依赖列表
├── run.py                   # 启动脚本
└── README.md                # 本文档
```

---

## 🔧 开发工具

### 查看日志

```bash
# 查看实时日志（如果配置了文件日志）
tail -f logs/app.log
```

### 数据库操作

```bash
# 查看用户表
mysql -u root -p tumor_screening -e "SELECT * FROM users;"
```

### Redis操作

```bash
# 查看所有key
redis-cli KEYS "*"

# 查看验证码
redis-cli GET "verification_code:test@qq.com"
```

---

## 📝 下一步开发

- [ ] 问卷模块
- [ ] 风险评估模块
- [ ] 报告生成模块
- [ ] 管理后台接口

---

## 📞 测试命令

```bash
# 测试Python环境
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)"
python -c "import redis; print('✅ Redis: OK')"

# 测试邮件配置
python -c "from app.core.config import settings; print('✅ 邮件配置:', settings.MAIL_USERNAME)"

# 测试数据库连接
python -c "from app.core.database import engine; print('✅ 数据库连接: OK')"
```

---

## 🎉 成功标志

服务启动后，访问 http://localhost:8000 应该看到：

```json
{
  "message": "肿瘤数智化筛查系统",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

---

**祝你测试顺利！遇到问题随时找我！** 💪

