#!/usr/bin/env python3

"""
Schneller Test der Optimierungsparameter
"""

from crypto_backtesting_module import run_backtest

# Test für BTC
print("🔍 Teste Optimierung für BTC-EUR...")

config = {
    'timeframe': 'daily',
    'lookback_period': 5,
    'csv_path': './'
}

try:
    result = run_backtest('BTC-EUR', config)
    
    if result:
        print(f"\n📊 Optimierungsergebnisse für BTC-EUR:")
        print(f"   Past Window: {result.get('optimal_past_window', 'N/A')}")
        print(f"   Trade Window: {result.get('optimal_trade_window', 'N/A')}")
        print(f"   Optimal PnL: {result.get('optimal_pnl', 'N/A')}")
        print(f"   Optimierung erfolgreich: {result.get('optimization_success', 'N/A')}")
        print(f"   Methode: {result.get('method', 'N/A')}")
    else:
        print("❌ Backtest fehlgeschlagen")
        
except Exception as e:
    print(f"❌ Fehler: {e}")
