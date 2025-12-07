from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import random
import string
from uuid import UUID

from backend.apps.referral.models.referral_models import (
    ReferralProgram, ReferralRelationship, ReferralCode,
    ReferralStats, ReferralStatus, RewardStatus
)
from backend.apps.scoring.services.scoring_engine import ScoringEngine
from backend.apps.scoring.models.scoring_models import ScoreSource

logger = logging.getLogger(__name__)

class ReferralService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_referral_code(self, user_id: UUID, custom_code: str = None) -> ReferralCode:
        """ایجاد کد معرف برای کاربر"""
        try:
            # بررسی وجود کد
            existing_code = self.db.query(ReferralCode).filter(
                ReferralCode.user_id == user_id
            ).first()
            
            if existing_code:
                return existing_code
            
            # ایجاد کد جدید
            if custom_code:
                # بررسی تکراری نبودن کد دلخواه
                existing_custom = self.db.query(ReferralCode).filter(
                    ReferralCode.code == custom_code
                ).first()
                if existing_custom:
                    raise ValueError("کد معرف دلخواه تکراری است")
                code = custom_code
                is_custom = True
            else:
                code = self._generate_random_code()
                is_custom = False
            
            referral_code = ReferralCode(
                user_id=user_id,
                code=code,
                is_custom=is_custom,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(referral_code)
            self.db.commit()
            self.db.refresh(referral_code)
            
            logger.info(f"کد معرف {code} برای کاربر {user_id} ایجاد شد")
            return referral_code
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در ایجاد کد معرف برای کاربر {user_id}: {str(e)}")
            raise
    
    def _generate_random_code(self, length: int = 8) -> str:
        """تولید کد تصادفی"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def get_or_create_referral_code(self, user_id: UUID) -> Dict[str, Any]:
        """دریافت یا ایجاد کد معرف"""
        try:
            # بررسی وجود کد
            existing_code = self.db.query(ReferralCode).filter(
                ReferralCode.user_id == user_id
            ).first()
            
            if existing_code:
                return {
                    "user_id": str(user_id),
                    "referral_code": existing_code.code,
                    "is_custom": existing_code.is_custom,
                    "is_active": existing_code.is_active,
                    "total_referrals": existing_code.total_referrals,
                    "created_at": existing_code.created_at.isoformat() if existing_code.created_at else None,
                    "last_used_at": existing_code.last_used_at.isoformat() if existing_code.last_used_at else None
                }
            
            # ایجاد کد جدید
            new_code = self.generate_referral_code(user_id)
            
            return {
                "user_id": str(user_id),
                "referral_code": new_code.code,
                "is_custom": new_code.is_custom,
                "is_active": new_code.is_active,
                "total_referrals": new_code.total_referrals,
                "created_at": new_code.created_at.isoformat() if new_code.created_at else None,
                "last_used_at": new_code.last_used_at.isoformat() if new_code.last_used_at else None
            }
            
        except Exception as e:
            logger.error(f"خطا در دریافت/ایجاد کد معرف برای کاربر {user_id}: {str(e)}")
            raise
    
    def apply_referral_code(self, referred_user_id: UUID, referral_code: str) -> Dict[str, Any]:
        """اعمال کد معرف در ثبت‌نام"""
        try:
            # پیدا کردن کد معرف
            referrer_code = self.db.query(ReferralCode).filter(
                ReferralCode.code == referral_code,
                ReferralCode.is_active == True
            ).first()
            
            if not referrer_code:
                raise ValueError("کد معرف معتبر نیست")
            
            referrer_id = referrer_code.user_id
            
            # بررسی خودمعرفی
            if referrer_id == referred_user_id:
                raise ValueError("خودمعرفی مجاز نیست")
            
            # بررسی وجود رابطه
            existing_relationship = self.db.query(ReferralRelationship).filter(
                ReferralRelationship.referred_id == referred_user_id
            ).first()
            
            if existing_relationship:
                raise ValueError("کاربر قبلاً با کد معرف ثبت‌نام کرده است")
            
            # ایجاد رابطه رفرال
            relationship = ReferralRelationship(
                referrer_id=referrer_id,
                referred_id=referred_user_id,
                referral_code=referral_code,
                status=ReferralStatus.REGISTERED.value,
                referred_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(relationship)
            
            # بروزرسانی آمار کد معرف
            referrer_code.total_referrals += 1
            referrer_code.last_used_at = datetime.utcnow()
            referrer_code.updated_at = datetime.utcnow()
            
            # بروزرسانی آمار رفرال
            self._update_referral_stats(referrer_id)
            
            self.db.commit()
            self.db.refresh(relationship)
            
            # تخصیص پاداش ثبت‌نام
            self._award_registration_bonus(referrer_id, referred_user_id, relationship.id)
            
            logger.info(f"کد معرف {referral_code} برای کاربر {referred_user_id} اعمال شد")
            
            return {
                "success": True,
                "referrer_id": str(referrer_id),
                "referred_id": str(referred_user_id),
                "referral_code": referral_code,
                "relationship_id": relationship.id,
                "bonus_awarded": True
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در اعمال کد معرف برای کاربر {referred_user_id}: {str(e)}")
            raise
    
    def get_referral_stats(self, user_id: UUID) -> Dict[str, Any]:
        """دریافت آمار رفرال کاربر"""
        try:
            # پیدا کردن آمار موجود
            stats = self.db.query(ReferralStats).filter(
                ReferralStats.user_id == user_id
            ).first()
            
            if not stats:
                # ایجاد آمار جدید اگر وجود ندارد
                stats = ReferralStats(
                    user_id=user_id,
                    total_signups=0,
                    total_kyc_completed=0,
                    total_first_trades=0,
                    total_points_earned=0,
                    total_cash_earned=0.0,
                    conversion_rates={},
                    leaderboard_rank=0,
                    stats_updated_at=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                self.db.add(stats)
                self.db.commit()
                self.db.refresh(stats)
            
            # محاسبه آمار واقعی - بدون استفاده از meta_info
            total_signups = self.db.query(ReferralRelationship).filter(
                ReferralRelationship.referrer_id == user_id
            ).count()
            
            kyc_completed = self.db.query(ReferralRelationship).filter(
                ReferralRelationship.referrer_id == user_id,
                ReferralRelationship.status.in_([ReferralStatus.KYC_COMPLETED.value, ReferralStatus.FIRST_TRADE.value, ReferralStatus.COMPLETED.value])
            ).count()
            
            first_trades = self.db.query(ReferralRelationship).filter(
                ReferralRelationship.referrer_id == user_id,
                ReferralRelationship.status.in_([ReferralStatus.FIRST_TRADE.value, ReferralStatus.COMPLETED.value])
            ).count()
            
            # محاسبه نرخ تبدیل
            conversion_rates = {}
            if total_signups > 0:
                conversion_rates = {
                    "signup_rate": 100.0,
                    "kyc_rate": round((kyc_completed / total_signups) * 100, 2),
                    "trade_rate": round((first_trades / total_signups) * 100, 2)
                }
            
            return {
                "user_id": str(user_id),
                "total_signups": total_signups,
                "total_kyc_completed": kyc_completed,
                "total_first_trades": first_trades,
                "total_points_earned": stats.total_points_earned,
                "total_cash_earned": float(stats.total_cash_earned),
                "conversion_rates": conversion_rates,
                "leaderboard_rank": stats.leaderboard_rank,
                "stats_updated_at": stats.stats_updated_at.isoformat() if stats.stats_updated_at else None,
                "created_at": stats.created_at.isoformat() if stats.created_at else None
            }
            
        except Exception as e:
            logger.error(f"خطا در دریافت آمار رفرال کاربر {user_id}: {str(e)}")
            # بازگشت آمار پیش‌فرض در صورت خطا
            return {
                "user_id": str(user_id),
                "total_signups": 0,
                "total_kyc_completed": 0,
                "total_first_trades": 0,
                "total_points_earned": 0,
                "total_cash_earned": 0.0,
                "conversion_rates": {},
                "leaderboard_rank": 0,
                "stats_updated_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
    
    def get_referral_rewards(self, user_id: UUID) -> Dict[str, Any]:
        """دریافت تاریخچه پاداش‌ها"""
        try:
            relationships = self.db.query(ReferralRelationship).filter(
                ReferralRelationship.referrer_id == user_id
            ).all()
            
            rewards = []
            total_points = 0
            
            for rel in relationships:
                reward_info = {
                    "referred_user_id": str(rel.referred_id),
                    "referral_code": rel.referral_code,
                    "status": rel.status,
                    "referred_at": rel.referred_at.isoformat() if rel.referred_at else None,
                    "points_earned": 0
                }
                
                # محاسبه امتیاز بر اساس وضعیت
                if rel.status == ReferralStatus.REGISTERED.value:
                    reward_info["points_earned"] = 5
                    reward_info["bonus_type"] = "registration"
                elif rel.status == ReferralStatus.KYC_COMPLETED.value:
                    reward_info["points_earned"] = 10
                    reward_info["bonus_type"] = "kyc_completion"
                elif rel.status in [ReferralStatus.FIRST_TRADE.value, ReferralStatus.COMPLETED.value]:
                    reward_info["points_earned"] = 15
                    reward_info["bonus_type"] = "first_trade"
                
                total_points += reward_info["points_earned"]
                rewards.append(reward_info)
            
            return {
                "user_id": str(user_id),
                "total_rewards": len(rewards),
                "total_points_earned": total_points,
                "rewards": rewards
            }
            
        except Exception as e:
            logger.error(f"خطا در دریافت پاداش‌های کاربر {user_id}: {str(e)}")
            return {
                "user_id": str(user_id),
                "total_rewards": 0,
                "total_points_earned": 0,
                "rewards": [],
                "error": str(e)
            }
    
    def get_referral_leaderboard(self, limit: int = 50) -> Dict[str, Any]:
        """دریافت جدول برترین معرف‌ها"""
        try:
            # محاسبه رتبه‌بندی بر اساس تعداد معرفی‌های موفق
            leaderboard_data = []
            
            # پیدا کردن همه کاربرانی که معرفی داشته‌اند
            all_referrers = self.db.query(ReferralRelationship.referrer_id).distinct().all()
            
            for (referrer_id,) in all_referrers:
                stats = self.get_referral_stats(referrer_id)
                if stats and stats.get("total_first_trades", 0) > 0:
                    leaderboard_data.append({
                        "user_id": str(referrer_id),
                        "total_signups": stats["total_signups"],
                        "successful_referrals": stats["total_first_trades"],
                        "total_points": stats["total_points_earned"],
                        "conversion_rate": stats["conversion_rates"].get("trade_rate", 0)
                    })
            
            # مرتب‌سازی بر اساس موفق‌ترین معرفی‌ها
            leaderboard_data.sort(key=lambda x: x["successful_referrals"], reverse=True)
            
            # محدود کردن نتایج
            leaderboard_data = leaderboard_data[:limit]
            
            # اضافه کردن رتبه
            for i, item in enumerate(leaderboard_data, 1):
                item["rank"] = i
            
            return {
                "leaderboard": leaderboard_data,
                "total_count": len(leaderboard_data),
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطا در دریافت جدول برترین‌ها: {str(e)}")
            return {
                "leaderboard": [],
                "total_count": 0,
                "error": str(e)
            }
    
    def _update_referral_stats(self, user_id: UUID):
        """بروزرسانی آمار رفرال کاربر"""
        try:
            stats = self.db.query(ReferralStats).filter(
                ReferralStats.user_id == user_id
            ).first()
            
            if not stats:
                stats = ReferralStats(user_id=user_id)
                self.db.add(stats)
            
            # محاسبه آمار واقعی
            total_signups = self.db.query(ReferralRelationship).filter(
                ReferralRelationship.referrer_id == user_id
            ).count()
            
            kyc_completed = self.db.query(ReferralRelationship).filter(
                ReferralRelationship.referrer_id == user_id,
                ReferralRelationship.status.in_([ReferralStatus.KYC_COMPLETED.value, ReferralStatus.FIRST_TRADE.value, ReferralStatus.COMPLETED.value])
            ).count()
            
            first_trades = self.db.query(ReferralRelationship).filter(
                ReferralRelationship.referrer_id == user_id,
                ReferralRelationship.status.in_([ReferralStatus.FIRST_TRADE.value, ReferralStatus.COMPLETED.value])
            ).count()
            
            # بروزرسانی آمار
            stats.total_signups = total_signups
            stats.total_kyc_completed = kyc_completed
            stats.total_first_trades = first_trades
            
            # محاسبه نرخ تبدیل
            if total_signups > 0:
                stats.conversion_rates = {
                    "signup_rate": 100.0,
                    "kyc_rate": round((kyc_completed / total_signups) * 100, 2),
                    "trade_rate": round((first_trades / total_signups) * 100, 2)
                }
            
            stats.stats_updated_at = datetime.utcnow()
            stats.updated_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"خطا در بروزرسانی آمار رفرال کاربر {user_id}: {str(e)}")
    
    def _award_registration_bonus(self, referrer_id: UUID, referred_id: UUID, relationship_id: int):
        """تخصیص پاداش ثبت‌نام"""
        try:
            scoring_engine = ScoringEngine(self.db)
            
            # امتیاز برای معرف
            scoring_engine.add_score(
                referrer_id,
                5,  # امتیاز ثبت‌نام
                ScoreSource.REFERRAL_BONUS,
                "پاداش ثبت‌نام کاربر معرفی شده",
                meta_info={
                    "referred_user_id": str(referred_id),
                    "relationship_id": relationship_id,
                    "bonus_type": "registration"
                }
            )
            
            logger.info(f"پاداش ثبت‌نام برای معرف {referrer_id} تخصیص یافت")
            
        except Exception as e:
            logger.error(f"خطا در تخصیص پاداش ثبت‌نام: {str(e)}")
    
    def process_kyc_completion(self, user_id: UUID) -> bool:
        """پردازش تکمیل KYC کاربر و تخصیص پاداش"""
        try:
            # پیدا کردن رابطه رفرال
            relationship = self.db.query(ReferralRelationship).filter(
                ReferralRelationship.referred_id == user_id,
                ReferralRelationship.status == ReferralStatus.REGISTERED.value
            ).first()
            
            if not relationship:
                return False
            
            # بروزرسانی وضعیت
            relationship.status = ReferralStatus.KYC_COMPLETED.value
            relationship.kyc_completed_at = datetime.utcnow()
            relationship.updated_at = datetime.utcnow()
            
            # تخصیص پاداش تکمیل KYC
            self._award_kyc_bonus(relationship.referrer_id, user_id, relationship.id)
            
            self.db.commit()
            
            logger.info(f"پاداش KYC برای معرف کاربر {user_id} تخصیص یافت")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در پردازش KYC کاربر {user_id}: {str(e)}")
            return False
    
    def process_first_trade(self, user_id: UUID, trade_data: Dict) -> bool:
        """پردازش اولین معامله کاربر و تخصیص پاداش"""
        try:
            # پیدا کردن رابطه رفرال
            relationship = self.db.query(ReferralRelationship).filter(
                ReferralRelationship.referred_id == user_id,
                ReferralRelationship.status.in_([ReferralStatus.REGISTERED.value, ReferralStatus.KYC_COMPLETED.value])
            ).first()
            
            if not relationship:
                return False
            
            # بروزرسانی وضعیت
            relationship.status = ReferralStatus.FIRST_TRADE.value
            relationship.first_trade_at = datetime.utcnow()
            relationship.updated_at = datetime.utcnow()
            
            # تخصیص پاداش اولین معامله
            self._award_first_trade_bonus(relationship.referrer_id, user_id, relationship.id, trade_data)
            
            self.db.commit()
            
            logger.info(f"پاداش اولین معامله برای معرف کاربر {user_id} تخصیص یافت")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در پردازش اولین معامله کاربر {user_id}: {str(e)}")
            return False
    
    def _award_kyc_bonus(self, referrer_id: UUID, referred_id: UUID, relationship_id: int):
        """تخصیص پاداش تکمیل KYC"""
        try:
            scoring_engine = ScoringEngine(self.db)
            
            # امتیاز برای معرف
            scoring_engine.add_score(
                referrer_id,
                10,  # امتیاز تکمیل KYC
                ScoreSource.REFERRAL_BONUS,
                "پاداش تکمیل KYC کاربر معرفی شده",
                meta_info={
                    "referred_user_id": str(referred_id),
                    "relationship_id": relationship_id,
                    "bonus_type": "kyc_completion"
                }
            )
            
            logger.info(f"پاداش KYC برای معرف {referrer_id} تخصیص یافت")
            
        except Exception as e:
            logger.error(f"خطا در تخصیص پاداش KYC: {str(e)}")
    
    def _award_first_trade_bonus(self, referrer_id: UUID, referred_id: UUID, 
                               relationship_id: int, trade_data: Dict):
        """تخصیص پاداش اولین معامله"""
        try:
            scoring_engine = ScoringEngine(self.db)
            
            # امتیاز برای معرف
            scoring_engine.add_score(
                referrer_id,
                15,  # امتیاز اولین معامله
                ScoreSource.REFERRAL_BONUS,
                "پاداش اولین معامله کاربر معرفی شده",
                meta_info={
                    "referred_user_id": str(referred_id),
                    "relationship_id": relationship_id,
                    "bonus_type": "first_trade",
                    "trade_data": trade_data
                }
            )
            
            logger.info(f"پاداش اولین معامله برای معرف {referrer_id} تخصیص یافت")
            
        except Exception as e:
            logger.error(f"خطا در تخصیص پاداش اولین معامله: {str(e)}")
    
    def get_referral_relationships(self, user_id: UUID, status: str = None) -> List[ReferralRelationship]:
        """دریافت لیست کاربران معرفی شده"""
        query = self.db.query(ReferralRelationship).filter(
            ReferralRelationship.referrer_id == user_id
        )
        
        if status:
            query = query.filter(ReferralRelationship.status == status)
        
        return query.order_by(ReferralRelationship.created_at.desc()).all()
    
    def get_referral_program(self) -> Optional[ReferralProgram]:
        """دریافت برنامه رفرال فعال"""
        return self.db.query(ReferralProgram).filter(
            ReferralProgram.is_active == True
        ).first()
    
    def deactivate_referral_code(self, user_id: UUID) -> bool:
        """غیرفعال کردن کد معرف کاربر"""
        try:
            referral_code = self.db.query(ReferralCode).filter(
                ReferralCode.user_id == user_id
            ).first()
            
            if not referral_code:
                return False
            
            referral_code.is_active = False
            referral_code.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"کد معرف کاربر {user_id} غیرفعال شد")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در غیرفعال کردن کد معرف کاربر {user_id}: {str(e)}")
            return False