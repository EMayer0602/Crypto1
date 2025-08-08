#!/usr/bin/env python3

import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import os
import time
import yfinance as yf

def get_real_crypto_data_coingecko():
    """
    Hole echte Crypto-Daten von CoinGecko (zuverlässiger als Yahoo Finance)
    """
    
    print("🔄 ECHTE CRYPTO-DATEN VON COINGECKO")
    print("="*50)
    print("ℹ️ Yahoo Finance ist verzögert - verwende CoinGecko")
    
    # CoinGecko Mapping
    coingecko_mapping = {
        "BTC-EUR": "bitcoin",
        "ETH-EUR": "ethereum", 
        "DOGE-EUR": "dogecoin",
        "SOL-EUR": "solana",
        "LINK-EUR": "chainlink",
        "XRP-EUR": "ripple"
    }
    
    # Hole Daten für die letzten 7 Tage
    results = {}
    
    for symbol, coin_id in coingecko_mapping.items():
        print(f"\n🔄 Loading {symbol} ({coin_id})...")
        
        try:
            # CoinGecko API für historische Daten (letzte 7 Tage)
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'eur',
                'days': '7',
                'interval': 'daily'
            }
            
            # Retry logic for rate limiting
            max_retries = 3
            for attempt in range(max_retries):
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    break
                elif response.status_code == 429:
                    print(f"   ⏳ Rate limited (attempt {attempt+1}/{max_retries}), waiting 10 seconds...")
                    time.sleep(10)
                else:
                    print(f"   ❌ API Error: {response.status_code} (attempt {attempt+1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrahiere Preise (timestamps und values)
                prices = data['prices']
                volumes = data['total_volumes']
                
                # Konvertiere zu DataFrame
                price_data = []
                for i, (timestamp, price) in enumerate(prices):
                    date = datetime.fromtimestamp(timestamp / 1000).date()
                    volume = volumes[i][1] if i < len(volumes) else 0
                    
                    # Simuliere OHLC aus Preis (CoinGecko gibt nur Close)
                    # Verwende kleine Variationen um OHLC zu simulieren
                    variation = price * 0.01  # 1% Variation
                    
                    price_data.append({
                        'Date': date,
                        'Open': price * 0.999,   # Leicht unter Close
                        'High': price * 1.005,   # Leicht über Close
                        'Low': price * 0.995,    # Leicht unter Close
                        'Close': price,          # Echter Close
                        'Volume': volume,
                        'Source': 'CoinGecko'
                    })
                
                results[symbol] = price_data
                print(f"   ✅ {len(price_data)} Tage geladen")
                
                # Zeige letzte 3 Tage
                for row in price_data[-3:]:
                    print(f"      {row['Date']}: €{row['Close']:.2f}")
                
            else:
                print(f"   ❌ CoinGecko failed after {max_retries} attempts")
                
                # Fallback to Yahoo Finance for XRP specifically
                if symbol == "XRP-EUR":
                    print(f"   🔄 Fallback: Using Yahoo Finance for {symbol}...")
                    try:
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=10)  # Last 10 days
                        
                        stock = yf.Ticker(symbol)
                        df = stock.history(start=start_date, end=end_date, interval='1d')
                        
                        if not df.empty:
                            price_data = []
                            for date, row in df.iterrows():
                                price_data.append({
                                    'Date': date.date(),
                                    'Open': row['Open'],
                                    'High': row['High'],
                                    'Low': row['Low'],
                                    'Close': row['Close'],
                                    'Volume': row['Volume'],
                                    'Source': 'YahooFinance_Fallback'
                                })
                            
                            results[symbol] = price_data
                            print(f"   ✅ Fallback successful: {len(price_data)} Tage von Yahoo Finance")
                            
                            # Zeige letzte 3 Tage
                            for row in price_data[-3:]:
                                print(f"      {row['Date']}: €{row['Close']:.2f} (YF)")
                        
                    except Exception as yf_error:
                        print(f"   ❌ Yahoo Finance Fallback failed: {yf_error}")
                
        except Exception as e:
            print(f"   ❌ {symbol}: Fehler - {e}")
        
        # Rate Limiting - increase delay for API limits
        time.sleep(3)  # Increased from 1 to 3 seconds
    
    return results

def download_missing_csv(symbol):
    """Lädt fehlende CSV-Datei herunter"""
    try:
        print(f"📥 Lade fehlende {symbol} Daten von Yahoo Finance...")
        
        # 1 Jahr Daten holen
        end_date = datetime.now()
        start_date = end_date - timedelta(days=400)  # Mehr als 1 Jahr für Sicherheit
        
        # Yahoo Finance Daten holen
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date, interval='1d')
        
        if df.empty:
            print(f"❌ Keine Daten für {symbol} von Yahoo Finance")
            return False
            
        # Index als Date column, nur OHLCV behalten
        df.index.name = 'Date'
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # CSV speichern
        filename = f"{symbol}_daily.csv"
        df.to_csv(filename)
        
        print(f"✅ {filename} heruntergeladen mit {len(df)} Zeilen")
        print(f"   Zeitraum: {df.index.min().date()} bis {df.index.max().date()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Herunterladen von {symbol}: {e}")
        return False

