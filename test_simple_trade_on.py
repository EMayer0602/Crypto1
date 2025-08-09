#!/usr/bin/env python3
"""
Simple test to verify trade_on parameter works
"""

import pandas as pd
import numpy as np
from crypto_tickers import crypto_tickers

# Create test data
dates = pd.date_range('2024-01-01', periods=5, freq='D')
test_df = pd.DataFrame({
    'Open': [100.0, 102.0, 104.0, 103.0, 105.0],
    'Close': [101.5, 103.2, 102.8, 104.1, 106.3],
    'High': [102.0, 104.0, 105.0, 105.0, 107.0],
    'Low': [99.5, 101.5, 102.0, 102.5, 104.5],
    'Volume': [1000, 1100, 950, 1200, 1050]
}, index=dates)

print("📊 Test Data:")
print(test_df[['Open', 'Close']])
print()

# Test with trade_on='Open'
print("🔍 Testing with trade_on='Open':")
try:
    from signal_utils import assign_long_signals_extended, calculate_support_resistance
    
    # Create simple support/resistance
    supp_data = pd.DataFrame({
        'date': [dates[0], dates[2]], 
        'level': [99.0, 102.0],
        'base_action': ['buy', 'sell']
    })
    res_data = pd.DataFrame({
        'date': [dates[1], dates[3]], 
        'level': [104.0, 105.0],
        'base_action': ['sell', 'buy']
    })
    
    # Test with Open
    ext_open = assign_long_signals_extended(supp_data, res_data, test_df, 1, "1d", "Open")
    print("Level Close values (should be Open prices):")
    if 'Level Close' in ext_open.columns:
        print(ext_open[['Long Date detected', 'Level Close', 'Action']].to_string())
    
    print()
    
    # Test with Close  
    print("🔍 Testing with trade_on='Close':")
    ext_close = assign_long_signals_extended(supp_data, res_data, test_df, 1, "1d", "Close")
    print("Level Close values (should be Close prices):")
    if 'Level Close' in ext_close.columns:
        print(ext_close[['Long Date detected', 'Level Close', 'Action']].to_string())
    
    print()
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
