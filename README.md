# 多用户任务管理系统（FastAPI）

## 项目目标

在现有单用户 Todo 项目的基础上，扩展为 **多用户任务管理系统**：

- 支持用户注册 / 登录
- 使用 JWT 做身份认证
- 每个用户只能管理自己的任务
- 支持任务的创建 / 查看 / 更新 / 删除
- 支持按完成状态、关键字、优先级等过滤，附带分页
- 提供用户维度的任务统计接口

## 技术栈

- 后端框架：FastAPI
- 数据库：SQLite + SQLAlchemy
- 数据校验：Pydantic
- 身份认证：JWT（基于 python-jose / passlib[bcrypt]）
- 测试：pytest + FastAPI TestClient

## 数据模型（初步设计）

### User（用户）

- `id`: str (UUID)
- `username`: str（唯一）
- `email`: str（可选，唯一）
- `hashed_password`: str
- `created_at`: datetime

### Task（任务）

- `id`: str (UUID)
- `user_id`: str（外键，关联 User）
- `title`: str
- `description`: str
- `is_done`: bool
- `priority`: int
- `created_at`: datetime

## 接口设计（草稿）

### 认证相关

- `POST /auth/register`
  - 请求：username, password, (email)
  - 返回：用户基本信息
- `POST /auth/login`
  - 请求：username, password
  - 返回：access_token（JWT），token_type

### 任务相关（需要登录）

所有下面接口都要求携带 `Authorization: Bearer <token>`：

- `GET /tasks`：获取当前用户的任务列表（支持 done、keyword、skip、limit）
- `POST /tasks`：创建任务
- `GET /tasks/{task_id}`：获取当前用户的一条任务
- `PUT /tasks/{task_id}`：更新任务
- `DELETE /tasks/{task_id}`：删除任务
- `GET /tasks/stats`：获取当前用户的任务统计数据


### 注册用户
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "email": "demo@example.com",
    "password": "demo123"
  }'

### 登录获得token
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo123"
### 返回
{
  "access_token": "xxxx.yyyy.zzzz",
  "token_type": "bearer"
}


### 携带token调用受保护的任务接口
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Authorization: Bearer xxxx.yyyy.zzzz" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "first task",
    "description": "created by demo",
    "is_done": false,
    "priority": 3
  }'

### SwaggerUI 中如何使用token
打开 http://127.0.0.1:8000/docs

点右上角 Authorize

在输入框里填：Bearer 空格 + 你的 access_token

例如：Bearer eyJhbGciOiJIUzI1NiIs...

点 Authorize → Close
然后再去调 /tasks 相关接口，就是以该用户身份访问。

### 数据库迁移（Alembic）

生成迁移：
```bash
alembic revision --autogenerate -m "描述本次改动"
