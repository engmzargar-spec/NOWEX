# ============================================
# NOWEX Platform Startup Script (Final Version)
# ============================================

Write-Host "=== NOWEX Platform Startup ===" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Yellow

Write-Host ""
Write-Host "Options:" -ForegroundColor Cyan
Write-Host "1. Start Backend only" -ForegroundColor White
Write-Host "2. Start Admin Frontend only" -ForegroundColor White  
Write-Host "3. Start Both (Backend + Admin Frontend)" -ForegroundColor White
Write-Host "4. Exit" -ForegroundColor White

$choice = Read-Host "Enter choice (1-4)"

# --------------------------------------------
# 🔥 Correct Absolute Paths
# --------------------------------------------
$BackendPath = "D:\NOWEX-Platform\backend"
$FrontendPath = "D:\NOWEX-Platform\frontend\admin-frontend"

# --------------------------------------------
# 1) Backend Only
# --------------------------------------------
if ($choice -eq "1") {

    Write-Host ""
    Write-Host "Starting Backend..." -ForegroundColor Magenta
    Write-Host "Backend URL: http://localhost:8000" -ForegroundColor White
    Write-Host ""

    Set-Location $BackendPath
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

# --------------------------------------------
# 2) Admin Frontend Only
# --------------------------------------------
elseif ($choice -eq "2") {

    Write-Host ""
    Write-Host "Starting Admin Frontend..." -ForegroundColor Magenta
    Write-Host "Admin Panel: http://localhost:3000" -ForegroundColor White
    Write-Host ""

    Set-Location $FrontendPath
    npm run dev
}

# --------------------------------------------
# 3) Start Both
# --------------------------------------------
elseif ($choice -eq "3") {

    Write-Host ""
    Write-Host "Starting Both Services..." -ForegroundColor Cyan

    # Backend window
    $backendScript = @"
cd '$BackendPath'
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"@

    Start-Process PowerShell -ArgumentList "-NoExit -Command `"$backendScript`""

    Start-Sleep 3

    # Frontend window
    $frontendScript = @"
cd '$FrontendPath'
npm run dev
"@

    Start-Process PowerShell -ArgumentList "-NoExit -Command `"$frontendScript`""

    Write-Host ""
    Write-Host "✅ Services starting..." -ForegroundColor Green
}

# --------------------------------------------
# 4) Exit
# --------------------------------------------
elseif ($choice -eq "4") {
    Write-Host "Goodbye!" -ForegroundColor Cyan
}

# --------------------------------------------
# Invalid Input
# --------------------------------------------
else {
    Write-Host "Invalid choice!" -ForegroundColor Red
}
