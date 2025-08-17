#!/usr/bin/env python3
"""
EMERGENCY FIX für alle 3 Probleme:
1. SOL-EUR nicht umgeschaltet
2. MAX nicht gewählt  
3. BPS nicht gewählt

Diese Datei ersetzt fusion_ui_fixes.py komplett
"""
import time
from selenium.webdriver.common.by import By

def fix_pair_selection_soleur(driver, debug=False):
    """AGGRESSIVE SOL-EUR Auswahl"""
    try:
        if debug:
            print("🎯 EMERGENCY SOL-EUR FIX...")
        
        # 1. Finde aktuelles Paar (ETH-USD etc.)
        current_selectors = [
            "//*[contains(text(),'ETH-USD')]",
            "//*[contains(text(),'BTC-EUR')]", 
            "//*[contains(text(),'-USD')]",
            "//*[contains(text(),'-EUR')]"
        ]
        
        clicked = False
        for selector in current_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for el in elements:
                if el.is_displayed():
                    try:
                        if debug:
                            print(f"   Klicke aktuelles Paar: {el.text}")
                        el.click()
                        time.sleep(1)
                        clicked = True
                        break
                    except:
                        continue
            if clicked:
                break
        
        # 2. Suche SOL-EUR in Dropdown/Liste
        time.sleep(1)
        sol_selectors = [
            "//div[contains(text(),'SOL-EUR')]",
            "//span[contains(text(),'SOL-EUR')]",
            "//option[contains(text(),'SOL-EUR')]",
            "//*[@role='option' and contains(text(),'SOL-EUR')]",
            "//*[contains(text(),'SOL') and contains(text(),'EUR')]"
        ]
        
        for selector in sol_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for el in elements:
                if el.is_displayed():
                    try:
                        if debug:
                            print(f"   ✅ SOL-EUR gefunden, klicke...")
                        el.click()
                        time.sleep(1)
                        return True
                    except:
                        continue
        
        # 3. JS Fallback
        js_result = driver.execute_script("""
            const elements = [...document.querySelectorAll('*')];
            const solOption = elements.find(el => 
                el.offsetParent && 
                (el.innerText||'').includes('SOL-EUR')
            );
            if(solOption){
                solOption.click();
                return true;
            }
            return false;
        """)
        
        if js_result and debug:
            print("   ✅ SOL-EUR via JS aktiviert")
        
        return js_result
        
    except Exception as e:
        if debug:
            print(f"❌ SOL-EUR ERROR: {e}")
        return False

def fix_limit_strategy(driver, debug=False):
    """AGGRESSIVE Limit Strategie Aktivierung"""
    try:
        if debug:
            print("⚙️ EMERGENCY LIMIT FIX...")
        
        # 1. Suche Limit Button/Tab
        limit_selectors = [
            "//button[normalize-space()='Limit']",
            "//*[@role='tab' and contains(text(),'Limit')]",
            "//div[contains(text(),'Limit') and contains(@class,'tab')]",
            "//option[contains(text(),'Limit')]"
        ]
        
        for selector in limit_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for el in elements:
                if el.is_displayed() and not el.get_attribute('disabled'):
                    try:
                        if debug:
                            print(f"   Limit gefunden: {el.text}")
                        el.click()
                        time.sleep(1)
                        
                        # Prüfe ob Limitpreis-Feld erscheint
                        limit_fields = driver.find_elements(By.XPATH, "//input[contains(@placeholder,'Limitpreis') or contains(@placeholder,'Limit')]")
                        if any(f.is_displayed() for f in limit_fields):
                            if debug:
                                print("   ✅ Limit aktiviert - Limitpreis-Feld sichtbar")
                            return True
                    except:
                        continue
        
        # 2. JS Fallback
        js_result = driver.execute_script("""
            const buttons = [...document.querySelectorAll('button, [role="button"], [role="tab"]')];
            const limitBtn = buttons.find(b => 
                b.offsetParent && 
                (b.innerText||'').trim().toLowerCase() === 'limit' &&
                !b.disabled
            );
            if(limitBtn){
                limitBtn.click();
                return true;
            }
            return false;
        """)
        
        if js_result:
            time.sleep(1)
            if debug:
                print("   ✅ Limit via JS aktiviert")
        
        return js_result
        
    except Exception as e:
        if debug:
            print(f"❌ LIMIT ERROR: {e}")
        return False

