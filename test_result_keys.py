#!/usr/bin/env python3
"""Simple test to see result keys"""

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

# Test BTC-EUR
config = crypto_tickers['BTC-EUR']
print(f"Config: {config}")

result = run_backtest('BTC-EUR', config)

if result:
    print("\n✅ RESULT KEYS:")
    for key, value in result.items():
        print(f"  {key}: {type(value)}")
        if hasattr(value, '__len__') and not isinstance(value, str):
            print(f"      Length: {len(value)}")
else:
    print("❌ No result")
