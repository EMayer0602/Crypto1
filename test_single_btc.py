#!/usr/bin/env python3
"""
Test the NEW DAILY EQUITY FUNCTION with BTC only
"""

from crypto_backtesting_module import run_backtest
import crypto_tickers as tickers

def test_single_btc():
    print("🎯 Testing BTC with NEW DAILY EQUITY FUNCTION")
    print("=" * 60)
    
    # Get BTC ticker
    btc_config = None
    for ticker in tickers.CRYPTO_TICKERS:
        if ticker['symbol'] == 'BTC-EUR':
            btc_config = ticker
            break
    
    if not btc_config:
        print("❌ BTC-EUR not found!")
        return
    
    print(f"📊 BTC Config:")
    print(f"   Symbol: {btc_config['symbol']}")
    print(f"   Initial Capital: €{btc_config['initial_capital']}")
    print(f"   Order Round Factor: {btc_config['order_round_factor']}")
    
    # Run backtest
    try:
        print(f"\n🚀 Running backtest...")
        result = run_backtest(
            symbol=btc_config['symbol'],
            past_window=5,
            trade_window=2,
            initial_capital=btc_config['initial_capital'],
            order_round_factor=btc_config['order_round_factor'],
            max_position_size=btc_config['max_position_size']
        )
        
        if result:
            print(f"✅ Backtest complete!")
            print(f"   Final Capital: €{result.get('final_capital', 0):.2f}")
            print(f"   PnL: €{result.get('pnl', 0):.2f}")
            
            matched_trades = result.get('matched_trades', [])
            print(f"   Trades: {len(matched_trades)}")
            
            # Check if new equity function was used
            if 'equity_curve' in result:
                equity = result['equity_curve']
                print(f"\n📊 Equity Curve Analysis:")
                print(f"   Length: {len(equity)} values")
                print(f"   Start: €{equity[0]:.0f}")
                print(f"   End: €{equity[-1]:.0f}")
                
                # Check daily variation
                unique_values = len(set([int(v/10)*10 for v in equity]))
                print(f"   Unique values: {unique_values}")
                
                if unique_values > 50:
                    print("   ✅ NEW DAILY EQUITY FUNCTION WORKING!")
                elif unique_values > 10:
                    print("   ⚠️ Some daily variation")
                else:
                    print("   ❌ Still using old flat curve")
            
        else:
            print("❌ Backtest failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_single_btc()
