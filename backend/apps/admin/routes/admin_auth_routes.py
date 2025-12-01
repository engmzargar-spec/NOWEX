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
from backend.apps.admin.models import Admin

router = APIRouter(prefix="/admin/auth", tags=["Admin Authentication"])
security = HTTPBearer()

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
    
    access_token = AdminAuthService.create_access_token(
        data={"sub": admin.username, "admin_id": str(admin.id), "role": admin.role}
    )
    
    return AdminTokenResponse(
        access_token=access_token,
        admin_id=str(admin.id),
        username=admin.username,
        role=admin.role
    )

@router.post("/logout")
async def admin_logout(
    token: str = Depends(security),
    redis_client = Depends(get_redis)
):
    """Logout admin user"""
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

@router.get("/me")
async def get_current_admin_info(
    token: str = Depends(security),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis)
):
    """Get current admin info - با چک blacklist و debug"""
    print(f"🔍 DEBUG: Checking token: {token.credentials[:20]}...")
    
    try:
        # Check if token is blacklisted - با debug
        blacklist_key = f"blacklist_token:{token.credentials}"
        blacklisted = redis_client.get(blacklist_key)
        print(f"🔍 DEBUG: Blacklist check for {blacklist_key}: {blacklisted}")
        
        if blacklisted:
            print("❌ DEBUG: Token is blacklisted!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        print("✅ DEBUG: Token is valid, decoding...")
        payload = jwt.decode(
            token.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        admin_service = AdminUserService(db)
        admin = admin_service.get_admin_by_username(payload.get("sub"))
        
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        print("✅ DEBUG: Returning admin info")
        return {
            "id": str(admin.id),
            "username": admin.username,
            "email": admin.email,
            "full_name": admin.full_name,
            "role": admin.role,
            "is_active": admin.is_active,
            "last_login": admin.last_login.isoformat() if admin.last_login else None,
            "created_at": admin.created_at.isoformat()
        }
        
    except JWTError:
        print("❌ DEBUG: JWT Error")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ DEBUG: Other error: {e}")
        raise