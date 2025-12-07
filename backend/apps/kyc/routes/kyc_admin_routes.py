from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.core.database.base import get_db
from backend.core.security.auth import get_current_admin_user
from backend.apps.kyc.services.kyc_service import KYCService
from backend.apps.kyc.schemas.kyc_schemas import (
    ProfileResponse, KYCStatsResponse, KYCApproveRequest, KYCRejectRequest
)

# 🔧 اصلاح شده: حذف prefix از اینجا
router = APIRouter(tags=["Admin KYC"])

@router.get("/profiles", response_model=List[ProfileResponse])
async def get_all_profiles(
    status: Optional[str] = Query(None, description="فیلتر بر اساس وضعیت"),
    level: Optional[str] = Query(None, description="فیلتر بر اساس سطح"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """دریافت لیست تمام پروفایل‌ها (ادمین)"""
    try:
        kyc_service = KYCService(db)
        
        from backend.apps.kyc.models.kyc_models import UserProfile
        query = db.query(UserProfile)
        
        if status:
            query = query.filter(UserProfile.kyc_status == status)
        if level:
            query = query.filter(UserProfile.kyc_level == level)
        
        profiles = query.offset(skip).limit(limit).all()
        return profiles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت لیست پروفایل‌ها")

@router.get("/pending", response_model=List[ProfileResponse])
async def get_pending_kyc(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """دریافت درخواست‌های KYC در انتظار بررسی"""
    try:
        from backend.apps.kyc.models.kyc_models import UserProfile, KYCStatus
        profiles = db.query(UserProfile).filter(
            UserProfile.kyc_status == KYCStatus.SUBMITTED
        ).offset(skip).limit(limit).all()
        
        return profiles
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت درخواست‌های pending")

@router.post("/approve")
async def approve_kyc(
    approve_data: KYCApproveRequest,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """تأیید درخواست KYC"""
    try:
        kyc_service = KYCService(db)
        profile = await kyc_service.approve_kyc(
            approve_data.user_id, 
            current_admin["id"], 
            approve_data.kyc_level
        )
        
        return {
            "message": "درخواست KYC با موفقیت تأیید شد",
            "profile": profile
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در تأیید KYC")

@router.post("/reject")
async def reject_kyc(
    reject_data: KYCRejectRequest,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """رد درخواست KYC"""
    try:
        kyc_service = KYCService(db)
        profile = await kyc_service.reject_kyc(
            reject_data.user_id, 
            current_admin["id"], 
            reject_data.reason
        )
        
        return {
            "message": "درخواست KYC رد شد",
            "profile": profile
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در رد KYC")

@router.get("/stats", response_model=KYCStatsResponse)
async def get_kyc_stats(
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """دریافت آمار KYC"""
    try:
        kyc_service = KYCService(db)
        stats = await kyc_service.get_kyc_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت آمار KYC")