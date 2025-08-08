#!/usr/bin/env python3
"""
Debug the quantity rounding calculation
"""

def test_rounding():
    # BTC-EUR case
    capital = 5000
    entry_price = 100.0
    round_factor = 0.001
    
    raw_quantity = capital / entry_price
    expected_quantity = round(raw_quantity / round_factor) * round_factor
    
    print(f"Capital: {capital}")
    print(f"Entry price: {entry_price}")
    print(f"Round factor: {round_factor}")
    print(f"Raw quantity: {raw_quantity}")
    print(f"Raw quantity / round_factor: {raw_quantity / round_factor}")
    print(f"Round(raw_quantity / round_factor): {round(raw_quantity / round_factor)}")
    print(f"Expected quantity: {expected_quantity}")
    
    # Test if it's a multiple
    remainder = expected_quantity % round_factor
    print(f"Remainder: {remainder}")
    print(f"Is multiple? {abs(remainder) < 1e-10}")

if __name__ == "__main__":
    test_rounding()
