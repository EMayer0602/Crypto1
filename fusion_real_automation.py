#!/usr/bin/env python3
"""
ECHTE BITPANDA FUSION AUTOMATISIERUNG
====================================

Automatisiert WIRKLICH die Eingabe des ersten Trades in Bitpanda Fusion.
Verwendet Playwright für robuste Browser-Automatisierung.

Trade: BUY 0.009886 BTC-EUR @ €99,127.64
"""

import asyncio
import sys
import time
from datetime import datetime

def install_playwright_if_needed():
    """Installiert Playwright falls nötig"""
    try:
        import playwright
        print("✅ Playwright bereits installiert")
        return True
    except ImportError:
        print("📦 Installiere Playwright...")
        import subprocess
        
        try:
            # Installiere playwright
            subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
            
            # Installiere Browser
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            
            print("✅ Playwright erfolgreich installiert")
            return True
        except Exception as e:
            print(f"❌ Playwright Installation fehlgeschlagen: {e}")
            return False

async def automate_fusion_trade():
    """Automatisiert den ersten Trade in Bitpanda Fusion"""
    
    print("🎯 ECHTE FUSION AUTOMATISIERUNG STARTET")
    print("="*50)
    
    # Trade Details
    trade = {
        'pair': 'BTC-EUR',
        'crypto': 'BTC',
        'action': 'BUY',
        'quantity': 0.009886,
        'limit_price': 99127.64,
        'market_price': 101150.66
    }
    
    print("📋 TRADE WIRD AUTOMATISCH EINGEGEBEN:")
    print(f"   🪙 {trade['action']} {trade['quantity']:.6f} {trade['crypto']}")
    print(f"   💰 Limit Price: €{trade['limit_price']:.2f}")
    print(f"   💵 Order Value: €{trade['quantity'] * trade['limit_price']:.2f}")
    
    try:
        from playwright.async_api import async_playwright
        
        print("\n🤖 STARTE BROWSER AUTOMATISIERUNG...")
        
        async with async_playwright() as p:
            # Browser starten
            print("🌐 Öffne Browser...")
            browser = await p.chromium.launch(
                headless=False,  # Sichtbarer Browser
                args=[
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            page = await browser.new_page()
            
            # User Agent setzen
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            print("✅ Browser gestartet")
            
            # Bitpanda öffnen
            print("🔗 Öffne Bitpanda Fusion...")
            await page.goto('https://web.bitpanda.com/fusion', wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            print("✅ Fusion geöffnet")
            
            # Warte auf Login
            print("\n🔐 WARTEN AUF LOGIN...")
            print("="*40)
            print("📋 Bitte loggen Sie sich ein:")
            print("   1. 📧 Email eingeben")
            print("   2. 🔑 Passwort eingeben") 
            print("   3. 🛡️ 2FA (falls nötig)")
            print("="*40)
            
            # Warte auf Trading Interface
            login_success = False
            max_wait = 120  # 2 Minuten warten
            
            for i in range(max_wait):
                try:
                    # Prüfe ob Trading Interface geladen ist
                    trading_elements = [
                        'text=BTC',
                        'text=Buy',
                        'text=Sell',
                        '[data-cy*="buy"]',
                        '[data-testid*="buy"]',
                        '.buy-button',
                        'button:has-text("Buy")'
                    ]
                    
                    for element in trading_elements:
                        try:
                            if await page.locator(element).count() > 0:
                                login_success = True
                                break
                        except:
                            continue
                    
                    if login_success:
                        break
                        
                    await page.wait_for_timeout(1000)
                    
                    if i % 10 == 0 and i > 0:
                        print(f"⏳ Warten auf Login... ({i}s)")
                        
                except:
                    continue
            
            if not login_success:
                print("❌ Login Timeout - Bitte versuchen Sie es nochmal")
                await browser.close()
                return False
            
            print("✅ Login erfolgreich erkannt!")
            
            # Automatische Trade Eingabe startet
            print("\n🤖 AUTOMATISCHE TRADE EINGABE STARTET...")
            print("="*50)
            
            success_steps = []
            
            # Schritt 1: BTC auswählen
            print("🪙 1. Suche und wähle BTC...")
            btc_found = False
            
            btc_selectors = [
                'text=BTC',
                '[data-symbol="BTC"]',
                '[data-testid*="BTC"]',
                'button:has-text("BTC")',
                '.asset-BTC',
                '.crypto-BTC'
            ]
            
            for selector in btc_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.locator(selector).first.click()
                        btc_found = True
                        success_steps.append("✅ BTC ausgewählt")
                        print("   ✅ BTC erfolgreich ausgewählt")
                        await page.wait_for_timeout(2000)
                        break
                except Exception as e:
                    continue
            
            if not btc_found:
                print("   ⚠️ BTC nicht automatisch gefunden - suche manuell...")
                # Versuche Suchfeld
                search_selectors = [
                    'input[placeholder*="Search"]',
                    'input[placeholder*="search"]',
                    '[data-testid*="search"]',
                    '.search-input'
                ]
                
                for search_sel in search_selectors:
                    try:
                        if await page.locator(search_sel).count() > 0:
                            await page.locator(search_sel).first.fill('BTC')
                            await page.wait_for_timeout(1000)
                            
                            # Klicke erstes Ergebnis
                            await page.locator('text=BTC').first.click()
                            btc_found = True
                            success_steps.append("✅ BTC über Suche ausgewählt")
                            print("   ✅ BTC über Suche gefunden")
                            break
                    except:
                        continue
            
            # Schritt 2: BUY Button
            print("🟢 2. Klicke BUY Button...")
            buy_found = False
            
            buy_selectors = [
                'button:has-text("Buy")',
                'button:has-text("BUY")',
                '[data-cy*="buy"]',
                '[data-testid*="buy"]',
                '.buy-button',
                '.btn-buy'
            ]
            
            for selector in buy_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.locator(selector).first.click()
                        buy_found = True
                        success_steps.append("✅ BUY Button geklickt")
                        print("   ✅ BUY Button erfolgreich geklickt")
                        await page.wait_for_timeout(2000)
                        break
                except:
                    continue
            
            # Schritt 3: Limit Order
            print("⚡ 3. Wähle Limit Order...")
            limit_found = False
            
            limit_selectors = [
                'button:has-text("Limit")',
                'text=Limit',
                '[data-type="limit"]',
                '[data-testid*="limit"]'
            ]
            
            for selector in limit_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.locator(selector).first.click()
                        limit_found = True
                        success_steps.append("✅ Limit Order ausgewählt")
                        print("   ✅ Limit Order erfolgreich ausgewählt")
                        await page.wait_for_timeout(1000)
                        break
                except:
                    continue
            
            # Schritt 4: Quantity eingeben
            print("📈 4. Gebe Quantity ein...")
            quantity_found = False
            
            quantity_selectors = [
                'input[placeholder*="Amount"]',
                'input[placeholder*="Quantity"]',
                'input[placeholder*="amount"]',
                '[data-testid*="amount"]',
                '[data-cy*="amount"]'
            ]
            
            for selector in quantity_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.locator(selector).first.clear()
                        await page.locator(selector).first.fill(str(trade['quantity']))
                        quantity_found = True
                        success_steps.append(f"✅ Quantity {trade['quantity']:.6f} eingegeben")
                        print(f"   ✅ Quantity {trade['quantity']:.6f} erfolgreich eingegeben")
                        await page.wait_for_timeout(1000)
                        break
                except:
                    continue
            
            # Schritt 5: Limit Price eingeben
            print("💰 5. Gebe Limit Price ein...")
            price_found = False
            
            price_selectors = [
                'input[placeholder*="Price"]',
                'input[placeholder*="price"]',
                '[data-testid*="price"]',
                '[data-cy*="price"]'
            ]
            
            for selector in price_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.locator(selector).first.clear()
                        await page.locator(selector).first.fill(str(trade['limit_price']))
                        price_found = True
                        success_steps.append(f"✅ Limit Price €{trade['limit_price']:.2f} eingegeben")
                        print(f"   ✅ Limit Price €{trade['limit_price']:.2f} erfolgreich eingegeben")
                        await page.wait_for_timeout(1000)
                        break
                except:
                    continue
            
            # Ergebnis
            await page.wait_for_timeout(2000)
            
            print("\n" + "="*50)
            print("🎉 AUTOMATISIERUNG ABGESCHLOSSEN!")
            print("="*50)
            
            print("📊 ERFOLGREICH AUSGEFÜHRT:")
            for step in success_steps:
                print(f"   {step}")
            
            total_steps = len(success_steps)
            print(f"\n✅ {total_steps}/5 Schritte erfolgreich automatisiert!")
            
            if total_steps >= 3:
                print("🎯 TRADE BEREIT FÜR MANUELLE ÜBERPRÜFUNG!")
                print("\n📋 NÄCHSTE SCHRITTE:")
                print("   1. 🔍 Prüfen Sie alle Eingaben")
                print("   2. ✏️ Korrigieren Sie falls nötig")
                print("   3. 🚀 Klicken Sie 'Place Order' zum Senden")
                print("   4. ❌ Oder schließen Sie den Browser zum Abbrechen")
            else:
                print("⚠️ TEILWEISE AUTOMATISIERUNG")
                print("📋 Bitte vervollständigen Sie manuell:")
                
                if not btc_found:
                    print("   🪙 BTC auswählen")
                if not buy_found:
                    print("   🟢 BUY Button klicken")
                if not limit_found:
                    print("   ⚡ Limit Order wählen")
                if not quantity_found:
                    print(f"   📈 Quantity: {trade['quantity']:.6f}")
                if not price_found:
                    print(f"   💰 Limit Price: €{trade['limit_price']:.2f}")
            
            print("\n❌ TRADE WIRD NICHT AUTOMATISCH GESENDET!")
            print("👀 Browser bleibt offen für Ihre Überprüfung")
            print("="*50)
            
            # Browser offen lassen
            input("⏸️ DRÜCKEN SIE ENTER UM BROWSER ZU SCHLIESSEN...")
            
            await browser.close()
            return True
            
    except Exception as e:
        print(f"❌ Fehler bei Automatisierung: {str(e)}")
        return False

async def main():
    """Hauptfunktion"""
    print("🎯 ECHTE BITPANDA FUSION AUTOMATISIERUNG")
    print("="*50)
    print("✅ Automatisiert ersten heutigen Trade")
    print("✅ Verwendet robuste Playwright Automatisierung")
    print("✅ Bleibt offen für manuelle Überprüfung")
    print("❌ Sendet NICHT automatisch")
    print()
    
    # Installiere Playwright falls nötig
    if not install_playwright_if_needed():
        print("❌ Playwright Installation fehlgeschlagen")
        return False
    
    print("🤖 STARTE ECHTE AUTOMATISIERUNG...")
    confirm = input("📋 Ersten Trade automatisch eingeben? (j/n): ")
    
    if confirm.lower() in ['j', 'ja', 'y', 'yes']:
        success = await automate_fusion_trade()
        
        if success:
            print("\n🎉 AUTOMATISIERUNG ABGESCHLOSSEN!")
            print("🔍 Browser bleibt offen für Ihre Überprüfung")
        else:
            print("\n❌ AUTOMATISIERUNG FEHLGESCHLAGEN")
        
        return success
    else:
        print("❌ Automatisierung abgebrochen")
        return False

if __name__ == "__main__":
    asyncio.run(main())
