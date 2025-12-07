import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models.models import User, UserScore, ScoreHistory

logger = logging.getLogger("seed_tester")

def run_seed_tester():
    db: Session = SessionLocal()
    try:
        # شناسه کاربر تستی
        user_id = "bf76777a-62a4-4008-9734-5ff57868e9cd"

        # بررسی وجود کاربر تستی
        test_user = db.query(User).filter(User.id == user_id).first()
        if not test_user:
            logger.info("⚠️ کاربر تستی وجود ندارد، ایجاد می‌شود...")
            new_user = User(
                id=user_id,
                username="testuser4",
                email="testuser4@example.com",
                hashed_password="testpassword",  # در محیط واقعی باید هش شود
                is_active=True
            )
            db.add(new_user)
            db.commit()
            logger.info("✅ کاربر تستی ایجاد شد.")
        else:
            logger.info("✅ کاربر تستی وجود دارد.")

        # آخرین امتیاز از جدول score_history
        latest_score = db.query(func.max(ScoreHistory.new_total_score))\
                         .filter(ScoreHistory.user_id == user_id).scalar()

        if latest_score is None:
            logger.info("⚠️ هیچ رکوردی در score_history برای این کاربر وجود ندارد.")
            return

        # مقدار موجود در user_scores
        user_score = db.query(UserScore).filter(UserScore.user_id == user_id).first()

        if user_score:
            if user_score.total_score != latest_score:
                logger.info(f"🔧 اصلاح total_score از {user_score.total_score} به {latest_score}")
                user_score.total_score = latest_score
                db.commit()
            else:
                logger.info("✅ total_score هماهنگ است.")
        else:
            logger.info("⚠️ هیچ رکوردی در user_scores برای این کاربر وجود ندارد.")

    except Exception as e:
        logger.error(f"❌ خطا در اجرای تست: {e}")
    finally:
        db.close()
