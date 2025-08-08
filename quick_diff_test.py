#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schneller Test für Trade on Open Equity Unstimmigkeit
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_test():
    """Schneller Test eines Trade on Open Symbols"""
    print("🔍 SCHNELLER EQUITY vs FINAL CAPITAL TEST")
    print("=" * 60)
    
    # Test nur BTC-EUR (Trade on Open)
    from crypto_backtesting_module import run_backtest
    
    print("📊 Testing BTC-EUR (Trade on Open)...")
    
    try:
        result = run_backtest('BTC-EUR')
        
        if result:
            print(f"\n✅ BTC-EUR Backtest Results:")
            print(f"   Initial Capital: €{result.get('initial_capital', 0):.2f}")
            print(f"   Final Capital (DEBUG): €{result.get('final_capital', 0):.2f}")
            print(f"   Total Return %: {result.get('total_return_pct', 0):.2f}%")
            print(f"   Number of Trades: {result.get('num_trades', 0)}")
            
            if 'equity_curve' in result and result['equity_curve']:
                equity_curve = result['equity_curve']
                last_equity = equity_curve[-1]
                final_capital = result.get('final_capital', 0)
                
                print(f"\n🔍 EQUITY CURVE ANALYSE:")
                print(f"   Equity Curve Length: {len(equity_curve)}")
                print(f"   First Equity Value: €{equity_curve[0]:.2f}")
                print(f"   Last Equity Value: €{last_equity:.2f}")
                print(f"   Final Capital (DEBUG): €{final_capital:.2f}")
                
                difference = last_equity - final_capital
                print(f"\n❗ DIFFERENZ: €{difference:.2f}")
                
                if abs(difference) > 0.01:
                    print(f"   ⚠️ UNSTIMMIGKEIT ERKANNT! Differenz = €{difference:.2f}")
                    print(f"   💡 Mögliche Ursache: Equity Curve Berechnung vs. Backtest Final Capital")
                else:
                    print(f"   ✅ Werte stimmen überein (Differenz < €0.01)")
                    
                # Zeige die letzten 5 Equity Werte
                print(f"\n📊 Letzte 5 Equity Values:")
                for i in range(max(0, len(equity_curve)-5), len(equity_curve)):
                    print(f"   Day {i+1}: €{equity_curve[i]:.2f}")
                    
            else:
                print("   ❌ Keine Equity Curve verfügbar")
        else:
            print("   ❌ Backtest fehlgeschlagen")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    quick_test()
