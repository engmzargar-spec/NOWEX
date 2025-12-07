-- ایجاد جداول سیستم KYC - نسخه اصلاح شده با UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- سطوح KYC
    kyc_level VARCHAR(20) DEFAULT 'level_0' CHECK (kyc_level IN ('level_0', 'level_1', 'level_2', 'level_3')),
    kyc_status VARCHAR(20) DEFAULT 'draft' CHECK (kyc_status IN ('draft', 'submitted', 'under_review', 'approved', 'rejected', 'expired')),
    
    -- اطلاعات شخصی
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    national_code VARCHAR(10) UNIQUE,
    birth_date TIMESTAMP,
    birth_city VARCHAR(100),
    gender VARCHAR(10) CHECK (gender IN ('male', 'female')),
    
    -- اطلاعات تماس
    address TEXT,
    postal_code VARCHAR(10),
    phone VARCHAR(15),
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Iran',
    
    -- اطلاعات بانکی
    bank_name VARCHAR(100),
    sheba_number VARCHAR(26),
    account_number VARCHAR(20),
    card_number VARCHAR(16),
    
    -- وضعیت تأییدها
    email_verified BOOLEAN DEFAULT FALSE,
    mobile_verified BOOLEAN DEFAULT FALSE,
    bank_verified BOOLEAN DEFAULT FALSE,
    identity_verified BOOLEAN DEFAULT FALSE,
    address_verified BOOLEAN DEFAULT FALSE,
    video_verified BOOLEAN DEFAULT FALSE,
    
    -- امتیاز و ریسک
    risk_score INTEGER DEFAULT 0,
    completion_percentage FLOAT DEFAULT 0.0,
    
    -- متادیتا
    submitted_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by UUID, -- REFERENCES admin_users(id) -- موقتاً غیرفعال
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ایجاد ایندکس برای جداول KYC
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_kyc_status ON user_profiles(kyc_status);
CREATE INDEX idx_user_profiles_kyc_level ON user_profiles(kyc_level);
CREATE INDEX idx_user_profiles_national_code ON user_profiles(national_code);

-- جدول تأییدیه‌های KYC
CREATE TABLE kyc_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    verification_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    method VARCHAR(50),
    
    -- نتایج اعتبارسنجی خودکار
    confidence_score FLOAT,
    auto_verification_result JSONB,
    
    -- اطلاعات تأیید دستی
    verified_by UUID, -- REFERENCES admin_users(id) -- موقتاً غیرفعال
    verified_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- متادیتا
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kyc_verifications_user_id ON kyc_verifications(user_id);
CREATE INDEX idx_kyc_verifications_profile_id ON kyc_verifications(profile_id);
CREATE INDEX idx_kyc_verifications_status ON kyc_verifications(status);

-- جدول مدارک KYC
CREATE TABLE kyc_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    
    -- وضعیت document
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    verification_result JSONB,
    
    -- امنیت
    file_hash VARCHAR(64),
    encrypted BOOLEAN DEFAULT TRUE,
    
    -- متادیتا
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    verified_by UUID, -- REFERENCES admin_users(id) -- موقتاً غیرفعال
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kyc_documents_user_id ON kyc_documents(user_id);
CREATE INDEX idx_kyc_documents_profile_id ON kyc_documents(profile_id);
CREATE INDEX idx_kyc_documents_document_type ON kyc_documents(document_type);

-- جدول تاریخچه وضعیت KYC
CREATE TABLE kyc_state_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    from_state VARCHAR(50) NOT NULL,
    to_state VARCHAR(50) NOT NULL,
    transition VARCHAR(50) NOT NULL,
    reason TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_kyc_state_history_user_id ON kyc_state_history(user_id);
CREATE INDEX idx_kyc_state_history_created_at ON kyc_state_history(created_at);