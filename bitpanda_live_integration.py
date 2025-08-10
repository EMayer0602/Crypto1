#!/usr/bin/env python3
"""
BITPANDA LIVE INTEGRATION - Mit echtem API
Sichere Integration für Paper Trading mit echten Bitpanda Daten
"""

import sys
import os
import json
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bitpanda_secure_api import get_api_key_safely, create_secure_api_url, BITPANDA_SECURE_CONFIG
from crypto_tickers import crypto_tickers

class BitpandaLiveIntegration:
    """
    Echte Bitpanda API Integration für Paper Trading
    """
    
    def __init__(self):
        self.api_key = get_api_key_safely()
        self.session = requests.Session()
        self.session.headers.update(BITPANDA_SECURE_CONFIG['headers'])
        
        # Paper Trading Portfolio
        self.paper_portfolio = {
            'EUR': 16000.0,
            'positions': {},
            'trade_history': []
        }
        
        print(f"🔗 Bitpanda Live Integration initialisiert")
        if self.api_key:
            print(f"✅ API-Key gefunden - Live-Daten verfügbar")
        else:
            print(f"⚠️ Kein API-Key - Fallback auf Yahoo Finance")
    
    def get_bitpanda_ticker_data(self) -> Optional[Dict]:
        """
        Hole echte Ticker-Daten von Bitpanda API
        """
        if not self.api_key:
            print("⚠️ Kein API-Key - verwende Fallback")
            return None
        
        try:
            url = create_secure_api_url('ticker', self.api_key)
            print(f"🌐 API Call: {url[:50]}...")
            
            response = self.session.get(
                url,
                timeout=BITPANDA_SECURE_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Bitpanda API: {len(data)} Ticker empfangen")
                return data
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ Bitpanda API Fehler: {e}")
            return None
    
    def get_current_prices_live(self) -> Dict[str, Dict[str, float]]:
        """
        Hole aktuelle Preise - Bitpanda + Yahoo Finance Fallback
        """
        print(f"\n📈 HOLE LIVE MARKTDATEN")
        print("-" * 40)
        
        prices = {}
        
        # Versuche zuerst Bitpanda API
        bitpanda_data = self.get_bitpanda_ticker_data()
        
        if bitpanda_data:
            # Parse Bitpanda Ticker-Daten
            print(f"🔍 Debug: Bitpanda Data Type: {type(bitpanda_data)}")
            if isinstance(bitpanda_data, list) and len(bitpanda_data) > 0:
                print(f"🔍 Debug: First ticker type: {type(bitpanda_data[0])}")
                print(f"🔍 Debug: First ticker: {str(bitpanda_data[0])[:200]}...")
            
            for ticker_name, config in crypto_tickers.items():
                symbol = config['symbol'].replace('-', '_')  # BTC-EUR -> BTC_EUR
                
                # Parse verschiedene API-Formate
                found_ticker = None
                
                if isinstance(bitpanda_data, list):
                    # Format: Liste von Ticker-Objekten
                    for ticker in bitpanda_data:
                        if isinstance(ticker, dict):
                            # Prüfe verschiedene Feld-Namen
                            ticker_symbol = (ticker.get('instrument_code') or 
                                           ticker.get('symbol') or 
                                           ticker.get('pair') or 
                                           ticker.get('name', ''))
                            
                            if ticker_symbol == symbol or ticker_symbol == ticker_name:
                                found_ticker = ticker
                                break
                        elif isinstance(ticker, str):
                            # Falls ticker nur String ist, überspringe
                            print(f"   ⚠️ Unerwartetes String-Format: {ticker[:50]}...")
                            continue
                
                elif isinstance(bitpanda_data, dict):
                    # Format: Dict mit Ticker als Keys
                    found_ticker = bitpanda_data.get(symbol) or bitpanda_data.get(ticker_name)
                
                if found_ticker and isinstance(found_ticker, dict):
                    # Extrahiere Preisdaten mit flexiblen Feldnamen
                    last = float(found_ticker.get('last') or found_ticker.get('price') or found_ticker.get('close') or 0)
                    bid = float(found_ticker.get('bid') or last * 0.999)
                    ask = float(found_ticker.get('ask') or last * 1.001) 
                    volume = float(found_ticker.get('volume') or found_ticker.get('vol') or 0)
                    change_24h = float(found_ticker.get('change') or found_ticker.get('change_24h') or 0)
                    
                    prices[ticker_name] = {
                        'last': last,
                        'bid': bid,
                        'ask': ask,
                        'volume': volume,
                        'change_24h': change_24h,
                        'source': 'bitpanda_live'
                    }
                    print(f"   🟢 {ticker_name}: €{last:.4f} (Bitpanda Live)")
                else:
                    print(f"   ⚠️ {ticker_name} nicht in Bitpanda Daten gefunden")
        
        # Yahoo Finance Fallback für fehlende Daten
        for ticker_name, config in crypto_tickers.items():
            if ticker_name not in prices:
                try:
                    import yfinance as yf
                    symbol = config['symbol']
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d", interval="1m")
                    
                    if not hist.empty:
                        last_price = hist['Close'].iloc[-1]
                        high_price = hist['High'].iloc[-1]
                        low_price = hist['Low'].iloc[-1]
                        volume = hist['Volume'].iloc[-1]
                        
                        prices[ticker_name] = {
                            'last': float(last_price),
                            'bid': float(last_price * 0.999),  # Geschätzter Bid
                            'ask': float(last_price * 1.001),  # Geschätzter Ask
                            'volume': float(volume),
                            'change_24h': 0.0,
                            'source': 'yahoo_fallback'
                        }
                        print(f"   🟡 {ticker_name}: €{prices[ticker_name]['last']:.4f} (Yahoo Fallback)")
                    
                except Exception as e:
                    print(f"   🔴 {ticker_name}: Fehler - {e}")
                    prices[ticker_name] = {
                        'last': 0.0, 'bid': 0.0, 'ask': 0.0, 'volume': 0.0,
                        'change_24h': 0.0, 'source': 'error'
                    }
        
        return prices
    
    def create_market_data_csv(self, prices: Dict) -> str:
        """
        Erstelle current_market_prices.csv für andere Scripts
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"current_market_prices.csv"
        
        market_data = []
        for ticker_name, price_data in prices.items():
            market_data.append({
                'symbol': ticker_name,
                'last': price_data['last'],
                'bid': price_data['bid'],
                'ask': price_data['ask'],
                'volume': price_data['volume'],
                'change_24h': price_data['change_24h'],
                'source': price_data['source'],
                'timestamp': datetime.now().isoformat()
            })
        
        df = pd.DataFrame(market_data)
        df.to_csv(filename, index=False)
        
        print(f"\n💾 Market Data gespeichert: {filename}")
        return filename
    
    def update_artificial_daily_data(self, prices: Dict) -> None:
        """
        Aktualisiere Daily CSVs mit Live-Daten (für add_artificial_daily.py)
        """
        print(f"\n🔄 AKTUALISIERE DAILY CSV-DATEIEN")
        print("-" * 40)
        
        today = datetime.now().date()
        
        for ticker_name, price_data in prices.items():
            if price_data['source'] == 'error':
                continue
                
            csv_file = f"{ticker_name}_daily.csv"
            
            if not os.path.exists(csv_file):
                print(f"   ⚠️ {csv_file} nicht gefunden")
                continue
            
            try:
                # Lade bestehende CSV
                df = pd.read_csv(csv_file)
                df['Date'] = pd.to_datetime(df['Date'])
                
                # Prüfe ob heute bereits existiert
                today_mask = df['Date'].dt.date == today
                
                last = price_data['last']
                bid = price_data['bid']
                ask = price_data['ask']
                
                if today_mask.any():
                    # Update bestehende Daten (falls artificial entry)
                    existing_row = df[today_mask]
                    if existing_row['Volume'].iloc[0] == -1000:  # Artificial marker
                        df.loc[today_mask, 'Open'] = last
                        df.loc[today_mask, 'High'] = ask
                        df.loc[today_mask, 'Low'] = bid
                        df.loc[today_mask, 'Close'] = last
                        df.loc[today_mask, 'Volume'] = -1000  # Keep artificial marker
                        action = "Updated artificial"
                    else:
                        action = "Skipped (real data exists)"
                else:
                    # Erstelle neuen Eintrag
                    new_row = pd.DataFrame({
                        'Date': [pd.Timestamp(today)],
                        'Open': [last],
                        'High': [ask],
                        'Low': [bid],
                        'Close': [last],
                        'Volume': [-1000]  # Artificial marker
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
                    df = df.sort_values('Date')
                    action = "Added new artificial"
                
                # Speichere aktualisierte CSV
                df.to_csv(csv_file, index=False)
                
                spread = ask - bid
                spread_pct = (spread / last * 100) if last > 0 else 0
                
                print(f"   ✅ {ticker_name}: {action}")
                print(f"      💰 Price: €{last:.4f} | Spread: {spread_pct:.3f}% | Source: {price_data['source']}")
                
            except Exception as e:
                print(f"   ❌ {ticker_name}: Fehler - {e}")
    
    def generate_live_report(self, prices: Dict) -> None:
        """
        Generiere Live-Market-Report
        """
        print(f"\n📊 LIVE MARKET REPORT")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_value = 0
        bitpanda_count = 0
        yahoo_count = 0
        
        print(f"\n💱 AKTUELLE PREISE:")
        for ticker_name, price_data in prices.items():
            config = crypto_tickers[ticker_name]
            allocation = config['initialCapitalLong']
            
            last = price_data['last']
            change = price_data['change_24h']
            source = price_data['source']
            
            if source == 'bitpanda_live':
                source_icon = "🟢"
                bitpanda_count += 1
            elif source == 'yahoo_fallback':
                source_icon = "🟡" 
                yahoo_count += 1
            else:
                source_icon = "🔴"
            
            total_value += allocation
            
            print(f"   {source_icon} {ticker_name:8} | €{last:>8.4f} | €{allocation:>6.0f} | {change:>+6.2f}% | {source}")
        
        print(f"\n📊 DATENQUELLEN:")
        print(f"   🟢 Bitpanda Live: {bitpanda_count}")
        print(f"   🟡 Yahoo Fallback: {yahoo_count}")
        print(f"   🔴 Fehler: {6 - bitpanda_count - yahoo_count}")
        
        print(f"\n💰 PORTFOLIO:")
        print(f"   📈 Gesamtallokation: €{total_value:,.2f}")
        print(f"   🎯 API Status: {'✅ Live Connected' if self.api_key else '⚠️ No API Key'}")

def run_live_integration():
    """
    Führe komplette Live-Integration aus
    """
    print("🚀 BITPANDA LIVE INTEGRATION GESTARTET")
    print("=" * 60)
    
    # Initialisiere Integration
    integration = BitpandaLiveIntegration()
    
    # Hole Live-Preise
    prices = integration.get_current_prices_live()
    
    # Erstelle Market Data CSV
    csv_file = integration.create_market_data_csv(prices)
    
    # Update Daily CSVs
    integration.update_artificial_daily_data(prices)
    
    # Generiere Report
    integration.generate_live_report(prices)
    
    print(f"\n✅ LIVE INTEGRATION ABGESCHLOSSEN")
    print(f"📁 Market Data: {csv_file}")
    print(f"🔄 Daily CSVs aktualisiert")
    print(f"📊 Bereit für add_artificial_daily.py oder Paper Trading")
    
    return integration

if __name__ == "__main__":
    integration = run_live_integration()
