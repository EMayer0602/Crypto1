#!/usr/bin/env python3
"""
Test the NEW equity function with BTC data and chart
"""

import pandas as pd
from crypto_backtesting_module import run_backtest
from plotly_utils import create_enhanced_plotly_chart
import crypto_tickers as tickers

def test_btc_with_new_equity():
    print("🎯 Testing BTC with NEW EQUITY FUNCTION")
    print("=" * 60)
    
    # Get BTC ticker config
    ticker_info = None
    for ticker in tickers.CRYPTO_TICKERS:
        if ticker['symbol'] == 'BTC-EUR':
            ticker_info = ticker
            break
    
    if not ticker_info:
        print("❌ BTC-EUR ticker not found!")
        return
    
    print(f"📊 Testing {ticker_info['symbol']} with:")
    print(f"   Initial Capital: €{ticker_info['initial_capital']}")
    print(f"   Order Round Factor: {ticker_info['order_round_factor']}")
    print(f"   Max Position Size: {ticker_info['max_position_size']}")
    
    # Run backtest with optimal parameters
    symbol = ticker_info['symbol']
    try:
        result = run_backtest(
            symbol=symbol,
            past_window=5,  # Use known good parameters
            trade_window=2,
            initial_capital=ticker_info['initial_capital'],
            order_round_factor=ticker_info['order_round_factor'],
            max_position_size=ticker_info['max_position_size']
        )
        
        if result and 'matched_trades' in result:
            matched_trades = result['matched_trades']
            df_bt = result.get('df_bt')
            
            print(f"✅ Backtest successful:")
            print(f"   Final Capital: €{result.get('final_capital', 0):.2f}")
            print(f"   PnL: €{result.get('pnl', 0):.2f}")
            print(f"   Trades: {len(matched_trades)}")
            
            if df_bt is not None and len(matched_trades) > 0:
                print(f"\n🎨 Creating enhanced chart with NEW equity...")
                
                chart_path = create_enhanced_plotly_chart(
                    df_bt, 
                    matched_trades, 
                    symbol, 
                    ticker_info['initial_capital'],
                    past_window=5,
                    trade_window=2
                )
                
                if chart_path:
                    print(f"✅ Chart created: {chart_path}")
                    
                    # Open the chart
                    import webbrowser
                    import os
                    webbrowser.open(f'file://{os.path.abspath(chart_path)}')
                    print("🎯 Chart opened in browser!")
                else:
                    print("❌ Failed to create chart")
            else:
                print("⚠️ No data for chart creation")
        else:
            print("❌ Backtest failed or no result")
            
    except Exception as e:
        print(f"❌ Error during backtest: {e}")

if __name__ == "__main__":
    test_btc_with_new_equity()
