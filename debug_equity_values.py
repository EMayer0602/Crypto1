#!/usr/bin/env python3

import sys
import os
import pandas as pd

sys.path.append(os.getcwd())

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def debug_equity_values():
    """Debug die EXAKTEN Werte der Equity Curve"""
    
    symbol = "XRP-EUR"  # Der problematische Ticker
    config = crypto_tickers[symbol]
    
    print(f"🔍 DEBUGGING EQUITY VALUES FOR {symbol}")
    print(f"💰 Expected Initial Capital: €{config['initialCapitalLong']}")
    
    # Run backtest
    result = run_backtest(symbol, config)
    
    if result and isinstance(result, dict):
        equity_curve = result.get('equity_curve', [])
        
        print(f"\n🔍 EQUITY CURVE DEBUG:")
        print(f"   Length: {len(equity_curve)}")
        print(f"   First 10 values: {equity_curve[:10] if equity_curve else 'EMPTY'}")
        print(f"   Last 10 values: {equity_curve[-10:] if equity_curve else 'EMPTY'}")
        
        # Check if all values are the same (flat line problem)
        if equity_curve:
            unique_vals = set(equity_curve[:50])  # First 50 values
            print(f"   First 50 unique values: {len(unique_vals)}")
            print(f"   Sample unique values: {list(unique_vals)[:5]}")
            
            if len(unique_vals) == 1:
                print("   ❌ PROBLEM: All values are identical (flat line)!")
            else:
                print("   ✅ Values do vary")
                
        # Check config values
        print(f"\n🔍 CONFIG DEBUG:")
        print(f"   Result config keys: {list(result.get('config', {}).keys())}")
        print(f"   InitialCapitalLong: {result.get('config', {}).get('initialCapitalLong', 'MISSING')}")
        
        # Check matched trades
        matched_trades = result.get('matched_trades', pd.DataFrame())
        print(f"\n🔍 TRADES DEBUG:")
        print(f"   Matched trades count: {len(matched_trades)}")
        if not matched_trades.empty:
            print(f"   First trade: {dict(matched_trades.iloc[0])}")
        
    else:
        print("❌ Backtest failed!")

if __name__ == "__main__":
    debug_equity_values()
