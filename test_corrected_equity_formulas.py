#!/usr/bin/env python3
"""
Test-Script zur Validierung der korrigierten Equity-Kurven-Berechnung
Testet die User-Spezifikation für Trade on Open vs Close
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def test_corrected_equity_formulas():
    """Test die korrigierte Equity-Kurven-Berechnung"""
    print("🎯 TEST: KORRIGIERTE EQUITY-KURVEN-BERECHNUNG")
    print("="*80)
    
    # Test mit einem Trade on Open und einem Trade on Close Ticker
    test_cases = [
        ('BTC-EUR', 'Open'),   # BTC: Trade on Open
        ('XRP-EUR', 'Close')   # XRP: Trade on Close
    ]
    
    for symbol, expected_mode in test_cases:
        print(f"\n📊 Testing {symbol} (Expected: {expected_mode})")
        print("-"*60)
        
        config = crypto_tickers[symbol]
        actual_mode = config.get('trade_on', 'Close')
        initial_capital = config.get('initialCapitalLong', 1000)
        
        print(f"🔧 Initial Capital: €{initial_capital}")
        print(f"🔧 Trade Mode: {actual_mode}")
        print(f"🔧 Expected Formulas:")
        
        if actual_mode == 'Open':
            print("   📈 BUY day: capital = capital + shares * (Close - Open) - fees")
            print("   📊 LONG days: capital = capital + shares * (Close - previous_Close)")
            print("   💰 SELL day: capital = capital + shares * (Open - previous_Close) - fees")
        else:
            print("   📈 BUY day: capital = capital - fees")
            print("   📊 LONG days: capital = capital + shares * (Close - previous_Close)")
            print("   💰 SELL day: capital = capital + shares * (Close - previous_Close) - fees")
        
        print("   🔒 After SELL: capital bleibt CONSTANT")
        
        try:
            # Run backtest
            result = run_backtest(symbol, config)
            
            if result and 'matched_trades' in result and 'equity_curve' in result:
                matched_trades = result['matched_trades']
                equity_curve = result['equity_curve']
                
                print(f"\n✅ Backtest Result:")
                print(f"   📊 Matched Trades: {len(matched_trades)}")
                print(f"   📈 Equity Curve Length: {len(equity_curve)}")
                
                if len(equity_curve) > 0:
                    print(f"   💰 Start Capital: €{equity_curve[0]:.2f}")
                    print(f"   💰 End Capital: €{equity_curve[-1]:.2f}")
                    print(f"   📊 Total Return: {(equity_curve[-1]/equity_curve[0] - 1)*100:.2f}%")
                    
                    # Prüfe Variation (sollte nicht flach sein)
                    unique_values = len(set([round(v, -1) for v in equity_curve]))
                    variation_pct = (max(equity_curve) - min(equity_curve)) / equity_curve[0] * 100
                    
                    print(f"   📊 Unique Values (10€ gerundet): {unique_values}")
                    print(f"   📊 Total Variation: {variation_pct:.1f}%")
                    
                    if unique_values > 10:
                        print("   ✅ GOOD: Equity curve shows daily variation!")
                    else:
                        print("   ⚠️  WARNING: Equity curve may be too flat")
                    
                    # Sample einige Werte
                    if len(equity_curve) >= 10:
                        sample_indices = [0, 2, 4, 6, 8, -5, -3, -1]
                        print(f"   📋 Sample Values:")
                        for i in sample_indices:
                            if abs(i) < len(equity_curve):
                                print(f"      Day {i if i >= 0 else len(equity_curve)+i}: €{equity_curve[i]:.2f}")
                
                # Prüfe erste paar Matched Trades
                if len(matched_trades) > 0:
                    print(f"\n📋 First Matched Trade Details:")
                    first_trade = matched_trades.iloc[0]
                    print(f"   Entry: {first_trade.get('Entry Date')} @ €{first_trade.get('Entry Price'):.4f}")
                    print(f"   Exit:  {first_trade.get('Exit Date')} @ €{first_trade.get('Exit Price'):.4f}")
                    print(f"   PnL: €{first_trade.get('PnL', 0):.2f}")
                    print(f"   Net PnL: €{first_trade.get('Net PnL', 0):.2f}")
                    
            else:
                print(f"❌ {symbol}: Backtest failed or incomplete result")
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 CONCLUSION:")
    print(f"✅ Test completed for Trade on Open vs Close formulas")
    print(f"✅ Check console output above for equity curve validation")

def compare_open_vs_close_differences():
    """Vergleiche die Unterschiede zwischen Open und Close Trading"""
    print(f"\n🔍 COMPARISON: OPEN VS CLOSE TRADING DIFFERENCES")
    print("="*80)
    
    # Verwende XRP für beide Modi (nur zum Vergleich)
    symbol = 'XRP-EUR'
    base_config = crypto_tickers[symbol].copy()
    
    results = {}
    
    for mode in ['Open', 'Close']:
        print(f"\n📊 Testing {symbol} with forced trade_on='{mode}'")
        test_config = base_config.copy()
        test_config['trade_on'] = mode
        
        try:
            result = run_backtest(symbol, test_config)
            if result and 'equity_curve' in result:
                equity_curve = result['equity_curve']
                results[mode] = {
                    'start': equity_curve[0] if len(equity_curve) > 0 else 0,
                    'end': equity_curve[-1] if len(equity_curve) > 0 else 0,
                    'length': len(equity_curve)
                }
                print(f"   💰 Final Capital: €{results[mode]['end']:.2f}")
            else:
                print(f"   ❌ Failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Vergleich
    if 'Open' in results and 'Close' in results:
        open_final = results['Open']['end']
        close_final = results['Close']['end']
        difference = abs(open_final - close_final)
        
        print(f"\n📊 COMPARISON RESULTS:")
        print(f"   Trade on Open:  €{open_final:.2f}")
        print(f"   Trade on Close: €{close_final:.2f}")
        print(f"   Difference: €{difference:.2f}")
        
        if difference > 10:
            print(f"   ✅ GOOD: Significant difference between Open/Close trading")
        else:
            print(f"   ⚠️  WARNING: Small difference - formulas may be similar")

if __name__ == "__main__":
    test_corrected_equity_formulas()
    compare_open_vs_close_differences()
