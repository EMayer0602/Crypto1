#!/usr/bin/env python3
"""Erstelle einen frischen Chart mit deiner verbesserten Funktion"""

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers
import os
import datetime

print("🎯 Creating FRESH chart with your improved function...")
print("=" * 60)

# Lösche erst den alten Chart
old_chart = "reports/chart_BTC_EUR.html"
if os.path.exists(old_chart):
    os.remove(old_chart)
    print("🗑️ Old chart deleted")

# Erstelle neuen Chart
config = crypto_tickers['BTC-EUR']
print(f"📊 Running backtest for BTC-EUR...")

result = run_backtest('BTC-EUR', config)

if result and result.get('success'):
    print("✅ Backtest successful!")
    
    # Prüfe ob neuer Chart erstellt wurde
    if os.path.exists(old_chart):
        file_time = os.path.getmtime(old_chart)
        timestamp = datetime.datetime.fromtimestamp(file_time)
        print(f"📅 NEW chart created at: {timestamp}")
        
        # Öffne im Browser
        import webbrowser
        abs_path = os.path.abspath(old_chart)
        webbrowser.open(f"file://{abs_path}")
        print("🌐 Fresh chart opened in browser with your improvements!")
    else:
        print("❌ Chart file not found")
else:
    print("❌ Backtest failed")
    if result:
        print(f"   Keys available: {list(result.keys())}")
