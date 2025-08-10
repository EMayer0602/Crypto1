#!/usr/bin/env python3
"""
Automatisierte Bitpanda Fusion Trade Eingabe
==========================================

Automatisiert die komplette Eingabe des ersten Trades in Bitpanda Fusion.
- Öffnet Browser automatisch
- Navigiert zu Fusion
- Gibt Trade-Details automatisch ein
- SENDET NICHT automatisch (manuelle Prüfung möglich)

Created: August 10, 2025
"""

import os
import sys
import pandas as pd
import time
from datetime import datetime
import json

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("❌ Selenium nicht installiert!")
    print("💡 Installation: pip install selenium")
    print("💡 ChromeDriver: https://chromedriver.chromium.org/")
    sys.exit(1)

class AutomatedFusionTradeEntry:
    """Vollständig automatisierte Trade-Eingabe in Bitpanda Fusion"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.first_trade = None
        self.debug_mode = True
        
        print("🤖 AUTOMATISIERTE BITPANDA FUSION TRADE EINGABE")
        print("="*60)
        print("✅ Vollständig automatisiert")
        print("❌ Sendet NICHT automatisch (manuelle Bestätigung)")
        print()
        
    def load_first_trade(self):
        """Lädt den ersten Trade"""
        print("📋 Lade ersten Trade...")
        
        trades_file = "TODAY_ONLY_trades_20250810_093857.csv"
        
        if not os.path.exists(trades_file):
            print(f"❌ Datei nicht gefunden: {trades_file}")
            return False
        
        try:
            df = pd.read_csv(trades_file, delimiter=';')
            
            if len(df) == 0:
                print("❌ Keine Trades")
                return False
            
            first_row = df.iloc[0]
            
            # Parse Trade-Details
            self.first_trade = {
                'pair': first_row['Ticker'],  # BTC-EUR
                'crypto': first_row['Ticker'].split('-')[0],  # BTC
                'action': 'BUY',  # Da es ein "Open" Trade ist
                'quantity': float(first_row['Quantity']),
                'limit_price': float(first_row['Limit Price']),
                'market_price': float(first_row['Realtime Price Bitpanda']),
                'order_type': 'Limit',
                'order_value': float(first_row['Quantity']) * float(first_row['Limit Price'])
            }
            
            print(f"✅ Trade geladen:")
            print(f"   🪙 {self.first_trade['action']} {self.first_trade['quantity']:.6f} {self.first_trade['pair']}")
            print(f"   💰 Limit: €{self.first_trade['limit_price']:.4f}")
            print(f"   📈 Markt: €{self.first_trade['market_price']:.4f}")
            print(f"   💵 Wert: €{self.first_trade['order_value']:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Laden: {str(e)}")
            return False
    
    def setup_browser(self):
        """Setup Chrome Browser mit optimalen Einstellungen"""
        print("🌐 Setup automatisierter Browser...")
        
        try:
            chrome_options = Options()
            
            # Optimale Einstellungen für Automation
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--start-maximized")
            
            # Anti-Detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User Agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Starte Chrome
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Anti-Detection Script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            self.wait = WebDriverWait(self.driver, 30)
            
            print("✅ Browser gestartet und konfiguriert")
            return True
            
        except Exception as e:
            print(f"❌ Browser Setup Fehler: {str(e)}")
            print("💡 Bitte ChromeDriver installieren und in PATH hinzufügen")
            return False
    
    def navigate_to_fusion(self):
        """Navigiert zu Bitpanda Fusion"""
        print("🔗 Öffne Bitpanda Fusion...")
        
        try:
            self.driver.get("https://web.bitpanda.com/")
            time.sleep(5)
            
            # Prüfe ob Seite geladen
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            print("✅ Bitpanda Webseite geladen")
            
            # Suche nach Fusion/Pro Link
            fusion_selectors = [
                "//a[contains(text(), 'Fusion')]",
                "//a[contains(text(), 'Pro')]",
                "//a[contains(text(), 'Advanced')]",
                "//a[contains(@href, 'fusion')]",
                "//a[contains(@href, 'pro')]"
            ]
            
            for selector in fusion_selectors:
                try:
                    fusion_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    fusion_link.click()
                    time.sleep(3)
                    print("✅ Fusion Link gefunden und geklickt")
                    break
                except:
                    continue
            else:
                # Direkt zu Fusion navigieren
                print("🔗 Navigiere direkt zu Fusion...")
                self.driver.get("https://web.bitpanda.com/fusion")
                time.sleep(5)
            
            print("✅ Bitpanda Fusion geöffnet")
            return True
            
        except Exception as e:
            print(f"❌ Navigation Fehler: {str(e)}")
            return False
    
    def wait_for_login(self):
        """Wartet auf manuellen Login"""
        print("🔐 LOGIN ERFORDERLICH")
        print("-"*30)
        print("📋 Bitte loggen Sie sich MANUELL ein:")
        print("   1. Email/Username eingeben")
        print("   2. Passwort eingeben") 
        print("   3. 2FA Code eingeben (falls erforderlich)")
        print("   4. Einloggen")
        print("   5. Warten bis Dashboard sichtbar")
        print()
        
        # Warte auf Login-Bestätigung
        input("⏸️ Drücken Sie ENTER wenn Sie eingeloggt sind und das Dashboard sehen...")
        
        time.sleep(3)
        print("✅ Login bestätigt")
        return True
    
    def navigate_to_trading(self):
        """Navigiert zum Trading-Bereich"""
        print("📈 Navigiere zu Trading...")
        
        try:
            # Verschiedene mögliche Trading-Links
            trading_selectors = [
                "//a[contains(text(), 'Trade')]",
                "//a[contains(text(), 'Trading')]",
                "//a[contains(text(), 'Exchange')]",
                "//button[contains(text(), 'Trade')]",
                "//nav//a[contains(@href, 'trade')]",
                "//nav//a[contains(@href, 'trading')]",
                "[data-testid*='trade']",
                "[href*='trade']"
            ]
            
            for selector in trading_selectors:
                try:
                    if selector.startswith("//"):
                        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    element.click()
                    time.sleep(5)
                    print("✅ Trading-Bereich geöffnet")
                    return True
                except:
                    continue
            
            print("⚠️ Trading-Link nicht automatisch gefunden")
            print("📋 Bitte navigieren Sie manuell zum Trading und drücken ENTER...")
            input("⏸️ ENTER wenn Sie im Trading-Bereich sind...")
            return True
            
        except Exception as e:
            print(f"❌ Trading Navigation Fehler: {str(e)}")
            return False
    
    def select_crypto_pair(self):
        """Wählt das Crypto-Paar aus"""
        crypto = self.first_trade['crypto']  # BTC
        pair = self.first_trade['pair']      # BTC-EUR
        
        print(f"🪙 Wähle {pair}...")
        
        try:
            # Suche nach Markt/Paar-Auswahl
            pair_selectors = [
                f"//span[contains(text(), '{crypto}')]",
                f"//span[contains(text(), '{pair}')]",
                f"//button[contains(text(), '{crypto}')]",
                f"//option[contains(text(), '{crypto}')]",
                f"//div[contains(text(), '{crypto}')]",
                f"[data-symbol='{crypto}']",
                f"[data-pair='{pair}']",
                f"[value='{crypto}']"
            ]
            
            for selector in pair_selectors:
                try:
                    if selector.startswith("//"):
                        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    element.click()
                    time.sleep(3)
                    print(f"✅ {pair} ausgewählt")
                    return True
                except:
                    continue
            
            # Suche nach Dropdown oder Search
            dropdown_selectors = [
                "//select[contains(@name, 'pair') or contains(@name, 'symbol')]",
                "//input[contains(@placeholder, 'Search') or contains(@placeholder, 'Symbol')]",
                ".pair-selector",
                ".symbol-search"
            ]
            
            for selector in dropdown_selectors:
                try:
                    if selector.startswith("//"):
                        element = self.driver.find_element(By.XPATH, selector)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if element.tag_name == 'select':
                        select = Select(element)
                        select.select_by_visible_text(crypto)
                    elif element.tag_name == 'input':
                        element.clear()
                        element.send_keys(crypto)
                        element.send_keys(Keys.ENTER)
                    
                    time.sleep(3)
                    print(f"✅ {pair} über Dropdown/Search ausgewählt")
                    return True
                except:
                    continue
            
            print(f"⚠️ {pair} nicht automatisch gefunden")
            print(f"📋 Bitte wählen Sie manuell {pair} aus und drücken ENTER...")
            input("⏸️ ENTER wenn richtiges Paar ausgewählt...")
            return True
            
        except Exception as e:
            print(f"❌ Paar-Auswahl Fehler: {str(e)}")
            return False
    
    def input_buy_order(self):
        """Gibt Buy Order Details ein"""
        print("📝 Gebe Buy Order ein...")
        
        quantity = self.first_trade['quantity']
        limit_price = self.first_trade['limit_price']
        
        try:
            # 1. BUY Button klicken
            print("🟢 Wähle BUY...")
            buy_selectors = [
                "//button[contains(text(), 'Buy') or contains(text(), 'BUY')]",
                "//span[contains(text(), 'Buy')]//parent::button",
                "//div[contains(text(), 'Buy')]//parent::button",
                "[data-testid*='buy']",
                "[data-side='buy']",
                ".buy-button",
                ".buy-tab"
            ]
            
            for selector in buy_selectors:
                try:
                    if selector.startswith("//"):
                        buy_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        buy_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    buy_btn.click()
                    time.sleep(2)
                    print("✅ Buy Button geklickt")
                    break
                except:
                    continue
            
            # 2. Limit Order wählen
            print("⚡ Wähle Limit Order...")
            limit_selectors = [
                "//button[contains(text(), 'Limit') or contains(text(), 'LIMIT')]",
                "//span[contains(text(), 'Limit')]",
                "//div[contains(text(), 'Limit')]",
                "[data-testid*='limit']",
                "[data-type='limit']",
                ".limit-button"
            ]
            
            for selector in limit_selectors:
                try:
                    if selector.startswith("//"):
                        limit_btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        limit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    limit_btn.click()
                    time.sleep(2)
                    print("✅ Limit Order gewählt")
                    break
                except:
                    continue
            
            # 3. Quantity eingeben
            print(f"📈 Gebe Quantity ein: {quantity:.6f}...")
            quantity_selectors = [
                "//input[@placeholder*='Amount' or @placeholder*='Quantity' or @placeholder*='Menge']",
                "//input[contains(@name, 'amount') or contains(@name, 'quantity')]",
                "//input[contains(@id, 'amount') or contains(@id, 'quantity')]",
                "[placeholder*='Amount']",
                "[placeholder*='Quantity']",
                "[name*='amount']",
                "[name*='quantity']",
                ".amount-input input",
                ".quantity-input input"
            ]
            
            quantity_entered = False
            for selector in quantity_selectors:
                try:
                    if selector.startswith("//"):
                        qty_input = self.driver.find_element(By.XPATH, selector)
                    else:
                        qty_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Clear und eingeben
                    qty_input.click()
                    qty_input.clear()
                    time.sleep(1)
                    qty_input.send_keys(Keys.CONTROL + "a")
                    qty_input.send_keys(str(quantity))
                    time.sleep(2)
                    
                    print(f"✅ Quantity eingegeben: {quantity:.6f}")
                    quantity_entered = True
                    break
                except:
                    continue
            
            if not quantity_entered:
                print("⚠️ Quantity nicht automatisch eingegeben")
                print(f"📋 Bitte geben Sie manuell ein: {quantity:.6f}")
                input("⏸️ ENTER wenn Quantity eingegeben...")
            
            # 4. Limit Price eingeben
            print(f"💰 Gebe Limit Price ein: €{limit_price:.4f}...")
            price_selectors = [
                "//input[@placeholder*='Price' or @placeholder*='Preis' or @placeholder*='Limit']",
                "//input[contains(@name, 'price') or contains(@name, 'limit')]",
                "//input[contains(@id, 'price') or contains(@id, 'limit')]",
                "[placeholder*='Price']",
                "[placeholder*='Limit']",
                "[name*='price']",
                "[name*='limit']",
                ".price-input input",
                ".limit-price-input input"
            ]
            
            price_entered = False
            for selector in price_selectors:
                try:
                    if selector.startswith("//"):
                        price_input = self.driver.find_element(By.XPATH, selector)
                    else:
                        price_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Clear und eingeben
                    price_input.click()
                    price_input.clear()
                    time.sleep(1)
                    price_input.send_keys(Keys.CONTROL + "a")
                    price_input.send_keys(str(limit_price))
                    time.sleep(2)
                    
                    print(f"✅ Limit Price eingegeben: €{limit_price:.4f}")
                    price_entered = True
                    break
                except:
                    continue
            
            if not price_entered:
                print("⚠️ Limit Price nicht automatisch eingegeben")
                print(f"📋 Bitte geben Sie manuell ein: €{limit_price:.4f}")
                input("⏸️ ENTER wenn Limit Price eingegeben...")
            
            time.sleep(3)
            print("✅ Alle Order-Details eingegeben!")
            return True
            
        except Exception as e:
            print(f"❌ Order Input Fehler: {str(e)}")
            return False
    
    def show_final_preview(self):
        """Zeigt finale Vorschau und lässt Benutzer entscheiden"""
        print("\n" + "="*60)
        print("🎯 AUTOMATISIERTE EINGABE ABGESCHLOSSEN")
        print("="*60)
        
        trade = self.first_trade
        print(f"✅ EINGEGEBEN IN BITPANDA FUSION:")
        print(f"   🪙 Paar: {trade['pair']}")
        print(f"   📊 Action: {trade['action']}")
        print(f"   📈 Quantity: {trade['quantity']:.6f}")
        print(f"   💰 Limit Price: €{trade['limit_price']:.4f}")
        print(f"   📍 Markt Price: €{trade['market_price']:.4f}")
        print(f"   💵 Order Value: €{trade['order_value']:.2f}")
        
        print(f"\n🔍 TRADE STATUS:")
        print(f"   ✅ Alle Felder automatisch ausgefüllt")
        print(f"   ❌ Trade wurde NICHT gesendet")
        print(f"   👀 Trade bereit zur manuellen Prüfung")
        
        print(f"\n📋 NÄCHSTE SCHRITTE:")
        print(f"   1. 🔍 Prüfen Sie alle Eingaben in der Fusion-Oberfläche")
        print(f"   2. ✏️ Anpassungen falls nötig")
        print(f"   3. 🚀 Manuell senden wenn korrekt")
        print(f"   4. ❌ Oder abbrechen/löschen")
        
        print("="*60)
        print("⏸️ Browser bleibt geöffnet für Ihre Entscheidung...")
        print("📋 Drücken Sie ENTER um Browser zu schließen...")
        
        input()
        return True
    
    def run(self):
        """Hauptausführung - Vollständige Automatisierung"""
        try:
            # 1. Trade laden
            if not self.load_first_trade():
                return False
            
            # 2. Browser setup
            if not self.setup_browser():
                return False
            
            # 3. Zu Fusion navigieren
            if not self.navigate_to_fusion():
                return False
            
            # 4. Warten auf manuellen Login
            if not self.wait_for_login():
                return False
            
            # 5. Zum Trading navigieren
            if not self.navigate_to_trading():
                return False
            
            # 6. Crypto-Paar auswählen
            if not self.select_crypto_pair():
                return False
            
            # 7. Buy Order eingeben
            if not self.input_buy_order():
                return False
            
            # 8. Finale Vorschau
            self.show_final_preview()
            
            return True
            
        except Exception as e:
            print(f"❌ Automatisierung Fehler: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔚 Browser geschlossen")

def main():
    """Hauptfunktion"""
    print("🤖 VOLLSTÄNDIG AUTOMATISIERTE FUSION TRADE EINGABE")
    print("="*60)
    print("✅ Öffnet Browser automatisch")
    print("✅ Navigiert zu Bitpanda Fusion")  
    print("✅ Gibt alle Trade-Details automatisch ein")
    print("❌ Sendet NICHT automatisch (Ihre Kontrolle)")
    print()
    
    # Prüfe Selenium Installation
    try:
        import selenium
        print("✅ Selenium verfügbar")
    except ImportError:
        print("❌ Selenium nicht installiert!")
        print("💡 Installation: pip install selenium")
        return False
    
    automation = AutomatedFusionTradeEntry()
    
    try:
        success = automation.run()
        
        if success:
            print("\n🎉 AUTOMATISIERTE EINGABE ERFOLGREICH!")
            print("🔍 Trade in Bitpanda Fusion eingegeben")
            print("📋 Bereit für Ihre manuelle Prüfung und Sendung")
        else:
            print("\n❌ AUTOMATISIERUNG FEHLGESCHLAGEN")
            print("🔧 Bitte Fehler prüfen und wiederholen")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⏹️ Automatisierung abgebrochen")
        return False
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {str(e)}")
        return False

if __name__ == "__main__":
    main()
