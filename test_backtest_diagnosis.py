#!/usr/bin/env python3
"""
Quick backtest diagnosis - check what might be causing worse results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import run_backtest, simulate_matched_trades
from crypto_tickers import crypto_tickers
import pandas as pd

def test_single_ticker():
    """Test a single ticker to diagnose issues"""
    ticker = "BTC-EUR"
    config = crypto_tickers[ticker]
    
    print(f"🔍 Testing {ticker} with config:")
    print(f"   Initial Capital: €{config['initialCapitalLong']}")
    print(f"   Order Round Factor: {config['order_round_factor']}")
    print(f"   Trade On: {config['trade_on']}")
    
    try:
        # Test the simulate_matched_trades function with simple data
        test_ext_full = pd.DataFrame([
            {
                'Action': 'buy',
                'Long Date detected': '2024-01-01',
                'Level Close': 50000.0  # BTC at 50k EUR
            },
            {
                'Action': 'sell', 
                'Long Date detected': '2024-01-02',
                'Level Close': 55000.0  # BTC at 55k EUR (10% gain)
            }
        ])
        
        initial_capital = config['initialCapitalLong']
        commission_rate = 0.001
        order_round_factor = config['order_round_factor']
        
        print(f"\n📊 Test trade simulation:")
        print(f"   Buy at: €50,000")
        print(f"   Sell at: €55,000 (10% gain)")
        
        matched_trades = simulate_matched_trades(
            test_ext_full, 
            initial_capital, 
            commission_rate, 
            order_round_factor=order_round_factor
        )
        
        if not matched_trades.empty:
            trade = matched_trades.iloc[0]
            print(f"\n✅ Trade Results:")
            print(f"   Quantity: {trade['Quantity']:.6f} BTC")
            print(f"   Gross PnL: €{trade['PnL']:.2f}")
            print(f"   Commission: €{trade['Commission']:.2f}")
            print(f"   Net PnL: €{trade['Net PnL']:.2f}")
            print(f"   Final Capital: €{trade['Capital']:.2f}")
            
            # Calculate expected values manually
            raw_quantity = initial_capital / 50000.0
            expected_quantity = round(raw_quantity / order_round_factor) * order_round_factor
            expected_pnl = (55000.0 - 50000.0) * expected_quantity
            expected_commission = (50000.0 + 55000.0) * expected_quantity * commission_rate
            expected_net_pnl = expected_pnl - expected_commission
            expected_final_capital = initial_capital + expected_net_pnl
            
            print(f"\n📊 Expected vs Actual:")
            print(f"   Expected Quantity: {expected_quantity:.6f}")
            print(f"   Expected Net PnL: €{expected_net_pnl:.2f}")
            print(f"   Expected Final Capital: €{expected_final_capital:.2f}")
            
            # Check for issues
            if abs(trade['Quantity'] - expected_quantity) > 0.000001:
                print(f"❌ QUANTITY MISMATCH!")
            if abs(trade['Net PnL'] - expected_net_pnl) > 0.01:
                print(f"❌ NET PNL MISMATCH!")
            if trade['Quantity'] == 0:
                print(f"❌ ZERO QUANTITY - Order round factor too large!")
        else:
            print("❌ No matched trades generated!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_all_tickers():
    """Quick test of all tickers"""
    print(f"\n🔍 Testing all tickers for quantity issues:")
    
    for ticker, config in crypto_tickers.items():
        initial_capital = config['initialCapitalLong'] 
        order_round_factor = config['order_round_factor']
        
        # Test with a typical crypto price
        test_price = 100.0  # €100 per coin
        raw_quantity = initial_capital / test_price
        rounded_quantity = round(raw_quantity / order_round_factor) * order_round_factor
        
        print(f"   {ticker:10} | Capital: €{initial_capital:4.0f} | Round: {order_round_factor:8.3f} | Raw: {raw_quantity:8.2f} | Rounded: {rounded_quantity:8.2f}")
        
        if rounded_quantity == 0:
            print(f"      ❌ ZERO QUANTITY! Round factor {order_round_factor} too large for capital €{initial_capital}")

if __name__ == "__main__":
    test_single_ticker()
    test_all_tickers()
