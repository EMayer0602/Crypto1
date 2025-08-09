#!/usr/bin/env python3
"""
Quick check to verify the Net PnL fix is working in real backtest results
"""

import pandas as pd
from crypto_backtesting_module import run_backtest, load_crypto_data_yf
from config import backtest_years
from crypto_tickers import crypto_tickers

def check_net_pnl_fix():
    """Quick verification that the fix is working"""
    
    print("🔍 Checking Net PnL fix in real backtest...")
    
    # Test with XRP-EUR (has been showing good results)
    ticker = "XRP-EUR"
    config = crypto_tickers[ticker]
    
    try:
        # Run backtest with correct parameters
        result = run_backtest(ticker, config)
        
        if 'matched_trades' in result and not result['matched_trades'].empty:
            matched_trades = result['matched_trades']
            
            print(f"✅ Found {len(matched_trades)} matched trades for {ticker}")
            
            # Check all trades for correct Net PnL usage
            initial_capital = config['initialCapitalLong']
            running_capital = initial_capital
            
            print(f"\n📊 Verifying Capital calculations:")
            print(f"Initial Capital: €{initial_capital:.2f}")
            
            for idx, trade in matched_trades.iterrows():
                status = trade['Status']
                pnl = trade['PnL']
                net_pnl = trade['Net PnL']
                capital = trade['Capital']
                
                if status == 'closed':
                    # For closed trades, capital should be running + net_pnl
                    expected_capital = running_capital + net_pnl
                    running_capital = expected_capital
                else:
                    # For open trades, capital should be initial + net_pnl (with artificial close)
                    expected_capital = initial_capital + net_pnl
                
                print(f"Trade {idx+1} ({status}): PnL=€{pnl:.2f}, Net PnL=€{net_pnl:.2f}, Capital=€{capital:.2f}")
                
                if abs(capital - expected_capital) < 0.01:
                    print(f"  ✅ CORRECT: Uses Net PnL")
                else:
                    print(f"  ❌ ERROR: Expected €{expected_capital:.2f}, got €{capital:.2f}")
                    
            print(f"\n🎯 Final Result:")
            final_trade = matched_trades.iloc[-1]
            print(f"Final Capital: €{final_trade['Capital']:.2f}")
            print(f"Total Return: {((final_trade['Capital'] / initial_capital - 1) * 100):.2f}%")
            
        else:
            print("❌ No trades found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_net_pnl_fix()
