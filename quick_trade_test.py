#!/usr/bin/env python3

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

# Quick test with just XRP-EUR (Close) and DOGE-EUR (Open)
def quick_test():
    print("🔍 QUICK TEST: XRP-EUR vs DOGE-EUR matched trades")
    print("="*80)
    
    for symbol in ['XRP-EUR', 'DOGE-EUR']:
        config = crypto_tickers[symbol]
        trade_on = config.get('trade_on', 'Close')
        print(f"\n📊 {symbol}: trade_on = {trade_on}")
        
        try:
            result = run_backtest(symbol, config)
            if result and 'matched_trades' in result:
                matched = result['matched_trades']
                if not matched.empty:
                    print(f"✅ Generated {len(matched)} matched trades")
                    first_trade = matched.iloc[0]
                    print(f"📋 First trade: Entry={first_trade['Entry Price']}, Exit={first_trade['Exit Price']}")
                else:
                    print("❌ No matched trades")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
