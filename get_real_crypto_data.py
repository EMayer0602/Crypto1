#!/usr/bin/env python3

import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import os
import time
import yfinance as yf
from typing import Optional

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
                
                # Zeige letzte 5 Tage
                for row in price_data[-5:]:
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

def show_recent_overview(days:int=5):
    """Zeige dynamische Übersicht der letzten N Tage nach Update (default 5)."""
    print(f"\n📅 LETZTE {days} TAGE ÜBERSICHT")
    print("="*60)
    symbols = ["BTC-EUR", "ETH-EUR", "DOGE-EUR", "SOL-EUR", "LINK-EUR", "XRP-EUR"]
    
    today = datetime.now().date()
    recent_dates = [ (today - timedelta(days=i)) for i in range(days-1, -1, -1) ]
    
    for symbol in symbols:
        csv_file = f"{symbol}_daily.csv"
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            # Normalize to date objects for comparison
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            print(f"\n💰 {symbol}:")
            for d in recent_dates:
                if d in set(df['Date']):
                    row = df[df['Date'] == d].iloc[0]
                    source = " (artificial)" if row.get('Volume', 0) == -1000 else " (real)"
                    print(f"   {d}: €{row['Close']:>10.2f}{source}")
                else:
                    print(f"   {d}: ❌ FEHLT")

def update_csv_files_with_realtime_data():
    """
    Wrapper function für Live Backtest - Yahoo Advanced + Bitpanda live price for today.
    CoinGecko is no longer used in this pipeline.
    """
    print("🚀 CSV UPDATE MIT ECHTZEITDATEN (Yahoo + Bitpanda)")
    print("="*50)
    try:
        return update_csv_files_with_yahoo_advanced()
    except Exception as e:
        print(f"❌ Yahoo advanced update failed: {e}")
        return False

# ========================= YAHOO ADVANCED (daily to T-3, hourly fill, live today) =========================
def _fetch_yahoo_daily(symbol: str, start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
    stock = yf.Ticker(symbol)
    df = stock.history(start=start_dt, end=end_dt, interval='1d')
    if df is None or df.empty:
        return pd.DataFrame()
    df = df[['Open','High','Low','Close','Volume']].copy()
    # Normalize index to naive datetime.date
    if hasattr(df.index, 'tz') and df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    df.index = pd.to_datetime(df.index)
    df.index.name = 'Date'
    df.reset_index(inplace=True)
    df['Date'] = df['Date'].dt.date
    return df

def _fetch_yahoo_hourly(symbol: str, period: str = '5d') -> pd.DataFrame:
    stock = yf.Ticker(symbol)
    df = stock.history(period=period, interval='1h')
    if df is None or df.empty:
        return pd.DataFrame()
    df = df[['Open','High','Low','Close','Volume']].copy()
    if hasattr(df.index, 'tz') and df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    df.index = pd.to_datetime(df.index)
    df.index.name = 'Datetime'
    df.reset_index(inplace=True)
    return df

def _aggregate_hourly_to_daily(hourly_df: pd.DataFrame) -> pd.DataFrame:
    if hourly_df is None or hourly_df.empty:
        return pd.DataFrame()
    hourly_df['Date'] = pd.to_datetime(hourly_df['Datetime']).dt.date
    agg = hourly_df.groupby('Date').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).reset_index()
    return agg

def _get_live_price_proxy(symbol: str) -> Optional[float]:
    """Try BitpandaLiveIntegration; fallback to Yahoo intraday last close."""
    # Try Bitpanda live (with YF fallback internally)
    try:
        from bitpanda_live_integration import BitpandaLiveIntegration
        bli = BitpandaLiveIntegration()
        prices = bli.get_current_prices_live()
        # keys in prices are like BTC-EUR
        if symbol in prices and prices[symbol]['last']:
            return float(prices[symbol]['last'])
    except Exception:
        pass
    # Fallback: Yahoo 1m/1h
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period='1d', interval='1m')
        if df is None or df.empty:
            df = stock.history(period='1d', interval='1h')
        if df is not None and not df.empty:
            return float(pd.to_numeric(df['Close'], errors='coerce').dropna().iloc[-1])
    except Exception:
        return None
    return None

def get_bitpanda_price(symbol: str) -> Optional[float]:
    """Public helper to fetch a live price preferably from Bitpanda; falls back to Yahoo intraday.
    Returns None on failure."""
    return _get_live_price_proxy(symbol)

