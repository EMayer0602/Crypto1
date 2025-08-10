#!/usr/bin/env python3
"""
BITPANDA FUSION WEB AUTOMATION
Automatisiert die Bitpanda Fusion Weboberfläche für Trading
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import pandas as pd

class BitpandaFusionAutomation:
    """Automatisiert Bitpanda Fusion Weboberfläche"""
    
    def __init__(self, headless=False):
        """Initialize web automation"""
        
        print("🤖 BITPANDA FUSION WEB AUTOMATION")
        print("=" * 60)
        print("🌐 Automatisiert die Weboberfläche für Trading")
        print("⚠️ Benötigt: Chrome Browser + ChromeDriver")
        print("=" * 60)
        
        # Chrome Optionen
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")  # Unsichtbar
        
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Chrome WebDriver gestartet")
        except Exception as e:
            print(f"❌ Fehler beim Starten des WebDrivers: {e}")
            print("💡 Installieren Sie ChromeDriver: https://chromedriver.chromium.org/")
            raise
        
        self.trade_log = []
        self.logged_in = False
    
    def login_to_bitpanda_fusion(self, email, password):
        """Login zu Bitpanda Fusion"""
        
        print("\n🔐 LOGIN ZU BITPANDA FUSION...")
        
        try:
            # Gehe zu Bitpanda Fusion
            fusion_url = "https://web.bitpanda.com/fusion"  # Oder die richtige Fusion URL
            self.driver.get(fusion_url)
            
            print("📍 Navigiert zu Bitpanda Fusion")
            time.sleep(3)
            
            # Suche Login-Elemente (müssen angepasst werden!)
            email_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))  # Beispiel - anpassen!
            )
            password_field = self.driver.find_element(By.NAME, "password")  # Beispiel
            
            # Eingabe Credentials
            email_field.send_keys(email)
            password_field.send_keys(password)
            
            # Login Button
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_button.click()
            
            # Warte auf erfolgreichen Login
            time.sleep(5)
            
            # Prüfe ob Login erfolgreich (Trading Dashboard sichtbar)
            if "dashboard" in self.driver.current_url.lower() or "trading" in self.driver.current_url.lower():
                print("✅ Login erfolgreich!")
                self.logged_in = True
                return True
            else:
                print("❌ Login fehlgeschlagen")
                return False
                
        except Exception as e:
            print(f"❌ Login Fehler: {e}")
            return False
    
    def navigate_to_trading(self):
        """Navigiere zum Trading Bereich"""
        
        if not self.logged_in:
            print("❌ Nicht eingeloggt!")
            return False
        
        try:
            print("\n📈 NAVIGIERE ZUM TRADING BEREICH...")
            
            # Suche Trading/Exchange Link (anpassen!)
            trading_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Trading')]"))
            )
            trading_link.click()
            
            time.sleep(3)
            print("✅ Trading Bereich erreicht")
            return True
            
        except Exception as e:
            print(f"❌ Navigation Fehler: {e}")
            return False
    
    def place_order(self, ticker, action, amount_eur, order_type="market"):
        """Platziere einen Order über die Weboberfläche"""
        
        print(f"\n📊 PLATZIERE ORDER: {action} {ticker} €{amount_eur}")
        
        try:
            # 1. Wähle Trading Pair
            pair_selector = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{ticker}')]"))
            )
            pair_selector.click()
            time.sleep(2)
            
            # 2. Wähle Buy/Sell Tab
            if action.upper() == "BUY":
                buy_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Buy')]")
                buy_tab.click()
            else:
                sell_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sell')]")
                sell_tab.click()
            
            time.sleep(1)
            
            # 3. Order Type auswählen (Market/Limit)
            if order_type.lower() == "market":
                market_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Market')]")
                market_btn.click()
            
            # 4. Amount eingeben
            amount_field = self.driver.find_element(By.NAME, "amount")  # Anpassen!
            amount_field.clear()
            amount_field.send_keys(str(amount_eur))
            
            time.sleep(1)
            
            # 5. Order bestätigen
            place_order_btn = self.driver.find_element(
                By.XPATH, f"//button[contains(text(), '{action.title()}')]"
            )
            place_order_btn.click()
            
            # 6. Bestätigung abwarten
            time.sleep(3)
            
            # 7. Erfolg prüfen (Toast notification, etc.)
            try:
                success_message = self.driver.find_element(
                    By.XPATH, "//div[contains(text(), 'Order placed') or contains(text(), 'Success')]"
                )
                print(f"✅ Order erfolgreich: {action} {ticker} €{amount_eur}")
                
                # Log trade
                trade_record = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ticker': ticker,
                    'action': action,
                    'amount_eur': amount_eur,
                    'order_type': order_type,
                    'status': 'PLACED',
                    'method': 'WEB_AUTOMATION'
                }
                self.trade_log.append(trade_record)
                
                return True
                
            except:
                print(f"⚠️ Order Status unbekannt für {ticker}")
                return False
                
        except Exception as e:
            print(f"❌ Order Fehler: {e}")
            return False
    
    def execute_trading_signals(self, signals):
        """Führe mehrere Trading Signale aus"""
        
        print(f"\n🚀 FÜHRE {len(signals)} TRADING SIGNALE AUS...")
        print("-" * 50)
        
        successful_orders = 0
        
        for signal in signals:
            ticker = signal.get('ticker', '')
            action = signal.get('action', '')
            amount = signal.get('amount_eur', 0)
            
            if ticker and action and amount > 0:
                success = self.place_order(ticker, action, amount)
                if success:
                    successful_orders += 1
                
                # Kurze Pause zwischen Orders
                time.sleep(2)
            else:
                print(f"⚠️ Ungültiges Signal: {signal}")
        
        print(f"\n📊 SIGNALE VERARBEITET:")
        print(f"✅ Erfolgreich: {successful_orders}")
        print(f"❌ Fehlgeschlagen: {len(signals) - successful_orders}")
        
        return successful_orders
    
    def save_trade_log(self):
        """Speichere Trade Log"""
        
        if self.trade_log:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"bitpanda_fusion_trades_{timestamp}.csv"
            
            df = pd.DataFrame(self.trade_log)
            df.to_csv(filename, index=False)
            
            print(f"💾 Trade Log gespeichert: {filename}")
            return filename
        
        return None
    
    def close(self):
        """Schließe Browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("🔴 Browser geschlossen")

