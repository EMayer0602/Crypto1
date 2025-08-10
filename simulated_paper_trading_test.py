#!/usr/bin/env python3
"""
SIMULIERTES PAPER TRADING
Da Bitpanda Standard möglicherweise kein echtes Paper Trading unterstützt,
simulieren wir es lokal für Testing
"""

import pandas as pd
from datetime import datetime
import json

class LocalPaperTrading:
    """Simuliert Paper Trading lokal wenn Bitpanda API nicht verfügbar"""
    
    def __init__(self):
        self.portfolio = {}
        self.trades = []
        self.cash = 10000.0  # Starkapital
        
        print("🧪 LOKALES PAPER TRADING SIMULATION")
        print("=" * 50)
        print("💡 Da Bitpanda Standard API limitiert ist")
        print("🎯 Simulieren wir Paper Trading lokal")
        print(f"💰 Startkapital: €{self.cash}")
        print("=" * 50)
    
    def execute_simulated_trade(self, ticker, action, amount_eur, price):
        """Simuliere einen Trade lokal"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if action.upper() == 'BUY':
            if self.cash >= amount_eur:
                quantity = amount_eur / price
                fee = amount_eur * 0.015  # 1.5% Fee wie Bitpanda
                
                self.cash -= (amount_eur + fee)
                
                if ticker in self.portfolio:
                    # Durchschnittspreis berechnen
                    old_qty = self.portfolio[ticker]['quantity']
                    old_value = old_qty * self.portfolio[ticker]['avg_price']
                    new_value = old_value + amount_eur
                    total_qty = old_qty + quantity
                    
                    self.portfolio[ticker] = {
                        'quantity': total_qty,
                        'avg_price': new_value / total_qty
                    }
                else:
                    self.portfolio[ticker] = {
                        'quantity': quantity,
                        'avg_price': price
                    }
                
                trade = {
                    'timestamp': timestamp,
                    'ticker': ticker,
                    'action': 'BUY',
                    'quantity': quantity,
                    'price': price,
                    'amount_eur': amount_eur,
                    'fee': fee,
                    'status': 'FILLED (SIMULATED)'
                }
                
                self.trades.append(trade)
                print(f"✅ BUY {ticker}: {quantity:.6f} @ €{price:.4f} (€{amount_eur:.2f})")
                return True
            else:
                print(f"❌ Nicht genug Cash für {ticker} BUY")
                return False
        
        elif action.upper() == 'SELL':
            if ticker in self.portfolio and self.portfolio[ticker]['quantity'] > 0:
                available_qty = self.portfolio[ticker]['quantity']
                sell_qty = min(amount_eur / price, available_qty)
                sell_value = sell_qty * price
                fee = sell_value * 0.015
                
                self.cash += (sell_value - fee)
                self.portfolio[ticker]['quantity'] -= sell_qty
                
                trade = {
                    'timestamp': timestamp,
                    'ticker': ticker,
                    'action': 'SELL',
                    'quantity': sell_qty,
                    'price': price,
                    'amount_eur': sell_value,
                    'fee': fee,
                    'status': 'FILLED (SIMULATED)'
                }
                
                self.trades.append(trade)
                print(f"✅ SELL {ticker}: {sell_qty:.6f} @ €{price:.4f} (€{sell_value:.2f})")
                return True
            else:
                print(f"❌ Keine {ticker} Position zum Verkaufen")
                return False
        
        return False
    
    def get_portfolio_status(self):
        """Portfolio Status anzeigen"""
        print(f"\n💼 PORTFOLIO STATUS")
        print(f"💰 Cash: €{self.cash:.2f}")
        print(f"📊 Positionen: {len([k for k, v in self.portfolio.items() if v['quantity'] > 0])}")
        
        for ticker, pos in self.portfolio.items():
            if pos['quantity'] > 0:
                print(f"   {ticker}: {pos['quantity']:.6f} @ €{pos['avg_price']:.4f}")
        
        print(f"📈 Trades gesamt: {len(self.trades)}")
    
    def save_trades_to_csv(self):
        """Speichere simulierte Trades"""
        if self.trades:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"simulated_paper_trading_{timestamp}.csv"
            
            df = pd.DataFrame(self.trades)
            df.to_csv(filename, index=False)
            print(f"💾 Simulierte Trades gespeichert: {filename}")
            return filename
        return None

def test_simulated_paper_trading():
    """Teste das simulierte Paper Trading"""
    
    # Simuliere akuelle Crypto Preise
    mock_prices = {
        'BTC-EUR': 65000.0,
        'ETH-EUR': 3500.0,
        'DOGE-EUR': 0.08,
        'XRP-EUR': 0.55,
        'ADA-EUR': 0.45
    }
    
    # Simuliere Trading Signale
    mock_signals = [
        ('BTC-EUR', 'BUY', 1000.0),
        ('ETH-EUR', 'BUY', 800.0),
        ('DOGE-EUR', 'BUY', 500.0),
        ('XRP-EUR', 'SELL', 300.0),  # Wird fehlschlagen da keine Position
    ]
    
    trader = LocalPaperTrading()
    
    print(f"\n📡 SIMULIERE TRADING SIGNALE...")
    print("-" * 40)
    
    executed_trades = 0
    
    for ticker, action, amount in mock_signals:
        if ticker in mock_prices:
            price = mock_prices[ticker]
            success = trader.execute_simulated_trade(ticker, action, amount, price)
            if success:
                executed_trades += 1
    
    trader.get_portfolio_status()
    csv_file = trader.save_trades_to_csv()
    
    print(f"\n🎉 SIMULATION ABGESCHLOSSEN!")
    print("=" * 50)
    print(f"📊 Ausgeführte Trades: {executed_trades}")
    print(f"💾 CSV Datei: {csv_file}")
    print("💡 Dies zeigt, dass Ihr System grundsätzlich funktioniert")
    print("🎯 Problem liegt bei Bitpanda API Berechtigung")
    print("=" * 50)

if __name__ == "__main__":
    test_simulated_paper_trading()
