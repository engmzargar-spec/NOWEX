import logging
import os
import sys

# 🔧 افزایش سطح لاگ برای دیدن خطاهای دقیق
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("main")

# اضافه کردن مسیر root پروژه به sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # پوشه NOWEX-Platform
sys.path.insert(0, project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 🔧 ایمپورت Error Handler
try:
    from backend.core.middleware.error_handler import setup_exception_handlers
    logger.info("✅ Error handler imported successfully")
except ImportError as e:
    logger.error(f"❌ Error handler import failed: {e}")

# 🔧 تنظیم سطح لاگ برای ماژول‌های مشکل‌دار
logging.getLogger("backend.apps.scoring").setLevel(logging.DEBUG)
logging.getLogger("backend.apps.referral").setLevel(logging.DEBUG)
logging.getLogger("backend.apps.scoring.services").setLevel(logging.DEBUG)
logging.getLogger("backend.apps.referral.services").setLevel(logging.DEBUG)

# ساخت اپلیکیشن FastAPI
app = FastAPI(
    title="NOWEX Backend",
    description="پلتفرم معاملاتی نواکس",
    version="1.0.0",
    debug=True  # 🔧 فعال کردن حالت debug برای خطاهای دقیق‌تر
)

# 🔧 راه‌اندازی Error Handler مرکزی
try:
    setup_exception_handlers(app)
    logger.info("✅ Centralized error handling activated")
except Exception as e:
    logger.error(f"❌ Error handler setup failed: {e}")

# فعال‌سازی CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ایمپورت‌های دیتابیس - حالا با مسیر کامل
try:
    from backend.core.database.base import Base, engine
    from backend.core.database.setup import setup_database
    logger.info("✅ Database modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Database import error: {e}")
    # ایجاد mock objects برای جلوگیری از crash
    Base = type('Base', (), {})
    engine = None
    
# ایمپورت روت‌ها با try/except
routers = []

try:
    from backend.apps.auth.routes.user_routes import router as user_router
    routers.append(("auth", user_router, "/api/v1/auth"))
except ImportError as e:
    logger.warning(f"⚠️ Auth routes not available: {e}")

try:
    from backend.apps.admin.routes.admin_auth_routes import router as admin_auth_router
    routers.append(("admin_auth", admin_auth_router, "/api/v1/admin/auth"))
except ImportError as e:
    logger.warning(f"⚠️ Admin auth routes not available: {e}")

try:
    from backend.apps.admin.routes.user_management_routes import router as user_management_router
    routers.append(("user_management", user_management_router, "/api/v1/admin/users"))
except ImportError as e:
    logger.warning(f"⚠️ User management routes not available: {e}")

try:
    from backend.apps.kyc.routes.kyc_routes import router as kyc_router
    routers.append(("kyc", kyc_router, "/api/v1/kyc"))
except ImportError as e:
    logger.warning(f"⚠️ KYC routes not available: {e}")

try:
    from backend.apps.kyc.routes.kyc_admin_routes import router as kyc_admin_router
    routers.append(("kyc_admin", kyc_admin_router, "/api/v1/admin/kyc"))
except ImportError as e:
    logger.warning(f"⚠️ KYC admin routes not available: {e}")

try:
    from backend.apps.scoring.routes.scoring_routes import router as scoring_router
    routers.append(("scoring", scoring_router, "/api/v1/scoring"))
except ImportError as e:
    logger.warning(f"⚠️ Scoring routes not available: {e}")

try:
    from backend.apps.referral.routes.referral_routes import router as referral_router
    routers.append(("referral", referral_router, "/api/v1/referral"))
except ImportError as e:
    logger.warning(f"⚠️ Referral routes not available: {e}")

try:
    from backend.apps.finance.routes.finance_routes import router as finance_router
    routers.append(("finance", finance_router, "/api/v1/finance"))
except ImportError as e:
    logger.warning(f"⚠️ Finance routes not available: {e}")

# ثبت روت‌ها
for name, router, prefix in routers:
    app.include_router(router, prefix=prefix, tags=[name.title()])
    logger.info(f"✅ Registered {name} routes at {prefix}")

# ایجاد جداول دیتابیس
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting NOWEX Backend...")
    
    # ایجاد جداول
    try:
        setup_database()
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")

# رویداد shutdown
@app.on_event("shutdown")
def shutdown_event():
    logger.info("🛑 Shutting down NOWEX Backend...")

# روت سلامت
@app.get("/")
async def root():
    return {
        "message": "NOWEX Backend API", 
        "status": "running",
        "routes": len(routers)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "NOWEX Backend",
        "database": "connected" if engine else "disconnected"
    }

@app.get("/routes")
async def list_routes():
    return {
        "available_routes": [{"name": name, "prefix": prefix} for name, _, prefix in routers]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"  # 🔧 تغییر به debug
    )