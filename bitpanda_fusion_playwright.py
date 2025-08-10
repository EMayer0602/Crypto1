#!/usr/bin/env python3
"""
BITPANDA FUSION PLAYWRIGHT AUTOMATION
Modernere Alternative zu Selenium für Web Automation
"""

# Installation erforderlich: pip install playwright
# Danach: playwright install chromium

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright nicht installiert: pip install playwright")

import time
from datetime import datetime
import pandas as pd

class BitpandaFusionPlaywright:
    """Bitpanda Fusion Automation mit Playwright"""
    
    def __init__(self, headless=False):
        """Initialize Playwright automation"""
        
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright ist nicht installiert!")
        
        print("🎭 BITPANDA FUSION PLAYWRIGHT AUTOMATION")
        print("=" * 60)
        print("🌐 Modernere Web Automation mit Playwright")
        print("🚀 Schneller und zuverlässiger als Selenium")
        print("=" * 60)
        
        self.headless = headless
        self.trade_log = []
        self.page = None
        self.browser = None
    
    def start_browser(self):
        """Starte Browser"""
        
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
            )
            self.page = self.browser.new_page()
            
            # Set user agent
            self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            print("✅ Playwright Browser gestartet")
            return True
            
        except Exception as e:
            print(f"❌ Browser Start Fehler: {e}")
            return False
    
    def login_to_fusion(self, email, password):
        """Login zu Bitpanda Fusion mit Playwright"""
        
        print("\n🔐 LOGIN ZU BITPANDA FUSION (PLAYWRIGHT)...")
        
        try:
            # Navigate to Bitpanda Fusion
            fusion_url = "https://web.bitpanda.com"  # Hauptseite, dann zu Fusion
            self.page.goto(fusion_url)
            
            print("📍 Seite geladen")
            
            # Warte auf Login Elements
            self.page.wait_for_selector('input[type="email"], input[name="email"]', timeout=10000)
            
            # Fill login form
            email_selector = 'input[type="email"], input[name="email"]'
            password_selector = 'input[type="password"], input[name="password"]'
            
            self.page.fill(email_selector, email)
            self.page.fill(password_selector, password)
            
            # Submit login
            login_button = 'button[type="submit"], button:has-text("Sign in"), button:has-text("Login")'
            self.page.click(login_button)
            
            # Wait for login success
            self.page.wait_for_timeout(5000)
            
            # Check if logged in
            current_url = self.page.url
            if "dashboard" in current_url or "portfolio" in current_url:
                print("✅ Login erfolgreich!")
                return True
            else:
                print(f"❌ Login fehlgeschlagen - URL: {current_url}")
                return False
                
        except Exception as e:
            print(f"❌ Login Fehler: {e}")
            return False
    
    def navigate_to_fusion_trading(self):
        """Navigiere zu Fusion Trading"""
        
        try:
            print("\n📈 SUCHE FUSION TRADING BEREICH...")
            
            # Suche nach Fusion/Exchange/Trading Links
            possible_selectors = [
                'a:has-text("Fusion")',
                'a:has-text("Exchange")',
                'a:has-text("Trading")',
                'a:has-text("Pro")',
                '[data-testid="fusion-link"]',
                '[href*="fusion"]',
                '[href*="exchange"]'
            ]
            
            for selector in possible_selectors:
                try:
                    element = self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        print(f"✅ Gefunden: {selector}")
                        element.click()
                        self.page.wait_for_timeout(3000)
                        
                        # Check if we're in trading area
                        current_url = self.page.url
                        if "fusion" in current_url or "exchange" in current_url:
                            print("✅ Fusion Trading erreicht!")
                            return True
                        
                except:
                    continue
            
            print("❌ Fusion Trading Bereich nicht gefunden")
            return False
            
        except Exception as e:
            print(f"❌ Navigation Fehler: {e}")
            return False
    
    def place_fusion_order(self, ticker, action, amount_eur):
        """Platziere Order in Fusion"""
        
        print(f"\n📊 FUSION ORDER: {action} {ticker} €{amount_eur}")
        
        try:
            # 1. Trading Pair auswählen
            # Diese Selektoren müssen an die echte Bitpanda Fusion UI angepasst werden!
            
            pair_selector = f'text="{ticker}", [data-symbol="{ticker}"]'
            try:
                self.page.click(pair_selector, timeout=5000)
                self.page.wait_for_timeout(1000)
            except:
                print(f"⚠️ Trading Pair {ticker} nicht gefunden")
                return False
            
            # 2. Buy/Sell auswählen
            if action.upper() == "BUY":
                self.page.click('button:has-text("Buy"), [data-testid="buy-button"]')
            else:
                self.page.click('button:has-text("Sell"), [data-testid="sell-button"]')
            
            self.page.wait_for_timeout(500)
            
            # 3. Market Order
            market_selector = 'button:has-text("Market"), [data-order-type="market"]'
            try:
                self.page.click(market_selector)
            except:
                pass  # Möglicherweise schon ausgewählt
            
            # 4. Amount eingeben
            amount_selectors = [
                'input[name="amount"]',
                'input[placeholder*="Amount"]',
                'input[data-testid="amount-input"]',
                '.amount-input input'
            ]
            
            amount_filled = False
            for selector in amount_selectors:
                try:
                    self.page.fill(selector, str(amount_eur))
                    amount_filled = True
                    break
                except:
                    continue
            
            if not amount_filled:
                print("❌ Amount Input nicht gefunden")
                return False
            
            self.page.wait_for_timeout(500)
            
            # 5. Order platzieren
            place_order_selectors = [
                f'button:has-text("{action.title()}")',
                f'button:has-text("Place {action}")',
                '[data-testid="place-order-button"]',
                '.place-order-button'
            ]
            
            order_placed = False
            for selector in place_order_selectors:
                try:
                    self.page.click(selector)
                    order_placed = True
                    break
                except:
                    continue
            
            if not order_placed:
                print("❌ Place Order Button nicht gefunden")
                return False
            
            # 6. Bestätigung warten
            self.page.wait_for_timeout(3000)
            
            # 7. Erfolg prüfen
            success_selectors = [
                'text="Order placed"',
                'text="Success"',
                '[data-testid="success-message"]',
                '.success-message'
            ]
            
            for selector in success_selectors:
                try:
                    if self.page.is_visible(selector):
                        print(f"✅ Order erfolgreich: {action} {ticker} €{amount_eur}")
                        
                        # Log trade
                        trade_record = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'ticker': ticker,
                            'action': action,
                            'amount_eur': amount_eur,
                            'status': 'PLACED',
                            'method': 'PLAYWRIGHT_FUSION'
                        }
                        self.trade_log.append(trade_record)
                        
                        return True
                except:
                    continue
            
            print(f"⚠️ Order Status unbekannt für {ticker}")
            return False
            
        except Exception as e:
            print(f"❌ Order Fehler: {e}")
            return False
    
    def close_browser(self):
        """Browser schließen"""
        
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        
        print("🔴 Playwright Browser geschlossen")

