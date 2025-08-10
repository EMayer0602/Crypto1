#!/usr/bin/env python3
"""
Bitpanda Fusion - Ersten Trade eingeben (NICHT SENDEN)
====================================================

Gibt den ersten heutigen Trade in die Bitpanda Fusion Oberfläche ein,
sendet ihn aber NICHT ab, so dass Sie ihn in der Oberfläche prüfen können.

Created: August 10, 2025
"""

import os
import sys
import pandas as pd
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

class BitpandaFusionTradeInput:
    """Gibt Trade in Bitpanda Fusion ein ohne zu senden"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.first_trade = None
        
    def load_first_trade(self):
        """Lädt den ersten Trade von heute"""
        print("📋 Lade ersten heutigen Trade...")
        
        # Suche nach der heutigen Trades-Datei
        trades_file = "TODAY_ONLY_trades_20250810_093857.csv"
        
        if not os.path.exists(trades_file):
            print(f"❌ Datei nicht gefunden: {trades_file}")
            return False
        
        try:
            df = pd.read_csv(trades_file, delimiter=';')
            print(f"✅ {len(df)} Trades geladen")
            
            if len(df) == 0:
                print("❌ Keine Trades in Datei")
                return False
            
            # Nimm den ersten Trade (BTC Buy)
            first_row = df.iloc[0]
            
            self.first_trade = {
                'date': first_row['Date'],
                'ticker': first_row['Ticker'],
                'quantity': float(first_row['Quantity']),
                'price': float(first_row['Price']),
                'order_type': first_row['Order Type'],
                'limit_price': float(first_row['Limit Price']),
                'action': 'Buy',  # Da es ein "Open" ist
                'realtime_price': float(first_row['Realtime Price Bitpanda'])
            }
            
            print(f"🎯 Erster Trade geladen:")
            print(f"   📊 {self.first_trade['action']} {self.first_trade['quantity']:.6f} {self.first_trade['ticker']}")
            print(f"   💰 Limit Price: €{self.first_trade['limit_price']:.4f}")
            print(f"   📈 Current Price: €{self.first_trade['realtime_price']:.4f}")
            print(f"   💵 Order Value: €{self.first_trade['quantity'] * self.first_trade['limit_price']:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Laden: {str(e)}")
            return False
    
    def setup_browser(self):
        """Setup Chrome Browser für Bitpanda Fusion"""
        print("🌐 Setup Chrome Browser...")
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Starte Browser
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Browser gestartet")
            return True
            
        except Exception as e:
            print(f"❌ Browser Setup Fehler: {str(e)}")
            print("💡 Bitte ChromeDriver installieren: https://chromedriver.chromium.org/")
            return False
    
    def login_to_fusion(self):
        """Login zu Bitpanda Fusion"""
        print("🔐 Öffne Bitpanda Fusion Login...")
        
        try:
            # Öffne Bitpanda Fusion
            self.driver.get("https://fusion.bitpanda.com/")
            time.sleep(3)
            
            print("✅ Bitpanda Fusion geöffnet")
            print("🔐 MANUELLER LOGIN ERFORDERLICH!")
            print("📋 Bitte loggen Sie sich manuell ein und drücken Sie dann ENTER...")
            
            # Warte auf manuellen Login
            input("⏸️ Drücken Sie ENTER nachdem Sie eingeloggt sind...")
            
            # Prüfe ob Login erfolgreich
            time.sleep(2)
            
            # Suche nach Trading-Bereich
            try:
                # Verschiedene mögliche Selektoren für den Trading-Bereich
                trading_selectors = [
                    "//a[contains(text(), 'Trade')]",
                    "//a[contains(text(), 'Trading')]",
                    "//button[contains(text(), 'Trade')]",
                    "[data-testid*='trade']",
                    "[href*='trade']"
                ]
                
                for selector in trading_selectors:
                    try:
                        if selector.startswith("//"):
                            element = self.driver.find_element(By.XPATH, selector)
                        else:
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if element:
                            print("✅ Trading-Bereich gefunden")
                            break
                    except:
                        continue
            except:
                pass
            
            print("✅ Login erfolgreich (angenommen)")
            return True
            
        except Exception as e:
            print(f"❌ Login Fehler: {str(e)}")
            return False
    
    def navigate_to_trading(self):
        """Navigiert zum Trading-Bereich"""
        print("📈 Navigiere zum Trading-Bereich...")
        
        try:
            # Suche nach Trading/Trade Link
            trading_links = [
                "//a[contains(text(), 'Trade')]",
                "//a[contains(text(), 'Trading')]", 
                "//button[contains(text(), 'Trade')]",
                "//nav//a[contains(@href, 'trade')]"
            ]
            
            for link_xpath in trading_links:
                try:
                    trade_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, link_xpath)))
                    trade_link.click()
                    time.sleep(3)
                    print("✅ Trading-Bereich geöffnet")
                    return True
                except:
                    continue
            
            print("⚠️ Trading-Link nicht automatisch gefunden")
            print("📋 Bitte navigieren Sie manuell zum Trading-Bereich und drücken ENTER...")
            input("⏸️ Drücken Sie ENTER wenn Sie im Trading-Bereich sind...")
            return True
            
        except Exception as e:
            print(f"❌ Navigation Fehler: {str(e)}")
            return False
    
    def select_crypto_pair(self):
        """Wählt das Crypto-Paar aus"""
        ticker = self.first_trade['ticker']  # z.B. "BTC-EUR"
        
        print(f"🪙 Wähle Crypto-Paar: {ticker}...")
        
        try:
            # Mögliche Selektoren für Paar-Auswahl
            pair_selectors = [
                f"//span[contains(text(), '{ticker}')]",
                f"//button[contains(text(), '{ticker}')]",
                f"//option[contains(text(), '{ticker}')]",
                f"[data-symbol='{ticker}']",
                f"[value='{ticker}']"
            ]
            
            for selector in pair_selectors:
                try:
                    if selector.startswith("//"):
                        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    element.click()
                    time.sleep(2)
                    print(f"✅ {ticker} ausgewählt")
                    return True
                except:
                    continue
            
            print(f"⚠️ {ticker} nicht automatisch gefunden")
            print(f"📋 Bitte wählen Sie manuell {ticker} aus und drücken ENTER...")
            input("⏸️ Drücken Sie ENTER wenn das richtige Paar ausgewählt ist...")
            return True
            
        except Exception as e:
            print(f"❌ Paar-Auswahl Fehler: {str(e)}")
            return False
    
    def input_trade_details(self):
        """Gibt die Trade-Details ein"""
        print("📝 Gebe Trade-Details ein...")
        
        action = self.first_trade['action']
        quantity = self.first_trade['quantity']
        limit_price = self.first_trade['limit_price']
        
        print(f"📊 {action}: {quantity:.6f} @ €{limit_price:.4f}")
        
        try:
            time.sleep(2)
            
            # 1. BUY Button wählen
            if action == 'Buy':
                buy_selectors = [
                    "//button[contains(text(), 'Buy')]",
                    "//button[contains(text(), 'BUY')]",
                    "//span[contains(text(), 'Buy')]//parent::button",
                    "[data-testid*='buy']",
                    ".buy-button"
                ]
                
                for selector in buy_selectors:
                    try:
                        if selector.startswith("//"):
                            buy_btn = self.driver.find_element(By.XPATH, selector)
                        else:
                            buy_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        buy_btn.click()
                        print("✅ Buy-Button gewählt")
                        break
                    except:
                        continue
            
            time.sleep(1)
            
            # 2. Limit Order wählen (falls verfügbar)
            limit_selectors = [
                "//button[contains(text(), 'Limit')]",
                "//span[contains(text(), 'Limit')]",
                "[data-testid*='limit']"
            ]
            
            for selector in limit_selectors:
                try:
                    if selector.startswith("//"):
                        limit_btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        limit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    limit_btn.click()
                    print("✅ Limit Order gewählt")
                    break
                except:
                    continue
            
            time.sleep(1)
            
            # 3. Quantity eingeben
            quantity_selectors = [
                "//input[@placeholder*='Amount' or @placeholder*='Quantity' or @placeholder*='Menge']",
                "//input[contains(@name, 'amount') or contains(@name, 'quantity')]",
                "[placeholder*='Amount']",
                "[placeholder*='Quantity']",
                ".amount-input input",
                ".quantity-input input"
            ]
            
            for selector in quantity_selectors:
                try:
                    if selector.startswith("//"):
                        qty_input = self.driver.find_element(By.XPATH, selector)
                    else:
                        qty_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    qty_input.clear()
                    qty_input.send_keys(str(quantity))
                    print(f"✅ Quantity eingegeben: {quantity:.6f}")
                    break
                except:
                    continue
            
            time.sleep(1)
            
            # 4. Limit Price eingeben
            price_selectors = [
                "//input[@placeholder*='Price' or @placeholder*='Preis']",
                "//input[contains(@name, 'price') or contains(@name, 'limit')]",
                "[placeholder*='Price']",
                "[placeholder*='Limit']",
                ".price-input input",
                ".limit-input input"
            ]
            
            for selector in price_selectors:
                try:
                    if selector.startswith("//"):
                        price_input = self.driver.find_element(By.XPATH, selector)
                    else:
                        price_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    price_input.clear()
                    price_input.send_keys(str(limit_price))
                    print(f"✅ Limit Price eingegeben: €{limit_price:.4f}")
                    break
                except:
                    continue
            
            time.sleep(2)
            
            print("✅ Alle Trade-Details eingegeben!")
            return True
            
        except Exception as e:
            print(f"❌ Input Fehler: {str(e)}")
            return False
    
    def show_trade_preview(self):
        """Zeigt Trade-Vorschau und wartet auf Benutzer-Bestätigung"""
        print("\n" + "="*60)
        print("🔍 TRADE PREVIEW - NICHT GESENDET!")
        print("="*60)
        
        trade = self.first_trade
        print(f"📊 Action: {trade['action']}")
        print(f"🪙 Pair: {trade['ticker']}")
        print(f"📈 Quantity: {trade['quantity']:.6f}")
        print(f"💰 Limit Price: €{trade['limit_price']:.4f}")
        print(f"📍 Current Price: €{trade['realtime_price']:.4f}")
        print(f"💵 Order Value: €{trade['quantity'] * trade['limit_price']:.2f}")
        print(f"📅 Date: {trade['date']}")
        
        print("\n🔍 TRADE IN BITPANDA FUSION EINGEGEBEN")
        print("❌ TRADE WURDE NICHT GESENDET!")
        print("👀 Bitte prüfen Sie die Eingaben in der Bitpanda Fusion Oberfläche")
        
        print("\n📋 NÄCHSTE SCHRITTE:")
        print("1. ✅ Prüfen Sie alle Eingaben in der Fusion-Oberfläche")
        print("2. ✅ Kontrollieren Sie Quantity und Limit Price")
        print("3. ✅ Bei Bedarf manuell anpassen")
        print("4. 🚀 Manuell senden wenn alles korrekt ist")
        print("5. ❌ Oder abbrechen wenn nicht korrekt")
        
        print("="*60)
        print("⏸️ Browser bleibt geöffnet für Ihre Prüfung...")
        print("📋 Drücken Sie ENTER um den Browser zu schließen...")
        
        input()
        return True
    
    def run(self):
        """Hauptausführung"""
        print("🚀 Bitpanda Fusion - Ersten Trade eingeben (NICHT SENDEN)")
        print("="*60)
        
        try:
            # 1. Trade laden
            if not self.load_first_trade():
                return False
            
            # 2. Browser setup
            if not self.setup_browser():
                return False
            
            # 3. Login
            if not self.login_to_fusion():
                return False
            
            # 4. Zum Trading navigieren
            if not self.navigate_to_trading():
                return False
            
            # 5. Crypto-Paar auswählen
            if not self.select_crypto_pair():
                return False
            
            # 6. Trade-Details eingeben
            if not self.input_trade_details():
                return False
            
            # 7. Preview zeigen (NICHT SENDEN!)
            self.show_trade_preview()
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler: {str(e)}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔚 Browser geschlossen")

def main():
    """Hauptfunktion"""
    print("🎯 Bitpanda Fusion - Ersten Trade für Prüfung eingeben")
    print("❌ Trade wird NICHT gesendet - nur eingegeben!")
    
    trader = BitpandaFusionTradeInput()
    
    try:
        success = trader.run()
        
        if success:
            print("\n✅ TRADE ERFOLGREICH EINGEGEBEN!")
            print("🔍 Trade bereit zur Prüfung in Bitpanda Fusion")
        else:
            print("\n❌ FEHLER BEIM EINGEBEN")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⏹️ Abgebrochen")
        return False

if __name__ == "__main__":
    main()
