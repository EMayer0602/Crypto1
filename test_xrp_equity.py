#!/usr/bin/env python3

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

# Test XRP nur
symbol = "XRP-EUR"
config = crypto_tickers[symbol]

print(f"Testing {symbol} with initial capital €{config['initialCapitalLong']}")

result = run_backtest(symbol, config)

if result:
    equity_curve = result.get('equity_curve', [])
    print(f"Equity curve start: €{equity_curve[0] if equity_curve else 'EMPTY'}")
    print(f"Expected start: €{config['initialCapitalLong']}")
    
    if equity_curve and abs(equity_curve[0] - config['initialCapitalLong']) > 0.01:
        print("❌ EQUITY CURVE STARTS WRONG!")
    else:
        print("✅ Equity curve starts correctly")
else:
    print("❌ Backtest failed")
