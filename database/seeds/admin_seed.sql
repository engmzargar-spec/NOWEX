-- database/seeds/admin_seed.sql
-- درج نقش‌های پیش‌فرض
INSERT INTO admin_roles (name, description, permissions) VALUES 
('super_admin', 'دسترسی کامل به تمام سیستم', ARRAY['*']),
('support_agent', 'پشتیبان کاربران', ARRAY['user:read', 'user:edit', 'ticket:read', 'ticket:create']),
('compliance_officer', 'مسئول انطباق', ARRAY['user:read', 'user:kyc_verify', 'user:kyc_reject', 'user:suspend']),
('risk_manager', 'مدیر ریسک', ARRAY['user:read', 'risk:leverage_change', 'order:cancel', 'trade:view']),
('financial_operator', 'اپراتور مالی', ARRAY['transaction:withdrawal_approve', 'transaction:withdrawal_reject', 'transaction:view'])
ON CONFLICT (name) DO NOTHING;

-- درج دسترسی‌های پیش‌فرض
INSERT INTO admin_permissions (name, description, category) VALUES 
('user:read', 'مشاهده کاربران', 'user_management'),
('user:edit', 'ویرایش کاربران', 'user_management'),
('user:kyc_verify', 'تایید KYC کاربر', 'user_management'),
('user:kyc_reject', 'رد KYC کاربر', 'user_management'),
('user:suspend', 'معلق کردن کاربر', 'user_management'),
('order:cancel', 'لغو سفارش', 'trading'),
('trade:view', 'مشاهده معاملات', 'trading'),
('risk:leverage_change', 'تغییر اهرم', 'risk_management'),
('transaction:withdrawal_approve', 'تایید برداشت', 'financial'),
('transaction:withdrawal_reject', 'رد برداشت', 'financial'),
('transaction:view', 'مشاهده تراکنش‌ها', 'financial'),
('ticket:read', 'مشاهده تیکت‌ها', 'support'),
('ticket:create', 'ایجاد تیکت', 'support')
ON CONFLICT (name) DO NOTHING;

-- ایجاد ادمین اصلی
INSERT INTO admin_users (
    username, 
    email, 
    hashed_password, 
    full_name, 
    role,
    is_active,
    created_at,
    updated_at
) VALUES (
    'admin',
    'admin@nowex.com',
    '$2b$12$LQv3c1yqBWVHxkd0L8k4Cuph1R7Mh2W5M5RZ9VnY9WzJkK8b5B6a', -- password: admin123
    'مدیر سیستم نواکس',
    'super_admin',
    true,
    NOW(),
    NOW()
) ON CONFLICT (username) DO NOTHING;