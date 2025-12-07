# server.ps1 - NOWEX Server Runner
Write-Host "NOWEX Platform Startup" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Yellow

Write-Host ""
Write-Host "Options:" -ForegroundColor Cyan
Write-Host "1. Start Backend only" -ForegroundColor White
Write-Host "2. Start Frontend only" -ForegroundColor White  
Write-Host "3. Start Both" -ForegroundColor White
Write-Host "4. Exit" -ForegroundColor White

$choice = Read-Host "Enter choice (1-4)"

if ($choice -eq "1") {
    Write-Host "Starting Backend..." -ForegroundColor Magenta
    Set-Location backend
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}
elseif ($choice -eq "2") {
    Write-Host "Starting Frontend..." -ForegroundColor Magenta
    Set-Location frontend
    npm start
}
elseif ($choice -eq "3") {
    Write-Host "Starting Both Services..." -ForegroundColor Cyan
    
    Start-Process PowerShell -ArgumentList "-NoExit -Command `"cd '$PWD\backend'; uvicorn main:app --host 0.0.0.0 --port 8000 --reload`""
    
    Start-Sleep 3
    
    if (Test-Path "frontend") {
        Start-Process PowerShell -ArgumentList "-NoExit -Command `"cd '$PWD\frontend'; npm start`""
    }
    
    Write-Host "Services starting..." -ForegroundColor Green
    Write-Host "Backend: http://localhost:8000" -ForegroundColor White
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
}
elseif ($choice -eq "4") {
    Write-Host "Goodbye!" -ForegroundColor Cyan
}
else {
    Write-Host "Invalid choice!" -ForegroundColor Red
}