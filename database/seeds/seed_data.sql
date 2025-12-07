-- =========================
-- Users
-- =========================
INSERT INTO users (id, email, username, hashed_password, is_active, created_at, updated_at)
VALUES (
    'bf76777a-62a4-4008-9734-5ff57868e9cd'::uuid,
    'test4@example.com',
    'testuser4',
    '$2b$12$Vk1PVhv1yUrd9QuY14EWZuyIW1z86eO0teX51JcIv4m7j5.5OAKUG',
    TRUE,
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- =========================
-- User Scores
-- =========================
INSERT INTO user_scores (id, user_id, total_score, current_level, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'bf76777a-62a4-4008-9734-5ff57868e9cd'::uuid,
    150,
    'bronze',
    NOW(),
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- =========================
-- Score History (با مقادیر صحیح)
-- =========================
INSERT INTO score_history (
    id, user_id, score_id, score_change, new_total_score,
    source, description, created_at
)
SELECT
    gen_random_uuid(),
    'bf76777a-62a4-4008-9734-5ff57868e9cd'::uuid,
    (SELECT id FROM user_scores WHERE user_id = 'bf76777a-62a4-4008-9734-5ff57868e9cd'::uuid),
    100,
    100,
    'referral_bonus',  -- lowercase
    'Referral bonus awarded',
    NOW()
WHERE EXISTS (SELECT 1 FROM user_scores WHERE user_id = 'bf76777a-62a4-4008-9734-5ff57868e9cd'::uuid)

UNION ALL

SELECT
    gen_random_uuid(),
    'bf76777a-62a4-4008-9734-5ff57868e9cd'::uuid,
    (SELECT id FROM user_scores WHERE user_id = 'bf76777a-62a4-4008-9734-5ff57868e9cd'::uuid),
    50,
    150,
    'kyc_completion',  -- lowercase
    'KYC completed successfully',
    NOW()
WHERE EXISTS (SELECT 1 FROM user_scores WHERE user_id = 'bf76777a-62a4-4008-9734-5ff57868e9cd'::uuid);

-- =========================
-- User Profiles (نام صحیح جدول)
-- =========================
INSERT INTO user_profiles (
    id, user_id, kyc_level, kyc_status,
    first_name, last_name, national_code,
    birth_date, gender,
    address, postal_code, phone, city, country,
    bank_name, sheba_number, account_number,
    email_verified, mobile_verified, bank_verified,
    identity_verified, address_verified, video_verified,
    risk_score, completion_percentage,
    submitted_at, reviewed_at, created_at, updated_at
)
VALUES (
    gen_random_uuid(),
    'bf76777a-62a4-4008-9734-5ff57868e9cd'::uuid,
    'level_1', 'approved',  -- مقادیر صحیح برای constraint
    'Test', 'User', '1234567890',
    '1995-01-01', 'male',
    'خیابان آزادی، پلاک 10', '1234567890', '09120000003',
    'Tehran', 'Iran',
    'Melli Bank', 'IR820540102680020817909002', '123456789',
    TRUE, TRUE, TRUE, TRUE, TRUE, FALSE,
    75, 0.85,
    NOW(), NOW(), NOW(), NOW()
)
ON CONFLICT (id) DO NOTHING;

-- =========================
-- Score Benefits (ساختار اصلاح شده)
-- =========================
INSERT INTO score_benefits (
    id, level, level_name, min_score_required, benefits, created_at, updated_at
)
VALUES
(gen_random_uuid(), 'bronze', 'Bronze Benefits', 0, '{"basic_trading": true, "referral_access": true}'::jsonb, NOW(), NOW()),
(gen_random_uuid(), 'silver', 'Silver Benefits', 500, '{"higher_withdrawal": true, "extra_referral": true}'::jsonb, NOW(), NOW()),
(gen_random_uuid(), 'gold', 'Gold Benefits', 1000, '{"priority_support": true, "advanced_trading": true}'::jsonb, NOW(), NOW()),
(gen_random_uuid(), 'platinum', 'Platinum Benefits', 5000, '{"vip_rewards": true, "exclusive_offers": true}'::jsonb, NOW(), NOW())
ON CONFLICT (level) DO NOTHING;

-- =========================
-- Referral Codes
-- =========================
INSERT INTO referral_codes (id, user_id, code, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'bf76777a-62a4-4008-9734-5ff57868e9cd'::uuid,
    'TESTCODE123',
    NOW(), NOW()
)
ON CONFLICT (id) DO NOTHING;