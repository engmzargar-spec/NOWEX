from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

# Base Schemas
class WalletBase(BaseModel):
    balance: Decimal
    available_balance: Decimal
    frozen_balance: Decimal
    currency: str = "IRT"
    status: str = "active"

class WalletCreate(WalletBase):
    user_id: int

class WalletUpdate(BaseModel):
    balance: Optional[Decimal] = None
    available_balance: Optional[Decimal] = None
    frozen_balance: Optional[Decimal] = None
    status: Optional[str] = None

class WalletResponse(WalletBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Transaction Schemas
class WalletTransactionBase(BaseModel):
    amount: Decimal
    transaction_type: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class WalletTransactionCreate(WalletTransactionBase):
    wallet_id: int

class WalletTransactionUpdate(BaseModel):
    status: Optional[str] = None
    reference_id: Optional[str] = None

class WalletTransactionResponse(WalletTransactionBase):
    id: int
    wallet_id: int
    status: str
    reference_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Deposit Schemas
class DepositRequestBase(BaseModel):
    amount: Decimal
    gateway_id: int

class DepositRequestCreate(DepositRequestBase):
    user_id: int

class DepositRequestUpdate(BaseModel):
    status: Optional[str] = None
    payment_reference: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    verified_at: Optional[datetime] = None

class DepositRequestResponse(DepositRequestBase):
    id: int
    user_id: int
    payment_reference: Optional[str]
    status: str
    gateway_response: Optional[Dict[str, Any]]
    verified_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# Withdrawal Schemas
class WithdrawalRequestBase(BaseModel):
    amount: Decimal
    destination_type: str
    destination_data: Dict[str, Any]

class WithdrawalRequestCreate(WithdrawalRequestBase):
    user_id: int

class WithdrawalRequestUpdate(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None

class WithdrawalRequestResponse(WithdrawalRequestBase):
    id: int
    user_id: int
    status: str
    admin_notes: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# Risk Management Schemas
class RiskRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    condition: str
    action: str
    severity: str = "medium"
    parameters: Optional[Dict[str, Any]] = None

class RiskRuleCreate(RiskRuleBase):
    pass

class RiskRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[str] = None
    action: Optional[str] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None

class RiskRuleResponse(RiskRuleBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SuspiciousActivityBase(BaseModel):
    activity_type: str
    risk_score: int
    triggered_rules: List[str]
    investigation_notes: Optional[str] = None

class SuspiciousActivityCreate(SuspiciousActivityBase):
    user_id: int

class SuspiciousActivityUpdate(BaseModel):
    status: Optional[str] = None
    investigation_notes: Optional[str] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None

class SuspiciousActivityResponse(SuspiciousActivityBase):
    id: int
    user_id: int
    status: str
    resolved_by: Optional[int]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# Financial Overview Schemas
class FinancialOverviewResponse(BaseModel):
    total_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    active_users: int
    pending_withdrawals: Decimal
    daily_transaction_volume: Decimal

# Pagination and Filter Schemas
class TransactionFilter(BaseModel):
    user_id: Optional[int] = None
    transaction_type: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int