#!/usr/bin/env python3
"""
Direkter Test für trade_on Funktionalität
"""

import pandas as pd
from signal_utils import assign_long_signals_extended, calculate_support_resistance

print("🧪 DIREKTER TRADE_ON TEST")
print("="*50)

# Lade SOL-EUR Daten
df = pd.read_csv("SOL-EUR_daily.csv", parse_dates=['Date'], index_col='Date')
print(f"Daten geladen: {len(df)} Zeilen")
print(f"Erste 3 Zeilen:")
print(df[['Open', 'Close']].head(3))

# Calculiere Support/Resistance (einfach)
support, resistance = calculate_support_resistance(df, 5, 2, verbose=False)

# Teste unterschiedliche trade_on Werte
print("\n🔍 TESTE TRADE_ON PARAMETER...")

# Mit Close
print("\n1️⃣ Mit trade_on='Close':")
ext_close = assign_long_signals_extended(support, resistance, df, 2, "1d", "Close")
buy_close = ext_close[ext_close['Action'] == 'BUY']
print(f"  BUY-Signale: {len(buy_close)}")
if len(buy_close) > 0:
    first_signal = buy_close.iloc[0]
    print(f"  Erstes Signal: Level Close = {first_signal.get('Level Close', 'N/A')}")

# Mit Open
print("\n2️⃣ Mit trade_on='Open':")
ext_open = assign_long_signals_extended(support, resistance, df, 2, "1d", "Open")
buy_open = ext_open[ext_open['Action'] == 'BUY']
print(f"  BUY-Signale: {len(buy_open)}")
if len(buy_open) > 0:
    first_signal = buy_open.iloc[0]
    print(f"  Erstes Signal: Level Close = {first_signal.get('Level Close', 'N/A')}")

# Vergleiche
if len(buy_close) > 0 and len(buy_open) > 0:
    close_price = buy_close.iloc[0].get('Level Close', 0)
    open_price = buy_open.iloc[0].get('Level Close', 0)
    
    print(f"\n📊 VERGLEICH:")
    print(f"  Close-Preis: {close_price}")
    print(f"  Open-Preis: {open_price}")
    
    if abs(close_price - open_price) > 0.01:  # Mehr als 1 Cent Unterschied
        print("✅ ERFOLGREICH: Open und Close sind unterschiedlich!")
        print("✅ trade_on Parameter funktioniert korrekt!")
    else:
        print("⚠️ WARNUNG: Open und Close sind fast identisch")
        print("   Möglicherweise trade_on nicht korrekt implementiert")
else:
    print("⚠️ Keine BUY-Signale zum Vergleichen gefunden")

print("\n=== Test abgeschlossen ===")
