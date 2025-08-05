#!/usr/bin/env python3
"""
Test Script für einzelnes Symbol
"""

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

# Teste nur BTC-EUR
symbol = "BTC-EUR"
config = crypto_tickers[symbol]

print(f"🧪 Testing einzelnes Symbol: {symbol}")
result = run_backtest(symbol, config)

if result:
    print(f"✅ Test erfolgreich für {symbol}")
    print(f"📊 Result keys: {list(result.keys())}")
    
    if 'weekly_trades_html' in result:
        print(f"📅 Weekly Trades HTML length: {len(result['weekly_trades_html'])}")
    
    if 'weekly_trades_count' in result:
        print(f"📈 Weekly Trades count: {result['weekly_trades_count']}")
else:
    print(f"❌ Test fehlgeschlagen für {symbol}")
