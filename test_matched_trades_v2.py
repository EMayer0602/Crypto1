#!/usr/bin/env python3
"""
Test der simulate_matched_trades Funktion
"""
import pandas as pd
from crypto_backtesting_module import simulate_matched_trades
from crypto_tickers import crypto_tickers

# Test mit einem Ticker
ticker = 'BTC-EUR'
config = crypto_tickers[ticker]
order_round_factor = config.get('order_round_factor', 1)
initial_capital = config.get('initialCapitalLong', 1000)
commission_rate = 0.001  # Standard commission rate

# Erstelle Test-Extended Trades als DataFrame
test_extended_trades = pd.DataFrame([
    {
        'Timestamp': '2025-08-03 10:00:00',
        'Symbol': 'BTC-EUR',
        'Action': 'buy',
        'shares': 0.101,
        'Level Close': 50000.0,
        'Index': 37
    },
    {
        'Timestamp': '2025-08-01 14:00:00',
        'Symbol': 'BTC-EUR',
        'Action': 'sell',
        'shares': 0.101,  # Should be same as previous BUY
        'Level Close': 52000.0,
        'Index': 35
    }
])

print(f"Testing simulate_matched_trades for {ticker}")
print(f"Order round factor: {order_round_factor}")
print(f"Initial capital: {initial_capital}")
print("\nInput extended trades:")
print(test_extended_trades)

# Test die Funktion
matched_trades = simulate_matched_trades(test_extended_trades, initial_capital, commission_rate, order_round_factor=order_round_factor)

print(f"\nOutput matched trades ({len(matched_trades)}):")
if len(matched_trades) > 0:
    print(matched_trades)
else:
    print("  No matched trades returned")

# Erstelle DataFrame zum Testen
if len(matched_trades) > 0:
    print(f"\nMatched trades DataFrame:")
    print(matched_trades)
    
    if 'Shares' in matched_trades.columns:
        print(f"\n✅ 'Shares' column is present!")
        print(f"Shares values: {matched_trades['Shares'].tolist()}")
    else:
        print(f"\n❌ 'Shares' column is missing!")
        print(f"Available columns: {list(matched_trades.columns)}")
else:
    print("\n❌ No matched trades returned!")
