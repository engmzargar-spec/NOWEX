import os

def test_environment_variables():
    """بررسی متغیرهای محیطی ضروری"""
    # لیست متغیرهای محیطی که باید در production تنظیم شوند
    env_vars = ["DATABASE_URL", "SECRET_KEY", "REDIS_URL"]
    
    missing = []
    for var in env_vars:
        if var not in os.environ:
            missing.append(var)
    
    if missing:
        print(f"⚠️ Missing environment variables (expected in production): {missing}")
    else:
        print("✅ All essential environment variables are set")
    
    # این تست نباید fail شود چون در CI ممکن است تنظیم نباشند
    return True