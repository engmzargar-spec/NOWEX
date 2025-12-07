-- database/init.sql
-- ایجاد اسکیماهای اصلی اگر وجود ندارند
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS wallet;

-- ایجاد اکستنشن برای تولید UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- (جداول در مراحل بعدی و با استفاده از Alembic ایجاد خواهند شد)
-- این فایل در حال حاضر خالی است و برای عملیات اولیه کافی است.