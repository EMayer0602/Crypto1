#!/usr/bin/env python3
"""
Optimierte CSV-Update-Logik:
- Täglich: Nur heute neu laden
- Gestern: Nur wenn artificial value
- Ältere Tage: Nur bei gaps
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from crypto_tickers import crypto_tickers

def check_csv_needs_update(symbol):
    """
    Prüft welche Daten für einen Ticker aktualisiert werden müssen
    
    Returns:
    - today_needed: Bool - heute braucht Update
    - yesterday_needed: Bool - gestern braucht Update (artificial)  
    - gaps_needed: List - Liste der gap-Daten die gefüllt werden müssen
    """
    
    csv_file = f"{symbol}_daily.csv"
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    print(f"\n🔍 Analysiere {symbol}...")
    
    # Defaults
    today_needed = True  # Heute immer updaten
    yesterday_needed = False
    gaps_needed = []
    
    if not os.path.exists(csv_file):
        print(f"   ❌ CSV nicht vorhanden - vollständiger Download nötig")
        return True, True, []  # Alles laden bei fehlendem CSV
        
    try:
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        # 1. Prüfe gestern auf artificial value
        yesterday_data = df[df['Date'] == yesterday]
        if not yesterday_data.empty:
            yesterday_volume = yesterday_data.iloc[0]['Volume']
            if yesterday_volume == -1000:
                yesterday_needed = True
                print(f"   📅 Gestern ({yesterday}) hat artificial value - Update nötig")
            else:
                print(f"   ✅ Gestern ({yesterday}) hat echte Daten")
        else:
            yesterday_needed = True  # Gestern fehlt komplett
            print(f"   ❌ Gestern ({yesterday}) fehlt - Update nötig")
            
        # 2. Prüfe auf Datenlücken (gaps) in letzten 30 Tagen
        thirty_days_ago = today - timedelta(days=30)
        recent_dates = pd.date_range(thirty_days_ago, today - timedelta(days=2), freq='D').date
        
        existing_dates = set(df['Date'])
        
        for check_date in recent_dates:
            if check_date not in existing_dates:
                gaps_needed.append(check_date)
                
        if gaps_needed:
            print(f"   📊 {len(gaps_needed)} Datenlücken gefunden: {gaps_needed[:3]}...")
        else:
            print(f"   ✅ Keine Datenlücken in letzten 30 Tagen")
            
    except Exception as e:
        print(f"   ❌ Fehler beim CSV-Check: {e}")
        return True, True, []  # Bei Fehlern alles laden
        
    print(f"   📋 Update nötig: Heute=Ja, Gestern={yesterday_needed}, Gaps={len(gaps_needed)}")
    return today_needed, yesterday_needed, gaps_needed

def smart_update_csv_files():
    """
    Intelligente CSV-Update-Logik:
    - Heute: Immer von Bitpanda
    - Gestern: Nur bei artificial values von CoinGecko  
    - Gaps: Nur fehlende Tage von Yahoo Finance
    """
    
    print("🧠 INTELLIGENTES CSV UPDATE")
    print("="*50)
    print("📅 Heute: Immer Bitpanda")
    print("🔄 Gestern: Nur bei artificial values (CoinGecko)")
    print("📊 Lücken: Nur fehlende Tage (Yahoo Finance)")
    print("="*50)
    
    from get_real_crypto_data import get_bitpanda_price, get_coingecko_yesterday_price
    import yfinance as yf
    
    for symbol in crypto_tickers.keys():
        print(f"\n🔄 Verarbeite {symbol}...")
        
        today_needed, yesterday_needed, gaps_needed = check_csv_needs_update(symbol)
        
        csv_file = f"{symbol}_daily.csv"
        
        # Lade bestehende CSV
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        else:
            print(f"   📥 Lade komplett neue CSV für {symbol}...")
            # Fallback auf vollständigen Download
            continue
            
        updates_made = False
        
        # 1. UPDATE HEUTE (Bitpanda)
        if today_needed:
            today = datetime.now().date()
            print(f"   📅 Update heute ({today}) mit Bitpanda...")
            
            try:
                bitpanda_price = get_bitpanda_price(symbol)
                if bitpanda_price:
                    # Entferne bestehenden Eintrag für heute falls vorhanden
                    df = df[df['Date'] != today]
                    
                    # Füge neuen Eintrag hinzu
                    new_row = pd.DataFrame([{
                        'Date': today,
                        'Open': bitpanda_price,
                        'High': bitpanda_price,
                        'Low': bitpanda_price,
                        'Close': bitpanda_price,
                        'Volume': 1000000  # Marker für Bitpanda
                    }])
                    
                    df = pd.concat([df, new_row], ignore_index=True)
                    updates_made = True
                    print(f"      ✅ Heute: €{bitpanda_price:.2f} (Bitpanda)")
                else:
                    print(f"      ❌ Bitpanda Fehler für {symbol}")
            except Exception as e:
                print(f"      ❌ Bitpanda Update Fehler: {e}")
        
        # 2. UPDATE GESTERN (CoinGecko) - nur bei artificial
        if yesterday_needed:
            yesterday = datetime.now().date() - timedelta(days=1)
            print(f"   📅 Update gestern ({yesterday}) mit CoinGecko...")
            
            try:
                coingecko_price = get_coingecko_yesterday_price(symbol)
                if coingecko_price:
                    # Ersetze artificial value für gestern
                    df.loc[df['Date'] == yesterday, 'Close'] = coingecko_price
                    df.loc[df['Date'] == yesterday, 'Open'] = coingecko_price
                    df.loc[df['Date'] == yesterday, 'High'] = coingecko_price
                    df.loc[df['Date'] == yesterday, 'Low'] = coingecko_price
                    df.loc[df['Date'] == yesterday, 'Volume'] = 2000000  # Marker für CoinGecko
                    
                    updates_made = True
                    print(f"      ✅ Gestern: €{coingecko_price:.2f} (CoinGecko ersetzt artificial)")
                else:
                    print(f"      ❌ CoinGecko Fehler für {symbol}")
            except Exception as e:
                print(f"      ❌ CoinGecko Update Fehler: {e}")
        
        # 3. FÜLLE GAPS (Yahoo Finance) - nur fehlende Tage
        if gaps_needed:
            print(f"   📊 Fülle {len(gaps_needed)} Datenlücken mit Yahoo Finance...")
            
            try:
                # Download nur für Gap-Zeitraum
                start_date = min(gaps_needed)
                end_date = max(gaps_needed) + timedelta(days=1)
                
                yf_symbol = symbol.replace('-EUR', '-EUR')
                ticker = yf.Ticker(yf_symbol)
                hist = ticker.history(start=start_date, end=end_date)
                
                if not hist.empty:
                    filled_count = 0
                    for gap_date in gaps_needed:
                        hist_date_data = hist[hist.index.date == gap_date]
                        if not hist_date_data.empty:
                            row = hist_date_data.iloc[0]
                            
                            new_row = pd.DataFrame([{
                                'Date': gap_date,
                                'Open': row['Open'],
                                'High': row['High'], 
                                'Low': row['Low'],
                                'Close': row['Close'],
                                'Volume': row['Volume']
                            }])
                            
                            df = pd.concat([df, new_row], ignore_index=True)
                            filled_count += 1
                            
                    if filled_count > 0:
                        updates_made = True
                        print(f"      ✅ {filled_count} Lücken gefüllt (Yahoo Finance)")
                    else:
                        print(f"      ⚠️ Keine Yahoo Daten für Lücken verfügbar")
                else:
                    print(f"      ❌ Yahoo Finance keine Daten für Gap-Zeitraum")
                    
            except Exception as e:
                print(f"      ❌ Yahoo Finance Gap-Fill Fehler: {e}")
        
        # Speichere falls Updates gemacht wurden
        if updates_made:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').drop_duplicates(subset=['Date'])
            df.to_csv(csv_file, index=False)
            print(f"   💾 {csv_file} gespeichert")
        else:
            print(f"   ℹ️ Keine Updates nötig für {symbol}")
            
    print(f"\n✅ INTELLIGENTES UPDATE ABGESCHLOSSEN")
    print("🎯 Nur notwendige Daten wurden aktualisiert")

if __name__ == "__main__":
    smart_update_csv_files()
