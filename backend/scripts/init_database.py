import sys
import os

# اضافه کردن مسیر پروژه به sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from core.database.base import Base
from apps.admin.models.admin_user import AdminUser
from apps.admin.models.admin_role import AdminRole
from apps.admin.models.admin_permission import AdminPermission
from apps.admin.models.admin_audit_log import AdminAuditLog

def init_database():
    """Initialize database with all tables"""
    from core.config.base_config import Settings
    settings = Settings()
    
    print(f"Connecting to database: {settings.DATABASE_URL}")
    
    # ایجاد موتور
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # ایجاد تمام جداول
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    init_database()