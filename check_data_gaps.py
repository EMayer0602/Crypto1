#!/usr/bin/env python3

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os

def check_data_gaps():
    """Prüfe Datenlücken in den Daily CSV Dateien"""
    
    symbols = ["BTC-EUR", "ETH-EUR", "DOGE-EUR", "SOL-EUR", "LINK-EUR", "XRP-EUR"]
    
    for symbol in symbols:
        csv_file = f"{symbol}_daily.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ {csv_file} nicht gefunden")
            continue
            
        print(f"\n{'='*50}")
        print(f"📊 Checking {symbol}")
        print(f"{'='*50}")
        
        # Lade bestehende Daten
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'])
        
        print(f"📅 Datenbereich: {df['Date'].min()} bis {df['Date'].max()}")
        print(f"📊 Anzahl Zeilen: {len(df)}")
        
        # Zeige letzte 5 Tage
        print(f"\n🔍 Letzte 5 Einträge:")
        for i, row in df.tail(5).iterrows():
            print(f"   {row['Date'].strftime('%Y-%m-%d')}: Close €{row['Close']:.2f}")
        
        # Prüfe ob Daten bis heute fehlen
        today = datetime.now().date()
        last_date = df['Date'].max().date()
        
        if last_date < today:
            missing_days = (today - last_date).days
            print(f"\n⚠️ DATEN FEHLEN: {missing_days} Tage seit {last_date}")
            
            # Lade fehlende Daten
            print(f"🔄 Lade fehlende Daten für {symbol}...")
            try:
                ticker = yf.Ticker(symbol)
                
                # Lade Daten ab dem Tag nach dem letzten verfügbaren Datum
                start_date = last_date + timedelta(days=1)
                
                new_data = ticker.history(
                    start=start_date.strftime('%Y-%m-%d'),
                    end=today.strftime('%Y-%m-%d'),
                    interval='1d'
                )
                
                if len(new_data) > 0:
                    # Reset index um Date als Spalte zu haben
                    new_data = new_data.reset_index()
                    
                    # Fix timezone issue - convert to date only
                    new_data['Date'] = pd.to_datetime(new_data['Date']).dt.date
                    new_data['Date'] = pd.to_datetime(new_data['Date'])
                    
                    # Wähle nur benötigte Spalten und benenne um
                    new_data = new_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
                    
                    # Kombiniere mit bestehenden Daten
                    combined_df = pd.concat([df, new_data], ignore_index=True)
                    combined_df = combined_df.drop_duplicates(subset=['Date']).sort_values('Date')
                    
                    # Speichere aktualisierte Datei
                    combined_df.to_csv(csv_file, index=False)
                    print(f"✅ {len(new_data)} neue Zeilen hinzugefügt")
                    print(f"📅 Neuer Datenbereich: {combined_df['Date'].min()} bis {combined_df['Date'].max()}")
                    
                    # Zeige neue Einträge
                    print(f"\n🆕 Neue Einträge:")
                    for i, row in new_data.iterrows():
                        date_str = row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date'])
                        print(f"   {date_str}: Close €{row['Close']:.2f}")
                        
                else:
                    print(f"ℹ️ Keine neuen Daten verfügbar (möglicherweise Wochenende)")
                    
            except Exception as e:
                print(f"❌ Fehler beim Laden neuer Daten: {e}")
        else:
            print(f"✅ Daten sind aktuell bis {last_date}")

if __name__ == "__main__":
    check_data_gaps()
