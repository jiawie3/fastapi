from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# === 关键：这里定义 DATABASE_URL，给 Alembic 用 ===
DATABASE_URL = settings.database_url   # 名字要和 config.Settings 里的字段一致

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()



