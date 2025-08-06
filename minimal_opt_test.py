#!/usr/bin/env python3
"""
Minimaler Test nur für die Optimierung
"""

from crypto_backtesting_module import optimize_parameters
from crypto_tickers import crypto_tickers
import pandas as pd

print("🧪 MINIMAL OPTIMIERUNG TEST")
print("="*40)

# BTC-EUR laden
df = pd.read_csv("BTC-EUR_daily.csv", parse_dates=['Date'], index_col='Date')
ticker = "BTC-EUR"
ticker_config = crypto_tickers.get(ticker, {})

config = {
    'initial_capital': ticker_config.get('initialCapitalLong', 10000),
    'trade_on': ticker_config.get('trade_on', 'Close'),
    'order_round_factor': ticker_config.get('order_round_factor', 0.01)
}

print(f"Config: {config}")

try:
    result = optimize_parameters(df, ticker, config)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("=== Test abgeschlossen ===")
