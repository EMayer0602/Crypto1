#!/usr/bin/env python3

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

def update_missing_data():
    """Update fehlende Daten in allen CSV Dateien"""
    
    symbols = ["BTC-EUR", "ETH-EUR", "DOGE-EUR", "SOL-EUR", "LINK-EUR", "XRP-EUR"]
    
    for symbol in symbols:
        csv_file = f"{symbol}_daily.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ {csv_file} nicht gefunden")
            continue
            
        print(f"\n{'='*50}")
        print(f"🔄 Updating {symbol}")
        print(f"{'='*50}")
        
        # Lade bestehende Daten
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date']).dt.date  # Timezone-naive
        
        # Finde Datenlücken und fehlende Tage
        last_date = max(df['Date'])
        print(f"📅 Letztes Datum in CSV: {last_date}")
        
        # Lade neue Daten von Yahoo Finance
        try:
            ticker = yf.Ticker(symbol)
            
            # Lade Daten ab 30. Juli bis heute
            data = ticker.history(
                start='2025-07-30',
                end=datetime.now().strftime('%Y-%m-%d'),
                interval='1d'
            )
            
            if len(data) > 0:
                # Konvertiere zu DataFrame mit Date als Spalte
                new_df = data.reset_index()
                new_df['Date'] = pd.to_datetime(new_df['Date']).dt.date  # Timezone-naive
                
                # Wähle nur benötigte Spalten
                new_df = new_df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
                
                # Filtere nur Daten die noch nicht existieren
                existing_dates = set(df['Date'])
                new_df = new_df[~new_df['Date'].isin(existing_dates)]
                
                if len(new_df) > 0:
                    print(f"📊 Neue Daten gefunden:")
                    for _, row in new_df.iterrows():
                        print(f"   {row['Date']}: Close €{row['Close']:.2f}")
                    
                    # Kombiniere und sortiere
                    combined_df = pd.concat([df, new_df], ignore_index=True)
                    combined_df['Date'] = pd.to_datetime(combined_df['Date'])
                    combined_df = combined_df.sort_values('Date')
                    
                    # Speichere
                    combined_df.to_csv(csv_file, index=False)
                    print(f"✅ {len(new_df)} neue Zeilen zu {csv_file} hinzugefügt")
                    
                    # Prüfe 1. August speziell
                    aug_1 = datetime(2025, 8, 1).date()
                    if aug_1 in new_df['Date'].values:
                        aug_1_row = new_df[new_df['Date'] == aug_1]
                        print(f"🎯 1. August hinzugefügt: €{aug_1_row['Close'].iloc[0]:.2f}")
                    
                else:
                    print(f"ℹ️ Keine neuen Daten für {symbol}")
                    
            else:
                print(f"❌ Keine Daten von Yahoo Finance für {symbol}")
                
        except Exception as e:
            print(f"❌ Fehler bei {symbol}: {e}")

if __name__ == "__main__":
    update_missing_data()
    print(f"\n{'='*60}")
    print("🎉 UPDATE ABGESCHLOSSEN")
    print("='*60")
