#!/usr/bin/env python3
"""
SOFORT BITPANDA PAPER TRADING
Führt die heutigen Trades JETZT aus, ohne auf Mitternacht zu warten
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def sofortiger_paper_trade():
    """Führe Paper Trading SOFORT aus"""
    
    print("🚀 SOFORT BITPANDA PAPER TRADING")
    print("=" * 60)
    print(f"🕐 JETZT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⚡ KEINE WARTEZEIT - Trades werden SOFORT ausgeführt")
    print("🎯 Bitpanda Paper Trading API")
    print("=" * 60)
    
    try:
        # Importiere das Simple Daily Trader Modul
        print("📋 Lade Trading Module...")
        
        # Führe die gleiche Funktion aus wie der Daily Trader, aber JETZT
        from signal_transmitter import transmit_backtest_signals
        
        print("✅ Signal Transmitter geladen")
        print("\n📡 STARTE SIGNAL ÜBERTRAGUNG...")
        print("-" * 40)
        
        # Führe die Signalübertragung SOFORT aus
        orders_transmitted = transmit_backtest_signals()
        
        print("-" * 40)
        print(f"\n🎉 SOFORT PAPER TRADING ABGESCHLOSSEN!")
        print("=" * 60)
        print(f"📈 Orders erfolgreich übertragen: {orders_transmitted}")
        print(f"🏛️ Alle Orders an Bitpanda Paper Trading gesendet")
        print(f"🕐 Ausführungszeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        if orders_transmitted > 0:
            print("✅ ERFOLGREICH: Paper Trading Orders wurden übertragen!")
            print("📊 Prüfen Sie Ihr Bitpanda Paper Trading Konto")
        else:
            print("⚠️ HINWEIS: Keine Orders übertragen")
            print("💡 Möglicherweise keine aktuellen Signale verfügbar")
        
        return orders_transmitted
        
    except ImportError as e:
        print(f"❌ Import Fehler: {e}")
        print("💡 Stelle sicher, dass signal_transmitter.py verfügbar ist")
        return 0
        
    except Exception as e:
        print(f"❌ Fehler bei Paper Trading: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    
    print("⚡ BITPANDA PAPER TRADING - SOFORTIGE AUSFÜHRUNG")
    print("🚫 KEINE WARTEZEIT - Führt Trades JETZT aus")
    print()
    
    try:
        orders = sofortiger_paper_trade()
        
        print(f"\n{'='*60}")
        if orders > 0:
            print(f"✅ ERFOLG: {orders} Orders an Bitpanda Paper Trading übertragen!")
            print("📱 Die Orders sind jetzt in Ihrem Paper Trading Konto")
        else:
            print("ℹ️ Keine Orders übertragen")
            print("🔍 Prüfen Sie die aktuellen Signale und API-Verbindung")
        
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print("\n🛑 Abgebrochen durch Benutzer")
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
    
    print("\n🏁 PROGRAMM BEENDET")
    input("Drücken Sie Enter zum Schließen...")
