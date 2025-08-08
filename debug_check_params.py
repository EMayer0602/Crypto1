#!/usr/bin/env python3
"""
Check the optimal parameters in the result.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import run_backtest

def main():
    print("🔍 DEBUG: Check optimal parameters")
    
    # Create basic config
    cfg = {
        "commission_rate": 0.0018,
        "min_commission": 1.0,
        "order_round_factor": 0.01,
        "backtest_years": 1,
        "backtest_start_percent": 0.25,
        "backtest_end_percent": 0.95,
        "initialCapitalLong": 1000
    }
    
    # Test with XRP-EUR
    symbol = "XRP-EUR"
    print(f"\n📊 Testing {symbol}")
    
    # Run backtest
    result = run_backtest(symbol, cfg)
    
    if result:
        print(f"\n📈 Results for {symbol}:")
        print(f"   Optimal Past Window (p): {result.get('optimal_past_window', 'N/A')}")
        print(f"   Optimal Trade Window (tw): {result.get('optimal_trade_window', 'N/A')}")
        print(f"   Final Capital: €{result.get('final_capital', 0):,.2f}")
        
        # Check trades
        trades = result.get('matched_trades')
        if trades is not None and not trades.empty:
            print(f"   Total trades: {len(trades)}")
            
            # Check the tw column in trades
            if 'tw' in trades.columns:
                tw_values = trades['tw'].unique()
                print(f"   Trade Window (tw) values in trades: {tw_values}")
            else:
                print(f"   Available trade columns: {list(trades.columns)}")
                
        else:
            print(f"   No trades found")
            
    else:
        print(f"❌ No result returned for {symbol}")

if __name__ == "__main__":
    main()
