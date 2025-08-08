#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direkte Analyse der Trade on Open Probleme
"""

print("🔍 TRADE ON OPEN EQUITY CURVE ANALYSE")
print("=" * 60)

print("""
📝 IDENTIFIZIERTE PROBLEME BEI TRADE ON OPEN:

1. ❌ PROBLEM: previous_close Initialisierung
   - Erste Tag: previous_close = today_open ist falsch
   - KORREKTUR: ✅ Verwende Close des Vortages

2. ❌ PROBLEM: Sell-Day Berechnung bei Trade on Open
   - Aktuell: capital + (open - previous_close) * shares - fee
   - Das ist FALSCH, weil:
     * Bei Trade on Open wird zum Open gekauft/verkauft
     * Am Sell-Tag gibt es KEINE zusätzliche tägliche PnL
     * Die Position wurde über Nacht gehalten

3. 💡 KORREKTE TRADE ON OPEN LOGIK:
   
   BUY-TAG:
   - Kauf zum Open-Preis
   - capital = capital + (close - open) * shares - buy_fees
   - Grund: Position über den Tag gehalten, PnL = close - open
   
   LONG-TAGE (außer Buy/Sell):
   - capital = capital + (close - previous_close) * shares  
   - Grund: Overnight-Bewegung der Position
   
   SELL-TAG:
   - Verkauf zum Open-Preis
   - capital = capital - sell_fees
   - Grund: Keine zusätzliche PnL, da Verkauf zum Open

4. 🔧 LÖSUNGSVORSCHLAG:
   - ✅ previous_close Korrektur bereits implementiert
   - ⏳ Sell-Day Logik für Trade on Open korrigieren
   - 🧪 Test mit BTC-EUR, DOGE-EUR, LINK-EUR

""")

print("=" * 60)
print("🚀 NÄCHSTE SCHRITTE:")
print("1. Sell-Day Logik für Trade on Open korrigieren")
print("2. Live-Backtest mit korrigierter Logik ausführen") 
print("3. Differenzen zwischen Equity Curve und Final Capital prüfen")
print("=" * 60)
