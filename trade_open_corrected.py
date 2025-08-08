#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trade on Open Korrektur - Zusammenfassung
"""

print("🔧 TRADE ON OPEN EQUITY CURVE - KORRIGIERTE FORMELN")
print("=" * 70)

print("""
✅ KORREKTE TRADE ON OPEN LOGIK IMPLEMENTIERT:

📈 BUY DATE:
   capital = capital + (Close - Open) * shares - fee
   
📊 LONG DAY (außer Buy/Sell):
   capital = capital + (Close - previous_Close) * shares
   
💰 SELL DAY:
   capital = capital + (Open - previous_Close) * shares - fee
   
💤 NOT INVESTED DAY:
   capital = capital (konstant)

""")

print("🔍 ANGEWANDT AUF FOLGENDE SYMBOLS:")
print("-" * 40)
print("🔶 BTC-EUR  (€5000) - Trade on Open")
print("🔶 DOGE-EUR (€2000) - Trade on Open") 
print("🔶 LINK-EUR (€1500) - Trade on Open")
print()
print("🔷 ETH-EUR  (€3000) - Trade on Close")
print("🔷 SOL-EUR  (€2000) - Trade on Close")
print("🔷 XRP-EUR  (€1000) - Trade on Close")

print("\n" + "=" * 70)
print("🚀 BEREIT FÜR LIVE BACKTEST!")
print("=" * 70)