def update_csv_files_with_yahoo_advanced(symbols=None):
    """
    Load daily data from Yahoo up to T-3; if T-2/T-1 are missing, fill from hourly (last 5d);
    for today (T), set a row using a live price proxy (Bitpanda preferred).
    Saves to SYMBOL_daily.csv for each symbol.
    """
    print("🚀 YAHOO ADVANCED DAILY UPDATE")
    print("="*60)
    if symbols is None:
        try:
            from crypto_tickers import crypto_tickers as _ct
            symbols = list(_ct.keys())
        except Exception:
            symbols = ["BTC-EUR","ETH-EUR","DOGE-EUR","SOL-EUR","LINK-EUR","XRP-EUR"]

    today = datetime.now().date()
    cutoff_daily = today - timedelta(days=3)  # inclusive daily data until T-3

    for symbol in symbols:
        print(f"\n🔄 Updating {symbol} (Yahoo advanced)...")
        csv_file = f"{symbol}_daily.csv"

        # Load existing
        existing = pd.DataFrame()
        if os.path.exists(csv_file):
            try:
                existing = pd.read_csv(csv_file)
                if not existing.empty and 'Date' in existing.columns:
                    existing['Date'] = pd.to_datetime(existing['Date']).dt.date
                else:
                    existing = pd.DataFrame()
            except Exception as e:
                print(f"   ⚠️ Could not read existing CSV: {e}")
                existing = pd.DataFrame()

        # 1) Daily up to and including T-3 (end exclusive needs +1)
        start_dt = today - timedelta(days=420)
        end_dt = cutoff_daily + timedelta(days=1)
        daily_df = _fetch_yahoo_daily(symbol, start_dt, end_dt)
        print(f"   📅 Daily rows fetched (<= T-3): {len(daily_df)}")

        # Merge with existing (prefer fetched values for overlaps)
        merged = existing.copy()
        if not daily_df.empty:
            merged = pd.concat([merged, daily_df], ignore_index=True) if not merged.empty else daily_df.copy()
            merged.drop_duplicates(subset=['Date'], keep='last', inplace=True)

        # 2) Check T-2 and T-1; fill from hourly if missing
        target_dates = [today - timedelta(days=2), today - timedelta(days=1)]
        have_dates = set(merged['Date']) if not merged.empty else set()
        need_hourly = any(d not in have_dates for d in target_dates)
        if need_hourly:
            hourly = _fetch_yahoo_hourly(symbol, period='5d')
            agg = _aggregate_hourly_to_daily(hourly)
            if not agg.empty:
                valid_dates = { (today - timedelta(days=i)) for i in range(1,6) }
                agg = agg[agg['Date'].isin(valid_dates)]
                merged = pd.concat([merged, agg], ignore_index=True) if not merged.empty else agg.copy()
                merged.drop_duplicates(subset=['Date'], keep='last', inplace=True)
                print(f"   🕒 Filled from hourly: {len(agg)} days")
            else:
                print("   ⚠️ No hourly data available to fill gaps")

        # 3) Today (T) from live price proxy
        live_price = _get_live_price_proxy(symbol)
        if live_price is not None and live_price > 0:
            today_row = None
            have_dates = set(merged['Date']) if not merged.empty else set()
            if today in have_dates:
                # Update existing today's row: set Close to live
                mask = (pd.Series(list(merged['Date'])) == today)  # placeholder; will replace below
                # Simpler: remove today's row, re-add
                merged = merged[merged['Date'] != today]
            # Try intraday OHLC aggregation for today
            hourly = _fetch_yahoo_hourly(symbol, period='5d')
            agg = _aggregate_hourly_to_daily(hourly)
            if not agg.empty and today in set(agg['Date']):
                today_row = agg[agg['Date'] == today].iloc[0].to_dict()
                today_row['Close'] = live_price
            else:
                today_row = {'Date': today, 'Open': live_price, 'High': live_price, 'Low': live_price, 'Close': live_price, 'Volume': 0}
            today_df = pd.DataFrame([today_row])
            merged = pd.concat([merged, today_df], ignore_index=True) if not merged.empty else today_df
            merged.drop_duplicates(subset=['Date'], keep='last', inplace=True)
            print(f"   � Set today's close from live: €{live_price:.4f}")
        else:
            print("   ⚠️ Live price unavailable; skipping today's row update")

        # Finalize and save
        if not merged.empty:
            merged['Date'] = pd.to_datetime(merged['Date']).dt.date
            merged = merged[['Date','Open','High','Low','Close','Volume']]
            merged.sort_values('Date', inplace=True)
            merged.to_csv(csv_file, index=False)
            print(f"   ✅ Saved {csv_file} with {len(merged)} rows")
        else:
            print("   ❌ No data to save")

    print("\n✅ Yahoo advanced update completed")
    return True

def main():
    """Hauptfunktion"""
    print("🚀 YAHOO ADVANCED DATA UPDATE (daily to T-3, hourly backfill T-2/T-1, live today)")
    print("="*60)
    update_csv_files_with_yahoo_advanced()
    # Übersicht der letzten 5 Tage
    show_recent_overview(5)

if __name__ == "__main__":
    main()
