# backend/apps/admin/routes/admin_user_routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.core.database.base import get_db
from backend.apps.admin.services.admin_user_service import AdminUserService
from backend.apps.admin.schemas.admin_user_schema import (
    AdminUserResponse,
    AdminUserListResponse,
    AdminUserCreate,
    AdminUserUpdate,
    AdminUserPasswordUpdate,
)

router = APIRouter(prefix="/users", tags=["Admin Users"])


# ---------------------------------------------------------
# 📌 Create Admin User
# ---------------------------------------------------------
@router.post("/create", response_model=AdminUserResponse)
async def create_admin_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db)
):
    try:
        user_service = AdminUserService(db)
        new_user = user_service.create_user(payload)
        return new_user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_BAD_REQUEST,
            detail=f"خطا در ایجاد کاربر جدید: {str(e)}"
        )


# ---------------------------------------------------------
# 📌 Get Admin Users
# ---------------------------------------------------------
@router.get("/", response_model=AdminUserListResponse)
async def get_admin_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        user_service = AdminUserService(db)

        users = user_service.get_users(
            skip=skip,
            limit=limit,
            search=search,
            position=position,
            is_active=is_active
        )

        total_count = user_service.count_users()

        return AdminUserListResponse(
            users=users,
            total_count=total_count,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_BAD_REQUEST,
            detail=f"خطا در دریافت لیست کاربران: {str(e)}"
        )


# ---------------------------------------------------------
# 📌 Get Single User
# ---------------------------------------------------------
@router.get("/{user_id}", response_model=AdminUserResponse)
async def get_admin_user(user_id: str, db: Session = Depends(get_db)):
    user_service = AdminUserService(db)
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    return user


# ---------------------------------------------------------
# 📌 Update User
# ---------------------------------------------------------
@router.put("/{user_id}", response_model=AdminUserResponse)
async def update_admin_user(
    user_id: str,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db)
):
    try:
        user_service = AdminUserService(db)

        updated_user = user_service.update_user(
            user_id,
            payload.dict(exclude_unset=True)
        )

        if not updated_user:
            raise HTTPException(status_code=404, detail="کاربر یافت نشد")

        return updated_user

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"خطا در ویرایش کاربر: {str(e)}"
        )


# ---------------------------------------------------------
# 📌 Delete User
# ---------------------------------------------------------
@router.delete("/{user_id}")
async def delete_admin_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user_service = AdminUserService(db)
        success = user_service.delete_user(user_id)

        if not success:
            raise HTTPException(status_code=404, detail="کاربر یافت نشد")

        return {"detail": "کاربر با موفقیت حذف شد"}

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"خطا در حذف کاربر: {str(e)}"
        )


# ---------------------------------------------------------
# 📌 Update Password
# ---------------------------------------------------------
@router.put("/{user_id}/password")
async def update_admin_password(
    user_id: str,
    payload: AdminUserPasswordUpdate,
    db: Session = Depends(get_db)
):
    try:
        user_service = AdminUserService(db)
        user_service.update_password(user_id, payload.new_password)
        return {"detail": "رمز عبور با موفقیت تغییر کرد"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"خطا در تغییر رمز عبور: {str(e)}"
        )


# ---------------------------------------------------------
# 📌 Activate User
# ---------------------------------------------------------
@router.put("/{user_id}/activate")
async def activate_admin_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user_service = AdminUserService(db)
        user_service.activate_user(user_id)
        return {"detail": "کاربر با موفقیت فعال شد"}

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"خطا در فعال‌سازی کاربر: {str(e)}"
        )
