#!/usr/bin/env python3
"""
Test to verify that the new equity curve is saved in the result dictionary
"""

import sys
sys.path.append('.')

import pandas as pd
from crypto_backtesting_module import run_backtest
import config
from crypto_tickers import crypto_tickers

def test_equity_in_result():
    """Test if the equity curve is properly saved in the result dict"""
    print("🧪 Testing equity curve in result dictionary")
    print("="*60)
    
    # Load ticker config
    symbol = 'BTC-EUR'
    ticker_config = crypto_tickers.get(symbol, {})
    cfg = {
        'commission_rate': config.COMMISSION_RATE,
        'min_commission': config.MIN_COMMISSION,
        'initial_capital': ticker_config.get('initialCapitalLong', 5000),
        'order_round_factor': ticker_config.get('order_round_factor', 0.01)
    }
    
    # Run backtest for BTC
    result = run_backtest(symbol, cfg)
    
    if not result:
        print("❌ Backtest failed")
        return
    
    print(f"✅ Backtest successful for {result['symbol']}")
    print(f"📊 Result keys: {list(result.keys())}")
    
    # Check if equity_curve exists
    if 'equity_curve' in result:
        equity = result['equity_curve']
        print(f"✅ Equity curve found!")
        print(f"📊 Length: {len(equity)} values")
        print(f"📊 Start: €{equity[0]:.2f}")
        print(f"📊 End: €{equity[-1]:.2f}")
        print(f"📊 Min: €{min(equity):.2f}")
        print(f"📊 Max: €{max(equity):.2f}")
        
        # Check variation
        unique_values = len(set([int(v/10)*10 for v in equity]))  # Round to nearest 10 for unique count
        print(f"📊 Unique value groups (±10€): {unique_values}")
        
        if unique_values > 5:
            print("✅ Equity curve varies correctly!")
        else:
            print("⚠️ WARNING: Limited variation in equity curve")
            
        print(f"📊 Sample first 10: {[f'€{v:.0f}' for v in equity[:10]]}")
        print(f"📊 Sample last 10: {[f'€{v:.0f}' for v in equity[-10:]]}")
        
    else:
        print("❌ No equity_curve in result dictionary")
        
    # Check matched trades
    if 'matched_trades' in result:
        trades = result['matched_trades']
        print(f"📈 Matched trades: {len(trades)} trades")
        if len(trades) > 0:
            print(f"📈 First trade: {trades.iloc[0]['Entry Date']} -> {trades.iloc[0]['Net PnL']:.2f}")
            print(f"📈 Last trade: {trades.iloc[-1]['Entry Date']} -> {trades.iloc[-1]['Net PnL']:.2f}")

if __name__ == "__main__":
    test_equity_in_result()
