#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der Equity Curve vs Final Capital Differenzen
Speziell für Trade on Open vs Close
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def test_equity_vs_final_capital():
    """Teste die Differenzen zwischen Equity Curve Ende und Final Capital"""
    print("🔍 TESTE EQUITY CURVE vs FINAL CAPITAL DIFFERENZEN")
    print("=" * 80)
    
    results = {}
    
    for symbol, config in crypto_tickers.items():
        print(f"\n📊 Testing {symbol} (Trade on {config['trade_on']})...")
        
        try:
            result = run_backtest(symbol)
            
            if result and 'equity_curve' in result:
                equity_curve = result['equity_curve']
                final_capital_debug = result.get('final_capital', 0)
                initial_capital = result.get('initial_capital', 0)
                
                if equity_curve and len(equity_curve) > 0:
                    last_equity_value = equity_curve[-1]
                    difference = last_equity_value - final_capital_debug
                    
                    results[symbol] = {
                        'trade_on': config['trade_on'],
                        'initial_capital': initial_capital,
                        'last_equity_value': last_equity_value,
                        'final_capital_debug': final_capital_debug,
                        'difference': difference,
                        'difference_pct': (difference / initial_capital * 100) if initial_capital > 0 else 0
                    }
                    
                    print(f"   ✅ {symbol}: Equity End = €{last_equity_value:.2f}, Final Capital = €{final_capital_debug:.2f}, Diff = €{difference:.2f}")
                else:
                    print(f"   ❌ {symbol}: Keine Equity Curve verfügbar")
            else:
                print(f"   ❌ {symbol}: Backtest fehlgeschlagen")
                
        except Exception as e:
            print(f"   ❌ {symbol}: ERROR - {e}")
    
    print("\n" + "=" * 80)
    print("📊 ZUSAMMENFASSUNG DER DIFFERENZEN:")
    print("=" * 80)
    
    # Gruppiere nach Trade Mode
    open_symbols = []
    close_symbols = []
    
    for symbol, data in results.items():
        if data['trade_on'] == 'Open':
            open_symbols.append((symbol, data))
        else:
            close_symbols.append((symbol, data))
    
    print(f"\n🔶 TRADE ON OPEN ({len(open_symbols)} Symbols):")
    print("-" * 60)
    for symbol, data in open_symbols:
        print(f"{symbol:<10} | Diff: €{data['difference']:>8.2f} | {data['difference_pct']:>6.2f}%")
    
    print(f"\n🔷 TRADE ON CLOSE ({len(close_symbols)} Symbols):")
    print("-" * 60)
    for symbol, data in close_symbols:
        print(f"{symbol:<10} | Diff: €{data['difference']:>8.2f} | {data['difference_pct']:>6.2f}%")
    
    # Statistiken
    if results:
        all_diffs = [abs(data['difference']) for data in results.values()]
        open_diffs = [abs(data['difference']) for data in results.values() if data['trade_on'] == 'Open']
        close_diffs = [abs(data['difference']) for data in results.values() if data['trade_on'] == 'Close']
        
        print(f"\n📈 STATISTIKEN:")
        print(f"   Durchschnittliche |Differenz| gesamt: €{sum(all_diffs)/len(all_diffs):.2f}")
        if open_diffs:
            print(f"   Durchschnittliche |Differenz| OPEN:   €{sum(open_diffs)/len(open_diffs):.2f}")
        if close_diffs:
            print(f"   Durchschnittliche |Differenz| CLOSE:  €{sum(close_diffs)/len(close_diffs):.2f}")
        
        print(f"   Maximale |Differenz|: €{max(all_diffs):.2f}")
        print(f"   Minimale |Differenz|: €{min(all_diffs):.2f}")
    
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    test_equity_vs_final_capital()