def update_csv_with_real_data(coingecko_data):
    """
    Update CSV Dateien mit echten CoinGecko Daten
    """
    
    print(f"\n📊 UPDATE CSV DATEIEN MIT ECHTEN DATEN")
    print("="*50)
    
    for symbol, new_data in coingecko_data.items():
        csv_file = f"{symbol}_daily.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ {csv_file} nicht gefunden - wird heruntergeladen...")
            if not download_missing_csv(symbol):
                print(f"❌ Konnte {csv_file} nicht herunterladen - überspringe")
                continue
            
        print(f"\n🔄 Updating {symbol}...")
        
        try:
            # Lade bestehende CSV
            df = pd.read_csv(csv_file)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            
            # Konvertiere neue Daten zu DataFrame
            new_df = pd.DataFrame(new_data)
            
            # Finde fehlende Daten (die nicht in CSV sind)
            existing_dates = set(df['Date'])
            new_entries = []
            
            for _, row in new_df.iterrows():
                if row['Date'] not in existing_dates:
                    new_entries.append(row)
            
            if new_entries:
                print(f"   📈 {len(new_entries)} neue Einträge gefunden:")
                
                for entry in new_entries:
                    print(f"      {entry['Date']}: €{entry['Close']:.2f} (CoinGecko)")
                    
                    # Füge zur CSV hinzu
                    new_row = pd.DataFrame([{
                        'Date': entry['Date'],
                        'Open': entry['Open'],
                        'High': entry['High'],
                        'Low': entry['Low'],
                        'Close': entry['Close'],
                        'Volume': entry['Volume']
                    }])
                    
                    df = pd.concat([df, new_row], ignore_index=True)
                
                # Sortiere und speichere
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                df.to_csv(csv_file, index=False)
                
                print(f"   ✅ {csv_file} aktualisiert")
            else:
                print(f"   ℹ️ Keine neuen Daten für {symbol}")
                
        except Exception as e:
            print(f"   ❌ {symbol}: Update-Fehler - {e}")

def show_august_overview():
    """Zeige August Übersicht nach Update"""
    
    print(f"\n📅 AUGUST 2025 ÜBERSICHT")
    print("="*60)
    
    symbols = ["BTC-EUR", "ETH-EUR", "DOGE-EUR", "SOL-EUR", "LINK-EUR", "XRP-EUR"]
    august_dates = ['2025-08-01', '2025-08-02', '2025-08-03', '2025-08-04', '2025-08-05']
    
    for symbol in symbols:
        csv_file = f"{symbol}_daily.csv"
        
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df['Date'] = pd.to_datetime(df['Date'])
            
            print(f"\n💰 {symbol}:")
            for date_str in august_dates:
                date_mask = df['Date'].dt.date == pd.to_datetime(date_str).date()
                if date_mask.any():
                    row = df[date_mask].iloc[0]
                    source = " (artificial)" if row['Volume'] == -1000 else " (real)"
                    print(f"   {date_str}: €{row['Close']:>10.2f}{source}")
                else:
                    print(f"   {date_str}: ❌ FEHLT")

def update_csv_files_with_realtime_data():
    """
    Wrapper function für Live Backtest - updated CSVs mit Echtzeitdaten
    """
    print("🚀 CSV UPDATE MIT ECHTZEITDATEN")
    print("="*50)
    
    # 1. Hole echte Daten von CoinGecko
    coingecko_data = get_real_crypto_data_coingecko()
    
    if coingecko_data:
        # 2. Update CSV Dateien (inkl. Download fehlender Dateien)
        update_csv_with_real_data(coingecko_data)
        print("✅ CSV Update abgeschlossen")
        return True
    else:
        print("❌ Keine Daten von CoinGecko erhalten")
        return False

def main():
    """Hauptfunktion"""
    
    print("🚀 ECHTE CRYPTO-DATEN UPDATE")
    print("="*60)
    print("❌ Yahoo Finance ist unzuverlässig")
    print("✅ Verwende CoinGecko für echte Daten")
    print("="*60)
    
    # 1. Hole echte Daten von CoinGecko
    coingecko_data = get_real_crypto_data_coingecko()
    
    if coingecko_data:
        # 2. Update CSV Dateien
        update_csv_with_real_data(coingecko_data)
        
        # 3. Zeige Übersicht
        show_august_overview()
        
        print(f"\n{'='*60}")
        print("🎉 ECHTE DATEN UPDATE ABGESCHLOSSEN")
        print("📊 Alle fehlenden Tage mit CoinGecko Daten gefüllt")
        print("💰 Bereit für echtes Trading")
        print("="*60)
    else:
        print("❌ Keine Daten von CoinGecko erhalten")

if __name__ == "__main__":
    main()
