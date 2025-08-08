#!/usr/bin/env python3
"""Test der direkten Chart-Erstellung"""

import pandas as pd
from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers
from plotly_utils import plotly_combined_chart_and_equity
import os

print("🎯 Direct chart creation test...")
print("=" * 60)

# Führe Backtest aus
config = crypto_tickers['BTC-EUR']
ticker = 'BTC-EUR'

print(f"📊 Running backtest for {ticker}...")
result = run_backtest(ticker, config)

if result and result.get('success'):
    print("✅ Backtest successful!")
    final_cap = result.get('final_capital', 0)
    if final_cap != 'N/A':
        print(f"📈 Final Capital: €{final_cap:,.2f}")
    else:
        print(f"📈 Final Capital: {final_cap}")
    
    # Lade die CSV-Daten
    csv_file = f"{ticker}_daily.csv"
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'])
        
        print(f"📊 Data loaded: {len(df)} rows")
        
        # Erstelle Chart direkt
        chart_file = plotly_combined_chart_and_equity(
            df,
            extended_signals=result.get('extended_signals', pd.DataFrame()),
            ticker=ticker,
            strategy_name="BTC Strategy",
            initial_capital=config['initial_capital'],
            final_capital=result.get('final_capital', config['initial_capital'])
        )
        
        if chart_file and os.path.exists(chart_file):
            print(f"✅ Chart created: {chart_file}")
            
            # Öffne im Browser
            import webbrowser
            abs_path = os.path.abspath(chart_file)
            webbrowser.open(f"file://{abs_path}")
            print("🌐 Chart opened in browser!")
        else:
            print("❌ Chart creation failed")
    else:
        print(f"❌ CSV file not found: {csv_file}")
else:
    print("❌ Backtest failed")
    if result:
        print(f"   Available keys: {list(result.keys())}")
