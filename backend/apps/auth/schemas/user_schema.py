# backend/apps/auth/schemas/user_schema.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime, date
from uuid import UUID

# Base Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Schema برای ایجاد کاربر
class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v

# Schema برای آپدیت کاربر
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None

# Schema برای پاسخ API
class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    is_suspended: bool
    kyc_status: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema برای لاگین
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema برای توکن - ✅ اصلاح شده
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str  # ✅ فقط ID رو برگردون
    email: str    # ✅ ایمیل رو هم برگردون

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None