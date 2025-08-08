#!/usr/bin/env python3

import sys
import os
sys.path.append(os.getcwd())

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def test_equity_fix():
    """Test der korrigierten Equity Curve mit richtigen Initial Capital Werten"""
    print("🧪 Testing corrected equity curve with proper initial capital...")
    
    # Test mit BTC-EUR
    symbol = "BTC-EUR"
    config = crypto_tickers[symbol]
    
    print(f"\n📊 Testing {symbol}:")
    print(f"   💰 Expected Initial Capital: €{config['initialCapitalLong']}")
    print(f"   🔧 Order Round Factor: {config['order_round_factor']}")
    
    # Run backtest
    result = run_backtest(symbol, config)
    
    if result and isinstance(result, dict):
        print(f"\n✅ BACKTEST SUCCESSFUL!")
        
        # Check config in result
        result_config = result.get('config', {})
        print(f"   🔧 Config keys in result: {list(result_config.keys())}")
        print(f"   💰 initialCapitalLong in config: {result_config.get('initialCapitalLong', 'MISSING')}")
        
        # Check equity curve
        equity_curve = result.get('equity_curve', [])
        if equity_curve:
            print(f"   📈 Equity Curve Length: {len(equity_curve)}")
            print(f"   💰 Start Capital: €{equity_curve[0]:.2f}")
            print(f"   🎯 Expected Start: €{config['initialCapitalLong']}")
            print(f"   📊 End Capital: €{equity_curve[-1]:.2f}")
            
            # Check if start matches expected
            if abs(equity_curve[0] - config['initialCapitalLong']) < 0.01:
                print("   ✅ START CAPITAL CORRECT!")
            else:
                print("   ❌ START CAPITAL MISMATCH!")
                print(f"   🔍 Difference: {equity_curve[0] - config['initialCapitalLong']:.2f}")
            
            # Check variation
            unique_values = len(set([round(v, 0) for v in equity_curve]))
            print(f"   📊 Unique Values: {unique_values}")
            
            if unique_values > 10:
                print("   ✅ EQUITY CURVE VARIES CORRECTLY!")
            else:
                print("   ⚠️ Limited variation in equity curve")
                print(f"   📊 Sample values: {[f'€{v:.0f}' for v in equity_curve[:10]]}")
                
        # Check final capital
        final_capital = result.get('final_capital', 0)
        print(f"   💼 Final Capital: €{final_capital:.2f}")
        
        # Check trade stats
        trade_stats = result.get('trade_statistics', {})
        total_return = trade_stats.get('📊 Total Return', '0%')
        print(f"   📊 Total Return: {total_return}")
        
        return True
    else:
        print("   ❌ BACKTEST FAILED!")
        return False

if __name__ == "__main__":
    test_equity_fix()
