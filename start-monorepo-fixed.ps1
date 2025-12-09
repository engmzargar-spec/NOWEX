# NOWEX Monorepo Development Starter
Write-Host "=== NOWEX Platform Development ===" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Yellow
Write-Host "Monorepo Architecture with Turborepo" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "turbo.json")) {
    Write-Host "ERROR: Not in NOWEX Platform root directory!" -ForegroundColor Red
    Write-Host "Please run this script from D:\NOWEX-Platform" -ForegroundColor Yellow
    exit 1
}

Write-Host "Available Services:" -ForegroundColor Cyan
Write-Host "1. Admin Frontend (Next.js 15)" -ForegroundColor White
Write-Host "2. Backend API (FastAPI)" -ForegroundColor White  
Write-Host "3. All Services (Admin + Backend)" -ForegroundColor White
Write-Host "4. Build All Packages" -ForegroundColor White
Write-Host "5. Run Tests" -ForegroundColor White
Write-Host "6. Exit" -ForegroundColor White

$choice = Read-Host "`nSelect option (1-6)"

switch ($choice) {
    "1" {
        # Admin Frontend
        Write-Host "`n=== Starting Admin Frontend ===" -ForegroundColor Magenta
        Write-Host "URL: http://localhost:3000" -ForegroundColor White
        Write-Host "Login: admin@nowex.com / password123" -ForegroundColor White
        
        Set-Location "apps\admin-frontend"
        npm run dev
    }
    
    "2" {
        # Backend API
        Write-Host "`n=== Starting Backend API ===" -ForegroundColor Magenta
        Write-Host "API: http://localhost:8000" -ForegroundColor White
        Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor White
        
        Set-Location "backend"
        
        # Check if virtual environment exists
        if (Test-Path "venv") {
            Write-Host "Activating Python virtual environment..." -ForegroundColor Gray
            & .\venv\Scripts\Activate.ps1
        }
        else {
            Write-Host "NOTE: No virtual environment found. Using system Python." -ForegroundColor Yellow
        }
        
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    }
    
    "3" {
        # All Services
        Write-Host "`n=== Starting All Services ===" -ForegroundColor Cyan
        
        # Start Backend
        $backendJob = Start-Job -ScriptBlock {
            Set-Location $using:PWD\backend
            uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        }
        
        Write-Host "Backend starting... (waiting 3 seconds)" -ForegroundColor Gray
        Start-Sleep 3
        
        # Start Frontend
        $frontendJob = Start-Job -ScriptBlock {
            Set-Location $using:PWD\apps\admin-frontend
            npm run dev
        }
        
        Write-Host "`nSUCCESS: Services started!" -ForegroundColor Green
        Write-Host "`n=== Access URLs ===" -ForegroundColor Cyan
        Write-Host "Admin Panel:    http://localhost:3000" -ForegroundColor White
        Write-Host "Backend API:    http://localhost:8000" -ForegroundColor White
        Write-Host "API Docs:       http://localhost:8000/docs" -ForegroundColor White
        
        Write-Host "`n=== Login Credentials ===" -ForegroundColor Cyan
        Write-Host "Email:    admin@nowex.com" -ForegroundColor White
        Write-Host "Password: password123" -ForegroundColor White
        
        Write-Host "`n=== Monitoring ===" -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
        
        try {
            # Keep script running
            while ($true) {
                Start-Sleep 1
            }
        }
        finally {
            # Cleanup
            Stop-Job $backendJob -ErrorAction SilentlyContinue
            Stop-Job $frontendJob -ErrorAction SilentlyContinue
            Remove-Job $backendJob -ErrorAction SilentlyContinue
            Remove-Job $frontendJob -ErrorAction SilentlyContinue
        }
    }
    
    "4" {
        # Build All Packages
        Write-Host "`n=== Building All Packages ===" -ForegroundColor Magenta
        npm run build
        
        Write-Host "`nSUCCESS: Build completed!" -ForegroundColor Green
        Write-Host "Packages built:" -ForegroundColor White
        Write-Host "  - @nowex/ui" -ForegroundColor Gray
        Write-Host "  - @nowex/types" -ForegroundColor Gray
        Write-Host "  - @nowex/api" -ForegroundColor Gray
        Write-Host "  - admin-frontend" -ForegroundColor Gray
    }
    
    "5" {
        # Run Tests
        Write-Host "`n=== Running Tests ===" -ForegroundColor Magenta
        npm test
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`nSUCCESS: All tests passed!" -ForegroundColor Green
        }
        else {
            Write-Host "`nERROR: Some tests failed" -ForegroundColor Red
        }
    }
    
    "6" {
        Write-Host "`nGoodbye!" -ForegroundColor Cyan
    }
    
    default {
        Write-Host "`nERROR: Invalid option!" -ForegroundColor Red
        Write-Host "Please select 1-6" -ForegroundColor Yellow
    }
}