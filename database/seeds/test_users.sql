-- database/seeds/test_users.sql
-- ایجاد کاربران تستی برای توسعه

-- کاربر تستی ۱
INSERT INTO users (
    id,
    email, 
    phone_number,
    username,
    hashed_password,
    first_name,
    last_name,
    is_active,
    is_verified,
    kyc_status,
    created_at,
    updated_at
) VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'test@example.com',
    '09123456789',
    'testuser',
    '$2b$12$LQv3c1yqBWVHxkd0L8k4Cuph1R7Mh2W5M5RZ9VnY9WzJkK8b5B6a', -- password: admin123
    'کاربر',
    'تستی',
    true,
    true,
    'pending',
    NOW(),
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- کاربر تستی ۲
INSERT INTO users (
    id,
    email, 
    phone_number,
    username,
    hashed_password,
    first_name,
    last_name,
    is_active,
    is_verified,
    kyc_status,
    created_at,
    updated_at
) VALUES (
    'b1ffcc99-9c0b-4ef8-bb6d-6bb9bd380a12',
    'user2@example.com',
    '09123456780',
    'testuser2',
    '$2b$12$LQv3c1yqBWVHxkd0L8k4Cuph1R7Mh2W5M5RZ9VnY9WzJkK8b5B6a', -- password: admin123
    'کاربر',
    'دوم',
    true,
    false,
    'pending',
    NOW(),
    NOW()
) ON CONFLICT (email) DO NOTHING;