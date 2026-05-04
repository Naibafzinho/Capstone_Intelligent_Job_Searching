@echo off
REM Redis Installation and Startup Helper Script
REM This script helps install and manage Redis via WSL

setlocal enabledelayedexpansion

echo.
echo ============================================
echo Redis Setup Helper for JobRush
echo ============================================
echo.

REM Check if WSL is installed
wsl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: WSL is not installed or not in PATH
    echo.
    echo To install WSL:
    echo   1. Open PowerShell as Administrator
    echo   2. Run: wsl --install
    echo   3. Follow the prompts and restart your computer
    echo   4. Run this script again after restart
    echo.
    pause
    exit /b 1
)

echo WSL is installed. Proceeding...
echo.

REM Check what the user wants to do
echo What would you like to do?
echo.
echo 1. Install Redis (first time setup)
echo 2. Start Redis
echo 3. Check Redis status
echo 4. Stop Redis
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto start
if "%choice%"=="3" goto status
if "%choice%"=="4" goto stop
echo Invalid choice. Exiting.
exit /b 1

:install
echo.
echo Installing Redis in WSL...
echo.
wsl sudo apt-get update
wsl sudo apt-get install -y redis-server
wsl redis-cli --version
echo.
echo ✓ Redis installed successfully!
echo.
echo Next step: Run this script again and choose option 2 to start Redis.
pause
exit /b 0

:start
echo.
echo Starting Redis...
wsl sudo service redis-server start
timeout /t 1 /nobreak
echo.
echo Verifying Redis is running...
wsl redis-cli ping
if %errorlevel% equ 0 (
    echo.
    echo ✓ Redis is running on localhost:6379
    echo.
    echo You can now start the JobRush application:
    echo   Terminal 1: cd DB ^& .venv\Scripts\Activate.ps1 ^& uvicorn main:app --host 127.0.0.1 --port 8000 --reload
    echo   Terminal 2: cd DB ^& .venv\Scripts\Activate.ps1 ^& python worker.py
    echo   Terminal 3: cd WebServer ^& dotnet watch run
) else (
    echo.
    echo ✗ Failed to start Redis
    echo Please check the error messages above
)
pause
exit /b 0

:status
echo.
echo Checking Redis status...
wsl sudo service redis-server status
echo.
pause
exit /b 0

:stop
echo.
echo Stopping Redis...
wsl sudo service redis-server stop
timeout /t 1 /nobreak
echo.
echo Verifying Redis is stopped...
wsl redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo ✓ Redis stopped
) else (
    echo ✗ Redis is still running
)
echo.
pause
exit /b 0
