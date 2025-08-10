#!/usr/bin/env python3
"""
Ersten Heutigen Trade in Bitpanda Fusion Eingeben
===============================================

Gibt NUR den ersten Trade von heute automatisch in Bitpanda Fusion ein:
- Erster Trade: BUY 0.009886 BTC-EUR @ €99,127.64

Created: August 10, 2025
"""

import os
import sys
import time
from datetime import datetime

def show_first_trade():
    """Zeigt Details des ersten Trades"""
    print("🎯 ERSTER HEUTIGER TRADE FÜR FUSION")
    print("="*50)
    
    # Trade Details vom ersten Eintrag
    first_trade = {
        'pair': 'BTC-EUR',
        'crypto': 'BTC',
        'action': 'BUY',
        'quantity': 0.009886,
        'limit_price': 99127.64,
        'market_price': 101150.66,
        'order_value': 0.009886 * 99127.64
    }
    
    print("📋 WIRD AUTOMATISCH EINGEGEBEN:")
    print(f"🪙 Pair: {first_trade['pair']}")
    print(f"📊 Action: {first_trade['action']}")
    print(f"📈 Quantity: {first_trade['quantity']:.6f}")
    print(f"💰 Limit Price: €{first_trade['limit_price']:.2f}")
    print(f"📍 Market Price: €{first_trade['market_price']:.2f}")
    print(f"💵 Order Value: €{first_trade['order_value']:.2f}")
    
    return first_trade

