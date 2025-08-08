#!/usr/bin/env python3
"""Erstelle einen frischen Chart mit deiner verbesserten Funktion"""

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers
from plotly_utils import plotly_combined_chart_and_equity
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
    
    # Extrahiere die Daten für den Chart
    df = result.get('df')
    ext_signals = result.get('ext_signals')
    equity_curve = result.get('equity_curve', [])
    buyhold_curve = result.get('buyhold_curve', [])
    initial_capital = config.get('initialCapitalLong', 10000)
    
    if df is not None and not df.empty:
        print(f"📊 Creating chart with {len(df)} data points...")
        print(f"📊 Equity curve: {len(equity_curve)} values")
        print(f"📊 Extended signals: {len(ext_signals) if ext_signals is not None else 0} trades")
        
        # Support/Resistance aus result extrahieren oder leer lassen
        support_series = []  # Diese müssen aus df extrahiert werden
        resistance_series = []  # Diese müssen aus df extrahiert werden
        
        # Chart erstellen
        chart_success = plotly_combined_chart_and_equity(
            df=df,
            standard_signals=ext_signals,
            support=support_series,
            resistance=resistance_series,
            equity_curve=equity_curve,
            buyhold_curve=buyhold_curve,
            ticker='BTC-EUR',
            backtest_years=1,
            initial_capital=initial_capital
        )
        
        if chart_success:
            print("✅ Chart creation successful!")
        else:
            print("❌ Chart creation failed!")
    
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
