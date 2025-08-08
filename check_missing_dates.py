#!/usr/bin/env python3
"""Check for missing dates in BTC-EUR data"""

import pandas as pd
from datetime import datetime, timedelta

# Load BTC-EUR data
df = pd.read_csv('BTC-EUR_daily.csv')
df['Date'] = pd.to_datetime(df['Date'])

print("🔍 CHECKING FOR MISSING DATES")
print("=" * 50)

# Check August 2025 specifically
august_dates = []
start_date = datetime(2025, 8, 1)
end_date = datetime(2025, 8, 8)

current = start_date
while current <= end_date:
    august_dates.append(current.date())
    current += timedelta(days=1)

print("Expected August dates:", august_dates)
print()

# Check which dates exist in data
existing_august = []
missing_august = []

for target_date in august_dates:
    if any(df['Date'].dt.date == target_date):
        existing_august.append(target_date)
    else:
        missing_august.append(target_date)

print(f"✅ Existing dates: {len(existing_august)}")
for date in existing_august:
    print(f"   {date}")

print(f"\n❌ Missing dates: {len(missing_august)}")
for date in missing_august:
    print(f"   {date}")

# Show last few entries
print(f"\n📊 Last 5 entries in BTC-EUR data:")
print(df.tail(5)[['Date', 'Close', 'Volume']].to_string())
