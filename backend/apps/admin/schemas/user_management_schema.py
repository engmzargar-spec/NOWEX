from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    REJECTED = "REJECTED"

class KYCStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class UserListResponse(BaseModel):
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    status: UserStatus
    kyc_status: KYCStatus
    created_at: datetime
    last_login: Optional[datetime]

class UserDetailResponse(BaseModel):
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    status: UserStatus
    kyc_status: KYCStatus
    created_at: datetime
    last_login: Optional[datetime]
    login_count: int
    email_verified: bool
    phone_verified: bool

class KYCVerificationRequest(BaseModel):
    status: KYCStatus
    rejection_reason: Optional[str] = Field(None, max_length=500)

class UserStatusUpdateRequest(BaseModel):
    status: UserStatus
    reason: str = Field(..., max_length=500)

class UserSearchFilter(BaseModel):
    email: Optional[str] = None
    status: Optional[UserStatus] = None
    kyc_status: Optional[KYCStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class PaginatedUserResponse(BaseModel):
    users: List[UserListResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class UserManagementLogResponse(BaseModel):
    id: UUID
    admin_id: UUID
    user_id: UUID
    action_type: str
    previous_status: Optional[str]
    new_status: Optional[str]
    reason: Optional[str]
    created_at: datetime