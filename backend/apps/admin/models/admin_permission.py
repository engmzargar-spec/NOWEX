# backend/apps/admin/models/admin_permission.py
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from datetime import datetime
from core.database.base import Base

class AdminPermission(Base):
    __tablename__ = "admin_permissions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AdminPermission(name={self.name}, category={self.category})>"