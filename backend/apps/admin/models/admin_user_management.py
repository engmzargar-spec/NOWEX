from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.core.database.base import Base  # تغییر به absolute import

class UserManagementLog(Base):
    __tablename__ = "admin_user_management_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    admin_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # VERIFY_KYC, SUSPEND, ACTIVATE, etc.
    previous_status = Column(String(50))
    new_status = Column(String(50))
    reason = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserKYCData(Base):
    __tablename__ = "user_kyc_data"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    status = Column(String(20), nullable=False, default="PENDING")  # PENDING, VERIFIED, REJECTED
    document_type = Column(String(50))  # NATIONAL_CARD, PASSPORT, DRIVER_LICENSE
    document_number = Column(String(100))
    document_front_url = Column(Text)
    document_back_url = Column(Text)
    selfie_url = Column(Text)
    verification_date = Column(DateTime(timezone=True))
    verified_by_admin_id = Column(UUID(as_uuid=True))
    rejection_reason = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())