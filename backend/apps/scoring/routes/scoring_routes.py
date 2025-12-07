from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from backend.core.database.base import get_db
from backend.core.security.auth import get_current_user
from backend.apps.scoring.services.scoring_engine import ScoringEngine
from backend.apps.scoring.schemas.scoring_schemas import (
    UserScoreResponse, ScoreBreakdownResponse, ScoreHistoryResponse
)
from backend.core.exceptions import ScoringError, NotFoundError

# 🔧 اصلاح شده: حذف prefix از اینجا
router = APIRouter(tags=["Scoring"])

# 🔧 اضافه کردن endpointهای تست بدون احراز هویت
@router.get("/test/user/{user_id}/score")
def get_user_score_test(
    user_id: str,
    db: Session = Depends(get_db)
):
    """دریافت امتیاز کاربر (تست بدون احراز هویت)"""
    try:
        scoring_engine = ScoringEngine(db)
        score_data = scoring_engine.get_user_score_data(UUID(user_id))  # 🔧 حذف await
        return {
            "success": True,
            "data": score_data,
            "user_id": user_id
        }
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User score not found")
    except Exception as e:
        raise ScoringError(f"Failed to get user score: {str(e)}")

@router.get("/test/user/{user_id}/breakdown")
def get_score_breakdown_test(
    user_id: str,
    db: Session = Depends(get_db)
):
    """دریافت جزئیات امتیاز (تست بدون احراز هویت)"""
    try:
        scoring_engine = ScoringEngine(db)
        breakdown = scoring_engine.get_score_breakdown(UUID(user_id))  # 🔧 حذف await
        return {
            "success": True,
            "data": breakdown,
            "user_id": user_id
        }
    except Exception as e:
        raise ScoringError(f"Failed to get score breakdown: {str(e)}")

@router.get("/test/health")
def scoring_health_check():
    """بررسی سلامت سیستم Scoring"""
    return {
        "status": "healthy",
        "service": "Scoring System",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# endpointهای اصلی با احراز هویت (بدون تغییر)
@router.get("/score", response_model=UserScoreResponse)
def get_user_score(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت امتیاز کاربر"""
    try:
        scoring_engine = ScoringEngine(db)
        score_data = scoring_engine.get_user_score_data(current_user.id)  # 🔧 حذف await
        return score_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت امتیاز")

@router.get("/score/breakdown", response_model=ScoreBreakdownResponse)
def get_score_breakdown(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت جزئیات امتیاز"""
    try:
        scoring_engine = ScoringEngine(db)
        breakdown = scoring_engine.get_score_breakdown(current_user.id)  # 🔧 حذف await
        return breakdown
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت جزئیات امتیاز")

@router.get("/benefits")
def get_user_benefits(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت مزایای سطح کاربری"""
    try:
        scoring_engine = ScoringEngine(db)
        benefits = scoring_engine.get_user_benefits(current_user.id)  # 🔧 حذف await
        return benefits
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت مزایا")

@router.get("/history")
def get_score_history(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت تاریخچه امتیاز"""
    try:
        scoring_engine = ScoringEngine(db)
        history = scoring_engine.get_score_history(current_user.id)  # 🔧 حذف await
        return {
            "success": True,
            "data": history,
            "count": len(history) if history else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="خطا در دریافت تاریخچه امتیاز")