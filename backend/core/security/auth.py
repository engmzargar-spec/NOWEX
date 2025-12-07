from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.core.database.base import get_db
from backend.core.config.base_config import settings  # ✅ اصلاح شد
from backend.apps.admin.models.admin_user import AdminUser
from backend.apps.auth.models.user import User

# برای کاربران عادی
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# برای ادمین‌ها
admin_security = HTTPBearer()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    وابستگی برای دریافت کاربر عادی جاری
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")  # ✅ تغییر از username به user_id
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()  # ✅ جستجو با ID
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user

def get_current_admin_user(
    token: str = Depends(admin_security),
    db: Session = Depends(get_db)
) -> AdminUser:
    """
    وابستگی برای دریافت کاربر ادمین جاری
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    admin_user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if admin_user is None or not admin_user.is_active:
        raise credentials_exception
    
    return admin_user

# Alias برای سازگاری با کد موجود
get_current_admin = get_current_admin_user