#!/usr/bin/env python3
"""
FUSION AUTOMATION - BESTEHENDER BROWSER
======================================

Verbindet sich mit Ihrem BEREITS LAUFENDEN Fusion-Browser.
Kein neuer Browser - arbeitet mit dem bestehenden Tab.

Trade: BUY 0.009886 BTC-EUR @ €99,127.64
"""

import time
import sys
import json
import subprocess
from datetime import datetime

def install_selenium():
    """Installiert Selenium falls nötig"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        return webdriver, Service, Options, By, WebDriverWait, EC, Keys, ActionChains
    except ImportError:
        print("📦 Installiere Selenium...")
        subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        return webdriver, Service, Options, By, WebDriverWait, EC, Keys, ActionChains

def connect_to_existing_browser():
    """Verbindet sich mit bereits laufendem Chrome Browser"""
    webdriver, Service, Options, By, WebDriverWait, EC, Keys, ActionChains = install_selenium()
    
    print("🔗 VERBINDE MIT BESTEHENDEM BROWSER...")
    
    try:
        # Chrome Options für bestehenden Browser
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        # Versuche Verbindung
        try:
            driver = webdriver.Chrome(options=options)
            print("✅ Verbindung mit bestehendem Browser erfolgreich!")
            return driver, By, WebDriverWait, EC, Keys, ActionChains
        except:
            print("⚠️ Kein Debug-Port gefunden. Starte Chrome mit Debug-Modus...")
            return start_chrome_with_debug()
            
    except Exception as e:
        print(f"❌ Verbindung fehlgeschlagen: {e}")
        return None, None, None, None, None, None

def start_chrome_with_debug():
    """Startet Chrome mit Debug-Port falls nötig"""
    webdriver, Service, Options, By, WebDriverWait, EC, Keys, ActionChains = install_selenium()
    
    print("🚀 STARTE CHROME MIT DEBUG-MODUS...")
    
    # Starte Chrome mit Debug-Port
    chrome_cmd = 'start chrome --remote-debugging-port=9222 --user-data-dir="%TEMP%\\chrome_debug"'
    subprocess.run(chrome_cmd, shell=True)
    time.sleep(3)
    
    # Verbinde mit Debug-Chrome
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Debug-Chrome gestartet und verbunden!")
        return driver, By, WebDriverWait, EC, Keys, ActionChains
    except Exception as e:
        print(f"❌ Debug-Chrome Fehler: {e}")
        return None, None, None, None, None, None

def find_fusion_tab(driver):
    """Findet den Fusion-Tab im Browser"""
    print("🔍 SUCHE FUSION TAB...")
    
    # Alle offenen Tabs durchgehen
    all_handles = driver.window_handles
    
    for handle in all_handles:
        try:
            driver.switch_to.window(handle)
            current_url = driver.current_url.lower()
            title = driver.title.lower()
            
            # Prüfe ob es Fusion/Bitpanda ist
            if any(keyword in current_url for keyword in ['bitpanda', 'fusion']):
                print(f"✅ Fusion Tab gefunden: {driver.title}")
                return True
            
            if any(keyword in title for keyword in ['bitpanda', 'fusion']):
                print(f"✅ Fusion Tab gefunden: {driver.title}")
                return True
                
        except Exception as e:
            continue
    
    print("❌ Fusion Tab nicht gefunden")
    print("📋 Verfügbare Tabs:")
    for i, handle in enumerate(all_handles):
        try:
            driver.switch_to.window(handle)
            print(f"   {i+1}. {driver.title} - {driver.current_url}")
        except:
            continue
    
    return False

def execute_trade_in_existing_browser(trade_data):
    """Führt Trade im bestehenden Browser aus"""
    print("🎯 AUTOMATISIERUNG IN BESTEHENDEM BROWSER")
    print("="*60)
    
    # Verbinde mit Browser
    components = connect_to_existing_browser()
    if not all(components):
        print("❌ Browser-Verbindung fehlgeschlagen")
        return False
    
    driver, By, WebDriverWait, EC, Keys, ActionChains = components
    wait = WebDriverWait(driver, 10)
    
    try:
        # Finde Fusion Tab
        if not find_fusion_tab(driver):
            print("❌ Fusion Tab nicht gefunden")
            print("📋 Öffnen Sie bitte Bitpanda Fusion in einem Tab")
            return False
        
        print("✅ Fusion Tab aktiv!")
        time.sleep(2)
        
        # Trade Details
        trade = {
            'pair': 'BTC-EUR',
            'action': 'KAUFEN',
            'quantity': '0.009886',
            'price': '99127.64'
        }
        
        print(f"📋 AUTOMATISIERE TRADE:")
        print(f"   🪙 {trade['action']} {trade['quantity']} BTC")
        print(f"   💰 Limit Preis: €{trade['price']}")
        
        success_count = 0
        
        # 1. Kaufen Button klicken
        print("🟢 1. Klicke 'Kaufen'...")
        kaufen_selectors = [
            "//button[contains(text(), 'Kaufen')]",
            "//div[contains(text(), 'Kaufen') and contains(@class, 'button')]",
            ".buy-button",
            "[data-testid*='buy']",
            "button[class*='buy']"
        ]
        
        kaufen_clicked = False
        for selector in kaufen_selectors:
            try:
                if selector.startswith("//"):
                    element = driver.find_element(By.XPATH, selector)
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                
                if element.is_displayed() and element.is_enabled():
                    # Verschiedene Klick-Methoden probieren
                    try:
                        element.click()
                        kaufen_clicked = True
                        print("   ✅ 'Kaufen' erfolgreich geklickt")
                        success_count += 1
                        time.sleep(1)
                        break
                    except:
                        try:
                            driver.execute_script("arguments[0].click();", element)
                            kaufen_clicked = True
                            print("   ✅ 'Kaufen' per Script geklickt")
                            success_count += 1
                            time.sleep(1)
                            break
                        except:
                            continue
            except:
                continue
        
        if not kaufen_clicked:
            print("   ⚠️ 'Kaufen' Button nicht gefunden - prüfen Sie das Interface")
        
        # 2. Strategie Dropdown öffnen und Limit wählen
        print("⚡ 2. Wähle Limit Strategie...")
        strategy_selectors = [
            "//div[contains(text(), 'Strategie auswählen')]",
            "//select[contains(@class, 'strategy')]",
            ".strategy-dropdown",
            "[data-testid*='strategy']"
        ]
        
        strategy_opened = False
        for selector in strategy_selectors:
            try:
                if selector.startswith("//"):
                    element = driver.find_element(By.XPATH, selector)
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                
                if element.is_displayed():
                    try:
                        element.click()
                        time.sleep(1)
                        strategy_opened = True
                        
                        # Suche Limit Option
                        limit_selectors = [
                            "//option[contains(text(), 'Limit')]",
                            "//div[contains(text(), 'Limit')]",
                            "//li[contains(text(), 'Limit')]"
                        ]
                        
                        for limit_sel in limit_selectors:
                            try:
                                limit_opt = driver.find_element(By.XPATH, limit_sel)
                                limit_opt.click()
                                print("   ✅ Limit Strategie ausgewählt")
                                success_count += 1
                                time.sleep(1)
                                break
                            except:
                                continue
                        break
                    except:
                        continue
            except:
                continue
        
        if not strategy_opened:
            print("   ⚠️ Strategie Dropdown nicht gefunden")
        
        # 3. Anzahl eingeben
        print("📈 3. Gebe Anzahl ein...")
        quantity_selectors = [
            "//input[contains(@placeholder, 'Anzahl')]",
            "//input[@name='amount']",
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
                
                if input_field.is_displayed() and input_field.is_enabled():
                    try:
                        input_field.clear()
                        input_field.send_keys(trade['quantity'])
                        input_field.send_keys(Keys.TAB)
                        quantity_entered = True
                        print(f"   ✅ Anzahl {trade['quantity']} eingegeben")
                        success_count += 1
                        time.sleep(1)
                        break
                    except:
                        try:
                            driver.execute_script(f"arguments[0].value = '{trade['quantity']}';", input_field)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", input_field)
                            quantity_entered = True
                            print(f"   ✅ Anzahl per Script eingegeben")
                            success_count += 1
                            time.sleep(1)
                            break
                        except:
                            continue
            except:
                continue
        
        if not quantity_entered:
            print(f"   ⚠️ Anzahl-Feld nicht gefunden - {trade['quantity']} manuell eingeben")
        
        # 4. Preis eingeben
        print("💰 4. Gebe Limit Preis ein...")
        price_selectors = [
            "//input[contains(@placeholder, 'Preis')]",
            "//input[@name='price']",
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
                
                if input_field.is_displayed() and input_field.is_enabled():
                    try:
                        input_field.clear()
                        input_field.send_keys(trade['price'])
                        input_field.send_keys(Keys.TAB)
                        price_entered = True
                        print(f"   ✅ Preis €{trade['price']} eingegeben")
                        success_count += 1
                        time.sleep(1)
                        break
                    except:
                        try:
                            driver.execute_script(f"arguments[0].value = '{trade['price']}';", input_field)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", input_field)
                            price_entered = True
                            print(f"   ✅ Preis per Script eingegeben")
                            success_count += 1
                            time.sleep(1)
                            break
                        except:
                            continue
            except:
                continue
        
        if not price_entered:
            print(f"   ⚠️ Preis-Feld nicht gefunden - €{trade['price']} manuell eingeben")
        
        # Final Status
        time.sleep(2)
        
        print(f"\n{'='*60}")
        print(f"🎉 AUTOMATISIERUNG ABGESCHLOSSEN!")
        print(f"{'='*60}")
        print(f"📊 {success_count}/4 Schritte erfolgreich")
        
        if success_count >= 3:
            print("✅ TRADE ERFOLGREICH VORBEREITET!")
            print("\n📋 NÄCHSTE SCHRITTE:")
            print("   1. 🔍 Prüfen Sie alle Eingaben")
            print("   2. 🚀 Klicken Sie 'Order' zum Senden")
            print("   3. ❌ Oder korrigieren Sie Eingaben")
        else:
            print("⚠️ TEILWEISE AUTOMATISIERT")
            print("📝 Vervollständigen Sie manuell")
        
        print(f"\n❌ TRADE NICHT AUTOMATISCH GESENDET!")
        print(f"👀 Browser-Tab bleibt für Ihre Kontrolle offen")
        print(f"{'='*60}")
        
        return success_count >= 3
        
    except Exception as e:
        print(f"❌ Automatisierung Fehler: {str(e)}")
        return False
    
    # Browser NICHT schließen - bleibt offen

def main():
    """Hauptfunktion für bestehenden Browser"""
    print("🎯 FUSION AUTOMATISIERUNG - BESTEHENDER BROWSER")
    print("="*60)
    print("✅ Verwendet Ihren BEREITS LAUFENDEN Browser")
    print("✅ Sucht automatisch Fusion-Tab")
    print("✅ Automatische Eingabe ohne neuen Browser")
    print("❌ Sendet NICHT automatisch")
    print()
    
    print("📋 WIRD AUTOMATISCH EINGEGEBEN:")
    print("   🪙 BTC-EUR Kaufen")
    print("   📈 Anzahl: 0.009886")
    print("   💰 Limit Preis: €99,127.64")
    
    print("\n⚠️ VORAUSSETZUNG:")
    print("   📱 Bitpanda Fusion muss in einem Browser-Tab offen sein")
    print("   🔐 Sie müssen bereits eingeloggt sein")
    
    confirm = input("\n🚀 Automatisierung in bestehendem Browser starten? (j/n): ")
    
    if confirm.lower() in ['j', 'ja', 'y', 'yes']:
        trade_data = {'pair': 'BTC-EUR', 'action': 'BUY', 'quantity': 0.009886, 'price': 99127.64}
        
        success = execute_trade_in_existing_browser(trade_data)
        
        if success:
            print("\n🎉 TRADE ERFOLGREICH AUTOMATISIERT!")
            print("🔍 Prüfen und senden Sie in Ihrem Fusion-Tab")
        else:
            print("\n⚠️ AUTOMATISIERUNG TEILWEISE ERFOLGREICH")
            print("📝 Vervollständigen Sie manuell in Fusion")
        
        return success
    else:
        print("❌ Automatisierung abgebrochen")
        return False

if __name__ == "__main__":
    main()
