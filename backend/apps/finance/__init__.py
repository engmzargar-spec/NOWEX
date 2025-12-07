"""
NOWEX Finance Module
ماژول مدیریت مالی و کیف پول نواکس

این ماژول شامل:
- سیستم کیف پول کاربران
- مدیریت تراکنش‌های مالی
- درگاه‌های پرداخت
- سیستم مدیریت ریسک
- گزارش‌گیری مالی
"""

from fastapi import APIRouter
from .routes.finance_routes import router as finance_router

# ایجاد روتر اصلی برای ماژول مالی
router = APIRouter()
router.include_router(finance_router, prefix="/finance", tags=["Finance"])

# export مدل‌ها، اسکیماها و سرویس‌ها
from .models.finance_models import (
    Wallet,
    WalletTransaction, 
    DepositRequest,
    WithdrawalRequest,
    PaymentGateway,
    RiskRule,
    SuspiciousActivity,
    FinancialAuditLog
)

from .schemas.finance_schemas import (
    WalletResponse,
    WalletTransactionResponse,
    DepositRequestResponse, 
    WithdrawalRequestResponse,
    FinancialOverviewResponse,
    RiskRuleResponse,
    SuspiciousActivityResponse
)

from .services.finance_services import (
    WalletService,
    TransactionService,
    DepositService,
    WithdrawalService,
    RiskManagementService,
    FinancialReportService
)

__all__ = [
    # روترها
    "router",
    
    # مدل‌ها
    "Wallet",
    "WalletTransaction",
    "DepositRequest", 
    "WithdrawalRequest",
    "PaymentGateway",
    "RiskRule",
    "SuspiciousActivity",
    "FinancialAuditLog",
    
    # اسکیماها
    "WalletResponse",
    "WalletTransactionResponse",
    "DepositRequestResponse",
    "WithdrawalRequestResponse", 
    "FinancialOverviewResponse",
    "RiskRuleResponse",
    "SuspiciousActivityResponse",
    
    # سرویس‌ها
    "WalletService",
    "TransactionService",
    "DepositService",
    "WithdrawalService", 
    "RiskManagementService",
    "FinancialReportService"
]

__version__ = "1.0.0"
__author__ = "NOWEX Team"