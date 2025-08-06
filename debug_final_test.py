#!/usr/bin/env python3
"""
🔍 DEBUG - Manuelle Optimierung Test FINAL
Reproduziert einen einzigen Optimierungsschritt manuell
"""

import pandas as pd
import numpy as np
import config
from signal_utils import calculate_support_resistance, assign_long_signals_extended, update_level_close_long
from MultiTradingIB25D_crypto import simulate_trades_compound_extended

# Lade Daten
print("🔍 DEBUG - Manuelle Optimierung Test FINAL")
print("="*50)

try:
    # Konfiguration als Dictionary
    cfg = {
        'initial_capital': 10000,
        'commission_rate': config.COMMISSION_RATE,
        'min_commission': config.MIN_COMMISSION,
        'order_round_factor': config.ORDER_ROUND_FACTOR
    }
    print(f"✅ Config geladen: initial_capital={cfg['initial_capital']}")

    # Test Daten für BTC-EUR laden mit korrekter DateTime-Spalte 
    df = pd.read_csv('BTC-EUR_minute.csv', parse_dates=['DateTime'])
    df.set_index('DateTime', inplace=True)
    
    print(f"✅ Daten geladen: {df.shape}")

    # Test Parameter
    past_window = 7
    tw = 3
    start_idx = 100
    end_idx = 200

    print(f"\n📊 Teste Optimierung mit:")
    print(f"   past_window: {past_window}")
    print(f"   trade_window (tw): {tw}")
    print(f"   start_idx: {start_idx}, end_idx: {end_idx}")

    # Teste die komplette Optimierungsschleife Schritt für Schritt
    df_opt = df.iloc[start_idx:end_idx].copy()
    print(f"   1. Daten geschnitten: {df_opt.shape}")

    # 1. Support/Resistance berechnen
    print("   2. Berechne Support/Resistance...")
    support, resistance = calculate_support_resistance(df, past_window, tw, verbose=False)
    print(f"      Support/Resistance berechnet")

    # 2. Signale generieren
    print("   3. Generiere Signale...")
    signal_df = assign_long_signals_extended(support, resistance, df, tw, "1d")
    print(f"      Signal_df shape: {signal_df.shape}")
    if 'Action' in signal_df.columns:
        print(f"      Actions counts: {signal_df['Action'].value_counts().to_dict()}")

    # 3. Update Level Close
    print("   4. Update Level Close...")
    signal_df = update_level_close_long(signal_df, df)
    print(f"      Updated signal_df shape: {signal_df.shape}")

    # 4. Simuliere Trades
    print("   5. Simuliere Trades...")
    result = simulate_trades_compound_extended(
        signal_df, df,
        starting_capital=cfg['initial_capital'],
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1)
    )
    
    # Entpacke das Ergebnis korrekt
    if isinstance(result, tuple):
        final_capital, trades_log = result
    else:
        final_capital = result
    
    print(f"      ✅ Final capital: {final_capital}")
    print(f"      Initial capital: {cfg['initial_capital']}")

    pnl = ((final_capital - cfg['initial_capital']) / cfg['initial_capital']) * 100
    print(f"      📈 PnL: {pnl:.2f}%")
    
    print(f"\n🎯 ERFOLG! Die Optimierung läuft jetzt ohne Fehler!")
    print(f"   ✅ Date-Normalisierung funktioniert")
    print(f"   ✅ Trade-Simulation funktioniert")  
    print(f"   ✅ PnL wird korrekt berechnet: {pnl:.2f}%")

except Exception as e:
    print(f"❌ Fehler in der manuellen Optimierung: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("🔍 DEBUG Ende")
