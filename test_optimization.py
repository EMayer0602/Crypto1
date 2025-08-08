#!/usr/bin/env python3
"""Test script to debug parameter optimization"""

from crypto_backtesting_module import optimize_parameters, load_crypto_data_yf
from signal_utils import berechne_best_p_tw_long
import pandas as pd
import traceback

def test_optimization():
    print('=== Testing Parameter Optimization ===')
    
    # Test mit BTC-EUR
    print('\n1. Loading BTC-EUR data...')
    df = load_crypto_data_yf('BTC-EUR', 1)
    
    if df is None or df.empty:
        print('❌ Failed to load data')
        return
    
    print(f'✅ Data loaded: {len(df)} rows')
    print(f'   Date range: {df.index[0].date()} to {df.index[-1].date()}')
    
    # Test optimize_parameters function
    print('\n2. Testing optimize_parameters function...')
    try:
        result = optimize_parameters(df, 'BTC-EUR')
        print(f'✅ optimize_parameters result: {result}')
    except Exception as e:
        print(f'❌ optimize_parameters failed: {e}')
        traceback.print_exc()
        return
    
    # Test berechne_best_p_tw_long directly
    print('\n3. Testing berechne_best_p_tw_long directly...')
    try:
        # Lade ticker-spezifische Konfiguration
        from crypto_tickers import crypto_tickers
        from config import COMMISSION_RATE, MIN_COMMISSION
        
        ticker_config = crypto_tickers.get('BTC-EUR', {})
        
        cfg = {
            'initial_capital': ticker_config.get('initialCapitalLong', 5000),  # BTC-EUR default, not 10000
            'commission_rate': COMMISSION_RATE,
            'min_commission': MIN_COMMISSION,
            'order_round_factor': ticker_config.get('order_round_factor', 0.01)
        }
        
        start_idx = 0
        end_idx = len(df)
        
        print(f'   Config: {cfg}')
        print(f'   Data range: {start_idx} to {end_idx}')
        
        p, tw = berechne_best_p_tw_long(df, cfg, start_idx, end_idx, verbose=True, ticker='BTC-EUR')
        print(f'✅ Direct berechne_best_p_tw_long result: Past={p}, Trade={tw}')
        
    except Exception as e:
        print(f'❌ berechne_best_p_tw_long failed: {e}')
        traceback.print_exc()

if __name__ == "__main__":
    test_optimization()
