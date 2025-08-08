#!/usr/bin/env python3
"""
Quick test to check if the NEW equity function is being used
"""

print("🎯 Testing NEW Daily Equity Function...")

# Test import
try:
    from plotly_utils import create_equity_curve_from_matched_trades
    print("✅ New equity function imported successfully")
    
    # Check if it's the new version
    import inspect
    source = inspect.getsource(create_equity_curve_from_matched_trades)
    if "TÄGLICHE Equity über ganz df" in source:
        print("✅ NEW CORRECTED function is loaded!")
    else:
        print("❌ OLD function still loaded")
        
    # Test with dummy data
    import pandas as pd
    import numpy as np
    
    # Create simple test data
    dates = pd.date_range('2024-08-01', periods=5, freq='D')
    df = pd.DataFrame({
        'Open': [100, 101, 102, 103, 104],
        'Close': [101, 102, 103, 104, 105]
    }, index=dates)
    
    # Simple trade: buy day 1, sell day 4
    trades = [{
        'buy_date': '2024-08-01',
        'sell_date': '2024-08-04',
        'buy_price': 100,
        'sell_price': 104,
        'shares': 10,
        'pnl': 35,  # 10 * (104-100) - 5 fees
        'is_open': False
    }]
    
    print("\n📊 Testing with 5 days, 1 trade...")
    equity = create_equity_curve_from_matched_trades(trades, 1000, df)
    
    print(f"✅ Equity curve computed: {len(equity)} values")
    for i, (date, eq) in enumerate(zip(df.index, equity)):
        print(f"   Day {i+1} {date.date()}: €{eq:.2f}")
    
    # Check variation
    unique_vals = len(set([int(v) for v in equity]))
    if unique_vals >= 4:
        print("✅ DAILY VARIATION CONFIRMED!")
    else:
        print("❌ Not enough daily variation")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Test complete!")
