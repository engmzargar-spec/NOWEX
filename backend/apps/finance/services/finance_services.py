from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from decimal import Decimal
import logging
from datetime import datetime, timedelta
from sqlalchemy import func

from backend.apps.finance.models.finance_models import (
    Wallet, WalletTransaction, DepositRequest, 
    WithdrawalRequest, RiskRule, SuspiciousActivity,
    PaymentGateway
)
from backend.apps.finance.schemas.finance_schemas import (
    WalletCreate, WalletUpdate, WalletTransactionCreate,
    DepositRequestCreate, WithdrawalRequestCreate,
    RiskRuleCreate, TransactionFilter
)

logger = logging.getLogger(__name__)

class WalletService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_wallet(self, wallet_data: WalletCreate) -> Wallet:
        """ایجاد کیف پول جدید برای کاربر"""
        db_wallet = Wallet(**wallet_data.dict())
        self.db.add(db_wallet)
        self.db.commit()
        self.db.refresh(db_wallet)
        return db_wallet
    
    def get_user_wallet(self, user_id: int) -> Optional[Wallet]:
        """دریافت کیف پول کاربر"""
        return self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
    
    def update_balance(self, wallet_id: int, amount: Decimal, transaction_type: str) -> Wallet:
        """به‌روزرسانی موجودی کیف پول"""
        wallet = self.db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise ValueError("Wallet not found")
        
        if transaction_type in ["deposit", "bonus"]:
            wallet.balance += amount
            wallet.available_balance += amount
        elif transaction_type in ["withdrawal", "fee"]:
            if wallet.available_balance < amount:
                raise ValueError("Insufficient balance")
            wallet.balance -= amount
            wallet.available_balance -= amount
        elif transaction_type == "freeze":
            if wallet.available_balance < amount:
                raise ValueError("Insufficient available balance")
            wallet.available_balance -= amount
            wallet.frozen_balance += amount
        elif transaction_type == "unfreeze":
            if wallet.frozen_balance < amount:
                raise ValueError("Insufficient frozen balance")
            wallet.frozen_balance -= amount
            wallet.available_balance += amount
        
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

class TransactionService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_transaction(self, transaction_data: WalletTransactionCreate) -> WalletTransaction:
        """ایجاد تراکنش جدید"""
        db_transaction = WalletTransaction(**transaction_data.dict())
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction
    
    def get_user_transactions(self, user_id: int, filters: TransactionFilter, 
                            skip: int = 0, limit: int = 100) -> List[WalletTransaction]:
        """دریافت تراکنش‌های کاربر با فیلتر"""
        query = self.db.query(WalletTransaction).join(Wallet).filter(Wallet.user_id == user_id)
        
        if filters.transaction_type:
            query = query.filter(WalletTransaction.transaction_type == filters.transaction_type)
        if filters.status:
            query = query.filter(WalletTransaction.status == filters.status)
        if filters.start_date:
            query = query.filter(WalletTransaction.created_at >= filters.start_date)
        if filters.end_date:
            query = query.filter(WalletTransaction.created_at <= filters.end_date)
        
        return query.offset(skip).limit(limit).all()
    
    def update_transaction_status(self, transaction_id: int, status: str, reference_id: str = None) -> WalletTransaction:
        """به‌روزرسانی وضعیت تراکنش"""
        transaction = self.db.query(WalletTransaction).filter(WalletTransaction.id == transaction_id).first()
        if not transaction:
            raise ValueError("Transaction not found")
        
        transaction.status = status
        if reference_id:
            transaction.reference_id = reference_id
        
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_all_transactions(self, filters: TransactionFilter, skip: int = 0, limit: int = 100):
        """دریافت تمام تراکنش‌ها (برای ادمین)"""
        from backend.apps.finance.models.finance_models import WalletTransaction, Wallet
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

class DepositService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_deposit_request(self, deposit_data: DepositRequestCreate) -> DepositRequest:
        """ایجاد درخواست واریز"""
        db_deposit = DepositRequest(**deposit_data.dict())
        self.db.add(db_deposit)
        self.db.commit()
        self.db.refresh(db_deposit)
        return db_deposit
    
    def process_deposit(self, deposit_id: int, gateway_response: Dict[str, Any]) -> DepositRequest:
        """پردازش واریز پس از بازگشت از درگاه"""
        deposit = self.db.query(DepositRequest).filter(DepositRequest.id == deposit_id).first()
        if not deposit:
            raise ValueError("Deposit request not found")
        
        deposit.gateway_response_data = gateway_response
        
        # اگر پرداخت موفق بود
        if gateway_response.get("status") == "success":
            deposit.status = "completed"
            deposit.verified_at = datetime.now()
            
            # افزایش موجودی کاربر
            wallet_service = WalletService(self.db)
            wallet_service.update_balance(
                wallet_id=deposit.user.wallet.id,
                amount=deposit.amount,
                transaction_type="deposit"
            )
            
            # ایجاد تراکنش
            transaction_service = TransactionService(self.db)
            transaction_service.create_transaction(WalletTransactionCreate(
                wallet_id=deposit.user.wallet.id,
                amount=deposit.amount,
                transaction_type="deposit",
                description=f"Deposit via {deposit.gateway.name}",
                transaction_metadata=gateway_response
            ))
        
        self.db.commit()
        self.db.refresh(deposit)
        return deposit

    def get_deposit_requests(self, status: str = None, skip: int = 0, limit: int = 100):
        """دریافت درخواست‌های واریز"""
        from backend.apps.finance.models.finance_models import DepositRequest
        query = self.db.query(DepositRequest)
        if status:
            query = query.filter(DepositRequest.status == status)
        return query.offset(skip).limit(limit).all()

