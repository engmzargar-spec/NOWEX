-- قوانین امتیازدهی
INSERT INTO scoring_rules (rule_name, rule_description, rule_type, action_type, base_points, max_daily_points, conditions) VALUES
('email_verification', 'تأیید ایمیل', 'kyc', 'email_verification', 2, NULL, '{}'),
('mobile_verification', 'تأیید موبایل', 'kyc', 'mobile_verification', 3, NULL, '{}'),
('profile_completion', 'تکمیل پروفایل', 'kyc', 'profile_completion', 5, NULL, '{"completion_percentage": 50}'),
('daily_login', 'ورود روزانه', 'activity', 'daily_login', 1, 1, '{}'),
('first_trade', 'انجام اولین معامله', 'activity', 'complete_first_trade', 5, NULL, '{}'),
('account_age_1_month', 'یک ماه فعالیت', 'loyalty', 'account_1_month_old', 5, NULL, '{"account_age_days": 30}'),
('account_age_6_months', 'شش ماه فعالیت', 'loyalty', 'account_6_months_old', 15, NULL, '{"account_age_days": 180}'),
('continuous_login_7_days', 'ورود ۷ روز متوالی', 'loyalty', 'continuous_login_7_days', 5, NULL, '{"login_streak": 7}');