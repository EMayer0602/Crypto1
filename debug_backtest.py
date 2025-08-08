#!/usr/bin/env python3
"""Debug der Backtest-Funktion"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest

print("🔍 DEBUG: Testing run_backtest function")
print("=" * 50)

# Test mit einem Ticker
ticker = "BTC-EUR"
config = crypto_tickers[ticker]

print(f"Testing {ticker} with config: {config}")

try:
    result = run_backtest(ticker, config)
    print(f"✅ Backtest result type: {type(result)}")
    if result:
        print(f"✅ Result keys: {list(result.keys())}")
        print(f"✅ PnL: {result.get('pnl_perc', 'NOT_FOUND')}")
        
        # Check trade data
        for source in ['extended_trades', 'matched_trades', 'trades']:
            if source in result:
                data = result[source]
                print(f"✅ {source}: {len(data)} records")
                if not data.empty:
                    print(f"   Columns: {data.columns.tolist()}")
                    print(f"   Actions: {data.get('Action', 'NO_ACTION_COLUMN').unique() if 'Action' in data.columns else 'NO_ACTION_COLUMN'}")
            else:
                print(f"❌ {source}: NOT_FOUND")
    else:
        print("❌ No result returned")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
