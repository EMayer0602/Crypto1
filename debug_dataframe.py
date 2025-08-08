#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

# Test data simulating matched trades with fees
test_matched_trades = pd.DataFrame([
    {
        'Entry Date': '2024-01-01',
        'Entry Price': 100.0,
        'Exit Date': '2024-01-05', 
        'Exit Price': 110.0,
        'Quantity': 10.0,
        'PnL': 100.0,  # Gross PnL: (110-100)*10 = 100
        'Commission': 5.0,  # Buy fee + Sell fee
        'Net PnL': 95.0,  # Net PnL: 100 - 5 = 95
        'Capital': 10095.0,
        'Status': 'CLOSED'
    },
    {
        'Entry Date': '2024-01-10',
        'Entry Price': 120.0,
        'Exit Date': '2024-01-15',
        'Exit Price': 115.0,
        'Quantity': 8.0,
        'PnL': -40.0,  # Gross PnL: (115-120)*8 = -40
        'Commission': 4.0,  # Buy fee + Sell fee
        'Net PnL': -44.0,  # Net PnL: -40 - 4 = -44
        'Capital': 10051.0,
        'Status': 'CLOSED'
    }
])

print("=== Debug: Test DataFrame ===")
print("Type:", type(test_matched_trades))
print("Shape:", test_matched_trades.shape)
print("Columns:", list(test_matched_trades.columns))
print()
print("DataFrame content:")
print(test_matched_trades)
print()

print("=== Converting to records ===")
trades_list = test_matched_trades.to_dict('records')
print("Type:", type(trades_list))
print("Length:", len(trades_list))
print("First item type:", type(trades_list[0]) if trades_list else "Empty")
print("First item:", trades_list[0] if trades_list else "Empty")
print()

print("=== Testing iteration ===")
for i, trade in enumerate(trades_list):
    print(f"Trade {i}: type={type(trade)}")
    if hasattr(trade, 'get'):
        buy_date = trade.get('Entry Date', 'N/A')
        print(f"  Entry Date: {buy_date}")
    else:
        print(f"  No .get() method available. Keys: {trade.keys() if hasattr(trade, 'keys') else 'No keys'}")
    if i >= 1:  # Only show first 2 trades
        break
