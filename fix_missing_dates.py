#!/usr/bin/env python3
"""Fix missing dates 05.08 and 06.08 in BTC-EUR CSV"""

import pandas as pd
import numpy as np

def fix_missing_dates():
    print('=== Fixing Missing Dates in BTC-EUR CSV ===')
    
    # Load CSV
    df = pd.read_csv('BTC-EUR_daily.csv', index_col=0, parse_dates=True)
    print(f'Before: {len(df)} rows')
    print(f'Range: {df.index.min()} to {df.index.max()}')
    
    # Create missing dates
    missing_dates = pd.date_range(start='2025-08-05', end='2025-08-06', freq='D', tz='UTC')
    print(f'Missing dates: {list(missing_dates)}')
    
    # Get reference values (interpolate between 08-04 and 08-07)
    price_04 = df.loc[pd.Timestamp('2025-08-04', tz='UTC'), 'Close']
    price_07 = df.loc[pd.Timestamp('2025-08-07', tz='UTC'), 'Close']
    print(f'Price 08-04: {price_04}')
    print(f'Price 08-07: {price_07}')
    
    # Create missing rows with interpolated values
    for i, date in enumerate(missing_dates):
        ratio = (i + 1) / (len(missing_dates) + 1)
        interpolated_price = price_04 + (price_07 - price_04) * ratio
        
        new_row = df.loc[pd.Timestamp('2025-08-04', tz='UTC')].copy()
        new_row['Close'] = interpolated_price
        new_row['High'] = interpolated_price * 1.01
        new_row['Low'] = interpolated_price * 0.99  
        new_row['Open'] = interpolated_price
        new_row['Volume'] = -1000  # Marker für artificial
        
        df.loc[date] = new_row
        print(f'Added {date.date()}: Close={interpolated_price:.2f}')
    
    # Sort by date
    df = df.sort_index()
    
    # Save updated CSV
    df.to_csv('BTC-EUR_daily.csv')
    print(f'After: {len(df)} rows')
    print('CSV updated successfully!')
    
    # Verify the fix
    recent = df.tail(8)
    print('\n=== Last 8 days after fix ===')
    print(recent[['Close', 'Volume']].to_string())

if __name__ == "__main__":
    fix_missing_dates()
