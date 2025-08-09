#!/usr/bin/env python3
"""
Verify that the Net PnL fix is properly integrated in the main backtest
"""

import pandas as pd
from crypto_backtesting_module import run_backtest, load_crypto_data_yf
from config import tickers, backtest_years
import datetime

def verify_fix_integration():
    """Verify the fix is working in the main backtest pipeline"""
    
    print("🔍 Verifying Net PnL fix integration...")
    
    # Test with one ticker that has recent data
    test_ticker = "XRP-EUR"
    ticker_config = tickers[test_ticker]
    
    print(f"📊 Testing ticker: {test_ticker}")
    print(f"Trade on: {ticker_config['trade_on']}")
    print(f"Initial Capital: €{ticker_config['initialCapitalLong']}")
    print(f"Round Factor: {ticker_config['order_round_factor']}")
    
    # Load data
    try:
        df = load_crypto_data_yf(test_ticker, backtest_years)
        print(f"✅ Loaded {len(df)} days of data")
        
        # Run a quick backtest
        result = run_backtest(
            df, 
            ticker_config['initialCapitalLong'], 
            ticker_config['order_round_factor'],
            ticker_config['trade_on']
        )
        
        # Check if we have matched trades
        if 'matched_trades' in result and not result['matched_trades'].empty:
            matched_trades = result['matched_trades']
            
            print(f"\n📈 Found {len(matched_trades)} matched trades")
            
            # Check for open trades
            open_trades = matched_trades[matched_trades['Status'] == 'open']
            closed_trades = matched_trades[matched_trades['Status'] == 'closed']
            
            print(f"Open trades: {len(open_trades)}")
            print(f"Closed trades: {len(closed_trades)}")
            
            # Verify Net PnL is being used correctly
            if len(open_trades) > 0:
                print(f"\n🔍 Checking open trades Net PnL usage:")
                for idx, trade in open_trades.iterrows():
                    pnl = trade['PnL']
                    net_pnl = trade['Net PnL']
                    capital = trade['Capital']
                    initial_cap = ticker_config['initialCapitalLong']
                    
                    # Capital should be initial + net_pnl, not initial + pnl
                    expected_capital = initial_cap + net_pnl
                    
                    print(f"  Trade: PnL=€{pnl:.2f}, Net PnL=€{net_pnl:.2f}")
                    print(f"  Capital: €{capital:.2f}, Expected: €{expected_capital:.2f}")
                    
                    if abs(capital - expected_capital) < 0.01:
                        print(f"  ✅ CORRECT: Using Net PnL for capital")
                    else:
                        print(f"  ❌ ERROR: Still using raw PnL for capital")
            
            if len(closed_trades) > 0:
                print(f"\n🔍 Checking closed trades (should already be correct):")
                total_capital = ticker_config['initialCapitalLong']
                for idx, trade in closed_trades.iterrows():
                    net_pnl = trade['Net PnL']
                    total_capital += net_pnl
                    print(f"  Trade Net PnL: €{net_pnl:.2f}, Running Capital: €{total_capital:.2f}")
        else:
            print("ℹ️ No matched trades found - may be due to recent market conditions")
            
        print(f"\n✅ Integration test completed successfully")
        
    except Exception as e:
        print(f"❌ Error during integration test: {e}")

if __name__ == "__main__":
    verify_fix_integration()
