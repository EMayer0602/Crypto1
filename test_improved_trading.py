#!/usr/bin/env python3
"""
🔍 TEST - Verbesserte Einzelticker-Optimierung 
"""

import pandas as pd
import config
from signal_utils import calculate_support_resistance, assign_long_signals_extended, update_level_close_long
from MultiTradingIB25D_crypto import simulate_trades_compound_extended

print("🔍 TEST - Verbesserte Trade-Simulation")
print("="*50)

try:
    # Config
    cfg = {
        'initial_capital': 10000,
        'commission_rate': config.COMMISSION_RATE,
        'min_commission': config.MIN_COMMISSION,
        'order_round_factor': config.ORDER_ROUND_FACTOR
    }
    
    # Lade BTC-EUR Daten
    df = pd.read_csv('BTC-EUR_minute.csv', parse_dates=['DateTime'])
    df.set_index('DateTime', inplace=True)
    print(f"✅ Daten geladen: {df.shape}")
    
    # Test Parameter
    past_window = 7
    tw = 3
    
    print(f"\n📊 Teste mit:")
    print(f"   past_window: {past_window}")
    print(f"   trade_window: {tw}")
    
    # 1. Support/Resistance berechnen
    print("\n1. Support/Resistance...")
    support, resistance = calculate_support_resistance(df, past_window, tw, verbose=False)
    
    # 2. Signale generieren
    print("2. Signale generieren...")
    signal_df = assign_long_signals_extended(support, resistance, df, tw, "1d")
    print(f"   Signal_df shape: {signal_df.shape}")
    
    # Signal-Analyse
    if 'Action' in signal_df.columns:
        actions = signal_df['Action'].value_counts()
        print(f"   Actions: {actions.to_dict()}")
        buy_signals = signal_df[signal_df['Action'] == 'buy']
        sell_signals = signal_df[signal_df['Action'] == 'sell']
        print(f"   BUY Signale: {len(buy_signals)}")
        print(f"   SELL Signale: {len(sell_signals)}")

    # 3. Update Level Close
    print("3. Update Level Close...")
    signal_df = update_level_close_long(signal_df, df)
    
    # 4. Trade Simulation
    print("4. Trade Simulation...")
    result = simulate_trades_compound_extended(
        signal_df, df,
        starting_capital=cfg['initial_capital'],
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1)
    )
    
    # Ergebnis-Analyse
    if isinstance(result, tuple):
        final_capital, trades_log = result
    else:
        final_capital = result
        trades_log = []
    
    print(f"\n📊 ERGEBNIS:")
    print(f"   Final capital: {final_capital}")
    print(f"   Initial capital: {cfg['initial_capital']}")
    
    if final_capital != cfg['initial_capital']:
        pnl = ((final_capital - cfg['initial_capital']) / cfg['initial_capital']) * 100
        print(f"   ✅ PnL: {pnl:.2f}%")
        print(f"   ✅ SUCCESS! Trades wurden ausgeführt!")
        
        if hasattr(trades_log, '__len__') and len(trades_log) > 0:
            print(f"   ✅ {len(trades_log)} Trades ausgeführt")
        
    else:
        print(f"   ❌ FEHLER: Keine Trades ausgeführt (PnL = 0%)")
        print(f"   🔍 Debugging Info:")
        print(f"       - Signale vorhanden: {len(signal_df[signal_df['Action'].isin(['buy', 'sell'])])}")
        print(f"       - Level Close valid: {signal_df['Level Close'].notna().sum()}")

except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("🔍 TEST Ende")
