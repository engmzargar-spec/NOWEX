from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from backend.core.database.base import get_db  # ✅ اصلاح شد
from backend.apps.auth.schemas.user_schema import UserCreate, UserResponse, UserLogin, Token  # ✅ اصلاح شد
from backend.apps.auth.services.user_service import user_service  # ✅ اصلاح شد

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """ثبت‌نام کاربر جدید"""
    try:
        user = user_service.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """لاگین کاربر و دریافت توکن"""
    user = user_service.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # ایجاد توکن دسترسی
    from backend.core.security.jwt_handler import create_access_token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "email": user.email
    }

# endpointهای ساده برای تست
@router.get("/test")
def test_endpoint():
    return {"message": "User routes are working!"}