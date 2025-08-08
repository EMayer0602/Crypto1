#!/usr/bifrom crypto_backtesting_module import run_backtest
from config import cfg

def main():
    print("🔍 DEBUG: Testing optimal parameter usage in run_backtest")thon3
"""
Test script to debug optimal parameter usage in run_backtest.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import run_backtest
from crypto_tickers import get_crypto_config

def main():
    print("🔍 DEBUG: Testing optimal parameter application in run_backtest")
    
    # Get config
    cfg = get_crypto_config()
    
    # Test with XRP-EUR
    symbol = "XRP-EUR"
    print(f"\n📊 Testing {symbol}")
    
    # Run backtest
    result = run_backtest(cfg, symbol)
    
    if result:
        print(f"\n📈 Results for {symbol}:")
        print(f"   Optimal p: {result.get('optimal_p', 'N/A')}")
        print(f"   Optimal tw: {result.get('optimal_tw', 'N/A')}")
        print(f"   Final Capital: €{result.get('final_capital', 0):,.2f}")
        print(f"   Total Trades: {result.get('total_trades', 0)}")
        print(f"   Backtest Range: {result.get('backtest_range', 'N/A')}")
        
        # Check if trades exist
        trades = result.get('matched_trades', [])
        print(f"   Recent trades: {len(trades)} trades")
        
        if trades:
            print("   📝 First few trades:")
            for i, trade in enumerate(trades[:3]):
                action = trade.get('action', 'Unknown')
                date = trade.get('date', 'Unknown')
                price = trade.get('price', 0)
                tw = trade.get('tw', 'N/A')
                print(f"      {i+1}. {action} on {date} at €{price:.4f} (tw={tw})")
    else:
        print(f"❌ No result returned for {symbol}")

if __name__ == "__main__":
    main()
