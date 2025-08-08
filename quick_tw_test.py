#!/usr/bin/env python3
"""Quick test für tw>1"""

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest
from config import *

print("🔍 Quick test der ersten 3 Ticker...")

# Config für run_backtest
config = {
    'initialCapitalLong': 10000,
    'trade_on': 'close',
    'order_round_factor': 0.01,
    'commission_rate': 0.0018
}

results = []
for ticker in crypto_tickers[:3]:  # Nur erste 3
    try:
        print(f"Testing {ticker}...")
        result = run_backtest(ticker, config)
        tw = int(result.get('optimal_trade_window', 1))
        p = int(result.get('optimal_past_window', 2))
        print(f'✅ {ticker}: p={p}, tw={tw}')
        
        if tw > 1:
            print(f'🎯 FOUND tw>1: {ticker} has p={p}, tw={tw}')
            
    except Exception as e:
        print(f'❌ {ticker}: ERROR - {str(e)[:100]}')

print("\n✅ Quick test complete!")
