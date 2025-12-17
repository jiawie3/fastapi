# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Settings：配置。名字就是“配置类”的意思
    # JWT 密钥
    SECRET_KEY: str = "change_this_to_a_random_long_string"
    # 算法
    ALGORITHM: str = "HS256"
    # token 过期时间（分钟）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 天

    # 数据库 URL（现在你是 sqlite，可以先保持不动）
    database_url: str = "sqlite:///./todo.db"

    # 让它支持从 .env 里读配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

# 这个函数叫 get_settings：意思就是“拿到一个全局的配置对象”
# 以后别的模块只要 from app.config import settings 就能用
settings = Settings()
