param(
    [string]$TradesFile = ".\TODAY_ONLY_trades_TEST.csv",
    [string]$OnlyPair = '',     # e.g. ETH-USD
    [string]$OnlyAction = ''    # BUY or SELL
)

# Move to script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Minimal, safe preview: show Review only, wait for Enter between trades
$Env:FUSION_SAFE_PREVIEW_MODE = '1'
$Env:FUSION_WAIT_FOR_CLICK    = '1'
$Env:FUSION_AUTO_SUBMIT       = '0'
$Env:FUSION_AUTO_CONTINUE     = '0'
$Env:FUSION_PREVIEW_ONLY      = '1'
$Env:FUSION_NO_SUBMIT         = '1'
$Env:FUSION_BLOCK_REVIEW      = '1'
$Env:FUSION_PAPER_MODE        = '1'
$Env:FUSION_STOP_AFTER_BUTTONS= '1'
$Env:FUSION_DISABLE_SELLS     = '0'
$Env:DISABLE_SELLS            = '0'
$Env:FUSION_DISABLE_TICKER_WHITELIST = '1'
$Env:FUSION_STRICT_SCREENSHOT_MATCH = '0'
$Env:FUSION_ENFORCE_PAIR_FIRST      = '1'

# Clear any leftover single-trade filters
$Env:FUSION_ONLY_PAIR         = ''
$Env:FUSION_ONLY_ACTION       = ''
# Logic: MAX + 0.25% BUY fee buffer; BUY −25bps, SELL +25bps
$Env:FUSION_USE_MAX             = '1'
$Env:FUSION_FORCE_MAX_BUTTON    = '1'
$Env:FUSION_APPLY_FEE_BUFFER_BUY= '1'
$Env:FUSION_FEE_BUFFER_BPS      = '25'
$Env:FUSION_NO_BUY_TICKER_TOGGLE= '1'
$Env:FUSION_USE_BPS             = '1'
$Env:FUSION_SELL_BPS_OFFSET     = '25'
if (-not $Env:FUSION_BPS_PRIMARY) { $Env:FUSION_BPS_PRIMARY = '25' }

# Safety: holdings check on SELL; allow *-EUR by default, relax if test file has non-EUR
$Env:FUSION_PORTFOLIO_CHECK   = '1'
$Env:FUSION_STRICT_EUR_ONLY   = '0'

# Use provided trades file and relax EUR-only if needed
$Env:FUSION_TRADES_FILE = $TradesFile
try {
    if (Test-Path -LiteralPath $TradesFile) {
        $txt = Get-Content -LiteralPath $TradesFile -Raw
        if ($txt -match '-USD' -or $txt -match '-USDT' -or $txt -match '-USDC' -or $txt -match '-GBP' -or $txt -match '-CHF') {
            $Env:FUSION_STRICT_EUR_ONLY = '0'
        }
    }
} catch {}

# Optional single-trade targeting
if ($OnlyPair) {
    $Env:FUSION_ONLY_PAIR = $OnlyPair
    if ($OnlyAction) { $Env:FUSION_ONLY_ACTION = $OnlyAction }
    if ($OnlyPair -notmatch '-EUR$') { $Env:FUSION_STRICT_EUR_ONLY = '0' }
}

Write-Host ('🧪 Simple Preview | File=' + $TradesFile + ' | SAFE=1 WAIT_FOR_CLICK=1 | BUY buffer=0.25% | BPS: BUY=-25 SELL=+25') -ForegroundColor Green
if ($OnlyPair) { Write-Host ('🎯 Filter: Pair=' + $OnlyPair + ' Action=' + $OnlyAction) -ForegroundColor DarkCyan }

$py = 'C:/Users/Edgar.000/AppData/Local/Microsoft/WindowsApps/python3.13.exe'
if (-not (Test-Path $py)) { $py = 'python' }
& $py .\fusion_existing_all_trades_auto.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python exited with code $LASTEXITCODE" -ForegroundColor Red
}
