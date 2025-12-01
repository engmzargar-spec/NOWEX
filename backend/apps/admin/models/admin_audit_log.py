# backend/apps/admin/models/admin_audit_log.py
from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import JSON  # ✅ اضافه کردن این خط
from datetime import datetime
from core.database.base import Base

class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_user_id = Column(Integer, nullable=False, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)  # ✅ حالا JSON تعریف شده
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AdminAuditLog(admin={self.admin_user_id}, action={self.action})>"