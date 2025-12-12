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
