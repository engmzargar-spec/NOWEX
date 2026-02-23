from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import uuid
import base64
import os
import re
from datetime import datetime

from backend.apps.admin.models.admin_user import AdminUser
from backend.core.security.password import get_password_hash, pwd_context


# ---------------------------------------------------------
# 📌 مسیر ذخیره آواتار
# ---------------------------------------------------------
UPLOAD_DIR = "uploads/admin_avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_avatar(base64_data: Optional[str]) -> Optional[str]:
    """Decode Base64 image and save to disk."""
    if not base64_data:
        return None

    try:
        header, encoded = base64_data.split(",", 1)
        ext = "png" if "png" in header else "jpg"

        file_name = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(encoded))

        # 🔥 مسیر صحیح (static ❌ / uploads ✔)
        return f"/uploads/admin_avatars/{file_name}"

    except Exception:
        raise ValueError("خطا در پردازش تصویر پروفایل")


# ---------------------------------------------------------
# 📌 اعتبارسنجی رمز عبور
# ---------------------------------------------------------
def validate_password(password: str):
    if len(password) < 8:
        raise ValueError("رمز عبور باید حداقل ۸ کاراکتر باشد")

    if not re.search(r"[A-Z]", password):
        raise ValueError("رمز عبور باید حداقل یک حرف بزرگ داشته باشد")

    if not re.search(r"[a-z]", password):
        raise ValueError("رمز عبور باید حداقل یک حرف کوچک داشته باشد")

    if not re.search(r"[0-9]", password):
        raise ValueError("رمز عبور باید حداقل یک عدد داشته باشد")

    if not re.search(r"[\W_]", password):
        raise ValueError("رمز عبور باید حداقل یک علامت خاص داشته باشد")


# ---------------------------------------------------------
# 📌 اعتبارسنجی شماره موبایل
# ---------------------------------------------------------
def validate_phone(phone: str):
    if not re.match(r"^09\d{9}$", phone):
        raise ValueError("شماره موبایل معتبر نیست")


