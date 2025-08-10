#!/usr/bin/env python3
"""
SOFORTIGER PAPER TRADING AUSFÜHRER
Führt die heutigen Trading-Signale sofort im Paper Trading aus
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from signal_transmitter import transmit_backtest_signals

def execute_immediate_paper_trading():
    """Führe sofortiges Paper Trading aus"""
    
    print("🚀 SOFORTIGER PAPER TRADING START")
    print("=" * 60)
    print(f"🕐 Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💡 Führe heutige Signale SOFORT im Paper Trading aus")
    print("📡 Bitpanda Paper Trading API")
    print("=" * 60)
    
    try:
        # Führe die Signalübertragung aus
        orders_transmitted = transmit_backtest_signals()
        
        print(f"\n🎉 PAPER TRADING AUSFÜHRUNG ABGESCHLOSSEN!")
        print("=" * 60)
        print(f"📈 Orders übertragen: {orders_transmitted}")
        print(f"🕐 Ausführungszeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("💰 Alle Orders wurden an Bitpanda Paper Trading gesendet")
        print("=" * 60)
        
        return orders_transmitted
        
    except Exception as e:
        print(f"❌ Fehler beim Paper Trading: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    """Hauptfunktion"""
    
    print("🎯 SOFORTIGE PAPER TRADING AUSFÜHRUNG")
    print("💡 Kein Warten bis Mitternacht - JETZT ausführen!")
    print()
    
    orders = execute_immediate_paper_trading()
    
    if orders > 0:
        print(f"\n✅ ERFOLGREICH: {orders} Paper Trading Orders ausgeführt!")
    else:
        print(f"\n⚠️ Keine Orders ausgeführt - möglicherweise keine Signale für heute")

if __name__ == "__main__":
    main()
