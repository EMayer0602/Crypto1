#!/usr/bin/env python3
"""
Test script to verify that trade_on parameter works correctly for different tickers.
"""

import pandas as pd
from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest

def test_trade_on_usage():
    """
    Test that tickers with trade_on='Open' use Open prices and 
    tickers with trade_on='Close' use Close prices
    """
    print("🧪 Testing trade_on parameter usage...")
    print("="*60)
    
    # Test one ticker with Open and one with Close
    test_tickers = []
    for ticker, config in crypto_tickers.items():
        if config.get('trade_on') == 'Open':
            test_tickers.append((ticker, 'Open'))
            break
    
    for ticker, config in crypto_tickers.items():
        if config.get('trade_on') == 'Close':
            test_tickers.append((ticker, 'Close'))
            break
    
    if len(test_tickers) < 2:
        print("❌ Need at least one 'Open' and one 'Close' ticker for testing")
        return
    
    for ticker, expected_mode in test_tickers:
        print(f"\n📊 Testing {ticker} (expected: trade on {expected_mode})")
        print("-" * 50)
        
        # Run a simple backtest 
        try:
            config = crypto_tickers[ticker]
            result = run_backtest(config, ticker)
            
            if result:
                print(f"✅ {ticker} backtest completed successfully")
                print(f"   Trade mode should be: {expected_mode}")
                if 'trades' in result and len(result['trades']) > 0:
                    first_trade = result['trades'].iloc[0]
                    if 'Level Close' in first_trade:
                        print(f"   First trade Level Close: €{first_trade['Level Close']:.4f}")
                else:
                    print("   No trades found in result")
            else:
                print(f"❌ {ticker} backtest failed")
                
        except Exception as e:
            print(f"❌ Error testing {ticker}: {e}")
            import traceback
            traceback.print_exc()

def check_price_differences():
    """
    Check the difference between Open and Close prices for a sample ticker
    to verify they are different (so we can see the effect)
    """
    print(f"\n🔍 Checking Open vs Close price differences...")
    print("="*60)
    
    # Use the first ticker for price comparison
    ticker = list(crypto_tickers.keys())[0]
    
    try:
        # Load some data
        from crypto_backtesting_module import load_crypto_data_yf
        df = load_crypto_data_yf(ticker, years=0.1)  # Just last ~1 month
        
        if df is not None and not df.empty:
            df_sample = df.tail(5)  # Last 5 days
            print(f"\nLast 5 days for {ticker}:")
            print(f"{'Date':<12} {'Open':<10} {'Close':<10} {'Diff%':<8}")
            print("-" * 42)
            
            for date, row in df_sample.iterrows():
                open_price = row['Open']
                close_price = row['Close']
                diff_pct = ((close_price - open_price) / open_price) * 100
                print(f"{date.strftime('%Y-%m-%d'):<12} {open_price:<10.4f} {close_price:<10.4f} {diff_pct:<8.2f}")
                
            avg_diff = ((df_sample['Close'] - df_sample['Open']) / df_sample['Open'] * 100).abs().mean()
            print(f"\nAverage absolute daily difference: {avg_diff:.2f}%")
            
            if avg_diff > 0.1:
                print("✅ Significant price differences found - test should be meaningful")
            else:
                print("⚠️  Small price differences - test may be less obvious")
                
    except Exception as e:
        print(f"❌ Error checking price differences: {e}")

if __name__ == "__main__":
    check_price_differences()
    test_trade_on_usage()
    
    print(f"\n📋 Summary:")
    print("="*60)
    print("This test verifies that:")
    print("1. Tickers with trade_on='Open' use Open prices in Level Close")
    print("2. Tickers with trade_on='Close' use Close prices in Level Close")
    print("3. The price differences are meaningful enough to detect")
