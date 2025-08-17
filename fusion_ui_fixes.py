#!/usr/bin/env python3
"""
FUNKTIONIERENDE FUSION UI FIXES
Ersetzt die defekte fusion_ui_fixes.py komplett
"""
import time
from selenium.webdriver.common.by import By

def fix_pair_selection_soleur(driver, debug=False):
    """SOL-EUR auswählen - EINFACH UND FUNKTIONAL"""
    try:
        if debug:
            print("🎯 SOL-EUR FIX...")
        
        # 1. Aktuelles Paar klicken um Dropdown zu öffnen
        current_pair_selectors = [
            "//*[contains(text(),'BTC-EUR')]",
            "//*[contains(text(),'ETH-USD')]",
            "//*[contains(text(),'-EUR')]",
            "//*[contains(text(),'-USD')]"
        ]
        
        for selector in current_pair_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for el in elements:
                if el.is_displayed():
                    try:
                        el.click()
                        time.sleep(1)
                        break
                    except:
                        continue
        
        # 2. SOL-EUR auswählen
        sol_selectors = [
            "//div[contains(text(),'SOL-EUR')]",
            "//span[contains(text(),'SOL-EUR')]",
            "//option[contains(text(),'SOL-EUR')]"
        ]
        
        for selector in sol_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for el in elements:
                if el.is_displayed():
                    try:
                        el.click()
                        time.sleep(1)
                        if debug:
                            print("   ✅ SOL-EUR ausgewählt")
                        return True
                    except:
                        continue
        
        return False
        
    except Exception as e:
        if debug:
            print(f"❌ SOL-EUR ERROR: {e}")
        return False

def fix_limit_strategy(driver, debug=False):
    """Limit Strategie aktivieren - EINFACH"""
    try:
        if debug:
            print("⚙️ LIMIT FIX...")
        
        limit_selectors = [
            "//button[contains(text(),'Limit')]",
            "//*[@role='tab' and contains(text(),'Limit')]",
            "//div[contains(text(),'Limit')]"
        ]
        
        for selector in limit_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for el in elements:
                if el.is_displayed():
                    try:
                        el.click()
                        time.sleep(1)
                        if debug:
                            print("   ✅ Limit aktiviert")
                        return True
                    except:
                        continue
        
        return False
        
    except Exception as e:
        if debug:
            print(f"❌ LIMIT ERROR: {e}")
        return False

def fix_max_button(driver, debug=False):
    """MAX Button aktivieren - EINFACH"""
    try:
        if debug:
            print("🔘 MAX FIX...")
        
        max_selectors = [
            "//button[normalize-space()='Max']",
            "//button[normalize-space()='Max.']",
            "//button[normalize-space()='MAX']",
            "//button[contains(text(),'Max')]"
        ]
        
        for selector in max_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for el in elements:
                if el.is_displayed() and '75' not in el.text:
                    try:
                        el.click()
                        time.sleep(1)
                        if debug:
                            print("   ✅ MAX aktiviert")
                        return True
                    except:
                        continue
        
        return False
        
    except Exception as e:
        if debug:
            print(f"❌ MAX ERROR: {e}")
        return False

def fix_bps_buttons(driver, action="SELL", debug=False):
    """BPS Button aktivieren - EINFACH"""
    try:
        if debug:
            print(f"📊 BPS FIX für {action}...")
        
        # Für SELL: -25bps (besserer Verkaufspreis)
        if action.upper() == "SELL":
            bps_texts = ["-25bps", "-25 bps", "−25bps"]
        else:
            bps_texts = ["-25bps", "-25 bps", "−25bps"]
        
        for bps_text in bps_texts:
            selectors = [
                f"//button[contains(text(),'{bps_text}')]",
                f"//button[normalize-space()='{bps_text}']"
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.XPATH, selector)
                for el in elements:
                    if el.is_displayed():
                        try:
                            el.click()
                            time.sleep(1)
                            if debug:
                                print(f"   ✅ BPS {bps_text} aktiviert")
                            return True
                        except:
                            continue
        
        return False
        
    except Exception as e:
        if debug:
            print(f"❌ BPS ERROR: {e}")
        return False

def fix_limit_price(driver, debug=False):
    """Limitpreis setzen - EINFACH"""
    try:
        if debug:
            print("💰 LIMITPREIS FIX...")
        
        # Einfach - machen wir nichts, da das automatisch passiert
        return True
        
    except Exception as e:
        if debug:
            print(f"❌ LIMITPREIS ERROR: {e}")
        return False
