# backend/apps/auth/models/user.py - نسخه ساده و تستی
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4
from backend.core.database.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # وضعیت کاربر
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)
    
    # اطلاعات KYC
    kyc_status = Column(String(50), default="pending")
    kyc_verified_at = Column(DateTime, nullable=True)
    
    # تایم‌ستمپ‌ها
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    # ❌ کامنت کردن تمام روابط - برای حل مشکل circular dependency
    # profile = relationship("UserProfile", back_populates="user", uselist=False)
    # kyc_verifications = relationship("KYCVerification", back_populates="user")
    # kyc_documents = relationship("KYCDocument", back_populates="user")