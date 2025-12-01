# ایجاد پوشه‌های اصلی برای سیستم KYC
Write-Host "Creating KYC System Directory Structure..." -ForegroundColor Green

# پوشه‌های اصلی در backend/apps/
$kycFolders = @(
    "backend/apps/kyc/models",
    "backend/apps/kyc/routes", 
    "backend/apps/kyc/schemas",
    "backend/apps/kyc/services",
    "backend/apps/kyc/tests",
    
    "backend/apps/scoring/models",
    "backend/apps/scoring/routes",
    "backend/apps/scoring/schemas", 
    "backend/apps/scoring/services",
    "backend/apps/scoring/tests",
    
    "backend/apps/referral/models",
    "backend/apps/referral/routes",
    "backend/apps/referral/schemas",
    "backend/apps/referral/services",
    "backend/apps/referral/tests"
)

# ایجاد پوشه‌ها
foreach ($folder in $kycFolders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force
        Write-Host "Created: $folder" -ForegroundColor Yellow
    } else {
        Write-Host "Already exists: $folder" -ForegroundColor Gray
    }
}

# پوشه‌های دیتابیس
$dbFolders = @(
    "database/migrations/kyc_migrations",
    "database/seeds"
)

foreach ($folder in $dbFolders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force
        Write-Host "Created: $folder" -ForegroundColor Yellow
    } else {
        Write-Host "Already exists: $folder" -ForegroundColor Gray
    }
}

# پوشه‌های فرانت‌اند
$frontendFolders = @(
    "frontend/src/pages/kyc",
    "frontend/src/components/kyc", 
    "frontend/src/services/api",
    "frontend/src/services/kyc"
)

foreach ($folder in $frontendFolders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force
        Write-Host "Created: $folder" -ForegroundColor Yellow
    } else {
        Write-Host "Already exists: $folder" -ForegroundColor Gray
    }
}

# ایجاد فایل‌های __init__.py
Write-Host "`nCreating __init__.py files..." -ForegroundColor Green

$initFiles = @(
    "backend/apps/kyc/__init__.py",
    "backend/apps/kyc/models/__init__.py",
    "backend/apps/kyc/routes/__init__.py", 
    "backend/apps/kyc/schemas/__init__.py",
    "backend/apps/kyc/services/__init__.py",
    "backend/apps/kyc/tests/__init__.py",
    
    "backend/apps/scoring/__init__.py",
    "backend/apps/scoring/models/__init__.py",
    "backend/apps/scoring/routes/__init__.py",
    "backend/apps/scoring/schemas/__init__.py",
    "backend/apps/scoring/services/__init__.py",
    "backend/apps/scoring/tests/__init__.py",
    
    "backend/apps/referral/__init__.py", 
    "backend/apps/referral/models/__init__.py",
    "backend/apps/referral/routes/__init__.py",
    "backend/apps/referral/schemas/__init__.py",
    "backend/apps/referral/services/__init__.py",
    "backend/apps/referral/tests/__init__.py"
)

