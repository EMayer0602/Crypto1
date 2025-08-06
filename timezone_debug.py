#!/usr/bin/env python3
"""
🔍 TIMEZONE DEBUG
"""

import pandas as pd

print("🔍 TIMEZONE DEBUG")
print("="*30)

# Lade Daten
df = pd.read_csv('BTC-EUR_minute.csv', parse_dates=['DateTime'])
df.set_index('DateTime', inplace=True)

print(f"df.index Info:")
print(f"  Type: {type(df.index)}")
print(f"  Timezone: {df.index.tz}")
print(f"  First 3: {df.index[:3]}")

# Simuliere 'Long Date detected' Wert
sample_date = df.index[10]  # Nimm einen existierenden Wert
print(f"\nSample Date: {sample_date}")
print(f"  Type: {type(sample_date)}")
print(f"  Timezone: {sample_date.tz}")

# Teste Vergleich
try:
    result = sample_date in df.index
    print(f"  In index: {result}")
except Exception as e:
    print(f"  Error comparing: {e}")

# Teste String-Konvertierung
sample_str = str(sample_date)
print(f"\nString version: {sample_str}")

converted = pd.to_datetime(sample_str)
print(f"Converted back: {converted}")
print(f"  Type: {type(converted)}")
print(f"  Timezone: {converted.tz}")

# Teste manuelle Timezone-Konvertierung
if df.index.tz is not None:
    if converted.tz is None:
        converted_tz = converted.tz_localize(df.index.tz)
        print(f"Localized: {converted_tz}")
        print(f"  Timezone: {converted_tz.tz}")
        
        try:
            result = converted_tz in df.index
            print(f"  In index after tz fix: {result}")
        except Exception as e:
            print(f"  Error after tz fix: {e}")

print("\n" + "="*30)
print("🔍 DEBUG Ende")
