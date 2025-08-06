#!/usr/bin/env python3

"""
Debug der PnL-Berechnung
"""

import pandas as pd
from signal_utils import berechne_best_p_tw_long

# Lade BTC Daten
print("🔍 Lade BTC-EUR Daten...")
try:
    df = pd.read_csv('BTC-EUR_daily.csv', index_col=0, parse_dates=True)
    print(f"✅ BTC Daten geladen: {df.shape}")
    print(f"   Letzte 5 Zeilen:")
    print(df.tail().to_string())
    
    # Config für Optimierung
    cfg = {
        'initial_capital': 10000,
        'commission_rate': 0.0018,
        'min_commission': 1.0,
        'order_round_factor': 0.01
    }
    
    start_idx = 0
    end_idx = len(df)
    
    print(f"\n🔍 Teste berechne_best_p_tw_long...")
    print(f"   DataFrame shape: {df.shape}")
    print(f"   Start_idx: {start_idx}, End_idx: {end_idx}")
    
    # Teste die Funktion
    result = berechne_best_p_tw_long(df, cfg, start_idx, end_idx, verbose=True, ticker="BTC-EUR")
    print(f"\n📊 Result: {result}")
    print(f"   Type: {type(result)}")
    print(f"   Length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
    
    if len(result) == 2:
        p, tw = result
        print(f"   Alte Rückgabe: p={p}, tw={tw}")
    elif len(result) == 3:
        p, tw, best_final_cap = result
        print(f"   Neue Rückgabe: p={p}, tw={tw}, best_final_cap={best_final_cap}")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
