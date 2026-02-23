# backend/apps/admin/routes/admin_auth_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from backend.core.database.base import get_db
from backend.core.dependencies import get_redis
from backend.core.config.base_config import settings
from backend.apps.admin.schemas.admin_auth_schema import AdminLoginRequest, AdminTokenResponse
from backend.apps.admin.services.admin_user_service import AdminUserService
from backend.apps.admin.services.admin_auth_service import AdminAuthService

router = APIRouter(prefix="/auth", tags=["Admin Authentication"])
security = HTTPBearer()


# ---------------------------------------------------------
# 🔐 LOGIN
# ---------------------------------------------------------
@router.post("/login", response_model=AdminTokenResponse)
async def admin_login(login_data: AdminLoginRequest, db: Session = Depends(get_db)):
    admin_service = AdminUserService(db)
    admin = admin_service.authenticate_admin(login_data.username, login_data.password)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    admin_service.update_last_login(str(admin.id))

    # ساخت full_name جدید
    full_name = f"{admin.first_name} {admin.last_name}"

    # ساخت توکن بدون role
    access_token = AdminAuthService.create_access_token(
        data={
            "sub": admin.username,
            "admin_id": str(admin.id),
            "position": admin.position
        }
    )

    return AdminTokenResponse(
        access_token=access_token,
        admin_id=str(admin.id),
        username=admin.username,
        position=admin.position
    )


# ---------------------------------------------------------
# 🔐 LOGOUT
# ---------------------------------------------------------
@router.post("/logout")
async def admin_logout(
    token: str = Depends(security),
    redis_client = Depends(get_redis)
):
    try:
        payload = jwt.decode(
            token.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        ttl = 1800
        blacklist_key = f"blacklist_token:{token.credentials}"
        redis_client.setex(blacklist_key, ttl, "revoked")

        return {"message": "Logout successful", "success": True}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout error: {str(e)}")


# ---------------------------------------------------------
# 🔐 AUTH / ME
# ---------------------------------------------------------
@router.get("/me")
async def get_current_admin_info(
    token: str = Depends(security),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    try:
        blacklist_key = f"blacklist_token:{token.credentials}"
        blacklisted = redis_client.get(blacklist_key)

        if blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )

        payload = jwt.decode(
            token.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        admin_service = AdminUserService(db)
        admin = admin_service.get_admin_by_username(username)

        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")

        full_name = f"{admin.first_name} {admin.last_name}"

        return {
            "id": str(admin.id),
            "username": admin.username,
            "email": admin.email,
            "full_name": full_name,
            "position": admin.position,
            "is_active": admin.is_active,
            "last_login": admin.last_login.isoformat() if admin.last_login else None,
            "created_at": admin.created_at.isoformat()
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
