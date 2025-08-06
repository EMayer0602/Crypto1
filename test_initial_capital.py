#!/usr/bin/env python3
"""
TEST: Prüfe ob initialCapitalLong korrekt verwendet wird
"""

from crypto_tickers import crypto_tickers

print("🧪 TEST: initialCapitalLong Verwendung")
print("="*50)

# Test für BTC-EUR (sollte 40000 sein)
ticker = "BTC-EUR"
ticker_config = crypto_tickers.get(ticker, {})

base_config = {
    'timeframe': 'daily',
    'lookback_period': 5,
    'csv_path': './',
    'initial_capital': 10000,  # Standard
    'order_round_factor': 0.01  # Standard
}

print(f"Ticker: {ticker}")
print(f"Ticker Config: {ticker_config}")
print(f"Base Config (vor Update): {base_config}")

# Update wie in unified_crypto_report.py
trade_on = ticker_config.get('trade_on', 'Close')
base_config['trade_on'] = trade_on
base_config['initial_capital'] = ticker_config.get('initialCapitalLong', base_config['initial_capital'])
base_config['order_round_factor'] = ticker_config.get('order_round_factor', base_config.get('order_round_factor', 0.01))

print(f"Updated Config (nach Update): {base_config}")
print(f"✅ Initial Capital korrekt: {base_config['initial_capital'] == 40000}")

# Test für ETH-EUR (sollte 10000 sein)
print(f"\n--- ETH-EUR Test ---")
ticker2 = "ETH-EUR"
ticker_config2 = crypto_tickers.get(ticker2, {})

base_config2 = {'initial_capital': 10000}
base_config2['initial_capital'] = ticker_config2.get('initialCapitalLong', base_config2['initial_capital'])

print(f"ETH-EUR initial_capital: {base_config2['initial_capital']}")
print(f"✅ ETH-EUR korrekt: {base_config2['initial_capital'] == 10000}")

print("\n=== Test abgeschlossen ===")
