#!/usr/bin/env python3
"""
🔍 TEST - Einzelner Ticker Optimierung Test
Teste die korrigierte Optimierung für einen einzelnen Ticker
"""

import pandas as pd
from signal_utils import berechne_best_p_tw_long

print("🔍 TEST - Einzelner Ticker Optimierung")
print("="*50)

try:
    # Test mit BTC-EUR
    ticker = "BTC-EUR"
    print(f"Teste Optimierung für {ticker}...")
    
    # Lade Daten
    df = pd.read_csv('BTC-EUR_minute.csv', parse_dates=['DateTime'])
    df.set_index('DateTime', inplace=True)
    print(f"✅ Daten geladen: {df.shape}")
    
    # Config
    cfg = {
        'initial_capital': 10000,
        'commission_rate': 0.0018,
        'min_commission': 1.0,
        'order_round_factor': 0.01
    }
    
    # Begrenzte Optimierung (weniger Iterationen)
    print("🔄 Starte Optimierung...")
    best_p, best_tw, best_cap = berechne_best_p_tw_long(
        df, cfg, 
        start_idx=50, end_idx=100,  # Kleinere Range für Tests
        verbose=True, 
        ticker=ticker
    )
    
    print(f"\n🎯 ERGEBNIS für {ticker}:")
    print(f"   Best past_window: {best_p}")
    print(f"   Best trade_window: {best_tw}")
    print(f"   Best final_capital: {best_cap}")
    
    if best_cap is not None and best_cap > 0:
        pnl = ((best_cap - cfg['initial_capital']) / cfg['initial_capital']) * 100
        print(f"   📈 PnL: {pnl:.2f}%")
        print(f"   ✅ SUCCESS! PnL ist nicht mehr None!")
    else:
        print(f"   ❌ PnL ist immer noch None oder 0")
        
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("🔍 TEST Ende")
