-- دیتای اولیه برای سطوح KYC
INSERT INTO score_benefits (level, level_name, level_description, min_score_required, benefits, level_color, level_icon) VALUES
('bronze', 'برنز', 'سطح ابتدایی برای کاربران جدید', 0, '{"fee_discount": 0, "priority_support": false, "exclusive_events": false, "higher_limits": false, "cashback_bonus": 0}', '#CD7F32', 'bronze-medal'),
('silver', 'نقره‌ای', 'سطح متوسط برای کاربران فعال', 50, '{"fee_discount": 5, "priority_support": true, "exclusive_events": false, "higher_limits": true, "cashback_bonus": 1}', '#C0C0C0', 'silver-medal'),
('gold', 'طلایی', 'سطح پیشرفته برای کاربران ویژه', 150, '{"fee_discount": 10, "priority_support": true, "exclusive_events": true, "higher_limits": true, "cashback_bonus": 2}', '#FFD700', 'gold-medal'),
('platinum', 'پلاتینیوم', 'سطح ویژه برای کاربران حرفه‌ای', 300, '{"fee_discount": 15, "priority_support": true, "exclusive_events": true, "higher_limits": true, "cashback_bonus": 3, "personal_manager": true}', '#E5E4E2', 'platinum-medal'),
('diamond', 'الماس', 'سطح اختصاصی برای کاربران VIP', 600, '{"fee_discount": 20, "priority_support": true, "exclusive_events": true, "higher_limits": true, "cashback_bonus": 5, "personal_manager": true, "vip_services": true}', '#B9F2FF', 'diamond-medal');

-- دیتای اولیه برای برنامه رفرال
INSERT INTO referral_programs (program_name, program_description, rewards, max_referrals_per_user, minimum_kyc_level) VALUES
('default', 'برنامه پیشفرض دعوت از دوستان', '{"registration": {"points": 5, "cash": 0}, "kyc_completion": {"points": 10, "cash": 50000}, "first_trade": {"points": 15, "cash": 100000}}', 100, 'level_1');

-- دیتای اولیه برای تنظیمات برنامه
INSERT INTO program_configurations (site_name, program_title, program_description, default_rewards) VALUES
('NOWEX', 'دعوت از دوستان', 'دوستان خود را به NOWEX دعوت کنید و پاداش بگیرید', '{"registration": {"points": 5, "cash": 0}, "kyc_completion": {"points": 10, "cash": 50000}, "first_trade": {"points": 15, "cash": 100000}}');