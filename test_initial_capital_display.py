#!/usr/bin/env python3
"""
Quick test to verify that ticker-specific initial capital is displayed correctly
"""
import sys
sys.path.append('.')

from crypto_tickers import crypto_tickers

print("🎯 TEST: Ticker-specific Initial Capital")
print("=" * 50)

for ticker, config in crypto_tickers.items():
    initial_capital = config.get('initialCapitalLong', 10000)
    trade_on = config.get('trade_on', 'Close')
    print(f"📊 {ticker}:")
    print(f"   💰 Initial Capital: {initial_capital} EUR")
    print(f"   📊 Trade on: {trade_on} price")
    print()
