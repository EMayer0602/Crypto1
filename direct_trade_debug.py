#!/usr/bin/env python3
"""
🔍 DIRECT DEBUG - Trade Simulation
"""

import pandas as pd
import numpy as np
import config

print("🔍 DIRECT DEBUG - Trade Simulation")
print("="*50)

try:
    # Lade Signale
    from signal_utils import calculate_support_resistance, assign_long_signals_extended, update_level_close_long
    
    df = pd.read_csv('BTC-EUR_minute.csv', parse_dates=['DateTime'])
    df.set_index('DateTime', inplace=True)
    
    support, resistance = calculate_support_resistance(df, 7, 3, verbose=False)
    signal_df = assign_long_signals_extended(support, resistance, df, 3, "1d")
    signal_df = update_level_close_long(signal_df, df)
    
    print(f"Signal DataFrame Shape: {signal_df.shape}")
    print(f"Spalten: {list(signal_df.columns)}")
    print(f"Actions: {signal_df['Action'].value_counts().to_dict()}")
    
    # Filtere nur BUY/SELL Signale
    trades_df = signal_df[signal_df['Action'].isin(['buy', 'sell'])]
    print(f"Trade Signale: {len(trades_df)}")
    
    if len(trades_df) > 0:
        print(f"Erste 5 Trade Signale:")
        print(trades_df[['Action', 'Long Date detected', 'Close', 'Level Close']].head())
        
        # MANUELLE TRADE SIMULATION
        print(f"\n🔧 MANUELLE TRADE SIMULATION:")
        capital = 10000
        position_active = False
        trades = []
        
        for idx, row in trades_df.iterrows():
            action = row['Action']
            exec_date = row['Long Date detected']
            level_close = row['Level Close']
            
            print(f"  Signal {idx}: {action} am {exec_date}, Level Close: {level_close}")
            
            # Prüfe ob Datum im Market Data existiert
            if exec_date in df.index:
                price = float(df.loc[exec_date, "Close"])
                print(f"    ✅ Preis gefunden: {price}")
                
                if action == 'buy' and not position_active:
                    shares = capital / price * 0.99  # Vereinfachte Berechnung
                    print(f"    📈 BUY: {shares:.4f} shares @ {price}")
                    position_active = True
                    buy_price = price
                    trades.append(f"BUY {shares:.4f} @ {price}")
                    
                elif action == 'sell' and position_active:
                    pnl = (price - buy_price) / buy_price * capital
                    capital += pnl
                    print(f"    📉 SELL: @ {price}, PnL: {pnl:.2f}")
                    position_active = False
                    trades.append(f"SELL @ {price}, PnL: {pnl:.2f}")
                    
            else:
                print(f"    ❌ Datum nicht im Market Data gefunden!")
        
        print(f"\n📊 MANUELLE SIMULATION ERGEBNIS:")
        print(f"   Final Capital: {capital}")
        print(f"   Trades: {len(trades)}")
        print(f"   PnL: {((capital - 10000) / 10000) * 100:.2f}%")
        
        if len(trades) > 0:
            print(f"   ✅ Trades ausgeführt!")
            for trade in trades[:5]:  # Erste 5
                print(f"     - {trade}")
        else:
            print(f"   ❌ Keine Trades ausgeführt!")
    
    else:
        print(f"❌ Keine Trade-Signale gefunden!")
        
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("🔍 DEBUG Ende")
