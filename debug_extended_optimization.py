#!/usr/bin/env python3
"""
🔍 DEBUG - Überprüfe ob Extended Trades jetzt optimierte Parameter verwenden
"""

import pandas as pd
from signal_utils import calculate_support_resistance, assign_long_signals_extended, berechne_best_p_tw_long
from datetime import datetime

print("🔍 DEBUG - Extended Trades mit optimierten Parametern")
print("="*60)

try:
    # Lade BTC Daten
    df = pd.read_csv('BTC-EUR_daily.csv', index_col=0, parse_dates=True)
    print(f"✅ BTC Daten geladen: {df.shape}")
    
    # Config für Optimierung
    cfg = {
        'initial_capital': 10000,
        'commission_rate': 0.0018,
        'min_commission': 1.0,
        'order_round_factor': 0.01
    }
    
    # 1. Optimiere Parameter
    print(f"\n1. 📊 OPTIMIERE PARAMETER...")
    n = len(df)
    start_idx = int(n * 0.0)  # 0%
    end_idx = int(n * 0.5)    # 50%
    
    p, tw, best_final_cap = berechne_best_p_tw_long(df, cfg, start_idx, end_idx, verbose=True, ticker="BTC-EUR")
    print(f"✅ Optimale Parameter: past_window={p}, trade_window={tw}, best_cap={best_final_cap}")
    
    # 2. Support/Resistance mit optimierten Parametern
    print(f"\n2. 📊 CALCULATE SUPPORT/RESISTANCE...")
    support, resistance = calculate_support_resistance(df, p, tw, verbose=True, ticker="BTC-EUR")
    print(f"✅ Support Levels: {len(support)}")
    print(f"✅ Resistance Levels: {len(resistance)}")
    
    # 3. Extended Signals mit optimierten tw
    print(f"\n3. 📊 GENERATE EXTENDED SIGNALS...")
    print(f"   🎯 Verwende tw={tw} für Trade Day Berechnung...")
    
    ext_signals = assign_long_signals_extended(support, resistance, df, tw, "1d")
    
    print(f"✅ Extended Signals generiert: {len(ext_signals)}")
    
    # 4. Zeige erste paar Signale zur Überprüfung
    if len(ext_signals) > 0:
        print(f"\n4. 📊 ERSTE 10 EXTENDED SIGNALS:")
        print("-"*120)
        display_cols = ['Date high/low', 'Supp/Resist', 'Action', 'Long Date detected', 'Level Close']
        print(ext_signals[display_cols].head(10).to_string(index=False))
        
        # 5. Überprüfe Trade Day Offset
        print(f"\n5. 🔍 TRADE DAY OFFSET VERIFICATION:")
        print("-"*60)
        for i in range(min(5, len(ext_signals))):
            row = ext_signals.iloc[i]
            level_date = pd.to_datetime(row['Date high/low'])
            trade_date = pd.to_datetime(row['Long Date detected'])
            offset_days = (trade_date - level_date).days
            
            print(f"   Signal {i+1}: Level={level_date.strftime('%Y-%m-%d')}, "
                  f"Trade={trade_date.strftime('%Y-%m-%d')}, "
                  f"Offset={offset_days} Tage (soll {tw} sein)")
            
            if offset_days != tw:
                print(f"   ❌ FEHLER: Offset ist {offset_days}, sollte {tw} sein!")
            else:
                print(f"   ✅ KORREKT: Offset ist {offset_days} = tw")
    
    print(f"\n🎯 ZUSAMMENFASSUNG:")
    print(f"   Optimiertes past_window: {p}")
    print(f"   Optimiertes trade_window: {tw}")
    print(f"   Extended Signals: {len(ext_signals)}")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
