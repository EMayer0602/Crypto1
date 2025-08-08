#!/usr/bin/env python3

import sys
import os

# Pfade hinzufügen
sys.path.append(os.getcwd())

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def debug_equity_direct():
    """Test nur BTC direkt ohne alle anderen"""
    
    symbol = "BTC-EUR"
    config = crypto_tickers[symbol]
    
    print(f"🔍 TESTING DIRECT BACKTEST FOR {symbol}")
    print(f"🔍 Expected Initial Capital: €{config['initialCapitalLong']}")
    
    # Direkter Backtest-Aufruf
    result = run_backtest(symbol, config, debug=True)
    
    if result and result.get('success'):
        equity_curve = result.get('equity_curve', [])
        final_capital = result.get('final_capital', 0)
        
        print(f"\n✅ EQUITY CURVE ANALYSIS:")
        print(f"   Length: {len(equity_curve)}")
        if equity_curve:
            print(f"   Start: €{equity_curve[0]:.0f}")
            print(f"   End: €{equity_curve[-1]:.0f}")
            print(f"   Expected Start: €{config['initialCapitalLong']}")
            print(f"   Match: {'✅' if abs(equity_curve[0] - config['initialCapitalLong']) < 1 else '❌'}")
        
        print(f"\n✅ FINAL CAPITAL: €{final_capital:.0f}")
        print(f"✅ RETURN: {((equity_curve[-1] / equity_curve[0]) - 1) * 100:.1f}% if equity_curve else 'N/A'")
    else:
        print("❌ Backtest failed!")

if __name__ == "__main__":
    debug_equity_direct()
