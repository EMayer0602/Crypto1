#!/usr/bin/env python3

import sys
import os

# Pfade hinzufügen
sys.path.append(os.getcwd())

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def test_single_equity():
    """Test nur BTC mit Debug-Ausgabe für Equity"""
    
    symbol = "BTC-EUR"
    config = crypto_tickers[symbol]
    
    print(f"🔍 Testing {symbol}")
    print(f"🔍 Config: {config}")
    print(f"🔍 Initial Capital: {config['initialCapitalLong']}")
    
    result = run_backtest(symbol, config)
    
    if result and result.get('success'):
        print(f"\n✅ RESULT KEYS: {list(result.keys())}")
        print(f"✅ Config in result: {result.get('config', {}).keys()}")
        print(f"✅ Initial Capital in config: {result.get('config', {}).get('initialCapitalLong', 'NOT FOUND')}")
        
        equity_curve = result.get('equity_curve', [])
        print(f"✅ Equity Curve length: {len(equity_curve)}")
        if equity_curve:
            print(f"✅ Equity Start: €{equity_curve[0]:.0f}")
            print(f"✅ Equity End: €{equity_curve[-1]:.0f}")
            print(f"✅ First 5 values: {[f'€{v:.0f}' for v in equity_curve[:5]]}")
            print(f"✅ Last 5 values: {[f'€{v:.0f}' for v in equity_curve[-5:]]}")
        
        final_capital = result.get('final_capital', 0)
        print(f"✅ Final Capital: €{final_capital:.0f}")
        
        # Check for variation
        if equity_curve:
            unique_values = len(set([int(v/100)*100 for v in equity_curve]))
            print(f"✅ Unique values (rounded to 100s): {unique_values}")
            if unique_values > 10:
                print("✅ Equity curve shows good variation!")
            else:
                print("❌ Equity curve shows little variation")
    else:
        print("❌ Backtest failed!")

if __name__ == "__main__":
    test_single_equity()
