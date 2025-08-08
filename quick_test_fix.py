#!/usr/bin/env python3
"""Quick test für PnL extraction fix"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest

def test_single_ticker():
    """Test nur BTC"""
    print("🔍 Testing BTC-EUR PnL extraction...")
    
    ticker = 'BTC-EUR'
    config = crypto_tickers[ticker]
    
    print(f"Running backtest for {ticker}...")
    result = run_backtest(ticker, config)
    
    print(f"\nResult keys: {list(result.keys()) if result else 'None'}")
    
    # Try to extract PnL
    pnl_perc = 0
    if result and 'trade_statistics' in result and result['trade_statistics']:
        stats = result['trade_statistics']
        print(f"Trade statistics keys: {list(stats.keys())}")
        
        # Print all stats values to see what we have
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Look for Total Return or Total PnL
        if '📊 Total Return' in stats:
            pnl_perc = stats['📊 Total Return']
            print(f"✅ Found Total Return: {pnl_perc}")
        elif '💰 Total PnL' in stats:
            # If we have Total PnL and Final Capital, calculate percentage
            total_pnl = stats['💰 Total PnL']
            final_capital = stats.get('💼 Final Capital', config['initialCapitalLong'])
            pnl_perc = (total_pnl / config['initialCapitalLong']) * 100
            print(f"✅ Calculated PnL%: {pnl_perc:.2f}% (PnL: {total_pnl}, Initial: {config['initialCapitalLong']})")
        elif 'total_return_pct' in stats:
            pnl_perc = stats['total_return_pct']
            print(f"✅ Found total_return_pct: {pnl_perc}")
        elif 'net_profit_pct' in stats:
            pnl_perc = stats['net_profit_pct']
            print(f"✅ Found net_profit_pct: {pnl_perc}")
        elif 'return_pct' in stats:
            pnl_perc = stats['return_pct']  
            print(f"✅ Found return_pct: {pnl_perc}")
        else:
            print("❌ No PnL percentage found in trade_statistics")
    else:
        print("❌ No trade_statistics found")
        
    # Check matched_trades
    if result and 'matched_trades' in result:
        trades = result['matched_trades']
        print(f"Matched trades: {len(trades)} records")
        if not trades.empty:
            print("Sample trades:")
            print(trades.head().to_string())
    
    return result, pnl_perc

if __name__ == "__main__":
    test_single_ticker()
