#!/usr/bin/env python3
"""
DIREKTER TEST der Optimierung für einen einzelnen Ticker
"""

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

print("🧪 DIREKTER OPTIMIERUNGS-TEST")
print("="*50)

# Teste BTC-EUR
ticker = "BTC-EUR"
ticker_config = crypto_tickers.get(ticker, {})

config = {
    'timeframe': 'daily',
    'lookback_period': 5,
    'csv_path': './',
    'initial_capital': ticker_config.get('initialCapitalLong', 10000),
    'order_round_factor': ticker_config.get('order_round_factor', 0.01),
    'trade_on': ticker_config.get('trade_on', 'Close')
}

print(f"Ticker: {ticker}")
print(f"Config: {config}")

try:
    print(f"\n🔄 Führe run_backtest aus...")
    result = run_backtest(ticker, config)
    
    print(f"\n📊 RESULT KEYS:")
    for key, value in result.items():
        if key not in ['df_bt', 'ext_signals', 'matched_trades']:  # Skip large objects
            print(f"   {key}: {value}")
            
    print(f"\n🎯 OPTIMIERUNG ERGEBNISSE:")
    print(f"   optimal_past_window: {result.get('optimal_past_window', 'MISSING!')}")
    print(f"   optimal_trade_window: {result.get('optimal_trade_window', 'MISSING!')}")
    print(f"   optimal_pnl: {result.get('optimal_pnl', 'MISSING!')}")
    print(f"   optimization_success: {result.get('optimization_success', 'MISSING!')}")
    
except Exception as e:
    print(f"❌ FEHLER: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test abgeschlossen ===")
