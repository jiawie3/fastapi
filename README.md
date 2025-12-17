# FastAPI Todo 应用

这是一个基于 **FastAPI** 开发的简单任务管理（Todo）应用，包含：

- 任务的增删改查（CRUD）
- 条件过滤 / 分页
- 用户注册 / 登录
- JWT 鉴权 & 多用户任务隔离
- Pydantic 参数校验 & 统一异常处理
- Logging 日志
- Alembic 数据库迁移
- Docker 镜像打包 & 运行
- pytest 自动化测试


---

## 技术栈

- **框架**：FastAPI
- **语言**：Python 3.10
- **ORM**：SQLAlchemy
- **数据校验**：Pydantic v2
- **数据库**：SQLite（开发环境）
- **迁移工具**：Alembic
- **鉴权**：JWT（`python-jose`）、OAuth2 Password Flow
- **测试**：pytest、FastAPI TestClient
- **日志**：标准库 `logging`
- **容器化**：Docker

---

## 目录结构（简要）

```text
fastapi/
├─ app/
│  ├─ main.py           # FastAPI 入口，路由、依赖、异常处理等
│  ├─ models.py         # SQLAlchemy ORM 模型（User / Task）
│  ├─ schemas.py        # Pydantic 模型（请求 / 响应）
│  ├─ database.py       # 数据库引擎 & SessionLocal
│  ├─ config.py         # 配置（Settings：数据库 URL、日志级别、JWT 配置等）
│  └─ __init__.py
├─ migrations/          # Alembic 迁移脚本目录
├─ tests/
│  └─ test_tasks.py     # 任务相关接口的自动化测试
├─ Dockerfile
├─ alembic.ini
└─ README.md

### 本地运行（非docker）
git clone 
cd fastapi

### 创建并激活虚拟环境
conda create -n fastapi python=3.10
conda activate fastapi

### 安装依赖
pip install -r requirements.txt

### 初始化数据库（Alembic）
alembic upgrade head

### 启动服务
uvicorn app.main:app --reload
接口文档：http://127.0.0.1:8000/docs

### Docker 运行
1.构建镜像
docker build -t fastapi-todo .
2.初始化数据库
docker run --rm -it fastapi-todo alembic upgrade head
3.启动服务
docker run --rm -p 8000:8000 fastapi-todo

