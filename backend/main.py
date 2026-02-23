import logging
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

print("🔥 MAIN LOADED FROM:", __file__)

# ---------------------------------------------------------
# 📌 تنظیم مسیر صحیح پروژه
# ---------------------------------------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

backend_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_root)

# ---------------------------------------------------------
# 📌 ساخت اپلیکیشن
# ---------------------------------------------------------
app = FastAPI(
    title="NOWEX Backend",
    version="1.0.0",
    debug=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# 📌 Static Files (Profile Images, Uploads)
# ---------------------------------------------------------
# اگر فولدر uploads وجود نداشت، ساخته شود
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# سرو کردن فایل‌های آپلود شده
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

print("INFO:main:📁 Static /uploads mounted successfully")

# ---------------------------------------------------------
# 📌 ایمپورت دیتابیس
# ---------------------------------------------------------
try:
    from backend.core.database.base import Base, engine
    from backend.core.database.setup import setup_database
    print("INFO:main:✅ Database modules imported successfully")
except Exception as e:
    print("❌ Database import error:", e)
    Base = None
    engine = None

# ---------------------------------------------------------
# 📌 ایمپورت مدل‌ها
# ---------------------------------------------------------
try:
    from backend.apps.admin.models.admin_user import AdminUser
    from backend.apps.admin.models.admin_role import AdminRole
    from backend.apps.admin.models.admin_permission import AdminPermission
    from backend.apps.admin.models.admin_audit_log import AdminAuditLog

    try:
        from backend.apps.admin.models.admin_user_management import AdminUserManagement
    except:
        pass

    from backend.apps.auth.models.user import User

    print("INFO:main:✅ All models imported successfully")

except Exception as e:
    print("❌ Model import error:", e)

# ---------------------------------------------------------
# 📌 ایمپورت روت‌ها
# ---------------------------------------------------------
routers_map = [
    ("auth", "backend.apps.auth.routes.user_routes", "/api/v1/auth"),

    # 🔥 همه روت‌های ادمین زیر /api/v1/admin
    ("admin_auth", "backend.apps.admin.routes.admin_auth_routes", "/api/v1/admin"),
    ("admin_users", "backend.apps.admin.routes.admin_user_routes", "/api/v1/admin"),
    ("user_management", "backend.apps.admin.routes.user_management_routes", "/api/v1/admin"),

    ("kyc", "backend.apps.kyc.routes.kyc_routes", "/api/v1/kyc"),
    ("kyc_admin", "backend.apps.kyc.routes.kyc_admin_routes", "/api/v1/admin/kyc"),
    ("scoring", "backend.apps.scoring.routes.scoring_routes", "/api/v1/scoring"),
    ("referral", "backend.apps.referral.routes.referral_routes", "/api/v1/referral"),
    ("finance", "backend.apps.finance.routes.finance_routes", "/api/v1/finance"),
    ("health", "backend.apps.health.routes", "/api/v1/health"),
]

def safe_import(name, import_func):
    try:
        return import_func()
    except Exception as e:
        print(f"❌ {name} import error:", e)
        return None

for name, module_path, prefix in routers_map:
    router = safe_import(name, lambda m=module_path: __import__(m, fromlist=["router"]).router)
    if router:
        app.include_router(router, prefix=prefix, tags=[name.title()])
        print(f"INFO:main:✅ Registered {name} routes at {prefix}")

# ---------------------------------------------------------
# 📌 Startup
# ---------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    print("INFO:main:🚀 Starting NOWEX Backend...")
    try:
        setup_database()
        print("INFO:main:✅ Database tables created/verified")
    except Exception as e:
        print("❌ Database setup error:", e)

# ---------------------------------------------------------
# 📌 Root Routes
# ---------------------------------------------------------
@app.get("/")
async def root():
    return {"message": "NOWEX Backend Running"}

@app.get("/routes")
async def list_routes():
    return {
        "available_routes": [{"name": name, "prefix": prefix} for name, _, prefix in routers_map],
        "total_routes": len(routers_map),
        "ci_cd_tested": True
    }

# ---------------------------------------------------------
# 📌 Run (local)
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
