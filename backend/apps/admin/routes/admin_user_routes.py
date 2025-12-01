# backend/apps/admin/routes/admin_user_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database.base import get_db
from apps.admin.services.admin_user_service import AdminUserService
from apps.admin.schemas.admin_user_schema import (
    AdminUserResponse,
    AdminUserListResponse,
    AdminUserCreate,
    AdminUserUpdate,
    AdminRole
)

router = APIRouter()

@router.get("/users", response_model=AdminUserListResponse)
async def get_admin_users(
    skip: int = Query(0, ge=0, description="تعداد رکوردهای رد شده"),
    limit: int = Query(100, ge=1, le=1000, description="تعداد رکوردهای بازگشتی"),
    search: Optional[str] = Query(None, description="جستجو در نام کاربری، ایمیل و نام کامل"),
    role: Optional[AdminRole] = Query(None, description="فیلتر بر اساس نقش"),
    is_active: Optional[bool] = Query(None, description="فیلتر بر اساس وضعیت فعال"),
    db: Session = Depends(get_db)
):
    """
    دریافت لیست کاربران ادمین با قابلیت فیلتر و صفحه‌بندی
    """
    try:
        user_service = AdminUserService(db)
        
        # دریافت کاربران
        users = user_service.get_users(
            skip=skip,
            limit=limit,
            search=search,
            role=role,
            is_active=is_active
        )
        
        # تعداد کل کاربران
        total_count = user_service.count_users()
        
        return AdminUserListResponse(
            users=users,
            total_count=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در دریافت لیست کاربران: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_admin_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    دریافت اطلاعات کاربر ادمین خاص
    """
    user_service = AdminUserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر مورد نظر یافت نشد"
        )
    
    return user

@router.post("/users", response_model=AdminUserResponse)
async def create_admin_user(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db)
):
    """
    ایجاد کاربر ادمین جدید
    """
    try:
        user_service = AdminUserService(db)
        user = user_service.create_user(user_data)
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ایجاد کاربر: {str(e)}"
        )

@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_admin_user(
    user_id: str,
    user_data: AdminUserUpdate,
    db: Session = Depends(get_db)
):
    """
    بروزرسانی اطلاعات کاربر ادمین
    """
    try:
        user_service = AdminUserService(db)
        user = user_service.update_user(user_id, user_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="کاربر مورد نظر یافت نشد"
            )
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در بروزرسانی کاربر: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_admin_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    حذف کاربر ادمین
    """
    user_service = AdminUserService(db)
    success = user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر مورد نظر یافت نشد"
        )
    
    return {"message": "کاربر با موفقیت حذف شد"}