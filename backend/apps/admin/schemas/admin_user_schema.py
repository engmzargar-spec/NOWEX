# backend/apps/admin/schemas/admin_user_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    SUPPORT_AGENT = "support_agent" 
    COMPLIANCE_OFFICER = "compliance_officer"
    RISK_MANAGER = "risk_manager"
    FINANCIAL_OPERATOR = "financial_operator"

class AdminUserResponse(BaseModel):
    id: int  # 🔥 تغییر از str به int
    username: str
    email: EmailStr
    full_name: str
    role: AdminRole
    is_active: bool
    last_login: Optional[datetime]
    login_attempts: int
    is_locked: bool
    two_factor_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class AdminUserListResponse(BaseModel):
    users: List[AdminUserResponse]
    total_count: int
    skip: int
    limit: int

class AdminUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: AdminRole = AdminRole.SUPPORT_AGENT

class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None

class AdminUserSearchParams(BaseModel):
    skip: int = 0
    limit: int = 100
    search: Optional[str] = None
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None