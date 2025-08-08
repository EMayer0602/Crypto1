#!/usr/bin/env python3
"""Check XRP-EUR data status"""

import pandas as pd
from datetime import datetime

# Load XRP-EUR data
try:
    df = pd.read_csv('XRP-EUR_daily.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    print("🔍 XRP-EUR DATA STATUS")
    print("=" * 50)
    
    print(f"Total rows: {len(df)}")
    print(f"Date range: {df['Date'].iloc[0].date()} to {df['Date'].iloc[-1].date()}")
    
    print(f"\nLast 5 entries:")
    print(df.tail(5)[['Date', 'Close', 'Volume']].to_string())
    
    # Check for recent dates
    today = datetime.now().date()
    latest_date = df['Date'].iloc[-1].date()
    days_behind = (today - latest_date).days
    
    print(f"\nToday: {today}")
    print(f"Latest data: {latest_date}")
    print(f"Days behind: {days_behind}")
    
    if days_behind > 0:
        print(f"⚠️ XRP-EUR data is {days_behind} days behind!")
    else:
        print("✅ XRP-EUR data is up to date")
        
    # Check for August 2025 data
    august_data = df[df['Date'].dt.month == 8]
    if not august_data.empty:
        print(f"\nAugust 2025 data:")
        print(august_data[['Date', 'Close']].tail(10).to_string())
    else:
        print("\n❌ No August 2025 data found")
        
except FileNotFoundError:
    print("❌ XRP-EUR_daily.csv not found!")
except Exception as e:
    print(f"❌ Error: {e}")
