#!/usr/bin/env python3
"""
UI Debug Helper - Zeigt mir genau was im Bitpanda Fusion UI passiert
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def get_ui_structure():
    """Verbinde mit Chrome und analysiere die UI-Struktur"""
    print("🔍 Verbinde mit Chrome...")
    
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Verbunden!")
        
        # 1. Zeige aktuelle URL
        print(f"📍 URL: {driver.current_url}")
        
        # 2. Zeige aktuell sichtbares Paar
        print("\n🔍 PAAR-SELEKTION:")
        try:
            # Suche nach allen Elementen die wie Paar-Anzeigen aussehen
            pair_candidates = driver.find_elements(By.XPATH, "//*[contains(text(),'EUR') or contains(text(),'USD') or contains(text(),'USDT')]")
            for i, el in enumerate(pair_candidates[:10]):  # max 10
                if el.is_displayed():
                    print(f"   [{i}] {el.tag_name}: '{el.text}' | class='{el.get_attribute('class')}' | id='{el.get_attribute('id')}'")
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
        
        # 3. Zeige BUY/SELL Buttons
        print("\n🔍 BUY/SELL BUTTONS:")
        try:
            side_candidates = driver.find_elements(By.XPATH, "//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'buy') or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sell') or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'kauf') or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'verkauf')]")
            for i, el in enumerate(side_candidates[:10]):
                if el.is_displayed():
                    active = "ACTIVE" if any(x in (el.get_attribute('class') or '').lower() for x in ['active', 'selected']) else ""
                    pressed = f" pressed={el.get_attribute('aria-pressed')}" if el.get_attribute('aria-pressed') else ""
                    print(f"   [{i}] {el.tag_name}: '{el.text}' {active}{pressed} | class='{el.get_attribute('class')}' | testid='{el.get_attribute('data-testid')}'")
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
        
        # 4. Zeige Strategie-Auswahl
        print("\n🔍 STRATEGIE-AUSWAHL:")
        try:
            strategy_candidates = driver.find_elements(By.XPATH, "//*[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'limit') or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'market') or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'strateg')]")
            for i, el in enumerate(strategy_candidates[:10]):
                if el.is_displayed():
                    active = "ACTIVE" if any(x in (el.get_attribute('class') or '').lower() for x in ['active', 'selected']) else ""
                    selected = f" selected={el.get_attribute('aria-selected')}" if el.get_attribute('aria-selected') else ""
                    print(f"   [{i}] {el.tag_name}: '{el.text}' {active}{selected} | class='{el.get_attribute('class')}'")
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
        
        # 5. Zeige MAX/Prozent Buttons
        print("\n🔍 MAX/PROZENT BUTTONS:")
        try:
            qty_candidates = driver.find_elements(By.XPATH, "//*[contains(text(),'Max') or contains(text(),'MAX') or contains(text(),'%')]")
            for i, el in enumerate(qty_candidates[:10]):
                if el.is_displayed():
                    clickable = "CLICKABLE" if el.tag_name.lower() in ['button', 'a'] or el.get_attribute('role') in ['button'] else ""
                    print(f"   [{i}] {el.tag_name}: '{el.text}' {clickable} | class='{el.get_attribute('class')}' | role='{el.get_attribute('role')}'")
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
        
        # 6. Zeige BPS Buttons
        print("\n🔍 BPS BUTTONS:")
        try:
            bps_candidates = driver.find_elements(By.XPATH, "//*[contains(text(),'bps') or contains(text(),'BPS')]")
            for i, el in enumerate(bps_candidates[:10]):
                if el.is_displayed():
                    clickable = "CLICKABLE" if el.tag_name.lower() in ['button', 'a'] or el.get_attribute('role') in ['button'] else ""
                    print(f"   [{i}] {el.tag_name}: '{el.text}' {clickable} | class='{el.get_attribute('class')}'")
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
        
        # 7. Zeige Input-Felder
        print("\n🔍 INPUT-FELDER:")
        try:
            input_candidates = driver.find_elements(By.XPATH, "//input | //*[@contenteditable='true'] | //*[@role='spinbutton']")
            for i, el in enumerate(input_candidates[:10]):
                if el.is_displayed():
                    value = el.get_attribute('value') or el.text or ""
                    placeholder = el.get_attribute('placeholder') or ""
                    print(f"   [{i}] {el.tag_name}: value='{value}' placeholder='{placeholder}' | class='{el.get_attribute('class')}' | name='{el.get_attribute('name')}'")
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
        
        # 8. Zeige alle EUR Elemente (für Quote-Switching)
        print("\n🔍 EUR QUOTE ELEMENTE:")
        try:
            eur_candidates = driver.find_elements(By.XPATH, "//*[normalize-space()='EUR']")
            for i, el in enumerate(eur_candidates[:5]):
                if el.is_displayed():
                    clickable = "CLICKABLE" if el.tag_name.lower() in ['button', 'a'] or el.get_attribute('role') in ['button'] or 'onclick' in (el.get_attribute('onclick') or '') else ""
                    print(f"   [{i}] {el.tag_name}: '{el.text}' {clickable} | class='{el.get_attribute('class')}' | role='{el.get_attribute('role')}'")
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
        
        print("\n✅ UI-Analyse abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Verbindung fehlgeschlagen: {e}")
        print("💡 Stelle sicher dass Chrome mit --remote-debugging-port=9222 läuft")

if __name__ == "__main__":
    get_ui_structure()
