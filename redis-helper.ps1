# Redis Setup Helper for JobRush
# This PowerShell script helps install and manage Redis via WSL

function Test-WSL {
    try {
        $version = wsl --version 2>$null
        return $true
    }
    catch {
        return $false
    }
}

function Install-Redis {
    Write-Host ""
    Write-Host "Installing Redis in WSL..." -ForegroundColor Yellow
    Write-Host ""
    
    wsl sudo apt-get update
    Write-Host ""
    wsl sudo apt-get install -y redis-server
    Write-Host ""
    
    Write-Host "Verifying installation..." -ForegroundColor Yellow
    wsl redis-cli --version
    
    Write-Host ""
    Write-Host "✓ Redis installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next: Run 'redis-helper start' to start Redis" -ForegroundColor Cyan
}

function Start-Redis {
    Write-Host ""
    Write-Host "Starting Redis..." -ForegroundColor Yellow
    
    wsl sudo service redis-server start
    Start-Sleep -Seconds 2
    
    Write-Host ""
    Write-Host "Verifying Redis is running..." -ForegroundColor Yellow
    $result = wsl redis-cli ping
    
    if ($result -eq "PONG") {
        Write-Host ""
        Write-Host "✓ Redis is running on localhost:6379" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now start the JobRush application:" -ForegroundColor Cyan
        Write-Host "  Terminal 1: cd DB & .venv\Scripts\Activate.ps1 & uvicorn main:app --host 127.0.0.1 --port 8000 --reload" -ForegroundColor Cyan
        Write-Host "  Terminal 2: cd DB & .venv\Scripts\Activate.ps1 & python worker.py" -ForegroundColor Cyan
        Write-Host "  Terminal 3: cd WebServer & dotnet watch run" -ForegroundColor Cyan
    }
    else {
        Write-Host ""
        Write-Host "✗ Failed to start Redis" -ForegroundColor Red
        Write-Host "Status result: $result" -ForegroundColor Red
    }
}

function Stop-Redis {
    Write-Host ""
    Write-Host "Stopping Redis..." -ForegroundColor Yellow
    
    wsl sudo service redis-server stop
    Start-Sleep -Seconds 1
    
    Write-Host "✓ Redis stopped" -ForegroundColor Green
}

function Get-RedisStatus {
    Write-Host ""
    Write-Host "Redis Status:" -ForegroundColor Yellow
    wsl sudo service redis-server status
}

function Show-Menu {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Redis Setup Helper for JobRush" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Install Redis (first time setup)" -ForegroundColor White
    Write-Host "2. Start Redis" -ForegroundColor White
    Write-Host "3. Check Redis status" -ForegroundColor White
    Write-Host "4. Stop Redis" -ForegroundColor White
    Write-Host ""
}

# Main script
if (-not (Test-WSL)) {
    Write-Host ""
    Write-Host "ERROR: WSL is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "To install WSL:" -ForegroundColor Yellow
    Write-Host "  1. Open PowerShell as Administrator"
    Write-Host "  2. Run: wsl --install"
    Write-Host "  3. Follow the prompts and restart your computer"
    Write-Host "  4. Run this script again after restart"
    Write-Host ""
    exit 1
}

# If argument provided, execute that command
if ($args.Count -gt 0) {
    switch ($args[0].ToLower()) {
        "install" { Install-Redis }
        "start" { Start-Redis }
        "stop" { Stop-Redis }
        "status" { Get-RedisStatus }
        default { 
            Write-Host "Unknown command: $($args[0])" -ForegroundColor Red
            Write-Host "Usage: .\redis-helper.ps1 [install|start|stop|status]" -ForegroundColor Yellow
        }
    }
}
else {
    # Interactive mode
    Show-Menu
    $choice = Read-Host "Enter your choice (1-4)"
    
    switch ($choice) {
        "1" { Install-Redis }
        "2" { Start-Redis }
        "3" { Get-RedisStatus }
        "4" { Stop-Redis }
        default { Write-Host "Invalid choice" -ForegroundColor Red }
    }
}
