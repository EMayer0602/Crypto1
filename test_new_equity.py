#!/usr/bin/env python3
"""
Test the NEW CORRECTED create_equity_curve_from_matched_trades function
"""

import pandas as pd
import numpy as np
from plotly_utils import create_equity_curve_from_matched_trades

def test_new_equity_function():
    print("🧪 Testing the NEW CORRECTED Equity Function")
    print("=" * 60)
    
    # Simulate price data for 10 days
    dates = pd.date_range('2024-08-01', periods=10, freq='D')
    np.random.seed(42)
    
    # Create realistic price data
    initial_price = 100.0
    price_changes = np.random.normal(0, 2, 10)  # Daily changes
    prices = [initial_price]
    
    for change in price_changes[1:]:
        new_price = max(prices[-1] + change, 50)  # Minimum €50
        prices.append(new_price)
    
    df = pd.DataFrame({
        'Open': prices,
        'Close': [p + np.random.normal(0, 0.5) for p in prices]  # Small intraday moves
    }, index=dates)
    
    print(f"📊 Price Data (10 days):")
    for i, (date, row) in enumerate(df.iterrows()):
        print(f"   Day {i+1} {date.date()}: Open €{row['Open']:.2f}, Close €{row['Close']:.2f}")
    
    # Create trade data: BUY day 2, SELL day 8
    buy_date = dates[1]
    sell_date = dates[7]
    shares = 10.0
    buy_price = df.loc[buy_date, 'Open']
    sell_price = df.loc[sell_date, 'Open']
    
    # Calculate theoretical P&L and fees
    gross_pnl = shares * (sell_price - buy_price)
    fees = 5.0  # €5 total fees
    net_pnl = gross_pnl - fees
    
    matched_trades = [{
        'buy_date': buy_date.strftime('%Y-%m-%d'),
        'sell_date': sell_date.strftime('%Y-%m-%d'),
        'buy_price': buy_price,
        'sell_price': sell_price,
        'shares': shares,
        'pnl': net_pnl,
        'is_open': False
    }]
    
    print(f"\n📈 Trade Details:")
    print(f"   BUY:  {buy_date.date()} @ €{buy_price:.2f} for {shares} shares")
    print(f"   SELL: {sell_date.date()} @ €{sell_price:.2f}")
    print(f"   Gross P&L: €{gross_pnl:.2f}")
    print(f"   Fees: €{fees:.2f}")
    print(f"   Net P&L: €{net_pnl:.2f}")
    
    # Test the function
    initial_capital = 1000.0
    print(f"\n🎯 Testing with Initial Capital: €{initial_capital}")
    
    equity_curve = create_equity_curve_from_matched_trades(matched_trades, initial_capital, df)
    
    print(f"\n📊 Equity Results:")
    for i, (date, equity) in enumerate(zip(df.index, equity_curve)):
        print(f"   Day {i+1} {date.date()}: €{equity:.2f}")
    
    # Validate expectations
    print(f"\n✅ Validation:")
    print(f"   Start Capital: €{equity_curve[0]:.2f} (should be ~€{initial_capital})")
    print(f"   Final Capital: €{equity_curve[-1]:.2f}")
    
    # Check for daily variations during long position
    long_period = equity_curve[2:7]  # Days 3-7 (during long position)
    unique_values = len(set([int(v) for v in long_period]))
    print(f"   Daily variations during Long (days 3-7): {unique_values} unique values")
    
    if unique_values >= 4:
        print("   ✅ Equity varies DAILY during long position!")
    else:
        print("   ❌ Equity not varying enough during long")
    
    return equity_curve

if __name__ == "__main__":
    test_new_equity_function()
