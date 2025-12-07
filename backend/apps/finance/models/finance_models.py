from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, ForeignKey, Text, JSON, Numeric, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database.base import Base

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), unique=True, index=True, nullable=False)  # تغییر به UUID
    balance = Column(DECIMAL(20, 8), default=0.0, nullable=False)
    available_balance = Column(DECIMAL(20, 8), default=0.0, nullable=False)
    frozen_balance = Column(DECIMAL(20, 8), default=0.0, nullable=False)
    currency = Column(String(10), default="IRT", nullable=False)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship("WalletTransaction", back_populates="wallet")

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False, index=True)
    amount = Column(DECIMAL(20, 8), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    reference_id = Column(String(100), unique=True, index=True)
    description = Column(Text)
    transaction_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")

class PaymentGateway(Base):
    __tablename__ = "payment_gateways"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    gateway_config = Column(JSON)
    supported_currencies = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DepositRequest(Base):
    __tablename__ = "deposit_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)  # تغییر به UUID
    amount = Column(DECIMAL(20, 8), nullable=False)
    gateway_id = Column(Integer, ForeignKey("payment_gateways.id"), nullable=False)
    payment_reference = Column(String(100), unique=True, index=True)
    status = Column(String(20), default="pending", nullable=False)
    gateway_response_data = Column(JSON)
    verified_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    gateway = relationship("PaymentGateway")

class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)  # تغییر به UUID
    amount = Column(DECIMAL(20, 8), nullable=False)
    destination_type = Column(String(50), nullable=False)
    destination_data = Column(JSON)
    status = Column(String(20), default="pending", nullable=False)
    admin_notes = Column(Text)
    approved_by = Column(Integer, ForeignKey("admin_users.id"))
    approved_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    admin_approver = relationship("AdminUser")

class RiskRule(Base):
    __tablename__ = "risk_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    condition = Column(Text, nullable=False)
    action = Column(String(50), nullable=False)
    severity = Column(String(20), default="medium", nullable=False)
    is_active = Column(Boolean, default=True)
    parameters = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SuspiciousActivity(Base):
    __tablename__ = "suspicious_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), index=True)  # تغییر به UUID
    activity_type = Column(String(100), nullable=False)
    risk_score = Column(Integer, default=0, nullable=False)
    triggered_rules = Column(JSON)
    status = Column(String(20), default="investigating", nullable=False)
    investigation_notes = Column(Text)
    resolved_by = Column(Integer, ForeignKey("admin_users.id"))
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    resolver = relationship("AdminUser")

class FinancialAuditLog(Base):
    __tablename__ = "financial_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), index=True)  # تغییر به UUID
    admin_id = Column(Integer, ForeignKey("admin_users.id"))
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    admin = relationship("AdminUser")

# برای رابطه با مدل User موجود
from backend.apps.auth.models.user import User

# اضافه کردن رابطه به مدل User
if not hasattr(User, 'wallet'):
    User.wallet = relationship("Wallet", back_populates="user", uselist=False)