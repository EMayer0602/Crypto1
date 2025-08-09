#!/usr/bin/env python3
"""
Direkter Vergleich: Letzter Equity-Wert vs Final Capital aus Matched Trades
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def direct_comparison_test():
    """Direkter Vergleich für einen Ticker"""
    symbol = 'XRP-EUR'
    config = crypto_tickers[symbol]
    
    print(f"🔍 DIRECT COMPARISON: {symbol}")
    print("="*50)
    print(f"Trade Mode: {config.get('trade_on', 'Close')}")
    print(f"Initial Capital: €{config.get('initialCapitalLong', 1000)}")
    
    try:
        result = run_backtest(symbol, config)
        
        if result and 'matched_trades' in result and 'equity_curve' in result:
            matched_trades = result['matched_trades']
            equity_curve = result['equity_curve']
            
            print(f"\n📊 RESULTS:")
            print(f"Matched Trades: {len(matched_trades)} trades")
            print(f"Equity Curve: {len(equity_curve)} daily values")
            
            if len(matched_trades) > 0 and len(equity_curve) > 0:
                # Final values
                equity_final = equity_curve[-1]
                
                # Debug: show matched trades structure
                print(f"\n📋 MATCHED TRADES COLUMNS:")
                print(list(matched_trades.columns))
                
                print(f"\n📋 LAST MATCHED TRADE:")
                last_trade = matched_trades.iloc[-1]
                for col in ['Entry Date', 'Exit Date', 'Entry Price', 'Exit Price', 'Net PnL', 'Capital']:
                    if col in last_trade:
                        print(f"   {col}: {last_trade[col]}")
                
                # Final capital from matched trades
                if 'Capital' in matched_trades.columns:
                    matched_final = matched_trades['Capital'].iloc[-1]
                    difference = abs(equity_final - matched_final)
                    
                    print(f"\n🎯 FINAL COMPARISON:")
                    print(f"📈 Equity Curve Final: €{equity_final:.4f}")
                    print(f"💰 Matched Final:      €{matched_final:.4f}")
                    print(f"🔍 Difference:         €{difference:.4f}")
                    
                    if difference <= 0.01:
                        print(f"✅ PERFECT MATCH! (≤ €0.01)")
                        return True
                    else:
                        print(f"❌ MISMATCH! (> €0.01)")
                        
                        # Debug: Show calculation breakdown
                        initial = config.get('initialCapitalLong', 1000)
                        total_net_pnl = matched_trades['Net PnL'].sum()
                        calculated_final = initial + total_net_pnl
                        
                        print(f"\n🔍 DEBUG CALCULATION:")
                        print(f"   Initial Capital: €{initial:.2f}")
                        print(f"   Total Net PnL:   €{total_net_pnl:.2f}")
                        print(f"   Calculated:      €{calculated_final:.2f}")
                        print(f"   Equity Final:    €{equity_final:.2f}")
                        print(f"   Matched Final:   €{matched_final:.2f}")
                        
                        return False
                else:
                    print("❌ 'Capital' column not found in matched trades")
                    return False
            else:
                print("❌ No trades or equity data")
                return False
        else:
            print("❌ Backtest failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = direct_comparison_test()
    
    if success:
        print(f"\n🎉 SUCCESS: Equity formulas are CORRECT!")
        print(f"✅ Equity curve final value matches matched trades final capital")
    else:
        print(f"\n❌ ISSUE: Equity formulas need adjustment")
        print(f"⚠️  Equity curve does not match matched trades final capital")
