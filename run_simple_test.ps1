#!/usr/bin/env powershell

# SUPER EINFACHER TEST - NUR DIE 3 PROBLEME
# Ignoriert alle komplexen Features

Write-Host "🎯 SUPER EINFACHER TEST" -ForegroundColor Green
Write-Host "Nur: SOL-EUR + MAX + BPS" -ForegroundColor Yellow
Write-Host ""

# Move to script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# NUR die wichtigsten Flags - NICHTS ANDERES
$Env:FUSION_SAFE_PREVIEW_MODE = '1'      # Sicherheit
$Env:FUSION_WAIT_FOR_CLICK = '1'         # Sicherheit
$Env:FUSION_AUTO_SUBMIT = '0'            # Sicherheit
$Env:FUSION_DEBUG = '1'                  # Debug
$Env:FUSION_FORCE_MAX_BUTTON = '1'       # MAX erzwingen
$Env:FUSION_SELL_BPS_OFFSET = '-25'      # SELL: -25bps
$Env:FUSION_USE_MAX_SELL_ONLY = '0'      # MAX für alle

# Alle anderen Flags löschen
Get-ChildItem Env:FUSION_* | Where-Object { $_.Name -notin @(
    'FUSION_SAFE_PREVIEW_MODE', 
    'FUSION_WAIT_FOR_CLICK', 
    'FUSION_AUTO_SUBMIT',
    'FUSION_DEBUG',
    'FUSION_FORCE_MAX_BUTTON',
    'FUSION_SELL_BPS_OFFSET',
    'FUSION_USE_MAX_SELL_ONLY'
)} | Remove-Item

Write-Host "🚀 Starte mit minimalen Flags..." -ForegroundColor Cyan
python .\fusion_existing_all_trades_auto.py
