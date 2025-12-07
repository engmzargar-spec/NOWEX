# backend/apps/kyc/models/user_profile.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Enum, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship  # ❌ کامنت کردن
from backend.core.database.base import Base
import enum
from uuid import uuid4

class KYCLevel(str, enum.Enum):
    BASIC = "level_0"
    VERIFIED = "level_1" 
    ADVANCED = "level_2"
    PREMIUM = "level_3"
    
    @classmethod
    def _missing_(cls, value):
        # پشتیبانی از هر دو حالت عددی و متنی
        if isinstance(value, str):
            # اگر مقدار عددی بود، تبدیل به فرمت level_x
            if value.isdigit():
                level_value = f"level_{value}"
                for member in cls:
                    if member.value == level_value:
                        return member
            # اگر فرمت level_x داشت
            elif value.startswith('level_'):
                for member in cls:
                    if member.value == value:
                        return member
        # اگر عدد بود
        elif isinstance(value, int):
            level_value = f"level_{value}"
            for member in cls:
                if member.value == level_value:
                    return member
        return None

class KYCStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, index=True, nullable=False)
    kyc_level = Column(String(20), default=KYCLevel.BASIC.value)  # 🔧 تغییر به String
    kyc_status = Column(String(20), default=KYCStatus.DRAFT.value)  # 🔧 تغییر به String
    
    # اطلاعات شخصی
    first_name = Column(String(100))
    last_name = Column(String(100))
    national_code = Column(String(10), unique=True)
    birth_date = Column(DateTime)
    birth_city = Column(String(100))
    gender = Column(String(10))  # male, female
    
    # اطلاعات تماس
    address = Column(Text)
    postal_code = Column(String(10))
    phone = Column(String(15))
    city = Column(String(100))
    country = Column(String(100), default="Iran")
    
    # اطلاعات بانکی
    bank_name = Column(String(100))
    sheba_number = Column(String(26))
    account_number = Column(String(20))
    card_number = Column(String(16))
    
    # وضعیت تأییدها
    email_verified = Column(Boolean, default=False)
    mobile_verified = Column(Boolean, default=False)
    bank_verified = Column(Boolean, default=False)
    identity_verified = Column(Boolean, default=False)
    address_verified = Column(Boolean, default=False)
    video_verified = Column(Boolean, default=False)
    
    # امتیاز و ریسک
    risk_score = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    
    # متادیتا
    submitted_at = Column(DateTime)
    reviewed_at = Column(DateTime)
        
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # ❌ کامنت کردن روابط - برای حل circular dependency
    # verifications = relationship("KYCVerification", back_populates="profile", foreign_keys="KYCVerification.profile_id")
    # documents = relationship("KYCDocument", back_populates="profile", foreign_keys="KYCDocument.profile_id")
    # user = relationship("User", back_populates="profile")