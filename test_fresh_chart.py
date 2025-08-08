#!/usr/bin/env python3
"""Test der neuen Chart-Funktion mit Module-Reload"""

import importlib
import sys

# Module neu laden um Cache zu leeren
if 'plotly_utils' in sys.modules:
    importlib.reload(sys.modules['plotly_utils'])
if 'crypto_backtesting_module' in sys.modules:
    importlib.reload(sys.modules['crypto_backtesting_module'])

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

print("🔄 Testing with reloaded modules...")
print("🎯 Testing your improved Equity Curve function...")

# Test BTC-EUR
config = crypto_tickers['BTC-EUR']
result = run_backtest('BTC-EUR', config)

if result and result.get('success'):
    print("✅ Chart created with reloaded function!")
    
    # Check the timestamp to see if it's new
    import glob
    import os
    chart_files = glob.glob("reports/chart_BTC_EUR.html")
    if chart_files:
        file_time = os.path.getmtime(chart_files[0])
        import datetime
        timestamp = datetime.datetime.fromtimestamp(file_time)
        print(f"📅 Chart file timestamp: {timestamp}")
        
        # Open the new chart
        import webbrowser
        abs_path = os.path.abspath(chart_files[0])
        webbrowser.open(f"file://{abs_path}")
        print("🌐 Chart opened in browser")
    
else:
    print("❌ Failed to create chart")