# ---------------------------------------------------------
# 📌 سرویس اصلی مدیریت کاربران ادمین
# ---------------------------------------------------------
class AdminUserService:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------
    def get_admin_by_username(self, username: str):
        return self.db.query(AdminUser).filter(AdminUser.username == username).first()

    def authenticate_admin(self, username: str, password: str):
        admin = self.get_admin_by_username(username)
        if not admin or not pwd_context.verify(password, admin.hashed_password):
            return None
        return admin

    def update_last_login(self, admin_id: str):
        admin = self.db.query(AdminUser).filter(AdminUser.id == admin_id).first()
        if admin:
            admin.last_login = datetime.utcnow()
            self.db.commit()

    # ---------------------------------------------------------
    # User Queries
    # ---------------------------------------------------------
    def get_users(self, skip=0, limit=100, search=None, position=None, is_active=None):
        query = self.db.query(AdminUser)

        if search:
            query = query.filter(
                or_(
                    AdminUser.username.ilike(f"%{search}%"),
                    AdminUser.email.ilike(f"%{search}%"),
                    AdminUser.first_name.ilike(f"%{search}%"),
                    AdminUser.last_name.ilike(f"%{search}%"),
                )
            )

        if position:
            query = query.filter(AdminUser.position == position)

        if is_active is not None:
            query = query.filter(AdminUser.is_active == is_active)

        return query.order_by(AdminUser.created_at.desc()).offset(skip).limit(limit).all()

    def get_user_by_id(self, user_id: str):
        return self.db.query(AdminUser).filter(AdminUser.id == user_id).first()

    def get_user_by_email(self, email: str):
        return self.db.query(AdminUser).filter(AdminUser.email == email).first()

    # ---------------------------------------------------------
    # Create User
    # ---------------------------------------------------------
    def create_user(self, data) -> AdminUser:

        validate_password(data.password)
        validate_phone(data.phone)

        if self.get_admin_by_username(data.username):
            raise ValueError("نام کاربری از قبل وجود دارد")

        if self.get_user_by_email(data.email):
            raise ValueError("ایمیل از قبل وجود دارد")

        avatar_path = save_avatar(data.avatar_url)

        hashed_password = get_password_hash(data.password)

        db_user = AdminUser(
            id=str(uuid.uuid4()),
            username=data.username,
            email=data.email,
            first_name=data.first_name,
            # اگر اسکیمای قبلی last_last_name داشت، این خط سازگار می‌ماند
            last_name=data.last_last_name if hasattr(data, "last_last_name") else data.last_name,
            phone=data.phone,
            position=data.position,
            employee_id=data.employee_id,
            address=data.address,
            description=data.description,
            hashed_password=hashed_password,
            is_active=data.is_active,
            two_factor_enabled=data.two_factor_enabled,
            avatar_url=avatar_path,
            login_attempts=0,
            is_locked=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            password_changed_at=datetime.utcnow()
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    # ---------------------------------------------------------
    # Update User
    # ---------------------------------------------------------
    def update_user(self, user_id: str, update_data: dict):
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None

        # -------------------------------
        # 🔥 Normalize & update username
        # -------------------------------
        if "username" in update_data:
            new_username = (update_data["username"] or "").strip()

            # اگر نام کاربری واقعاً تغییر کرده
            if new_username and new_username != db_user.username:
                existing = self.get_admin_by_username(new_username)
                if existing and existing.id != user_id:
                    raise ValueError("نام کاربری تکراری است")

                db_user.username = new_username

            # دیگر نیازی نیست در حلقهٔ عمومی دوباره ست شود
            update_data.pop("username", None)

        # -------------------------------
        # 🔥 Normalize & update email
        # -------------------------------
        if "email" in update_data:
            new_email = (update_data["email"] or "").strip()

            if new_email and new_email != db_user.email:
                existing = self.get_user_by_email(new_email)
                if existing and existing.id != user_id:
                    raise ValueError("ایمیل تکراری است")

                db_user.email = new_email

            update_data.pop("email", None)

        # -------------------------------
        # 🔥 Password update
        # -------------------------------
        if "password" in update_data:
            validate_password(update_data["password"])
            db_user.hashed_password = get_password_hash(update_data.pop("password"))
            db_user.password_changed_at = datetime.utcnow()

        # -------------------------------
        # 🔥 Avatar update
        # -------------------------------
        if "avatar_url" in update_data:
            db_user.avatar_url = save_avatar(update_data["avatar_url"])
            update_data.pop("avatar_url", None)

        # -------------------------------
        # 🔥 Update other fields
        # -------------------------------
        for field, value in update_data.items():
            if hasattr(db_user, field) and field != "id":
                setattr(db_user, field, value)

        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    # ---------------------------------------------------------
    # Delete User
    # ---------------------------------------------------------
    def delete_user(self, user_id: str):
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True

    # ---------------------------------------------------------
    # Update Password
    # ---------------------------------------------------------
    def update_password(self, user_id: str, new_password: str):
        validate_password(new_password)

        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise ValueError("کاربر یافت نشد")

        db_user.hashed_password = get_password_hash(new_password)
        db_user.password_changed_at = datetime.utcnow()
        db_user.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_user)

    # ---------------------------------------------------------
    # Activate User
    # ---------------------------------------------------------
    def activate_user(self, user_id: str):
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise ValueError("کاربر یافت نشد")

        db_user.is_active = True
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)

    # ---------------------------------------------------------
    # Lock / Unlock User
    # ---------------------------------------------------------
    def lock_user(self, user_id: str):
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise ValueError("کاربر یافت نشد")

        db_user.is_locked = True
        db_user.updated_at = datetime.utcnow()
        self.db.commit()

    def unlock_user(self, user_id: str):
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise ValueError("کاربر یافت نشد")

        db_user.is_locked = False
        db_user.login_attempts = 0
        db_user.updated_at = datetime.utcnow()
        self.db.commit()

    # ---------------------------------------------------------
    # Count Users
    # ---------------------------------------------------------
    def count_users(self):
        return self.db.query(AdminUser).count()
