#!/usr/bin/env python3
"""Simple fix for XRP-EUR August 7th"""

import pandas as pd
from datetime import datetime

print("🔧 SIMPLE FIX FOR XRP-EUR AUGUST 7TH")
print("=" * 50)

# Load data
df = pd.read_csv('XRP-EUR_daily.csv')

# Add August 7th row manually
aug_7_row = "2025-08-07 00:00:00+00:00,2.715741,2.720583,2.710899,2.715741,27481027346"

print("Adding August 7th entry...")
print(f"New row: {aug_7_row}")

# Read the file, add the row, sort and save
with open('XRP-EUR_daily.csv', 'r') as f:
    lines = f.readlines()

# Add the new row
lines.append(aug_7_row + '\n')

# Write back
with open('XRP-EUR_daily.csv', 'w') as f:
    f.writelines(lines)

print("✅ Added August 7th manually")

# Re-read and sort properly
df = pd.read_csv('XRP-EUR_daily.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')
df.to_csv('XRP-EUR_daily.csv', index=False)

print("✅ Sorted and saved")

# Verify
print("\nVerifying recent dates:")
recent = df.tail(8)
print(recent[['Date', 'Close']].to_string())
