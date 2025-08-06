#!/usr/bin/env python3
"""
🔍 DEBUG - Trade Execution Check
Überprüfe warum keine Trades ausgeführt werden (PnL = 0%)
"""

import pandas as pd
import numpy as np
import config
from signal_utils import calculate_support_resistance, assign_long_signals_extended, update_level_close_long
from MultiTradingIB25D_crypto import simulate_trades_compound_extended

print("🔍 DEBUG - Trade Execution Check")
print("="*50)

try:
    # Konfiguration
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
    
    # Verwende größeren Datenbereich für mehr Trades
    past_window = 7
    tw = 3
    start_idx = 100
    end_idx = 500  # Größerer Bereich für mehr Signale
    
    print(f"\n📊 Teste mit größerem Bereich:")
    print(f"   past_window: {past_window}")
    print(f"   trade_window: {tw}")
    print(f"   Data range: {start_idx} bis {end_idx} ({end_idx - start_idx} Zeilen)")
    
    # 1. Support/Resistance berechnen
    print("\n1. Support/Resistance...")
    support, resistance = calculate_support_resistance(df, past_window, tw, verbose=False)
    print(f"   Support type: {type(support)}")
    print(f"   Resistance type: {type(resistance)}")
    
    # 2. Signale generieren
    print("\n2. Signale generieren...")
    signal_df = assign_long_signals_extended(support, resistance, df, tw, "1d")
    print(f"   Signal_df shape: {signal_df.shape}")
    
    # DETAILLIERTE SIGNAL-ANALYSE
    print(f"\n🔍 DETAILLIERTE SIGNAL-ANALYSE:")
    print(f"   Spalten: {list(signal_df.columns)}")
    
    if 'Action' in signal_df.columns:
        print(f"   Action Counts: {signal_df['Action'].value_counts().to_dict()}")
        buy_count = sum(signal_df['Action'] == 'buy')
        sell_count = sum(signal_df['Action'] == 'sell')
        none_count = sum(signal_df['Action'].isna()) + sum(signal_df['Action'] == 'None') + sum(signal_df['Action'] == None)
        print(f"   BUY Signale: {buy_count}")
        print(f"   SELL Signale: {sell_count}")
        print(f"   None/NaN: {none_count}")
        
        # Zeige erste paar BUY/SELL Signale
        trades = signal_df[signal_df['Action'].isin(['buy', 'sell'])]
        print(f"   Erste 5 Trades:")
        if len(trades) > 0:
            print(trades[['Action', 'Long Date detected', 'Close']].head())
        else:
            print("   ❌ KEINE BUY/SELL Signale gefunden!")
    
    # 3. Update Level Close
    print("\n3. Update Level Close...")
    signal_df = update_level_close_long(signal_df, df)
    print(f"   Updated signal_df shape: {signal_df.shape}")
    
    # Level Close Analysis
    if 'Level Close' in signal_df.columns:
        level_close_valid = signal_df['Level Close'].notna().sum()
        print(f"   Valid Level Close values: {level_close_valid}")
        print(f"   Level Close sample: {signal_df['Level Close'].dropna().head().tolist()}")
    
    # 4. Trade Simulation mit Debug
    print("\n4. Trade Simulation...")
    print(f"   Übergebe an simulate_trades_compound_extended:")
    print(f"   - signal_df: {signal_df.shape}")
    print(f"   - df: {df.shape}")
    print(f"   - starting_capital: {cfg['initial_capital']}")
    
    result = simulate_trades_compound_extended(
        signal_df, df,
        starting_capital=cfg['initial_capital'],
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1)
    )
    
    # Ergebnis-Analyse
    print(f"\n📊 TRADE SIMULATION ERGEBNIS:")
    print(f"   Result type: {type(result)}")
    print(f"   Result: {result}")
    
    if isinstance(result, tuple):
        final_capital, trades_log = result
        print(f"   Final capital: {final_capital}")
        print(f"   Trades log type: {type(trades_log)}")
        print(f"   Trades log length: {len(trades_log) if hasattr(trades_log, '__len__') else 'N/A'}")
        if hasattr(trades_log, '__len__') and len(trades_log) > 0:
            print(f"   First few trades: {trades_log[:3]}")
    else:
        final_capital = result
        print(f"   Final capital: {final_capital}")
    
    # PnL Berechnung
    if final_capital == cfg['initial_capital']:
        print(f"\n❌ PROBLEM: Final capital = Initial capital")
        print(f"   Das bedeutet: KEINE TRADES wurden ausgeführt!")
        print(f"   Mögliche Ursachen:")
        print(f"   - Keine BUY/SELL Signale")
        print(f"   - Signale werden von Trade-Simulation ignoriert")
        print(f"   - Fehler in simulate_trades_compound_extended")
    else:
        pnl = ((final_capital - cfg['initial_capital']) / cfg['initial_capital']) * 100
        print(f"   ✅ PnL: {pnl:.2f}%")

except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("🔍 DEBUG Ende")
