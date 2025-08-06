#!/usr/bin/env python3
"""
🔍 SIGNAL TIMEZONE DEBUG
"""

import pandas as pd
from signal_utils import calculate_support_resistance, assign_long_signals_extended

print("🔍 SIGNAL TIMEZONE DEBUG")
print("="*40)

# Lade Daten
df = pd.read_csv('BTC-EUR_minute.csv', parse_dates=['DateTime'])
df.set_index('DateTime', inplace=True)

print(f"df.index timezone: {df.index.tz}")

# Erstelle Signale
support, resistance = calculate_support_resistance(df, 7, 3, verbose=False)
signal_df = assign_long_signals_extended(support, resistance, df, 3, "1d")

print(f"Signal DataFrame Spalten: {list(signal_df.columns)}")

if 'Long Date detected' in signal_df.columns:
    print(f"\nLong Date detected Analyse:")
    for i in range(min(3, len(signal_df))):
        date_val = signal_df.iloc[i]['Long Date detected']
        print(f"  {i}: {date_val}")
        print(f"     Type: {type(date_val)}")
        if hasattr(date_val, 'tz'):
            print(f"     Timezone: {date_val.tz}")
        print(f"     In df.index: {date_val in df.index if pd.notna(date_val) else 'NaN'}")

print("\n" + "="*40)
print("🔍 DEBUG Ende")
