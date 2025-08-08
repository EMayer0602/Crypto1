#!/usr/bin/env python3
"""
Test script to debug optimal parameter usage in run_backtest.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def main():
    print("🔍 DEBUG: Testing optimal parameter application in run_backtest")
    
    # Test with XRP-EUR
    symbol = "XRP-EUR"
    config = crypto_tickers[symbol]
    print(f"\n📊 Testing {symbol}")
    
    # Run backtest
    result = run_backtest(symbol, config)
    
    if result:
        print(f"\n📈 Results for {symbol}:")
        print(f"   Optimal p: {result.get('optimal_past_window', 'N/A')}")
        print(f"   Optimal tw: {result.get('optimal_trade_window', 'N/A')}")
        print(f"   Final Capital: €{result.get('final_capital', 0):,.2f}")
        print(f"   Success: {result.get('success', False)}")
        
        # Check if trades exist
        trades = result.get('matched_trades')
        if trades is not None and not trades.empty:
            print(f"   Recent trades: {len(trades)} trades")
            print("   📝 First few trades:")
            for i, (_, trade) in enumerate(trades.head(3).iterrows()):
                entry_date = trade.get('Entry Date', 'Unknown')
                exit_date = trade.get('Exit Date', 'Unknown')
                entry_price = trade.get('Entry Price', 0)
                exit_price = trade.get('Exit Price', 0)
                pnl = trade.get('Net PnL', 0)
                print(f"      {i+1}. {entry_date} → {exit_date}: €{entry_price:.4f} → €{exit_price:.4f} (PnL: €{pnl:.2f})")
        else:
            print("   ❌ No trades found")
    else:
        print(f"❌ No result returned for {symbol}")

if __name__ == "__main__":
    main()
