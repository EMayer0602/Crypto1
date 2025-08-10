#!/usr/bin/env python3
"""
TEST PAPER TRADING - NUR HEUTE
Testet das System einmalig, um zu sehen ob es funktioniert
"""

import sys
import os
from datetime import datetime
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_paper_trading_heute():
    """Test das Paper Trading System einmalig für heute"""
    
    print("🧪 TEST PAPER TRADING - NUR HEUTE")
    print("=" * 60)
    print(f"🕐 Test Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Einmaliger Test um zu prüfen ob das System funktioniert")
    print("📡 Bitpanda Paper Trading API Test")
    print("=" * 60)
    
    test_erfolgreich = False
    orders_uebertragen = 0
    
    try:
        print("\n1️⃣ TESTE MODULE IMPORTS...")
        print("-" * 40)
        
        # Test 1: Module importieren
        try:
            from signal_transmitter import transmit_backtest_signals
            print("✅ signal_transmitter.py erfolgreich importiert")
        except ImportError as e:
            print(f"❌ Fehler beim Import von signal_transmitter: {e}")
            return False
        
        try:
            from bitpanda_secure_api import get_api_key_safely
            api_key = get_api_key_safely()
            print(f"✅ API Key: {'Verfügbar' if api_key else 'Nicht verfügbar'}")
        except ImportError as e:
            print(f"❌ Fehler beim Import von bitpanda_secure_api: {e}")
            return False
        
        print("\n2️⃣ TESTE SIGNAL EXTRAKTION...")
        print("-" * 40)
        
        # Test 2: Signale extrahieren und übertragen
        print("🔍 Führe Signal Extraktion und Übertragung aus...")
        
        orders_uebertragen = transmit_backtest_signals()
        
        print(f"📊 Ergebnis: {orders_uebertragen} Orders verarbeitet")
        
        if orders_uebertragen >= 0:  # Auch 0 ist ein gültiges Ergebnis
            test_erfolgreich = True
            print("✅ Signal Übertragung erfolgreich ausgeführt")
        else:
            print("❌ Problem bei Signal Übertragung")
        
    except Exception as e:
        print(f"❌ Fehler während Test: {e}")
        print("\n🔍 DETAILLIERTE FEHLER INFO:")
        traceback.print_exc()
        test_erfolgreich = False
    
    print("\n" + "=" * 60)
    print("🏁 TEST ERGEBNIS")
    print("=" * 60)
    
    if test_erfolgreich:
        print("✅ TEST ERFOLGREICH!")
        print(f"📈 Orders übertragen: {orders_uebertragen}")
        if orders_uebertragen > 0:
            print("🎉 Das System funktioniert! Orders wurden an Bitpanda Paper Trading gesendet")
        else:
            print("ℹ️ System funktioniert, aber keine aktuellen Signale vorhanden")
        print("🔄 Sie können jetzt das 2-Wochen-System starten")
    else:
        print("❌ TEST FEHLGESCHLAGEN!")
        print("🔧 Das System benötigt Korrekturen vor dem 2-Wochen-Lauf")
    
    print("=" * 60)
    
    return test_erfolgreich, orders_uebertragen

def main():
    """Hauptfunktion für einmaligen Test"""
    
    # Schreibe Ausgabe auch in Datei
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    output_buffer = io.StringIO()
    
    with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
        print("🧪 EINMALIGER SYSTEM TEST")
        print("💡 Prüft ob Paper Trading System funktioniert")
        print("🎯 Nur heute - danach 2-Wochen-System starten")
        print()
        
        erfolg, orders = test_paper_trading_heute()
        
        print(f"\n{'✅ SYSTEM BEREIT' if erfolg else '❌ SYSTEM PROBLEM'}")
        
        if erfolg and orders > 0:
            print(f"🎉 PERFEKT: {orders} Test-Orders wurden erfolgreich übertragen!")
            print("📱 Prüfen Sie Ihr Bitpanda Paper Trading Konto")
            print("🚀 Das 2-Wochen-System kann gestartet werden")
        elif erfolg and orders == 0:
            print("✅ System funktioniert, aber keine aktuellen Trading-Signale")
            print("💡 Das ist normal - bedeutet keine Trades für heute")
            print("🚀 Das 2-Wochen-System kann trotzdem gestartet werden")
        else:
            print("🔧 Bitte Fehler beheben bevor 2-Wochen-System gestartet wird")
    
    # Speichere Output in Datei
    output_text = output_buffer.getvalue()
    with open("test_results.txt", "w", encoding='utf-8') as f:
        f.write(f"Test ausgeführt am: {datetime.now()}\n")
        f.write("=" * 60 + "\n")
        f.write(output_text)
    
    # Zeige auch auf Konsole
    print(output_text)

if __name__ == "__main__":
    main()
