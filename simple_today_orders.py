#!/usr/bin/env python3
"""
Einfache Heutige Orders - Direkt aus bestehender Strategie
========================================================

Nutzt Ihre bestehenden Module um heutige Orders zu generieren.
Basiert auf live_backtest_WORKING.py Logik.

"""

import os
import sys
import pandas as pd
import yfinance as yf
from datetime import datetime
import json

# Füge aktuelles Verzeichnis zum Python-Pfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def get_today_prices():
    """Holt heutige Preise für alle Cryptos"""
    print("🔄 Lade aktuelle Preise...")
    
    crypto_pairs = ['BTC-EUR', 'ETH-EUR', 'XRP-EUR', 'DOGE-EUR', 'SOL-EUR', 'LINK-EUR']
    prices = {}
    
    for pair in crypto_pairs:
        try:
            ticker = yf.Ticker(pair)
            hist = ticker.history(period="1d", interval="5m")
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                prices[pair] = current_price
                print(f"   ✅ {pair}: €{current_price:.4f}")
            else:
                print(f"   ❌ {pair}: Keine Daten")
                
        except Exception as e:
            print(f"   ❌ {pair}: Fehler - {str(e)}")
    
    return prices

def update_csv_files(prices):
    """Aktualisiert CSV-Dateien mit heutigen Preisen"""
    print("\n🔄 Aktualisiere CSV-Dateien...")
    
    today = datetime.now().strftime('%Y-%m-%d')
    updated_files = []
    
    for pair, price in prices.items():
        csv_file = f"{pair}_daily.csv"
        
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                
                # Prüfe ob heute schon existiert
                if today not in df['Date'].values:
                    # Füge heutige Daten hinzu
                    new_row = {
                        'Date': today,
                        'Open': price,
                        'High': price * 1.01,  # +1% für High
                        'Low': price * 0.99,   # -1% für Low
                        'Close': price,
                        'Volume': 1000000
                    }
                    
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(csv_file, index=False)
                    print(f"   ✅ {pair}: CSV aktualisiert")
                    updated_files.append(csv_file)
                else:
                    print(f"   ℹ️ {pair}: Heute bereits vorhanden")
                    updated_files.append(csv_file)
                    
            except Exception as e:
                print(f"   ❌ {pair}: CSV Fehler - {str(e)}")
        else:
            print(f"   ⚠️ {pair}: CSV nicht gefunden - {csv_file}")
    
    return updated_files

def run_strategy_and_get_trades():
    """Führt die bestehende Strategie aus"""
    print("\n🧠 Führe Strategie aus...")
    
    try:
        # Versuche das bestehende live_backtest_WORKING.py zu importieren und ausführen
        if os.path.exists('live_backtest_WORKING.py'):
            print("   📋 Nutze live_backtest_WORKING.py...")
            
            # Führe das Script aus und fange die Ausgabe ab
            import subprocess
            result = subprocess.run([sys.executable, 'live_backtest_WORKING.py'], 
                                  capture_output=True, text=True, cwd=current_dir)
            
            if result.returncode == 0:
                print("   ✅ Strategie erfolgreich ausgeführt")
                
                # Suche nach der neuesten Trades-Datei
                today = datetime.now().strftime('%Y%m%d')
                potential_files = [
                    f'TODAY_ONLY_trades_{today}_*.csv',
                    f'14_day_trades_REAL_{today}_*.csv',
                    'portfolio_summary_*.csv'
                ]
                
                # Finde die neueste Datei
                import glob
                latest_file = None
                latest_time = 0
                
                for pattern in potential_files:
                    files = glob.glob(pattern)
                    for file in files:
                        file_time = os.path.getmtime(file)
                        if file_time > latest_time:
                            latest_time = file_time
                            latest_file = file
                
                if latest_file:
                    print(f"   📄 Neueste Trades-Datei: {latest_file}")
                    return latest_file
                else:
                    print("   ⚠️ Keine Trades-Datei gefunden")
                    return None
            else:
                print(f"   ❌ Strategie-Fehler: {result.stderr}")
                return None
        else:
            print("   ❌ live_backtest_WORKING.py nicht gefunden")
            return None
            
    except Exception as e:
        print(f"   ❌ Strategie-Ausführung fehlgeschlagen: {str(e)}")
        return None