foreach ($file in $initFiles) {
    if (!(Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force
        Write-Host "Created: $file" -ForegroundColor Cyan
    } else {
        Write-Host "Already exists: $file" -ForegroundColor Gray
    }
}

# ایجاد فایل‌های اصلی مدل‌ها
Write-Host "`nCreating main model files..." -ForegroundColor Green

$modelFiles = @{
    "backend/apps/kyc/models/kyc_models.py" = "# مدل‌های اصلی KYC"
    "backend/apps/kyc/models/kyc_verification.py" = "# مدل تأییدیه‌های KYC"
    "backend/apps/kyc/models/user_profile.py" = "# مدل پروفایل کاربری"
    "backend/apps/kyc/models/kyc_state_machine.py" = "# State Machine برای KYC"
    
    "backend/apps/scoring/models/scoring_models.py" = "# مدل‌های امتیازدهی"
    "backend/apps/scoring/models/user_score.py" = "# مدل امتیاز کاربر"
    "backend/apps/scoring/models/score_benefits.py" = "# مدل مزایای امتیازی"
    
    "backend/apps/referral/models/referral_models.py" = "# مدل‌های سیستم رفرال"
    "backend/apps/referral/models/referral_program.py" = "# مدل برنامه رفرال"
}

foreach ($file in $modelFiles.GetEnumerator()) {
    if (!(Test-Path $file.Key)) {
        $content = "# " + $file.Value + "`n# Created: $(Get-Date)`n`n"
        Set-Content -Path $file.Key -Value $content
        Write-Host "Created: $($file.Key)" -ForegroundColor Cyan
    } else {
        Write-Host "Already exists: $($file.Key)" -ForegroundColor Gray
    }
}

# ایجاد فایل‌های routes
Write-Host "`nCreating route files..." -ForegroundColor Green

$routeFiles = @{
    "backend/apps/kyc/routes/kyc_routes.py" = "API های KYC برای کاربران"
    "backend/apps/kyc/routes/kyc_admin_routes.py" = "API های مدیریت KYC برای ادمین"
    "backend/apps/kyc/routes/profile_routes.py" = "API های پروفایل کاربری"
    
    "backend/apps/scoring/routes/scoring_routes.py" = "API های امتیازدهی"
    "backend/apps/scoring/routes/benefits_routes.py" = "API های مزایای امتیازی"
    
    "backend/apps/referral/routes/referral_routes.py" = "API های سیستم رفرال"
    "backend/apps/referral/routes/referral_admin_routes.py" = "API های مدیریت رفرال"
}

foreach ($file in $routeFiles.GetEnumerator()) {
    if (!(Test-Path $file.Key)) {
        $content = "# " + $file.Value + "`n# Created: $(Get-Date)`n`n"
        Set-Content -Path $file.Key -Value $content
        Write-Host "Created: $($file.Key)" -ForegroundColor Cyan
    } else {
        Write-Host "Already exists: $($file.Key)" -ForegroundColor Gray
    }
}

# ایجاد فایل‌های services
Write-Host "`nCreating service files..." -ForegroundColor Green

$serviceFiles = @{
    "backend/apps/kyc/services/kyc_service.py" = "سرویس اصلی KYC"
    "backend/apps/kyc/services/profile_service.py" = "سرویس پروفایل کاربری"
    "backend/apps/kyc/services/verification_service.py" = "سرویس تأییدیه‌ها"
    "backend/apps/kyc/services/document_service.py" = "سرویس مدیریت مدارک"
    "backend/apps/kyc/services/kyc_state_service.py" = "سرویس State Machine"
    
    "backend/apps/scoring/services/scoring_engine.py" = "موتور امتیازدهی"
    "backend/apps/scoring/services/score_calculator.py" = "ماشین حساب امتیاز"
    "backend/apps/scoring/services/benefits_service.py" = "سرویس مزایای امتیازی"
    
    "backend/apps/referral/services/referral_service.py" = "سرویس اصلی رفرال"
    "backend/apps/referral/services/referral_codes.py" = "مدیریت کدهای معرف"
    "backend/apps/referral/services/referral_rewards.py" = "مدیریت پاداش‌های رفرال"
}

foreach ($file in $serviceFiles.GetEnumerator()) {
    if (!(Test-Path $file.Key)) {
        $content = "# " + $file.Value + "`n# Created: $(Get-Date)`n`n"
        Set-Content -Path $file.Key -Value $content
        Write-Host "Created: $($file.Key)" -ForegroundColor Cyan
    } else {
        Write-Host "Already exists: $($file.Key)" -ForegroundColor Gray
    }
}

# ایجاد فایل‌های schemas
Write-Host "`nCreating schema files..." -ForegroundColor Green

$schemaFiles = @{
    "backend/apps/kyc/schemas/kyc_schemas.py" = "Schemas برای KYC"
    "backend/apps/kyc/schemas/profile_schemas.py" = "Schemas برای پروفایل"
    "backend/apps/kyc/schemas/verification_schemas.py" = "Schemas برای تأییدیه‌ها"
    
    "backend/apps/scoring/schemas/scoring_schemas.py" = "Schemas برای امتیازدهی"
    "backend/apps/scoring/schemas/benefits_schemas.py" = "Schemas برای مزایا"
    
    "backend/apps/referral/schemas/referral_schemas.py" = "Schemas برای رفرال"
}

foreach ($file in $schemaFiles.GetEnumerator()) {
    if (!(Test-Path $file.Key)) {
        $content = "# " + $file.Value + "`n# Created: $(Get-Date)`n`n"
        Set-Content -Path $file.Key -Value $content
        Write-Host "Created: $($file.Key)" -ForegroundColor Cyan
    } else {
        Write-Host "Already exists: $($file.Key)" -ForegroundColor Gray
    }
}

# ایجاد فایل‌های فرانت‌اند
Write-Host "`nCreating frontend files..." -ForegroundColor Green

$frontendFiles = @{
    "frontend/src/pages/kyc/KYCVerification.jsx" = "صفحه اصلی KYC"
    "frontend/src/pages/kyc/ProfileCompletion.jsx" = "تکمیل پروفایل"
    "frontend/src/pages/kyc/DocumentUpload.jsx" = "آپلود مدارک"
    "frontend/src/pages/kyc/KYCStatus.jsx" = "وضعیت KYC"
    "frontend/src/pages/kyc/KYCSuccess.jsx" = "صفحه موفقیت"
    
    "frontend/src/components/kyc/KYCProgress.jsx" = "نوار پیشرفت KYC"
    "frontend/src/components/kyc/DocumentUploader.jsx" = "کامپوننت آپلود مدارک"
    "frontend/src/components/kyc/VerificationSteps.jsx" = "مراحل تأیید"
    "frontend/src/components/kyc/ScoreDisplay.jsx" = "نمایش امتیاز"
    
    "frontend/src/services/api/kycApi.js" = "API calls برای KYC"
    "frontend/src/services/api/scoringApi.js" = "API calls برای امتیاز"
    "frontend/src/services/api/referralApi.js" = "API calls برای رفرال"
    
    "frontend/src/services/kyc/kycService.js" = "سرویس KYC در فرانت‌اند"
    "frontend/src/services/kyc/documentService.js" = "مدیریت مدارک در فرانت‌اند"
}

foreach ($file in $frontendFiles.GetEnumerator()) {
    if (!(Test-Path $file.Key)) {
        $content = "// " + $file.Value + "`n// Created: $(Get-Date)`n`n"
        Set-Content -Path $file.Key -Value $content
        Write-Host "Created: $($file.Key)" -ForegroundColor Cyan
    } else {
        Write-Host "Already exists: $($file.Key)" -ForegroundColor Gray
    }
}

# ایجاد فایل‌های مایگریشن دیتابیس
Write-Host "`nCreating database migration files..." -ForegroundColor Green

$migrationFiles = @{
    "database/migrations/kyc_migrations/001_initial_kyc_tables.sql" = "ایجاد جداول اولیه KYC"
    "database/migrations/kyc_migrations/002_scoring_tables.sql" = "ایجاد جداول امتیازدهی"
    "database/migrations/kyc_migrations/003_referral_tables.sql" = "ایجاد جداول رفرال"
    
    "database/seeds/kyc_seed_data.sql" = "دیتای اولیه KYC"
    "database/seeds/scoring_levels_seed.sql" = "دیتای سطوح امتیازی"
    "database/seeds/referral_rewards_seed.sql" = "دیتای پاداش‌های رفرال"
}

foreach ($file in $migrationFiles.GetEnumerator()) {
    if (!(Test-Path $file.Key)) {
        $content = "-- " + $file.Value + "`n-- Created: $(Get-Date)`n`n"
        Set-Content -Path $file.Key -Value $content
        Write-Host "Created: $($file.Key)" -ForegroundColor Cyan
    } else {
        Write-Host "Already exists: $($file.Key)" -ForegroundColor Gray
    }
}

# ایجاد فایل تست
Write-Host "`nCreating test files..." -ForegroundColor Green

$testFiles = @{
    "backend/apps/kyc/tests/test_kyc_models.py" = "تست مدل‌های KYC"
    "backend/apps/kyc/tests/test_kyc_routes.py" = "تست routes های KYC"
    "backend/apps/kyc/tests/test_kyc_service.py" = "تست سرویس‌های KYC"
    
    "backend/apps/scoring/tests/test_scoring_engine.py" = "تست موتور امتیازدهی"
    "backend/apps/scoring/tests/test_scoring_routes.py" = "تست routes های امتیازدهی"
    
    "backend/apps/referral/tests/test_referral_service.py" = "تست سرویس رفرال"
}

foreach ($file in $testFiles.GetEnumerator()) {
    if (!(Test-Path $file.Key)) {
        $content = "# " + $file.Value + "`n# Created: $(Get-Date)`n`n"
        Set-Content -Path $file.Key -Value $content
        Write-Host "Created: $($file.Key)" -ForegroundColor Cyan
    } else {
        Write-Host "Already exists: $($file.Key)" -ForegroundColor Gray
    }
}

Write-Host "`n✅ Directory structure created successfully!" -ForegroundColor Green
Write-Host "📁 Total KYC modules created: 3 (KYC, Scoring, Referral)" -ForegroundColor Yellow
Write-Host "📄 Total files created: $($modelFiles.Count + $routeFiles.Count + $serviceFiles.Count + $schemaFiles.Count + $frontendFiles.Count + $migrationFiles.Count + $testFiles.Count)" -ForegroundColor Yellow
Write-Host "`n🎯 Next step: Start implementing the core models and services" -ForegroundColor Cyan