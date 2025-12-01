from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.core.database.base import get_db
from backend.core.security.auth import get_current_admin_user, get_current_user
from backend.apps.admin.models.admin_user import AdminUser
from backend.apps.auth.models.user import User

from backend.apps.finance.services import (
    WalletService, TransactionService, DepositService,
    RiskManagementService, FinancialReportService
)
from backend.apps.finance.schemas import (
    WalletResponse, WalletTransactionResponse, DepositRequestResponse,
    WithdrawalRequestResponse, FinancialOverviewResponse, TransactionFilter,
    PaginatedResponse, DepositRequestCreate, WithdrawalRequestCreate
)

# 🔧 اصلاح شده: حذف prefix از اینجا
router = APIRouter(tags=["Finance"])

# User Routes
@router.get("/wallet/balance", response_model=WalletResponse)
async def get_wallet_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت موجودی کیف پول کاربر"""
    wallet_service = WalletService(db)
    wallet = wallet_service.get_user_wallet(current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    return wallet

@router.get("/wallet/transactions", response_model=List[WalletTransactionResponse])
async def get_wallet_transactions(
    transaction_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت تاریخچه تراکنش‌های کاربر"""
    transaction_service = TransactionService(db)
    
    filters = TransactionFilter(
        transaction_type=transaction_type,
        status=status
    )
    
    transactions = transaction_service.get_user_transactions(
        user_id=current_user.id,
        filters=filters,
        skip=skip,
        limit=limit
    )
    return transactions

