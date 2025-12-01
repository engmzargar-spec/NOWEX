from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from uuid import UUID
from backend.apps.kyc.models.kyc_models import (
    UserProfile, KYCVerification, KYCDocument, 
    KYCLevel, KYCStatus
)
from backend.apps.kyc.models.kyc_state_machine import KYCStateMachine
from backend.apps.kyc.schemas.kyc_schemas import (
    ProfileCreate, ProfileUpdate, VerificationCreate, DocumentUpload
)
from backend.core.security.password import get_password_hash
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class KYCService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user_profile(self, user_id: UUID, profile_data: ProfileCreate) -> UserProfile:
        """ایجاد پروفایل کاربری جدید"""
        try:
            # بررسی وجود پروفایل
            existing_profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if existing_profile:
                raise ValueError("پروفایل کاربر از قبل وجود دارد")
            
            # ایجاد پروفایل جدید
            profile = UserProfile(
                user_id=user_id,
                first_name=profile_data.first_name,
                last_name=profile_data.last_name,
                national_code=profile_data.national_code,
                birth_date=profile_data.birth_date,
                birth_city=profile_data.birth_city,
                gender=profile_data.gender,
                address=profile_data.address,
                postal_code=profile_data.postal_code,
                phone=profile_data.phone,
                city=profile_data.city,
                country=profile_data.country,
                completion_percentage=10.0  # پس از تکمیل اطلاعات اولیه
            )
            
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"پروفایل کاربر {user_id} ایجاد شد")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در ایجاد پروفایل کاربر {user_id}: {str(e)}")
            raise
    
    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """دریافت پروفایل کاربر"""
        return self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
    
    async def update_user_profile(self, user_id: UUID, update_data: ProfileUpdate) -> UserProfile:
        """بروزرسانی پروفایل کاربر"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                raise ValueError("پروفایل کاربر یافت نشد")
            
            # بروزرسانی فیلدها
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(profile, field, value)
            
            # محاسبه درصد تکمیل
            profile.completion_percentage = self._calculate_completion_percentage(profile)
            profile.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"پروفایل کاربر {user_id} بروزرسانی شد")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در بروزرسانی پروفایل کاربر {user_id}: {str(e)}")
            raise
    
    async def submit_kyc_application(self, user_id: UUID) -> UserProfile:
        """ارسال درخواست KYC برای بررسی"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                raise ValueError("پروفایل کاربر یافت نشد")
            
            # بررسی شرایط ارسال
            if profile.kyc_status != KYCStatus.DRAFT:
                raise ValueError("درخواست قبلاً ارسال شده است")
            
            # تغییر وضعیت به submitted
            profile.kyc_status = KYCStatus.SUBMITTED
            profile.submitted_at = datetime.utcnow()
            profile.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(profile)
            
            # ثبت در تاریخچه state machine
            await self._log_state_change(
                user_id, 
                KYCStatus.DRAFT.value, 
                KYCStatus.SUBMITTED.value,
                "user_submit"
            )
            
            logger.info(f"درخواست KYC کاربر {user_id} ارسال شد")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در ارسال درخواست KYC کاربر {user_id}: {str(e)}")
            raise
    
    async def verify_user_identity(self, user_id: UUID, verification_data: VerificationCreate) -> KYCVerification:
        """ثبت تأییدیه هویت کاربر"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                raise ValueError("پروفایل کاربر یافت نشد")
            
            verification = KYCVerification(
                user_id=user_id,
                profile_id=profile.id,
                verification_type=verification_data.verification_type,
                status="pending",
                method=verification_data.method,
                confidence_score=verification_data.confidence_score,
                auto_verification_result=verification_data.auto_verification_result,
                submitted_at=datetime.utcnow()
            )
            
            self.db.add(verification)
            self.db.commit()
            self.db.refresh(verification)
            
            logger.info(f"تأییدیه {verification_data.verification_type} برای کاربر {user_id} ثبت شد")
            return verification
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در ثبت تأییدیه کاربر {user_id}: {str(e)}")
            raise
    
    async def upload_document(self, user_id: UUID, document_data: DocumentUpload) -> KYCDocument:
        """آپلود سند هویتی"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                raise ValueError("پروفایل کاربر یافت نشد")
            
            document = KYCDocument(
                user_id=user_id,
                profile_id=profile.id,
                document_type=document_data.document_type,
                file_name=document_data.file_name,
                file_path=document_data.file_path,
                file_size=document_data.file_size,
                mime_type=document_data.mime_type,
                file_hash=document_data.file_hash,
                status="pending",
                uploaded_at=datetime.utcnow()
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            logger.info(f"سند {document_data.document_type} برای کاربر {user_id} آپلود شد")
            return document
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در آپلود سند کاربر {user_id}: {str(e)}")
            raise
    
    async def approve_kyc(self, user_id: UUID, admin_id: UUID, kyc_level: KYCLevel) -> UserProfile:
        """تأیید درخواست KYC توسط ادمین"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                raise ValueError("پروفایل کاربر یافت نشد")
            
            profile.kyc_status = KYCStatus.APPROVED
            profile.kyc_level = kyc_level
            profile.reviewed_at = datetime.utcnow()
            profile.reviewed_by = admin_id
            profile.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(profile)
            
            # ثبت در تاریخچه state machine
            await self._log_state_change(
                user_id, 
                profile.kyc_status.value, 
                KYCStatus.APPROVED.value,
                "admin_approve",
                meta_info={"admin_id": admin_id, "kyc_level": kyc_level.value}
            )
            
            logger.info(f"درخواست KYC کاربر {user_id} توسط ادمین {admin_id} تأیید شد")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در تأیید KYC کاربر {user_id}: {str(e)}")
            raise
    
    async def reject_kyc(self, user_id: UUID, admin_id: UUID, reason: str) -> UserProfile:
        """رد درخواست KYC توسط ادمین"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                raise ValueError("پروفایل کاربر یافت نشد")
            
            profile.kyc_status = KYCStatus.REJECTED
            profile.reviewed_at = datetime.utcnow()
            profile.reviewed_by = admin_id
            profile.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(profile)
            
            # ثبت در تاریخچه state machine
            await self._log_state_change(
                user_id, 
                profile.kyc_status.value, 
                KYCStatus.REJECTED.value,
                "admin_reject",
                meta_info={"admin_id": admin_id, "reason": reason}
            )
            
            logger.info(f"درخواست KYC کاربر {user_id} توسط ادمین {admin_id} رد شد")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در رد KYC کاربر {user_id}: {str(e)}")
            raise
    
    def _calculate_completion_percentage(self, profile: UserProfile) -> float:
        """محاسبه درصد تکمیل پروفایل"""
        total_fields = 10  # تعداد فیلدهای اصلی
        completed_fields = 0
        
        if profile.first_name: completed_fields += 1
        if profile.last_name: completed_fields += 1
        if profile.national_code: completed_fields += 1
        if profile.birth_date: completed_fields += 1
        if profile.address: completed_fields += 1
        if profile.phone: completed_fields += 1
        if profile.city: completed_fields += 1
        if profile.bank_name: completed_fields += 1
        if profile.sheba_number: completed_fields += 1
        if profile.email_verified: completed_fields += 0.5
        if profile.mobile_verified: completed_fields += 0.5
        
        return (completed_fields / total_fields) * 100
    
    async def _log_state_change(self, user_id: UUID, from_state: str, to_state: str, 
                              transition: str, meta_info: Dict = None):
        """ثبت تغییر وضعیت در تاریخچه"""
        logger.info(f"State change for user {user_id}: {from_state} -> {to_state} via {transition}")
        
        # اگر بخواهید در دیتابیس ذخیره کنید:
        # from backend.apps.kyc.models.kyc_state_machine import KYCStateHistory
        # history_entry = KYCStateHistory(
        #     user_id=str(user_id),
        #     from_state=from_state,
        #     to_state=to_state,
        #     transition=transition,
        #     reason="",
        #     meta_info=meta_info or {}
        # )
        # self.db.add(history_entry)
        # self.db.commit()
    
    async def get_kyc_stats(self) -> Dict[str, Any]:
        """دریافت آمار KYC"""
        total_profiles = self.db.query(UserProfile).count()
        pending_reviews = self.db.query(UserProfile).filter(
            UserProfile.kyc_status == KYCStatus.SUBMITTED
        ).count()
        approved_profiles = self.db.query(UserProfile).filter(
            UserProfile.kyc_status == KYCStatus.APPROVED
        ).count()
        
        return {
            "total_profiles": total_profiles,
            "pending_reviews": pending_reviews,
            "approved_profiles": approved_profiles,
            "approval_rate": (approved_profiles / total_profiles * 100) if total_profiles > 0 else 0
        }
    
    async def verify_email(self, user_id: UUID) -> bool:
        """تأیید ایمیل کاربر"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                return False
            
            profile.email_verified = True
            profile.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"ایمیل کاربر {user_id} تأیید شد")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در تأیید ایمیل کاربر {user_id}: {str(e)}")
            return False
    
    async def verify_mobile(self, user_id: UUID) -> bool:
        """تأیید موبایل کاربر"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                return False
            
            profile.mobile_verified = True
            profile.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"موبایل کاربر {user_id} تأیید شد")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در تأیید موبایل کاربر {user_id}: {str(e)}")
            return False
    
    async def verify_bank_account(self, user_id: UUID) -> bool:
        """تأیید حساب بانکی کاربر"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                return False
            
            profile.bank_verified = True
            profile.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"حساب بانکی کاربر {user_id} تأیید شد")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در تأیید حساب بانکی کاربر {user_id}: {str(e)}")
            return False
    
    async def get_pending_verifications(self, user_id: UUID) -> List[KYCVerification]:
        """دریافت لیست تأییدیه‌های در انتظار کاربر"""
        return self.db.query(KYCVerification).filter(
            KYCVerification.user_id == user_id,
            KYCVerification.status == "pending"
        ).all()
    
    async def get_user_documents(self, user_id: UUID) -> List[KYCDocument]:
        """دریافت لیست مدارک کاربر"""
        return self.db.query(KYCDocument).filter(
            KYCDocument.user_id == user_id
        ).order_by(KYCDocument.created_at.desc()).all()
    
    async def update_kyc_level(self, user_id: UUID, new_level: KYCLevel) -> UserProfile:
        """بروزرسانی سطح KYC کاربر"""
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                raise ValueError("پروفایل کاربر یافت نشد")
            
            profile.kyc_level = new_level
            profile.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(profile)
            
            logger.info(f"سطح KYC کاربر {user_id} به {new_level.value} بروزرسانی شد")
            return profile
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در بروزرسانی سطح KYC کاربر {user_id}: {str(e)}")
            raise