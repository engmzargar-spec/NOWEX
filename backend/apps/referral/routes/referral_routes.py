from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from backend.core.database.base import get_db
from backend.core.security.auth import get_current_user
from backend.apps.referral.services.referral_service import ReferralService
from backend.apps.referral.schemas.referral_schemas import (
    ReferralCodeResponse, ReferralStatsResponse, 
    ReferralRewardsResponse, ReferralLeaderboardResponse
)

# 🔧 اصلاح شده: حذف prefix از اینجا
router = APIRouter(tags=["Referral"])

# 🔧 اضافه کردن endpointهای تست بدون احراز هویت
@router.get("/test/health")
def referral_health_check():
    """بررسی سلامت سیستم Referral"""
    return {
        "status": "healthy",
        "service": "Referral System",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@router.get("/test/user/{user_id}/code")
def get_referral_code_test(
    user_id: str,
    db: Session = Depends(get_db)
):
    """دریافت کد معرف (تست بدون احراز هویت)"""
    try:
        referral_service = ReferralService(db)
        code_data = referral_service.get_or_create_referral_code(UUID(user_id))
        return {
            "success": True,
            "data": code_data,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در دریافت کد معرف: {str(e)}")

@router.get("/test/user/{user_id}/stats")
def get_referral_stats_test(
    user_id: str,
    db: Session = Depends(get_db)
):
    """دریافت آمار رفرال (تست بدون احراز هویت)"""
    try:
        referral_service = ReferralService(db)
        stats = referral_service.get_referral_stats(UUID(user_id))
        return {
            "success": True,
            "data": stats,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در دریافت آمار رفرال: {str(e)}")

@router.get("/test/user/{user_id}/rewards")
def get_referral_rewards_test(
    user_id: str,
    db: Session = Depends(get_db)
):
    """دریافت پاداش‌های رفرال (تست بدون احراز هویت)"""
    try:
        referral_service = ReferralService(db)
        rewards = referral_service.get_referral_rewards(UUID(user_id))
        return {
            "success": True,
            "data": rewards,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در دریافت پاداش‌ها: {str(e)}")

@router.get("/test/leaderboard")
def get_referral_leaderboard_test(
    db: Session = Depends(get_db)
):
    """دریافت جدول برترین‌ها (تست بدون احراز هویت)"""
    try:
        referral_service = ReferralService(db)
        leaderboard = referral_service.get_referral_leaderboard()
        return {
            "success": True,
            "data": leaderboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در دریافت جدول برترین‌ها: {str(e)}")

# endpointهای اصلی با احراز هویت
@router.get("/code", response_model=ReferralCodeResponse)
def get_referral_code(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت کد معرف"""
    try:
        referral_service = ReferralService(db)
        code_data = referral_service.get_or_create_referral_code(current_user.id)
        return code_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت کد معرف")

@router.post("/apply/{referral_code}")
def apply_referral_code(
    referral_code: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """اعمال کد معرف"""
    try:
        referral_service = ReferralService(db)
        result = referral_service.apply_referral_code(current_user.id, referral_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در اعمال کد معرف")

@router.get("/stats", response_model=ReferralStatsResponse)
def get_referral_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت آمار رفرال"""
    try:
        referral_service = ReferralService(db)
        stats = referral_service.get_referral_stats(current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت آمار رفرال")

@router.get("/rewards", response_model=ReferralRewardsResponse)
def get_referral_rewards(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت تاریخچه پاداش‌ها"""
    try:
        referral_service = ReferralService(db)
        rewards = referral_service.get_referral_rewards(current_user.id)
        return rewards
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت پاداش‌ها")

@router.get("/leaderboard", response_model=ReferralLeaderboardResponse)
def get_referral_leaderboard(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت جدول برترین‌ها"""
    try:
        referral_service = ReferralService(db)
        leaderboard = referral_service.get_referral_leaderboard()
        return leaderboard
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت جدول برترین‌ها")