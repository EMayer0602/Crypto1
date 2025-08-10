#!/usr/bin/env python3
"""
Quick Trading Test - Schneller Test ohne Order-Übermittlung
=========================================================

Schneller Test aller wichtigen Trading-Funktionen:
- Live-Preise abrufen
- Signale prüfen  
- Orders vorbereiten
- Risiko checken
- Portfolio simulieren

Created: August 10, 2025
"""

import os
import sys
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime
import logging

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

class QuickTradingTest:
    """Schneller Trading-Test"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_prices = {}
        self.prepared_orders = []
        
        # Setup simple logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.logger = logging.getLogger('QuickTest')
        
        print("🚀 Quick Trading Test gestartet")
        print(f"⏰ Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
    
    def test_market_data(self) -> bool:
        """Test 1: Live-Marktdaten"""
        print("🔄 Test 1: Live-Marktdaten abrufen...")
        
        crypto_pairs = ['BTC-EUR', 'ETH-EUR', 'XRP-EUR', 'DOGE-EUR', 'SOL-EUR']
        success_count = 0
        
        for pair in crypto_pairs:
            try:
                ticker = yf.Ticker(pair)
                hist = ticker.history(period="1d", interval="5m")
                
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
                    self.current_prices[pair] = price
                    print(f"   ✅ {pair}: €{price:.4f}")
                    success_count += 1
                else:
                    print(f"   ❌ {pair}: Keine Daten")
                    
            except Exception as e:
                print(f"   ❌ {pair}: Fehler - {str(e)}")
        
        success_rate = success_count / len(crypto_pairs) * 100
        print(f"📊 Marktdaten: {success_count}/{len(crypto_pairs)} erfolgreich ({success_rate:.0f}%)")
        
        return success_count >= 3  # Mindestens 3 von 5 erfolgreich
    
    def test_signals(self) -> bool:
        """Test 2: Signal-Check"""
        print("\n🔄 Test 2: Trading-Signale prüfen...")
        
        # Simuliere einige Signale für Test
        test_signals = []
        
        for pair, price in self.current_prices.items():
            # Einfache Test-Signale generieren
            if pair == 'BTC-EUR':
                test_signals.append({
                    'pair': pair,
                    'action': 'BUY',
                    'quantity': 0.001,
                    'price': price * 0.999,  # 0.1% unter Marktpreis
                    'confidence': 0.75
                })
            elif pair == 'ETH-EUR':
                test_signals.append({
                    'pair': pair,
                    'action': 'SELL',
                    'quantity': 0.01,
                    'price': price * 1.001,  # 0.1% über Marktpreis
                    'confidence': 0.65
                })
        
        for signal in test_signals:
            print(f"   📋 {signal['action']}: {signal['quantity']:.6f} {signal['pair']} @ €{signal['price']:.4f}")
            self.prepared_orders.append(signal)
        
        print(f"📊 Signale: {len(test_signals)} generiert")
        return len(test_signals) > 0
    
    def test_risk_check(self) -> bool:
        """Test 3: Risiko-Check"""
        print("\n🔄 Test 3: Risiko-Management prüfen...")
        
        total_value = 0
        max_single_order = 0
        warnings = []
        
        for order in self.prepared_orders:
            current_price = self.current_prices.get(order['pair'], order['price'])
            order_value = order['quantity'] * current_price
            total_value += order_value
            
            if order_value > max_single_order:
                max_single_order = order_value
            
            # Risiko-Checks
            if order_value > 1000:  # €1000 Limit pro Order
                warnings.append(f"Große Order: {order['pair']} €{order_value:.2f}")
            
            price_diff = abs(order['price'] - current_price) / current_price * 100
            if price_diff > 5:  # 5% Preisabweichung
                warnings.append(f"Hohe Preisabweichung: {order['pair']} {price_diff:.1f}%")
        
        print(f"   💰 Gesamt-Exposure: €{total_value:.2f}")
        print(f"   📊 Größte Order: €{max_single_order:.2f}")
        print(f"   ⚠️ Warnungen: {len(warnings)}")
        
        for warning in warnings:
            print(f"      ⚠️ {warning}")
        
        # Risiko OK wenn unter €5000 Gesamt-Exposure
        risk_ok = total_value < 5000
        print(f"📊 Risiko-Check: {'✅ Bestanden' if risk_ok else '❌ Fehlgeschlagen'}")
        
        return risk_ok
    
    def test_portfolio_simulation(self) -> bool:
        """Test 4: Portfolio-Simulation"""
        print("\n🔄 Test 4: Portfolio-Simulation...")
        
        # Start-Portfolio
        portfolio = {
            'cash': 5000,  # €5000 Cash
            'crypto': {},  # Keine Crypto-Positionen
            'total_value': 5000
        }
        
        print(f"   💰 Start-Cash: €{portfolio['cash']:.2f}")
        
        # Simuliere Orders
        trades_executed = 0
        total_fees = 0
        
        for order in self.prepared_orders:
            current_price = self.current_prices.get(order['pair'], order['price'])
            order_value = order['quantity'] * current_price
            fee = order_value * 0.0015  # 0.15% Fee
            
            if order['action'] == 'BUY':
                if portfolio['cash'] >= (order_value + fee):
                    # Buy ausführen
                    portfolio['cash'] -= (order_value + fee)
                    crypto = order['pair'].replace('-EUR', '')
                    portfolio['crypto'][crypto] = portfolio['crypto'].get(crypto, 0) + order['quantity']
                    trades_executed += 1
                    total_fees += fee
                    print(f"   ✅ KAUFE: {order['quantity']:.6f} {crypto} für €{order_value:.2f}")
                else:
                    print(f"   ❌ Nicht genug Cash für {order['pair']}")
            
            elif order['action'] == 'SELL':
                crypto = order['pair'].replace('-EUR', '')
                if portfolio['crypto'].get(crypto, 0) >= order['quantity']:
                    # Sell ausführen
                    portfolio['cash'] += (order_value - fee)
                    portfolio['crypto'][crypto] -= order['quantity']
                    trades_executed += 1
                    total_fees += fee
                    print(f"   ✅ VERKAUFE: {order['quantity']:.6f} {crypto} für €{order_value:.2f}")
                else:
                    print(f"   ❌ Nicht genug {crypto} zum verkaufen")
        
        # End-Portfolio berechnen
        crypto_value = 0
        for crypto, quantity in portfolio['crypto'].items():
            if quantity > 0:
                price = self.current_prices.get(f"{crypto}-EUR", 0)
                value = quantity * price
                crypto_value += value
                print(f"   🪙 Position: {quantity:.6f} {crypto} = €{value:.2f}")
        
        portfolio['total_value'] = portfolio['cash'] + crypto_value
        pnl = portfolio['total_value'] - 5000
        
        print(f"   💰 End-Cash: €{portfolio['cash']:.2f}")
        print(f"   🪙 Crypto-Wert: €{crypto_value:.2f}")
        print(f"   📈 Gesamt-Wert: €{portfolio['total_value']:.2f}")
        print(f"   📊 P&L: €{pnl:+.2f}")
        print(f"   🔄 Trades: {trades_executed}")
        print(f"   💸 Fees: €{total_fees:.2f}")
        
        return True
    
    def run_quick_test(self) -> bool:
        """Führe alle Tests durch"""
        print("🚀 Starte Quick Trading Test...")
        
        results = {}
        
        # Test 1: Marktdaten
        results['market_data'] = self.test_market_data()
        
        # Test 2: Signale
        results['signals'] = self.test_signals()
        
        # Test 3: Risiko
        results['risk_check'] = self.test_risk_check()
        
        # Test 4: Portfolio
        results['portfolio'] = self.test_portfolio_simulation()
        
        # Zusammenfassung
        print("\n" + "="*60)
        print("📋 QUICK TEST ERGEBNISSE")
        print("="*60)
        
        all_passed = True
        for test_name, passed in results.items():
            status = "✅ BESTANDEN" if passed else "❌ FEHLGESCHLAGEN"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if not passed:
                all_passed = False
        
        print("="*60)
        if all_passed:
            print("🎉 ALLE TESTS BESTANDEN!")
            print("📤 System bereit für Trading (Orders deaktiviert)")
        else:
            print("❌ EINIGE TESTS FEHLGESCHLAGEN")
            print("🔧 Bitte Probleme beheben")
        
        print(f"⏰ Test abgeschlossen: {datetime.now().strftime('%H:%M:%S')}")
        
        return all_passed

def main():
    """Main function"""
    print("🚀 Quick Trading Test - Ohne Order-Übermittlung")
    print("="*60)
    
    test = QuickTradingTest()
    
    try:
        success = test.run_quick_test()
        return success
        
    except KeyboardInterrupt:
        print("\n⏹️ Test abgebrochen")
        return False
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
        return False

if __name__ == "__main__":
    main()
