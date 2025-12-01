from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from backend.core.database.base import get_db
from backend.core.security.auth import get_current_user
from backend.apps.kyc.services.kyc_service import KYCService
from backend.apps.kyc.services.kyc_state_service import KYCStateService
from backend.apps.kyc.schemas.kyc_schemas import (
    ProfileCreate, ProfileUpdate, ProfileResponse, 
    VerificationCreate, VerificationResponse,
    DocumentUpload, DocumentResponse,
    KYCStatusResponse
)

# 🔧 اصلاح شده: حذف prefix از اینجا
router = APIRouter(tags=["KYC"])
logger = logging.getLogger(__name__)

@router.post("/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ایجاد پروفایل کاربری"""
    try:
        kyc_service = KYCService(db)
        profile = await kyc_service.create_user_profile(current_user.id, profile_data)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در ایجاد پروفایل")

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت پروفایل کاربر"""
    try:
        kyc_service = KYCService(db)
        profile = await kyc_service.get_user_profile(current_user.id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="پروفایل یافت نشد")
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در دریافت پروفایل")

@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """بروزرسانی پروفایل کاربر"""
    try:
        kyc_service = KYCService(db)
        profile = await kyc_service.update_user_profile(current_user.id, profile_data)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در بروزرسانی پروفایل")

@router.post("/submit", response_model=ProfileResponse)
async def submit_kyc(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ارسال درخواست KYC برای بررسی"""
    try:
        kyc_service = KYCService(db)
        profile = await kyc_service.submit_kyc_application(current_user.id)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting KYC: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در ارسال درخواست KYC")

@router.post("/verify", response_model=VerificationResponse)
async def verify_identity(
    verification_data: VerificationCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ثبت تأییدیه هویت"""
    try:
        kyc_service = KYCService(db)
        verification = await kyc_service.verify_user_identity(
            current_user.id, verification_data
        )
        return verification
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error verifying identity: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در ثبت تأییدیه")

@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    document_data: DocumentUpload,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """آپلود سند هویتی"""
    try:
        kyc_service = KYCService(db)
        document = await kyc_service.upload_document(current_user.id, document_data)
        return document
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در آپلود سند")

@router.get("/status", response_model=KYCStatusResponse)
async def get_kyc_status(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت وضعیت KYC"""
    try:
        kyc_service = KYCService(db)
        profile = await kyc_service.get_user_profile(current_user.id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="پروفایل یافت نشد")
        
        return {
            "kyc_level": profile.kyc_level,
            "kyc_status": profile.kyc_status,
            "completion_percentage": profile.completion_percentage,
            "verified_fields": {
                "email": profile.email_verified,
                "mobile": profile.mobile_verified,
                "bank": profile.bank_verified,
                "identity": profile.identity_verified,
                "address": profile.address_verified
            },
            "submitted_at": profile.submitted_at,
            "reviewed_at": profile.reviewed_at
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting KYC status: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در دریافت وضعیت KYC")

@router.get("/state/transitions")
async def get_available_transitions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت انتقال‌های ممکن برای وضعیت فعلی"""
    try:
        kyc_service = KYCService(db)
        profile = await kyc_service.get_user_profile(current_user.id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="پروفایل یافت نشد")
        
        state_service = KYCStateService(db)
        transitions = await state_service.get_available_transitions(profile.kyc_status.value)
        
        return {
            "current_state": profile.kyc_status.value,
            "available_transitions": transitions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transitions: {str(e)}")
        raise HTTPException(status_code=500, detail="خطا در دریافت انتقال‌های ممکن")