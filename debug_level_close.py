#!/usr/bin/env python3
"""
🔍 DEBUG - Level Close Problem
"""

import pandas as pd
from signal_utils import calculate_support_resistance, assign_long_signals_extended, update_level_close_long

print("🔍 DEBUG - Level Close Problem")
print("="*50)

# Lade Daten
df = pd.read_csv('BTC-EUR_minute.csv', parse_dates=['DateTime'])
df.set_index('DateTime', inplace=True)

# Erstelle Signale
support, resistance = calculate_support_resistance(df, 7, 3, verbose=False)
signal_df = assign_long_signals_extended(support, resistance, df, 3, "1d")

print(f"Signal DataFrame vor Level Close Update:")
print(f"  Shape: {signal_df.shape}")
print(f"  Spalten: {list(signal_df.columns)}")

# Prüfe 'Long Date detected' Spalte
if 'Long Date detected' in signal_df.columns:
    print(f"  Long Date detected Werte (erste 5):")
    for i in range(min(5, len(signal_df))):
        date_val = signal_df.iloc[i]['Long Date detected']
        print(f"    {i}: {date_val} (type: {type(date_val)})")
        
        # Prüfe ob Datum im df.index ist
        if pd.notna(date_val):
            if isinstance(date_val, str):
                date_val = pd.to_datetime(date_val)
            
            date_norm = date_val.normalize()
            print(f"       Normalisiert: {date_norm}")
            print(f"       In df.index? {date_norm in df.index}")
            
            # Finde nächstes verfügbares Datum
            if date_norm not in df.index:
                idx = df.index.searchsorted(date_norm)
                if idx < len(df.index):
                    next_date = df.index[idx]
                    print(f"       Nächstes Datum: {next_date}")

# Prüfe df.index Format
print(f"\nDataFrame index Info:")
print(f"  Index type: {type(df.index)}")
print(f"  Index dtype: {df.index.dtype}")
print(f"  Index first 3: {df.index[:3].tolist()}")
print(f"  Index timezone: {df.index.tz}")

# Update Level Close mit Debug
print(f"\nUpdate Level Close...")
signal_df = update_level_close_long(signal_df, df)

print(f"\nNach Level Close Update:")
print(f"  Level Close NaN count: {signal_df['Level Close'].isna().sum()}")
print(f"  Level Close valid count: {signal_df['Level Close'].notna().sum()}")

if signal_df['Level Close'].notna().sum() > 0:
    print(f"  Erste gültige Level Close Werte:")
    valid_closes = signal_df[signal_df['Level Close'].notna()]['Level Close']
    print(f"    {valid_closes.head().tolist()}")
else:
    print(f"  ❌ ALLE Level Close Werte sind NaN!")

print("\n" + "="*50)
print("🔍 DEBUG Ende")
