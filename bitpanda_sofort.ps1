Write-Host "BITPANDA PAPER TRADING - SOFORT AUSFUEHRUNG" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Yellow

$startTime = Get-Date
Write-Host "Start Zeit: $startTime" -ForegroundColor Cyan

Write-Host "Fuehre Python Skript aus..." -ForegroundColor Yellow

try {
    # Führe das Python Skript aus und capture die Ausgabe
    $output = python signal_transmitter.py 2>&1
    
    Write-Host "Python Ausgabe:" -ForegroundColor Green
    Write-Host $output -ForegroundColor White
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "ERFOLGREICH AUSGEFUEHRT!" -ForegroundColor Green
    } else {
        Write-Host "FEHLER BEI AUSFUEHRUNG!" -ForegroundColor Red
    }
}
catch {
    Write-Host "FEHLER: $($_.Exception.Message)" -ForegroundColor Red
}

$endTime = Get-Date
$duration = $endTime - $startTime
Write-Host "Ende Zeit: $endTime" -ForegroundColor Cyan
Write-Host "Dauer: $($duration.TotalSeconds) Sekunden" -ForegroundColor Cyan

Write-Host "ABGESCHLOSSEN" -ForegroundColor Green
Write-Host "Druecken Sie eine Taste zum Beenden..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