def extract_today_orders(trades_file, current_prices):
    """Extrahiert heutige Orders aus Trades-Datei"""
    print(f"\n📋 Extrahiere heutige Orders aus {trades_file}...")
    
    if not trades_file or not os.path.exists(trades_file):
        print("   ❌ Keine Trades-Datei verfügbar")
        return []
    
    try:
        df = pd.read_csv(trades_file)
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Filtere heutige Trades
        if 'Date' in df.columns:
            today_trades = df[df['Date'] == today].copy()
        else:
            # Falls keine Date-Spalte, nimm die neuesten
            today_trades = df.tail(10).copy()  # Letzte 10 als heutige
        
        print(f"   📊 {len(today_trades)} heutige Trades gefunden")
        
        orders = []
        for _, trade in today_trades.iterrows():
            # Bestimme das Paar
            ticker = trade.get('Ticker', trade.get('Symbol', 'BTC'))
            pair = f"{ticker}-EUR"
            
            # Hole aktuellen Preis
            current_price = current_prices.get(pair, trade.get('Price', 0))
            
            order = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'pair': pair,
                'ticker': ticker,
                'action': trade.get('Action', 'Buy'),
                'quantity': abs(float(trade.get('Shares', trade.get('Quantity', 0)))),
                'price': float(trade.get('Price', current_price)),
                'current_market_price': current_price,
                'order_value_eur': abs(float(trade.get('Shares', 0))) * current_price,
                'date': today,
                'ready_to_send': True
            }
            
            orders.append(order)
            
            action_emoji = "🟢" if order['action'] == 'Buy' else "🔴"
            print(f"   {action_emoji} {order['action']}: {order['quantity']:.6f} {ticker} @ €{order['price']:.4f} (Markt: €{current_price:.4f})")
        
        return orders
        
    except Exception as e:
        print(f"   ❌ Order-Extraktion fehlgeschlagen: {str(e)}")
        return []

def save_prepared_orders(orders):
    """Speichert vorbereitete Orders"""
    if not orders:
        print("\nℹ️ Keine Orders zu speichern")
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # JSON speichern
    json_file = f'PREPARED_ORDERS_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'generation_time': datetime.now().isoformat(),
            'total_orders': len(orders),
            'orders': orders
        }, f, indent=2, default=str)
    
    # CSV speichern
    csv_file = f'PREPARED_ORDERS_{timestamp}.csv'
    df = pd.DataFrame(orders)
    df.to_csv(csv_file, index=False)
    
    print(f"\n💾 Orders gespeichert:")
    print(f"   📄 JSON: {json_file}")
    print(f"   📄 CSV: {csv_file}")
    
    # Zusammenfassung anzeigen
    print(f"\n📊 ORDERS ZUSAMMENFASSUNG:")
    print(f"   📋 Gesamt Orders: {len(orders)}")
    
    buy_orders = [o for o in orders if o['action'] == 'Buy']
    sell_orders = [o for o in orders if o['action'] == 'Sell']
    
    print(f"   🟢 Kauf-Orders: {len(buy_orders)}")
    print(f"   🔴 Verkauf-Orders: {len(sell_orders)}")
    
    total_buy_value = sum(o['order_value_eur'] for o in buy_orders)
    total_sell_value = sum(o['order_value_eur'] for o in sell_orders)
    
    print(f"   💰 Gesamt Kaufwert: €{total_buy_value:.2f}")
    print(f"   💰 Gesamt Verkaufswert: €{total_sell_value:.2f}")
    print(f"   💰 Netto Cashflow: €{total_sell_value - total_buy_value:.2f}")

def main():
    """Hauptfunktion"""
    print("🚀 Einfache Heutige Orders Vorbereitung")
    print("📋 Nutzt bestehende Strategie-Module")
    print(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d')}")
    print("="*60)
    
    try:
        # 1. Hole aktuelle Preise
        current_prices = get_today_prices()
        if not current_prices:
            print("❌ Keine Preise verfügbar")
            return False
        
        # 2. Aktualisiere CSV-Dateien
        updated_files = update_csv_files(current_prices)
        
        # 3. Führe Strategie aus
        trades_file = run_strategy_and_get_trades()
        
        # 4. Extrahiere heutige Orders
        orders = extract_today_orders(trades_file, current_prices)
        
        # 5. Speichere Orders
        save_prepared_orders(orders)
        
        if orders:
            print("\n🎉 ORDERS ERFOLGREICH VORBEREITET!")
            print("📤 Orders sind bereit zum Senden (wenn aktiviert)")
            print("❌ Orders wurden NICHT gesendet - nur vorbereitet")
        else:
            print("\n⚠️ Keine Orders für heute generiert")
        
        return len(orders) > 0
        
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
