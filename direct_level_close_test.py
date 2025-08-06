#!/usr/bin/env python3
"""
🔍 DIRECT LEVEL CLOSE TEST
"""

import pandas as pd
import numpy as np
from signal_utils import assign_long_signals_extended, calculate_support_resistance

print("🔍 DIRECT LEVEL CLOSE TEST")
print("="*35)

# Lade Daten
df = pd.read_csv('BTC-EUR_minute.csv', parse_dates=['DateTime'])
df.set_index('DateTime', inplace=True)

print(f"df shape: {df.shape}")
print(f"df.index sample: {df.index[:3].tolist()}")
print(f"df.index.date sample: {[x.date() for x in df.index[:3]]}")

# Erstelle Signal
support, resistance = calculate_support_resistance(df, 7, 3, verbose=False)
signal_df = assign_long_signals_extended(support, resistance, df, 3, "1d")

# MANUELLER LEVEL CLOSE TEST
print(f"\n🔧 MANUELLER LEVEL CLOSE TEST:")

# Teste mit einem konkreten Datum
test_date = "2025-07-28"
print(f"Test Datum: {test_date}")

# Finde alle Daten für diesen Tag
dt_start = pd.to_datetime(test_date + ' 00:00:00')
print(f"Parsed Start: {dt_start}")
print(f"Start Date: {dt_start.date()}")

# Filtere df nach diesem Tag
day_data = df[df.index.date == dt_start.date()]
print(f"Day data shape: {day_data.shape}")

if len(day_data) > 0:
    print(f"First entry: {day_data.index[0]}")
    print(f"Close value: {day_data['Close'].iloc[0]}")
else:
    print("No data found for this day!")

# Teste die echte Funktion
print(f"\n🔧 ECHTER LEVEL CLOSE TEST:")
from signal_utils import update_level_close_long

# Erstelle ein minimales Test-DataFrame
test_signal = pd.DataFrame({
    'Long Date detected': ['2025-07-27', '2025-07-28', '2025-07-29']
})

print(f"Test signal shape: {test_signal.shape}")
result = update_level_close_long(test_signal, df)
print(f"Result shape: {result.shape}")
print(f"Result columns: {list(result.columns)}")

if 'Level Close' in result.columns:
    print(f"Level Close values: {result['Level Close'].tolist()}")
    print(f"Valid Level Close count: {result['Level Close'].notna().sum()}")

print("\n" + "="*35)
print("🔍 TEST Ende")
