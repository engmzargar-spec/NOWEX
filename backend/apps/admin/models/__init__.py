from .admin_user import AdminUser
from .admin_audit_log import AdminAuditLog
from .admin_permission import AdminPermission
from .admin_role import AdminRole

# ایجاد alias برای Admin
Admin = AdminUser

__all__ = ["AdminUser", "AdminAuditLog", "AdminPermission", "AdminRole", "Admin"]