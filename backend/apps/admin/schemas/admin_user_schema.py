from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ---------------------------------------------------------
# 📌 مدل خروجی اطلاعات کاربر
# ---------------------------------------------------------
class AdminUserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    position: str
    is_active: bool
    last_login: Optional[datetime]
    login_attempts: int
    is_locked: bool
    two_factor_enabled: bool
    avatar_url: Optional[str]
    phone: Optional[str]
    employee_id: Optional[str]
    address: Optional[str]
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------
# 📌 مدل خروجی لیست کاربران
# ---------------------------------------------------------
class AdminUserListResponse(BaseModel):
    users: List[AdminUserResponse]
    total_count: int
    skip: int
    limit: int


# ---------------------------------------------------------
# 📌 مدل ورودی ایجاد کاربر جدید
# ---------------------------------------------------------
class AdminUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str
    employee_id: Optional[str] = None
    position: str
    address: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    two_factor_enabled: bool = False
    avatar_url: Optional[str] = None


# ---------------------------------------------------------
# 📌 مدل ورودی ویرایش کاربر
# ---------------------------------------------------------
class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    employee_id: Optional[str] = None
    position: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None
    avatar_url: Optional[str] = None


# ---------------------------------------------------------
# 📌 مدل تغییر رمز عبور
# ---------------------------------------------------------
class AdminUserPasswordUpdate(BaseModel):
    new_password: str


# ---------------------------------------------------------
# 📌 مدل پارامترهای جستجو
# ---------------------------------------------------------
class AdminUserSearchParams(BaseModel):
    skip: int = 0
    limit: int = 100
    search: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None
