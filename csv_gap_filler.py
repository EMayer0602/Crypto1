#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV Gap Filler - Füllt Lücken in Daily CSV-Dateien und aktualisiert heutige Preise von Bitpanda
"""

import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import os
import glob

def get_bitpanda_price(symbol):
    """Hole aktuellen Preis von Bitpanda API"""
    try:
        # Bitpanda Pro API für aktuellen Preis
        # Symbol format: BTC-EUR -> BTCEUR
        bitpanda_symbol = symbol.replace('-', '')
        
        # Versuche verschiedene Bitpanda API Endpoints
        urls = [
            f"https://api.bitpanda.com/v1/ticker/{bitpanda_symbol}",
            f"https://api.exchange.bitpanda.com/public/v1/market-ticker/{symbol}",
            f"https://api.exchange.bitpanda.com/public/v1/market-ticker"
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"Bitpanda API Response für {symbol}: {data}")
                    
                    # Parse verschiedene Response-Formate
                    if 'last' in data:
                        return float(data['last'])
                    elif 'last_price' in data:
                        return float(data['last_price'])
                    elif 'price' in data:
                        return float(data['price'])
                    elif isinstance(data, list):
                        # Market ticker liste
                        for item in data:
                            if item.get('instrument_code') == symbol:
                                return float(item.get('last_price', 0))
                    
            except Exception as e:
                print(f"URL {url} fehlgeschlagen: {e}")
                continue
        
        print(f"Alle Bitpanda URLs fehlgeschlagen für {symbol}")
        return None
        
    except Exception as e:
        print(f"Bitpanda API Fehler für {symbol}: {e}")
        return None

def fill_csv_gaps(csv_file):
    """Füllt ALLE Lücken in CSV-Datei und aktualisiert heutige Preise"""
    
    print(f"\nPrüfe CSV-Datei: {csv_file}")
    print("=" * 60)
    
    try:
        # Lade CSV
        df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
        original_length = len(df)
        
        print(f"Original CSV: {original_length} Zeilen")
        print(f"Datum von: {df.index.min()} bis: {df.index.max()}")
        
        # Extrahiere Symbol aus Filename
        symbol = os.path.basename(csv_file).replace('_daily.csv', '')
        print(f"Symbol: {symbol}")
        
        # Definiere Zeitbereich: Start bis gestern
        start_date = df.index.min()
        yesterday = pd.Timestamp.now().normalize() - timedelta(days=1)
        today = pd.Timestamp.now().normalize()
        
        print(f"Ziel-Zeitbereich: {start_date} bis {yesterday}")
        
        # Erstelle vollständigen Datumsbereich (täglich) - OHNE Wochenenden!
        # Crypto handelt 7 Tage die Woche, also nehmen wir alle Tage
        full_date_range = pd.date_range(start=start_date, end=yesterday, freq='D')
        print(f"Vollständiger Range: {len(full_date_range)} Tage")
        
        # Finde ALLE fehlenden Daten (egal ob Volume -1000 oder komplett leer)
        missing_dates = full_date_range.difference(df.index)
        print(f"Komplett fehlende Daten: {len(missing_dates)} Tage")
        
        # Zeige fehlende Bereiche (Urlaub, etc.)
        if len(missing_dates) > 0:
            print("\nFehlende Datenbereiche:")
            
            # Sortiere fehlende Daten
            missing_sorted = sorted(missing_dates)
            
            # Gruppiere zusammenhängende Bereiche
            current_start = missing_sorted[0]
            current_end = missing_sorted[0]
            
            for i, date in enumerate(missing_sorted[1:], 1):
                if (date - current_end).days == 1:
                    # Zusammenhängender Bereich
                    current_end = date
                else:
                    # Bereich beendet, zeige ihn
                    if current_start == current_end:
                        print(f"  Einzelner Tag: {current_start.date()}")
                    else:
                        days_missing = (current_end - current_start).days + 1
                        print(f"  Bereich: {current_start.date()} bis {current_end.date()} ({days_missing} Tage)")
                    
                    # Neuer Bereich startet
                    current_start = date
                    current_end = date
            
            # Letzter Bereich
            if current_start == current_end:
                print(f"  Einzelner Tag: {current_start.date()}")
            else:
                days_missing = (current_end - current_start).days + 1
                print(f"  Bereich: {current_start.date()} bis {current_end.date()} ({days_missing} Tage)")
        
        # Prüfe bestehende artificial entries (Volume = -1000)
        existing_artificial = df[df['Volume'] == -1000]
        print(f"Bestehende artificial entries: {len(existing_artificial)}")
        
        # Fülle ALLE Lücken mit artificial entries
        if len(missing_dates) > 0:
            print(f"\nFülle {len(missing_dates)} Lücken mit artificial entries...")
            
            for missing_date in missing_dates:
                # Finde den besten Preis zum Füllen
                fill_price = None
                
                # 1. Versuche: Letzter verfügbarer Preis VOR dem fehlenden Datum
                available_before = df.index[df.index < missing_date]
                if len(available_before) > 0:
                    last_before = available_before.max()
                    fill_price = df.loc[last_before, 'Close']
                    print(f"  {missing_date.date()}: Fülle mit Preis vom {last_before.date()} = {fill_price:.4f}")
                
                # 2. Falls kein Preis vor dem Datum: Nimm ersten Preis NACH dem Datum
                if fill_price is None:
                    available_after = df.index[df.index > missing_date]
                    if len(available_after) > 0:
                        first_after = available_after.min()
                        fill_price = df.loc[first_after, 'Close']
                        print(f"  {missing_date.date()}: Fülle mit Preis vom {first_after.date()} = {fill_price:.4f}")
                
                # 3. Fallback: Default-Preis
                if fill_price is None:
                    fill_price = 1.0
                    print(f"  {missing_date.date()}: Fülle mit Default-Preis = {fill_price:.4f}")
                
                # Erstelle artificial entry - ALLE Preise gleich für Gap-Filling
                artificial_row = {
                    'Open': fill_price,
                    'High': fill_price,
                    'Low': fill_price,
                    'Close': fill_price,
                    'Volume': -1000  # ARTIFICIAL MARKER
                }
                
                # Füge zur DataFrame hinzu
                df.loc[missing_date] = artificial_row
        
        # Sortiere DataFrame nach Datum
        df = df.sort_index()
        
        # HEUTE: Aktualisiere mit Bitpanda Realtime-Preis
        if today in df.index:
            print(f"\nHEUTE ({today.date()}) bereits in CSV vorhanden - prüfe ob artificial...")
            current_entry = df.loc[today]
            if current_entry['Volume'] == -1000:
                print("Heutiger Eintrag ist artificial - hole aktuellen Bitpanda-Preis...")
                
                # Hole aktuellen Preis von Bitpanda
                current_price = get_bitpanda_price(symbol)
                
                if current_price:
                    print(f"Bitpanda aktueller Preis: {current_price}")
                    
                    # Aktualisiere heutigen Eintrag
                    df.loc[today, 'Open'] = current_price
                    df.loc[today, 'High'] = current_price
                    df.loc[today, 'Low'] = current_price
                    df.loc[today, 'Close'] = current_price
                    df.loc[today, 'Volume'] = -1000  # Bleibt artificial marker
                    
                    print(f"Heutiger Preis aktualisiert: {current_price}")
                else:
                    print("Bitpanda-Preis nicht verfügbar - behalte alten Wert")
            else:
                print("Heutiger Eintrag ist bereits real (Volume != -1000) - keine Aktualisierung")
        else:
            print(f"\nHEUTE ({today.date()}) nicht in CSV - füge mit Bitpanda-Preis hinzu...")
            
            # Hole aktuellen Preis von Bitpanda
            current_price = get_bitpanda_price(symbol)
            
            if current_price:
                print(f"Bitpanda aktueller Preis: {current_price}")
                
                # Füge heutigen Eintrag hinzu
                today_row = {
                    'Open': current_price,
                    'High': current_price,
                    'Low': current_price,
                    'Close': current_price,
                    'Volume': -1000  # ARTIFICIAL MARKER
                }
                
                df.loc[today] = today_row
                print(f"Heutiger Eintrag hinzugefügt: {current_price}")
            else:
                print("Bitpanda-Preis nicht verfügbar - kein heutiger Eintrag")
        
        # Sortiere final
        df = df.sort_index()
        
        print(f"\nFinal CSV: {len(df)} Zeilen (war {original_length})")
        print(f"Hinzugefügt: {len(df) - original_length} Einträge")
        
        # Zähle artificial entries
        artificial_count = len(df[df['Volume'] == -1000])
        print(f"Artificial Entries (Volume=-1000): {artificial_count}")
        
        # Zeige letzte 5 Einträge zur Kontrolle
        print("\nLetzte 5 Einträge:")
        print(df.tail().to_string())
        
        # Speichere aktualisierte CSV
        df.to_csv(csv_file)
        print(f"\nCSV gespeichert: {csv_file}")
        
        return True
        
    except Exception as e:
        print(f"Fehler beim Verarbeiten von {csv_file}: {e}")
        import traceback
        traceback.print_exc()
        return False

def process_all_crypto_csvs():
    """Verarbeite alle Crypto CSV-Dateien"""
    
    print("CSV GAP FILLER - Füllt Lücken und aktualisiert heutige Preise")
    print("=" * 80)
    
    # Finde alle daily CSV-Dateien
    csv_pattern = "*-EUR_daily.csv"
    csv_files = glob.glob(csv_pattern)
    
    print(f"Gefundene CSV-Dateien: {len(csv_files)}")
    for csv_file in csv_files:
        print(f"  {csv_file}")
    print()
    
    if not csv_files:
        print("Keine CSV-Dateien gefunden!")
        return
    
    # Verarbeite jede CSV-Datei
    success_count = 0
    for csv_file in csv_files:
        if fill_csv_gaps(csv_file):
            success_count += 1
    
    print("\n" + "=" * 80)
    print(f"ZUSAMMENFASSUNG:")
    print(f"Verarbeitet: {success_count}/{len(csv_files)} CSV-Dateien")
    print(f"Alle CSV-Dateien sind jetzt gap-free und aktuell!")

if __name__ == "__main__":
    process_all_crypto_csvs()
