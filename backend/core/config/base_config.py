# backend/core/config/base_config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

class Settings(BaseSettings):
    # اطلاعات پروژه
    PROJECT_NAME: str = "NOWEX Trading Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # دیتابیس PostgreSQL
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "nowex_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "nowex_development")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # URL دیتابیس
    @property
    def DATABASE_URL(self) -> str:
        password = self.POSTGRES_PASSWORD.replace('@', '%40')  # Encode @ symbol
        return f"postgresql://{self.POSTGRES_USER}:{password}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # امنیت - JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_key_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# ایجاد نمونه تنظیمات
settings = Settings()