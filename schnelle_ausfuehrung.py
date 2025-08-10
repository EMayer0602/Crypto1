#!/usr/bin/env python3
"""
SCHNELLE BITPANDA AUSFÜHRUNG
"""

from signal_transmitter import transmit_backtest_signals
from datetime import datetime

print("🚀 BITPANDA PAPER TRADING - JETZT AUSFÜHREN")
print("=" * 60)
print(f"Uhrzeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("🎯 Übertrage heutige Signale an Bitpanda Paper Trading")
print("=" * 60)

try:
    orders = transmit_backtest_signals()
    print(f"\n✅ ERFOLGREICH: {orders} Orders an Bitpanda Paper Trading gesendet!")
except Exception as e:
    print(f"\n❌ FEHLER: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 ABGESCHLOSSEN")
