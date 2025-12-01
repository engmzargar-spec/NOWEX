from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import uuid
from datetime import datetime

from backend.apps.admin.models.admin_user import AdminUser  # تغییر به absolute import
from backend.core.security.password import get_password_hash  # تغییر به absolute import
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AdminUserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_admin_by_username(self, username: str):
        return self.db.query(AdminUser).filter(AdminUser.username == username).first()
    
    def authenticate_admin(self, username: str, password: str):
        admin = self.get_admin_by_username(username)
        if not admin or not pwd_context.verify(password, admin.hashed_password):
            return None
        return admin
    
    def update_last_login(self, admin_id: str):
        admin = self.db.query(AdminUser).filter(AdminUser.id == admin_id).first()
        if admin:
            admin.last_login = datetime.utcnow()
            self.db.commit()

    # 🔥 متدهای جدید برای مدیریت کاربران
    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[AdminUser]:
        """دریافت لیست کاربران ادمین با فیلتر و صفحه‌بندی"""
        query = self.db.query(AdminUser)
        
        # اعمال فیلتر جستجو
        if search:
            query = query.filter(
                or_(
                    AdminUser.username.ilike(f"%{search}%"),
                    AdminUser.email.ilike(f"%{search}%"),
                    AdminUser.full_name.ilike(f"%{search}%")
                )
            )
        
        # اعمال فیلتر نقش
        if role:
            query = query.filter(AdminUser.role == role)
            
        # اعمال فیلتر وضعیت فعال
        if is_active is not None:
            query = query.filter(AdminUser.is_active == is_active)
        
        # اعمال صفحه‌بندی و مرتب‌سازی
        return query.order_by(AdminUser.created_at.desc()).offset(skip).limit(limit).all()

    def get_user_by_id(self, user_id: str) -> Optional[AdminUser]:
        """دریافت کاربر ادمین بر اساس ID"""
        return self.db.query(AdminUser).filter(AdminUser.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[AdminUser]:
        """دریافت کاربر ادمین بر اساس ایمیل"""
        return self.db.query(AdminUser).filter(AdminUser.email == email).first()

    def create_user(self, user_data) -> AdminUser:
        """ایجاد کاربر ادمین جدید"""
        # بررسی تکراری نبودن نام کاربری و ایمیل
        if self.get_admin_by_username(user_data.username):
            raise ValueError("نام کاربری از قبل وجود دارد")
            
        if self.get_user_by_email(user_data.email):
            raise ValueError("ایمیل از قبل وجود دارد")
        
        # هش کردن رمز عبور
        hashed_password = get_password_hash(user_data.password)
        
        # ایجاد کاربر جدید
        db_user = AdminUser(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def update_user(self, user_id: str, user_data) -> Optional[AdminUser]:
        """بروزرسانی کاربر ادمین"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        # بروزرسانی فیلدها
        update_data = user_data.dict(exclude_unset=True)
        
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            if hasattr(db_user, field) and field != "id":
                setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def delete_user(self, user_id: str) -> bool:
        """حذف کاربر ادمین"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        
        return True

    def count_users(self) -> int:
        """شمردن تعداد کل کاربران ادمین"""
        return self.db.query(AdminUser).count()