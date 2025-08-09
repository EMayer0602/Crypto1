#!/usr/bin/env python3

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def test_matched_trades_price_usage():
    """Test that matched trades use correct prices based on trade_on setting"""
    print("🔍 TESTING MATCHED TRADES PRICE USAGE")
    print("="*80)
    
    # Test with two tickers that have different trade_on settings
    test_symbols = []
    for symbol, config in crypto_tickers.items():
        if symbol in ['XRP-EUR', 'DOGE-EUR']:  # Different trade_on settings
            test_symbols.append((symbol, config))
    
    for symbol, config in test_symbols:
        print(f"\n📊 Testing {symbol}")
        print(f"📊 Config trade_on: {config.get('trade_on', 'Close')}")
        print("-"*60)
        
        try:
            result = run_backtest(symbol, config)
            if result and 'matched_trades' in result:
                matched_trades = result['matched_trades']
                if not matched_trades.empty:
                    print(f"✅ {symbol}: {len(matched_trades)} matched trades generated")
                    print("📋 First few trades:")
                    print(matched_trades[['Entry Date', 'Entry Price', 'Exit Date', 'Exit Price', 'Status']].head(3).to_string())
                else:
                    print(f"❌ {symbol}: No matched trades generated")
            else:
                print(f"❌ {symbol}: Backtest failed or no result")
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")

if __name__ == "__main__":
    test_matched_trades_price_usage()
