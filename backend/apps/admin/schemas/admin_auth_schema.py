# backend/apps/admin/schemas/admin_auth_schema.py
from pydantic import BaseModel
from typing import Optional

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_id: str
    username: str
    role: str

class AdminUserResponse(BaseModel):
    id: str
    username: str
    email: str  # تغییر از EmailStr به str
    full_name: str
    role: str
    is_active: bool
    last_login: Optional[str]
    created_at: str

class AdminCreateRequest(BaseModel):
    username: str
    email: str  # تغییر از EmailStr به str
    password: str
    full_name: str
    role: str