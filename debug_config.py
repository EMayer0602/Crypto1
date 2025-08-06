#!/usr/bin/env python3
"""
Debug config problem
"""

from crypto_tickers import crypto_tickers

print("=== Debug config problem ===")

# Test config setup
config = {
    'timeframe': 'daily',
    'lookback_period': 5,
    'csv_path': './',
    'initial_capital': 10000,
    'order_round_factor': 0.01
}

print(f"Initial config: {config}")
print(f"Config has initial_capital: {'initial_capital' in config}")

# Test ticker config
ticker = 'BTC-EUR'
ticker_config = crypto_tickers.get(ticker, {})
print(f"Ticker config for {ticker}: {ticker_config}")

# Test the problematic line
try:
    config['initial_capital'] = ticker_config.get('initialCapitalLong', config['initial_capital'])
    print(f"SUCCESS: New initial_capital: {config['initial_capital']}")
except KeyError as e:
    print(f"ERROR: {e}")
    print(f"Config keys: {list(config.keys())}")
