#!/usr/bin/env python3
"""
Simple test to see the actual result structure from run_backtest.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import run_backtest

def main():
    print("🔍 DEBUG: Quick test of run_backtest result structure")
    
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
        print(f"\n📈 Result type: {type(result)}")
        print(f"📈 Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        # Look for optimal parameters
        if 'optimal_p' in result:
            print(f"✅ Found optimal_p: {result['optimal_p']}")
        if 'optimal_tw' in result:  
            print(f"✅ Found optimal_tw: {result['optimal_tw']}")
            
        # Look for trades
        if 'matched_trades' in result:
            trades = result['matched_trades']
            print(f"✅ Found matched_trades: {type(trades)} with {len(trades) if hasattr(trades, '__len__') else 'unknown'} items")
    else:
        print(f"❌ No result returned for {symbol}")

if __name__ == "__main__":
    main()
