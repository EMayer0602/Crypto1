param(
    [string]$TradesFile = '',
    [int]$IncludeLastDays = 0,   # 0 = only today; 1 = today + yesterday; 2 = today + last 2 days, ...
    [switch]$AllowPast,           # must be set to allow IncludeLastDays > 0
    [switch]$Debug,               # enable verbose DEBUG logs in Python
    [switch]$DeepDebug            # enable deep input/JS debug logs
)

Write-Host "🚨🚨🚨 ULTIMATE SAFETY MODE - NIEMALS ORDERS ÜBERTRAGEN! 🚨🚨🚨" -ForegroundColor Red -BackgroundColor Yellow
Write-Host "✋✋✋ NUR PREVIEW - ABSOLUTE NOTBREMSE AKTIV! ✋✋✋" -ForegroundColor Red
Write-Host ""

# Move to script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# 🚨🚨🚨 ABSOLUTE SAFETY FLAGS 🚨🚨🚨
$Env:FUSION_SAFE_PREVIEW_MODE = '1'      # ULTIMATE SAFETY
$Env:FUSION_WAIT_FOR_CLICK     = '1'      # ULTIMATE SAFETY
$Env:FUSION_AUTO_SUBMIT        = '0'      # ULTIMATE SAFETY
$Env:FUSION_AUTO_CONTINUE      = '0'      # ULTIMATE SAFETY

# 🔒🔒🔒 EXTRA SAFETY LOCKS 🔒🔒🔒
$Env:FUSION_PAPER_MODE         = '1'      # Zusätzlicher Schutz
$Env:FUSION_EMERGENCY_STOP     = '1'      # Notbremse
$Env:FUSION_PREVIEW_ONLY       = '1'      # Nur Vorschau
$Env:FUSION_NO_SUBMIT          = '1'      # Nie absenden
$Env:FUSION_BLOCK_REVIEW       = '1'      # Review blockieren

# Working features (SOL-EUR, MAX, BPS)
$Env:FUSION_USE_MAX            = '1'
$Env:FUSION_USE_BPS            = '1'
$Env:FUSION_FORCE_MAX_BUTTON   = '1'      # MAX Button immer aktivieren
$Env:FUSION_SELL_BPS_OFFSET    = '-25'    # SELL: -25bps (unter Marktpreis)
$Env:FUSION_USE_MAX_SELL_ONLY  = '0'      # MAX für alle Seiten (BUY+SELL)

# Safety and filters
$Env:FUSION_STRICT_EUR_ONLY    = '1'      # Only *-EUR pairs
$Env:FUSION_PORTFOLIO_CHECK    = '1'      # Adjust SELL qty to holdings
$Env:FUSION_DISABLE_SELLS      = '0'      # Allow SELLs (prefixed)
$Env:FUSION_SELL_CONFIRM       = '0'      # No extra SELL confirmation prompts (prefixed)
$Env:DISABLE_SELLS             = '0'
$Env:SELL_CONFIRM              = '0'
$Env:FUSION_INCLUDE_LAST_DAYS  = [string]$IncludeLastDays
$Env:FUSION_BACKTEST_MODE      = '0'      # Live UI mode

# Diagnostics
$Env:FUSION_DEBUG              = $(if ($Debug) { '1' } else { '0' })
$Env:FUSION_DEEP_INPUT_DEBUG   = $(if ($DeepDebug) { '1' } else { '0' })

# Optional: force a specific trades file
if ($TradesFile) {
    $Env:FUSION_TRADES_FILE = $TradesFile
}

# Allow past days policy
if ($AllowPast -and $IncludeLastDays -gt 0) {
    $Env:FUSION_ALLOW_PAST_DAYS = '1'
    $Env:FUSION_ALLOW_PAST      = '1'
} else {
    $Env:FUSION_ALLOW_PAST_DAYS = '0'
    $Env:FUSION_ALLOW_PAST      = '0'
}

# Echo safety summary
Write-Host "🔐 ULTIMATE SAFETY: SAFE=$($Env:FUSION_SAFE_PREVIEW_MODE) | PAPER=$($Env:FUSION_PAPER_MODE) | AUTO_SUBMIT=$($Env:FUSION_AUTO_SUBMIT)" -ForegroundColor Green
Write-Host "📊 FEATURES: INCLUDE_LAST_DAYS=$IncludeLastDays | DEBUG=$($Env:FUSION_DEBUG) | FORCE_MAX=$($Env:FUSION_FORCE_MAX_BUTTON)" -ForegroundColor Cyan
Write-Host ""

Write-Host "🚀 Starte ULTRA-SICHERE Automation (NUR PREVIEW)..." -ForegroundColor Green

# Launch the automation (ULTIMATE SAFETY ensures NO execution)
python .\fusion_existing_all_trades_auto.py

Write-Host ""
Write-Host "✅ ABGESCHLOSSEN - ALLE ORDERS NUR VORBEREITET, NIEMALS ÜBERTRAGEN!" -ForegroundColor Green -BackgroundColor Black
