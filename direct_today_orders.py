#!/usr/bin/env python3
"""
Direkte Heutige Orders - Minimal Script
=====================================

Holt direkt die heutigen Signale und bereitet Orders vor.
Minimal dependencies, maximum results.

"""

import os
import sys
import pandas as pd
import yfinance as yf
from datetime import datetime
import json

def main():
    print("🚀 DIREKTE HEUTIGE ORDERS VORBEREITUNG")
    print("="*50)
    print(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. AKTUELLE PREISE HOLEN
    print("🔄 Hole aktuelle Crypto-Preise...")
    
    cryptos = ['BTC-EUR', 'ETH-EUR', 'XRP-EUR', 'DOGE-EUR', 'SOL-EUR', 'LINK-EUR']
    prices = {}
    
    for crypto in cryptos:
        try:
            ticker = yf.Ticker(crypto)
            hist = ticker.history(period="1d", interval="1h")
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                prices[crypto] = current_price
                print(f"   ✅ {crypto}: €{current_price:.4f}")
            else:
                print(f"   ❌ {crypto}: Keine Daten")
                
        except Exception as e:
            print(f"   ❌ {crypto}: Fehler - {str(e)}")
    
    if not prices:
        print("❌ KEINE PREISE VERFÜGBAR - ABBRUCH")
        return
    
    print(f"\n✅ {len(prices)} Preise erfolgreich geladen")
    
    # 2. SUCHE NACH BESTEHENDEN SIGNALEN
    print("\n🔍 Suche nach bestehenden Signalen...")
    
    today = datetime.now().strftime('%Y%m%d')
    possible_files = [
        f'TODAY_ONLY_trades_{today}_*.csv',
        f'14_day_trades_REAL_{today}_*.csv',
        'portfolio_summary_*.csv',
        'bitpanda_paper_trading_*.csv'
    ]
    
    # Finde die neueste relevante Datei
    import glob
    latest_file = None
    latest_time = 0
    
    for pattern in possible_files:
        files = glob.glob(pattern)
        for file in files:
            if os.path.exists(file):
                file_time = os.path.getmtime(file)
                if file_time > latest_time:
                    latest_time = file_time
                    latest_file = file
    
    orders = []
    
    if latest_file:
        print(f"   📄 Gefunden: {latest_file}")
        
        try:
            df = pd.read_csv(latest_file)
            print(f"   📊 {len(df)} Zeilen in Datei")
            
            # Verschiedene Spalten-Namen versuchen
            date_col = None
            for col in ['Date', 'date', 'Datum', 'timestamp']:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col:
                today_str = datetime.now().strftime('%Y-%m-%d')
                today_trades = df[df[date_col].str.contains(today_str, na=False)]
                print(f"   📋 {len(today_trades)} heutige Einträge gefunden")
                
                # Extrahiere Orders aus heutigen Trades
                for _, trade in today_trades.iterrows():
                    # Verschiedene Spalten-Namen versuchen
                    ticker = None
                    for col in ['Ticker', 'Symbol', 'ticker', 'symbol']:
                        if col in trade and pd.notna(trade[col]):
                            ticker = str(trade[col]).upper()
                            break
                    
                    if not ticker:
                        continue
                    
                    # Action bestimmen
                    action = None
                    for col in ['Action', 'action', 'Type', 'type']:
                        if col in trade and pd.notna(trade[col]):
                            action = str(trade[col]).title()
                            break
                    
                    if not action:
                        continue
                    
                    # Quantity bestimmen
                    quantity = None
                    for col in ['Shares', 'Quantity', 'shares', 'quantity', 'Amount']:
                        if col in trade and pd.notna(trade[col]):
                            try:
                                quantity = abs(float(trade[col]))
                                break
                            except:
                                continue
                    
                    if not quantity or quantity == 0:
                        continue
                    
                    # Price bestimmen
                    price = None
                    for col in ['Price', 'price', 'Close', 'close']:
                        if col in trade and pd.notna(trade[col]):
                            try:
                                price = float(trade[col])
                                break
                            except:
                                continue
                    
                    pair = f"{ticker}-EUR"
                    current_price = prices.get(pair, price if price else 0)
                    
                    if current_price == 0:
                        continue
                    
                    order = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'pair': pair,
                        'ticker': ticker,
                        'action': action,
                        'quantity': quantity,
                        'price': price if price else current_price,
                        'current_market_price': current_price,
                        'order_value_eur': quantity * current_price,
                        'ready_to_send': True
                    }
                    
                    orders.append(order)
                    
                    action_emoji = "🟢" if action == 'Buy' else "🔴"
                    print(f"      {action_emoji} {action}: {quantity:.6f} {ticker} @ €{current_price:.4f} (Wert: €{order['order_value_eur']:.2f})")
            else:
                print("   ⚠️ Keine Datums-Spalte gefunden")
                
        except Exception as e:
            print(f"   ❌ Fehler beim Lesen der Datei: {str(e)}")
    
    # 3. FALLS KEINE SIGNALE GEFUNDEN, ERSTELLE TEST-SIGNALE
    if not orders:
        print("\n⚠️ Keine bestehenden Signale gefunden")
        print("🧪 Erstelle Test-Signale basierend auf aktuellen Preisen...")
        
        # Einfache Test-Logik: Kleine Buy-Orders für verfügbare Cryptos
        for pair, price in prices.items():
            ticker = pair.replace('-EUR', '')
            
            # Sehr kleine Test-Orders
            test_orders = [
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'pair': pair,
                    'ticker': ticker,
                    'action': 'Buy',
                    'quantity': 0.001 if ticker == 'BTC' else (0.01 if ticker == 'ETH' else 1),
                    'price': price * 0.999,  # 0.1% unter Marktpreis
                    'current_market_price': price,
                    'order_value_eur': (0.001 if ticker == 'BTC' else (0.01 if ticker == 'ETH' else 1)) * price,
                    'ready_to_send': True,
                    'note': 'Test-Signal - basierend auf aktuellen Preisen'
                }
            ]
            
            orders.extend(test_orders)
    
    # 4. ORDERS SPEICHERN UND ANZEIGEN
    if orders:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON speichern
        json_file = f'DIRECT_ORDERS_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'generation_time': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_orders': len(orders),
                'current_prices': prices,
                'orders': orders
            }, f, indent=2, default=str)
        
        # CSV speichern
        csv_file = f'DIRECT_ORDERS_{timestamp}.csv'
        df_orders = pd.DataFrame(orders)
        df_orders.to_csv(csv_file, index=False)
        
        print(f"\n💾 Orders gespeichert:")
        print(f"   📄 {json_file}")
        print(f"   📄 {csv_file}")
        
        # ZUSAMMENFASSUNG
        print(f"\n📊 ORDERS ZUSAMMENFASSUNG:")
        print("="*50)
        print(f"📋 Gesamt Orders: {len(orders)}")
        
        buy_orders = [o for o in orders if o['action'] == 'Buy']
        sell_orders = [o for o in orders if o['action'] == 'Sell']
        
        print(f"🟢 Kauf-Orders: {len(buy_orders)}")
        print(f"🔴 Verkauf-Orders: {len(sell_orders)}")
        
        total_buy_value = sum(o['order_value_eur'] for o in buy_orders)
        total_sell_value = sum(o['order_value_eur'] for o in sell_orders)
        
        print(f"💰 Gesamt Kaufwert: €{total_buy_value:.2f}")
        print(f"💰 Gesamt Verkaufswert: €{total_sell_value:.2f}")
        print(f"💰 Netto Cashflow: €{total_sell_value - total_buy_value:.2f}")
        
        print(f"\n📋 DETAIL ORDERS:")
        print("-"*50)
        
        for i, order in enumerate(orders, 1):
            action_emoji = "🟢" if order['action'] == 'Buy' else "🔴"
            print(f"{i:2d}. {action_emoji} {order['action'].upper()}: {order['quantity']:.6f} {order['ticker']}")
            print(f"     Preis: €{order['price']:.4f} | Markt: €{order['current_market_price']:.4f}")
            print(f"     Wert: €{order['order_value_eur']:.2f}")
            if 'note' in order:
                print(f"     Note: {order['note']}")
        
        print("="*50)
        print("✅ ALLE ORDERS VORBEREITET")
        print("📤 BEREIT ZUM SENDEN (wenn aktiviert)")
        print("❌ ORDERS NICHT GESENDET - NUR VORBEREITET")
        print("="*50)
        
        return True
    else:
        print("\n⚠️ KEINE ORDERS GENERIERT")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 ERFOLGREICH ABGESCHLOSSEN!")
        else:
            print("\n⚠️ KEINE ORDERS ERSTELLT")
    except Exception as e:
        print(f"\n❌ FEHLER: {str(e)}")
        import traceback
        traceback.print_exc()
