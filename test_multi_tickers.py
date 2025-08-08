#!/usr/bin/env python3
"""Test parameter optimization for multiple tickers with correct values"""

from crypto_backtesting_module import optimize_parameters, load_crypto_data_yf
from crypto_tickers import crypto_tickers
import pandas as pd

def test_multiple_tickers():
    print('=== Testing Parameter Optimization for Multiple Tickers ===')
    
    # Test nur die ersten 3 Ticker
    test_tickers = list(crypto_tickers.keys())[:3]
    
    results = {}
    
    for ticker in test_tickers:
        print(f'\n{"="*60}')
        print(f'🔍 Testing {ticker}')
        print(f'{"="*60}')
        
        # Load data
        df = load_crypto_data_yf(ticker, 1)
        if df is None or df.empty:
            print(f'❌ Failed to load data for {ticker}')
            continue
            
        print(f'✅ Data loaded: {len(df)} rows')
        
        # Get ticker-specific config
        ticker_config = crypto_tickers[ticker]
        print(f'📊 Ticker config: Initial Capital = €{ticker_config["initialCapitalLong"]}, Round Factor = {ticker_config["order_round_factor"]}')
        
        # Run optimization
        try:
            result = optimize_parameters(df, ticker)
            results[ticker] = result
            print(f'✅ Optimization complete for {ticker}')
        except Exception as e:
            print(f'❌ Optimization failed for {ticker}: {e}')
    
    # Summary
    print(f'\n{"="*80}')
    print('📊 SUMMARY - Optimal Parameters by Ticker')
    print(f'{"="*80}')
    print(f'{"Ticker":<12} {"Initial Cap":<12} {"Past Window":<12} {"Trade Window":<12} {"Method":<12}')
    print('-' * 80)
    
    for ticker, result in results.items():
        ticker_config = crypto_tickers[ticker]
        initial_cap = ticker_config["initialCapitalLong"]
        past_w = result.get('optimal_past_window', 'N/A')
        trade_w = result.get('optimal_trade_window', 'N/A')
        method = result.get('method', 'N/A')
        print(f'{ticker:<12} €{initial_cap:<11} {past_w:<12} {trade_w:<12} {method:<12}')

if __name__ == "__main__":
    test_multiple_tickers()
