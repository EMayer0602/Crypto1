#!/usr/bin/env python3

"""
Fokussiertes Debug der    # 4.     # 4. Simuliere Trades
    print("   4. Simuliere Trades...")
    final_capital = simulate_trades_compound_extended(
        signal_df, df,
        starting_capital=cfg['initial_capital'],
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1)
    )
    
    print(f"      ✅ Final capital: {final_capital}")
    print(f"      Initial capital: {cfg['initial_capital']}")ades
    print("   4. Simuliere Trades...")
    final_capital = simulate_trades_compound_extended(
        signal_df, df,
        starting_capital=cfg['initial_capital'],
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1)
    )ung
"""

import pandas as pd
import numpy as np
from signal_utils import calculate_support_resistance, assign_long_signals_extended, update_level_close_long
from MultiTradingIB25D_crypto import simulate_trades_compound_extended

# Lade BTC Daten
print("🔍 Lade BTC-EUR Daten...")
df = pd.read_csv('BTC-EUR_daily.csv', index_col=0, parse_dates=True)
print(f"✅ BTC Daten geladen: {df.shape}")
print(f"   Spalten: {list(df.columns)}")
print(f"   Index type: {type(df.index[0])}")
print(f"   Letzte 3 Zeilen:")
print(df.tail(3))

# Config
cfg = {
    'initial_capital': 10000,
    'commission_rate': 0.0018,
    'min_commission': 1.0,
    'order_round_factor': 0.01
}

# Teste einen Durchlauf manuell
past_window = 5
tw = 2

print(f"\n🔍 Teste manuell: past_window={past_window}, tw={tw}")

try:
    # 1. Support/Resistance
    print("   1. Berechne Support/Resistance...")
    support, resistance = calculate_support_resistance(df, past_window, tw, verbose=False)
    print(f"      Support shape: {support.shape}, Resistance shape: {resistance.shape}")
    
    # 2. Signals
    print("   2. Erstelle Signals...")
    signal_df = assign_long_signals_extended(support, resistance, df, tw, "1d")
    print(f"      Signal_df shape: {signal_df.shape}")
    print(f"      Signal_df columns: {list(signal_df.columns)}")
    print(f"      Actions counts:")
    if 'Action' in signal_df.columns:
        print(signal_df['Action'].value_counts())
    
    # 3. Update Level Close
    print("   3. Update Level Close...")
    signal_df = update_level_close_long(signal_df, df)
    print(f"      Updated signal_df shape: {signal_df.shape}")
    
    # 4. Simulate Trades
    print("   4. Simuliere Trades...")
    final_capital, trades_log = simulate_trades_compound_extended(
        signal_df, df, cfg,
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1),
        direction="long"
    )
    
    print(f"      ✅ Final capital: {final_capital}")
    print(f"      Initial capital: {cfg['initial_capital']}")
    
    pnl = ((final_capital - cfg['initial_capital']) / cfg['initial_capital']) * 100
    print(f"      📈 PnL: {pnl:.2f}%")
    
except Exception as e:
    print(f"❌ Fehler in der manuellen Optimierung: {e}")
    import traceback
    traceback.print_exc()
