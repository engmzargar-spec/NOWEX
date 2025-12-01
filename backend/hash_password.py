from passlib.context import CryptContext

# تنظیم bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# رمز ساده که می‌خوای تست کنی
plain_password = "dummyhash"

# تولید هش
hashed_password = pwd_context.hash(plain_password)

print("رمز هش‌شده:")
print(hashed_password)
