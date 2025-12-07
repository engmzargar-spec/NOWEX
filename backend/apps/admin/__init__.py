from fastapi import APIRouter
from .routes import admin_routers

# ایجاد router اصلی برای ادمین
admin_router = APIRouter(prefix="/admin")

# ثبت تمام route های ادمین
for router in admin_routers:
    admin_router.include_router(router)

__all__ = ["admin_router"]