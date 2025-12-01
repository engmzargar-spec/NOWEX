# backend/core/security/password.py
from passlib.context import CryptContext

# Context برای هش کردن رمز عبور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """بررسی تطابق رمز عبور ساده با هش شده"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """هش کردن رمز عبور"""
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> bool:
    """بررسی قدرت رمز عبور"""
    if len(password) < 8:
        return False
    # می‌توانید قوانین بیشتری اضافه کنید
    return True