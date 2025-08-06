#!/usr/bin/env python3
"""
🔍 Quick Test - SOL-EUR mit optimierten Parametern
"""

import pandas as pd
from signal_utils import calculate_support_resistance, assign_long_signals_extended

print("🔍 TEST - SOL-EUR mit optimierten Parametern")
print("="*50)

try:
    # Lade SOL Daten
    df = pd.read_csv('SOL-EUR_daily.csv', index_col=0, parse_dates=True)
    print(f"✅ SOL Daten geladen: {df.shape}")
    
    # Verwende optimierte Parameter (aus CSV)
    p = 9
    tw = 1
    
    print(f"📊 Teste SOL-EUR mit past_window={p}, trade_window={tw}")
    
    # Support/Resistance mit optimierten Parametern
    support, resistance = calculate_support_resistance(df, p, tw, verbose=False)
    print(f"✅ Support Levels: {len(support)}")
    print(f"✅ Resistance Levels: {len(resistance)}")
    
    # Extended Signals mit optimierten tw
    ext_signals = assign_long_signals_extended(support, resistance, df, tw, "1d")
    print(f"✅ Extended Signals generiert: {len(ext_signals)}")
    
    # Überprüfe Trade Day Offset für erste 3 Signale
    if len(ext_signals) > 0:
        print(f"\n🔍 TRADE DAY OFFSET VERIFICATION (SOL-EUR):")
        print("-"*60)
        for i in range(min(3, len(ext_signals))):
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
    
    print(f"\n✅ SOL-EUR Test abgeschlossen!")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
