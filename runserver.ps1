# runserver.ps1 - Script for running NOWEX Platform Servers
Write-Host "🚀 NOWEX Platform Startup Script" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Yellow

# بررسی وجود پوشه‌ها
if (-not (Test-Path "backend")) {
    Write-Host "❌ پوشه backend پیدا نشد!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "frontend")) {
    Write-Host "⚠️  پوشه frontend پیدا نشد - فقط backend اجرا می‌شود" -ForegroundColor Yellow
}

# نمایش وضعیت سرویس‌ها
Write-Host "`n📊 وضعیت سرویس‌ها:" -ForegroundColor Cyan
Write-Host "• Backend API: http://localhost:8001" -ForegroundColor White
Write-Host "• API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host "• Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "• Health Check: http://localhost:8001/health" -ForegroundColor White

# تابع برای اجرای Backend
function Start-Backend {
    Write-Host "`n🔧 راه‌اندازی Backend..." -ForegroundColor Magenta
    Set-Location "backend"
    
    # بررسی فعال بودن پورت 8001
    $portInUse = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Host "⚠️  پورت 8001 در حال استفاده است" -ForegroundColor Yellow
        Write-Host "تلاش برای متوقف کردن process..." -ForegroundColor Yellow
        Get-Process -Id ($portInUse.OwningProcess) -ErrorAction SilentlyContinue | Stop-Process -Force
        Start-Sleep 2
    }
    
    # اجرای سرور
    Write-Host "▶️  اجرای FastAPI Server..." -ForegroundColor Green
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
}

# تابع برای اجرای Frontend
function Start-Frontend {
    if (Test-Path "frontend") {
        Write-Host "`n🎨 راه‌اندازی Frontend..." -ForegroundColor Magenta
        Set-Location "frontend"
        
        # بررسی وجود package.json
        if (Test-Path "package.json") {
            Write-Host "▶️  اجرای React Development Server..." -ForegroundColor Green
            
            # بررسی نصب بودن dependencies
            if (-not (Test-Path "node_modules")) {
                Write-Host "📦 نصب dependencies..." -ForegroundColor Yellow
                npm install
            }
            
            # اجرای سرور توسعه
            npm start
        } else {
            Write-Host "❌ package.json پیدا نشد!" -ForegroundColor Red
        }
    }
}

# منوی اصلی
Write-Host "`n🎯 گزینه‌های اجرا:" -ForegroundColor Cyan
Write-Host "1. فقط Backend" -ForegroundColor White
Write-Host "2. فقط Frontend" -ForegroundColor White
Write-Host "3. هر دو (Backend + Frontend)" -ForegroundColor White
Write-Host "4. وضعیت سیستم" -ForegroundColor White
Write-Host "5. خروج" -ForegroundColor White

$choice = Read-Host "`nلطفاً عدد گزینه مورد نظر را وارد کنید"

switch ($choice) {
    "1" {
        Start-Backend
    }
    "2" {
        Start-Frontend
    }
    "3" {
        # اجرای هر دو در پنجره‌های جداگانه
        Write-Host "`n🔄 اجرای هر دو سرویس..." -ForegroundColor Cyan
        
        # Backend در پنجره جدید
        Start-Process PowerShell -ArgumentList "-NoExit -Command `"cd '$PWD\backend'; uvicorn main:app --host 0.0.0.0 --port 8001 --reload`""
        
        # Frontend در پنجره جدید (اگر وجود دارد)
        if (Test-Path "frontend") {
            Start-Sleep 3
            Start-Process PowerShell -ArgumentList "-NoExit -Command `"cd '$PWD\frontend'; npm start`""
        }
        
        Write-Host "✅ سرویس‌ها در حال اجرا هستند..." -ForegroundColor Green
        Write-Host "Backend: http://localhost:8001" -ForegroundColor White
        Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
    }
    "4" {
        # وضعیت سیستم
        Write-Host "`n📈 وضعیت سیستم:" -ForegroundColor Cyan
        
        # بررسی پورت Backend
        $backendStatus = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
        if ($backendStatus) {
            Write-Host "✅ Backend: در حال اجرا (پورت 8001)" -ForegroundColor Green
        } else {
            Write-Host "❌ Backend: متوقف" -ForegroundColor Red
        }
        
        # بررسی پورت Frontend
        $frontendStatus = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
        if ($frontendStatus) {
            Write-Host "✅ Frontend: در حال اجرا (پورت 3000)" -ForegroundColor Green
        } else {
            Write-Host "❌ Frontend: متوقف" -ForegroundColor Red
        }
        
        # بررسی دیتابیس
        try {
            $dbStatus = Get-NetTCPConnection -LocalPort 5432 -ErrorAction SilentlyContinue
            if ($dbStatus) {
                Write-Host "✅ PostgreSQL: در حال اجرا (پورت 5432)" -ForegroundColor Green
            } else {
                Write-Host "❌ PostgreSQL: متوقف" -ForegroundColor Red
            }
        } catch {
            Write-Host "⚠️  وضعیت PostgreSQL: نامشخص" -ForegroundColor Yellow
        }
        
        # بررسی Redis
        try {
            $redisStatus = Get-NetTCPConnection -LocalPort 6379 -ErrorAction SilentlyContinue
            if ($redisStatus) {
                Write-Host "✅ Redis: در حال اجرا (پورت 6379)" -ForegroundColor Green
            } else {
                Write-Host "❌ Redis: متوقف" -ForegroundColor Red
            }
        } catch {
            Write-Host "⚠️  وضعیت Redis: نامشخص" -ForegroundColor Yellow
        }
    }
    "5" {
        Write-Host "👋 خدانگهدار!" -ForegroundColor Cyan
        exit
    }
    default {
        Write-Host "❌ گزینه نامعتبر!" -ForegroundColor Red
    }
}