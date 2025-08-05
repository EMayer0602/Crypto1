#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
import os

def add_artificial_daily_entry():
    """
    Füge künstlichen Tageseintrag mit Bitpanda Real-time Daten hinzu
    O = C = Last Price, H = Ask, L = Bid, V = -1000 (artificial marker)
    """
    
    print("🤖 KÜNSTLICHE TAGESEINTRÄGE ERSTELLEN")
    print("="*60)
    
    # Lade Real-time Daten
    realtime_file = "current_market_prices.csv"
    
    if not os.path.exists(realtime_file):
        print(f"❌ {realtime_file} nicht gefunden!")
        print("🔄 Führe zuerst update_yahoo_bitpanda.py aus")
        return
    
    # Lade Bitpanda Real-time Daten
    realtime_df = pd.read_csv(realtime_file)
    
    print(f"📊 Real-time Daten geladen: {len(realtime_df)} Symbole")
    print(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Verarbeite jedes Symbol
    for _, row in realtime_df.iterrows():
        symbol = row['symbol']
        bid = row['bid']
        ask = row['ask'] 
        last = row['last']
        
        csv_file = f"{symbol}_daily.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ {csv_file} nicht gefunden - überspringe")
            continue
            
        print(f"\n🔄 Processing {symbol}...")
        
        try:
            # Lade bestehende CSV
            df = pd.read_csv(csv_file)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Prüfe ob heute schon existiert
            today = datetime.now().date()
            today_timestamp = pd.Timestamp(today)
            today_mask = df['Date'].dt.date == today
            
            if today_mask.any():
                # Heute existiert bereits - prüfe ob artificial (-1000 Volume)
                existing_row = df[today_mask]
                if existing_row['Volume'].iloc[0] == -1000:
                    print(f"   🔄 Aktualisiere bestehenden artificial entry")
                    # Update bestehenden artificial entry
                    df.loc[today_mask, 'Open'] = last
                    df.loc[today_mask, 'High'] = ask  
                    df.loc[today_mask, 'Low'] = bid
                    df.loc[today_mask, 'Close'] = last
                    df.loc[today_mask, 'Volume'] = -1000
                else:
                    print(f"   ⚠️ Heute existiert bereits mit echten Daten (Volume: {existing_row['Volume'].iloc[0]})")
                    continue
            else:
                # Erstelle neuen artificial entry für heute
                print(f"   ➕ Erstelle neuen artificial entry")
                
                new_row = pd.DataFrame({
                    'Date': [pd.Timestamp(today)],
                    'Open': [last],      # O = aktueller Price
                    'High': [ask],       # H = Ask (höher)
                    'Low': [bid],        # L = Bid (niedriger)  
                    'Close': [last],     # C = aktueller Price
                    'Volume': [-1000]    # V = -1000 (artificial marker)
                })
                
                # Füge hinzu und sortiere
                df = pd.concat([df, new_row], ignore_index=True)
                df = df.sort_values('Date')
            
            # Speichere aktualisierte CSV
            df.to_csv(csv_file, index=False)
            
            print(f"   ✅ {symbol}: O={last:.4f} H={ask:.4f} L={bid:.4f} C={last:.4f} V=-1000")
            print(f"      💰 Spread: €{ask-bid:.4f} ({((ask-bid)/last*100):.3f}%)")
            
        except Exception as e:
            print(f"   ❌ {symbol}: Fehler - {e}")
    
    print(f"\n{'='*60}")
    print("🎉 ARTIFICIAL ENTRIES ERSTELLT")
    print("📝 Alle Einträge haben Volume = -1000 als Marker")
    print("🔄 Morgen können diese durch echte Yahoo Finance Daten ersetzt werden")
    print("="*60)

def show_artificial_entries():
    """Zeige alle artificial entries (Volume = -1000)"""
    
    symbols = ["BTC-EUR", "ETH-EUR", "DOGE-EUR", "SOL-EUR", "LINK-EUR", "XRP-EUR"]
    
    print(f"\n🔍 ARTIFICIAL ENTRIES ÜBERSICHT")
    print("="*80)
    
    for symbol in symbols:
        csv_file = f"{symbol}_daily.csv"
        
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            
            # Finde artificial entries
            artificial_mask = df['Volume'] == -1000
            artificial_entries = df[artificial_mask]
            
            if len(artificial_entries) > 0:
                print(f"\n📊 {symbol} - {len(artificial_entries)} artificial entries:")
                for _, row in artificial_entries.iterrows():
                    date = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
                    o, h, l, c = row['Open'], row['High'], row['Low'], row['Close']
                    spread = h - l
                    spread_pct = (spread / c * 100) if c > 0 else 0
                    print(f"   {date}: O={o:.4f} H={h:.4f} L={l:.4f} C={c:.4f} | Spread: {spread_pct:.3f}%")
            else:
                print(f"   {symbol}: Keine artificial entries")

if __name__ == "__main__":
    # Erstelle artificial entries
    add_artificial_daily_entry()
    
    # Zeige Übersicht
    show_artificial_entries()
