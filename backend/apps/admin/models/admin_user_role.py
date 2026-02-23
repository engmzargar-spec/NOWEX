# backend/apps/admin/models/admin_user_role.py

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.core.database.base import Base


class AdminUserRole(Base):
    __tablename__ = "admin_user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("admin_users.id", ondelete="CASCADE"))
    role_id = Column(Integer, ForeignKey("admin_roles.id", ondelete="CASCADE"))

    # روابط
    user = relationship("AdminUser", back_populates="roles")
    role = relationship("AdminRole")
