#!/usr/bin/env python3
"""Check the correct column names in extended trades"""

from crypto_backtesting_module import load_crypto_data_yf
from signal_utils import calculate_support_resistance, assign_long_signals_extended
import pandas as pd

def check_extended_trades_columns():
    print('=== Checking Extended Trades Column Names ===')
    
    # Load BTC-EUR data
    df = load_crypto_data_yf('BTC-EUR', 1)
    if df is None or df.empty:
        print('❌ Failed to load data')
        return
    
    print(f'✅ Data loaded: {len(df)} rows')
    
    # Generate signals with one specific combination
    past_window = 5
    tw = 2
    
    # Calculate support/resistance
    support, resistance = calculate_support_resistance(df, past_window, tw, verbose=False)
    print(f'Support levels: {len(support)}')
    print(f'Resistance levels: {len(resistance)}')
    
    # Generate extended signals
    signal_df = assign_long_signals_extended(support, resistance, df, tw, "1d")
    
    print(f'\n=== Extended Trades DataFrame Info ===')
    print(f'Shape: {signal_df.shape}')
    print(f'Columns: {list(signal_df.columns)}')
    
    print(f'\n=== Sample of Extended Trades ===')
    print(signal_df.head(3))

if __name__ == "__main__":
    check_extended_trades_columns()
