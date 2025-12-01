from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey, Enum, Float, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship  # ❌ کامنت کردن
from backend.core.database.base import Base
import enum
from uuid import uuid4

class VerificationType(enum.Enum):
    MOBILE = "mobile"
    EMAIL = "email" 
    IDENTITY = "identity"
    BANK = "bank"
    ADDRESS = "address"
    VIDEO = "video"

class VerificationStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class KYCVerification(Base):
    __tablename__ = "kyc_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), index=True, nullable=False)
    
    # نوع تأیید
    verification_type = Column(Enum(VerificationType), nullable=False)
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    
    # اطلاعات تأیید
    submitted_data = Column(JSON)
    verification_result = Column(JSON)
    confidence_score = Column(Float, default=0.0)
    auto_verified = Column(Boolean, default=False)
    
    # مستندات
    document_ids = Column(JSON)  # لیست ID مدارک مرتبط
    
    # زمان‌بندی
    submitted_at = Column(DateTime, default=func.now())
    reviewed_at = Column(DateTime)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    expires_at = Column(DateTime)
    
    # متادیتا
    attempt_count = Column(JSON, default=dict)  # تعداد تلاش‌های هر نوع
    verification_method = Column(String(50))  # manual, auto, third_party
    third_party_reference = Column(String(100))  # reference ID از سرویس خارجی
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # ❌ کامنت کردن تمام روابط - برای حل circular dependency
    # user = relationship("User", back_populates="kyc_verifications")
    # profile = relationship("UserProfile", back_populates="verifications")
    # documents = relationship("KYCDocument", back_populates="verification")

class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), index=True, nullable=False)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("kyc_verifications.id"), index=True, nullable=False)
    
    # اطلاعات سند
    document_type = Column(String(50), nullable=False)  # national_card, passport, driver_license, etc.
    document_number = Column(String(50))
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # وضعیت سند
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    rejection_reason = Column(Text)
    
    # متادیتا
    uploaded_at = Column(DateTime, default=func.now())
    verified_at = Column(DateTime)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    
    # امنیت
    hash_value = Column(String(64))  # SHA-256 hash برای یکتایی
    is_encrypted = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # ❌ کامنت کردن تمام روابط - برای حل circular dependency
    # user = relationship("User", back_populates="kyc_documents")
    # verification = relationship("KYCVerification", back_populates="documents")
    # profile = relationship("UserProfile", back_populates="documents")