#!/usr/bin/env python3
"""
Validierung: Equity Curve Final Value = Matched Trades Final Capital
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def validate_equity_matches_final_capital():
    """Prüft ob Equity Curve Final Value = Matched Trades Final Capital"""
    print("🎯 VALIDATION: EQUITY CURVE vs MATCHED TRADES FINAL CAPITAL")
    print("="*80)
    
    for symbol, config in crypto_tickers.items():
        print(f"\n📊 Testing {symbol}")
        print("-" * 50)
        
        trade_on = config.get('trade_on', 'Close')
        initial_capital = config.get('initialCapitalLong', 1000)
        
        print(f"🔧 Trade Mode: {trade_on}")
        print(f"🔧 Initial Capital: €{initial_capital}")
        
        try:
            # Run backtest
            result = run_backtest(symbol, config)
            
            if result and 'matched_trades' in result and 'equity_curve' in result:
                matched_trades = result['matched_trades']
                equity_curve = result['equity_curve']
                
                if len(matched_trades) > 0 and len(equity_curve) > 0:
                    # Get final values
                    equity_final = equity_curve[-1]
                    
                    # Calculate final capital from matched trades
                    # Method 1: Last trade's capital
                    if 'Capital' in matched_trades.columns:
                        matched_final_method1 = matched_trades['Capital'].iloc[-1]
                    else:
                        matched_final_method1 = None
                    
                    # Method 2: Initial + sum of all Net PnL
                    if 'Net PnL' in matched_trades.columns:
                        total_net_pnl = matched_trades['Net PnL'].sum()
                        matched_final_method2 = initial_capital + total_net_pnl
                    else:
                        matched_final_method2 = None
                    
                    print(f"📈 Equity Curve Final:     €{equity_final:.2f}")
                    if matched_final_method1:
                        print(f"💰 Matched Trades Final:   €{matched_final_method1:.2f} (Last Capital)")
                    if matched_final_method2:
                        print(f"💰 Initial + Net PnL Sum:  €{matched_final_method2:.2f}")
                    
                    # Check accuracy
                    tolerance = 0.01  # 1 cent tolerance
                    
                    if matched_final_method1:
                        diff1 = abs(equity_final - matched_final_method1)
                        if diff1 <= tolerance:
                            print(f"✅ PERFECT MATCH (Method 1): Difference = €{diff1:.4f}")
                        else:
                            print(f"❌ MISMATCH (Method 1): Difference = €{diff1:.2f}")
                    
                    if matched_final_method2:
                        diff2 = abs(equity_final - matched_final_method2)
                        if diff2 <= tolerance:
                            print(f"✅ PERFECT MATCH (Method 2): Difference = €{diff2:.4f}")
                        else:
                            print(f"❌ MISMATCH (Method 2): Difference = €{diff2:.2f}")
                    
                    # Show some trade details for debugging
                    print(f"📋 Trade Summary: {len(matched_trades)} trades")
                    if len(matched_trades) > 0:
                        print(f"   First Trade Net PnL: €{matched_trades['Net PnL'].iloc[0]:.2f}")
                        print(f"   Last Trade Net PnL:  €{matched_trades['Net PnL'].iloc[-1]:.2f}")
                        print(f"   Total Net PnL Sum:   €{matched_trades['Net PnL'].sum():.2f}")
                
                else:
                    print("⚠️  No trades or empty equity curve")
            else:
                print("❌ Backtest failed or incomplete result")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"✅ Check above results for perfect matches (≤ €0.01 difference)")
    print(f"✅ Equity curves are correct when they match matched trades final capital")

def quick_single_ticker_test(symbol='XRP-EUR'):
    """Schneller Test für einen einzelnen Ticker"""
    print(f"\n⚡ QUICK TEST: {symbol}")
    print("="*40)
    
    config = crypto_tickers[symbol]
    
    try:
        result = run_backtest(symbol, config)
        
        if result and 'matched_trades' in result and 'equity_curve' in result:
            matched_trades = result['matched_trades']
            equity_curve = result['equity_curve']
            
            if len(matched_trades) > 0 and len(equity_curve) > 0:
                equity_final = equity_curve[-1]
                matched_final = matched_trades['Capital'].iloc[-1]
                difference = abs(equity_final - matched_final)
                
                print(f"📈 Equity Final: €{equity_final:.2f}")
                print(f"💰 Matched Final: €{matched_final:.2f}")
                print(f"🔍 Difference: €{difference:.4f}")
                
                if difference <= 0.01:
                    print(f"✅ PERFECT MATCH!")
                else:
                    print(f"❌ MISMATCH!")
                    
                return difference <= 0.01
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    validate_equity_matches_final_capital()
    
    # Quick test
    if quick_single_ticker_test():
        print(f"\n🎯 CONCLUSION: Equity formulas are CORRECT! ✅")
    else:
        print(f"\n🎯 CONCLUSION: Equity formulas need adjustment ❌")
