# NOWEX Trading Platform

یک پلتفرم معاملاتی مدرن، ایمن و مقیاس‌پذیر با CI/CD Pipeline کاملاً اتوماتیک.

## 🛠️ CI/CD Status

| Pipeline              | Status                                                                                                           | Description                        |
| --------------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| **Main CI/CD**        | ![CI/CD Pipeline](https://github.com/engmzargar-spec/NOWEX/actions/workflows/ci-main.yml/badge.svg)              | Unit Tests, Code Quality, Security |
| **Security Scan**     | ![Security Scan](https://github.com/engmzargar-spec/NOWEX/actions/workflows/security-scan.yml/badge.svg)         | Code & Dependency Security         |
| **Integration Tests** | ![Integration Tests](https://github.com/engmzargar-spec/NOWEX/actions/workflows/integration-tests.yml/badge.svg) | API & Integration Testing          |
| **Smoke Test**        | ![Smoke Test](https://github.com/engmzargar-spec/NOWEX/actions/workflows/smoke-test.yml/badge.svg)               | Basic Health Checks                |
| **Deployment**        | ![Deployment](https://github.com/engmzargar-spec/NOWEX/actions/workflows/deploy.yml/badge.svg)                   | Environment Deployment             |

## 📋 Pipeline Overview

```mermaid
graph TD
    A[Commit/Push] --> B[CI/CD Main Pipeline]
    B --> C[Unit Tests & Code Quality]
    B --> D[Security Scanning]
    C --> E[Integration Tests]
    D --> E
    E --> F{All Tests Pass?}
    F -->|Yes| G[Deploy to Staging]
    F -->|No| H[Fail & Notify]
    G --> I[Smoke Tests]
    I --> J{Smoke Tests Pass?}
    J -->|Yes| K[Approval for Production]
    J -->|No| L[Auto Rollback]
    K --> M[Deploy to Production]
```
