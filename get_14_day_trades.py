#!/usr/bin/env python3
"""
14 TAGE TRADE REPORT - Extrahiert echte Trades aus Backtest-Ergebnissen
"""

import sys
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import glob

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest

def get_real_bitpanda_price(symbol):
    """
    Versucht den aktuellen Preis zu holen (Yahoo Finance als Proxy für Bitpanda)
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return hist['Close'].iloc[-1]
    except Exception as e:
        print(f"   ⚠️ Fehler beim Abrufen des Preises für {symbol}: {e}")
    return 0.0

def extract_trades_from_backtest_results():
    """
    Extrahiert echte Trades aus den Backtest-Ergebnissen der letzten 14 Tage
    """
    print("\n🔍 EXTRAHIERE ECHTE TRADES AUS BACKTEST-ERGEBNISSEN")
    print("="*60)
    
    cutoff_date = datetime.now() - timedelta(days=14)
    all_trades = []
    
    # Header inkl. Action (BUY/SELL)
    header = "Date;Ticker;Quantity;Price;Order Type;Limit Price;Open/Close;Action;Realtime Price Bitpanda"
    
    for ticker_name, config in crypto_tickers.items():
        symbol = config.get('symbol', ticker_name)
        
        print(f"\n📊 Verarbeite {ticker_name} ({symbol})...")
        
        try:
            # Führe Backtest für diesen Ticker aus
            backtest_result = run_backtest(symbol, config)
            
            if not backtest_result:
                print(f"   ⚠️ Kein Backtest-Ergebnis für {ticker_name}")
                continue
                
            # Extrahiere matched_trades
            matched_trades = backtest_result.get('matched_trades')
            if matched_trades is None or matched_trades.empty:
                print(f"   ⚠️ Keine Trades für {ticker_name}")
                continue
            
            # Hole aktuellen Preis
            current_price = get_real_bitpanda_price(symbol)
            
            # Verarbeite jeden Trade
            for _, trade in matched_trades.iterrows():
                entry_date_str = str(trade.get('Entry Date', ''))
                exit_date_str = str(trade.get('Exit Date', ''))
                
                # Parse Daten
                try:
                    if 'T' in entry_date_str:
                        entry_date = datetime.fromisoformat(entry_date_str.replace('T', ' '))
                    else:
                        entry_date = pd.to_datetime(entry_date_str)
                        
                    if pd.notna(exit_date_str) and exit_date_str != 'nan' and exit_date_str != '':
                        if 'T' in exit_date_str:
                            exit_date = datetime.fromisoformat(exit_date_str.replace('T', ' '))
                        else:
                            exit_date = pd.to_datetime(exit_date_str)
                    else:
                        exit_date = None
                        
                except Exception as e:
                    print(f"     ⚠️ Datum-Parse-Fehler: {e}")
                    continue
                
                # Entry Trade (BUY) hinzufügen wenn in den letzten 14 Tagen
                if entry_date >= cutoff_date:
                    entry_price = float(trade.get('Entry Price', 0))
                    quantity = float(trade.get('Quantity', 0))
                    
                    trade_entry = {
                        'date': entry_date.strftime('%Y-%m-%d'),
                        'ticker': ticker_name,
                        'quantity': quantity,
                        'price': entry_price,
                        'order_type': 'Limit',
                        'limit_price': entry_price * 0.999,  # Leicht unter Entry Price
                        'open_close': 'Open',
                        'action': 'BUY',
                        'realtime_price': current_price
                    }
                    all_trades.append(trade_entry)
                    print(f"     📈 BUY: {entry_date.date()}, {quantity:.6f} @ €{entry_price:.4f}")
                
                # Exit Trade (SELL) hinzufügen wenn in den letzten 14 Tagen
                if exit_date and exit_date >= cutoff_date:
                    exit_price = float(trade.get('Exit Price', 0))
                    quantity = float(trade.get('Quantity', 0))
                    
                    trade_exit = {
                        'date': exit_date.strftime('%Y-%m-%d'),
                        'ticker': ticker_name,
                        'quantity': quantity,
                        'price': exit_price,
                        'order_type': 'Limit',
                        'limit_price': exit_price * 1.001,  # Leicht über Exit Price
                        'open_close': 'Close',
                        'action': 'SELL',
                        'realtime_price': current_price
                    }
                    all_trades.append(trade_exit)
                    print(f"     💰 SELL: {exit_date.date()}, {quantity:.6f} @ €{exit_price:.4f}")
                    
        except Exception as e:
            print(f"   ❌ Fehler bei {ticker_name}: {e}")
    
    # Sortiere Trades nach Datum (neueste zuerst)
    all_trades.sort(key=lambda x: x['date'], reverse=True)
    
    # Ausgabe des Reports
    print(f"\n📊 ===== 14-TAGE TRADES REPORT (ECHTE DATEN) =====")
    print(f"📅 Zeitraum: {cutoff_date.date()} bis {datetime.now().date()}")
    print(f"🔢 Trades gefunden: {len(all_trades)}")
    print(f"\n{header}")
    print("-" * 150)
    
    for trade in all_trades:
        line = f"{trade['date']};{trade['ticker']};{trade['quantity']:.6f};{trade['price']:.4f};{trade['order_type']};{trade['limit_price']:.4f};{trade['open_close']};{trade.get('action','')};{trade['realtime_price']:.4f}"
        print(line)
    
    # Speichere als CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"14_day_trades_REAL_{timestamp}.csv"
    
    if all_trades:
        df = pd.DataFrame(all_trades)
        # Spaltenreihenfolge erzwingen
        cols = ['date','ticker','quantity','price','order_type','limit_price','open_close','action','realtime_price']
        for c in cols:
            if c not in df.columns:
                df[c] = ''
        df = df[cols]
        df.columns = ['Date', 'Ticker', 'Quantity', 'Price', 'Order Type', 'Limit Price', 'Open/Close', 'Action', 'Realtime Price Bitpanda']
        df.to_csv(csv_filename, sep=';', index=False)
        print(f"\n💾 Report gespeichert als: {csv_filename}")
        
        # Zusätzliche Statistiken
        buy_trades = [t for t in all_trades if t['open_close'] == 'Open']
        sell_trades = [t for t in all_trades if t['open_close'] == 'Close']
        
        print(f"\n📊 STATISTIKEN:")
        print(f"   🟢 BUY Trades:  {len(buy_trades)}")
        print(f"   🔴 SELL Trades: {len(sell_trades)}")
        print(f"   📈 Ticker mit Aktivität: {len(set(t['ticker'] for t in all_trades))}")
        
    else:
        print(f"\n⚠️ Keine Trades in den letzten 14 Tagen gefunden")
    
    return all_trades

if __name__ == "__main__":
    print("🚀 STARTE 14-TAGE TRADE EXTRAKTION...")
    
    trades = extract_trades_from_backtest_results()
    
    print(f"\n✅ FERTIG! {len(trades)} Trades extrahiert und gespeichert.")