class WithdrawalService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_withdrawal_request(self, withdrawal_data):
        from backend.apps.finance.models.finance_models import WithdrawalRequest
        db_withdrawal = WithdrawalRequest(**withdrawal_data.dict())
        self.db.add(db_withdrawal)
        self.db.commit()
        self.db.refresh(db_withdrawal)
        return db_withdrawal
    
    def get_withdrawal_requests(self, status: str = None, skip: int = 0, limit: int = 100):
        from backend.apps.finance.models.finance_models import WithdrawalRequest
        query = self.db.query(WithdrawalRequest)
        if status:
            query = query.filter(WithdrawalRequest.status == status)
        return query.offset(skip).limit(limit).all()
    
    def approve_withdrawal(self, withdrawal_id: int, admin_id: int):
        from backend.apps.finance.models.finance_models import WithdrawalRequest, Wallet
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
        from backend.apps.finance.models.finance_models import WithdrawalRequest, Wallet
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

class RiskManagementService:
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate_transaction_risk(self, user_id: int, amount: Decimal, transaction_type: str) -> Dict[str, Any]:
        """ارزیابی ریسک تراکنش"""
        risk_score = 0
        triggered_rules = []
        
        # دریافت قوانین فعال
        active_rules = self.db.query(RiskRule).filter(RiskRule.is_active == True).all()
        
        for rule in active_rules:
            # اجرای شرط ریسک (در حالت واقعی باید پارسر داشته باشیم)
            if self._evaluate_rule(rule, user_id, amount, transaction_type):
                risk_score += self._get_risk_score_by_severity(rule.severity)
                triggered_rules.append(rule.name)
        
        return {
            "risk_score": min(risk_score, 100),
            "triggered_rules": triggered_rules,
            "requires_verification": risk_score > 50,
            "should_block": risk_score > 80
        }
    
    def _evaluate_rule(self, rule: RiskRule, user_id: int, amount: Decimal, transaction_type: str) -> bool:
        """ارزیابی یک قانون ریسک (ساده شده)"""
        # در حالت واقعی اینجا باید یک پارسر شرط داشته باشیم
        try:
            if "amount >" in rule.condition:
                threshold = Decimal(rule.parameters.get("threshold", 1000000))
                return amount > threshold
            elif "new_user" in rule.condition:
                # چک کردن اینکه کاربر جدید هست یا نه
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    account_age = datetime.now() - user.created_at
                    return account_age.days < 7 and amount > Decimal(500000)
            return False
        except Exception as e:
            logger.error(f"Error evaluating risk rule {rule.name}: {e}")
            return False
    
    def _get_risk_score_by_severity(self, severity: str) -> int:
        """امتیاز ریسک بر اساس سطح شدت"""
        scores = {
            "low": 10,
            "medium": 25,
            "high": 50,
            "critical": 75
        }
        return scores.get(severity, 25)
    
    def create_suspicious_activity(self, activity_data: Dict[str, Any]) -> SuspiciousActivity:
        """ثبت فعالیت مشکوک"""
        db_activity = SuspiciousActivity(**activity_data)
        self.db.add(db_activity)
        self.db.commit()
        self.db.refresh(db_activity)
        return db_activity

class FinancialReportService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_financial_overview(self) -> Dict[str, Any]:
        """دریافت خلاصه وضعیت مالی"""
        total_balance = self.db.query(Wallet).with_entities(
            func.sum(Wallet.balance)
        ).scalar() or Decimal('0')
        
        total_deposits = self.db.query(WalletTransaction).filter(
            WalletTransaction.transaction_type == "deposit",
            WalletTransaction.status == "completed"
        ).with_entities(
            func.sum(WalletTransaction.amount)
        ).scalar() or Decimal('0')
        
        total_withdrawals = self.db.query(WalletTransaction).filter(
            WalletTransaction.transaction_type == "withdrawal",
            WalletTransaction.status == "completed"
        ).with_entities(
            func.sum(WalletTransaction.amount)
        ).scalar() or Decimal('0')
        
        active_users = self.db.query(Wallet).distinct(Wallet.user_id).count()
        
        pending_withdrawals = self.db.query(WithdrawalRequest).filter(
            WithdrawalRequest.status == "pending"
        ).with_entities(
            func.sum(WithdrawalRequest.amount)
        ).scalar() or Decimal('0')
        
        # حجم معاملات روزانه
        today = datetime.now().date()
        daily_volume = self.db.query(WalletTransaction).filter(
            func.date(WalletTransaction.created_at) == today
        ).with_entities(
            func.sum(WalletTransaction.amount)
        ).scalar() or Decimal('0')
        
        return {
            "total_balance": total_balance,
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "active_users": active_users,
            "pending_withdrawals": pending_withdrawals,
            "daily_transaction_volume": daily_volume
        }

# Import User model for risk evaluation
from backend.apps.auth.models.user import User