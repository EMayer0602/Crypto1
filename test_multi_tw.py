#!/usr/bin/env python3
"""
Test verschiedene Tickers um tw>1 zu finden
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import run_backtest

def main():
    print("🔍 Testing verschiedene Tickers für tw>1")
    
    # Create basic config
    cfg = {
        "commission_rate": 0.0018,
        "min_commission": 1.0,
        "order_round_factor": 0.01,
        "backtest_years": 1,
        "backtest_start_percent": 0.25,
        "backtest_end_percent": 0.95,
        "initialCapitalLong": 3000
    }
    
    # Test verschiedene Tickers
    test_tickers = ["ETH-EUR", "BTC-EUR", "DOGE-EUR"]
    
    for symbol in test_tickers:
        print(f"\n{'='*60}")
        print(f"🔍 Testing {symbol}")
        
        result = run_backtest(symbol, cfg)
        
        if result:
            p = result.get('optimal_past_window', 'N/A')
            tw = result.get('optimal_trade_window', 'N/A')
            final_cap = result.get('final_capital', 0)
            
            print(f"📈 {symbol}: p={p}, tw={tw}, Final=€{final_cap:,.2f}")
            
            # Zeige erste Extended Trades
            ext_signals = result.get('ext_signals')
            if ext_signals is not None and not ext_signals.empty:
                print(f"   📊 Erste 3 Extended Signals:")
                for i in range(min(3, len(ext_signals))):
                    row = ext_signals.iloc[i]
                    detected = row.get('Long Date detected', 'N/A')
                    trade_day = row.get('Long Trade Day', 'N/A')
                    action = row.get('Action', 'N/A')
                    
                    if hasattr(trade_day, 'strftime'):
                        trade_day_str = trade_day.strftime('%Y-%m-%d')
                    else:
                        trade_day_str = str(trade_day)
                        
                    print(f"     {i+1}. {action}: Detected={detected}, Trade={trade_day_str}")
        else:
            print(f"❌ {symbol}: Failed")

if __name__ == "__main__":
    main()
