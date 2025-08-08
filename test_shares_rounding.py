#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der Shares-Rundung für DOGE-EUR (order_round_factor: 1000)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers

def test_shares_rounding():
    """Test der Shares-Rundung für verschiedene Tickers"""
    print("🔍 TEST DER SHARES-RUNDUNG")
    print("=" * 60)
    
    # Simuliere Shares-Berechnung
    test_capital = 2000  # €2000 für DOGE
    test_price = 0.35    # €0.35 per DOGE
    
    for symbol, config in crypto_tickers.items():
        order_round_factor = config.get('order_round_factor', 1)
        initial_capital = config.get('initialCapitalLong', 1000)
        
        print(f"\n📊 {symbol}:")
        print(f"   Initial Capital: €{initial_capital}")
        print(f"   Round Factor: {order_round_factor}")
        
        # Simuliere raw_shares Berechnung (100% des Kapitals)
        if symbol == "DOGE-EUR":
            price = test_price
        else:
            price = 100  # Dummy-Preis für andere
            
        raw_shares = initial_capital / price  # 100% statt 95%
        print(f"   Raw Shares (100% Capital): {raw_shares}")
        
        # Anwende Rundung
        if order_round_factor >= 1:
            # Runde auf Vielfache des Rundungsfaktors
            rounded_shares = round(raw_shares / order_round_factor) * order_round_factor
            print(f"   Rounded Shares: {rounded_shares} (Vielfache von {order_round_factor})")
        else:
            # Runde auf Dezimalstellen
            decimal_places = len(str(order_round_factor).split('.')[-1])
            rounded_shares = round(raw_shares, decimal_places)
            print(f"   Rounded Shares: {rounded_shares} (auf {decimal_places} Dezimalstellen)")
        
        # Für DOGE speziell testen
        if symbol == "DOGE-EUR":
            print(f"   ✅ DOGE Test:")
            print(f"      Capital €{initial_capital} / Price €{price} = {raw_shares:.2f} raw shares")
            print(f"      Gerundet auf 1000er: {rounded_shares:.0f} shares")
            
            if rounded_shares % 1000 == 0:
                print(f"      ✅ Korrekt: {rounded_shares:.0f} ist Vielfaches von 1000")
            else:
                print(f"      ❌ FEHLER: {rounded_shares:.0f} ist NICHT Vielfaches von 1000!")
    
    print("\n" + "=" * 60)
    
    # Test spezifische DOGE Szenarien
    print("\n🎯 DOGE SPEZIFISCHE TESTS:")
    print("-" * 40)
    
    doge_config = crypto_tickers['DOGE-EUR']
    doge_capital = doge_config['initialCapitalLong']  # €2000
    doge_round_factor = doge_config['order_round_factor']  # 1000.0
    
    test_prices = [0.30, 0.35, 0.40, 0.50]
    
    for test_price in test_prices:
        raw_shares = doge_capital / test_price  # 100% statt 95%
        rounded_shares = round(raw_shares / doge_round_factor) * doge_round_factor
        
        print(f"   Price €{test_price}: {raw_shares:.0f} → {rounded_shares:.0f} shares (100% Capital)")
        
        # Verifikation
        is_correct = (rounded_shares % 1000 == 0)
        status = "✅" if is_correct else "❌"
        print(f"   {status} Vielfaches von 1000: {is_correct}")
        
        # Prüfe auch Gesamtkosten
        cost = rounded_shares * test_price
        commission_rate = 0.001  # 0.1%
        commission = max(cost * commission_rate, 1.0)  # Min €1
        total_cost = cost + commission
        
        if total_cost <= doge_capital:
            print(f"   ✅ Kosten OK: €{total_cost:.2f} <= €{doge_capital}")
        else:
            print(f"   ❌ Kosten zu hoch: €{total_cost:.2f} > €{doge_capital}")
            
        print()  # Leerzeile
    
    print("=" * 60)

if __name__ == "__main__":
    test_shares_rounding()
