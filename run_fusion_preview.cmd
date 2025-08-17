@echo off
setlocal EnableDelayedExpansion
REM Wrapper to run the PowerShell launcher with safe preview (no auto execution)
REM Usage options:
REM   1) Pass-through named args (recommended):
REM        run_fusion_preview.cmd -TradesFile "file.csv" -IncludeLastDays 1 -AllowPast
REM   2) Positional args (back-compat):
REM        run_fusion_preview.cmd [TradesFile] [IncludeLastDays] [AllowPast]
REM      Example: run_fusion_preview.cmd "TODAY_ONLY_trades_2025-08-15.csv" 1 true

set "SCRIPT_DIR=%~dp0"

REM No args -> use defaults from the PS1
if "%~1"=="" (
	powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run_fusion_preview.ps1"
	goto :eof
)

REM If first arg starts with '-' we pass everything through to PS1
set "ARG1=%~1"
set "FIRSTCHAR=!ARG1:~0,1!"
if "!FIRSTCHAR!"=="-" (
	powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run_fusion_preview.ps1" %*
	goto :eof
)

REM Positional mode
set "TRADESFILE=%~1"
set "INCLUDEDAYS=%~2"
set "ALLOWPAST=%~3"

set "PSARGS="
if not "%TRADESFILE%"=="" set "PSARGS=!PSARGS! -TradesFile \"%TRADESFILE%\""
if not "%INCLUDEDAYS%"=="" set "PSARGS=!PSARGS! -IncludeLastDays %INCLUDEDAYS%"
if /I "%ALLOWPAST%"=="true" set "PSARGS=!PSARGS! -AllowPast"
if /I "%ALLOWPAST%"=="1" set "PSARGS=!PSARGS! -AllowPast"
if /I "%ALLOWPAST%"=="yes" set "PSARGS=!PSARGS! -AllowPast"

powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run_fusion_preview.ps1" !PSARGS!

endlocal
