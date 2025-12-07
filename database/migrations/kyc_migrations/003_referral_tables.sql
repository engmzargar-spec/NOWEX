-- ایجاد جداول سیستم رفرال - نسخه اصلاح شده با UUID
CREATE TABLE referral_programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- اطلاعات برنامه
    program_name VARCHAR(100) UNIQUE NOT NULL,
    program_description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- پاداش‌ها
    rewards JSONB NOT NULL,
    
    -- محدودیت‌ها
    max_referrals_per_user INTEGER,
    reward_expiry_days INTEGER DEFAULT 30,
    minimum_kyc_level VARCHAR(20) DEFAULT 'level_1',
    
    -- تنظیمات
    allow_self_referral BOOLEAN DEFAULT FALSE,
    require_kyc_for_reward BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول روابط رفرال
CREATE TABLE referral_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- کاربران
    referrer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- کد معرف
    referral_code VARCHAR(20) NOT NULL,
    
    -- وضعیت
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'registered', 'kyc_completed', 'first_trade', 'completed', 'expired', 'cancelled'
    )),
    
    -- پاداش‌ها
    total_bonus_earned JSONB DEFAULT '{}',
    total_bonus_paid JSONB DEFAULT '{}',
    
    -- تاریخ‌های مهم
    referred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    kyc_completed_at TIMESTAMP,
    first_trade_at TIMESTAMP,
    completed_at TIMESTAMP,
    expired_at TIMESTAMP,
    
    -- متادیتا
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_referral_relationships_referrer_id ON referral_relationships(referrer_id);
CREATE INDEX idx_referral_relationships_referred_id ON referral_relationships(referred_id);
CREATE INDEX idx_referral_relationships_referral_code ON referral_relationships(referral_code);
CREATE INDEX idx_referral_relationships_status ON referral_relationships(status);

-- جدول پاداش‌های رفرال
CREATE TABLE referral_rewards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    referral_id UUID NOT NULL REFERENCES referral_relationships(id) ON DELETE CASCADE,
    referrer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- نوع پاداش
    reward_type VARCHAR(50) NOT NULL,
    reward_stage VARCHAR(50),
    
    -- مقدار پاداش
    points_awarded INTEGER DEFAULT 0,
    cash_awarded FLOAT DEFAULT 0.0,
    bonus_percentage FLOAT DEFAULT 0.0,
    
    -- وضعیت
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'earned', 'paid', 'cancelled', 'expired'
    )),
    
    -- تاریخ‌ها
    earned_at TIMESTAMP,
    paid_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- تأییدیه
    --verified_by UUID --REFERENCES admin_users(id),
    verified_at TIMESTAMP,
    
    -- متادیتا
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_referral_rewards_referral_id ON referral_rewards(referral_id);
CREATE INDEX idx_referral_rewards_referrer_id ON referral_rewards(referrer_id);
CREATE INDEX idx_referral_rewards_status ON referral_rewards(status);

-- جدول کدهای معرف
CREATE TABLE referral_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- کد معرف
    code VARCHAR(20) UNIQUE NOT NULL,
    custom_code VARCHAR(20) UNIQUE,
    
    -- آمار
    total_referrals INTEGER DEFAULT 0,
    successful_referrals INTEGER DEFAULT 0,
    total_earnings JSONB DEFAULT '{}',
    
    -- تنظیمات
    is_active BOOLEAN DEFAULT TRUE,
    is_custom BOOLEAN DEFAULT FALSE,
    
    -- تاریخ‌ها
    last_used_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_referral_codes_user_id ON referral_codes(user_id);
CREATE INDEX idx_referral_codes_code ON referral_codes(code);
CREATE INDEX idx_referral_codes_custom_code ON referral_codes(custom_code);

-- جدول آمار رفرال
CREATE TABLE referral_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- آمار کلی
    total_invites_sent INTEGER DEFAULT 0,
    total_signups INTEGER DEFAULT 0,
    total_kyc_completed INTEGER DEFAULT 0,
    total_first_trades INTEGER DEFAULT 0,
    
    -- نرخ تبدیل
    conversion_rates JSONB DEFAULT '{}',
    
    -- درآمد
    total_points_earned INTEGER DEFAULT 0,
    total_cash_earned FLOAT DEFAULT 0.0,
    pending_rewards JSONB DEFAULT '{}',
    
    -- رتبه‌بندی
    leaderboard_rank INTEGER,
    
    -- تاریخ‌ها
    last_invite_sent TIMESTAMP,
    stats_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_referral_stats_user_id ON referral_stats(user_id);
CREATE INDEX idx_referral_stats_leaderboard_rank ON referral_stats(leaderboard_rank);

-- جدول تنظیمات برنامه رفرال
CREATE TABLE program_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- تنظیمات عمومی
    site_name VARCHAR(100) DEFAULT 'NOWEX',
    program_title VARCHAR(200) DEFAULT 'دعوت از دوستان',
    program_description TEXT,
    
    -- تنظیمات پاداش
    default_rewards JSONB DEFAULT '{}',
    reward_currency VARCHAR(10) DEFAULT 'IRT',
    
    -- محدودیت‌ها
    max_referrals_per_user INTEGER DEFAULT 50,
    reward_expiry_days INTEGER DEFAULT 30,
    min_trade_amount_for_reward FLOAT DEFAULT 0.0,
    
    -- تنظیمات رابط کاربری
    invite_message_template TEXT,
    social_share_buttons JSONB DEFAULT '[]',
    show_leaderboard BOOLEAN DEFAULT TRUE,
    
    -- تنظیمات اعلان
    send_invite_emails BOOLEAN DEFAULT TRUE,
    send_reward_notifications BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);