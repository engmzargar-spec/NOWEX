from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config.base_config import settings

# ایجاد اتصال به دیتابیس - فقط اینجا
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# SessionLocal برای ایجاد sessionهای دیتابیس
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base برای مدل‌ها
Base = declarative_base()

# Metadata برای نام‌گذاری محدودیت‌ها
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base.metadata = MetaData(naming_convention=convention)

# Dependency برای گرفتن session دیتابیس
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# تابع برای ایجاد جداول
def create_tables():
    """ایجاد تمام جداول در دیتابیس"""
    try:
        # ایمپورت تمام مدل‌ها برای ثبت شدن در metadata
        from backend.apps.auth.models.user import User
        from backend.apps.kyc.models.kyc_models import UserProfile, KYCVerification, KYCDocument
        from backend.apps.scoring.models.scoring_models import UserScore, ScoreHistory, ScoreBenefits, UserBenefits, ScoringRules
        from backend.apps.referral.models.referral_models import ReferralProgram, ReferralRelationship, ReferralReward, ReferralCode, ReferralStats, ProgramConfiguration
        from backend.apps.admin.models.admin_user import AdminUser
        from backend.apps.finance.models.finance_models import PaymentGateway
        
        Base.metadata.create_all(bind=engine)
        print("✅ تمام جداول با موفقیت ایجاد شدند")
    except Exception as e:
        print(f"❌ خطا در ایجاد جداول: {e}")