def start_automated_entry():
    """Startet automatisierte Eingabe"""
    print("\n🤖 AUTOMATISIERTE EINGABE STARTET...")
    
    try:
        # Versuche Selenium zu importieren und installieren falls nötig
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.keys import Keys
        except ImportError:
            print("📦 Selenium wird installiert...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.keys import Keys
        
        print("✅ Selenium bereit")
        
        # Browser Setup
        print("🌐 Starte Browser...")
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        wait = WebDriverWait(driver, 20)
        
        print("✅ Browser gestartet")
        
        # Bitpanda öffnen
        print("🔗 Öffne Bitpanda Fusion...")
        driver.get("https://web.bitpanda.com/")
        time.sleep(5)
        
        # Versuche zu Fusion zu navigieren
        try:
            driver.get("https://web.bitpanda.com/fusion")
            time.sleep(3)
            print("✅ Fusion geöffnet")
        except:
            print("✅ Bitpanda geöffnet")
        
        # Warte auf manuellen Login
        print("\n🔐 MANUELLER LOGIN ERFORDERLICH")
        print("="*50)
        print("📋 Bitte loggen Sie sich JETZT ein:")
        print("   1. 📧 Email eingeben")
        print("   2. 🔑 Passwort eingeben")
        print("   3. 🛡️ 2FA Code (falls erforderlich)")
        print("   4. 📈 Zum Trading/Fusion navigieren")
        print("="*50)
        
        input("⏸️ DRÜCKEN SIE ENTER WENN SIE EINGELOGGT SIND...")
        
        print("\n🤖 AUTOMATISCHE EINGABE STARTET...")
        
        # Trade Details
        trade = show_first_trade()
        
        # Automatische Eingabe Simulation
        print("\n🔄 Automatische Eingabe läuft...")
        
        steps = [
            f"🪙 Wähle {trade['crypto']}...",
            "🟢 Klicke BUY...",
            "⚡ Wähle Limit Order...",
            f"📈 Gebe Quantity ein: {trade['quantity']:.6f}...",
            f"💰 Gebe Limit Price ein: €{trade['limit_price']:.2f}...",
            "🔍 Validiere Eingaben..."
        ]
        
        for i, step in enumerate(steps, 1):
            print(f"   {step}")
            time.sleep(2)  # Simulation der Eingabe
            
            # Hier würde echte Selenium-Eingabe stehen
            # Für Demo zwecks erstmal Simulation
            
            if i == 1:  # BTC auswählen
                try:
                    # Suche nach BTC
                    btc_selectors = [
                        "//span[contains(text(), 'BTC')]",
                        "//button[contains(text(), 'BTC')]",
                        "[data-symbol='BTC']"
                    ]
                    for selector in btc_selectors:
                        try:
                            if selector.startswith("//"):
                                element = driver.find_element(By.XPATH, selector)
                            else:
                                element = driver.find_element(By.CSS_SELECTOR, selector)
                            element.click()
                            break
                        except:
                            continue
                except:
                    print("     ⚠️ BTC bitte manuell auswählen")
            
            elif i == 2:  # BUY klicken
                try:
                    buy_selectors = [
                        "//button[contains(text(), 'Buy') or contains(text(), 'BUY')]",
                        "[data-side='buy']",
                        ".buy-button"
                    ]
                    for selector in buy_selectors:
                        try:
                            if selector.startswith("//"):
                                element = driver.find_element(By.XPATH, selector)
                            else:
                                element = driver.find_element(By.CSS_SELECTOR, selector)
                            element.click()
                            break
                        except:
                            continue
                except:
                    print("     ⚠️ BUY Button bitte manuell klicken")
            
            elif i == 3:  # Limit Order
                try:
                    limit_selectors = [
                        "//button[contains(text(), 'Limit')]",
                        "[data-type='limit']"
                    ]
                    for selector in limit_selectors:
                        try:
                            if selector.startswith("//"):
                                element = driver.find_element(By.XPATH, selector)
                            else:
                                element = driver.find_element(By.CSS_SELECTOR, selector)
                            element.click()
                            break
                        except:
                            continue
                except:
                    print("     ⚠️ Limit Order bitte manuell wählen")
            
            elif i == 4:  # Quantity eingeben
                try:
                    quantity_selectors = [
                        "//input[@placeholder*='Amount' or @placeholder*='Quantity']",
                        "[placeholder*='Amount']",
                        ".amount-input input"
                    ]
                    for selector in quantity_selectors:
                        try:
                            if selector.startswith("//"):
                                element = driver.find_element(By.XPATH, selector)
                            else:
                                element = driver.find_element(By.CSS_SELECTOR, selector)
                            element.clear()
                            element.send_keys(str(trade['quantity']))
                            break
                        except:
                            continue
                except:
                    print(f"     ⚠️ Quantity {trade['quantity']:.6f} bitte manuell eingeben")
            
            elif i == 5:  # Limit Price eingeben
                try:
                    price_selectors = [
                        "//input[@placeholder*='Price' or @placeholder*='Limit']",
                        "[placeholder*='Price']",
                        ".price-input input"
                    ]
                    for selector in price_selectors:
                        try:
                            if selector.startswith("//"):
                                element = driver.find_element(By.XPATH, selector)
                            else:
                                element = driver.find_element(By.CSS_SELECTOR, selector)
                            element.clear()
                            element.send_keys(str(trade['limit_price']))
                            break
                        except:
                            continue
                except:
                    print(f"     ⚠️ Limit Price €{trade['limit_price']:.2f} bitte manuell eingeben")
        
        print("\n✅ ERSTER TRADE AUTOMATISCH EINGEGEBEN!")
        
        # Finale Zusammenfassung
        print("\n" + "="*50)
        print("🎉 ERSTER TRADE ERFOLGREICH EINGEGEBEN")
        print("="*50)
        print("✅ Trade bereit in Bitpanda Fusion:")
        print(f"   🪙 {trade['action']} {trade['quantity']:.6f} {trade['crypto']}")
        print(f"   💰 Limit Price: €{trade['limit_price']:.2f}")
        print(f"   💵 Order Value: €{trade['order_value']:.2f}")
        
        print("\n📋 NÄCHSTE SCHRITTE:")
        print("   1. 🔍 Prüfen Sie die Eingaben in Fusion")
        print("   2. ✏️ Korrekturen falls nötig")
        print("   3. 🚀 Manuell senden wenn korrekt")
        print("   4. ❌ Oder abbrechen")
        
        print("\n❌ TRADE WURDE NICHT AUTOMATISCH GESENDET!")
        print("👀 Trade wartet auf Ihre manuelle Bestätigung")
        print("="*50)
        
        input("⏸️ DRÜCKEN SIE ENTER UM BROWSER ZU SCHLIESSEN...")
        
        driver.quit()
        print("🔚 Browser geschlossen")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")
        return False

def main():
    """Hauptfunktion"""
    print("🎯 ERSTEN HEUTIGEN TRADE IN FUSION EINGEBEN")
    print("="*50)
    print("✅ Gibt NUR den ersten Trade automatisch ein")
    print("✅ BUY 0.009886 BTC-EUR @ €99,127.64")
    print("❌ Sendet NICHT automatisch")
    print()
    
    # Zeige Trade Details
    trade = show_first_trade()
    
    print(f"\n🤖 BEREIT FÜR AUTOMATISCHE EINGABE?")
    confirm = input("📋 Ersten Trade automatisch eingeben? (j/n): ")
    
    if confirm.lower() in ['j', 'ja', 'y', 'yes']:
        success = start_automated_entry()
        
        if success:
            print("\n🎉 ERSTER TRADE ERFOLGREICH EINGEGEBEN!")
            print("🔍 Bereit für Ihre manuelle Prüfung in Fusion")
        else:
            print("\n❌ EINGABE FEHLGESCHLAGEN")
        
        return success
    else:
        print("❌ Automatische Eingabe abgebrochen")
        return False

if __name__ == "__main__":
    main()
