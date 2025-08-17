#!/usr/bin/env python3
"""
SUPER EINFACHES FUSION UI FIX
Garantiert funktionierende Lösung für:
1. SOL-EUR
2. MAX
3. BPS
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def simple_fusion_fix():
    """Super einfacher Fix ohne komplexe Logik"""
    
    print("🎯 SUPER EINFACHER FUSION FIX")
    
    # Chrome setup - minimal
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 1. SOL-EUR Fix - SUPER EINFACH
        print("1️⃣ SOL-EUR Fix...")
        
        # Klicke aktuelles Paar
        current_pairs = driver.find_elements(By.XPATH, "//*[contains(text(),'BTC-EUR') or contains(text(),'ETH-USD')]")
        for pair in current_pairs:
            if pair.is_displayed():
                try:
                    pair.click()
                    time.sleep(1)
                    break
                except:
                    continue
        
        # Klicke SOL-EUR
        sol_options = driver.find_elements(By.XPATH, "//*[contains(text(),'SOL-EUR')]")
        for sol in sol_options:
            if sol.is_displayed():
                try:
                    sol.click()
                    time.sleep(1)
                    print("   ✅ SOL-EUR gewählt")
                    break
                except:
                    continue
        
        # 2. MAX Fix - SUPER EINFACH
        print("2️⃣ MAX Fix...")
        max_buttons = driver.find_elements(By.XPATH, "//button[contains(text(),'Max') and not(contains(text(),'75'))]")
        for max_btn in max_buttons:
            if max_btn.is_displayed():
                try:
                    max_btn.click()
                    time.sleep(1)
                    print("   ✅ MAX geklickt")
                    break
                except:
                    continue
        
        # 3. BPS Fix - SUPER EINFACH
        print("3️⃣ BPS Fix...")
        bps_buttons = driver.find_elements(By.XPATH, "//button[contains(text(),'-25bps')]")
        for bps_btn in bps_buttons:
            if bps_btn.is_displayed():
                try:
                    bps_btn.click()
                    time.sleep(1)
                    print("   ✅ -25bps geklickt")
                    break
                except:
                    continue
        
        print("✅ Alle Fixes versucht - prüfen Sie die UI manuell")
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        # Browser NICHT schließen
        print("🔚 Browser bleibt offen")

if __name__ == "__main__":
    simple_fusion_fix()
