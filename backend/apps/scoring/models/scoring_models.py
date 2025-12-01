from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database.base import Base
import enum
from uuid import uuid4

class UserLevel(str, enum.Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    DIAMOND = "DIAMOND"

class ScoreSource(str, enum.Enum):
    KYC_COMPLETION = "kyc_completion"
    REFERRAL_BONUS = "referral_bonus"
    TRADING_VOLUME = "trading_volume"
    ACCOUNT_AGE = "account_age"
    DAILY_LOGIN = "daily_login"
    TRADE_ACTIVITY = "trade_activity"
    LOYALTY_BONUS = "loyalty_bonus"
    MANUAL_ADJUSTMENT = "manual_adjustment"
    PENALTY = "penalty"

class UserScore(Base):
    __tablename__ = "user_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, index=True, nullable=False)
    
    total_score = Column(Integer, default=0)
    current_level = Column(String(50), default=UserLevel.BRONZE.value)
    
    score_breakdown = Column(JSON, default=dict)
    
    daily_login_streak = Column(Integer, default=0)
    total_trading_volume = Column(Float, default=0.0)
    total_trades_count = Column(Integer, default=0)
    account_age_days = Column(Integer, default=0)
    
    last_login_date = Column(DateTime)
    last_score_calculation = Column(DateTime)
    level_updated_at = Column(DateTime)
    
    score_multiplier = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    score_history = relationship("ScoreHistory", back_populates="user_score")
    benefits = relationship("UserBenefits", back_populates="user_score")
    user = relationship("User")

class ScoreHistory(Base):
    __tablename__ = "score_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    score_id = Column(Integer, ForeignKey("user_scores.id"), nullable=False)
    
    score_change = Column(Integer, nullable=False)
    new_total_score = Column(Integer, nullable=False)
    
    source = Column(String(50), nullable=False)
    source_details = Column(JSON)
    
    description = Column(Text)
    meta_info = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())
    
    user_score = relationship("UserScore", back_populates="score_history")
    user = relationship("User")

class ScoreBenefits(Base):
    __tablename__ = "score_benefits"
    
    id = Column(Integer, primary_key=True, index=True)
    
    level = Column(String(50), unique=True, index=True)
    level_name = Column(String(50))
    level_description = Column(Text)
    
    min_score_required = Column(Integer, nullable=False)
    max_score = Column(Integer)
    
    benefits = Column(JSON, nullable=False)
    
    withdrawal_limit_multiplier = Column(Float, default=1.0)
    deposit_limit_multiplier = Column(Float, default=1.0)
    
    level_color = Column(String(7))
    level_icon = Column(String(100))
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class UserBenefits(Base):
    __tablename__ = "user_benefits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    score_id = Column(Integer, ForeignKey("user_scores.id"), nullable=False)
    
    active_benefits = Column(JSON, default=dict)
    
    benefits_usage = Column(JSON, default=dict)
    
    auto_claim_benefits = Column(Boolean, default=True)
    notifications_enabled = Column(Boolean, default=True)
    
    benefits_updated_at = Column(DateTime)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user_score = relationship("UserScore", back_populates="benefits")

class ScoringRules(Base):
    __tablename__ = "scoring_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), unique=True, index=True)
    rule_description = Column(Text)
    
    rule_type = Column(String(50))
    action_type = Column(String(100))
    
    base_points = Column(Integer, default=0)
    max_daily_points = Column(Integer)
    max_total_points = Column(Integer)
    
    conditions = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    
    valid_from = Column(DateTime, default=func.now())
    valid_until = Column(DateTime)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())