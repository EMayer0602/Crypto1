#!/usr/bin/env python3

import pandas as pd
from datetime import datetime, date
import os

def add_missing_august_4():
    """
    Füge 4. August durch Interpolation hinzu (da Yahoo Finance keine Daten hat)
    """
    
    print("📅 4. AUGUST 2025 HINZUFÜGEN")
    print("="*50)
    print("ℹ️ Yahoo Finance hat keine Daten für 4. August (Sonntag)")
    print("🔄 Verwende Interpolation zwischen 3. und 5. August")
    
    symbols = ["BTC-EUR", "ETH-EUR", "DOGE-EUR", "SOL-EUR", "LINK-EUR", "XRP-EUR"]
    
    for symbol in symbols:
        csv_file = f"{symbol}_daily.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ {csv_file} nicht gefunden")
            continue
            
        print(f"\n🔄 Processing {symbol}...")
        
        try:
            # Lade CSV
            df = pd.read_csv(csv_file)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Prüfe ob 4. August schon existiert
            aug_4_date = pd.Timestamp('2025-08-04')
            aug_4_mask = df['Date'] == aug_4_date
            
            if aug_4_mask.any():
                print(f"   ℹ️ 4. August bereits vorhanden")
                continue
            
            # Finde 3. August und 5. August
            aug_3_mask = df['Date'] == pd.Timestamp('2025-08-03')
            aug_5_mask = df['Date'] == pd.Timestamp('2025-08-05')
            
            if not aug_3_mask.any():
                print(f"   ❌ 3. August nicht gefunden")
                continue
                
            if not aug_5_mask.any():
                print(f"   ❌ 5. August nicht gefunden")
                continue
            
            # Hole Daten vom 3. und 5. August
            aug_3_data = df[aug_3_mask].iloc[0]
            aug_5_data = df[aug_5_mask].iloc[0]
            
            # Prüfe ob 5. August artificial data ist (Volume = -1000)
            if aug_5_data['Volume'] == -1000:
                print(f"   📊 5. August ist artificial data - verwende für Interpolation")
            
            # Interpoliere OHLC Werte (Durchschnitt zwischen 3. und 5. August)
            interpolated_open = (aug_3_data['Open'] + aug_5_data['Open']) / 2
            interpolated_high = max(aug_3_data['High'], aug_5_data['High'])  # Höchster High
            interpolated_low = min(aug_3_data['Low'], aug_5_data['Low'])     # Niedrigster Low
            interpolated_close = (aug_3_data['Close'] + aug_5_data['Close']) / 2
            interpolated_volume = (aug_3_data['Volume'] + abs(aug_5_data['Volume'])) / 2
            
            # Erstelle 4. August Eintrag
            new_row = pd.DataFrame({
                'Date': [aug_4_date],
                'Open': [interpolated_open],
                'High': [interpolated_high],
                'Low': [interpolated_low],
                'Close': [interpolated_close],
                'Volume': [interpolated_volume]
            })
            
            # Füge hinzu und sortiere
            df = pd.concat([df, new_row], ignore_index=True)
            df = df.sort_values('Date')
            
            # Speichere
            df.to_csv(csv_file, index=False)
            
            print(f"   ✅ 4. August hinzugefügt:")
            print(f"      Open:   €{interpolated_open:.2f}")
            print(f"      High:   €{interpolated_high:.2f}")
            print(f"      Low:    €{interpolated_low:.2f}")
            print(f"      Close:  €{interpolated_close:.2f}")
            print(f"      Volume: {interpolated_volume:,.0f}")
            
        except Exception as e:
            print(f"   ❌ {symbol}: Fehler - {e}")
    
    print(f"\n{'='*50}")
    print("🎉 4. AUGUST HINZUGEFÜGT")
    print("📊 Verwendete Interpolation zwischen 3. und 5. August")
    print("="*50)

def verify_august_data():
    """Verifiziere dass alle August Daten vorhanden sind"""
    
    print(f"\n🔍 VERIFIKATION AUGUST DATEN")
    print("="*40)
    
    symbols = ["BTC-EUR", "ETH-EUR", "DOGE-EUR", "SOL-EUR", "LINK-EUR", "XRP-EUR"]
    august_dates = ['2025-08-01', '2025-08-02', '2025-08-03', '2025-08-04', '2025-08-05']
    
    for symbol in symbols:
        csv_file = f"{symbol}_daily.csv"
        
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df['Date'] = pd.to_datetime(df['Date'])
            
            print(f"\n📊 {symbol}:")
            for date_str in august_dates:
                date_mask = df['Date'].dt.date == pd.to_datetime(date_str).date()
                if date_mask.any():
                    row = df[date_mask].iloc[0]
                    volume_info = " (artificial)" if row['Volume'] == -1000 else ""
                    print(f"   ✅ {date_str}: Close €{row['Close']:.2f}{volume_info}")
                else:
                    print(f"   ❌ {date_str}: FEHLT")

if __name__ == "__main__":
    # Füge 4. August hinzu
    add_missing_august_4()
    
    # Verifiziere alle August Daten
    verify_august_data()
