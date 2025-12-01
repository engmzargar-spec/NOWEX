@echo off
chcp 65001 >nul
echo 🚀 NOWEX Platform Startup Script
echo ==========================================

cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

pause