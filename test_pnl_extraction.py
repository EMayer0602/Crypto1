#!/usr/bin/env python3
"""
Quick test to verify PnL extraction from Trade Statistics
"""

import sys
sys.path.append('.')

from crypto_backtesting_module import run_backtest
import config
from crypto_tickers import crypto_tickers

def test_pnl_extraction():
    """Test PnL extraction from trade statistics"""
    print("🧪 Testing PnL extraction from Trade Statistics")
    print("="*60)
    
    # Test with BTC
    symbol = 'BTC-EUR'
    ticker_config = crypto_tickers.get(symbol, {})
    cfg = {
        'commission_rate': config.COMMISSION_RATE,
        'min_commission': config.MIN_COMMISSION,
        'initial_capital': ticker_config.get('initialCapitalLong', 10000),
        'order_round_factor': ticker_config.get('order_round_factor', 0.01)
    }
    
    print(f"📊 Running backtest for {symbol}...")
    result = run_backtest(symbol, cfg)
    
    if result and 'trade_statistics' in result:
        stats = result['trade_statistics']
        print(f"\n📈 Trade Statistics Keys: {list(stats.keys())}")
        
        # Check for Total Return
        if '📊 Total Return' in stats:
            total_return_str = stats['📊 Total Return']
            print(f"✅ Total Return found: {total_return_str} (type: {type(total_return_str)})")
            
            # Extract percentage
            if isinstance(total_return_str, str) and total_return_str.endswith('%'):
                pnl_perc = float(total_return_str.replace('%', ''))
                print(f"💰 Extracted PnL percentage: {pnl_perc}%")
            else:
                print(f"⚠️ Unexpected format: {total_return_str}")
        else:
            print("❌ No '📊 Total Return' found in trade statistics")
            
        # Show all relevant statistics
        print(f"\n📊 All Statistics:")
        for key, value in stats.items():
            if 'return' in key.lower() or 'pnl' in key.lower() or '%' in str(value):
                print(f"   {key}: {value}")
    else:
        print("❌ No trade statistics found")

if __name__ == "__main__":
    test_pnl_extraction()
