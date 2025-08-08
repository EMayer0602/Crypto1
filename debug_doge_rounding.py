#!/usr/bin/env python3
"""
Debug the DOGE rounding issue
"""

def test_doge_rounding():
    # DOGE-EUR case
    capital = 2000
    entry_price = 100.0
    round_factor = 1000.0
    
    raw_quantity = capital / entry_price
    expected_quantity = round(raw_quantity / round_factor) * round_factor
    
    print(f"DOGE-EUR Debug:")
    print(f"Capital: {capital}")
    print(f"Entry price: {entry_price}")
    print(f"Round factor: {round_factor}")
    print(f"Raw quantity: {raw_quantity}")
    print(f"Raw quantity / round_factor: {raw_quantity / round_factor}")
    print(f"Round(raw_quantity / round_factor): {round(raw_quantity / round_factor)}")
    print(f"Expected quantity: {expected_quantity}")

def test_xrp_rounding():
    # XRP-EUR case
    capital = 1000
    entry_price = 100.0
    round_factor = 100.0
    
    raw_quantity = capital / entry_price
    expected_quantity = round(raw_quantity / round_factor) * round_factor
    
    print(f"\nXRP-EUR Debug:")
    print(f"Capital: {capital}")
    print(f"Entry price: {entry_price}")
    print(f"Round factor: {round_factor}")
    print(f"Raw quantity: {raw_quantity}")
    print(f"Raw quantity / round_factor: {raw_quantity / round_factor}")
    print(f"Round(raw_quantity / round_factor): {round(raw_quantity / round_factor)}")
    print(f"Expected quantity: {expected_quantity}")

if __name__ == "__main__":
    test_doge_rounding()
    test_xrp_rounding()
