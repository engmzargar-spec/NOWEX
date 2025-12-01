from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Enum, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database.base import Base
import enum
from uuid import uuid4

# Import مدل‌های اصلی از فایل‌های مربوطه
from .user_profile import UserProfile, KYCLevel, KYCStatus
from .kyc_verification import KYCVerification, KYCDocument, VerificationType, VerificationStatus

# این فایل حالا فقط برای import و export مدل‌ها استفاده می‌شه
# و خودش مدل جدیدی تعریف نمی‌کنه

__all__ = [
    "UserProfile", 
    "KYCLevel", 
    "KYCStatus",
    "KYCVerification", 
    "KYCDocument",
    "VerificationType",
    "VerificationStatus"
]