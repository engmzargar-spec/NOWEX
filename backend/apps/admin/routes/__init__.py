from .admin_auth_routes import router as admin_auth_router
from .user_management_routes import router as user_management_router

# لیست تمام route های ادمین
admin_routers = [
    admin_auth_router,
    user_management_router
]