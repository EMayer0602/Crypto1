#!/usr/bin/env python3
"""Quick test of matched trades"""

import pandas as pd
from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

# Test one ticker
ticker = 'BTC-EUR'
config = crypto_tickers[ticker]
print(f"Testing {ticker}...")

result = run_backtest(ticker, config)
print('Result keys:', list(result.keys()) if result else 'None')

if result:
    matched_trades = result.get('matched_trades', pd.DataFrame())
    print('Matched trades shape:', matched_trades.shape)
    print('Matched trades columns:', list(matched_trades.columns) if not matched_trades.empty else 'Empty')
    
    if not matched_trades.empty:
        print('Sample data:')
        print(matched_trades.head())
    else:
        print('No matched trades found')
        
    # Check weekly trades data
    weekly_trades_data = result.get('weekly_trades_data', [])
    print(f'\nWeekly trades data: {len(weekly_trades_data)} trades')
    if weekly_trades_data:
        print('Sample weekly trade:', weekly_trades_data[0])
