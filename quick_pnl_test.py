#!/usr/bin/env python3
"""Quick test for PnL fix"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest

def test_pnl_fix():
    """Test nur BTC mit PnL fix"""
    print("🔍 Testing PnL extraction fix...")
    
    ticker = 'BTC-EUR'
    config = crypto_tickers[ticker]
    
    print(f"Testing {ticker} with initialCapitalLong: {config['initialCapitalLong']}")
    
    result = run_backtest(ticker, config)
    
    if result and 'trade_statistics' in result:
        stats = result['trade_statistics']
        print(f"\nTrade Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        # Extract PnL like in live_backtest
        pnl_perc = 0
        if '📊 Total Return' in stats:
            pnl_value = stats['📊 Total Return']
            print(f"\nRaw Total Return: {pnl_value} (type: {type(pnl_value)})")
            
            # Handle string PnL (remove % and convert to float)
            if isinstance(pnl_value, str):
                pnl_perc = float(pnl_value.replace('%', ''))
                print(f"Converted to numeric: {pnl_perc}")
            else:
                pnl_perc = pnl_value
                print(f"Already numeric: {pnl_perc}")
                
            # Test comparison
            pnl_class = "pnl-positive" if pnl_perc > 0 else "pnl-negative"
            print(f"PnL Class: {pnl_class}")
            
        print(f"\n✅ SUCCESS: PnL = {pnl_perc}% (Initial Capital: {config['initialCapitalLong']})")
    
    return True

if __name__ == "__main__":
    test_pnl_fix()
