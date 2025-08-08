#!/usr/bin/env python3
"""Test aller Ticker für tw>1"""

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest

print("🔍 Testing all tickers for tw>1...")

results = []
tw_greater_than_1 = []

for ticker in crypto_tickers:
    try:
        print(f"Testing {ticker}...")
        result = run_backtest(ticker)
        tw = int(result.get('optimal_trade_window', 1))
        p = int(result.get('optimal_past_window', 2))
        results.append(f'{ticker}: p={p}, tw={tw}')
        
        if tw > 1:
            tw_greater_than_1.append((ticker, p, tw))
            print(f'🎯 FOUND tw>1: {ticker} has p={p}, tw={tw}')
            
    except Exception as e:
        results.append(f'{ticker}: ERROR - {e}')
        print(f'❌ {ticker}: ERROR - {e}')

print("\n📊 ZUSAMMENFASSUNG:")
print("==================")

if tw_greater_than_1:
    print(f"✅ {len(tw_greater_than_1)} Ticker haben tw>1:")
    for ticker, p, tw in tw_greater_than_1:
        print(f"   🎯 {ticker}: p={p}, tw={tw}")
else:
    print("❌ KEIN Ticker hat tw>1!")

print(f"\n📋 Alle Ergebnisse ({len(results)} Ticker):")
for r in results:
    print(f'   {r}')
