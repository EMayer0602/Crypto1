#!/usr/bin/env python3
"""
BITPANDA FUSION AUTOMATISIERUNG - EXAKT FÜR IHR INTERFACE
========================================================

Automatisiert GENAU die Fusion-Oberfläche die Sie im Screenshot zeigen.
Erkennt die spezifischen deutschen Elemente und Buttons.

Trade: BUY 0.009886 BTC-EUR @ €99,127.64
"""

import time
import sys
from datetime import datetime

def install_and_import_selenium():
    """Installiert und importiert Selenium"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        return webdriver, Options, By, WebDriverWait, EC, Keys
    except ImportError:
        print("📦 Installiere Selenium...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        return webdriver, Options, By, WebDriverWait, EC, Keys

def automate_fusion_german_interface():
    """Automatisiert die deutsche Fusion-Oberfläche"""
    
    print("🎯 FUSION DEUTSCHE INTERFACE AUTOMATISIERUNG")
    print("="*60)
    
    # Trade Details
    trade = {
        'pair': 'BTC-EUR',
        'action': 'KAUFEN',
        'quantity': '0.009886',
        'price': '99127.64',
        'order_value': '979.98'
    }
    
    print("📋 TRADE WIRD AUTOMATISCH EINGEGEBEN:")
    print(f"   🪙 {trade['action']} {trade['quantity']} BTC")
    print(f"   💰 Limit Preis: €{trade['price']}")
    print(f"   💵 Order Wert: €{trade['order_value']}")
    print()
    
    try:
        webdriver, Options, By, WebDriverWait, EC, Keys = install_and_import_selenium()
        
        print("🤖 STARTE AUTOMATISIERUNG...")
        
        # Browser Setup für bessere Erkennung
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        print("🌐 Starte Browser...")
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        wait = WebDriverWait(driver, 20)
        
        # Bitpanda Fusion öffnen
        print("🔗 Öffne Bitpanda Fusion...")
        driver.get("https://web.bitpanda.com/fusion")
        time.sleep(3)
        
        print("\n🔐 LOGGEN SIE SICH EIN UND NAVIGIEREN ZU FUSION")
        print("="*50)
        print("📋 Schritte:")
        print("   1. 📧 Einloggen in Bitpanda")
        print("   2. 🔄 Zu Fusion navigieren") 
        print("   3. 🪙 BTC-EUR auswählen (falls nicht schon)")
        print("   4. 🟢 'Kaufen' Button sichtbar machen")
        print("="*50)
        
        input("⏸️ DRÜCKEN SIE ENTER WENN FUSION BEREIT IST...")
        
        print("\n🤖 AUTOMATISCHE EINGABE STARTET...")
        print("="*40)
        
        success_count = 0
        
        # Schritt 1: Stelle sicher dass BTC-EUR ausgewählt ist
        print("🪙 1. Prüfe BTC-EUR Auswahl...")
        try:
            # Suche nach BTC-EUR Text im Interface
            btc_indicators = [
                "//div[contains(text(), 'BTC-EUR')]",
                "//span[contains(text(), 'Bitcoin')]",
                "//text()[contains(., 'BTC')]"
            ]
            
            btc_found = False
            for indicator in btc_indicators:
                try:
                    element = driver.find_element(By.XPATH, indicator)
                    if element:
                        print("   ✅ BTC-EUR bereits ausgewählt")
                        btc_found = True
                        success_count += 1
                        break
                except:
                    continue
            
            if not btc_found:
                print("   ⚠️ BTC-EUR nicht gefunden - bitte manuell auswählen")
        except Exception as e:
            print(f"   ⚠️ BTC Prüfung Fehler: {e}")
        
        time.sleep(2)
        
        # Schritt 2: Kaufen Button aktivieren
        print("🟢 2. Klicke 'Kaufen' Button...")
        try:
            kaufen_selectors = [
                "//button[contains(text(), 'Kaufen')]",
                "//div[contains(text(), 'Kaufen')]",
                "//span[contains(text(), 'Kaufen')]",
                ".buy-button",
                "[data-testid*='buy']",
                "button[class*='buy']"
            ]
            
            kaufen_found = False
            for selector in kaufen_selectors:
                try:
                    if selector.startswith("//"):
                        element = driver.find_element(By.XPATH, selector)
                    else:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Prüfe ob Element klickbar ist
                    if element.is_enabled() and element.is_displayed():
                        driver.execute_script("arguments[0].click();", element)
                        print("   ✅ 'Kaufen' erfolgreich geklickt")
                        kaufen_found = True
                        success_count += 1
                        time.sleep(2)
                        break
                except:
                    continue
            
            if not kaufen_found:
                print("   ⚠️ 'Kaufen' Button nicht gefunden - bitte manuell klicken")
        except Exception as e:
            print(f"   ⚠️ Kaufen Fehler: {e}")
        
        # Schritt 3: Strategie auf Limit setzen
        print("⚡ 3. Wähle Limit Order Strategie...")
        try:
            # Suche nach Strategie Dropdown
            strategy_selectors = [
                "//div[contains(@class, 'strategy')]",
                "//select[contains(@class, 'strategy')]",
                "//div[text()='Strategie auswählen']",
                ".strategy-dropdown",
                "[data-testid*='strategy']"
            ]
            
            for selector in strategy_selectors:
                try:
                    if selector.startswith("//"):
                        dropdown = driver.find_element(By.XPATH, selector)
                    else:
                        dropdown = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if dropdown:
                        dropdown.click()
                        time.sleep(1)
                        
                        # Suche nach Limit Option
                        limit_options = [
                            "//option[contains(text(), 'Limit')]",
                            "//div[contains(text(), 'Limit')]",
                            "//span[contains(text(), 'Limit')]"
                        ]
                        
                        for limit_opt in limit_options:
                            try:
                                limit_element = driver.find_element(By.XPATH, limit_opt)
                                limit_element.click()
                                print("   ✅ Limit Order Strategie ausgewählt")
                                success_count += 1
                                time.sleep(1)
                                break
                            except:
                                continue
                        break
                except:
                    continue
            
        except Exception as e:
            print(f"   ⚠️ Strategie Auswahl Fehler: {e}")
        
        # Schritt 4: Anzahl (Quantity) eingeben
        print("📈 4. Gebe Anzahl (Quantity) ein...")
        try:
            # Suche nach Anzahl Input Feld
            quantity_selectors = [
                "//input[contains(@placeholder, 'Anzahl')]",
                "//input[@name='amount']",
                "//input[@name='quantity']",
                ".amount-input input",
                ".quantity-input input",
                "[data-testid*='amount'] input"
            ]
            
            quantity_entered = False
            for selector in quantity_selectors:
                try:
                    if selector.startswith("//"):
                        input_field = driver.find_element(By.XPATH, selector)
                    else:
                        input_field = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if input_field and input_field.is_enabled():
                        # Clear und neue Quantity eingeben
                        input_field.clear()
                        input_field.send_keys(trade['quantity'])
                        input_field.send_keys(Keys.TAB)  # Tab um Feld zu verlassen
                        
                        print(f"   ✅ Anzahl {trade['quantity']} eingegeben")
                        quantity_entered = True
                        success_count += 1
                        time.sleep(2)
                        break
                except:
                    continue
            
            if not quantity_entered:
                print(f"   ⚠️ Anzahl-Feld nicht gefunden - bitte {trade['quantity']} manuell eingeben")
        except Exception as e:
            print(f"   ⚠️ Quantity Eingabe Fehler: {e}")
        
        # Schritt 5: Limit Preis eingeben
        print("💰 5. Gebe Limit Preis ein...")
        try:
            # Suche nach Preis Input Feld
            price_selectors = [
                "//input[contains(@placeholder, 'Preis')]",
                "//input[contains(@placeholder, 'Price')]",
                "//input[@name='price']",
                "//input[@name='limit_price']",
                ".price-input input",
                "[data-testid*='price'] input"
            ]
            
            price_entered = False
            for selector in price_selectors:
                try:
                    if selector.startswith("//"):
                        input_field = driver.find_element(By.XPATH, selector)
                    else:
                        input_field = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if input_field and input_field.is_enabled():
                        # Clear und neuen Preis eingeben
                        input_field.clear()
                        input_field.send_keys(trade['price'])
                        input_field.send_keys(Keys.TAB)  # Tab um Feld zu verlassen
                        
                        print(f"   ✅ Limit Preis €{trade['price']} eingegeben")
                        price_entered = True
                        success_count += 1
                        time.sleep(2)
                        break
                except:
                    continue
            
            if not price_entered:
                print(f"   ⚠️ Preis-Feld nicht gefunden - bitte €{trade['price']} manuell eingeben")
        except Exception as e:
            print(f"   ⚠️ Preis Eingabe Fehler: {e}")
        
        # Final validation
        time.sleep(3)
        
        print("\n" + "="*60)
        print("🎉 AUTOMATISIERUNG ABGESCHLOSSEN!")
        print("="*60)
        
        print(f"📊 ERFOLGSRATE: {success_count}/5 Schritte erfolgreich")
        
        if success_count >= 3:
            print("✅ TRADE ERFOLGREICH VORBEREITET!")
            print("\n📋 NÄCHSTE SCHRITTE:")
            print("   1. 🔍 Prüfen Sie alle Eingaben in Fusion")
            print("   2. 📊 Validieren Sie Order Value (~€979.98)")
            print("   3. 🚀 Klicken Sie 'Order' zum Senden")
            print("   4. ❌ Oder schließen Sie Browser zum Abbrechen")
        else:
            print("⚠️ TEILWEISE AUTOMATISIERUNG")
            print("📋 Bitte vervollständigen Sie manuell:")
            print(f"   📈 Anzahl: {trade['quantity']}")
            print(f"   💰 Limit Preis: €{trade['price']}")
            print("   ⚡ Strategie: Limit Order")
        
        print(f"\n❌ TRADE WURDE NICHT AUTOMATISCH GESENDET!")
        print("👀 Browser bleibt offen für Ihre Überprüfung")
        print("🔍 Sie entscheiden über das finale Senden")
        print("="*60)
        
        input("⏸️ DRÜCKEN SIE ENTER UM BROWSER ZU SCHLIESSEN...")
        
        driver.quit()
        return success_count >= 3
        
    except Exception as e:
        print(f"❌ Automatisierung Fehler: {str(e)}")
        return False

def main():
    """Hauptfunktion"""
    print("🎯 BITPANDA FUSION AUTOMATISIERUNG")
    print("="*50)
    print("✅ Speziell für deutsche Fusion-Oberfläche")
    print("✅ Erkennt 'Kaufen', 'Anzahl', 'Strategie'")
    print("✅ Automatische Eingabe aller Trade-Details")
    print("❌ Sendet NICHT automatisch - Ihre Kontrolle")
    print()
    
    print("📋 WIRD AUTOMATISCH EINGEGEBEN:")
    print("   🪙 BTC-EUR Kaufen")
    print("   📈 Anzahl: 0.009886")
    print("   💰 Limit Preis: €99,127.64")
    print("   ⚡ Limit Order Strategie")
    
    confirm = input("\n🤖 Automatisierung starten? (j/n): ")
    
    if confirm.lower() in ['j', 'ja', 'y', 'yes']:
        success = automate_fusion_german_interface()
        
        if success:
            print("\n🎉 TRADE ERFOLGREICH VORBEREITET!")
            print("🔍 Prüfen und senden Sie in Fusion")
        else:
            print("\n⚠️ AUTOMATISIERUNG TEILWEISE ERFOLGREICH")
            print("📝 Vervollständigen Sie manuell")
            
        return success
    else:
        print("❌ Automatisierung abgebrochen")
        return False

if __name__ == "__main__":
    main()
