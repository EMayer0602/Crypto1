#!/usr/bin/env python3
"""Debug Trade Simulation"""

from crypto_backtesting_module import load_crypto_data_yf
from signal_utils import calculate_support_resistance, assign_long_signals_extended, simulate_trades_compound_extended
from config import COMMISSION_RATE, MIN_COMMISSION
from crypto_tickers import crypto_tickers
import pandas as pd

def debug_trades():
    print('=== Debug Trade Simulation ===')
    
    # Load data
    df = load_crypto_data_yf('BTC-EUR', 1)
    if df is None or df.empty:
        print('❌ Failed to load data')
        return
    
    print(f'✅ Data loaded: {len(df)} rows')
    
    # Configuration
    ticker_config = crypto_tickers.get('BTC-EUR', {})
    cfg = {
        'initial_capital': ticker_config.get('initialCapitalLong', 5000),
        'commission_rate': COMMISSION_RATE,
        'min_commission': MIN_COMMISSION,
        'order_round_factor': ticker_config.get('order_round_factor', 0.01)
    }
    
    print(f'Config: {cfg}')
    
    # Test with specific parameters
    past_window = 5
    tw = 2
    
    print(f'\n=== Testing with past_window={past_window}, tw={tw} ===')
    
    # Calculate support/resistance
    support, resistance = calculate_support_resistance(df, past_window, tw, verbose=True)
    
    # Generate signals
    signal_df = assign_long_signals_extended(support, resistance, df, tw, "1d")
    
    print(f'\n=== Signal DataFrame ===')
    print(f'Shape: {signal_df.shape}')
    if not signal_df.empty:
        print('Sample signals:')
        print(signal_df[['Date high/low', 'Action', 'Level Close']].head(10))
        
        print(f'\nAction counts:')
        print(signal_df['Action'].value_counts())
        
        # Simulate trades
        print(f'\n=== Simulating Trades ===')
        final_capital, trades_df = simulate_trades_compound_extended(
            signal_df,
            cfg['initial_capital'],
            cfg['commission_rate'],
            cfg['min_commission'],
            cfg['order_round_factor'],
            df
        )
        
        print(f'Final capital: {final_capital}')
        print(f'Initial capital: {cfg["initial_capital"]}')
        print(f'Profit: {final_capital - cfg["initial_capital"]}')
        
        if not trades_df.empty:
            print(f'\nTrades executed: {len(trades_df)}')
            print(trades_df)
        else:
            print('❌ No trades executed!')
    else:
        print('❌ No signals generated!')

if __name__ == "__main__":
    debug_trades()
