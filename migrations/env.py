import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# 读取 alembic.ini 配置
config = context.config

# 如果有 logging 配置，加载一下
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# === 把项目根目录加到 sys.path，保证能 import app.xxx ===
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
sys.path.append(PROJECT_ROOT)

# === 从你的项目里导入 Base 和 DATABASE_URL ===
from app.database import Base, DATABASE_URL  # 确保 database.py 里有这两个
from app import models  # 导入 models，确保所有模型被注册到 Base 上

# 关键：提供给 Alembic 的 metadata 对象
target_metadata = Base.metadata

# 告诉 Alembic 数据库 URL
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """
    run_migrations_offline:
    函数名含义：以“离线”方式运行迁移（不真正连数据库，只生成 SQL）
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,  # 关键：把 metadata 传进去
        literal_binds=True,
        compare_type=True,  # 字段类型变化也检测
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    run_migrations_online:
    含义：以“在线”方式运行迁移（真正连数据库，直接执行变更）
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,  # 关键：同样传 metadata
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Alembic 的入口，根据当前模式（offline / online）调用对应函数
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
