# backend/apps/admin/models/admin_user.py
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text
from datetime import datetime
from backend.core.database.base import Base  # تغییر به absolute import

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # ✅ اضافه کردن autoincrement
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    
    role = Column(String(50), nullable=False)
    
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AdminUser(id={self.id}, username={self.username}, role={self.role})>"