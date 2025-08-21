param(
    [string]$TradesFile = '',
    [int]$IncludeLastDays = 0,   # 0 = only today; 1 = today + yesterday; 2 = today + last 2 days, ...
    [switch]$AllowPast,           # must be set to allow IncludeLastDays > 0
    [switch]$Debug,               # enable verbose DEBUG logs in Python
    [switch]$DeepDebug            # enable deep input/JS debug logs
)

# Move to script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Environment: Fill all fields, but never auto-execute
$Env:FUSION_SAFE_PREVIEW_MODE = '1'      # Only preview; do not click Review/Submit automatically
$Env:FUSION_WAIT_FOR_CLICK     = '1'      # Wait for user; no auto-advance action clicks
$Env:FUSION_AUTO_SUBMIT        = '0'      # Never auto-submit
$Env:FUSION_AUTO_CONTINUE      = '0'      # No auto-continue between orders when waiting for click

# Robust filling behavior (Keyboard Limit+BPS only)
$Env:FUSION_TAB_NAV            = '0'
$Env:FUSION_STRICT_TAB_STEPS   = '0'
$Env:FUSION_TABS_TO_SIDE       = '0'
$Env:FUSION_TABS_TO_STRATEGY   = '0'
$Env:FUSION_TABS_TO_QTY        = '0'
$Env:FUSION_REALTIME_LIMIT     = '0'
$Env:FUSION_USE_MAX            = '1'
$Env:FUSION_USE_BPS            = '1'
$Env:FUSION_STOP_AFTER_BUTTONS = '1'      # Stop after clicking buttons (preview)
$Env:FUSION_PRICE_COMMIT_VERIFY= '0'

# Ensure Limit+BPS keyboard flow only
$Env:FUSION_TICKER_MAX_MODE    = '0'
$Env:FUSION_LIMIT_KB_BPS_MODE  = '1'
$Env:FUSION_LIMIT_TAB_SEQ      = '0'
$Env:FUSION_BPS_PRIMARY        = '25'
$Env:FUSION_BPS_FALLBACK       = '10'
$Env:FUSION_USE_MAX_SELL_ONLY  = '0'      # MAX für alle Seiten (BUY+SELL)
$Env:FUSION_FORCE_MAX_BUTTON   = '1'      # MAX Button immer aktivieren
$Env:FUSION_SELL_BPS_OFFSET    = '-25'    # SELL: -25bps (unter Marktpreis)

# Safety and filters
$Env:FUSION_STRICT_EUR_ONLY    = '1'      # Only *-EUR pairs
$Env:FUSION_PORTFOLIO_CHECK    = '1'      # Adjust SELL qty to holdings
$Env:FUSION_DISABLE_SELLS      = '0'      # Allow SELLs (prefixed)
$Env:FUSION_SELL_CONFIRM       = '0'      # No extra SELL confirmation prompts (prefixed)
# Also set unprefixed variants to override any global env settings
$Env:DISABLE_SELLS             = '0'
$Env:SELL_CONFIRM              = '0'
$Env:FUSION_INCLUDE_LAST_DAYS  = [string]$IncludeLastDays
$Env:FUSION_BACKTEST_MODE      = '0'      # Live UI mode

# Diagnostics (optional)
$Env:FUSION_DEBUG              = $(if ($Debug) { '1' } else { '0' })
$Env:FUSION_DEEP_INPUT_DEBUG   = $(if ($DeepDebug) { '1' } else { '0' })
$Env:FUSION_DUMP_FILTER_DEBUG  = '0'

# Optional: force a specific trades file
if ($TradesFile) {
    $Env:FUSION_TRADES_FILE = $TradesFile
}

# Allow past days policy
if ($AllowPast -and $IncludeLastDays -gt 0) {
    # Accept both env names used by the Python loader
    $Env:FUSION_ALLOW_PAST_DAYS = '1'
    $Env:FUSION_ALLOW_PAST      = '1'
} else {
    $Env:FUSION_ALLOW_PAST_DAYS = '0'
    $Env:FUSION_ALLOW_PAST      = '0'
}

# Echo summary
Write-Host "Preview mode: SAFE=$($Env:FUSION_SAFE_PREVIEW_MODE) | ALLOW_PAST=$($Env:FUSION_ALLOW_PAST_DAYS) | INCLUDE_LAST_DAYS=$IncludeLastDays | DEBUG=$($Env:FUSION_DEBUG)" -ForegroundColor Cyan

# Launch the automation (preview mode ensures no auto execution)
python .\fusion_existing_all_trades_auto.py
