#!/usr/bin/env python3
"""
DIREKTE BITPANDA PAPER TRADING AUSFÜHRUNG
Führt die heutigen Signale sofort über Bitpanda Paper Trading aus
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def execute_paper_trading_now():
    """Führe Paper Trading jetzt aus"""
    
    print("🚀 BITPANDA PAPER TRADING - SOFORTIGE AUSFÜHRUNG")
    print("=" * 65)
    print(f"🕐 Ausführungszeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Direkte Übertragung an Bitpanda Paper Trading API")
    print("=" * 65)
    
    try:
        # Importiere das Signal Transmitter Modul
        from signal_transmitter import SignalTransmitter
        
        print("✅ Signal Transmitter Modul erfolgreich geladen")
        
        # Erstelle Transmitter Instanz
        transmitter = SignalTransmitter()
        
        # Hole aktuelle Signale
        print("\n🔍 Extrahiere aktuelle Trading-Signale...")
        signals = transmitter.get_current_signals_from_backtest()
        
        if not signals:
            print("⚠️ Keine aktuellen Signale gefunden")
            return 0
        
        print(f"📊 {len(signals)} Signale gefunden")
        
        # Übertrage Signale an Bitpanda
        print("\n📡 Übertrage Signale an Bitpanda Paper Trading...")
        orders_transmitted = 0
        
        for ticker, signal_data in signals.items():
            try:
                result = transmitter.transmit_signal_to_bitpanda(ticker, signal_data)
                if result.get('success'):
                    orders_transmitted += 1
                    print(f"✅ {ticker}: {signal_data.get('action', 'N/A')} Order übertragen")
                else:
                    print(f"❌ {ticker}: Fehler bei Übertragung")
            except Exception as e:
                print(f"❌ {ticker}: Fehler - {e}")
        
        print(f"\n🎉 PAPER TRADING ABGESCHLOSSEN!")
        print("=" * 50)
        print(f"📈 Erfolgreich übertragene Orders: {orders_transmitted}")
        print(f"🏛️ Alle Orders an Bitpanda Paper Trading gesendet")
        print("=" * 50)
        
        return orders_transmitted
        
    except ImportError as e:
        print(f"❌ Fehler beim Importieren: {e}")
        print("💡 Stelle sicher, dass alle Module verfügbar sind")
        return 0
    except Exception as e:
        print(f"❌ Allgemeiner Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    orders = execute_paper_trading_now()
    
    if orders > 0:
        print(f"\n✅ SUCCESS: {orders} Orders an Bitpanda Paper Trading übertragen!")
    else:
        print(f"\n⚠️ Keine Orders übertragen - prüfen Sie die Signale und API-Verbindung")
    
    input("\nDrücken Sie Enter zum Beenden...")
