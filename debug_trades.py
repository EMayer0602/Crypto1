import pandas as pd
import numpy as np
from crypto_backtesting_module import run_backtest
import config

# Debug Script für Extended Trades
symbol = 'ETH-EUR'
print(f"Analyzing {symbol}...")
result = run_backtest(symbol, config.config)

ext_full = result.get('ext_full')
df = result.get('data')

if ext_full is not None and df is not None:
    print(f"Extended Trades Shape: {ext_full.shape}")
    print(f"DataFrame Shape: {df.shape}")
    print(f"DataFrame Index Start: {df.index[0]}")
    print(f"DataFrame Index End: {df.index[-1]}")
    
    print("\nDataFrame letzte 5 Zeilen:")
    print(df.tail())
    
    print("\nExtended Trades letzte 5 Zeilen:")
    print(ext_full.tail())
    
    print("\nExtended Trades Actions:")
    print(ext_full['Action'].value_counts())
    
    # Test Offset Berechnung
    df_start_offset = len(df) - len(ext_full)
    print(f"\nOffset: {df_start_offset}")
    print(f"Offset bedeutet: Extended Trades starten bei DataFrame Position {df_start_offset}")
    print(f"DataFrame Position {df_start_offset}: {df.index[df_start_offset]}")
    print(f"DataFrame Position {df_start_offset + len(ext_full) - 1}: {df.index[df_start_offset + len(ext_full) - 1]}")
    
else:
    print("Konnte Extended Trades oder DataFrame nicht laden")
