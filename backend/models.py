from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Table, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# Config from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "nowex_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "Mezr@1360")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "nowex_development")

# URL encode the password to handle special characters
import urllib.parse
encoded_password = urllib.parse.quote_plus(POSTGRES_PASSWORD)

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ایجاد engine برای دیتابیس
engine = create_engine(DATABASE_URL)

# جدول واسط برای رابطه چند-به-چند بین کاربران و نقش‌ها
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID, ForeignKey('admin_users.id')),
    Column('role_id', UUID, ForeignKey('admin_roles.id'))
)

# جدول واسط برای رابطه چند-به-چند بین نقش‌ها و دسترسی‌ها
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID, ForeignKey('admin_roles.id')),
    Column('permission_id', UUID, ForeignKey('permissions.id'))
)

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(UUID, primary_key=True, default=generate_uuid, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # روابط
    roles = relationship("AdminRole", secondary=user_roles, back_populates="users")

class AdminRole(Base):
    __tablename__ = "admin_roles"

    id = Column(UUID, primary_key=True, default=generate_uuid, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    users = relationship("AdminUser", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID, primary_key=True, default=generate_uuid, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    module = Column(String(50))  # مثلاً: user_management, content_management
    action = Column(String(50))  # مثلاً: create, read, update, delete
    created_at = Column(DateTime, default=datetime.utcnow)

    # روابط
    roles = relationship("AdminRole", secondary=role_permissions, back_populates="permissions")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(UUID, ForeignKey('admin_users.id'), nullable=True)
    action = Column(String(100), nullable=False)  # مثلاً: login, create_user, delete_post
    resource_type = Column(String(50))  # مثلاً: user, post, role
    resource_id = Column(UUID, nullable=True)  # ID منبع مورد عمل
    ip_address = Column(String(45))  # برای IPv6
    user_agent = Column(Text)
    details = Column(Text)  # جزئیات اضافی در فرمت JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # رابطه
    user = relationship("AdminUser")