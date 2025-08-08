#!/usr/bin/env python3

import sys
import os
import pandas as pd
sys.path.append(os.getcwd())

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers
from plotly_utils import create_equity_curve_from_matched_trades

def debug_equity_problem():
    """Debug warum die grüne Strategy Equity Linie falsch ist"""
    
    symbol = "XRP-EUR"  # Das Symbol aus dem Chart
    config = crypto_tickers[symbol]
    
    print(f"🔍 DEBUGGING Strategy Equity für {symbol}")
    print(f"💰 Expected Initial Capital: €{config['initialCapitalLong']}")  # €1000
    
    # Run backtest
    result = run_backtest(symbol, config)
    
    if result and isinstance(result, dict):
        print(f"\n✅ BACKTEST RESULT:")
        
        # Check matched trades
        matched_trades = result.get('matched_trades', pd.DataFrame())
        print(f"📊 Matched Trades: {len(matched_trades)}")
        
        if not matched_trades.empty:
            print(f"📈 First 3 trades:")
            for i, (_, trade) in enumerate(matched_trades.head(3).iterrows()):
                print(f"   Trade {i+1}: Entry={trade.get('Entry Date', 'N/A')}, Exit={trade.get('Exit Date', 'N/A')}")
                print(f"            Entry Price={trade.get('Entry Price', 0):.4f}, Exit Price={trade.get('Exit Price', 0):.4f}")
                print(f"            Shares={trade.get('Quantity', 0):.6f}, PnL={trade.get('Net PnL', 0):.2f}")
        
        # Check equity curve from result
        equity_curve = result.get('equity_curve', [])
        print(f"\n💹 EQUITY CURVE:")
        print(f"   Length: {len(equity_curve)}")
        if equity_curve:
            print(f"   Start: €{equity_curve[0]:.2f} (should be €{config['initialCapitalLong']})")
            print(f"   End: €{equity_curve[-1]:.2f}")
            print(f"   First 10: {[f'€{v:.0f}' for v in equity_curve[:10]]}")
            print(f"   Last 10: {[f'€{v:.0f}' for v in equity_curve[-10:]]}")
            
            # Check if it starts correctly
            if abs(equity_curve[0] - config['initialCapitalLong']) > 0.01:
                print(f"   ❌ WRONG START VALUE!")
            else:
                print(f"   ✅ Start value correct")
        
        # Test the equity function directly
        df = result.get('df', pd.DataFrame())
        if not matched_trades.empty and not df.empty:
            print(f"\n🧪 TESTING EQUITY FUNCTION DIRECTLY:")
            
            # Convert matched trades to list format
            trades_list = []
            for _, trade in matched_trades.iterrows():
                trade_dict = {
                    'buy_date': trade['Entry Date'],
                    'sell_date': trade['Exit Date'], 
                    'buy_price': trade['Entry Price'],
                    'sell_price': trade['Exit Price'],
                    'shares': trade['Quantity'],
                    'pnl': trade['Net PnL'],
                    'is_open': trade.get('Status', '') == 'OPEN'
                }
                trades_list.append(trade_dict)
            
            print(f"   Calling create_equity_curve_from_matched_trades with:")
            print(f"   - trades_list: {len(trades_list)} trades")
            print(f"   - initial_capital: €{config['initialCapitalLong']}")
            print(f"   - df length: {len(df)} days")
            
            test_equity = create_equity_curve_from_matched_trades(
                trades_list, config['initialCapitalLong'], df
            )
            
            print(f"\n📊 DIRECT FUNCTION RESULT:")
            print(f"   Length: {len(test_equity)}")
            print(f"   Start: €{test_equity[0]:.2f}")
            print(f"   End: €{test_equity[-1]:.2f}")
            print(f"   Matches result curve: {test_equity == equity_curve}")
            
            # Check for differences
            if test_equity != equity_curve:
                print(f"   ❌ MISMATCH between function result and stored curve!")
                print(f"   Function first 5: {[f'€{v:.0f}' for v in test_equity[:5]]}")
                print(f"   Stored first 5: {[f'€{v:.0f}' for v in equity_curve[:5]]}")
    else:
        print("❌ BACKTEST FAILED!")

if __name__ == "__main__":
    debug_equity_problem()
