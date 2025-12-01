from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from uuid import UUID

class UserLevel(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    DIAMOND = "DIAMOND"

class ScoreSource(str, Enum):
    KYC_COMPLETION = "kyc_completion"
    REFERRAL_BONUS = "referral_bonus"
    TRADING_VOLUME = "trading_volume"
    ACCOUNT_AGE = "account_age"
    DAILY_LOGIN = "daily_login"
    TRADE_ACTIVITY = "trade_activity"
    LOYALTY_BONUS = "loyalty_bonus"
    MANUAL_ADJUSTMENT = "manual_adjustment"
    PENALTY = "penalty"

class UserScoreResponse(BaseModel):
    id: UUID
    user_id: UUID
    total_score: int
    current_level: UserLevel
    score_breakdown: Dict[str, int]
    daily_login_streak: int
    total_trading_volume: float
    total_trades_count: int
    account_age_days: int
    last_login_date: Optional[datetime]
    last_score_calculation: Optional[datetime]
    level_updated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ScoreHistoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    score_change: int
    new_total_score: int
    source: ScoreSource
    source_details: Dict[str, Any]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class LeaderboardResponse(BaseModel):
    leaderboard: List[UserScoreResponse]
    user_rank: Optional[int]
    total_users: int

class ScoreBenefitsResponse(BaseModel):
    current_level: UserLevel
    total_score: int
    benefits: Dict[str, Any]
    next_level: Optional[Dict[str, Any]]
    progress_percentage: float

class BenefitsResponse(BaseModel):
    level: UserLevel
    level_name: str
    level_description: str
    min_score_required: int
    benefits: Dict[str, Any]
    level_color: Optional[str]
    level_icon: Optional[str]

class ScoringStatsResponse(BaseModel):
    total_users: int
    active_users: int
    level_distribution: Dict[str, int]
    average_score: float
    timestamp: str

class AddScoreRequest(BaseModel):
    points: int
    source: ScoreSource
    description: Optional[str] = ""
    meta_info: Optional[Dict[str, Any]] = None

class AddPenaltyRequest(BaseModel):
    penalty_type: str
    reason: str

class ResetScoreRequest(BaseModel):
    reason: str

class TradingActivityRequest(BaseModel):
    volume: float
    trade_count: int = 1

# 🔧 کلاس‌های جدید اضافه شده
class ScoreBreakdownResponse(BaseModel):
    kyc_completion: int
    referral_bonus: int
    trading_volume: int
    account_age: int
    loyalty_bonus: int
    activity_score: int
    penalties: int
    total_score: int

    class Config:
        from_attributes = True