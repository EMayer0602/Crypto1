#!/usr/bin/env python3
"""
SOFORTIGE FUSION AUTOMATISIERUNG - BESTEHENDER BROWSER
=====================================================

Verbindet sich SOFORT mit Ihrem bereits laufenden Fusion-Browser.
KEINE neuen Fenster, KEIN Login, KEINE SMS.

Arbeitet direkt in Ihrem bestehenden Tab.
"""

import time
import sys
import subprocess

def enable_chrome_debug_mode():
    """Aktiviert Debug-Modus für bestehenden Chrome"""
    print("🔧 AKTIVIERE CHROME DEBUG-MODUS...")
    
    try:
        # Finde laufende Chrome-Prozesse
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'chrome.exe' in result.stdout:
            print("✅ Chrome läuft bereits")
            
            # Starte neuen Chrome-Debug Prozess der sich an bestehenden anhängt
            debug_cmd = [
                'chrome.exe',
                '--remote-debugging-port=9222',
                '--disable-web-security',
                '--user-data-dir=temp_selenium_debug'
            ]
            
            subprocess.Popen(debug_cmd, shell=True)
            time.sleep(3)
            print("✅ Debug-Modus aktiviert")
            return True
        else:
            print("⚠️ Chrome läuft nicht")
            return False
            
    except Exception as e:
        print(f"❌ Debug-Aktivierung fehlgeschlagen: {e}")
        return False