def fix_max_button(driver, debug=False):
    """AGGRESSIVE MAX Button Aktivierung"""
    try:
        if debug:
            print("🔘 EMERGENCY MAX FIX...")
        
        # 1. Alle Buttons scannen
        if debug:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            visible = [b for b in all_buttons if b.is_displayed() and b.text.strip()]
            print(f"   Sichtbare Buttons: {len(visible)}")
            for i, btn in enumerate(visible[:10]):
                print(f"   {i+1}. '{btn.text}'")
        
        # 2. MAX suchen - mehrere Varianten
        max_patterns = ["Max", "Max.", "MAX", "100%", "Alles"]
        
        for pattern in max_patterns:
            selectors = [
                f"//button[normalize-space()='{pattern}']",
                f"//button[contains(text(),'{pattern}')]",
                f"//*[@role='button' and contains(text(),'{pattern}')]"
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.XPATH, selector)
                for el in elements:
                    if el.is_displayed() and not el.get_attribute('disabled'):
                        text = el.text.strip()
                        # Vermeide 75% Buttons
                        if '75' in text:
                            continue
                        try:
                            if debug:
                                print(f"   MAX Versuch: '{text}'")
                            
                            driver.execute_script("arguments[0].click();", el)
                            time.sleep(1.5)
                            
                            # Prüfe ob Anzahl-Feld gefüllt
                            qty_field = driver.find_element(By.XPATH, "//input[contains(@placeholder,'Anzahl') or contains(@placeholder,'Menge')]")
                            if qty_field.is_displayed():
                                value = qty_field.get_attribute('value') or ''
                                if value and value != '0':
                                    if debug:
                                        print(f"   ✅ MAX erfolgreich: {value}")
                                    return True
                            
                        except:
                            continue
        
        # 3. JS Fallback
        js_result = driver.execute_script("""
            const buttons = [...document.querySelectorAll('button')];
            const maxBtn = buttons.find(b => 
                b.offsetParent &&
                (b.innerText||'').toLowerCase().includes('max') &&
                !(b.innerText||'').includes('75') &&
                !b.disabled
            );
            if(maxBtn){
                maxBtn.click();
                return true;
            }
            return false;
        """)
        
        if js_result:
            time.sleep(1)
            if debug:
                print("   ✅ MAX via JS aktiviert")
        
        return js_result
        
    except Exception as e:
        if debug:
            print(f"❌ MAX ERROR: {e}")
        return False

def fix_bps_buttons(driver, action="BUY", debug=False):
    """AGGRESSIVE BPS Button Aktivierung"""
    try:
        if debug:
            print(f"📊 EMERGENCY BPS FIX für {action}...")
        
        # BPS Richtung bestimmen
        if action.upper() == "SELL":
            # SELL: -25bps für besseren Preis
            target_bps = ["-25bps", "-25 bps", "−25bps", "-25"]
            sign = "-"
        else:
            # BUY: -25bps für besseren Preis  
            target_bps = ["-25bps", "-25 bps", "−25bps", "-25"]
            sign = "-"
        
        # 1. Suche exakte BPS Buttons
        for bps_text in target_bps:
            selectors = [
                f"//button[normalize-space()='{bps_text}']",
                f"//button[contains(text(),'{bps_text}')]",
                f"//*[@role='button' and contains(text(),'{bps_text}')]"
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.XPATH, selector)
                for el in elements:
                    if el.is_displayed() and not el.get_attribute('disabled'):
                        try:
                            if debug:
                                print(f"   BPS Versuch: '{el.text}'")
                            el.click()
                            time.sleep(1)
                            if debug:
                                print(f"   ✅ BPS geklickt: {el.text}")
                            return True
                        except:
                            continue
        
        # 2. JS Fallback für BPS
        js_result = driver.execute_script(f"""
            const buttons = [...document.querySelectorAll('button')];
            const bpsBtn = buttons.find(b => 
                b.offsetParent &&
                (b.innerText||'').includes('{sign}25') &&
                (b.innerText||'').includes('bps') &&
                !b.disabled
            );
            if(bpsBtn){{
                bpsBtn.click();
                return true;
            }}
            return false;
        """)
        
        if js_result:
            if debug:
                print(f"   ✅ BPS via JS aktiviert")
        
        return js_result
        
    except Exception as e:
        if debug:
            print(f"❌ BPS ERROR: {e}")
        return False

def emergency_complete_fix(driver, action="SELL", debug=False):
    """Führt alle Fixes in korrekter Reihenfolge aus"""
    try:
        if debug:
            print("🚨 EMERGENCY COMPLETE FIX - ALLE PROBLEME BEHEBEN")
        
        success_count = 0
        
        # 1. SOL-EUR auswählen
        if fix_pair_selection_soleur(driver, debug):
            success_count += 1
            if debug:
                print("✅ 1/4 SOL-EUR erfolgreich")
        
        time.sleep(1)
        
        # 2. Limit Strategie aktivieren
        if fix_limit_strategy(driver, debug):
            success_count += 1
            if debug:
                print("✅ 2/4 Limit erfolgreich")
        
        time.sleep(1)
        
        # 3. MAX Button aktivieren
        if fix_max_button(driver, debug):
            success_count += 1
            if debug:
                print("✅ 3/4 MAX erfolgreich")
        
        time.sleep(1)
        
        # 4. BPS Button aktivieren
        if fix_bps_buttons(driver, action, debug):
            success_count += 1
            if debug:
                print("✅ 4/4 BPS erfolgreich")
        
        if debug:
            print(f"🎯 EMERGENCY FIX: {success_count}/4 erfolgreich")
        
        return success_count >= 3  # Mindestens 3 von 4 müssen funktionieren
        
    except Exception as e:
        if debug:
            print(f"❌ EMERGENCY FIX ERROR: {e}")
        return False
