# 1. 选一个 Python 基础镜像
FROM python:3.10-slim

# 2. 设置工作目录（后面所有路径都以这里为根）
WORKDIR /app

# 3. 只先复制依赖文件，这样依赖安装有缓存
COPY requirements.txt /app/requirements.txt

# 4. 安装依赖
RUN pip install --no-cache-dir -r /app/requirements.txt

# 5. 再把项目代码整个复制进去
COPY . /app

# 6. 设置环境变量（可选，看你 config.py 怎么写的）
# 例如：指定生产环境、数据库地址等（现在可以先不配）
# ENV ENVIRONMENT=production

# 7. 暴露端口（容器内部端口）
EXPOSE 8000

# 8. 启动命令：用 uvicorn 跑 FastAPI
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
