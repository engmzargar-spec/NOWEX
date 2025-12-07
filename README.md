# NOWEX Platform - پلتفرم مدیریت صرافی نوکس

![NOWEX Platform](https://img.shields.io/badge/NOWEX-Platform-blue)
![Monorepo](https://img.shields.io/badge/Architecture-Monorepo-green)
![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black)
![TypeScript](https://img.shields.io/badge/Language-TypeScript-blue)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)

یک پلتفرم معاملاتی مدرن با معماری Monorepo و CI/CD Pipeline کاملا اتوماتیک.

## 🛠️ CI/CD Status

| Pipeline              | Status                                                                                                           | Description                        |
| --------------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| **Main CI/CD**        | ![CI/CD Pipeline](https://github.com/engmzargar-spec/NOWEX/actions/workflows/ci-main.yml/badge.svg)              | Unit Tests, Code Quality, Security |
| **Security Scan**     | ![Security Scan](https://github.com/engmzargar-spec/NOWEX/actions/workflows/security-scan.yml/badge.svg)         | Code & Dependency Security         |
| **Monorepo Build**    | ![Monorepo Build](https://img.shields.io/badge/Build-Passing-brightgreen)                                        | Turbo Build & Packages             |
| **TypeScript**        | ![TypeScript](https://img.shields.io/badge/TypeScript-Strict-blue)                                               | Type Safety                        |

## 🏗️ معماری مدرن (Monorepo)
NOWEX-Platform/
├── 📦 packages/ # Shared Packages
│ ├── shared-ui/ # کامپوننتهای UI مشترک
│ ├── shared-types/ # TypeScript types
│ └── shared-api/ # API client و hooks
│
├── 🚀 apps/ # Frontend Applications
│ ├── admin-frontend/ # پنل مدیریتی (Next.js 15) ✅
│ └── user-frontend/ # داشبورد کاربری (برنامهریزی شده)
│
├── ⚙️ backend/ # Backend Services (FastAPI)
├── 📚 docs/ # مستندات
├── 🐳 docker/ # Docker Configs
├── ⚡ turbo.json # Turborepo Config
└── 📄 package.json # Root Package

text

## ✅ وضعیت توسعه فعلی

### **فاز ۱: زیرساخت Monorepo (تکمیل شده)**
- ✅ ساختار Turborepo با workspaceهای جداگانه
- ✅ Shared packages: @nowex/ui, @nowex/types, @nowex/api
- ✅ Admin Frontend با Next.js 15 و App Router
- ✅ Layout کامل با Navigation و Header
- ✅ سیستم احراز هویت (JWT Mock)
- ✅ صفحه Dashboard با آمارهای کلی
- ✅ Routing و Protected Routes

### **فاز ۲: پنل مدیریتی (در حال توسعه)**
- 🚧 مدیریت کاربران (User Management)
- 🚧 سیستم تایید هویت (KYC)
- 🚧 گزارشهای مالی (Financial Reports)
- 🚧 سیستم امتیازدهی (Scoring)

## 🚀 راهاندازی سریع

```bash
# کلون کردن پروه
git clone https://github.com/engmzargar-spec/NOWEX.git
cd NOWEX

# نصب dependencies
npm install

# ساخت shared packages
npm run build

# راهاندازی Admin Frontend
cd apps/admin-frontend
npm run dev
آخرین بهروزرسانی: ۱۴۰۳/۱۰/۱۷
ورن: ۰.۱.۰ (آلفا)
وضعیت: فاز ۱ تکمیل شده فاز ۲ در حال توسعه
