param(
    [string]$TradesFile = ".\TODAY_ONLY_trades_20250818_121500.csv"
)

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

$Env:FUSION_SAFE_PREVIEW_MODE = '1'
$Env:FUSION_PREVIEW_ONLY      = '1'
$Env:FUSION_NO_SUBMIT         = '1'
$Env:FUSION_BLOCK_REVIEW      = '1'
$Env:FUSION_PAPER_MODE        = '1'
$Env:FUSION_AUTO_SUBMIT       = '0'
$Env:FUSION_STOP_AFTER_BUTTONS= '1'
$Env:FUSION_WAIT_FOR_CLICK    = '1'
$Env:FUSION_STRICT_SCREENSHOT_MATCH = '0'
$Env:FUSION_ENFORCE_PAIR_FIRST      = '1'
$Env:FUSION_TRADES_FILE = $TradesFile
$Env:FUSION_ONLY_PAIR   = 'XRP-EUR'
$Env:FUSION_ONLY_ACTION = 'SELL'
$Env:FUSION_FORCE_SIDE_RULES = 'ETH-USD:BUY;XRP-EUR:SELL'
$Env:FUSION_DISABLE_SELL_PAIRS = 'ETH-USD'
$Env:FUSION_SIDE_MISMATCH_ABORT = '1'

Write-Host "🎯 XRP-EUR SELL Preview (no submit)" -ForegroundColor Yellow

$py = 'C:/Users/Edgar.000/AppData/Local/Microsoft/WindowsApps/python3.13.exe'
if (-not (Test-Path $py)) { $py = 'python' }
& $py .\fusion_existing_all_trades_auto.py
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Python exited $LASTEXITCODE" -ForegroundColor Red }
