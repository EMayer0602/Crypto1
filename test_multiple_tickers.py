#!/usr/bin/env python3
"""Test different tickers to see if they really have the same optimal parameters"""

from signal_utils import berechne_best_p_tw_long
from crypto_backtesting_module import load_crypto_data_yf
from crypto_tickers import crypto_tickers

def test_multiple_tickers():
    print('=== Testing Optimization for Multiple Tickers ===')
    
    cfg = {
        'initial_capital': 10000,
        'commission_rate': 0.0018,
        'min_commission': 1.0,
        'order_round_factor': 0.01
    }
    
    results = {}
    
    for ticker, ticker_info in list(crypto_tickers.items())[:3]:  # Test first 3 tickers
        print(f'\n--- Testing {ticker} ---')
        
        # Load data
        df = load_crypto_data_yf(ticker, 1)
        if df is None or df.empty:
            print(f'❌ Failed to load data for {ticker}')
            continue
        
        print(f'✅ Data loaded: {len(df)} rows')
        
        # Run optimization
        start_idx = 0
        end_idx = len(df)
        
        try:
            p, tw = berechne_best_p_tw_long(df, cfg, start_idx, end_idx, verbose=True, ticker=ticker)
            results[ticker] = {'past_window': p, 'trade_window': tw}
            print(f'✅ {ticker}: Past={p}, Trade={tw}')
        except Exception as e:
            print(f'❌ {ticker} optimization failed: {e}')
    
    print('\n=== SUMMARY ===')
    for ticker, params in results.items():
        print(f'{ticker}: Past={params["past_window"]}, Trade={params["trade_window"]}')
    
    # Check if all are the same
    if len(set((p['past_window'], p['trade_window']) for p in results.values())) == 1:
        print('\n⚠️  All tickers have the same optimal parameters!')
        print('   This might indicate:')
        print('   1. Limited optimization range')
        print('   2. Similar market patterns') 
        print('   3. Issue with optimization function')
    else:
        print('\n✅ Different optimal parameters found for different tickers')

if __name__ == "__main__":
    test_multiple_tickers()
