#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from crypto_backtesting_module import capture_trades_output, simulate_matched_trades

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

# Test open trade info
open_trade_info = {
    'buy_date': '2024-01-20',
    'buy_price': 130.0,
    'shares': 7.0
}

print("=== Test: Net PnL vs Gross PnL in Open Position Handling ===")
print()
print("Matched trades (completed):")
print(test_matched_trades[['Entry Date', 'Exit Date', 'PnL', 'Net PnL', 'Commission', 'Status']].to_string())
print()

# Test with initial capital from config
initial_capital = 10000.0

print(f"Initial Capital: €{initial_capital:.2f}")
print(f"Total Gross PnL: €{test_matched_trades['PnL'].sum():.2f}")
print(f"Total Net PnL: €{test_matched_trades['Net PnL'].sum():.2f}")
print(f"Total Fees: €{test_matched_trades['Commission'].sum():.2f}")
print()

# Test the capture_trades_output function
trades_output = capture_trades_output(test_matched_trades, open_trade_info, initial_capital)

print("=== Trades Output (should use Net PnL for capital calculation) ===")
print(trades_output)
print()

# Extract capital values from output
lines = trades_output.strip().split('\n')
capital_lines = [line for line in lines if 'Capital=' in line]

print("=== Capital Values Used ===")
for line in capital_lines:
    print(line)

print()
print("=== Expected Behavior ===")
print("1. First trade should start with €10000.00")
print("2. Second trade should start with €10000.00 + €95.00 = €10095.00")
print("3. Open position should start with €10000.00 + €95.00 + (-€44.00) = €10051.00")
print()
print("If these values match the Capital values above, then Net PnL is being used correctly!")
