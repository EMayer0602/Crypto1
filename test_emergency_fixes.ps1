#!/usr/bin/env powershell

# EMERGENCY TEST SCRIPT
# Testet die 3 Hauptprobleme schnell

param(
    [switch]$OnlyTest,    # Nur Test-Modus ohne echte Automation
    [switch]$Verbose     # Ausführliche Ausgabe
)

Write-Host "🚨 EMERGENCY TEST - 3 Hauptprobleme" -ForegroundColor Red
Write-Host "1. SOL-EUR nicht umgeschaltet" -ForegroundColor Yellow
Write-Host "2. MAX nicht gewählt" -ForegroundColor Yellow  
Write-Host "3. BPS nicht gewählt" -ForegroundColor Yellow
Write-Host ""

# Move to script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

if ($OnlyTest) {
    Write-Host "🔍 NUR TEST-MODUS - keine echte Automation" -ForegroundColor Cyan
    python debug_fusion_complete.py
} else {
    Write-Host "⚡ VOLLTEST mit Emergency Fixes" -ForegroundColor Green
    
    # Alle Flags für maximale Debug-Ausgabe
    $Env:FUSION_DEBUG = '1'
    $Env:FUSION_DEEP_INPUT_DEBUG = '1'
    $Env:FUSION_SAFE_PREVIEW_MODE = '1'
    $Env:FUSION_WAIT_FOR_CLICK = '1'
    $Env:FUSION_AUTO_SUBMIT = '0'
    $Env:FUSION_FORCE_MAX_BUTTON = '1'
    $Env:FUSION_SELL_BPS_OFFSET = '-25'
    $Env:FUSION_USE_MAX_SELL_ONLY = '0'
    
    if ($Verbose) {
        Write-Host "Environment Flags:" -ForegroundColor Cyan
        Get-ChildItem Env:FUSION_* | Format-Table Name, Value -AutoSize
    }
    
    Write-Host "🚀 Starte Automation mit Emergency Fixes..." -ForegroundColor Green
    python .\fusion_existing_all_trades_auto.py
}

Write-Host ""
Write-Host "✅ Test abgeschlossen" -ForegroundColor Green
