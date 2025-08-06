#!/usr/bin/env python3
"""
🔍 QUICK TRADE TEST
"""

import pandas as pd
import config
from signal_utils import calculate_support_resistance, assign_long_signals_extended
from MultiTradingIB25D_crypto import simulate_trades_compound_extended

print("🔍 QUICK TRADE TEST")
print("="*25)

try:
    # Config
    cfg = {
        'initial_capital': 10000,
        'commission_rate': config.COMMISSION_RATE,
        'min_commission': config.MIN_COMMISSION,
        'order_round_factor': config.ORDER_ROUND_FACTOR
    }
    
    # Lade nur kleine Datenmenge
    df = pd.read_csv('BTC-EUR_minute.csv', parse_dates=['DateTime'], nrows=500)
    df.set_index('DateTime', inplace=True)
    print(f"✅ Kleine Datenmenge geladen: {df.shape}")
    
    # Erstelle Signale
    support, resistance = calculate_support_resistance(df, 5, 2, verbose=False)
    signal_df = assign_long_signals_extended(support, resistance, df, 2, "1d")
    
    print(f"Signal_df shape: {signal_df.shape}")
    if 'Action' in signal_df.columns:
        actions = signal_df['Action'].value_counts()
        print(f"Actions: {actions.to_dict()}")
        buy_sell_count = len(signal_df[signal_df['Action'].isin(['buy', 'sell'])])
        print(f"BUY/SELL Signale: {buy_sell_count}")

    # Trade Simulation direkt (ohne Level Close Update)
    print(f"Starte Trade Simulation...")
    result = simulate_trades_compound_extended(
        signal_df, df,
        starting_capital=cfg['initial_capital'],
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1)
    )
    
    if isinstance(result, tuple):
        final_capital, trades_log = result
    else:
        final_capital = result
        trades_log = []
    
    print(f"\n📊 QUICK TEST ERGEBNIS:")
    print(f"   Final capital: {final_capital}")
    print(f"   Initial capital: {cfg['initial_capital']}")
    
    if final_capital != cfg['initial_capital']:
        pnl = ((final_capital - cfg['initial_capital']) / cfg['initial_capital']) * 100
        print(f"   ✅ PnL: {pnl:.2f}%")
        print(f"   🎉 SUCCESS! Trades wurden ausgeführt!")
    else:
        print(f"   ❌ Keine Trades ausgeführt")
        
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*25)
print("🔍 QUICK TEST Ende")
