from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Enum, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database.base import Base
import enum
import secrets
import string
from uuid import uuid4

class ReferralStatus(enum.Enum):
    PENDING = "pending"
    REGISTERED = "registered"
    KYC_COMPLETED = "kyc_completed"
    FIRST_TRADE = "first_trade"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class RewardStatus(enum.Enum):
    PENDING = "pending"
    EARNED = "earned"
    PAID = "paid"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class ReferralProgram(Base):
    __tablename__ = "referral_programs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # اطلاعات برنامه
    program_name = Column(String(100), unique=True, index=True)
    program_description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # پاداش‌ها
    rewards = Column(JSON, nullable=False)
    
    # محدودیت‌ها
    max_referrals_per_user = Column(Integer)
    reward_expiry_days = Column(Integer, default=30)
    minimum_kyc_level = Column(String(20), default="level_1")
    
    # تنظیمات
    allow_self_referral = Column(Boolean, default=False)
    require_kyc_for_reward = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ReferralRelationship(Base):
    __tablename__ = "referral_relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # کاربران
    referrer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    referred_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, index=True, nullable=False)
    
    # کد معرف
    referral_code = Column(String(20), index=True)
    
    # وضعیت
    status = Column(Enum(ReferralStatus), default=ReferralStatus.PENDING)
    
    # پاداش‌ها
    total_bonus_earned = Column(JSON, default=dict)
    total_bonus_paid = Column(JSON, default=dict)
    
    # تاریخ‌های مهم
    referred_at = Column(DateTime, default=func.now())
    kyc_completed_at = Column(DateTime)
    first_trade_at = Column(DateTime)
    completed_at = Column(DateTime)
    expired_at = Column(DateTime)
    
    # متادیتا
    meta_info = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # ✅ اصلاح رابطه - با back_populates
    rewards = relationship("ReferralReward", back_populates="referral")
    referrer_user = relationship("User", foreign_keys=[referrer_id])
    referred_user = relationship("User", foreign_keys=[referred_id])

class ReferralReward(Base):
    __tablename__ = "referral_rewards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    referral_id = Column(UUID(as_uuid=True), ForeignKey("referral_relationships.id"), nullable=False)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    
    # نوع پاداش
    reward_type = Column(String(50))
    reward_stage = Column(String(50))
    
    # مقدار پاداش
    points_awarded = Column(Integer, default=0)
    cash_awarded = Column(Float, default=0.0)
    bonus_percentage = Column(Float, default=0.0)
    
    # وضعیت
    status = Column(Enum(RewardStatus), default=RewardStatus.PENDING)
    
    # تاریخ‌ها
    earned_at = Column(DateTime)
    paid_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # تأییدیه
    verified_by = Column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    verified_at = Column(DateTime)
    
    # متادیتا
    meta_info = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # ✅ اصلاح رابطه - با back_populates
    referral = relationship("ReferralRelationship", back_populates="rewards")

class ReferralCode(Base):
    __tablename__ = "referral_codes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, index=True, nullable=False)
    
    # کد معرف
    code = Column(String(20), unique=True, index=True)
    custom_code = Column(String(20), unique=True, index=True)
    
    # آمار
    total_referrals = Column(Integer, default=0)
    successful_referrals = Column(Integer, default=0)
    total_earnings = Column(JSON, default=dict)
    
    # تنظیمات
    is_active = Column(Boolean, default=True)
    is_custom = Column(Boolean, default=False)
    
    # تاریخ‌ها
    last_used_at = Column(DateTime)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # ✅ اصلاح رابطه
    user = relationship("User")

class ReferralStats(Base):
    __tablename__ = "referral_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, index=True, nullable=False)
    
    # آمار کلی
    total_invites_sent = Column(Integer, default=0)
    total_signups = Column(Integer, default=0)
    total_kyc_completed = Column(Integer, default=0)
    total_first_trades = Column(Integer, default=0)
    
    # نرخ تبدیل
    conversion_rates = Column(JSON, default=dict)
    
    # درآمد
    total_points_earned = Column(Integer, default=0)
    total_cash_earned = Column(Float, default=0.0)
    pending_rewards = Column(JSON, default=dict)
    
    # رتبه‌بندی
    leaderboard_rank = Column(Integer)
    
    # تاریخ‌ها
    last_invite_sent = Column(DateTime)
    stats_updated_at = Column(DateTime, default=func.now())
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # ✅ اصلاح رابطه
    user = relationship("User")

class ProgramConfiguration(Base):
    __tablename__ = "program_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # تنظیمات عمومی
    site_name = Column(String(100), default="NOWEX")
    program_title = Column(String(200), default="دعوت از دوستان")
    program_description = Column(Text)
    
    # تنظیمات پاداش
    default_rewards = Column(JSON, default=dict)
    reward_currency = Column(String(10), default="IRT")
    
    # محدودیت‌ها
    max_referrals_per_user = Column(Integer, default=50)
    reward_expiry_days = Column(Integer, default=30)
    min_trade_amount_for_reward = Column(Float, default=0.0)
    
    # تنظیمات رابط کاربری
    invite_message_template = Column(Text)
    social_share_buttons = Column(JSON, default=list)
    show_leaderboard = Column(Boolean, default=True)
    
    # تنظیمات اعلان
    send_invite_emails = Column(Boolean, default=True)
    send_reward_notifications = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())