@router.post("/deposit/request", response_model=DepositRequestResponse)
async def create_deposit_request(
    deposit_data: DepositRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ایجاد درخواست واریز"""
    deposit_service = DepositService(db)
    
    # ارزیابی ریسک
    risk_service = RiskManagementService(db)
    risk_assessment = risk_service.evaluate_transaction_risk(
        user_id=current_user.id,
        amount=deposit_data.amount,
        transaction_type="deposit"
    )
    
    if risk_assessment["should_block"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Transaction blocked due to high risk"
        )
    
    # ایجاد درخواست واریز
    deposit_data.user_id = current_user.id
    deposit_request = deposit_service.create_deposit_request(deposit_data)
    
    # اگر ریسک بالا بود، ثبت فعالیت مشکوک
    if risk_assessment["risk_score"] > 60:
        risk_service.create_suspicious_activity({
            "user_id": current_user.id,
            "activity_type": "high_risk_deposit",
            "risk_score": risk_assessment["risk_score"],
            "triggered_rules": risk_assessment["triggered_rules"]
        })
    
    return deposit_request

@router.post("/withdrawal/request", response_model=WithdrawalRequestResponse)
async def create_withdrawal_request(
    withdrawal_data: WithdrawalRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ایجاد درخواست برداشت"""
    wallet_service = WalletService(db)
    risk_service = RiskManagementService(db)
    
    # بررسی موجودی
    wallet = wallet_service.get_user_wallet(current_user.id)
    if not wallet or wallet.available_balance < withdrawal_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # ارزیابی ریسک
    risk_assessment = risk_service.evaluate_transaction_risk(
        user_id=current_user.id,
        amount=withdrawal_data.amount,
        transaction_type="withdrawal"
    )
    
    if risk_assessment["should_block"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Transaction blocked due to high risk"
        )
    
    # ایجاد درخواست برداشت
    withdrawal_data.user_id = current_user.id
    withdrawal_service = WithdrawalService(db)
    withdrawal_request = withdrawal_service.create_withdrawal_request(withdrawal_data)
    
    # مسدود کردن مبلغ برداشت
    wallet_service.update_balance(
        wallet_id=wallet.id,
        amount=withdrawal_data.amount,
        transaction_type="freeze"
    )
    
    return withdrawal_request

# Admin Routes
@router.get("/admin/financial/overview", response_model=FinancialOverviewResponse)
async def get_financial_overview(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """دریافت خلاصه وضعیت مالی (ادمین)"""
    report_service = FinancialReportService(db)
    overview = report_service.get_financial_overview()
    return overview

@router.get("/admin/transactions", response_model=List[WalletTransactionResponse])
async def get_all_transactions(
    user_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """دریافت تمام تراکنش‌ها (ادمین)"""
    transaction_service = TransactionService(db)
    
    filters = TransactionFilter(
        user_id=user_id,
        transaction_type=transaction_type,
        status=status
    )
    
    # برای ادمین، اگر user_id مشخص نشده باشد، همه تراکنش‌ها برگردانده می‌شود
    transactions = transaction_service.get_all_transactions(
        filters=filters,
        skip=skip,
        limit=limit
    )
    return transactions

@router.get("/admin/deposit-requests", response_model=List[DepositRequestResponse])
async def get_deposit_requests(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """دریافت درخواست‌های واریز (ادمین)"""
    deposit_service = DepositService(db)
    deposits = deposit_service.get_deposit_requests(
        status=status,
        skip=skip,
        limit=limit
    )
    return deposits

@router.get("/admin/withdrawal-requests", response_model=List[WithdrawalRequestResponse])
async def get_withdrawal_requests(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """دریافت درخواست‌های برداشت (ادمین)"""
    withdrawal_service = WithdrawalService(db)
    withdrawals = withdrawal_service.get_withdrawal_requests(
        status=status,
        skip=skip,
        limit=limit
    )
    return withdrawals

@router.post("/admin/withdrawal-requests/{withdrawal_id}/approve")
async def approve_withdrawal_request(
    withdrawal_id: int,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """تأیید درخواست برداشت (ادمین)"""
    withdrawal_service = WithdrawalService(db)
    
    try:
        withdrawal = withdrawal_service.approve_withdrawal(
            withdrawal_id=withdrawal_id,
            admin_id=current_admin.id
        )
        return {"message": "Withdrawal approved successfully", "withdrawal": withdrawal}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/admin/withdrawal-requests/{withdrawal_id}/reject")
async def reject_withdrawal_request(
    withdrawal_id: int,
    reason: str,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """رد درخواست برداشت (ادمین)"""
    withdrawal_service = WithdrawalService(db)
    
    try:
        withdrawal = withdrawal_service.reject_withdrawal(
            withdrawal_id=withdrawal_id,
            admin_id=current_admin.id,
            reason=reason
        )
        return {"message": "Withdrawal rejected successfully", "withdrawal": withdrawal}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# اضافه کردن سرویس‌های تکمیلی
class WithdrawalService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_withdrawal_request(self, withdrawal_data: WithdrawalRequestCreate):
        from backend.apps.finance.models import WithdrawalRequest
        db_withdrawal = WithdrawalRequest(**withdrawal_data.dict())
        self.db.add(db_withdrawal)
        self.db.commit()
        self.db.refresh(db_withdrawal)
        return db_withdrawal
    
    def get_withdrawal_requests(self, status: str = None, skip: int = 0, limit: int = 100):
        from backend.apps.finance.models import WithdrawalRequest
        query = self.db.query(WithdrawalRequest)
        if status:
            query = query.filter(WithdrawalRequest.status == status)
        return query.offset(skip).limit(limit).all()
    
    def approve_withdrawal(self, withdrawal_id: int, admin_id: int):
        from backend.apps.finance.models import WithdrawalRequest, Wallet
        withdrawal = self.db.query(WithdrawalRequest).filter(WithdrawalRequest.id == withdrawal_id).first()
        if not withdrawal:
            raise ValueError("Withdrawal request not found")
        
        if withdrawal.status != "pending":
            raise ValueError("Withdrawal request is not in pending status")
        
        # کاهش موجودی کاربر
        wallet = self.db.query(Wallet).filter(Wallet.user_id == withdrawal.user_id).first()
        if wallet:
            wallet.frozen_balance -= withdrawal.amount
            wallet.balance -= withdrawal.amount
        
        withdrawal.status = "approved"
        withdrawal.approved_by = admin_id
        withdrawal.approved_at = datetime.now()
        
        self.db.commit()
        return withdrawal
    
    def reject_withdrawal(self, withdrawal_id: int, admin_id: int, reason: str):
        from backend.apps.finance.models import WithdrawalRequest, Wallet
        withdrawal = self.db.query(WithdrawalRequest).filter(WithdrawalRequest.id == withdrawal_id).first()
        if not withdrawal:
            raise ValueError("Withdrawal request not found")
        
        if withdrawal.status != "pending":
            raise ValueError("Withdrawal request is not in pending status")
        
        # آزاد کردن مبلغ مسدود شده
        wallet = self.db.query(Wallet).filter(Wallet.user_id == withdrawal.user_id).first()
        if wallet:
            wallet.frozen_balance -= withdrawal.amount
            wallet.available_balance += withdrawal.amount
        
        withdrawal.status = "rejected"
        withdrawal.admin_notes = reason
        withdrawal.approved_by = admin_id
        withdrawal.approved_at = datetime.now()
        
        self.db.commit()
        return withdrawal

# برای تابع get_all_transactions در TransactionService
def get_all_transactions(self, filters: TransactionFilter, skip: int = 0, limit: int = 100):
    from backend.apps.finance.models import WalletTransaction, Wallet
    query = self.db.query(WalletTransaction).join(Wallet)
    
    if filters.user_id:
        query = query.filter(Wallet.user_id == filters.user_id)
    if filters.transaction_type:
        query = query.filter(WalletTransaction.transaction_type == filters.transaction_type)
    if filters.status:
        query = query.filter(WalletTransaction.status == filters.status)
    if filters.start_date:
        query = query.filter(WalletTransaction.created_at >= filters.start_date)
    if filters.end_date:
        query = query.filter(WalletTransaction.created_at <= filters.end_date)
    
    return query.offset(skip).limit(limit).all()

# اضافه کردن به TransactionService
TransactionService.get_all_transactions = get_all_transactions

# برای تابع get_deposit_requests در DepositService
def get_deposit_requests(self, status: str = None, skip: int = 0, limit: int = 100):
    from backend.apps.finance.models import DepositRequest
    query = self.db.query(DepositRequest)
    if status:
        query = query.filter(DepositRequest.status == status)
    return query.offset(skip).limit(limit).all()

DepositService.get_deposit_requests = get_deposit_requests