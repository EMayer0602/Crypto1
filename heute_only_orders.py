#!/usr/bin/env python3
"""
NUR HEUTIGE ORDERS - 10. August 2025
===================================

Bereitet AUSSCHLIESSLICH Orders vom heutigen Tag vor.
KEINE 14-Tage Historie - NUR HEUTE!

"""

import os
import sys
import pandas as pd
import yfinance as yf
from datetime import datetime
import json

def main():
    TODAY = "2025-08-10"  # Heute - 10. August 2025
    NOW = datetime.now().strftime('%H:%M:%S')
    
    print("🚀 NUR HEUTIGE ORDERS VORBEREITUNG")
    print("="*50)
    print(f"📅 HEUTE: {TODAY}")
    print(f"⏰ ZEIT: {NOW}")
    print("❌ KEINE 14-Tage Historie!")
    print("✅ NUR ORDERS VOM HEUTIGEN TAG!")
    print()
    
    # 1. AKTUELLE PREISE HOLEN (für Validierung)
    print("🔄 Hole aktuelle Preise für Validierung...")
    
    cryptos = ['BTC-EUR', 'ETH-EUR', 'XRP-EUR', 'DOGE-EUR', 'SOL-EUR', 'LINK-EUR']
    current_prices = {}
    
    for crypto in cryptos:
        try:
            ticker = yf.Ticker(crypto)
            hist = ticker.history(period="1d", interval="1h")
            
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
                current_prices[crypto] = price
                print(f"   ✅ {crypto}: €{price:.4f}")
            else:
                print(f"   ❌ {crypto}: Keine aktuellen Daten")
                
        except Exception as e:
            print(f"   ❌ {crypto}: Fehler - {str(e)}")
    
    print(f"\n✅ {len(current_prices)} aktuelle Preise geladen")
    
    # 2. SUCHE NUR NACH HEUTIGEN SIGNALEN
    print(f"\n🔍 Suche nach Signalen vom {TODAY}...")
    
    # Mögliche Dateinamen für heute
    today_short = TODAY.replace('-', '')  # 20250810
    possible_files = [
        f'TODAY_ONLY_trades_{today_short}_*.csv',
        f'14_day_trades_REAL_{today_short}_*.csv',
        f'portfolio_summary_{today_short}_*.csv',
        f'bitpanda_paper_trading_{today_short}_*.csv'
    ]
    
    # Finde ALLE Dateien von heute
    import glob
    today_files = []
    
    for pattern in possible_files:
        files = glob.glob(pattern)
        for file in files:
            if os.path.exists(file):
                # Prüfe ob Datei wirklich von heute ist
                file_time = datetime.fromtimestamp(os.path.getmtime(file))
                if file_time.strftime('%Y-%m-%d') == TODAY:
                    today_files.append((file, os.path.getmtime(file)))
    
    # Sortiere nach Zeit (neueste zuerst)
    today_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"   📄 Gefundene Dateien von heute: {len(today_files)}")
    for file, _ in today_files:
        print(f"      - {file}")
    
    # 3. EXTRAHIERE NUR HEUTIGE ORDERS
    today_orders = []
    
    for file_path, _ in today_files:
        print(f"\n📋 Verarbeite: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            print(f"   📊 {len(df)} Zeilen in Datei")
            
            # Filtere STRIKT nur heutige Einträge
            date_columns = ['Date', 'date', 'Datum', 'timestamp', 'DateTime']
            date_col = None
            
            for col in date_columns:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col:
                # Sehr strikte Filterung: NUR genau heute
                mask = df[date_col].astype(str).str.contains(TODAY, case=False, na=False)
                today_entries = df[mask].copy()
                
                print(f"   📅 {len(today_entries)} Einträge von HEUTE ({TODAY})")
                
                if len(today_entries) == 0:
                    print("   ⚠️ KEINE EINTRÄGE VON HEUTE!")
                    continue
                
                # Extrahiere Orders
                for _, entry in today_entries.iterrows():
                    # Ticker bestimmen
                    ticker = None
                    for col in ['Ticker', 'Symbol', 'ticker', 'symbol']:
                        if col in entry and pd.notna(entry[col]):
                            ticker = str(entry[col]).upper().replace('-EUR', '')
                            break
                    
                    if not ticker:
                        print(f"   ⚠️ Kein Ticker gefunden in Zeile")
                        continue
                    
                    # Action bestimmen
                    action = None
                    for col in ['Action', 'action', 'Type', 'type', 'Side']:
                        if col in entry and pd.notna(entry[col]):
                            action_val = str(entry[col]).strip().title()
                            if action_val in ['Buy', 'Sell', 'BUY', 'SELL']:
                                action = action_val.title()
                                break
                    
                    if not action:
                        print(f"   ⚠️ Keine Action gefunden für {ticker}")
                        continue
                    
                    # Quantity bestimmen
                    quantity = None
                    for col in ['Shares', 'Quantity', 'shares', 'quantity', 'Amount', 'Volume']:
                        if col in entry and pd.notna(entry[col]):
                            try:
                                quantity = abs(float(entry[col]))
                                if quantity > 0:
                                    break
                            except:
                                continue
                    
                    if not quantity or quantity == 0:
                        print(f"   ⚠️ Keine gültige Quantity für {ticker}")
                        continue
                    
                    # Price bestimmen
                    price = None
                    for col in ['Price', 'price', 'Close', 'close', 'ExecutionPrice']:
                        if col in entry and pd.notna(entry[col]):
                            try:
                                price = float(entry[col])
                                if price > 0:
                                    break
                            except:
                                continue
                    
                    # Aktueller Marktpreis
                    pair = f"{ticker}-EUR"
                    market_price = current_prices.get(pair, price if price else 0)
                    
                    if market_price == 0:
                        print(f"   ⚠️ Kein Preis verfügbar für {ticker}")
                        continue
                    
                    # ORDER ERSTELLEN
                    order = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'date': TODAY,
                        'pair': pair,
                        'ticker': ticker,
                        'action': action,
                        'quantity': round(quantity, 8),
                        'signal_price': round(price, 6) if price else round(market_price, 6),
                        'current_market_price': round(market_price, 6),
                        'order_value_eur': round(quantity * market_price, 2),
                        'source_file': file_path,
                        'ready_to_send': True,
                        'heute_only': True  # Markierung für heutige Orders
                    }
                    
                    today_orders.append(order)
                    
                    action_emoji = "🟢" if action == 'Buy' else "🔴"
                    price_info = f"Signal: €{order['signal_price']:.4f}" if price else f"Markt: €{market_price:.4f}"
                    
                    print(f"   {action_emoji} {action}: {quantity:.6f} {ticker} | {price_info} | Wert: €{order['order_value_eur']:.2f}")
            
            else:
                print("   ❌ Keine Datums-Spalte gefunden")
                
        except Exception as e:
            print(f"   ❌ Fehler beim Verarbeiten: {str(e)}")
    
    # 4. FALLS KEINE HEUTIGEN SIGNALE GEFUNDEN
    if not today_orders:
        print(f"\n⚠️ KEINE SIGNALE VOM {TODAY} GEFUNDEN!")
        print("🔍 Prüfe ob Dateien von heute existieren...")
        
        # Liste alle CSV-Dateien auf, die heute erstellt wurden
        all_csv_files = glob.glob("*.csv")
        today_created_files = []
        
        for file in all_csv_files:
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(file))
                if file_time.strftime('%Y-%m-%d') == TODAY:
                    today_created_files.append(file)
            except:
                pass
        
        if today_created_files:
            print(f"\n📄 Dateien die heute erstellt wurden ({len(today_created_files)}):")
            for file in today_created_files:
                print(f"   - {file}")
            print("\n💡 Möglicherweise sind Signale in anderen Spalten oder Formaten")
        else:
            print(f"\n❌ KEINE DATEIEN VON HEUTE GEFUNDEN!")
            print("💡 Strategie muss zuerst ausgeführt werden für heutige Signale")
        
        return False
    
    # 5. ORDERS SPEICHERN
    if today_orders:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON mit allen Details
        json_file = f'HEUTE_ONLY_ORDERS_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'generation_time': datetime.now().isoformat(),
                'target_date': TODAY,
                'total_orders': len(today_orders),
                'current_prices': current_prices,
                'orders': today_orders,
                'filter': f'STRICT - Only {TODAY}',
                'no_14_day_history': True
            }, f, indent=2, default=str)
        
        # CSV für einfache Bearbeitung
        csv_file = f'HEUTE_ONLY_ORDERS_{timestamp}.csv'
        df_orders = pd.DataFrame(today_orders)
        df_orders.to_csv(csv_file, index=False)
        
        print(f"\n💾 HEUTIGE ORDERS GESPEICHERT:")
        print(f"   📄 {json_file}")
        print(f"   📄 {csv_file}")
        
        # ZUSAMMENFASSUNG NUR FÜR HEUTE
        print(f"\n📊 NUR HEUTIGE ORDERS ({TODAY}):")
        print("="*50)
        print(f"📋 Gesamt Orders: {len(today_orders)}")
        
        buy_orders = [o for o in today_orders if o['action'] == 'Buy']
        sell_orders = [o for o in today_orders if o['action'] == 'Sell']
        
        print(f"🟢 Kauf-Orders: {len(buy_orders)}")
        print(f"🔴 Verkauf-Orders: {len(sell_orders)}")
        
        total_buy_value = sum(o['order_value_eur'] for o in buy_orders)
        total_sell_value = sum(o['order_value_eur'] for o in sell_orders)
        
        print(f"💰 Kaufwert heute: €{total_buy_value:.2f}")
        print(f"💰 Verkaufswert heute: €{total_sell_value:.2f}")
        print(f"💰 Netto Cashflow: €{total_sell_value - total_buy_value:.2f}")
        
        print(f"\n📋 DETAIL - ALLE {len(today_orders)} ORDERS VOM {TODAY}:")
        print("-"*50)
        
        for i, order in enumerate(today_orders, 1):
            action_emoji = "🟢" if order['action'] == 'Buy' else "🔴"
            print(f"{i:2d}. {action_emoji} {order['action'].upper()}: {order['quantity']:.6f} {order['ticker']}")
            print(f"     Signal: €{order['signal_price']:.4f} | Markt: €{order['current_market_price']:.4f}")
            print(f"     Wert: €{order['order_value_eur']:.2f} | Quelle: {os.path.basename(order['source_file'])}")
        
        print("="*50)
        print(f"✅ ALLE ORDERS VOM {TODAY} VORBEREITET")
        print("📤 BEREIT ZUM SENDEN")
        print("❌ NICHT GESENDET - NUR VORBEREITET")
        print("📅 KEINE 14-TAGE HISTORIE ENTHALTEN!")
        print("="*50)
        
        return True
    
    return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 HEUTE-ONLY ORDERS ERFOLGREICH VORBEREITET!")
        else:
            print(f"\n⚠️ KEINE ORDERS FÜR HEUTE (2025-08-10) GEFUNDEN")
            print("💡 Bitte zuerst Strategie für heute ausführen")
    except Exception as e:
        print(f"\n❌ FEHLER: {str(e)}")
        import traceback
        traceback.print_exc()
