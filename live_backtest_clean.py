#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LIVE BACKTEST REPORT - Mit automatischem Gap-Filling und Bitpanda Updates
"""

import os
import sys
import webbrowser
from datetime import datetime, timedelta
import pandas as pd
import requests
import glob

# Import unserer Module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from crypto_backtesting_module import run_backtest
import crypto_tickers

def get_bitpanda_price(symbol):
    """Hole aktuellen Preis von Bitpanda API"""
    try:
        # Bitpanda Pro API für aktuellen Preis
        bitpanda_symbol = symbol.replace('-', '')
        
        # Versuche verschiedene Bitpanda API Endpoints
        urls = [
            f"https://api.bitpanda.com/v1/ticker/{bitpanda_symbol}",
            f"https://api.exchange.bitpanda.com/public/v1/market-ticker/{symbol}",
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'last' in data:
                        return float(data['last'])
                    elif 'last_price' in data:
                        return float(data['last_price'])
                    elif 'price' in data:
                        return float(data['price'])
                    
            except Exception as e:
                continue
        
        print(f"Bitpanda API nicht verfügbar für {symbol}")
        return None
        
    except Exception as e:
        print(f"Bitpanda API Fehler für {symbol}: {e}")
        return None

def get_coingecko_historical_data_to_csv(symbol, days=7):
    """Hole CoinGecko Daten und speichere direkt in CSV (einmal täglich)"""
    try:
        csv_file = f"{symbol}_daily.csv"
        
        if not os.path.exists(csv_file):
            print(f"  ❌ CSV {csv_file} nicht gefunden")
            return False
            
        # Lade aktuelle CSV
        df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
        today = pd.Timestamp.now().normalize()
        yesterday = today - timedelta(days=1)
        
        # Prüfe ob wir heute schon CoinGecko Daten geholt haben
        # Marker: Wenn es artificial values (Volume=-1000) VOR heute gibt, dann CoinGecko ausführen
        artificial_before_today = df[(df['Volume'] == -1000) & (df.index < today)]
        
        if len(artificial_before_today) == 0:
            print(f"  ✅ {symbol}: Keine artificial values vor heute - CoinGecko bereits ausgeführt")
            return True
        else:
            print(f"  🔄 {symbol}: {len(artificial_before_today)} artificial values vor heute gefunden - führe CoinGecko aus")
        
        # CoinGecko Mapping
        coingecko_mapping = {
            "BTC-EUR": "bitcoin",
            "ETH-EUR": "ethereum", 
            "DOGE-EUR": "dogecoin",
            "SOL-EUR": "solana",
            "LINK-EUR": "chainlink",
            "XRP-EUR": "ripple"
        }
        
        coin_id = coingecko_mapping.get(symbol)
        if not coin_id:
            print(f"  ❌ CoinGecko mapping für {symbol} nicht gefunden")
            return False
        
        print(f"  🔄 Hole CoinGecko Daten für {symbol} (einmal täglich)...")
        
        # CoinGecko API für historische Daten
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'eur',
            'days': str(days),
            'interval': 'daily'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            updated = False
            
            # Parse und aktualisiere CSV direkt
            for price_entry in data['prices']:
                timestamp = pd.Timestamp(price_entry[0], unit='ms').normalize()
                price = price_entry[1]
                
                # Nur Daten VOR heute berücksichtigen (heute muss artificial bleiben!)
                if timestamp >= (today - timedelta(days=7)) and timestamp < today:
                    
                    if timestamp in df.index:
                        # Vorhandenen Eintrag nur aktualisieren wenn er artificial ist (Volume = -1000)
                        if df.loc[timestamp, 'Volume'] == -1000:
                            df.loc[timestamp, 'Open'] = price
                            df.loc[timestamp, 'High'] = price
                            df.loc[timestamp, 'Low'] = price
                            df.loc[timestamp, 'Close'] = price
                            df.loc[timestamp, 'Volume'] = 10000000  # Echter Marker
                            print(f"    ✅ {timestamp.date()}: artificial ersetzt mit CoinGecko: {price:.4f}")
                            updated = True
                        else:
                            print(f"    ⏭️ {timestamp.date()}: bereits echt (Volume != -1000)")
                    else:
                        # Neuen Eintrag erstellen für fehlende Tage VOR heute
                        df.loc[timestamp] = [price, price, price, price, 10000000]
                        print(f"    ➕ {timestamp.date()}: neue CoinGecko Daten: {price:.4f}")
                        updated = True
                elif timestamp == today:
                    print(f"    ⏭️ {timestamp.date()}: HEUTE - bleibt artificial (nicht durch CoinGecko ersetzen)")
            
            # CSV speichern wenn aktualisiert
            if updated:
                df = df.sort_index()
                df.to_csv(csv_file)
                print(f"  💾 {symbol}: CSV mit CoinGecko Daten aktualisiert!")
            else:
                print(f"  ✅ {symbol}: Keine CoinGecko Updates erforderlich")
            
            return True
        
        elif response.status_code == 429:
            print(f"  ⚠️ CoinGecko Rate Limit für {symbol}")
            return False
        else:
            print(f"  ❌ CoinGecko API Error für {symbol}: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"  ❌ CoinGecko Fehler für {symbol}: {e}")
        return False

def get_yahoo_finance_data(symbol, days=7):
    """Hole Yahoo Finance Daten für historische Werte (vor gestern)"""
    try:
        import yfinance as yf
        
        print(f"  🔄 Hole Yahoo Finance Daten für {symbol}...")
        
        # Lade Yahoo Finance Daten
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"{days}d")
        
        if len(hist) > 0:
            historical_data = {}
            for date, row in hist.iterrows():
                timestamp = pd.Timestamp(date).normalize()
                
                historical_data[timestamp] = {
                    'Open': row['Open'],
                    'High': row['High'],
                    'Low': row['Low'],
                    'Close': row['Close'],
                    'Volume': row['Volume'] if row['Volume'] > 0 else 1000000
                }
            
            print(f"  ✅ Yahoo Finance: {len(historical_data)} Datenpunkte für {symbol}")
            return historical_data
        else:
            print(f"  ❌ Yahoo Finance: Keine Daten für {symbol}")
            return None
        
    except Exception as e:
        print(f"  ❌ Yahoo Finance Fehler für {symbol}: {e}")
        return None

def update_csv_with_current_price(csv_file):
    """3-Tier System: YF für historisch, CoinGecko für gestern, Bitpanda für heute"""
    try:
        df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
        symbol = os.path.basename(csv_file).replace('_daily.csv', '')
        today = pd.Timestamp.now().normalize()
        yesterday = today - timedelta(days=1)
        
        print(f"  📊 3-Tier Update für {symbol}:")
        print(f"      • Historisch: Yahoo Finance")
        print(f"      • Gestern: CoinGecko") 
        print(f"      • Heute: Bitpanda (realtime)")
        
        updated = False
        
        # TIER 1: YAHOO FINANCE für historische Daten (VOR GESTERN)
        historical_artificial = df[(df['Volume'] == -1000) & (df.index < yesterday)]
        
        if len(historical_artificial) > 0:
            print(f"  🔄 TIER 1: {len(historical_artificial)} historische artificial values → Yahoo Finance")
            
            yf_data = get_yahoo_finance_data(symbol, days=14)
            yf_updated = False
            
            if yf_data:
                for date in historical_artificial.index:
                    if date in yf_data:
                        yf_entry = yf_data[date]
                        df.loc[date, 'Open'] = yf_entry['Open']
                        df.loc[date, 'High'] = yf_entry['High']
                        df.loc[date, 'Low'] = yf_entry['Low']
                        df.loc[date, 'Close'] = yf_entry['Close']
                        df.loc[date, 'Volume'] = yf_entry['Volume']
                        print(f"    ✅ {date.date()}: Yahoo Finance: {yf_entry['Close']:.4f}")
                        updated = True
                        yf_updated = True
                    else:
                        print(f"    ⏭️ {date.date()}: nicht in Yahoo Finance verfügbar")
            
            # Fallback: CoinGecko für historische Daten die YF nicht hat
            remaining_artificial = df[(df['Volume'] == -1000) & (df.index < yesterday)]
            
            if len(remaining_artificial) > 0:
                print(f"  🔄 TIER 1 FALLBACK: {len(remaining_artificial)} Daten → CoinGecko (YF unvollständig)")
                
                coingecko_success = get_coingecko_historical_data_to_csv(symbol, days=7)
                
                if coingecko_success:
                    # CSV neu laden nach CoinGecko Update
                    df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
                    print(f"    ✅ CoinGecko Fallback erfolgreich")
                    updated = True
                else:
                    print(f"    ⚠️ CoinGecko Fallback nicht verfügbar")
            
            if not yf_updated and not coingecko_success:
                print(f"  ⚠️ Yahoo Finance nicht verfügbar - behalte artificial values")
        
        # TIER 2: COINGECKO für GESTERN
        if yesterday in df.index and df.loc[yesterday, 'Volume'] == -1000:
            print(f"  🔄 TIER 2: GESTERN artificial value → CoinGecko")
            
            coingecko_success = get_coingecko_historical_data_to_csv(symbol, days=3)
            
            if coingecko_success:
                # CSV neu laden nach CoinGecko Update
                df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
                print(f"    ✅ GESTERN: CoinGecko Update erfolgreich")
                updated = True
            else:
                print(f"    ⚠️ GESTERN: CoinGecko nicht verfügbar")
        elif yesterday in df.index:
            print(f"  ✅ TIER 2: GESTERN bereits echt (Volume != -1000)")
        else:
            print(f"  ⏭️ TIER 2: GESTERN nicht in CSV vorhanden")
        
        # TIER 3: BITPANDA für HEUTE (immer ausführen!)
        print(f"  🔄 TIER 3: HEUTE → Bitpanda realtime (bei jedem Run)")
        
        current_price = get_bitpanda_price(symbol)
        
        if current_price:
            if today in df.index:
                # Update bestehenden heutigen Eintrag - IMMER auf artificial setzen!
                df.loc[today, 'Open'] = current_price
                df.loc[today, 'High'] = current_price
                df.loc[today, 'Low'] = current_price
                df.loc[today, 'Close'] = current_price
                df.loc[today, 'Volume'] = -1000  # IMMER artificial für heute
                print(f"    ✅ HEUTE aktualisiert: {current_price:.4f} (artificial)")
                updated = True
            else:
                # Erstelle neuen heutigen Eintrag - IMMER artificial
                df.loc[today] = [current_price, current_price, current_price, current_price, -1000]
                print(f"    ➕ HEUTE erstellt: {current_price:.4f} (artificial)")
                updated = True
        else:
            print(f"    ⚠️ Bitpanda nicht verfügbar")
            
            # Fallback: Wenn kein Bitpanda verfügbar, trotzdem auf artificial setzen
            if today in df.index and df.loc[today, 'Volume'] != -1000:
                df.loc[today, 'Volume'] = -1000  # Force artificial für heute
                print(f"    🔄 HEUTE auf artificial gesetzt (Fallback)")
                updated = True
        
        # Speichere wenn aktualisiert
        if updated:
            df = df.sort_index()  # Nach Datum sortieren
            df.to_csv(csv_file)
            print(f"  💾 {symbol}: 3-Tier Update abgeschlossen!")
        else:
            print(f"  ✅ {symbol}: Keine Updates erforderlich")
        
        return updated
        
    except Exception as e:
        print(f"❌ Fehler beim 3-Tier Update von {csv_file}: {e}")
        return False
        
        # 3. HEUTE: Bitpanda für aktuellen Preis
        current_price = get_bitpanda_price(symbol)
        
        if current_price:
            if today in df.index:
                # Update bestehenden heutigen Eintrag
                df.loc[today, 'Open'] = current_price
                df.loc[today, 'High'] = current_price
                df.loc[today, 'Low'] = current_price
                df.loc[today, 'Close'] = current_price
                df.loc[today, 'Volume'] = -1000  # Bleibt artificial für heute
                print(f"  {symbol}: HEUTE ({today.date()}) artificial aktualisiert mit Bitpanda: {current_price:.4f}")
                updated = True
            else:
                # Erstelle neuen heutigen Eintrag
                df.loc[today] = [current_price, current_price, current_price, current_price, -1000]
                print(f"  {symbol}: HEUTE ({today.date()}) artificial erstellt mit Bitpanda: {current_price:.4f}")
                updated = True
        else:
            print(f"  {symbol}: Bitpanda Preis für heute nicht verfügbar")
        
        # Speichere wenn aktualisiert
        if updated:
            df = df.sort_index()  # Nach Datum sortieren
            df.to_csv(csv_file)
            print(f"  {symbol}: CSV aktualisiert!")
        else:
            print(f"  {symbol}: Keine Updates erforderlich")
        
        return updated
        
    except Exception as e:
        print(f"Fehler beim Update von {csv_file}: {e}")
        return False

def fill_csv_gaps_quick(csv_file):
    """Schnelles Gap-Filling für Live-Backtest"""
    try:
        df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
        symbol = os.path.basename(csv_file).replace('_daily.csv', '')
        
        # Zeitbereich: Start bis gestern
        start_date = df.index.min()
        yesterday = pd.Timestamp.now().normalize() - timedelta(days=1)
        
        # Vollständiger Datumsbereich
        full_date_range = pd.date_range(start=start_date, end=yesterday, freq='D')
        missing_dates = full_date_range.difference(df.index)
        
        if len(missing_dates) > 0:
            print(f"  {symbol}: Fülle {len(missing_dates)} Lücken...")
            
            for missing_date in missing_dates:
                # Finde besten Fill-Preis
                available_before = df.index[df.index < missing_date]
                if len(available_before) > 0:
                    fill_price = df.loc[available_before.max(), 'Close']
                else:
                    available_after = df.index[df.index > missing_date]
                    if len(available_after) > 0:
                        fill_price = df.loc[available_after.min(), 'Close']
                    else:
                        fill_price = 1.0
                
                # Artificial entry
                df.loc[missing_date] = {
                    'Open': fill_price,
                    'High': fill_price,
                    'Low': fill_price,
                    'Close': fill_price,
                    'Volume': -1000
                }
            
            df = df.sort_index()
            df.to_csv(csv_file)
            return True
        else:
            print(f"  {symbol}: Keine Lücken gefunden")
            return False
            
    except Exception as e:
        print(f"  Fehler bei {csv_file}: {e}")
        return False

def update_all_csvs():
    """Aktualisiere alle CSV-Dateien mit Gap-Filling und heutigen Preisen"""
    print("CSV UPDATE - Gap-Filling und heutige Preise")
    print("=" * 60)
    
    # Finde alle CSV-Dateien
    csv_files = glob.glob("*-EUR_daily.csv")
    print(f"Gefunden: {len(csv_files)} CSV-Dateien")
    
    for csv_file in csv_files:
        # 1. Gap-Filling
        fill_csv_gaps_quick(csv_file)
        
        # 2. Heutigen Preis aktualisieren
        update_csv_with_current_price(csv_file)
    
    print("CSV Update abgeschlossen!")
    print()

def run_live_backtests():
    """Führt LIVE Backtests für alle Tickers aus und sammelt Results"""
    
    print("LIVE BACKTEST REPORT - Fuehre aktuelle Backtests durch...")
    print("=" * 80)
    
    tickers = list(crypto_tickers.crypto_tickers.keys())
    all_results = []
    summary_data = []
    all_trades_14_days = []
    
    for ticker in tickers:
        print(f"\nLIVE BACKTEST fuer {ticker}...")
        
        # Hole ticker-spezifische Config
        ticker_config = crypto_tickers.crypto_tickers.get(ticker, {})
        trade_on = ticker_config.get('trade_on', 'Close')
        
        print(f"   Trade-Ausfuehrung: {trade_on}")
        print(f"   Initial Capital: {ticker_config.get('initialCapitalLong', 10000)} EUR")
        print(f"   Order Round Factor: {ticker_config.get('order_round_factor', 0.01)}")
        
        # Erstelle vollständige Config
        config = {
            'initial_capital': ticker_config.get('initialCapitalLong', 10000),
            'commission_rate': 0.0018,
            'trade_on': trade_on,
            'order_round_factor': ticker_config.get('order_round_factor', 0.01),
            'timeframe': 'daily',
            'csv_path': './',
            'min_commission': 1.0
        }
        
        try:
            # Führe Backtest aus
            result = run_backtest(ticker, config)
            
            if result and result.get('success', False):
                all_results.append(result)
                
                # Sammle weekly trades
                weekly_trades = result.get('weekly_trades_data', [])
                actual_trades = []
                
                for trade in weekly_trades:
                    action = trade.get('Action', '')
                    if action in ['BUY', 'SELL']:
                        trade['ticker'] = ticker
                        trade['config'] = config
                        actual_trades.append(trade)
                        all_trades_14_days.append(trade)
                
                # Extrahiere ECHTE Total Return aus Trade Statistics!
                initial_capital = ticker_config.get('initialCapitalLong', 10000)
                trade_stats = result.get('trade_statistics', {})
                
                # Hole Total Return direkt aus den Trade Statistics
                total_return_str = trade_stats.get('📊 Total Return', '0.00%')
                if isinstance(total_return_str, str) and '%' in total_return_str:
                    # Parse "1234.56%" -> 1234.56
                    total_return_percent = float(total_return_str.replace('%', ''))
                else:
                    # Fallback: Berechne aus Total PnL / Initial Capital * 100
                    total_pnl_str = trade_stats.get('💰 Total PnL', '€0.00')
                    if isinstance(total_pnl_str, str) and '€' in total_pnl_str:
                        total_pnl = float(total_pnl_str.replace('€', '').replace(',', ''))
                        total_return_percent = (total_pnl / initial_capital) * 100
                    else:
                        total_return_percent = result.get('optimal_pnl', 0)
                
                summary_data.append({
                    'Symbol': ticker,
                    'Past_Window': result.get('optimal_past_window'),
                    'Trade_Window': result.get('optimal_trade_window'),
                    'Optimal_PnL': total_return_percent,  # ECHTE Total Return aus Trade Stats!
                    'Trades_2W': result.get('weekly_trades_count', 0),
                    'Order_Round_Factor': config['order_round_factor'],
                    'Initial_Capital': initial_capital,
                    'Total_Return_Raw': total_return_str
                })
                
                print(f"   Optimal: p={result.get('optimal_past_window')}, tw={result.get('optimal_trade_window')}")
                print(f"   Initial Capital: {initial_capital} EUR")
                print(f"   Total Return: {total_return_str} (= {total_return_percent:.2f}%)")
                print(f"   Trades (2 Wochen): {result.get('weekly_trades_count', 0)}")
                print(f"   Total Trades gefunden: {len(actual_trades)}")
                
            else:
                print(f"   Backtest fehlgeschlagen")
                
        except Exception as e:
            print(f"   Fehler: {e}")
    
    print(f"\nGESAMT: {len(all_trades_14_days)} Trades der letzten 14 Tage gefunden!")
    return all_results, summary_data, all_trades_14_days

def main():
    """Main function"""
    try:
        print("LIVE BACKTEST REPORT mit automatischem CSV-Update")
        print("=" * 80)
        
        # 1. ERST: Aktualisiere alle CSV-Dateien (Gap-Filling + heutige Preise)
        update_all_csvs()
        
        print("Fuehre AKTUELLE Backtests durch und erstelle SOFORT einen Report!")
        print("=" * 80)
        
        # 2. Sammle ALLE Trades der letzten 14 Tage aus Extended/Matched Trades
        all_results, summary_data, all_trades_14_days = run_live_backtests()
        
        if not all_results:
            print("Keine Backtest-Results erhalten!")
            return None
        
        print(f"\n{len(all_results)} Ticker erfolgreich analysiert!")
        
        # SAMMLE ALLE TRADES DER LETZTEN 14 TAGE mit SHARES
        print("\nSAMMLE TRADES DER LETZTEN 14 TAGE...")
        print("=" * 60)
        
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=14)
        
        recent_trades = []
        
        for result in all_results:
            ticker = result.get('symbol', 'Unknown')
            
            # 1. Extended Trades der letzten 14 Tage
            ext_trades = result.get('weekly_trades_data', [])
            print(f"{ticker}: {len(ext_trades)} Extended Trades gefunden")
            
            for trade in ext_trades:
                if trade.get('Action') in ['BUY', 'SELL']:
                    recent_trades.append({
                        'Ticker': ticker.replace('-EUR', ''),
                        'Date': trade.get('Long Date detected', 'N/A'),
                        'Action': trade.get('Action', 'N/A').upper(),
                        'Price': trade.get('Level Close', 0),
                        'Shares': trade.get('shares', 'N/A'),
                        'Type': 'Extended',
                        'Round_Factor': result.get('config', {}).get('order_round_factor', 'N/A')
                    })
            
            # 2. Matched Trades der letzten 14 Tage  
            matched_trades = result.get('matched_trades')
            if matched_trades is not None and not matched_trades.empty:
                print(f"{ticker}: {len(matched_trades)} Matched Trades gefunden")
                
                for _, trade in matched_trades.iterrows():
                    # Check if Entry oder Exit in den letzten 14 Tagen
                    entry_date = pd.to_datetime(trade.get('Entry Date', '1900-01-01'))
                    exit_date = pd.to_datetime(trade.get('Exit Date', '1900-01-01'))
                    
                    if entry_date >= cutoff_date:
                        recent_trades.append({
                            'Ticker': ticker.replace('-EUR', ''),
                            'Date': trade.get('Entry Date', 'N/A'),
                            'Action': 'BUY',
                            'Price': trade.get('Entry Price', 0),
                            'Shares': trade.get('Shares', 'N/A'),
                            'Type': 'Matched Entry',
                            'PnL': 'N/A',
                            'Status': trade.get('Status', 'N/A')
                        })
                    
                    if exit_date >= cutoff_date and trade.get('Status') == 'CLOSED':
                        recent_trades.append({
                            'Ticker': ticker.replace('-EUR', ''),
                            'Date': trade.get('Exit Date', 'N/A'),
                            'Action': 'SELL',
                            'Price': trade.get('Exit Price', 0),
                            'Shares': trade.get('Shares', 'N/A'),
                            'Type': 'Matched Exit',
                            'PnL': trade.get('Net PnL', 'N/A'),
                            'Status': trade.get('Status', 'N/A')
                        })
        
        print(f"\nGESAMT: {len(recent_trades)} Trades der letzten 14 Tage gesammelt!")
        print(f"Davon Extended: {len([t for t in recent_trades if t['Type'] == 'Extended'])}")
        print(f"Davon Matched: {len([t for t in recent_trades if 'Matched' in t['Type']])}")
        
        # EINFACHE TICKER PnL AUSGABE (OHNE EMOJIS!) - KORREKTE WERTE
        print()
        print("TICKER PnL UEBERSICHT (KORREKTE WERTE):")
        print("-" * 40)
        for result in summary_data:
            ticker = result['Symbol'].replace('-EUR', '').upper()
            optimal_pnl = result['Optimal_PnL']
            
            if ticker and optimal_pnl is not None:
                print(f"{ticker:<8} {optimal_pnl:>6.0f}%")
        print()
        
        print("HTML-Report wird erstellt...")
        
        # Hier könnte der HTML-Report erstellt werden
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LIVE_backtest_report_{timestamp}.html"
        
        # Einfacher HTML-Report
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Live Backtest Report {timestamp}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Live Backtest Report - {timestamp}</h1>
    <h2>Ticker PnL Übersicht</h2>
    <table>
        <tr><th>Ticker</th><th>PnL (%)</th><th>Past Window</th><th>Trade Window</th><th>Trades (2W)</th></tr>
"""
        
        for result in summary_data:
            ticker = result['Symbol'].replace('-EUR', '')
            html_content += f"""
        <tr>
            <td>{ticker}</td>
            <td>{result['Optimal_PnL']:.1f}%</td>
            <td>{result['Past_Window']}</td>
            <td>{result['Trade_Window']}</td>
            <td>{result['Trades_2W']}</td>
        </tr>"""
        
        html_content += """
    </table>
    <h2>Trades der letzten 14 Tage</h2>
    <table>
        <tr><th>Ticker</th><th>Datum</th><th>Aktion</th><th>Preis (€)</th><th>Shares</th><th>Typ</th><th>PnL</th><th>Status</th></tr>
"""
        
        # Sortiere Trades nach Datum
        recent_trades_sorted = sorted(recent_trades, key=lambda x: x.get('Date', ''), reverse=True)
        
        for trade in recent_trades_sorted:
            shares_display = trade.get('Shares', 'N/A')
            if isinstance(shares_display, float):
                shares_display = f"{shares_display:.0f}"
            
            pnl_display = trade.get('PnL', 'N/A')
            if isinstance(pnl_display, float):
                pnl_display = f"{pnl_display:.2f}€"
            
            html_content += f"""
        <tr>
            <td>{trade.get('Ticker', 'N/A')}</td>
            <td>{trade.get('Date', 'N/A')}</td>
            <td>{trade.get('Action', 'N/A')}</td>
            <td>{trade.get('Price', 0):.4f}</td>
            <td>{shares_display}</td>
            <td>{trade.get('Type', 'N/A')}</td>
            <td>{pnl_display}</td>
            <td>{trade.get('Status', 'N/A')}</td>
        </tr>"""
        
        html_content += f"""
    </table>
    <p><strong>Anzahl Trades (14 Tage):</strong> {len(recent_trades)}</p>
    <p><strong>Extended Trades:</strong> {len([t for t in recent_trades if t['Type'] == 'Extended'])}</p>
    <p><strong>Matched Trades:</strong> {len([t for t in recent_trades if 'Matched' in t['Type']])}</p>
</body>
</html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"LIVE BACKTEST REPORT erstellt: {filename}")
        print(f"Pfad: {os.path.abspath(filename)}")
        
        # Öffne Report im Browser
        try:
            file_url = f"file:///{os.path.abspath(filename).replace(os.sep, '/')}"
            print(f"Oeffne im Browser: {file_url}")
            webbrowser.open(file_url)
            print("Browser geoeffnet!")
        except Exception as e:
            print(f"Browser-Fehler: {e}")
        
        print(f"HTML-Report erfolgreich erstellt und gespeichert!")
        
        return filename
        
    except Exception as e:
        print(f"Fehler: {e}")
        return None

if __name__ == "__main__":
    main()
