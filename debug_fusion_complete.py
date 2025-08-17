#!/usr/bin/env python3
"""
Emergency UI Debug: SOL-EUR + MAX + BPS Probleme
Analysiert warum die Automatisierung nicht funktioniert
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def debug_fusion_ui():
    """Debug Fusion UI für SOL-EUR, MAX, BPS"""
    
    print("🔍 FUSION UI DEBUG - Probleme diagnostizieren")
    
    # Chrome setup
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("📱 Öffne Bitpanda Fusion...")
        driver.get("https://web.bitpanda.com/fusion")
        
        # Warte auf Fusion UI
        wait = WebDriverWait(driver, 30)
        
        print("⏳ Warte auf Fusion Interface...")
        time.sleep(5)
        
        # 1. SOL-EUR Debug
        print("\n🎯 1. SOL-EUR TICKER DEBUG:")
        sol_selectors = [
            "//div[contains(text(),'SOL-EUR')]",
            "//span[contains(text(),'SOL-EUR')]", 
            "//*[contains(text(),'SOL')]",
            "//select//option[contains(text(),'SOL')]",
            "//*[@role='option' and contains(text(),'SOL')]"
        ]
        
        for i, sel in enumerate(sol_selectors):
            try:
                elements = driver.find_elements(By.XPATH, sel)
                print(f"   Selector {i+1}: {len(elements)} SOL elements gefunden")
                for elem in elements[:3]:  # Nur erste 3
                    print(f"     → Text: '{elem.text}' | Visible: {elem.is_displayed()}")
            except Exception as e:
                print(f"   Selector {i+1}: ERROR - {e}")
        
        # 2. MAX Button Debug  
        print("\n🔘 2. MAX BUTTON DEBUG:")
        max_selectors = [
            "//button[normalize-space()='MAX']",
            "//button[contains(text(),'Max')]",
            "//button[contains(text(),'max')]",
            "//*[@role='button' and contains(text(),'MAX')]",
            "//*[contains(@class,'button') and contains(text(),'Max')]"
        ]
        
        for i, sel in enumerate(max_selectors):
            try:
                elements = driver.find_elements(By.XPATH, sel)
                print(f"   Selector {i+1}: {len(elements)} MAX elements gefunden")
                for elem in elements[:3]:
                    print(f"     → Text: '{elem.text}' | Visible: {elem.is_displayed()} | Enabled: {elem.is_enabled()}")
            except Exception as e:
                print(f"   Selector {i+1}: ERROR - {e}")
        
        # 3. BPS Button Debug
        print("\n📊 3. BPS BUTTONS DEBUG:")
        bps_selectors = [
            "//button[contains(text(),'+25')]",
            "//button[contains(text(),'-25')]", 
            "//button[contains(text(),'25bps')]",
            "//button[contains(text(),'bps')]",
            "//*[@role='button' and contains(text(),'25')]"
        ]
        
        for i, sel in enumerate(bps_selectors):
            try:
                elements = driver.find_elements(By.XPATH, sel)
                print(f"   Selector {i+1}: {len(elements)} BPS elements gefunden")
                for elem in elements[:3]:
                    print(f"     → Text: '{elem.text}' | Visible: {elem.is_displayed()} | Enabled: {elem.is_enabled()}")
            except Exception as e:
                print(f"   Selector {i+1}: ERROR - {e}")
        
        # 4. Limit Strategy Debug
        print("\n⚙️ 4. LIMIT STRATEGY DEBUG:")
        limit_selectors = [
            "//button[contains(text(),'Limit')]",
            "//div[contains(text(),'Limit')]",
            "//*[@role='tab' and contains(text(),'Limit')]",
            "//select//option[contains(text(),'Limit')]"
        ]
        
        for i, sel in enumerate(limit_selectors):
            try:
                elements = driver.find_elements(By.XPATH, sel)
                print(f"   Selector {i+1}: {len(elements)} LIMIT elements gefunden")
                for elem in elements[:3]:
                    print(f"     → Text: '{elem.text}' | Visible: {elem.is_displayed()} | Enabled: {elem.is_enabled()}")
            except Exception as e:
                print(f"   Selector {i+1}: ERROR - {e}")
        
        # 5. Gesamte UI Struktur
        print("\n🏗️ 5. UI STRUKTUR DEBUG:")
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"   Gesamte Buttons: {len(all_buttons)}")
            
            visible_buttons = [b for b in all_buttons if b.is_displayed() and b.text.strip()]
            print(f"   Sichtbare Buttons mit Text: {len(visible_buttons)}")
            
            print("   Top 10 sichtbare Buttons:")
            for i, btn in enumerate(visible_buttons[:10]):
                print(f"     {i+1}. '{btn.text[:30]}' | Classes: {btn.get_attribute('class')}")
        except Exception as e:
            print(f"   UI Struktur ERROR: {e}")
        
        print("\n✋ Debug abgeschlossen. Browser bleibt 30s offen für manuelle Inspektion...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ DEBUG ERROR: {e}")
    finally:
        driver.quit()
        print("🔚 Browser geschlossen")

if __name__ == "__main__":
    debug_fusion_ui()
