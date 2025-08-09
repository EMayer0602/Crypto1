#!/usr/bin/env python3
"""
Schneller Test der Optimierungslogik
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Import our modules
sys.path.append(os.getcwd())
from crypto_backtesting_module import run_backtest, load_crypto_data_yf

def test_optimization():
    """Testet ob die Optimierung verschiedene Parameter findet"""
    
    print("🔍 TEST DER OPTIMIERUNGSLOGIK")
    print("="*50)
    
    # Test mit 2 verschiedenen Tickers
    symbols = ['BTC-EUR', 'XRP-EUR']
    
    for symbol in symbols:
        print(f"\n📊 Teste {symbol}")
        print("-"*30)
        
        # Lade Daten
        df = load_crypto_data_yf(symbol)
        
        if df is None or df.empty:
            print(f"❌ Keine Daten für {symbol}")
            continue
            
        print(f"   Daten: {len(df)} Tage")
        
        # Manueller Test verschiedener Parameter
        test_params = [
            (2, 1), (5, 1), (10, 1), 
            (2, 2), (5, 2), (10, 2)
        ]
        
        results = []
        
        for p, tw in test_params:
            try:
                # Simuliere einen Mini-Backtest
                from crypto_backtesting_module import simulate_trades_compound_extended
                import crypto_tickers
                
                config = crypto_tickers.crypto_tickers[symbol]
                initial_capital = config['initialCapitalLong']
                
                # Truncate data for testing
                df_test = df.tail(100).copy()  # Nur letzte 100 Tage
                
                # Simulate trades
                ext_trades, _, final_capital = simulate_trades_compound_extended(
                    df_test, initial_capital, p, tw, 
                    commission_rate=0.0018, 
                    round_factor=config['order_round_factor'],
                    trade_on=config['trade_on']
                )
                
                profit = final_capital - initial_capital
                results.append((p, tw, final_capital, profit))
                
                print(f"     p={p}, tw={tw}: €{final_capital:.2f} (Profit: €{profit:.2f})")
                
            except Exception as e:
                print(f"     p={p}, tw={tw}: ERROR - {e}")
        
        if results:
            # Finde besten
            best = max(results, key=lambda x: x[2])
            print(f"   🏆 Bester: p={best[0]}, tw={best[1]} mit €{best[2]:.2f}")
            
            # Prüfe ob alle gleich sind
            all_same = len(set([r[2] for r in results])) == 1
            print(f"   ⚠️ Alle Ergebnisse gleich? {all_same}")
            
            if all_same:
                print(f"   📊 Alle Ergebnisse: €{results[0][2]:.2f}")
        else:
            print("   ❌ Keine gültigen Ergebnisse")

if __name__ == "__main__":
    test_optimization()
