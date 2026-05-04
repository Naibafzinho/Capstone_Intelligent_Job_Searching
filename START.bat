@echo off
REM JobRush Quick Start Script
REM This script helps you start all necessary services

setlocal enabledelayedexpansion

echo.
echo ============================================
echo JobRush Quick Start Guide
echo ============================================
echo.
echo This script will help you start the JobRush application.
echo Before proceeding, ensure that:
echo   1. MongoDB is running
echo   2. Redis is running on port 6379
echo   3. Your .env file is configured with MONGODB_URI
echo.

REM Check if .venv exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run the setup first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate.bat
    echo   pip install -r DB/requirements.txt
    pause
    exit /b 1
)

REM Check services
echo Checking if services are running...
echo.

cd DB
.venv\Scripts\activate.bat
python check_services.py
cd ..

echo.
pause /prompt "Press ENTER to continue with startup..."
echo.

REM Start services in separate windows
echo Starting services...
echo.

REM Terminal 1: DB API Server
echo Starting DB API Server (Terminal 1)...
start cmd /k "cd DB && .venv\Scripts\activate.bat && uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 2 /nobreak

REM Terminal 2: Worker
echo Starting Worker (Terminal 2)...
start cmd /k "cd DB && .venv\Scripts\activate.bat && python worker.py"
timeout /t 2 /nobreak

REM Terminal 3: WebServer
echo Starting WebServer (Terminal 3)...
start cmd /k "cd WebServer && dotnet watch run"

echo.
echo ============================================
echo Services started!
echo ============================================
echo.
echo DB API:   http://127.0.0.1:8000
echo WebServer: http://localhost:5168
echo.
echo All terminal windows have been opened.
echo Keep them open while the application is running.
echo.
pause /prompt "Press ENTER to close this window..."
