#!/usr/bin/env python3
"""
Create a NEW chart for BTC to test the CORRECTED daily equity
"""

print("🎯 Creating NEW BTC Chart with DAILY EQUITY...")

try:
    import pandas as pd
    
    # Load BTC data
    df = pd.read_csv("BTC-EUR_daily.csv", index_col=0, parse_dates=True)
    print(f"📊 Loaded {len(df)} days of BTC data")
    
    # Create dummy trades for testing
    from datetime import datetime, timedelta
    import numpy as np
    
    # Get recent dates from the data
    recent_dates = df.tail(30).index
    
    # Create a simple test trade
    buy_date = recent_dates[5]
    sell_date = recent_dates[15]
    
    buy_price = df.loc[buy_date, 'Close']
    sell_price = df.loc[sell_date, 'Close']
    shares = 0.1  # 0.1 BTC
    fees = 50.0  # €50 total fees
    pnl = shares * (sell_price - buy_price) - fees
    
    matched_trades = [{
        'buy_date': buy_date.strftime('%Y-%m-%d'),
        'sell_date': sell_date.strftime('%Y-%m-%d'),
        'buy_price': buy_price,
        'sell_price': sell_price,
        'shares': shares,
        'pnl': pnl,
        'is_open': False
    }]
    
    print(f"📈 Test Trade:")
    print(f"   BUY:  {buy_date.date()} @ €{buy_price:.2f}")
    print(f"   SELL: {sell_date.date()} @ €{sell_price:.2f}")
    print(f"   Shares: {shares}")
    print(f"   PnL: €{pnl:.2f}")
    
    # Create equity curve using NEW function
    from plotly_utils import create_equity_curve_from_matched_trades
    
    initial_capital = 10000
    equity_curve = create_equity_curve_from_matched_trades(matched_trades, initial_capital, df)
    
    print(f"\n📊 Equity Analysis:")
    print(f"   Length: {len(equity_curve)} days")
    print(f"   Start: €{equity_curve[0]:.0f}")
    print(f"   End: €{equity_curve[-1]:.0f}")
    
    # Check variation
    unique_vals = len(set([int(v/100)*100 for v in equity_curve]))
    print(f"   Unique values: {unique_vals}")
    
    # Create simple chart using built-in function  
    from plotly_utils import plotly_combined_chart_and_equity
    
    # Add dummy signals
    df['buy_signal'] = 0
    df['sell_signal'] = 0
    df.loc[buy_date, 'buy_signal'] = 1
    df.loc[sell_date, 'sell_signal'] = 1
    
    # Create buy&hold for comparison
    start_price = df['Close'].iloc[0]
    buyhold_curve = []
    for price in df['Close']:
        buyhold_curve.append(initial_capital * (price / start_price))
    
    print(f"\n🎨 Creating chart...")
    chart_file = plotly_combined_chart_and_equity(
        df=df,
        standard_signals=pd.DataFrame(),  # Empty signals
        support=pd.Series(dtype=float),
        resistance=pd.Series(dtype=float), 
        equity_curve=equity_curve,  # NEW DAILY EQUITY!
        buyhold_curve=buyhold_curve,
        ticker="BTC-EUR",
        backtest_years=1
    )
    
    if chart_file:
        print(f"✅ Chart created: {chart_file}")
        
        # Open in browser
        import webbrowser
        import os
        webbrowser.open(f'file://{os.path.abspath(chart_file)}')
        print("🎯 Chart opened with NEW DAILY EQUITY CURVE!")
    else:
        print("❌ Chart creation failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
