from enum import Enum
from typing import Dict, List
from sqlalchemy import Column, String, JSON, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class KYCStateMachine:
    """
    State Machine برای مدیریت وضعیت‌های KYC
    """
    
    class States(Enum):
        DRAFT = "draft"
        SUBMITTED = "submitted"
        UNDER_REVIEW = "under_review"
        APPROVED = "approved"
        REJECTED = "rejected"
        EXPIRED = "expired"
        SUSPENDED = "suspended"
    
    class Transitions(Enum):
        SUBMIT = "submit"
        ASSIGN_REVIEWER = "assign_reviewer"
        APPROVE = "approve"
        REJECT = "reject"
        RESUBMIT = "resubmit"
        EXPIRE = "expire"
        SUSPEND = "suspend"
        REACTIVATE = "reactivate"
    
    # تعریف انتقال‌های مجاز
    TRANSITIONS: Dict[States, List[Transitions]] = {
        States.DRAFT: [Transitions.SUBMIT],
        States.SUBMITTED: [Transitions.ASSIGN_REVIEWER, Transitions.REJECT],
        States.UNDER_REVIEW: [Transitions.APPROVE, Transitions.REJECT, Transitions.SUSPEND],
        States.APPROVED: [Transitions.EXPIRE, Transitions.SUSPEND],
        States.REJECTED: [Transitions.RESUBMIT],
        States.EXPIRED: [Transitions.RESUBMIT],
        States.SUSPENDED: [Transitions.REACTIVATE, Transitions.REJECT]
    }
    
    # نقشه انتقال‌ها
    TRANSITION_MAP: Dict[Transitions, Dict[str, States]] = {
        Transitions.SUBMIT: {"from": [States.DRAFT], "to": States.SUBMITTED},
        Transitions.ASSIGN_REVIEWER: {"from": [States.SUBMITTED], "to": States.UNDER_REVIEW},
        Transitions.APPROVE: {"from": [States.UNDER_REVIEW], "to": States.APPROVED},
        Transitions.REJECT: {"from": [States.SUBMITTED, States.UNDER_REVIEW, States.SUSPENDED], "to": States.REJECTED},
        Transitions.RESUBMIT: {"from": [States.REJECTED, States.EXPIRED], "to": States.DRAFT},
        Transitions.EXPIRE: {"from": [States.APPROVED], "to": States.EXPIRED},
        Transitions.SUSPEND: {"from": [States.UNDER_REVIEW, States.APPROVED], "to": States.SUSPENDED},
        Transitions.REACTIVATE: {"from": [States.SUSPENDED], "to": States.UNDER_REVIEW}
    }
    
    @classmethod
    def can_transition(cls, current_state: States, transition: Transitions) -> bool:
        """بررسی امکان انتقال از وضعیت فعلی"""
        if current_state not in cls.TRANSITIONS:
            return False
        return transition in cls.TRANSITIONS[current_state]
    
    @classmethod
    def get_next_state(cls, current_state: States, transition: Transitions) -> States:
        """دریافت وضعیت بعدی بر اساس انتقال"""
        if not cls.can_transition(current_state, transition):
            raise ValueError(f"Invalid transition {transition} from state {current_state}")
        
        return cls.TRANSITION_MAP[transition]["to"]
    
    @classmethod
    def get_available_transitions(cls, current_state: States) -> List[Transitions]:
        """دریافت لیست انتقال‌های ممکن از وضعیت فعلی"""
        return cls.TRANSITIONS.get(current_state, [])

class KYCStateHistory(Base):
    __tablename__ = "kyc_state_history"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=False)
    from_state = Column(String(50), nullable=False)
    to_state = Column(String(50), nullable=False)
    transition = Column(String(50), nullable=False)
    reason = Column(String(500))
    meta_info = Column(JSON)  # تغییر نام از metadata به meta_info
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id: str, from_state: str, to_state: str, transition: str, 
                 reason: str = None, meta_info: dict = None):
        self.id = f"{user_id}_{int(datetime.utcnow().timestamp())}"
        self.user_id = user_id
        self.from_state = from_state
        self.to_state = to_state
        self.transition = transition
        self.reason = reason
        self.meta_info = meta_info or {}