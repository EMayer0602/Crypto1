# NUCLEAR STOP - Kill ALL Python processes
Write-Host "🚨 NUCLEAR STOP: Killing ALL Python processes" -ForegroundColor Red
Write-Host "This will stop all Python scripts including the one sending 2024 signals"

# Get all Python processes
$pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "Found $($pythonProcesses.Count) Python processes:" -ForegroundColor Yellow
    
    foreach ($proc in $pythonProcesses) {
        Write-Host "  PID: $($proc.Id) | Started: $($proc.StartTime)" -ForegroundColor Cyan
    }
    
    Write-Host "`n💥 Killing all Python processes..." -ForegroundColor Red
    
    # Kill all Python processes
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ All Python processes terminated" -ForegroundColor Green
    
} else {
    Write-Host "No Python processes found running" -ForegroundColor Yellow
}

Write-Host "`n🔍 Checking if any processes remain..."
$remainingProcesses = Get-Process -Name python -ErrorAction SilentlyContinue

if ($remainingProcesses) {
    Write-Host "⚠️ Some processes still running - trying taskkill" -ForegroundColor Yellow
    taskkill /F /IM python.exe /T
} else {
    Write-Host "✅ All Python processes successfully stopped" -ForegroundColor Green
}

Write-Host "`n💡 The 'Cycle X' messages should now stop appearing"
Write-Host "🚀 You can now start fresh with: python simple_daily_trader.py"
