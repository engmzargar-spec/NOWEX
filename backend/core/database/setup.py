import os
from sqlalchemy import text
from backend.core.database.base import engine
from backend.models import Base

def setup_database():
    try:
        # ایجاد جداول اگر وجود ندارند
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")

        # مسیر درست به فایل seed (بدون backend)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        seed_file = os.path.join(project_root, "database", "seeds", "seed_data.sql")
        print(f"📍 Looking for seed file at: {seed_file}")

        if os.path.exists(seed_file):
            with engine.connect() as conn:
                with open(seed_file, "r", encoding="utf-8") as f:
                    sql_commands = f.read()
                    try:
                        conn.execute(text(sql_commands))
                        conn.commit()
                        print("✅ Seed data executed successfully.")
                    except Exception as e:
                        print(f"⚠️ Seed execution skipped: {e}")
        else:
            print(f"⚠️ Seed file not found at {seed_file}")

    except Exception as e:
        print(f"❌ Database setup error: {e}")
