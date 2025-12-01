import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from apps.admin.models.admin_user import AdminUser  # 🔧 استفاده از مدل جدید
from passlib.context import CryptContext
import urllib.parse

# Config - استفاده از localhost
POSTGRES_USER = "nowex_user"
POSTGRES_PASSWORD = "Mezr@1360"
POSTGRES_SERVER = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "nowex_development"

# URL encode the password
encoded_password = urllib.parse.quote_plus(POSTGRES_PASSWORD)
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ایجاد engine جدید
engine = create_engine(DATABASE_URL)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users():
    # ایجاد session با engine جدید
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔗 در حال اتصال به دیتابیس...")
        
        # ایجاد کاربر ادمین پیش‌فرض
        existing_admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not existing_admin:
            admin_user = AdminUser(
                username="admin",
                email="admin@nowex.com",
                full_name="System Administrator",
                hashed_password=pwd_context.hash("admin123"),
                role="super_admin",  # 🔧 مطابق با مدل جدید
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ کاربر ادمین ایجاد شد: admin / admin123")
        else:
            print("⚠️  کاربر ادمین از قبل وجود دارد")
        
        # ایجاد کاربر معمولی
        existing_user = db.query(AdminUser).filter(AdminUser.username == "user").first()
        if not existing_user:
            user = AdminUser(
                username="user",
                email="user@nowex.com", 
                full_name="Regular User",
                hashed_password=pwd_context.hash("user123"),
                role="user",  # 🔧 مطابق با مدل جدید
                is_active=True
            )
            db.add(user)
            db.commit()
            print("✅ کاربر معمولی ایجاد شد: user / user123")
        else:
            print("⚠️  کاربر معمولی از قبل وجود دارد")
            
        print("🎯 کاربران تستی آماده هستند!")
        
    except Exception as e:
        print(f"❌ خطا در ایجاد کاربران: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()