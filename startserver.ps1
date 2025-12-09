# server.ps1 - NOWEX Server Runner (Monorepo Version)
Write-Host "=== NOWEX Platform Startup ===" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Yellow

Write-Host ""
Write-Host "Options:" -ForegroundColor Cyan
Write-Host "1. Start Backend only" -ForegroundColor White
Write-Host "2. Start Admin Frontend only" -ForegroundColor White  
Write-Host "3. Start Both (Backend + Admin Frontend)" -ForegroundColor White
Write-Host "4. Exit" -ForegroundColor White

$choice = Read-Host "Enter choice (1-4)"

if ($choice -eq "1") {
    # Start Backend
    Write-Host ""
    Write-Host "Starting Backend..." -ForegroundColor Magenta
    Write-Host "Backend URL: http://localhost:8000" -ForegroundColor White
    Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    
    Set-Location backend
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}
elseif ($choice -eq "2") {
    # Start Admin Frontend
    Write-Host ""
    Write-Host "Starting Admin Frontend..." -ForegroundColor Magenta
    Write-Host "Admin Panel: http://localhost:3000" -ForegroundColor White
    Write-Host "Login: admin@nowex.com / password123" -ForegroundColor White
    Write-Host ""
    
    Set-Location "apps\admin-frontend"
    npm run dev
}
elseif ($choice -eq "3") {
    # Start Both Services
    Write-Host ""
    Write-Host "Starting Both Services..." -ForegroundColor Cyan
    
    # Start Backend in new PowerShell window
    Write-Host "Launching Backend..." -ForegroundColor Yellow
    $backendScript = @"
cd '$PWD\backend'
Write-Host '=== NOWEX Backend ===' -ForegroundColor Green
Write-Host 'Server: http://localhost:8000' -ForegroundColor White
Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor White
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
Write-Host ''
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"@
    
    Start-Process PowerShell -ArgumentList "-NoExit -Command `"$backendScript`"" -WindowStyle Normal
    
    # Wait for backend to start
    Write-Host "Waiting for Backend to initialize (3 seconds)..." -ForegroundColor Gray
    Start-Sleep 3
    
    # Start Admin Frontend in new PowerShell window
    Write-Host "Launching Admin Frontend..." -ForegroundColor Yellow
    $frontendScript = @"
cd '$PWD\apps\admin-frontend'
Write-Host '=== NOWEX Admin Frontend ===' -ForegroundColor Green
Write-Host 'URL: http://localhost:3000' -ForegroundColor White
Write-Host 'Login: admin@nowex.com / password123' -ForegroundColor White
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
Write-Host ''
npm run dev
"@
    
    Start-Process PowerShell -ArgumentList "-NoExit -Command `"$frontendScript`"" -WindowStyle Normal
    
    Write-Host ""
    Write-Host "✅ Services starting in separate windows..." -ForegroundColor Green
    Write-Host ""
    Write-Host "=== Access URLs ===" -ForegroundColor Cyan
    Write-Host "Backend API:    http://localhost:8000" -ForegroundColor White
    Write-Host "Admin Panel:    http://localhost:3000" -ForegroundColor White
    Write-Host ""
    Write-Host "=== Login Credentials ===" -ForegroundColor Cyan
    Write-Host "Email: admin@nowex.com" -ForegroundColor White
    Write-Host "Password: password123" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Enter to return to main menu..."
    Read-Host
}
elseif ($choice -eq "4") {
    Write-Host ""
    Write-Host "Goodbye!" -ForegroundColor Cyan
}
else {
    Write-Host ""
    Write-Host "Invalid choice!" -ForegroundColor Red
    Write-Host "Please enter 1, 2, 3, or 4" -ForegroundColor Yellow
}