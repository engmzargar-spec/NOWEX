# backend/create_users_simple.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apps.admin.models.admin_user import AdminUser  # 🔥 استفاده از مدل جدید
from core.security.password import get_password_hash
import uuid
from datetime import datetime

def create_users():
    # استفاده از DATABASE_URL از main.py
    DATABASE_URL = "postgresql://nowex_user:Mezr%401360@localhost:5432/nowex_development"
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔗 Creating test users...")
        
        # کاربر ادمین
        admin_user = AdminUser(
            id=uuid.uuid4(),
            username="admin",
            email="admin@nowex.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role="super_admin",  # 🔥 استفاده از role به جای is_superuser
            is_active=True
        )
        db.add(admin_user)
        
        # کاربر معمولی
        user = AdminUser(
            id=uuid.uuid4(),
            username="user",
            email="user@nowex.com", 
            full_name="Regular User",
            hashed_password=get_password_hash("user123"),
            role="support_agent",  # 🔥 استفاده از role
            is_active=True
        )
        db.add(user)
        
        db.commit()
        print("✅ Users created successfully!")
        print("   admin / admin123 (super_admin)")
        print("   user / user123 (support_agent)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_users()