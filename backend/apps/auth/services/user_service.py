from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import Optional

from backend.apps.auth.models.user import User  # ✅ اصلاح شد
from backend.apps.auth.schemas.user_schema import UserCreate  # ✅ اصلاح شد
from backend.core.security.password import get_password_hash, verify_password  # ✅ اصلاح شد

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """ایجاد کاربر جدید"""
        try:
            # بررسی وجود کاربر با این ایمیل
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # بررسی وجود کاربر با این username
            existing_username = db.query(User).filter(User.username == user_data.username).first()
            if existing_username:
                raise ValueError("Username already taken")
            
            # ایجاد کاربر جدید
            hashed_password = get_password_hash(user_data.password)
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone_number=user_data.phone_number,
                is_active=True  # ✅ برای تست فعال می‌کنیم
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
            
        except IntegrityError:
            db.rollback()
            raise ValueError("User creation failed due to integrity error")
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """احراز هویت کاربر"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """دریافت کاربر بر اساس ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """دریافت کاربر بر اساس ایمیل"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_last_login(db: Session, user_id: UUID):
        """آپدیت زمان آخرین لاگین"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            from sqlalchemy import func
            user.last_login = func.now()
            db.commit()

user_service = UserService()