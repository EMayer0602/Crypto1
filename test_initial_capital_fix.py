#!/usr/bin/env python3
"""
Test script to verify that initial capital and order round factor are working correctly
"""

import pandas as pd
from crypto_tickers import crypto_tickers
from crypto_backtesting_module import simulate_matched_trades

def test_initial_capital_and_round_factor():
    """Test that initial capital comes from crypto_tickers and shares are rounded correctly"""
    
    print("🧪 Testing Initial Capital and Order Round Factor...")
    
    # Test data for different tickers
    test_cases = [
        ("BTC-EUR", 5000, 0.001),   # BTC: 5000 capital, 0.001 round factor
        ("DOGE-EUR", 2000, 1000.0), # DOGE: 2000 capital, 1000.0 round factor
        ("XRP-EUR", 1000, 100.0),   # XRP: 1000 capital, 100.0 round factor
    ]
    
    # Create simple test ext_full data
    test_ext_full = pd.DataFrame([
        {
            'Action': 'buy',
            'Long Date detected': '2024-01-01',
            'Level Close': 100.0
        },
        {
            'Action': 'sell', 
            'Long Date detected': '2024-01-02',
            'Level Close': 110.0
        }
    ])
    
    for ticker, expected_capital, expected_round_factor in test_cases:
        print(f"\n📊 Testing {ticker}:")
        print(f"   Expected Capital: €{expected_capital}")
        print(f"   Expected Round Factor: {expected_round_factor}")
        
        # Get config from crypto_tickers
        config = crypto_tickers[ticker]
        actual_capital = config['initialCapitalLong']
        actual_round_factor = config['order_round_factor']
        
        print(f"   Actual Capital: €{actual_capital}")
        print(f"   Actual Round Factor: {actual_round_factor}")
        
        # Verify config values
        assert actual_capital == expected_capital, f"Capital mismatch for {ticker}: expected {expected_capital}, got {actual_capital}"
        assert actual_round_factor == expected_round_factor, f"Round factor mismatch for {ticker}: expected {expected_round_factor}, got {actual_round_factor}"
        
        # Test simulate_matched_trades with these values
        commission_rate = 0.001
        matched_trades = simulate_matched_trades(
            test_ext_full, 
            actual_capital, 
            commission_rate, 
            order_round_factor=actual_round_factor
        )
        
        if not matched_trades.empty:
            quantity = matched_trades.iloc[0]['Quantity']
            raw_quantity = actual_capital / 100.0  # entry price is 100
            expected_quantity = round(raw_quantity / actual_round_factor) * actual_round_factor
            
            print(f"   Raw Quantity: {raw_quantity:.6f}")
            print(f"   Expected Rounded Quantity: {expected_quantity:.6f}")
            print(f"   Actual Quantity: {quantity:.6f}")
            
            # Verify quantity is properly rounded
            assert abs(quantity - expected_quantity) < 0.000001, f"Quantity rounding error for {ticker}: expected {expected_quantity}, got {quantity}"
            
            # Verify quantity is a multiple of round factor (allow for floating point precision)
            # Check if the quantity can be divided by round_factor to get a whole number
            quotient = quantity / actual_round_factor
            remainder_from_quotient = abs(quotient - round(quotient))
            assert remainder_from_quotient < 1e-10, f"Quantity {quantity} is not a multiple of round factor {actual_round_factor} for {ticker} (quotient: {quotient}, remainder: {remainder_from_quotient})"
            
            print(f"   ✅ {ticker} passed all tests!")
        else:
            print(f"   ❌ No matched trades generated for {ticker}")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_initial_capital_and_round_factor()
