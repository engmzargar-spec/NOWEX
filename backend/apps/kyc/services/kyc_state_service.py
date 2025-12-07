from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from backend.apps.kyc.models.kyc_state_machine import KYCStateMachine, KYCStateHistory
from backend.apps.kyc.models.kyc_models import KYCStatus
import logging

logger = logging.getLogger(__name__)

class KYCStateService:
    def __init__(self, db: Session):
        self.db = db
        self.state_machine = KYCStateMachine()
    
    async def transition_kyc_state(self, user_id: int, current_state: str, 
                                 transition: str, reason: str = None, 
                                 meta_info: Dict = None) -> str:
        """انجام انتقال وضعیت KYC"""
        try:
            # تبدیل به enum
            current_state_enum = KYCStateMachine.States(current_state)
            transition_enum = KYCStateMachine.Transitions(transition)
            
            # بررسی امکان انتقال
            if not self.state_machine.can_transition(current_state_enum, transition_enum):
                raise ValueError(
                    f"انتقال {transition} از وضعیت {current_state} امکان‌پذیر نیست"
                )
            
            # دریافت وضعیت جدید
            new_state = self.state_machine.get_next_state(current_state_enum, transition_enum)
            
            # ثبت در تاریخچه
            await self._log_state_history(
                user_id, current_state, new_state.value, transition, reason, meta_info
            )
            
            logger.info(f"انتقال وضعیت KYC کاربر {user_id}: {current_state} -> {new_state.value}")
            return new_state.value
            
        except Exception as e:
            logger.error(f"خطا در انتقال وضعیت KYC کاربر {user_id}: {str(e)}")
            raise
    
    async def get_available_transitions(self, current_state: str) -> List[str]:
        """دریافت لیست انتقال‌های ممکن"""
        try:
            current_state_enum = KYCStateMachine.States(current_state)
            transitions = self.state_machine.get_available_transitions(current_state_enum)
            return [transition.value for transition in transitions]
        except Exception as e:
            logger.error(f"خطا در دریافت انتقال‌های ممکن: {str(e)}")
            return []
    
    async def get_state_history(self, user_id: int) -> List[Dict]:
        """دریافت تاریخچه وضعیت‌های کاربر"""
        try:
            history_entries = self.db.query(KYCStateHistory).filter(
                KYCStateHistory.user_id == str(user_id)
            ).order_by(KYCStateHistory.created_at.desc()).all()
            
            return [
                {
                    "id": entry.id,
                    "from_state": entry.from_state,
                    "to_state": entry.to_state,
                    "transition": entry.transition,
                    "reason": entry.reason,
                    "meta_info": entry.meta_info,
                    "created_at": entry.created_at.isoformat()
                }
                for entry in history_entries
            ]
        except Exception as e:
            logger.error(f"خطا در دریافت تاریخچه وضعیت کاربر {user_id}: {str(e)}")
            return []
    
    async def _log_state_history(self, user_id: int, from_state: str, to_state: str,
                               transition: str, reason: str = None, meta_info: Dict = None):
        """ثبت تاریخچه تغییر وضعیت"""
        try:
            history_entry = KYCStateHistory(
                user_id=str(user_id),
                from_state=from_state,
                to_state=to_state,
                transition=transition,
                reason=reason,
                meta_info=meta_info or {}
            )
            
            self.db.add(history_entry)
            self.db.commit()
            
            logger.info(f"State history logged for user {user_id}: {from_state} -> {to_state}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در ثبت تاریخچه وضعیت کاربر {user_id}: {str(e)}")
    
    async def validate_transition(self, user_id: int, current_state: str, transition: str) -> Dict:
        """اعتبارسنجی انتقال وضعیت"""
        try:
            current_state_enum = KYCStateMachine.States(current_state)
            transition_enum = KYCStateMachine.Transitions(transition)
            
            is_valid = self.state_machine.can_transition(current_state_enum, transition_enum)
            
            if is_valid:
                next_state = self.state_machine.get_next_state(current_state_enum, transition_enum)
                return {
                    "is_valid": True,
                    "current_state": current_state,
                    "transition": transition,
                    "next_state": next_state.value,
                    "message": "انتقال معتبر است"
                }
            else:
                available_transitions = self.state_machine.get_available_transitions(current_state_enum)
                return {
                    "is_valid": False,
                    "current_state": current_state,
                    "transition": transition,
                    "available_transitions": [t.value for t in available_transitions],
                    "message": f"انتقال {transition} از وضعیت {current_state} امکان‌پذیر نیست"
                }
                
        except Exception as e:
            logger.error(f"خطا در اعتبارسنجی انتقال وضعیت کاربر {user_id}: {str(e)}")
            return {
                "is_valid": False,
                "current_state": current_state,
                "transition": transition,
                "message": f"خطا در اعتبارسنجی: {str(e)}"
            }
    
    async def get_current_state_info(self, user_id: int) -> Dict:
        """دریافت اطلاعات وضعیت فعلی کاربر"""
        try:
            from backend.apps.kyc.models.kyc_models import UserProfile
            
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile:
                return {
                    "user_id": user_id,
                    "current_state": "not_found",
                    "available_transitions": [],
                    "message": "پروفایل کاربر یافت نشد"
                }
            
            current_state = profile.kyc_status.value
            available_transitions = await self.get_available_transitions(current_state)
            
            return {
                "user_id": user_id,
                "current_state": current_state,
                "kyc_level": profile.kyc_level.value,
                "available_transitions": available_transitions,
                "submitted_at": profile.submitted_at.isoformat() if profile.submitted_at else None,
                "reviewed_at": profile.reviewed_at.isoformat() if profile.reviewed_at else None
            }
            
        except Exception as e:
            logger.error(f"خطا در دریافت اطلاعات وضعیت کاربر {user_id}: {str(e)}")
            return {
                "user_id": user_id,
                "current_state": "error",
                "available_transitions": [],
                "message": f"خطا در دریافت اطلاعات: {str(e)}"
            }
    
    async def force_transition(self, user_id: int, target_state: str, 
                             admin_id: int, reason: str) -> Dict:
        """اجبار انتقال وضعیت (فقط برای ادمین)"""
        try:
            from backend.apps.kyc.models.kyc_models import UserProfile, KYCStatus
            
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile:
                raise ValueError("پروفایل کاربر یافت نشد")
            
            current_state = profile.kyc_status.value
            
            # بررسی معتبر بودن وضعیت هدف
            try:
                target_state_enum = KYCStateMachine.States(target_state)
            except ValueError:
                raise ValueError(f"وضعیت هدف {target_state} معتبر نیست")
            
            # تغییر وضعیت
            profile.kyc_status = KYCStatus(target_state)
            profile.updated_at = datetime.utcnow()
            
            # ثبت در تاریخچه
            await self._log_state_history(
                user_id,
                current_state,
                target_state,
                "admin_force_transition",
                reason,
                {"admin_id": admin_id, "forced": True, "reason": reason}
            )
            
            self.db.commit()
            
            logger.info(f"وضعیت KYC کاربر {user_id} توسط ادمین {admin_id} به {target_state} تغییر یافت")
            
            return {
                "success": True,
                "user_id": user_id,
                "previous_state": current_state,
                "new_state": target_state,
                "admin_id": admin_id,
                "reason": reason,
                "message": "انتقال وضعیت با موفقیت انجام شد"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در انتقال اجباری وضعیت کاربر {user_id}: {str(e)}")
            raise
    
    async def reset_kyc_status(self, user_id: int, reason: str = None) -> Dict:
        """بازنشانی وضعیت KYC به حالت پیش‌فرض"""
        try:
            from backend.apps.kyc.models.kyc_models import UserProfile, KYCStatus
            
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile:
                raise ValueError("پروفایل کاربر یافت نشد")
            
            current_state = profile.kyc_status.value
            
            # بازنشانی به حالت پیش‌فرض
            profile.kyc_status = KYCStatus.DRAFT
            profile.kyc_level = KYCLevel.BASIC
            profile.submitted_at = None
            profile.reviewed_at = None
            profile.reviewed_by = None
            profile.updated_at = datetime.utcnow()
            
            # ثبت در تاریخچه
            await self._log_state_history(
                user_id,
                current_state,
                KYCStatus.DRAFT.value,
                "system_reset",
                reason or "بازنشانی وضعیت KYC",
                {"reset_reason": reason, "system_action": True}
            )
            
            self.db.commit()
            
            logger.info(f"وضعیت KYC کاربر {user_id} بازنشانی شد")
            
            return {
                "success": True,
                "user_id": user_id,
                "previous_state": current_state,
                "new_state": KYCStatus.DRAFT.value,
                "message": "وضعیت KYC با موفقیت بازنشانی شد",
                "reason": reason
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در بازنشانی وضعیت KYC کاربر {user_id}: {str(e)}")
            raise
    
    async def get_state_statistics(self) -> Dict:
        """دریافت آمار وضعیت‌های KYC"""
        try:
            from backend.apps.kyc.models.kyc_models import UserProfile, KYCStatus
            
            # شمارش کاربران بر اساس وضعیت
            status_counts = {}
            for status in KYCStatus:
                count = self.db.query(UserProfile).filter(
                    UserProfile.kyc_status == status
                ).count()
                status_counts[status.value] = count
            
            # تاریخچه انتقال‌های اخیر
            recent_transitions = self.db.query(KYCStateHistory).order_by(
                KYCStateHistory.created_at.desc()
            ).limit(50).all()
            
            recent_history = [
                {
                    "user_id": entry.user_id,
                    "from_state": entry.from_state,
                    "to_state": entry.to_state,
                    "transition": entry.transition,
                    "timestamp": entry.created_at.isoformat()
                }
                for entry in recent_transitions
            ]
            
            return {
                "status_distribution": status_counts,
                "total_users": sum(status_counts.values()),
                "recent_transitions": recent_history,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطا در دریافت آمار وضعیت‌های KYC: {str(e)}")
            return {
                "status_distribution": {},
                "total_users": 0,
                "recent_transitions": [],
                "error": str(e)
            }

# ایمپورت datetime که در متدها استفاده شده
from datetime import datetime
from backend.apps.kyc.models.kyc_models import KYCLevel