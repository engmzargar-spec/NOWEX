# backend/apps/admin/models/admin_user.py

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from backend.core.database.base import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # اطلاعات پایه
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)

    # نام و نام خانوادگی
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    # شماره موبایل
    phone = Column(String(20), unique=True, nullable=False)

    # سمت (جایگزین role)
    position = Column(String(100), nullable=False)

    # رمز عبور هش‌شده
    hashed_password = Column(String(255), nullable=False)

    # اطلاعات تکمیلی
    employee_id = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    # وضعیت کاربر
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime, nullable=True)

    # ورود دو مرحله‌ای
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)

    # تصویر پروفایل
    avatar_url = Column(String(500), nullable=True)

    # زمان‌ها
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    password_changed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username={self.username}, position={self.position})>"
