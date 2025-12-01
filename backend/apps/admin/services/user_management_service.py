from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Tuple
from uuid import UUID
import logging

from backend.apps.auth.models.user import User
from backend.apps.admin.models.admin_user_management import UserManagementLog, UserKYCData
from backend.apps.admin.schemas.user_management_schema import (
    UserSearchFilter, 
    UserStatus, 
    KYCStatus,
    PaginatedUserResponse,
    UserListResponse
)

logger = logging.getLogger(__name__)

class UserManagementService:
    def __init__(self, db: Session):
        self.db = db

    async def get_users_paginated(
        self, 
        page: int = 1, 
        page_size: int = 50,
        filters: Optional[UserSearchFilter] = None
    ) -> PaginatedUserResponse:
        try:
            # ایجاد کوئری پایه
            query = self.db.query(User)
            
            # اعمال فیلترها - موقتاً غیرفعال
            # if filters:
            #     if filters.email:
            #         query = query.filter(User.email.ilike(f"%{filters.email}%"))
            #     if filters.status:
            #         query = query.filter(User.status == filters.status)  # ❌ این خط مشکل داره
            #     if filters.date_from:
            #         query = query.filter(User.created_at >= filters.date_from)
            #     if filters.date_to:
            #         query = query.filter(User.created_at <= filters.date_to)
            
            # محاسبه تعداد کل
            total_count = query.count()
            
            # اعمال pagination
            users = query.order_by(desc(User.created_at))\
                        .offset((page - 1) * page_size)\
                        .limit(page_size)\
                        .all()
            
            # تبدیل به schema
            user_list = []
            for user in users:
                # گرفتن وضعیت KYC
                kyc_data = self.db.query(UserKYCData)\
                                .filter(UserKYCData.user_id == user.id)\
                                .first()
                
                kyc_status = KYCStatus.PENDING
                if kyc_data:
                    kyc_status = kyc_data.status
                
                # محاسبه وضعیت کاربر بر اساس فیلدهای موجود
                user_status = UserStatus.ACTIVE
                if user.is_suspended:
                    user_status = UserStatus.SUSPENDED
                elif not user.is_verified:
                    user_status = UserStatus.PENDING_VERIFICATION
                
                user_list.append(UserListResponse(
                    id=user.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone_number=user.phone_number,
                    status=user_status,  # ✅ استفاده از وضعیت محاسبه شده
                    kyc_status=kyc_status,
                    created_at=user.created_at,
                    last_login=user.last_login
                ))
            
            return PaginatedUserResponse(
                users=user_list,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=(total_count + page_size - 1) // page_size
            )
            
        except Exception as e:
            logger.error(f"Error in get_users_paginated: {str(e)}")
            raise

    async def get_user_detail(self, user_id: UUID) -> Optional[dict]:
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            kyc_data = self.db.query(UserKYCData)\
                            .filter(UserKYCData.user_id == user_id)\
                            .first()
            
            # گرفتن لاگ‌های مدیریت کاربر
            management_logs = self.db.query(UserManagementLog)\
                                   .filter(UserManagementLog.user_id == user_id)\
                                   .order_by(desc(UserManagementLog.created_at))\
                                   .limit(50)\
                                   .all()
            
            return {
                "user": user,
                "kyc_data": kyc_data,
                "management_logs": management_logs
            }
            
        except Exception as e:
            logger.error(f"Error in get_user_detail: {str(e)}")
            raise

    async def update_user_status(
        self, 
        user_id: UUID, 
        new_status: UserStatus, 
        admin_id: UUID, 
        reason: str,
        ip_address: str,
        user_agent: str
    ) -> bool:
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # تبدیل وضعیت جدید به فیلدهای مدل User
            if new_status == UserStatus.SUSPENDED:
                user.is_suspended = True
            elif new_status == UserStatus.ACTIVE:
                user.is_suspended = False
                user.is_verified = True
            elif new_status == UserStatus.PENDING_VERIFICATION:
                user.is_verified = False
                user.is_suspended = False
            
            # ثبت لاگ
            log_entry = UserManagementLog(
                admin_id=admin_id,
                user_id=user_id,
                action_type="STATUS_UPDATE",
                previous_status="",  # موقتاً خالی
                new_status=new_status.value,
                reason=reason,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
            logger.info(f"User {user_id} status changed to {new_status} by admin {admin_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error in update_user_status: {str(e)}")
            raise