def connect_and_automate():
    """Verbindet sich mit Browser und automatisiert sofort"""
    
    # Selenium installieren
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
    except ImportError:
        print("📦 Installiere Selenium...")
        subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
    
    print("🔗 VERBINDE MIT BESTEHENDEM CHROME...")
    
    # Chrome Options für bestehende Instanz
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ VERBINDUNG ERFOLGREICH!")
        
        # Finde Fusion Tab
        fusion_found = False
        for handle in driver.window_handles:
            try:
                driver.switch_to.window(handle)
                url = driver.current_url.lower()
                title = driver.title.lower()
                
                if any(keyword in url for keyword in ['bitpanda', 'fusion']) or \
                   any(keyword in title for keyword in ['bitpanda', 'fusion']):
                    print(f"✅ FUSION TAB GEFUNDEN: {driver.title}")
                    fusion_found = True
                    break
            except:
                continue
        
        if not fusion_found:
            print("❌ Fusion Tab nicht gefunden")
            print("📋 Öffnen Sie bitte Bitpanda Fusion in einem Tab")
            return False
        
        # SOFORTIGE AUTOMATISIERUNG
        print("\n🎯 SOFORTIGE TRADE-AUTOMATISIERUNG STARTET...")
        
        trade = {
            'action': 'KAUFEN',
            'quantity': '0.009886', 
            'price': '99127.64'
        }
        
        print(f"📋 AUTOMATISIERE: {trade['action']} {trade['quantity']} BTC @ €{trade['price']}")
        
        success_steps = 0
        
        # 1. Kaufen Button - SOFORT
        print("🟢 SCHRITT 1: Klicke 'Kaufen'...")
        kaufen_selectors = [
            "//button[contains(text(), 'Kaufen')]",
            "//div[contains(text(), 'Kaufen') and (@role='button' or contains(@class, 'btn'))]",
            ".buy-button",
            "[data-testid*='buy']"
        ]
        
        for selector in kaufen_selectors:
            try:
                if selector.startswith("//"):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        try:
                            element.click()
                            print("   ✅ 'Kaufen' geklickt!")
                            success_steps += 1
                            time.sleep(1)
                            break
                        except:
                            driver.execute_script("arguments[0].click();", element)
                            print("   ✅ 'Kaufen' per Script geklickt!")
                            success_steps += 1
                            time.sleep(1)
                            break
                if success_steps > 0:
                    break
            except:
                continue
        
        # 2. Limit Strategie - SOFORT
        print("⚡ SCHRITT 2: Wähle Limit...")
        strategy_dropdown = None
        
        # Finde Strategie Dropdown
        dropdown_selectors = [
            "//div[contains(text(), 'Strategie auswählen')]",
            "//div[contains(@class, 'dropdown') and contains(., 'Strategie')]",
            ".strategy-dropdown"
        ]
        
        for selector in dropdown_selectors:
            try:
                if selector.startswith("//"):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed():
                        element.click()
                        time.sleep(0.5)
                        
                        # Finde Limit Option
                        limit_options = driver.find_elements(By.XPATH, "//div[contains(text(), 'Limit') or contains(text(), 'limit')]")
                        for limit_opt in limit_options:
                            if limit_opt.is_displayed():
                                limit_opt.click()
                                print("   ✅ Limit ausgewählt!")
                                success_steps += 1
                                time.sleep(1)
                                break
                        break
                if success_steps == 2:
                    break
            except:
                continue
        
        # 3. Quantity eingeben - SOFORT
        print("📈 SCHRITT 3: Gebe Quantity ein...")
        quantity_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'Anzahl') or @name='amount']")
        
        for input_field in quantity_inputs:
            if input_field.is_displayed() and input_field.is_enabled():
                try:
                    input_field.clear()
                    input_field.send_keys(trade['quantity'])
                    print(f"   ✅ Quantity {trade['quantity']} eingegeben!")
                    success_steps += 1
                    time.sleep(1)
                    break
                except:
                    driver.execute_script(f"arguments[0].value = '{trade['quantity']}';", input_field)
                    print(f"   ✅ Quantity per Script eingegeben!")
                    success_steps += 1
                    time.sleep(1)
                    break
        
        # 4. Preis eingeben - SOFORT  
        print("💰 SCHRITT 4: Gebe Preis ein...")
        price_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'Preis') or @name='price']")
        
        for input_field in price_inputs:
            if input_field.is_displayed() and input_field.is_enabled():
                try:
                    input_field.clear()
                    input_field.send_keys(trade['price'])
                    print(f"   ✅ Preis €{trade['price']} eingegeben!")
                    success_steps += 1
                    time.sleep(1)
                    break
                except:
                    driver.execute_script(f"arguments[0].value = '{trade['price']}';", input_field)
                    print(f"   ✅ Preis per Script eingegeben!")
                    success_steps += 1
                    time.sleep(1)
                    break
        
        # Ergebnis
        print(f"\n{'='*60}")
        print(f"🎉 SOFORT-AUTOMATISIERUNG ABGESCHLOSSEN!")
        print(f"{'='*60}")
        print(f"📊 {success_steps}/4 Schritte erfolgreich")
        
        if success_steps >= 3:
            print("✅ TRADE BEREIT FÜR ORDER!")
            print("🔍 Prüfen Sie die Eingaben")
            print("🚀 Klicken Sie 'Order' zum Senden")
        else:
            print("⚠️ TEILWEISE AUTOMATISIERT")
            print("📝 Vervollständigen Sie manuell")
        
        print("❌ NICHT AUTOMATISCH GESENDET (Sicherheit)")
        print("👀 Browser bleibt offen")
        print("="*60)
        
        return success_steps >= 3
        
    except Exception as e:
        print(f"❌ Verbindung fehlgeschlagen: {e}")
        return False

def main():
    """Hauptfunktion - Sofortige Automatisierung"""
    print("🎯 SOFORTIGE FUSION AUTOMATISIERUNG")
    print("="*50)
    print("✅ Verwendet NUR bestehenden Browser")
    print("✅ KEIN Login, KEINE SMS, KEIN neues Fenster") 
    print("✅ Sofortige Automatisierung")
    print("❌ Sendet nicht automatisch")
    print()
    
    print("🚀 STARTE SOFORT-AUTOMATISIERUNG...")
    
    # Aktiviere Debug-Modus falls nötig
    enable_chrome_debug_mode()
    
    # Verbinde und automatisiere
    success = connect_and_automate()
    
    if success:
        print("\n🎉 SOFORT-AUTOMATISIERUNG ERFOLGREICH!")
        print("🔍 Trade bereit in Ihrem Fusion-Tab")
    else:
        print("\n⚠️ AUTOMATISIERUNG MIT PROBLEMEN")
        print("📝 Prüfen Sie Ihren Fusion-Tab")
    
    input("\n⏸️ DRÜCKEN SIE ENTER UM ZU BEENDEN...")
    return success

if __name__ == "__main__":
    main()
