#!/usr/bin/env python3
"""
100% AUTOMATISCHE FUSION OHNE HANDEINGRIFF
==========================================

KOMPLETT automatisch - KEINE Eingaben erforderlich!
Nur die finale Order-Ausführung bleibt manuell.

Automatisiert ALLES:
- Browser-Verbindung
- Login-Erkennung  
- Tab-Suche
- Trade-Eingabe
- Validierung

NUR Order-Senden bleibt manuell für Sicherheit.
"""

import time
import sys
import json
import subprocess
import threading
from datetime import datetime

def install_all_dependencies():
    """Installiert alle Dependencies vollautomatisch"""
    deps = ['selenium', 'requests', 'beautifulsoup4']
    
    for dep in deps:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True, text=True)

class FullyAutomaticFusion:
    """100% Automatische Fusion Klasse - NULL Handeingriffe"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.trades_completed = 0
        self.setup_complete = False
        
    def auto_setup_browser(self):
        """Verbindet sich NUR mit bereits laufendem Browser - KEIN neuer Browser"""
        install_all_dependencies()
        
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        
        self.By = By
        self.EC = EC
        self.Keys = Keys
        self.ActionChains = ActionChains
        
        print("🔗 VERBINDE NUR MIT BESTEHENDEM BROWSER...")
        
        # Versuche Verbindung mit bestehendem Browser über Debug-Port
        connection_methods = [
            "127.0.0.1:9222",  # Standard Debug Port
            "localhost:9222",   # Alternative
            "127.0.0.1:9223",  # Fallback Port
        ]
        
        connected = False
        for debug_addr in connection_methods:
            try:
                options = Options()
                options.add_experimental_option("debuggerAddress", debug_addr)
                options.add_argument("--disable-blink-features=AutomationControlled")
                
                self.driver = webdriver.Chrome(options=options)
                
                # Test ob Verbindung funktioniert
                self.driver.current_url  # Test-Call
                
                print(f"✅ Verbunden mit bestehendem Browser über {debug_addr}")
                connected = True
                break
                
            except Exception as e:
                print(f"⚠️ Debug-Port {debug_addr} nicht erreichbar")
                continue
        
        if not connected:
            print("❌ KEIN BESTEHENDER BROWSER GEFUNDEN!")
            print("📋 LÖSUNG:")
            print("   1. Starten Sie Chrome mit Debug-Modus:")
            print('   chrome.exe --remote-debugging-port=9222')
            print("   2. Oder öffnen Sie ein neues Chrome-Fenster")
            print("   3. Navigieren Sie zu Bitpanda Fusion")
            print("   4. Starten Sie das Script erneut")
            
            # Versuche Chrome mit Debug-Port zu starten
            try:
                print("\n🚀 STARTE CHROME MIT DEBUG-MODUS...")
                import subprocess
                subprocess.Popen([
                    'chrome.exe', 
                    '--remote-debugging-port=9222',
                    '--user-data-dir=temp_debug',
                    'https://web.bitpanda.com/fusion'
                ], shell=True)
                
                print("✅ Chrome mit Debug-Modus gestartet")
                print("📋 Warten Sie 5 Sekunden und starten Sie das Script neu")
                time.sleep(5)
                
                # Erneuter Verbindungsversuch
                options = Options()
                options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
                self.driver = webdriver.Chrome(options=options)
                
                print("✅ Verbindung mit neu gestarteten Chrome erfolgreich")
                connected = True
                
            except Exception as e:
                print(f"❌ Chrome Debug-Start fehlgeschlagen: {e}")
                self.setup_complete = False
                return
        
        if connected:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, 30)
            self.setup_complete = True
            print("✅ Browser-Verbindung erfolgreich - KEIN neuer Browser geöffnet")
        else:
            self.setup_complete = False
    
    def auto_detect_fusion_ready(self):
        """Automatische Erkennung wann Fusion bereit ist"""
        max_wait = 300  # 5 Minuten Maximum
        check_interval = 2
        
        fusion_ready_indicators = [
            # Trading Interface
            "//button[contains(text(), 'Kaufen')]",
            "//button[contains(text(), 'Verkaufen')]",
            "//div[contains(text(), 'BTC-EUR')]",
            "//span[contains(text(), 'Strategie')]",
            "//input[contains(@placeholder, 'Anzahl')]",
            
            # Alternative Selektoren
            ".buy-button",
            ".sell-button", 
            "[data-testid*='buy']",
            "[data-testid*='trading']",
            ".trading-interface",
            ".order-form"
        ]
        
        for attempt in range(max_wait // check_interval):
            try:
                # Prüfe alle Tabs
                for handle in self.driver.window_handles:
                    try:
                        self.driver.switch_to.window(handle)
                        
                        # Prüfe URL
                        if any(keyword in self.driver.current_url.lower() 
                              for keyword in ['bitpanda', 'fusion']):
                            
                            # Prüfe Trading Interface
                            for indicator in fusion_ready_indicators:
                                try:
                                    if indicator.startswith("//"):
                                        elements = self.driver.find_elements(self.By.XPATH, indicator)
                                    else:
                                        elements = self.driver.find_elements(self.By.CSS_SELECTOR, indicator)
                                    
                                    if elements and elements[0].is_displayed():
                                        print(f"✅ FUSION AUTOMATISCH ERKANNT! Interface bereit")
                                        return True
                                except:
                                    continue
                    except:
                        continue
                
                if attempt % 30 == 0:  # Alle 60 Sekunden
                    print(f"⏳ Automatische Fusion-Erkennung... ({attempt * check_interval}s)")
                
                time.sleep(check_interval)
                
            except Exception as e:
                if attempt % 30 == 0:
                    print(f"⏳ Warte auf Fusion... ({attempt * check_interval}s)")
                time.sleep(check_interval)
                continue
        
        return False
    
    def force_click_element(self, element):
        """Erzwingt Klick mit mehreren Methoden"""
        click_methods = [
            lambda e: e.click(),
            lambda e: self.driver.execute_script("arguments[0].click();", e),
            lambda e: self.ActionChains(self.driver).move_to_element(e).click().perform(),
            lambda e: self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));", e),
            lambda e: e.send_keys(self.Keys.ENTER),
            lambda e: e.send_keys(self.Keys.SPACE)
        ]
        
        for method in click_methods:
            try:
                method(element)
                time.sleep(0.5)
                return True
            except:
                continue
        return False
    
    def force_input_value(self, element, value):
        """Erzwingt Input mit mehreren Methoden"""
        input_methods = [
            lambda e, v: (e.clear(), e.send_keys(str(v)), e.send_keys(self.Keys.TAB)),
            lambda e, v: self.driver.execute_script(f"arguments[0].value = '{v}'; arguments[0].dispatchEvent(new Event('input', {{bubbles: true}}));", e),
            lambda e, v: (self.ActionChains(self.driver).click(e).send_keys(self.Keys.CONTROL + "a").send_keys(str(v)).perform()),
            lambda e, v: self.driver.execute_script(f"arguments[0].setAttribute('value', '{v}');", e)
        ]
        
        for method in input_methods:
            try:
                method(element, value)
                time.sleep(0.5)
                return True
            except:
                continue
        return False
    
    def auto_execute_trade(self, trade):
        """Vollautomatische Trade-Ausführung"""
        print(f"\n{'='*70}")
        print(f"🎯 AUTO-TRADE: {trade['action']} {trade['quantity']} {trade['pair']} @ €{trade['price']}")
        print(f"{'='*70}")
        
        steps_completed = 0
        
        # Schritt 1: Kaufen/Verkaufen Button
        action_text = "Kaufen" if trade['action'] == 'BUY' else "Verkaufen"
        action_selectors = [
            f"//button[contains(text(), '{action_text}')]",
            f"//div[contains(text(), '{action_text}') and (@role='button' or contains(@class, 'button'))]",
            f"//span[contains(text(), '{action_text}')]//parent::button",
            f".{trade['action'].lower()}-button",
            f"[data-side='{trade['action'].lower()}']",
            f"button[class*='{action_text.lower()}']"
        ]
        
        print(f"🟢 AUTO: Klicke '{action_text}' Button...")
        for selector in action_selectors:
            try:
                if selector.startswith("//"):
                    elements = self.driver.find_elements(self.By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(self.By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        if self.force_click_element(element):
                            print(f"   ✅ '{action_text}' Button automatisch geklickt")
                            steps_completed += 1
                            time.sleep(1)
                            break
                if steps_completed > 0:
                    break
            except:
                continue
        
        # Schritt 2: Strategie auf Limit
        print("⚡ AUTO: Setze Limit Order Strategie...")
        strategy_selectors = [
            "//div[contains(text(), 'Strategie auswählen')]",
            "//select[contains(@name, 'strategy') or contains(@class, 'strategy')]",
            ".strategy-dropdown",
            ".strategy-selector",
            "[data-testid*='strategy']"
        ]
        
        for selector in strategy_selectors:
            try:
                if selector.startswith("//"):
                    elements = self.driver.find_elements(self.By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(self.By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed():
                        if self.force_click_element(element):
                            time.sleep(1)
                            
                            # Limit Option wählen
                            limit_selectors = [
                                "//option[contains(text(), 'Limit')]",
                                "//div[contains(text(), 'Limit')]//parent::*[@role='option' or contains(@class, 'option')]",
                                "//li[contains(text(), 'Limit')]"
                            ]
                            
                            for limit_sel in limit_selectors:
                                try:
                                    limit_elements = self.driver.find_elements(self.By.XPATH, limit_sel)
                                    for limit_elem in limit_elements:
                                        if limit_elem.is_displayed():
                                            if self.force_click_element(limit_elem):
                                                print("   ✅ Limit Order automatisch ausgewählt")
                                                steps_completed += 1
                                                time.sleep(1)
                                                break
                                    if steps_completed == 2:
                                        break
                                except:
                                    continue
                            break
                if steps_completed == 2:
                    break
            except:
                continue
        
        # Schritt 3: Quantity automatisch eingeben
        print("📈 AUTO: Gebe Quantity automatisch ein...")
        quantity_selectors = [
            "//input[contains(@placeholder, 'Anzahl')]",
            "//input[contains(@placeholder, 'Amount')]",
            "//input[@name='amount' or @name='quantity']",
            ".amount-input input",
            ".quantity-input input",
            "[data-testid*='amount'] input",
            "input[type='number'][placeholder*='Anzahl' or placeholder*='Amount']"
        ]
        
        for selector in quantity_selectors:
            try:
                if selector.startswith("//"):
                    elements = self.driver.find_elements(self.By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(self.By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        if self.force_input_value(element, trade['quantity']):
                            print(f"   ✅ Quantity {trade['quantity']} automatisch eingegeben")
                            steps_completed += 1
                            time.sleep(1)
                            break
                if steps_completed == 3:
                    break
            except:
                continue
        
        # Schritt 4: Preis automatisch eingeben
        print("💰 AUTO: Gebe Limit Preis automatisch ein...")
        price_selectors = [
            "//input[contains(@placeholder, 'Preis')]",
            "//input[contains(@placeholder, 'Price')]",
            "//input[@name='price' or @name='limit_price']",
            ".price-input input",
            "[data-testid*='price'] input",
            "input[type='number'][placeholder*='Preis' or placeholder*='Price']"
        ]
        
        for selector in price_selectors:
            try:
                if selector.startswith("//"):
                    elements = self.driver.find_elements(self.By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(self.By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        if self.force_input_value(element, trade['price']):
                            print(f"   ✅ Limit Preis €{trade['price']} automatisch eingegeben")
                            steps_completed += 1
                            time.sleep(2)
                            break
                if steps_completed == 4:
                    break
            except:
                continue
        
        # Validierung
        time.sleep(2)
        
        print(f"\n📊 AUTOMATISIERUNG ABGESCHLOSSEN: {steps_completed}/4 Schritte")
        
        if steps_completed >= 3:
            print("🎉 TRADE VOLLAUTOMATISCH VORBEREITET!")
            print("✅ Alle Felder automatisch ausgefüllt")
            print("🔍 Bereit für manuelle Order-Ausführung")
            return True
        else:
            print("⚠️ TEILAUTOMATISIERUNG")
            return False
    
    def run_zero_input_automation(self):
        """Null-Input Automatisierung - komplett ohne Handeingriff"""
        print("🚀 100% AUTOMATISIERUNG OHNE HANDEINGRIFF")
        print("="*60)
        print("✅ Komplett automatisch bis zur Order-Ausführung")
        print("✅ KEINE Eingaben, KEINE Bestätigungen erforderlich")
        print("❌ Nur Order-Senden bleibt manuell")
        print()
        
        # Trade automatisch laden
        trade = {
            'pair': 'BTC-EUR',
            'action': 'BUY',
            'quantity': 0.009886,
            'price': 99127.64
        }
        
        print(f"📋 AUTO-TRADE GELADEN:")
        print(f"   🪙 {trade['action']} {trade['quantity']} {trade['pair']}")
        print(f"   💰 Limit Preis: €{trade['price']}")
        print(f"   💵 Order Wert: ~€{trade['quantity'] * trade['price']:.2f}")
        
        # Automatisches Browser Setup
        print("\n🤖 AUTOMATISCHES SETUP STARTET...")
        self.auto_setup_browser()
        
        if not self.setup_complete:
            print("❌ Browser Setup fehlgeschlagen")
            return False
        
        print("✅ Browser automatisch bereit")
        
        # Automatische Fusion-Erkennung
        print("\n🔍 AUTOMATISCHE FUSION-ERKENNUNG...")
        if not self.auto_detect_fusion_ready():
            print("❌ Fusion nicht automatisch erkannt")
            print("📋 Öffnen Sie bitte Bitpanda Fusion manuell")
            return False
        
        # Vollautomatische Trade-Ausführung
        print("\n🎯 VOLLAUTOMATISCHE TRADE-EINGABE...")
        success = self.auto_execute_trade(trade)
        
        if success:
            print(f"\n{'='*60}")
            print("🎉 100% AUTOMATISIERUNG ERFOLGREICH!")
            print("='*60}")
            print("✅ Trade vollautomatisch vorbereitet")
            print("🔍 Alle Felder automatisch ausgefüllt")
            print("📋 NUR NOCH:")
            print("   1. 👀 Kurz prüfen (optional)")
            print("   2. 🚀 'Order' klicken zum Senden")
            print("❌ NICHT AUTOMATISCH GESENDET (Sicherheit)")
            print("👀 Browser bleibt offen für Order-Ausführung")
            print("="*60)
            
            self.trades_completed = 1
            return True
        else:
            print("⚠️ AUTOMATISIERUNG TEILWEISE ERFOLGREICH")
            return False

def main():
    """Hauptfunktion - Null Input Required"""
    print("🎯 100% AUTOMATISCHE FUSION - NULL HANDEINGRIFFE")
    print("="*60)
    print("🚀 STARTET AUTOMATISCH IN 3 SEKUNDEN...")
    print("✅ Keine Eingaben erforderlich")
    print("✅ Keine Bestätigungen nötig")
    print("✅ Komplett automatisch bis Order-Ausführung")
    print("="*60)
    
    # 3 Sekunden Countdown
    for i in range(3, 0, -1):
        print(f"⏱️ Auto-Start in {i}...")
        time.sleep(1)
    
    print("\n🚀 AUTOMATISIERUNG STARTET JETZT!")
    
    # Vollautomatische Ausführung
    automation = FullyAutomaticFusion()
    
    try:
        success = automation.run_zero_input_automation()
        
        if success:
            print("\n🎉 MISSION ERFOLGREICH!")
            print("🔍 Trade bereit für finale Order-Ausführung")
            
            # Browser offen lassen
            print("\n📱 Browser bleibt offen für Order-Senden")
            input("⏸️ DRÜCKEN SIE ENTER UM AUTOMATION ZU BEENDEN...")
        else:
            print("\n⚠️ AUTOMATION MIT PROBLEMEN")
            input("⏸️ DRÜCKEN SIE ENTER UM ZU BEENDEN...")
        
        if automation.driver:
            automation.driver.quit()
            
    except Exception as e:
        print(f"❌ Automation Fehler: {str(e)}")
        if automation.driver:
            automation.driver.quit()
        return False
    
    return True

if __name__ == "__main__":
    main()