def create_installation_guide():
    """Erstelle Installationsanleitung"""
    
    guide = """
🛠️ BITPANDA FUSION WEB AUTOMATION - INSTALLATION
===============================================

SCHRITT 1: SELENIUM INSTALLIEREN
--------------------------------
pip install selenium pandas

SCHRITT 2: CHROMEDRIVER DOWNLOADEN
----------------------------------
1. Gehe zu: https://chromedriver.chromium.org/
2. Lade ChromeDriver für deine Chrome Version
3. Extrahiere chromedriver.exe in diesen Ordner ODER
4. Füge ChromeDriver zu PATH hinzu

SCHRITT 3: PLAYWRIGHT INSTALLIEREN (EMPFOHLEN)
----------------------------------------------
pip install playwright pandas
playwright install chromium

SCHRITT 4: BITPANDA FUSION ELEMENT-SELEKTOREN ANPASSEN
------------------------------------------------------
1. Öffne Bitpanda Fusion im Browser
2. Rechtsklick → "Element untersuchen" 
3. Finde die echten CSS-Selektoren für:
   - Login Felder
   - Trading Pair Selektor  
   - Buy/Sell Buttons
   - Amount Input
   - Place Order Button
4. Passe die Selektoren im Code an

SCHRITT 5: VORSICHTIG TESTEN!
----------------------------
1. Teste zuerst mit KLEINEN Beträgen
2. Überwache die Ausführung manuell
3. Web Automation kann fehlschlagen bei:
   - UI-Änderungen
   - Netzwerkproblemen
   - CAPTCHA/2FA

VORTEILE:
✅ Funktioniert ohne API
✅ Kann echte Orders platzieren
✅ Nutzt bestehende Bitpanda Fusion

NACHTEILE:
❌ Fragil bei UI-Änderungen
❌ Langsamer als API
❌ Schwerer zu debuggen
❌ Kann durch CAPTCHA blockiert werden

EMPFEHLUNG:
💡 Für Production: Echter Trading API Broker (Binance, Kraken)
🧪 Für Testing: Web Automation OK
"""
    
    with open("BITPANDA_WEB_AUTOMATION_GUIDE.md", "w", encoding='utf-8') as f:
        f.write(guide)
    
    print("📋 Installationsanleitung erstellt: BITPANDA_WEB_AUTOMATION_GUIDE.md")

if __name__ == "__main__":
    create_installation_guide()
    print("📋 Installationsanleitung erstellt!")
    print("⚠️ Bitte folgen Sie der Anleitung bevor Sie Web Automation testen")
