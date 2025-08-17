param(
    [string]$TradesFile = '',
    [int]$IncludeLastDays = 0,   # 0 = only today; 1 = today + yesterday; 2 = today + last 2 days, ...
    [switch]$AllowPast,           # must be set to allow IncludeLastDays > 0
    [switch]$Debug,               # enable verbose DEBUG logs in Python
    [switch]$DeepDebug            # enable deep input/JS debug logs
)

Write-Host "⚠️ LIVE MODE – SAFETIES OFF (Review/Submit enabled)" -ForegroundColor Yellow

# Move to script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Live execution: no preview/paper, no manual wait, auto-continue and auto-submit
$Env:FUSION_SAFE_PREVIEW_MODE = '0'
$Env:FUSION_PAPER_MODE        = '0'
$Env:FUSION_WAIT_FOR_CLICK    = '0'
$Env:FUSION_AUTO_SUBMIT       = '1'
$Env:FUSION_AUTO_CONTINUE     = '1'

# Behavior: robust filling with MAX/BPS
$Env:FUSION_TAB_NAV            = '1'
$Env:FUSION_STRICT_TAB_STEPS   = '0'
$Env:FUSION_REALTIME_LIMIT     = '1'
$Env:FUSION_USE_MAX            = '1'
$Env:FUSION_USE_BPS            = '1'
$Env:FUSION_FORCE_MAX_BUTTON   = '1'
$Env:FUSION_SELL_BPS_OFFSET    = '25'
$Env:FUSION_USE_MAX_SELL_ONLY  = '0'

# Safety and filters (unblocked sells, no extra confirmations)
$Env:FUSION_STRICT_EUR_ONLY    = '1'
$Env:FUSION_PORTFOLIO_CHECK    = '1'
$Env:FUSION_DISABLE_SELLS      = '0'
$Env:FUSION_SELL_CONFIRM       = '0'
$Env:DISABLE_SELLS             = '0'
$Env:SELL_CONFIRM              = '0'
$Env:FUSION_INCLUDE_LAST_DAYS  = [string]$IncludeLastDays
$Env:FUSION_BACKTEST_MODE      = '0'

# Diagnostics
$Env:FUSION_DEBUG              = $(if ($Debug) { '1' } else { '0' })
$Env:FUSION_DEEP_INPUT_DEBUG   = $(if ($DeepDebug) { '1' } else { '0' })

# Optional: force a specific trades file
if ($TradesFile) { $Env:FUSION_TRADES_FILE = $TradesFile }

# Past-days policy
if ($AllowPast -and $IncludeLastDays -gt 0) {
    $Env:FUSION_ALLOW_PAST_DAYS = '1'
    $Env:FUSION_ALLOW_PAST      = '1'
} else {
    $Env:FUSION_ALLOW_PAST_DAYS = '0'
    $Env:FUSION_ALLOW_PAST      = '0'
}

Write-Host "LIVE summary: SAFE=$($Env:FUSION_SAFE_PREVIEW_MODE) | PAPER=$($Env:FUSION_PAPER_MODE) | AUTO_SUBMIT=$($Env:FUSION_AUTO_SUBMIT) | CONTINUE=$($Env:FUSION_AUTO_CONTINUE) | WAIT_FOR_CLICK=$($Env:FUSION_WAIT_FOR_CLICK)" -ForegroundColor Cyan

# Start automation (live)
python .\fusion_existing_all_trades_auto.py
