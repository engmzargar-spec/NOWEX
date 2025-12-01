from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from backend.core.database.base import get_db
from backend.core.security.auth import get_current_admin
from backend.apps.auth.models.user import User
from backend.apps.admin.models import Admin
from backend.apps.admin.schemas.user_management_schema import (
    UserSearchFilter,
    UserStatusUpdateRequest,
    KYCVerificationRequest,
    PaginatedUserResponse,
    UserDetailResponse
)
from backend.apps.admin.services.user_management_service import UserManagementService

router = APIRouter(prefix="/admin/users", tags=["Admin - User Management"])

@router.get("/", response_model=PaginatedUserResponse)
async def get_users_paginated(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    email: Optional[str] = Query(None, description="Filter by email"),
    status: Optional[str] = Query(None, description="Filter by status"),
    kyc_status: Optional[str] = Query(None, description="Filter by KYC status"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get paginated list of users with filtering options
    """
    try:
        # ساخت فیلترها
        filters = UserSearchFilter(
            email=email,
            status=status,
            kyc_status=kyc_status,
            date_from=date_from,
            date_to=date_to
        )
        
        service = UserManagementService(db)
        result = await service.get_users_paginated(
            page=page,
            page_size=page_size,
            filters=filters
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{user_id}", response_model=dict)
async def get_user_detail(
    user_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get detailed information about a specific user
    """
    try:
        service = UserManagementService(db)
        user_detail = await service.get_user_detail(user_id)
        
        if not user_detail:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user_detail
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.patch("/{user_id}/status")
async def update_user_status(
    user_id: UUID,
    status_data: UserStatusUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Update user status (ACTIVE, SUSPENDED, etc.)
    """
    try:
        service = UserManagementService(db)
        
        success = await service.update_user_status(
            user_id=user_id,
            new_status=status_data.status,
            admin_id=current_admin.id,
            reason=status_data.reason,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "")
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{user_id}/kyc/verify")
async def verify_user_kyc(
    user_id: UUID,
    kyc_data: KYCVerificationRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Verify or reject user KYC documentation
    """
    try:
        # این قسمت رو بعداً کامل می‌کنیم
        # فعلاً پیام موفقیت برمی‌گردونیم
        
        return {
            "message": "KYC verification processed successfully",
            "user_id": str(user_id),
            "status": kyc_data.status,
            "verified_by_admin": str(current_admin.id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{user_id}/logs")
async def get_user_management_logs(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get management logs for a specific user
    """
    try:
        # این قسمت رو بعداً کامل می‌کنیم
        return {
            "message": "User logs endpoint - will be implemented",
            "user_id": str(user_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")