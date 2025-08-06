#!/usr/bin/env python3
"""
Test to verify order_round_factor from crypto_tickers.py
"""
import sys
sys.path.append('.')

from crypto_tickers import crypto_tickers

print("🔧 TEST: Ticker-specific Order Round Factor")
print("=" * 60)

for ticker, config in crypto_tickers.items():
    initial_capital = config.get('initialCapitalLong', 10000)
    trade_on = config.get('trade_on', 'Close')
    order_round_factor = config.get('order_round_factor', 0.01)
    
    print(f"📊 {ticker}:")
    print(f"   💰 Initial Capital: {initial_capital} EUR")
    print(f"   📊 Trade on: {trade_on} price")
    print(f"   🔧 Order Round Factor: {order_round_factor}")
    print()
