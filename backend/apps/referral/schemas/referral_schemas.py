from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from uuid import UUID

class ReferralStatus(str, Enum):
    PENDING = "pending"
    REGISTERED = "registered"
    KYC_COMPLETED = "kyc_completed"
    FIRST_TRADE = "first_trade"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class RewardStatus(str, Enum):
    PENDING = "pending"
    EARNED = "earned"
    PAID = "paid"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class ReferralCodeResponse(BaseModel):
    user_id: UUID
    referral_code: str
    is_custom: bool
    total_referrals: int
    is_active: bool
    last_used_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class ReferralStatsResponse(BaseModel):
    user_id: UUID
    total_referrals: int
    successful_referrals: int
    total_earnings: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReferralRelationshipResponse(BaseModel):
    referrer_id: UUID
    referred_id: UUID
    referral_code: str
    status: ReferralStatus
    referred_at: datetime
    kyc_completed_at: Optional[datetime]
    first_trade_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class ApplyReferralRequest(BaseModel):
    referral_code: str

class GenerateCodeRequest(BaseModel):
    custom_code: Optional[str] = None

class LeaderboardResponse(BaseModel):
    leaderboard: List[ReferralStatsResponse]
    user_rank: Optional[int]
    user_stats: Optional[ReferralStatsResponse]
    total_referrers: int

class ReferralAnalyticsResponse(BaseModel):
    total_referrals: int
    successful_referrals: int
    conversion_rate: float
    status_breakdown: Dict[str, int]
    monthly_trend: int
    total_earnings: Dict[str, Any]
    leaderboard_rank: Optional[int]

class ReferralRewardsResponse(BaseModel):
    total_rewards: int
    pending_rewards: int
    paid_rewards: int
    rewards_history: List[Dict[str, Any]]
    next_reward_threshold: Optional[int]

    class Config:
        from_attributes = True

class ReferralLeaderboardResponse(BaseModel):
    leaderboard: List[Dict[str, Any]]
    user_rank: Optional[int]
    total_participants: int

    class Config:
        from_attributes = True