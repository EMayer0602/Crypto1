#!/usr/bin/env python3
"""
Quick test to see what prices are actually being used in trades
"""

from crypto_backtesting_module import run_backtest  
from crypto_tickers import crypto_tickers

def check_actual_prices_used():
    """Check which prices are actually being used"""
    
    print("🔍 CHECKING ACTUAL PRICES USED IN TRADES")
    print("="*50)
    
    # Test with one Open ticker and one Close ticker
    test_tickers = ["BTC-EUR", "ETH-EUR"]  # Open vs Close
    
    for symbol in test_tickers:
        config = crypto_tickers[symbol]
        print(f"\n📊 Testing {symbol}:")
        print(f"   Config: trade_on = '{config['trade_on']}'")
        
        try:
            result = run_backtest(symbol, config)
            
            if 'extended_trades' in result and not result['extended_trades'].empty:
                ext_trades = result['extended_trades']
                
                print(f"   📈 Found {len(ext_trades)} extended trades")
                
                # Show first few trades with their Level Close values
                for idx, trade in ext_trades.head(3).iterrows():
                    date = trade.get('Long Date detected', 'N/A')
                    action = trade.get('Action', 'N/A')
                    level_close = trade.get('Level Close', 0)
                    
                    print(f"   Trade {idx+1}: {date} | {action} | Level Close: €{level_close:.4f}")
                    
                # Check if the Level Close values match Open or Close prices
                # by comparing with the actual data
                print(f"   💡 Expected: {'Open' if config['trade_on'] == 'Open' else 'Close'} prices")
                
            else:
                print(f"   ❌ No extended trades found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    check_actual_prices_used()
