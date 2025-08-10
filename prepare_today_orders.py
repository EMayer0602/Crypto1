#!/usr/bin/env python3
"""
Heutige Orders Vorbereiten - Direkt aus Strategie
==============================================

Führt die echte Strategie aus und bereitet alle heutigen Orders vor.
OHNE Filter - alle Signale von heute werden vorbereitet.

Created: August 10, 2025
"""

import os
import sys
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import json
import traceback

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import our modules
try:
    from config import *
    from crypto_backtesting_module import optimize_parameters_with_fixed_data
    from add_artificial_daily import add_artificial_daily
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

class TodayOrderPreparation:
    """Bereitet heutige Orders direkt aus der Strategie vor"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.current_prices = {}
        self.strategy_results = {}
        self.today_orders = []
        
        print("🚀 Heutige Orders Vorbereitung gestartet")
        print(f"📅 Datum: {self.today}")
        print(f"⏰ Zeit: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
    
    def get_current_prices(self):
        """Holt aktuelle Marktpreise"""
        print("🔄 Lade aktuelle Marktpreise...")
        
        crypto_pairs = ['BTC-EUR', 'ETH-EUR', 'XRP-EUR', 'DOGE-EUR', 'SOL-EUR', 'LINK-EUR']
        
        for pair in crypto_pairs:
            try:
                ticker = yf.Ticker(pair)
                hist = ticker.history(period="2d", interval="1d")
                
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    previous_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                    
                    self.current_prices[pair] = {
                        'current': current_price,
                        'previous': previous_price,
                        'change': ((current_price - previous_price) / previous_price * 100) if previous_price != 0 else 0,
                        'timestamp': datetime.now()
                    }
                    
                    print(f"   ✅ {pair}: €{current_price:.4f} ({self.current_prices[pair]['change']:+.2f}%)")
                else:
                    print(f"   ❌ {pair}: Keine Daten verfügbar")
                    
            except Exception as e:
                print(f"   ❌ {pair}: Fehler - {str(e)}")
        
        print(f"📊 {len(self.current_prices)} Preise geladen")
    
    def update_csv_with_today_data(self, pair: str):
        """Aktualisiert CSV-Datei mit heutigen Daten"""
        csv_file = f"{pair}_daily.csv"
        
        if not os.path.exists(csv_file):
            print(f"   ⚠️ {csv_file} nicht gefunden")
            return None
        
        try:
            # Lade bestehende Daten
            df = pd.read_csv(csv_file)
            
            # Prüfe ob heute schon existiert
            if self.today in df['Date'].values:
                print(f"   ℹ️ {pair}: Heutige Daten bereits vorhanden")
                return df
            
            # Füge heutige Daten hinzu
            if pair in self.current_prices:
                price_data = self.current_prices[pair]
                new_row = {
                    'Date': self.today,
                    'Open': price_data['current'],  # Vereinfacht
                    'High': price_data['current'] * 1.02,  # +2% für High estimate
                    'Low': price_data['current'] * 0.98,   # -2% für Low estimate
                    'Close': price_data['current'],
                    'Volume': 1000000  # Dummy Volume
                }
                
                # Füge neue Zeile hinzu
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                print(f"   ✅ {pair}: Heutige Daten hinzugefügt")
                
                return df
            else:
                print(f"   ❌ {pair}: Keine aktuellen Preisdaten")
                return df
                
        except Exception as e:
            print(f"   ❌ {pair}: CSV Update Fehler - {str(e)}")
            return None
    
    def run_strategy_for_pair(self, pair: str):
        """Führt die Strategie für ein Paar aus"""
        print(f"🧠 Führe Strategie aus für {pair}...")
        
        try:
            # Update CSV mit heutigen Daten
            updated_df = self.update_csv_with_today_data(pair)
            if updated_df is None:
                return None
            
            # Führe Strategie-Optimierung aus
            ticker_symbol = pair.replace('-EUR', '')
            
            print(f"   🔍 Optimiere Parameter für {ticker_symbol}...")
            
            # Führe die echte Strategie aus
            result = optimize_parameters_with_fixed_data(
                ticker=ticker_symbol,
                data=updated_df,
                target_period=14,  # 14 Tage Optimierungsperiode
                silent=True
            )
            
            if result and 'trades' in result:
                trades_df = result['trades']
                
                # Filtere nur heutige Trades
                today_trades = trades_df[trades_df['Date'] == self.today].copy()
                
                if not today_trades.empty:
                    print(f"   📋 {len(today_trades)} Signale für heute gefunden")
                    
                    # Füge zusätzliche Informationen hinzu
                    today_trades['Pair'] = pair
                    today_trades['CurrentPrice'] = self.current_prices[pair]['current']
                    today_trades['PriceChange'] = self.current_prices[pair]['change']
                    today_trades['OrderValue'] = today_trades['Shares'].abs() * today_trades['Price']
                    today_trades['Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Log jedes Signal
                    for _, trade in today_trades.iterrows():
                        action_emoji = "🟢" if trade['Action'] == 'Buy' else "🔴"
                        print(f"     {action_emoji} {trade['Action']}: {trade['Shares']:.6f} @ €{trade['Price']:.4f} (Wert: €{trade['OrderValue']:.2f})")
                    
                    self.strategy_results[pair] = {
                        'trades': today_trades,
                        'best_params': result.get('best_params', {}),
                        'total_return': result.get('total_return', 0),
                        'success': True
                    }
                    
                    return today_trades
                else:
                    print(f"   ℹ️ Keine Signale für heute")
                    self.strategy_results[pair] = {
                        'trades': pd.DataFrame(),
                        'success': True,
                        'message': 'Keine Signale heute'
                    }
                    return pd.DataFrame()
            else:
                print(f"   ❌ Strategie-Ausführung fehlgeschlagen")
                self.strategy_results[pair] = {
                    'success': False,
                    'error': 'Keine Ergebnisse von Strategie'
                }
                return None
                
        except Exception as e:
            print(f"   ❌ Strategie-Fehler für {pair}: {str(e)}")
            self.strategy_results[pair] = {
                'success': False,
                'error': str(e)
            }
            return None
    
    def prepare_all_orders(self):
        """Bereitet alle heutigen Orders vor"""
        print("\n🔄 Bereite alle heutigen Orders vor...")
        
        crypto_pairs = list(self.current_prices.keys())
        
        for pair in crypto_pairs:
            today_trades = self.run_strategy_for_pair(pair)
            
            if today_trades is not None and not today_trades.empty:
                # Konvertiere zu Order-Format
                for _, trade in today_trades.iterrows():
                    order = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'pair': pair,
                        'ticker': pair.replace('-EUR', ''),
                        'action': trade['Action'],
                        'quantity': abs(float(trade['Shares'])),
                        'price': float(trade['Price']),
                        'current_market_price': float(trade['CurrentPrice']),
                        'order_value_eur': abs(float(trade['Shares'])) * float(trade['Price']),
                        'market_value_eur': abs(float(trade['Shares'])) * float(trade['CurrentPrice']),
                        'price_deviation_percent': abs(float(trade['Price']) - float(trade['CurrentPrice'])) / float(trade['CurrentPrice']) * 100,
                        'date': self.today,
                        'strategy_params': self.strategy_results[pair].get('best_params', {}),
                        'ready_to_send': True
                    }
                    
                    self.today_orders.append(order)
        
        print(f"\n📝 {len(self.today_orders)} Orders vorbereitet")
    
    def save_orders_to_file(self):
        """Speichert Orders in Datei"""
        if not self.today_orders:
            print("ℹ️ Keine Orders zu speichern")
            return
        
        # JSON Format
        json_filename = f'TODAY_ORDERS_{self.timestamp}.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'generation_time': datetime.now().isoformat(),
                'date': self.today,
                'total_orders': len(self.today_orders),
                'orders': self.today_orders,
                'market_prices': {pair: data['current'] for pair, data in self.current_prices.items()},
                'strategy_results_summary': {
                    pair: {
                        'success': data.get('success', False),
                        'trades_count': len(data.get('trades', [])),
                        'best_params': data.get('best_params', {})
                    } for pair, data in self.strategy_results.items()
                }
            }, f, indent=2, default=str)
        
        print(f"💾 Orders gespeichert: {json_filename}")
        
        # CSV Format für einfache Ansicht
        if self.today_orders:
            csv_filename = f'TODAY_ORDERS_{self.timestamp}.csv'
            orders_df = pd.DataFrame(self.today_orders)
            orders_df.to_csv(csv_filename, index=False)
            print(f"💾 Orders CSV: {csv_filename}")
    
    def display_order_summary(self):
        """Zeigt Zusammenfassung der Orders"""
        print("\n" + "="*80)
        print("📋 HEUTIGE ORDERS ZUSAMMENFASSUNG")
        print("="*80)
        
        if not self.today_orders:
            print("ℹ️ Keine Orders für heute generiert")
            return
        
        # Gruppiere nach Aktion
        buy_orders = [o for o in self.today_orders if o['action'] == 'Buy']
        sell_orders = [o for o in self.today_orders if o['action'] == 'Sell']
        
        print(f"📊 Gesamt Orders: {len(self.today_orders)}")
        print(f"🟢 Kauf-Orders: {len(buy_orders)}")
        print(f"🔴 Verkauf-Orders: {len(sell_orders)}")
        
        # Gesamtwerte
        total_buy_value = sum(o['market_value_eur'] for o in buy_orders)
        total_sell_value = sum(o['market_value_eur'] for o in sell_orders)
        
        print(f"💰 Gesamt Kaufwert: €{total_buy_value:.2f}")
        print(f"💰 Gesamt Verkaufswert: €{total_sell_value:.2f}")
        print(f"💰 Netto Cashflow: €{total_sell_value - total_buy_value:.2f}")
        
        print("\n📋 DETAIL ORDERS:")
        print("-"*80)
        
        for i, order in enumerate(self.today_orders, 1):
            action_emoji = "🟢" if order['action'] == 'Buy' else "🔴"
            deviation = order['price_deviation_percent']
            deviation_warning = " ⚠️" if deviation > 5 else ""
            
            print(f"{i:2d}. {action_emoji} {order['action'].upper()} {order['quantity']:.6f} {order['ticker']}")
            print(f"     Preis: €{order['price']:.4f} | Markt: €{order['current_market_price']:.4f} | Abweichung: {deviation:.2f}%{deviation_warning}")
            print(f"     Wert: €{order['market_value_eur']:.2f}")
        
        print("="*80)
        print("✅ ALLE ORDERS VORBEREITET - BEREIT ZUM SENDEN")
        print("❌ ORDERS NICHT GESENDET (nur vorbereitet)")
        print("="*80)
    
    def run(self):
        """Hauptausführung"""
        try:
            # 1. Hole aktuelle Preise
            self.get_current_prices()
            
            if not self.current_prices:
                print("❌ Keine Marktpreise verfügbar - Abbruch")
                return False
            
            # 2. Bereite alle Orders vor
            self.prepare_all_orders()
            
            # 3. Speichere Orders
            self.save_orders_to_file()
            
            # 4. Zeige Zusammenfassung
            self.display_order_summary()
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler bei Order-Vorbereitung: {str(e)}")
            traceback.print_exc()
            return False

def main():
    """Hauptfunktion"""
    print("🚀 Heutige Orders aus Strategie vorbereiten")
    print("📋 OHNE Filter - alle Signale werden vorbereitet")
    print("❌ Orders werden NICHT gesendet, nur vorbereitet")
    
    order_prep = TodayOrderPreparation()
    
    try:
        success = order_prep.run()
        
        if success:
            print("\n🎉 ORDER-VORBEREITUNG ERFOLGREICH!")
            print("📁 Dateien erstellt mit allen heutigen Orders")
            print("📤 Orders sind bereit zum Senden (wenn aktiviert)")
        else:
            print("\n❌ ORDER-VORBEREITUNG FEHLGESCHLAGEN")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⏹️ Abgebrochen durch Benutzer")
        return False
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
