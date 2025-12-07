from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum
from uuid import UUID

class KYCLevel(str, Enum):
    BRONZE = "level_0"  # ✅ تطابق با سیستم موجود
    SILVER = "level_1" 
    GOLD = "level_2"

class KYCStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ProfileCreate(BaseModel):
    first_name: str
    last_name: str
    national_code: str
    birth_date: date
    birth_city: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    phone: str
    city: Optional[str] = None
    country: Optional[str] = "Iran"
    bank_name: Optional[str] = None
    sheba_number: Optional[str] = None
    account_number: Optional[str] = None
    kyc_level: KYCLevel

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    national_code: Optional[str] = None
    birth_date: Optional[date] = None
    birth_city: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    bank_name: Optional[str] = None
    sheba_number: Optional[str] = None
    account_number: Optional[str] = None
    kyc_level: Optional[KYCLevel] = None

class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    kyc_level: KYCLevel
    kyc_status: KYCStatus
    first_name: Optional[str]
    last_name: Optional[str]
    national_code: Optional[str]
    birth_date: Optional[date]
    address: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    country: Optional[str]
    bank_name: Optional[str]
    sheba_number: Optional[str]
    email_verified: bool
    mobile_verified: bool
    bank_verified: bool
    identity_verified: bool
    address_verified: bool
    completion_percentage: float
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VerificationCreate(BaseModel):
    verification_type: str
    method: str
    confidence_score: Optional[float] = None
    auto_verification_result: Optional[Dict[str, Any]] = None

class VerificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    verification_type: str
    status: str
    method: str
    confidence_score: Optional[float]
    submitted_at: datetime
    verified_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentUpload(BaseModel):
    document_type: str
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    file_hash: str

class DocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    document_type: str
    file_name: str
    file_path: str
    status: str
    uploaded_at: datetime
    verified_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class KYCStatusResponse(BaseModel):
    kyc_level: KYCLevel
    kyc_status: KYCStatus
    completion_percentage: float
    verified_fields: Dict[str, bool]
    submitted_at: Optional[datetime]
    reviewed_at: Optional[datetime]

class KYCApproveRequest(BaseModel):
    user_id: UUID
    kyc_level: KYCLevel

class KYCRejectRequest(BaseModel):
    user_id: UUID
    reason: str

class KYCStatsResponse(BaseModel):
    total_profiles: int
    pending_reviews: int
    approved_profiles: int
    approval_rate: float