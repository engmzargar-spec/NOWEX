from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID
import logging
from backend.apps.scoring.models.scoring_models import (
    UserScore, ScoreHistory, ScoringRules, UserLevel, ScoreSource
)

logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self, db: Session):
        self.db = db
        self.scoring_rules = {
            "kyc_completion": {
                "email_verification": 2,
                "mobile_verification": 3,
                "profile_completion": 5,
                "bank_verification": 8,
                "identity_verification": 10,
                "address_verification": 5,
                "video_verification": 15
            },
            "activity_based": {
                "daily_login": 1,
                "complete_first_trade": 5,
                "trade_volume_1m": 10,
                "trade_volume_10m": 25,
                "account_1_month_old": 5,
                "account_6_months_old": 15,
                "account_1_year_old": 30
            },
            "referral_bonus": {
                "referral_signup": 5,
                "referral_kyc_complete": 10,
                "referral_first_trade": 15
            },
            "loyalty": {
                "continuous_login_7_days": 5,
                "continuous_login_30_days": 20,
                "monthly_trader": 10
            },
            "penalties": {
                "failed_login_attempts": -1,
                "chargeback": -20,
                "suspicious_activity": -50,
                "kyc_document_rejected": -5,
                "account_inactivity_30d": -10
            }
        }
    
    def initialize_user_score(self, user_id: UUID) -> UserScore:
        try:
            existing_score = self.db.query(UserScore).filter(
                UserScore.user_id == user_id
            ).first()
            
            if existing_score:
                return existing_score
            
            user_score = UserScore(
                user_id=user_id,
                total_score=0,
                current_level=UserLevel.BRONZE.value,
                score_breakdown={},
                daily_login_streak=0,
                total_trading_volume=0.0,
                total_trades_count=0,
                account_age_days=0,
                last_score_calculation=datetime.utcnow(),
                level_updated_at=datetime.utcnow()
            )
            
            self.db.add(user_score)
            self.db.commit()
            self.db.refresh(user_score)
            
            logger.info(f"رکورد امتیاز برای کاربر {user_id} ایجاد شد")
            return user_score
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در ایجاد رکورد امتیاز کاربر {user_id}: {str(e)}")
            raise
    
    def calculate_total_score(self, user_id: UUID) -> int:
        try:
            user_score = self.get_user_score(user_id)
            if not user_score:
                user_score = self.initialize_user_score(user_id)
            
            breakdown = {}
            total_score = 0
            
            kyc_score = self._calculate_kyc_score(user_id)
            breakdown["kyc_completion"] = kyc_score
            total_score += kyc_score
            
            activity_score = self._calculate_activity_score(user_id)
            breakdown["activity"] = activity_score
            total_score += activity_score
            
            loyalty_score = self._calculate_loyalty_score(user_id)
            breakdown["loyalty"] = loyalty_score
            total_score += loyalty_score
            
            referral_score = self._calculate_referral_score(user_id)
            breakdown["referral"] = referral_score
            total_score += referral_score
            
            user_score.total_score = max(0, total_score)
            user_score.score_breakdown = breakdown
            user_score.last_score_calculation = datetime.utcnow()
            
            self._check_level_upgrade(user_score)
            
            self.db.commit()
            self.db.refresh(user_score)
            
            logger.info(f"امتیاز کاربر {user_id} محاسبه شد: {total_score}")
            return user_score.total_score
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در محاسبه امتیاز کاربر {user_id}: {str(e)}")
            raise
    
    def add_score(self, user_id: UUID, points: int, source: ScoreSource, 
                 description: str = "", meta_info: Dict = None) -> ScoreHistory:
        try:
            user_score = self.get_user_score(user_id)
            if not user_score:
                user_score = self.initialize_user_score(user_id)
            
            score_history = ScoreHistory(
                user_id=user_id,
                score_id=user_score.id,
                score_change=points,
                new_total_score=user_score.total_score + points,
                source=source.value,
                source_details=meta_info or {},
                description=description,
                meta_info=meta_info or {}
            )
            
            user_score.total_score += points
            
            source_key = source.value
            if source_key in user_score.score_breakdown:
                user_score.score_breakdown[source_key] += points
            else:
                user_score.score_breakdown[source_key] = points
            
            user_score.updated_at = datetime.utcnow()
            
            self.db.add(score_history)
            self.db.commit()
            self.db.refresh(score_history)
            self.db.refresh(user_score)
            
            self._check_level_upgrade(user_score)
            
            logger.info(f"{points} امتیاز به کاربر {user_id} اضافه شد. منبع: {source.value}")
            return score_history
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در افزودن امتیاز به کاربر {user_id}: {str(e)}")
            raise
    
    def record_daily_login(self, user_id: UUID) -> bool:
        try:
            user_score = self.get_user_score(user_id)
            if not user_score:
                user_score = self.initialize_user_score(user_id)
            
            today = datetime.utcnow().date()
            last_login = user_score.last_login_date.date() if user_score.last_login_date else None
            
            if last_login == today:
                return True
            
            if last_login and last_login == today - timedelta(days=1):
                user_score.daily_login_streak += 1
            else:
                user_score.daily_login_streak = 1
            
            user_score.last_login_date = datetime.utcnow()
            
            self.add_score(
                user_id, 
                self.scoring_rules["activity_based"]["daily_login"],
                ScoreSource.DAILY_LOGIN,
                "ورود روزانه"
            )
            
            if user_score.daily_login_streak % 7 == 0:
                self.add_score(
                    user_id,
                    self.scoring_rules["loyalty"]["continuous_login_7_days"],
                    ScoreSource.LOYALTY_BONUS,
                    f"پاداش ورود {user_score.daily_login_streak} روز متوالی"
                )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در ثبت ورود روزانه کاربر {user_id}: {str(e)}")
            return False
    
    def add_trading_activity(self, user_id: UUID, volume: float, trade_count: int = 1) -> bool:
        try:
            user_score = self.get_user_score(user_id)
            if not user_score:
                user_score = self.initialize_user_score(user_id)
            
            user_score.total_trading_volume += volume
            user_score.total_trades_count += trade_count
            
            if user_score.total_trades_count == trade_count:
                self.add_score(
                    user_id,
                    self.scoring_rules["activity_based"]["complete_first_trade"],
                    ScoreSource.TRADE_ACTIVITY,
                    "انجام اولین معامله"
                )
            
            if user_score.total_trading_volume >= 10000000:
                self.add_score(
                    user_id,
                    self.scoring_rules["activity_based"]["trade_volume_10m"],
                    ScoreSource.TRADING_VOLUME,
                    "دستیابی به حجم معاملات 10 میلیون"
                )
            elif user_score.total_trading_volume >= 1000000:
                self.add_score(
                    user_id,
                    self.scoring_rules["activity_based"]["trade_volume_1m"],
                    ScoreSource.TRADING_VOLUME,
                    "دستیابی به حجم معاملات 1 میلیون"
                )
            
            user_score.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"فعالیت معاملاتی کاربر {user_id} ثبت شد: حجم {volume}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در ثبت فعالیت معاملاتی کاربر {user_id}: {str(e)}")
            return False
    
    def update_account_age(self, user_id: UUID) -> bool:
        try:
            user_score = self.get_user_score(user_id)
            if not user_score:
                user_score = self.initialize_user_score(user_id)
            
            from backend.apps.auth.models.user import User
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            account_creation = user.created_at
            now = datetime.utcnow()
            age_days = (now - account_creation).days
            
            old_age = user_score.account_age_days
            user_score.account_age_days = age_days
            
            if age_days >= 365 and old_age < 365:
                self.add_score(
                    user_id,
                    self.scoring_rules["activity_based"]["account_1_year_old"],
                    ScoreSource.ACCOUNT_AGE,
                    "یک سال فعالیت در پلتفرم"
                )
            elif age_days >= 180 and old_age < 180:
                self.add_score(
                    user_id,
                    self.scoring_rules["activity_based"]["account_6_months_old"],
                    ScoreSource.ACCOUNT_AGE,
                    "شش ماه فعالیت در پلتفرم"
                )
            elif age_days >= 30 and old_age < 30:
                self.add_score(
                    user_id,
                    self.scoring_rules["activity_based"]["account_1_month_old"],
                    ScoreSource.ACCOUNT_AGE,
                    "یک ماه فعالیت در پلتفرم"
                )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در بروزرسانی سن حساب کاربر {user_id}: {str(e)}")
            return False
    
    def add_kyc_score(self, user_id: UUID, kyc_action: str) -> bool:
        try:
            if kyc_action not in self.scoring_rules["kyc_completion"]:
                logger.warning(f"عمل KYC نامعتبر: {kyc_action}")
                return False
            
            points = self.scoring_rules["kyc_completion"][kyc_action]
            
            self.add_score(
                user_id,
                points,
                ScoreSource.KYC_COMPLETION,
                f"امتیاز تکمیل {kyc_action}",
                {"kyc_action": kyc_action}
            )
            
            logger.info(f"امتیاز KYC برای کاربر {user_id} اضافه شد: {kyc_action}")
            return True
            
        except Exception as e:
            logger.error(f"خطا در افزودن امتیاز KYC کاربر {user_id}: {str(e)}")
            return False
    
    def add_penalty(self, user_id: UUID, penalty_type: str, reason: str = "") -> bool:
        try:
            if penalty_type not in self.scoring_rules["penalties"]:
                logger.warning(f"نوع جریمه نامعتبر: {penalty_type}")
                return False
            
            points = self.scoring_rules["penalties"][penalty_type]
            
            self.add_score(
                user_id,
                points,
                ScoreSource.PENALTY,
                f"جریمه: {reason}",
                {"penalty_type": penalty_type, "reason": reason}
            )
            
            logger.info(f"جریمه برای کاربر {user_id} اعمال شد: {penalty_type}")
            return True
            
        except Exception as e:
            logger.error(f"خطا در اعمال جریمه کاربر {user_id}: {str(e)}")
            return False
    
    def _calculate_kyc_score(self, user_id: UUID) -> int:
        from backend.apps.kyc.models.kyc_models import UserProfile
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        if not profile:
            return 0
        
        score = 0
        if profile.email_verified:
            score += self.scoring_rules["kyc_completion"]["email_verification"]
        if profile.mobile_verified:
            score += self.scoring_rules["kyc_completion"]["mobile_verification"]
        if profile.completion_percentage >= 50:
            score += self.scoring_rules["kyc_completion"]["profile_completion"]
        if profile.bank_verified:
            score += self.scoring_rules["kyc_completion"]["bank_verification"]
        if profile.identity_verified:
            score += self.scoring_rules["kyc_completion"]["identity_verification"]
        if profile.address_verified:
            score += self.scoring_rules["kyc_completion"]["address_verification"]
        if profile.video_verified:
            score += self.scoring_rules["kyc_completion"]["video_verification"]
        
        return score
    
    def _calculate_activity_score(self, user_id: UUID) -> int:
        user_score = self.get_user_score(user_id)
        if not user_score:
            return 0
        
        score = 0
        if user_score.total_trading_volume >= 10000000:
            score += self.scoring_rules["activity_based"]["trade_volume_10m"]
        elif user_score.total_trading_volume >= 1000000:
            score += self.scoring_rules["activity_based"]["trade_volume_1m"]
        
        if user_score.total_trades_count > 0:
            score += self.scoring_rules["activity_based"]["complete_first_trade"]
        
        return score
    
    def _calculate_loyalty_score(self, user_id: UUID) -> int:
        user_score = self.get_user_score(user_id)
        if not user_score:
            return 0
        
        score = 0
        if user_score.account_age_days >= 365:
            score += self.scoring_rules["activity_based"]["account_1_year_old"]
        elif user_score.account_age_days >= 180:
            score += self.scoring_rules["activity_based"]["account_6_months_old"]
        elif user_score.account_age_days >= 30:
            score += self.scoring_rules["activity_based"]["account_1_month_old"]
        
        return score
    
    def _calculate_referral_score(self, user_id: UUID) -> int:
        user_score = self.get_user_score(user_id)
        if not user_score:
            return 0
        return user_score.score_breakdown.get("referral_bonus", 0)
    
    def _check_level_upgrade(self, user_score: UserScore):
        old_level = user_score.current_level
        new_level = self._get_level_for_score(user_score.total_score)
        if new_level != old_level:
            user_score.current_level = new_level
            user_score.level_updated_at = datetime.utcnow()
            logger.info(f"کاربر {user_score.user_id} به سطح {new_level} ارتقاء یافت")
    
    def _get_level_for_score(self, score: int) -> str:
        if score >= 600:
            return UserLevel.DIAMOND.value
        elif score >= 300:
            return UserLevel.PLATINUM.value
        elif score >= 150:
            return UserLevel.GOLD.value
        elif score >= 50:
            return UserLevel.SILVER.value
        else:
            return UserLevel.BRONZE.value
    
    def get_user_score(self, user_id: UUID) -> Optional[UserScore]:
        return self.db.query(UserScore).filter(
            UserScore.user_id == user_id
        ).first()
    
    def get_score_history(self, user_id: UUID, limit: int = 50) -> List[ScoreHistory]:
        return self.db.query(ScoreHistory).filter(
            ScoreHistory.user_id == user_id
        ).order_by(ScoreHistory.created_at.desc()).limit(limit).all()
    
    def get_leaderboard(self, limit: int = 100) -> List[UserScore]:
        return self.db.query(UserScore).filter(
            UserScore.is_active == True
        ).order_by(UserScore.total_score.desc()).limit(limit).all()
    
    def get_user_rank(self, user_id: UUID) -> Optional[int]:
        try:
            all_scores = self.db.query(UserScore).filter(
                UserScore.is_active == True
            ).order_by(UserScore.total_score.desc()).all()
            
            for rank, score in enumerate(all_scores, 1):
                if score.user_id == user_id:
                    return rank
            return None
        except Exception as e:
            logger.error(f"خطا در دریافت رتبه کاربر {user_id}: {str(e)}")
            return None
    
    def reset_user_score(self, user_id: UUID, reason: str = "") -> bool:
        try:
            user_score = self.get_user_score(user_id)
            if not user_score:
                return False
            
            self.add_score(
                user_id,
                -user_score.total_score,
                ScoreSource.MANUAL_ADJUSTMENT,
                f"بازنشانی امتیاز: {reason}",
                {"reset_reason": reason, "previous_score": user_score.total_score}
            )
            
            user_score.total_score = 0
            user_score.score_breakdown = {}
            user_score.current_level = UserLevel.BRONZE.value
            user_score.level_updated_at = datetime.utcnow()
            user_score.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"امتیاز کاربر {user_id} بازنشانی شد. دلیل: {reason}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"خطا در بازنشانی امتیاز کاربر {user_id}: {str(e)}")
            return False
    
    def get_scoring_stats(self) -> Dict[str, Any]:
        try:
            total_users = self.db.query(UserScore).count()
            active_users = self.db.query(UserScore).filter(
                UserScore.is_active == True
            ).count()
            
            level_distribution = {}
            for level in UserLevel:
                count = self.db.query(UserScore).filter(
                    UserScore.current_level == level.value
                ).count()
                level_distribution[level.value] = count
            
            avg_score = self.db.query(func.avg(UserScore.total_score)).scalar() or 0
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "level_distribution": level_distribution,
                "average_score": round(float(avg_score), 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"خطا در دریافت آمار سیستم امتیازدهی: {str(e)}")
            return {
                "total_users": 0,
                "active_users": 0,
                "level_distribution": {},
                "average_score": 0,
                "error": str(e)
            }

    # 🔧 اصلاح متدهای API - حذف async
    def get_user_score_data(self, user_id: UUID) -> Dict[str, Any]:
        """Get user score data for API response"""
        try:
            user_score = self.get_user_score(user_id)
            if not user_score:
                raise Exception("User score not found")
            
            # 🔧 رفع مشکل Enum - تبدیل به string
            current_level = user_score.current_level
            if isinstance(current_level, UserLevel):
                current_level = current_level.value
            elif isinstance(current_level, str):
                current_level = current_level.upper()
            else:
                current_level = "BRONZE"
            
            return {
                "user_id": str(user_score.user_id),
                "total_score": user_score.total_score,
                "current_level": current_level,
                "daily_login_streak": user_score.daily_login_streak,
                "total_trading_volume": user_score.total_trading_volume,
                "total_trades_count": user_score.total_trades_count,
                "account_age_days": user_score.account_age_days,
                "score_breakdown": user_score.score_breakdown,
                "last_score_calculation": user_score.last_score_calculation.isoformat() if user_score.last_score_calculation else None,
                "level_updated_at": user_score.level_updated_at.isoformat() if user_score.level_updated_at else None,
                "created_at": user_score.created_at.isoformat() if user_score.created_at else None,
                "updated_at": user_score.updated_at.isoformat() if user_score.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting user score data for {user_id}: {str(e)}")
            raise

    def get_score_breakdown(self, user_id: UUID) -> Dict[str, Any]:
        """Get detailed score breakdown for user"""
        try:
            user_score = self.get_user_score(user_id)
            if not user_score:
                raise Exception("User score not found")
            
            # محاسبه امتیازهای جزئی
            kyc_score = self._calculate_kyc_score(user_id)
            activity_score = self._calculate_activity_score(user_id)
            loyalty_score = self._calculate_loyalty_score(user_id)
            referral_score = self._calculate_referral_score(user_id)
            
            breakdown = {
                "kyc_completion": {
                    "score": kyc_score,
                    "max_possible": 48,  # مجموع امتیازهای KYC
                    "percentage": round((kyc_score / 48) * 100, 2) if 48 > 0 else 0
                },
                "activity": {
                    "score": activity_score,
                    "max_possible": 35,  # مجموع امتیازهای فعالیت
                    "percentage": round((activity_score / 35) * 100, 2) if 35 > 0 else 0
                },
                "loyalty": {
                    "score": loyalty_score,
                    "max_possible": 45,  # مجموع امتیازهای وفاداری
                    "percentage": round((loyalty_score / 45) * 100, 2) if 45 > 0 else 0
                },
                "referral": {
                    "score": referral_score,
                    "max_possible": 30,  # مجموع امتیازهای معرفی
                    "percentage": round((referral_score / 30) * 100, 2) if 30 > 0 else 0
                },
                "total": {
                    "score": user_score.total_score,
                    "max_possible": 158,  # مجموع کل امتیازهای ممکن
                    "percentage": round((user_score.total_score / 158) * 100, 2) if 158 > 0 else 0
                }
            }
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error getting score breakdown for {user_id}: {str(e)}")
            raise

    def get_user_benefits(self, user_id: UUID) -> Dict[str, Any]:
        """Get benefits based on user score level"""
        try:
            user_score = self.get_user_score(user_id)
            if not user_score:
                raise Exception("User score not found")
            
            # 🔧 رفع مشکل Enum
            current_level = user_score.current_level
            if isinstance(current_level, UserLevel):
                current_level = current_level.value
            elif isinstance(current_level, str):
                current_level = current_level.upper()
            else:
                current_level = "BRONZE"
            
            # مزایای هر سطح
            benefits_map = {
                "BRONZE": {
                    "level_name": "برنز",
                    "benefits": ["معاملات پایه", "دسترسی به سیستم معرفی", "پشتیبانی استاندارد"],
                    "fee_discount": 0,
                    "withdrawal_limit": 5000000,
                    "support_priority": "standard"
                },
                "SILVER": {
                    "level_name": "نقره‌ای",
                    "benefits": ["معاملات پیشرفته", "برداشت بالاتر", "پشتیبانی سریعتر"],
                    "fee_discount": 5,
                    "withdrawal_limit": 20000000,
                    "support_priority": "priority"
                },
                "GOLD": {
                    "level_name": "طلایی",
                    "benefits": ["معاملات VIP", "تخفیف کارمزد", "پشتیبانی اختصاصی"],
                    "fee_discount": 10,
                    "withdrawal_limit": 50000000,
                    "support_priority": "vip"
                },
                "PLATINUM": {
                    "level_name": "پلاتینیوم",
                    "benefits": ["معاملات اختصاصی", "تخفیف ویژه", "مدیر حساب شخصی"],
                    "fee_discount": 15,
                    "withdrawal_limit": 100000000,
                    "support_priority": "premium"
                },
                "DIAMOND": {
                    "level_name": "الماس",
                    "benefits": ["تمام مزایای ویژه", "تخفیف حداکثری", "پشتیبانی 24/7"],
                    "fee_discount": 20,
                    "withdrawal_limit": 0,  # نامحدود
                    "support_priority": "executive"
                }
            }
            
            current_benefits = benefits_map.get(current_level, benefits_map["BRONZE"])
            
            # مزایای سطح بعدی
            next_level = self._get_next_level(current_level)
            next_benefits = benefits_map.get(next_level, {})
            
            return {
                "current_level": current_level,
                "current_benefits": current_benefits,
                "next_level": next_level,
                "next_level_benefits": next_benefits,
                "score_to_next_level": self._get_score_to_next_level(user_score.total_score),
                "progress_percentage": self._get_level_progress_percentage(user_score.total_score, current_level)
            }
            
        except Exception as e:
            logger.error(f"Error getting user benefits for {user_id}: {str(e)}")
            raise

    def _get_next_level(self, current_level: str) -> str:
        """Get next level based on current level"""
        levels = ["BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND"]
        try:
            current_index = levels.index(current_level)
            return levels[current_index + 1] if current_index < len(levels) - 1 else "DIAMOND"
        except ValueError:
            return "SILVER"

    def _get_score_to_next_level(self, current_score: int) -> int:
        """Calculate score needed to reach next level"""
        if current_score < 50:
            return 50 - current_score
        elif current_score < 150:
            return 150 - current_score
        elif current_score < 300:
            return 300 - current_score
        elif current_score < 600:
            return 600 - current_score
        else:
            return 0

    def _get_level_progress_percentage(self, current_score: int, current_level: str) -> float:
        """Calculate progress percentage within current level"""
        level_ranges = {
            "BRONZE": (0, 50),
            "SILVER": (50, 150),
            "GOLD": (150, 300),
            "PLATINUM": (300, 600),
            "DIAMOND": (600, float('inf'))
        }
        
        if current_level not in level_ranges:
            return 0
        
        min_score, max_score = level_ranges[current_level]
        level_range = max_score - min_score
        
        if level_range <= 0:
            return 100
        
        progress = min(100, max(0, ((current_score - min_score) / level_range) * 100))
        return round(progress, 2)