#!/usr/bin/env python3
"""Test nur der Equity Curve"""

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

# Kurzer Test
config = crypto_tickers['BTC-EUR']
result = run_backtest('BTC-EUR', config)

if result:
    equity = result.get('equity_curve', [])
    final = result.get('final_capital', 0)
    
    print(f"📊 Equity length: {len(equity)}")
    print(f"📊 Final capital: €{final:,.0f}")
    print(f"📊 Equity start/end: €{equity[0]:.0f} -> €{equity[-1]:.0f}")
    print(f"📊 First 10: {[f'{v:.0f}' for v in equity[:10]]}")
    print(f"📊 Last 10: {[f'{v:.0f}' for v in equity[-10:]]}")
    
    unique = len(set([int(v) for v in equity]))
    print(f"📊 Unique values: {unique}")
    if unique > 10:
        print("✅ Equity curve varies correctly!")
    else:
        print("❌ Equity curve is too flat!")
