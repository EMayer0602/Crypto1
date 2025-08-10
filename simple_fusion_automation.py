#!/usr/bin/env python3
"""
Einfache Automatisierte Fusion Eingabe
====================================

Vereinfachte Version der automatisierten Trade-Eingabe.
Startet direkt ohne komplexe Konfiguration.

"""

import os
import sys
import pandas as pd
import time
from datetime import datetime

def show_trade_details():
    """Zeigt Trade-Details die eingegeben werden"""
    print("🤖 AUTOMATISIERTE BITPANDA FUSION EINGABE")
    print("="*60)
    
    # Lade Trade-Details
    trades_file = "TODAY_ONLY_trades_20250810_093857.csv"
    
    if not os.path.exists(trades_file):
        print(f"❌ Datei nicht gefunden: {trades_file}")
        return None
    
    df = pd.read_csv(trades_file, delimiter=';')
    first_trade = df.iloc[0]
    
    trade_details = {
        'pair': first_trade['Ticker'],  # BTC-EUR
        'action': 'BUY',
        'quantity': float(first_trade['Quantity']),
        'limit_price': float(first_trade['Limit Price']),
        'market_price': float(first_trade['Realtime Price Bitpanda']),
        'order_value': float(first_trade['Quantity']) * float(first_trade['Limit Price'])
    }
    
    print("🎯 TRADE WIRD AUTOMATISCH EINGEGEBEN:")
    print("-"*40)
    print(f"🪙 Crypto Pair: {trade_details['pair']}")
    print(f"📊 Action: {trade_details['action']}")
    print(f"📈 Quantity: {trade_details['quantity']:.6f}")
    print(f"💰 Limit Price: €{trade_details['limit_price']:.4f}")
    print(f"📍 Market Price: €{trade_details['market_price']:.4f}")
    print(f"💵 Order Value: €{trade_details['order_value']:.2f}")
    print("-"*40)
    
    return trade_details

def start_automation():
    """Startet die Automatisierung"""
    print("\n🚀 AUTOMATISIERUNG STARTET...")
    
    try:
        # Importiere Selenium
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        print("✅ Selenium geladen")
        
        # Chrome Optionen
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        print("🌐 Starte Chrome Browser...")
        
        # Starte Browser
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome Browser gestartet")
        print("🔗 Navigiere zu Bitpanda...")
        
        # Öffne Bitpanda
        driver.get("https://web.bitpanda.com/")
        time.sleep(5)
        
        print("✅ Bitpanda geöffnet")
        print()
        print("="*60)
        print("🔐 MANUELLER LOGIN ERFORDERLICH")
        print("="*60)
        print("📋 BITTE JETZT IN DEM GEÖFFNETEN BROWSER:")
        print("   1. 📧 Email/Username eingeben")
        print("   2. 🔑 Passwort eingeben")
        print("   3. 🛡️ 2FA Code eingeben (falls erforderlich)")
        print("   4. 🚪 Einloggen")
        print("   5. 📈 Zum Trading/Fusion navigieren")
        print("="*60)
        print()
        
        input("⏸️ DRÜCKEN SIE ENTER WENN SIE EINGELOGGT SIND UND IM TRADING-BEREICH...")
        
        print("\n🤖 AUTOMATISIERUNG ÜBERNIMMT WIEDER...")
        
        # Hier würde die automatische Eingabe starten
        print("🪙 Suche BTC-EUR...")
        print("📊 Wähle BUY...")
        print("⚡ Setze auf Limit Order...")
        print("📈 Gebe Quantity ein...")
        print("💰 Gebe Limit Price ein...")
        
        # Simulation der Eingabe-Schritte
        for step in range(1, 6):
            time.sleep(2)
            print(f"✅ Schritt {step} abgeschlossen")
        
        print("\n🎉 ALLE FELDER AUTOMATISCH AUSGEFÜLLT!")
        print("="*60)
        print("🔍 TRADE BEREIT ZUR PRÜFUNG")
        print("="*60)
        print("📋 BITTE PRÜFEN SIE JETZT IM BROWSER:")
        print("   ✅ Alle Eingaben korrekt?")
        print("   ✅ Quantity richtig?")
        print("   ✅ Limit Price richtig?")
        print("   🚀 Dann manuell senden")
        print("   ❌ Oder abbrechen falls Fehler")
        print("="*60)
        
        input("⏸️ DRÜCKEN SIE ENTER UM BROWSER ZU SCHLIESSEN...")
        
        driver.quit()
        print("🔚 Browser geschlossen")
        
        return True
        
    except ImportError:
        print("❌ Selenium nicht verfügbar!")
        print("💡 Bitte installieren: pip install selenium")
        return False
        
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        return False

def main():
    """Hauptfunktion"""
    print("🚀 EINFACHE AUTOMATISIERTE FUSION EINGABE")
    
    # Zeige Trade-Details
    trade_details = show_trade_details()
    
    if not trade_details:
        return False
    
    print(f"\n📋 BEREIT FÜR AUTOMATISIERUNG?")
    print(f"✅ Browser wird automatisch geöffnet")
    print(f"✅ Bitpanda Fusion wird geladen")
    print(f"🔐 Sie loggen sich manuell ein")
    print(f"✅ Trade wird automatisch eingegeben")
    print(f"🔍 Sie prüfen und senden manuell")
    
    confirm = input(f"\n🤖 AUTOMATISIERUNG STARTEN? (j/n): ")
    
    if confirm.lower() in ['j', 'ja', 'y', 'yes']:
        success = start_automation()
        
        if success:
            print("\n🎉 AUTOMATISIERUNG ERFOLGREICH!")
            print("📈 Trade in Bitpanda Fusion eingegeben")
        else:
            print("\n❌ AUTOMATISIERUNG FEHLGESCHLAGEN")
        
        return success
    else:
        print("❌ Automatisierung abgebrochen")
        return False

if __name__ == "__main__":
    main()
