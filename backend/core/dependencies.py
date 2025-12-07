from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from backend.core.database.base import get_db  # تغییر به absolute import

security = HTTPBearer()

def get_redis():
    """Dependency for Redis client"""
    from backend.core.redis_mock import get_redis_simple  # تغییر به absolute import
    return get_redis_simple()