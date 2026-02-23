# backend/apps/admin/schemas/admin_auth_schema.py
from pydantic import BaseModel
from typing import Optional


# ---------------------------------------------------------
# 📌 Login Request
# ---------------------------------------------------------
class AdminLoginRequest(BaseModel):
    username: str
    password: str


# ---------------------------------------------------------
# 📌 Login Response (Token)
# ---------------------------------------------------------
class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_id: str
    username: str
    position: str   # ← جایگزین role


# ---------------------------------------------------------
# 📌 User Info Response (for /me)
# ---------------------------------------------------------
class AdminUserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    position: str
    is_active: bool
    last_login: Optional[str]
    created_at: str


# ---------------------------------------------------------
# 📌 Create Admin (اگر هنوز استفاده می‌شود)
# ---------------------------------------------------------
class AdminCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    position: str
