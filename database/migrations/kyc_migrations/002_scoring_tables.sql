-- ایجاد جداول سیستم امتیازدهی - نسخه اصلاح شده با UUID
CREATE TABLE user_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- امتیاز کلی
    total_score INTEGER DEFAULT 0,
    current_level VARCHAR(20) DEFAULT 'bronze' CHECK (current_level IN ('bronze', 'silver', 'gold', 'platinum', 'diamond')),
    
    -- تجزیه امتیاز
    score_breakdown JSONB DEFAULT '{}',
    
    -- آمار فعالیت
    daily_login_streak INTEGER DEFAULT 0,
    total_trading_volume FLOAT DEFAULT 0.0,
    total_trades_count INTEGER DEFAULT 0,
    account_age_days INTEGER DEFAULT 0,
    
    -- تاریخ‌های مهم
    last_login_date TIMESTAMP,
    last_score_calculation TIMESTAMP,
    level_updated_at TIMESTAMP,
    
    -- تنظیمات
    score_multiplier FLOAT DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_scores_user_id ON user_scores(user_id);
CREATE INDEX idx_user_scores_total_score ON user_scores(total_score DESC);
CREATE INDEX idx_user_scores_current_level ON user_scores(current_level);

-- جدول تاریخچه امتیاز
CREATE TABLE score_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score_id UUID NOT NULL REFERENCES user_scores(id) ON DELETE CASCADE,
    
    -- تغییر امتیاز
    score_change INTEGER NOT NULL,
    new_total_score INTEGER NOT NULL,
    
    -- منبع تغییر
    source VARCHAR(50) NOT NULL CHECK (source IN (
        'kyc_completion', 'referral_bonus', 'trading_volume', 'account_age', 
        'daily_login', 'trade_activity', 'loyalty_bonus', 'manual_adjustment', 'penalty'
    )),
    source_details JSONB DEFAULT '{}',
    
    -- توضیحات
    description TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_score_history_user_id ON score_history(user_id);
CREATE INDEX idx_score_history_score_id ON score_history(score_id);
CREATE INDEX idx_score_history_source ON score_history(source);
CREATE INDEX idx_score_history_created_at ON score_history(created_at DESC);

-- جدول مزایای سطوح
CREATE TABLE score_benefits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- سطح کاربری
    level VARCHAR(20) UNIQUE NOT NULL CHECK (level IN ('bronze', 'silver', 'gold', 'platinum', 'diamond')),
    level_name VARCHAR(50) NOT NULL,
    level_description TEXT,
    
    -- محدوده امتیاز
    min_score_required INTEGER NOT NULL,
    max_score INTEGER,
    
    -- مزایا
    benefits JSONB NOT NULL,
    
    -- محدودیت‌ها
    withdrawal_limit_multiplier FLOAT DEFAULT 1.0,
    deposit_limit_multiplier FLOAT DEFAULT 1.0,
    
    -- ظاهر
    level_color VARCHAR(7),
    level_icon VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول مزایای کاربران
CREATE TABLE user_benefits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score_id UUID NOT NULL REFERENCES user_scores(id) ON DELETE CASCADE,
    
    -- مزایای فعال
    active_benefits JSONB DEFAULT '{}',
    
    -- آمار استفاده
    benefits_usage JSONB DEFAULT '{}',
    
    -- تنظیمات
    auto_claim_benefits BOOLEAN DEFAULT TRUE,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    
    -- تاریخ‌ها
    benefits_updated_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_benefits_user_id ON user_benefits(user_id);
CREATE INDEX idx_user_benefits_score_id ON user_benefits(score_id);

-- جدول قوانین امتیازدهی
CREATE TABLE scoring_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name VARCHAR(100) UNIQUE NOT NULL,
    rule_description TEXT,
    
    -- تنظیمات rule
    rule_type VARCHAR(50),
    action_type VARCHAR(100),
    
    -- امتیاز
    base_points INTEGER DEFAULT 0,
    max_daily_points INTEGER,
    max_total_points INTEGER,
    
    -- شرایط
    conditions JSONB DEFAULT '{}',
    
    -- فعال/غیرفعال
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 1,
    
    -- تاریخ‌ها
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scoring_rules_rule_type ON scoring_rules(rule_type);
CREATE INDEX idx_scoring_rules_is_active ON scoring_rules(is_active);