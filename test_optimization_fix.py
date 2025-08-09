#!/usr/bin/env python3
"""
Einfacher Test der reparierten Optimierung
"""

import sys
import os
sys.path.append(os.getcwd())

from crypto_backtesting_module import optimize_parameters, load_crypto_data_yf

def test_optimization_fix():
    """Testet ob die Optimierung jetzt verschiedene Parameter liefert"""
    print("🔍 TEST DER REPARIERTEN OPTIMIERUNG")
    print("="*40)
    
    # Test mit 2 verschiedenen Tickers
    symbols = ['BTC-EUR', 'XRP-EUR']
    
    for symbol in symbols:
        print(f"\n📊 Teste {symbol}")
        
        try:
            # Lade nur kleine Datenmenge für schnellen Test  
            df = load_crypto_data_yf(symbol)
            if df is None or df.empty:
                print(f"   ❌ Keine Daten")
                continue
                
            df_small = df.tail(60)  # Nur letzte 60 Tage für schnelle Optimierung
            print(f"   📈 Test mit {len(df_small)} Tagen")
            
            # Teste Optimierung
            result = optimize_parameters(df_small, symbol)
            
            if result:
                p = result.get('optimal_past_window', 'N/A')
                tw = result.get('optimal_trade_window', 'N/A')
                print(f"   ✅ Ergebnis: p={p}, tw={tw}")
            else:
                print(f"   ❌ Kein Ergebnis")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_optimization_fix()