def test_bitpanda_fusion_automation():
    """Test der Bitpanda Fusion Automation"""
    
    print("🧪 BITPANDA FUSION AUTOMATION TEST")
    print("=" * 60)
    
    # ACHTUNG: Echte Credentials nicht im Code!
    email = input("📧 Bitpanda Email: ")
    password = input("🔐 Bitpanda Password: ")
    
    automation = BitpandaFusionAutomation(headless=False)  # Sichtbar für Testing
    
    try:
        # Login
        if automation.login_to_bitpanda_fusion(email, password):
            
            # Zum Trading navigieren
            if automation.navigate_to_trading():
                
                # Test Signale
                test_signals = [
                    {'ticker': 'BTC-EUR', 'action': 'BUY', 'amount_eur': 100},
                    {'ticker': 'ETH-EUR', 'action': 'BUY', 'amount_eur': 50},
                ]
                
                # Signale ausführen
                automation.execute_trading_signals(test_signals)
                
                # Log speichern
                automation.save_trade_log()
                
                print("🎉 Test abgeschlossen!")
            
    except Exception as e:
        print(f"❌ Test Fehler: {e}")
    
    finally:
        automation.close()

if __name__ == "__main__":
    print("⚠️ WICHTIGER HINWEIS:")
    print("1. ChromeDriver muss installiert sein")
    print("2. Die Element-Selektoren müssen an Bitpanda Fusion angepasst werden")
    print("3. Testen Sie zuerst mit kleinen Beträgen!")
    print("4. Web Automation ist fragiler als API")
    print()
    
    # Nur ausführen wenn explizit gewünscht
    response = input("Möchten Sie den Test starten? (ja/nein): ")
    if response.lower() in ['ja', 'j', 'yes', 'y']:
        test_bitpanda_fusion_automation()
    else:
        print("Test übersprungen.")
