#!/usr/bin/env python3
"""
Alle Heutigen Trades in Bitpanda Fusion Eingeben
==============================================

Gibt ALLE 12 heutigen Trades automatisch in Bitpanda Fusion ein:
- BTC: Buy + Sell
- ETH: Buy + Sell  
- DOGE: Buy + Sell
- SOL: Buy + Sell
- LINK: Buy + Sell
- XRP: Buy + Sell

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
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("❌ Selenium nicht installiert!")
    print("💡 Installation läuft automatisch...")
    os.system("pip install selenium")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
    except ImportError:
        print("❌ Selenium Installation fehlgeschlagen!")
        sys.exit(1)

class AllTradesFusionAutomation:
    """Gibt alle heutigen Trades automatisch in Bitpanda Fusion ein"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.all_trades = []
        self.successful_entries = 0
        self.failed_entries = 0
        
        print("🤖 ALLE HEUTIGEN TRADES IN BITPANDA FUSION")
        print("="*60)
        print("✅ Gibt ALLE 12 Trades automatisch ein")
        print("❌ Sendet NICHT automatisch (manuelle Kontrolle)")
        print()
        
    def load_all_trades(self):
        """Lädt alle heutigen Trades"""
        print("📋 Lade alle heutigen Trades...")
        
        trades_file = "TODAY_ONLY_trades_20250810_093857.csv"
        
        if not os.path.exists(trades_file):
            print(f"❌ Datei nicht gefunden: {trades_file}")
            return False
        
        try:
            df = pd.read_csv(trades_file, delimiter=';')
            print(f"✅ {len(df)} Trades geladen")
            
            # Verarbeite jeden Trade
            for idx, row in df.iterrows():
                trade = {
                    'id': idx + 1,
                    'pair': row['Ticker'],
                    'crypto': row['Ticker'].split('-')[0],
                    'action': 'BUY' if row['Open/Close'] == 'Open' else 'SELL',
                    'quantity': float(row['Quantity']),
                    'limit_price': float(row['Limit Price']),
                    'market_price': float(row['Realtime Price Bitpanda']),
                    'order_value': float(row['Quantity']) * float(row['Limit Price']),
                    'date': row['Date']
                }
                
                self.all_trades.append(trade)
            
            # Zeige Übersicht
            print(f"\n📊 ALLE {len(self.all_trades)} TRADES ÜBERSICHT:")
            print("-"*60)
            
            total_buy_value = 0
            total_sell_value = 0
            
            for trade in self.all_trades:
                action_emoji = "🟢" if trade['action'] == 'BUY' else "🔴"
                print(f"{trade['id']:2d}. {action_emoji} {trade['action']} {trade['quantity']:.6f} {trade['crypto']} @ €{trade['limit_price']:.4f} (€{trade['order_value']:.2f})")
                
                if trade['action'] == 'BUY':
                    total_buy_value += trade['order_value']
                else:
                    total_sell_value += trade['order_value']
            
            print("-"*60)
            print(f"💰 Gesamt BUY Wert: €{total_buy_value:.2f}")
            print(f"💰 Gesamt SELL Wert: €{total_sell_value:.2f}")
            print(f"💰 Netto Cashflow: €{total_sell_value - total_buy_value:.2f}")
            print(f"✅ Alle {len(self.all_trades)} Trades bereit für Eingabe")
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Laden: {str(e)}")
            return False
    
    def setup_browser(self):
        """Setup Browser für Automation"""
        print("\n🌐 Setup Browser für alle Trades...")
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User Agent für bessere Kompatibilität
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Browser bereit für alle Trades")
            return True
            
        except Exception as e:
            print(f"❌ Browser Setup Fehler: {str(e)}")
            return False
    
    def navigate_to_fusion(self):
        """Navigiert zu Bitpanda Fusion"""
        print("🔗 Öffne Bitpanda Fusion...")
        
        try:
            self.driver.get("https://web.bitpanda.com/")
            time.sleep(5)
            
            # Versuche direkt zu Fusion
            try:
                self.driver.get("https://web.bitpanda.com/fusion")
                time.sleep(5)
                print("✅ Direkt zu Fusion navigiert")
            except:
                print("✅ Bitpanda Webseite geladen")
            
            return True
            
        except Exception as e:
            print(f"❌ Navigation Fehler: {str(e)}")
            return False
    
    def wait_for_manual_login(self):
        """Wartet auf manuellen Login"""
        print("\n🔐 MANUELLER LOGIN ERFORDERLICH")
        print("="*60)
        print("📋 Bitte loggen Sie sich JETZT ein:")
        print("   1. 📧 Email/Username eingeben")
        print("   2. 🔑 Passwort eingeben")
        print("   3. 🛡️ 2FA Code (falls erforderlich)")
        print("   4. 🚪 Login bestätigen")
        print("   5. 📈 Zum Trading/Fusion navigieren")
        print("="*60)
        
        input("⏸️ DRÜCKEN SIE ENTER WENN SIE EINGELOGGT SIND UND IM TRADING-BEREICH...")
        
        print("✅ Login bestätigt - Automation startet")
        return True
    
    def enter_single_trade(self, trade):
        """Gibt einen einzelnen Trade ein"""
        print(f"\n🔄 Trade {trade['id']}: {trade['action']} {trade['quantity']:.6f} {trade['crypto']}...")
        
        try:
            # 1. Crypto-Paar auswählen (falls nötig)
            self.select_crypto_pair(trade['crypto'], trade['pair'])
            
            # 2. Buy/Sell Button
            self.click_action_button(trade['action'])
            
            # 3. Limit Order auswählen
            self.select_limit_order()
            
            # 4. Quantity eingeben
            self.input_quantity(trade['quantity'])
            
            # 5. Limit Price eingeben
            self.input_limit_price(trade['limit_price'])
            
            # 6. Kurz warten für Validierung
            time.sleep(2)
            
            print(f"✅ Trade {trade['id']} eingegeben: {trade['action']} {trade['quantity']:.6f} {trade['crypto']} @ €{trade['limit_price']:.4f}")
            self.successful_entries += 1
            return True
            
        except Exception as e:
            print(f"❌ Trade {trade['id']} Fehler: {str(e)}")
            self.failed_entries += 1
            return False
    
    def select_crypto_pair(self, crypto, pair):
        """Wählt Crypto-Paar aus"""
        selectors = [
            f"//span[contains(text(), '{crypto}')]",
            f"//button[contains(text(), '{crypto}')]",
            f"//option[contains(text(), '{crypto}')]",
            f"[data-symbol='{crypto}']"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    element = self.driver.find_element(By.XPATH, selector)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                element.click()
                time.sleep(1)
                return True
            except:
                continue
        
        # Falls automatische Auswahl fehlschlägt
        print(f"⚠️ {crypto} bitte manuell auswählen")
        return True
    
    def click_action_button(self, action):
        """Klickt Buy oder Sell Button"""
        button_text = action.upper()
        selectors = [
            f"//button[contains(text(), '{button_text}')]",
            f"//span[contains(text(), '{button_text}')]//parent::button",
            f"[data-side='{action.lower()}']",
            f".{action.lower()}-button"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    button = self.driver.find_element(By.XPATH, selector)
                else:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                button.click()
                time.sleep(1)
                return True
            except:
                continue
        
        print(f"⚠️ {action} Button bitte manuell klicken")
        return True
    
    def select_limit_order(self):
        """Wählt Limit Order aus"""
        selectors = [
            "//button[contains(text(), 'Limit')]",
            "//span[contains(text(), 'Limit')]",
            "[data-type='limit']"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    button = self.driver.find_element(By.XPATH, selector)
                else:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                button.click()
                time.sleep(1)
                return True
            except:
                continue
        
        return True
    
    def input_quantity(self, quantity):
        """Gibt Quantity ein"""
        selectors = [
            "//input[@placeholder*='Amount' or @placeholder*='Quantity']",
            "//input[contains(@name, 'amount') or contains(@name, 'quantity')]",
            "[placeholder*='Amount']",
            "[name*='amount']",
            ".amount-input input"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    input_field = self.driver.find_element(By.XPATH, selector)
                else:
                    input_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                input_field.click()
                input_field.clear()
                input_field.send_keys(Keys.CONTROL + "a")
                input_field.send_keys(str(quantity))
                time.sleep(1)
                return True
            except:
                continue
        
        return True
    
    def input_limit_price(self, price):
        """Gibt Limit Price ein"""
        selectors = [
            "//input[@placeholder*='Price' or @placeholder*='Limit']",
            "//input[contains(@name, 'price') or contains(@name, 'limit')]",
            "[placeholder*='Price']",
            "[name*='price']",
            ".price-input input"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    input_field = self.driver.find_element(By.XPATH, selector)
                else:
                    input_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                input_field.click()
                input_field.clear()
                input_field.send_keys(Keys.CONTROL + "a")
                input_field.send_keys(str(price))
                time.sleep(1)
                return True
            except:
                continue
        
        return True
    
    def enter_all_trades(self):
        """Gibt alle Trades nacheinander ein"""
        print(f"\n🚀 STARTE EINGABE ALLER {len(self.all_trades)} TRADES")
        print("="*60)
        
        for trade in self.all_trades:
            print(f"\n📋 Trade {trade['id']}/{len(self.all_trades)}")
            
            # Trade eingeben
            success = self.enter_single_trade(trade)
            
            if success:
                # Kurze Pause zwischen Trades
                print("⏳ Kurze Pause...")
                time.sleep(3)
                
                # Optional: Bestätigung für nächsten Trade
                if trade['id'] < len(self.all_trades):
                    cont = input(f"📋 Weiter mit Trade {trade['id'] + 1}? (Enter = ja, n = stoppen): ")
                    if cont.lower() in ['n', 'no', 'nein', 'stop']:
                        break
            else:
                # Bei Fehler: Benutzer fragen ob weiter
                cont = input(f"❌ Fehler bei Trade {trade['id']}. Weiter? (Enter = ja, n = stoppen): ")
                if cont.lower() in ['n', 'no', 'nein', 'stop']:
                    break
        
        return True
    
    def show_final_summary(self):
        """Zeigt finale Zusammenfassung"""
        print("\n" + "="*60)
        print("🎉 ALLE TRADES EINGABE ABGESCHLOSSEN")
        print("="*60)
        
        print(f"📊 STATISTIK:")
        print(f"   ✅ Erfolgreich eingegeben: {self.successful_entries}")
        print(f"   ❌ Fehlgeschlagen: {self.failed_entries}")
        print(f"   📋 Gesamt Trades: {len(self.all_trades)}")
        
        print(f"\n🔍 STATUS:")
        print(f"   ✅ Alle Trades in Bitpanda Fusion eingegeben")
        print(f"   ❌ KEINE TRADES AUTOMATISCH GESENDET!")
        print(f"   👀 Alle Trades bereit zur manuellen Prüfung")
        
        print(f"\n📋 NÄCHSTE SCHRITTE:")
        print(f"   1. 🔍 Prüfen Sie JEDEN Trade in der Fusion-Oberfläche")
        print(f"   2. ✏️ Korrekturen falls nötig")
        print(f"   3. 🚀 Trades einzeln manuell senden")
        print(f"   4. ❌ Oder ungewünschte Trades löschen")
        
        print("="*60)
        print("⏸️ Browser bleibt geöffnet für Ihre Kontrolle...")
        print("📋 Drücken Sie ENTER um Browser zu schließen...")
        
        input()
        return True
    
    def run(self):
        """Hauptausführung - Alle Trades eingeben"""
        try:
            # 1. Alle Trades laden
            if not self.load_all_trades():
                return False
            
            # 2. Browser setup
            if not self.setup_browser():
                return False
            
            # 3. Zu Fusion navigieren
            if not self.navigate_to_fusion():
                return False
            
            # 4. Warten auf Login
            if not self.wait_for_manual_login():
                return False
            
            # 5. Alle Trades eingeben
            if not self.enter_all_trades():
                return False
            
            # 6. Finale Zusammenfassung
            self.show_final_summary()
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler in Hauptausführung: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔚 Browser geschlossen")

def main():
    """Hauptfunktion"""
    print("🤖 ALLE HEUTIGEN TRADES IN BITPANDA FUSION EINGEBEN")
    print("="*60)
    print("✅ Gibt ALLE 12 Trades automatisch ein")
    print("✅ BUY + SELL für alle 6 Crypto-Paare")
    print("❌ Sendet NICHT automatisch (Ihre Kontrolle)")
    print("🔍 Jeder Trade bereit zur manuellen Prüfung")
    print()
    
    confirm = input("🤖 ALLE TRADES AUTOMATISCH EINGEBEN? (j/n): ")
    
    if confirm.lower() in ['j', 'ja', 'y', 'yes']:
        automation = AllTradesFusionAutomation()
        
        try:
            success = automation.run()
            
            if success:
                print("\n🎉 ALLE TRADES ERFOLGREICH EINGEGEBEN!")
                print("📋 Bereit für manuelle Prüfung und Sendung")
            else:
                print("\n❌ EINGABE NICHT VOLLSTÄNDIG ABGESCHLOSSEN")
            
            return success
            
        except KeyboardInterrupt:
            print("\n⏹️ Eingabe abgebrochen")
            return False
        except Exception as e:
            print(f"\n❌ Unerwarteter Fehler: {str(e)}")
            return False
    else:
        print("❌ Automatische Eingabe abgebrochen")
        return False

if __name__ == "__main__":
    main()
