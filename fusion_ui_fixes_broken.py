#!/usr/bin/env python3
"""
GEZIELTE FIXES für die 3 Hauptprobleme:
1. SOL-EUR auswählen (nicht ETH-USD)
2. Strategie "Limit" aktivieren 
3. Echten MAX Button klicken (nicht 75%)
4. +25bps anwenden
"""
import time
from selenium.webdriver.common.by import By

def fix_pair_selection_soleur(driver, debug=False):
    """Forciert SOL-EUR Auswahl mit aggressiverer Suche"""
    try:
        if debug:
            print("🔧 AGGRESSIVE SOL-EUR SUCHE...")
        
        # 1. Erweiterte Suche nach aktuellem Paar-Display (ETH-USD oder anderes)
        current_pair_selectors = [
            "//*[contains(text(),'ETH-USD')]",
            "//*[contains(text(),'BTC-EUR')]", 
            "//*[contains(text(),'SOL-EUR')]",
            "//div[contains(@class,'trading-pair')]",
            "//div[contains(@class,'asset-selector')]",
            "//button[contains(@class,'pair')]",
            "//*[@data-testid*='pair']",
            "//*[@role='button' and contains(text(),'-')]"  # Alle Pairs haben "-"
        ]
        
        # 2. Finde und klicke Paar-Trigger
        clicked_trigger = False
        for selector in current_pair_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for el in elements:
                    if el.is_displayed() and el.text.strip():
                        try:
                            if debug:
                                print(f"   Teste Trigger: '{el.text}' | Tag: {el.tag_name}")
                            el.click()
                            clicked_trigger = True
                            time.sleep(0.8)  # Längere Pause für Dropdown
                            break
                        except Exception as e:
                            if debug:
                                print(f"   Trigger-Klick fehlgeschlagen: {e}")
                            continue
                if clicked_trigger:
                    break
            except Exception:
                continue
        
        # 3. Suche nach SOL in der geöffneten Liste
        time.sleep(0.3)
        sol_options = [
            "//li[contains(.,'SOL-EUR')]",
            "//option[contains(.,'SOL-EUR')]", 
            "//*[normalize-space()='SOL-EUR']",
            "//tr[contains(.,'SOL') and contains(.,'EUR')]",
            "//*[contains(.,'SOL')]/ancestor::*[contains(.,'EUR')]",
        ]
        
        for sol_xpath in sol_options:
            try:
                elements = driver.find_elements(By.XPATH, sol_xpath)
                for el in elements:
                    if el.is_displayed():
                        try:
                            el.click()
                            if debug:
                                print(f"   ✅ SOL-EUR gewählt: {el.tag_name}")
                            time.sleep(0.3)
                            return True
                        except Exception:
                            continue
            except Exception:
                continue
        
        # 4. JS Fallback für SOL-EUR
        try:
            js_result = driver.execute_script("""
                const nodes = [...document.querySelectorAll('*')];
                const target = nodes.find(n => 
                    n.offsetParent && 
                    (n.innerText||'').includes('SOL-EUR') &&
                    (n.tagName==='LI' || n.tagName==='BUTTON' || n.getAttribute('role')==='option')
                );
                if(target){ target.click(); return true; }
                return false;
            """)
            if js_result and debug:
                print("   ✅ SOL-EUR via JS gewählt")
            return js_result
        except Exception:
            return False
            
    except Exception as e:
        if debug:
            print(f"   ❌ Paar-Auswahl Fehler: {e}")
        return False

def fix_limit_strategy(driver, debug=False):
    """Forciert Limit-Strategie Aktivierung - KORREKTE SEQUENZ"""
    try:
        if debug:
            print("🔧 FORCE LIMIT STRATEGY...")
        
        # SCHRITT 1: ERST Strategie-Dropdown öffnen - KRITISCH!
        if debug:
            print("   🔍 Schritt 1: Öffne Strategie-Dropdown")
            
        dropdown_opened = False
        strategy_triggers = [
            "//div[contains(text(), 'Strategie auswählen')]",
            "//button[contains(text(), 'Strategie auswählen')]", 
            "//*[contains(text(), 'Strategie auswählen')]",
            "//*[contains(@placeholder, 'Strategie')]",
            "//select[contains(@class, 'strategy')]",
            "//*[contains(@class, 'strategy-select')]",
            "//*[contains(@class, 'dropdown')]//button"
        ]
        
        for dropdown_sel in strategy_triggers:
            if dropdown_opened:
                break
            try:
                elements = driver.find_elements(By.XPATH, dropdown_sel)
                for dropdown in elements:
                    if dropdown.is_displayed() and dropdown.is_enabled():
                        text = (dropdown.text or '').strip()
                        if 'Strategie auswählen' in text:
                            if debug:
                                print(f"   🎯 Dropdown-Trigger gefunden: {dropdown.tag_name}")
                            driver.execute_script("arguments[0].click();", dropdown)
                            time.sleep(1.5)  # WICHTIG: Warten bis Dropdown geöffnet ist
                            dropdown_opened = True
                            if debug:
                                print(f"   ✅ Dropdown geöffnet, warte auf Optionen...")
                            break
            except Exception:
                continue
        
        if not dropdown_opened:
            if debug:
                print("   ❌ Konnte Dropdown nicht öffnen")
            return False
        
        # SCHRITT 2: JETZT Limit-Option suchen (Dropdown ist offen)
        if debug:
            print("   🔍 Schritt 2: Suche Limit-Option im geöffneten Dropdown")
            
        # Zusätzliche Wartezeit für Dropdown-Rendering
        time.sleep(0.5)
        
        limit_selectors = [
            "//button[normalize-space()='Limit']",
            "//li[normalize-space()='Limit']",
            "//div[normalize-space()='Limit']", 
            "//option[normalize-space()='Limit']",
            "//span[normalize-space()='Limit']",
            "//*[@role='option' and normalize-space()='Limit']",
            "//*[@role='menuitem' and normalize-space()='Limit']",
            "//select/option[contains(.,'Limit')]",
            # Auch weniger strenge Suche
            "//*[contains(text(),'Limit') and not(contains(text(),'preis'))]"
        ]
        
        for strategy_xpath in limit_selectors:
            try:
                elements = driver.find_elements(By.XPATH, strategy_xpath)
                for el in elements:
                    if el.is_displayed() and el.is_enabled():
                        text_content = (el.text or el.get_attribute('textContent') or '').strip()
                        if text_content.lower() == 'limit':
                            if debug:
                                print(f"   🎯 Limit-Option gefunden: {el.tag_name} - Text: '{text_content}'")
                            
                            try:
                                if el.tag_name == 'OPTION':
                                    # Select Option
                                    from selenium.webdriver.support.ui import Select
                                    select_el = el.find_element(By.XPATH, "./..")
                                    select = Select(select_el)
                                    select.select_by_visible_text(el.text)
                                else:
                                    driver.execute_script("arguments[0].click();", el)
                                
                                time.sleep(1)  # Wartezeit für Strategie-Aktivierung
                                
                                # SCHRITT 3: Verifiziere Erfolg
                                page_text = driver.find_element(By.TAG_NAME, 'body').text
                                if 'Strategie auswählen' not in page_text:
                                    if debug:
                                        print(f"   ✅ Limit Strategie erfolgreich aktiviert!")
                                    
                                    # SCHRITT 4: Jetzt sollte Limitpreis-Feld erscheinen
                                    time.sleep(0.5)  # Kurz warten bis UI updated
                                    if 'Limitpreis' in driver.find_element(By.TAG_NAME, 'body').text:
                                        if debug:
                                            print(f"   ✅ Limitpreis-Feld ist jetzt sichtbar!")
                                    else:
                                        if debug:
                                            print(f"   ⚠️ Limitpreis-Feld noch nicht sichtbar")
                                    
                                    return True
                                else:
                                    if debug:
                                        print(f"   ⚠️ Limit geklickt aber 'Strategie auswählen' noch sichtbar")
                                        
                            except Exception as e:
                                if debug:
                                    print(f"   ⚠️ Limit-Click Fehler: {e}")
                                continue
            except Exception:
                continue
        
        # 2. JS Fallback für Limit
        try:
            js_result = driver.execute_script("""
                // Erst schauen ob Limit bereits aktiv
                const activeLimit = [...document.querySelectorAll('*')].find(n =>
                    n.offsetParent && 
                    (n.innerText||'').trim().toLowerCase() === 'limit' &&
                    (n.classList.contains('active') || n.getAttribute('aria-selected')==='true')
                );
                if(activeLimit) return true;
                
                // Sonst Limit Button suchen und klicken
                const limitBtn = [...document.querySelectorAll('button, [role="button"], [role="tab"]')].find(n =>
                    n.offsetParent && 
                    (n.innerText||'').trim().toLowerCase() === 'limit' &&
                    !n.disabled
                );
                if(limitBtn){ limitBtn.click(); return true; }
                
                // Dropdown/Select handling
                const selects = [...document.querySelectorAll('select')];
                for(const sel of selects){
                    const limitOpt = [...sel.options].find(opt => 
                        (opt.text||'').toLowerCase().includes('limit')
                    );
                    if(limitOpt){
                        limitOpt.selected = true;
                        sel.dispatchEvent(new Event('change'));
                        return true;
                    }
                }
                
                return false;
            """)
            if js_result and debug:
                print("   ✅ Limit Strategie via JS aktiviert")
            return js_result
        except Exception:
            return False
            
    except Exception as e:
        if debug:
            print(f"   ❌ Limit-Strategie Fehler: {e}")
        return False

def fix_limit_price(driver, target_price, debug=False):
    """Setzt den Limitpreis automatisch (nach Limit-Strategie Aktivierung)"""
    try:
        if debug:
            print(f"🔧 SETZE LIMITPREIS: {target_price}")
        
        # Suche Limitpreis-Feld
        limitpreis_selectors = [
            "//input[contains(@placeholder, 'Limitpreis')]",
            "//input[contains(@placeholder, 'Limit-Preis')]", 
            "//input[contains(@placeholder, 'Preis')]",
            "//input[contains(@name, 'price')]",
            "//input[contains(@id, 'price')]",
            "//input[contains(@id, 'limit')]",
            "//*[@role='spinbutton' and contains(@placeholder, 'Preis')]",
            "//*[@contenteditable='true' and contains(@placeholder, 'Preis')]"
        ]
        
        for price_sel in limitpreis_selectors:
            try:
                elements = driver.find_elements(By.XPATH, price_sel)
                for field in elements:
                    if field.is_displayed() and field.is_enabled():
                        if debug:
                            print(f"   🎯 Limitpreis-Feld gefunden: {field.tag_name}")
                        
                        # Feld leeren und Preis eingeben
                        field.clear()
                        time.sleep(0.2)
                        field.send_keys(str(target_price))
                        time.sleep(0.2)
                        
                        # Verifiziere Eingabe
                        entered_value = field.get_attribute('value') or ''
                        if str(target_price) in entered_value:
                            if debug:
                                print(f"   ✅ Limitpreis gesetzt: {entered_value}")
                            return True
                        else:
                            if debug:
                                print(f"   ⚠️ Preis-Eingabe nicht korrekt: {entered_value}")
                                
            except Exception as e:
                if debug:
                    print(f"   ⚠️ Preis-Feld Fehler: {e}")
                continue
        
        if debug:
            print("   ❌ Limitpreis-Feld nicht gefunden oder nicht setzbar")
        return False
        
    except Exception as e:
        if debug:
            print(f"   ❌ Limitpreis-Setzen Fehler: {e}")
        return False

def fix_max_button(driver, debug=False):
    """AGGRESSIVE MAX Button Suche und Aktivierung"""
    try:
        if debug:
            print("🔧 AGGRESSIVE MAX SUCHE...")
        
        # 1. Warte und prüfe Bereitschaft der UI
        time.sleep(2)  # Längere Wartezeit
        
        # 2. Erst alle Buttons scannen für Debug
        if debug:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            visible_buttons = [b for b in all_buttons if b.is_displayed() and b.text.strip()]
            print(f"   📊 Alle sichtbaren Buttons: {len(visible_buttons)}")
            for i, btn in enumerate(visible_buttons[:15]):  # Top 15
                text = btn.text.strip()
                classes = btn.get_attribute('class') or ''
                print(f"   {i+1}. '{text}' | Classes: {classes[:50]}")
        
        # 3. SEHR BREITE MAX Button Suche
        max_patterns = [
            "Max", "Max.", "MAX", "max", 
            "Maximum", "MAXIMUM", "100%",
            "Alles", "ALLES", "All"
        ]
        
        found_max = False
        for pattern in max_patterns:
            if found_max:
                break
                
            # Verschiedene Selektor-Ansätze
            selectors = [
                f"//button[normalize-space()='{pattern}']",
                f"//button[contains(text(),'{pattern}')]",
                f"//*[@role='button' and contains(text(),'{pattern}')]",
                f"//*[contains(@class,'button') and contains(text(),'{pattern}')]",
                f"//*[contains(@class,'max') and contains(text(),'{pattern}')]",
                f"//span[contains(text(),'{pattern}')]/parent::button",
                f"//div[contains(text(),'{pattern}') and contains(@class,'button')]"
            ]
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for el in elements:
                        if el.is_displayed() and not el.get_attribute('disabled'):
                            try:
                                text = el.text.strip()
                                classes = el.get_attribute('class') or ''
                                
                                # Vermeide Falsche Buttons (75%, Prozent ohne MAX)
                                if '75' in text or ('process' in classes.lower()):
                                    continue
                                    
                                if debug:
                                    print(f"   🎯 MAX Versuch: '{text}' | Pattern: {pattern}")
                                
                                # Scroll und klick
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                                time.sleep(0.3)
                                
                                # Force click mit JS
                                driver.execute_script("arguments[0].click();", el)
                                time.sleep(1.5)  # Längere Wartezeit
                                
                                found_max = True
                                if debug:
                                    print(f"   ✅ MAX geklickt: '{text}'")
                                break
                                
                            except Exception as e:
                                if debug:
                                    print(f"   ⚠️ MAX-Klick Fehler: {e}")
                                continue
                    if found_max:
                        break
        # 4. Verifiziere Erfolg durch gefülltes Anzahl-Feld
        if found_max:
            time.sleep(1)  # Warte auf Feld-Update
            
            # Prüfe Anzahl-Feld
            qty_selectors = [
                "//input[contains(@placeholder, 'Menge')]",
                "//input[contains(@placeholder, 'Anzahl')]", 
                "//input[contains(@name, 'amount')]",
                "//*[@role='spinbutton']"
            ]
            
            for field_sel in qty_selectors:
                try:
                    field = driver.find_element(By.XPATH, field_sel)
                    if field.is_displayed():
                        value = field.get_attribute('value') or ''
                        if value and value != '0':
                            if debug:
                                print(f"   ✅ MAX erfolgreich - Anzahl gefüllt: {value}")
                            return True
                except Exception:
                    continue
            
            if debug:
                print("   ⚠️ MAX geklickt aber Anzahl-Feld noch leer")
        
        # 5. JS Fallback für MAX
        try:
            if debug:
                print("   🔄 JS Fallback für MAX...")
            js_result = driver.execute_script("""
                const buttons = [...document.querySelectorAll('button, [role="button"]')];
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
                    print("   ✅ JS MAX erfolgreich")
                return True
        except Exception as e:
            if debug:
                print(f"   ⚠️ JS MAX Fehler: {e}")
        
        if debug:
            print("   ❌ MAX Button nicht gefunden oder aktiviert")
        return False
        
    except Exception as e:
        if debug:
            print(f"❌ fix_max_button ERROR: {e}")
        return False
            js_result = driver.execute_script("""
                const maxBtns = [...document.querySelectorAll('button, [role="button"]')].filter(n =>
                    n.offsetParent && 
                    (n.innerText||'').trim().toLowerCase() === 'max' &&
                    !n.disabled &&
                    !n.classList.contains('disabled')
                );
                
                // Bevorzuge Button der NICHT in einer Prozent-Gruppe ist
                const pureMax = maxBtns.find(btn => {
                    const parent = btn.parentElement;
                    const siblingText = (parent ? parent.innerText : '');
                    return !siblingText.includes('%');
                });
                
                const target = pureMax || maxBtns[0];
                if(target){ target.click(); return true; }
                return false;
            """)
            if js_result and debug:
                print("   ✅ MAX Button via JS geklickt")
            return js_result
        except Exception:
            return False
            
    except Exception as e:
        if debug:
            print(f"   ❌ MAX Button Fehler: {e}")
        return False

def fix_bps_plus25(driver, debug=False):
    """Forciert +25bps Button"""
    try:
        if debug:
            print("🔧 FORCE +25BPS...")
        
        # Suche +25bps Button
        bps_selectors = [
            "//button[normalize-space()='+25bps']",
            "//button[contains(.,'25bps') and contains(.,'+')]",
            "//button[contains(.,'25 bps') and contains(.,'+')]",
            "//*[@role='button' and contains(.,'25') and contains(.,'bps') and contains(.,'+')]",
        ]
        
        for bps_xpath in bps_selectors:
            try:
                elements = driver.find_elements(By.XPATH, bps_xpath)
                for el in elements:
                    if el.is_displayed():
                        try:
                            el.click()
                            if debug:
                                print(f"   ✅ +25bps Button geklickt: {el.text}")
                            time.sleep(0.2)
                            return True
                        except Exception:
                            continue
            except Exception:
                continue
        
        # JS Fallback für +25bps
        try:
            js_result = driver.execute_script("""
                const bpsBtns = [...document.querySelectorAll('button, [role="button"]')].filter(n =>
                    n.offsetParent && 
                    (n.innerText||'').includes('25') &&
                    (n.innerText||'').includes('bps') &&
                    (n.innerText||'').includes('+')
                );
                
                if(bpsBtns.length > 0){
                    bpsBtns[0].click();
                    return true;
                }
                return false;
            """)
            if js_result and debug:
                print("   ✅ +25bps Button via JS geklickt")
            return js_result
        except Exception:
            return False
            
    except Exception as e:
        if debug:
            print(f"   ❌ +25bps Fehler: {e}")
        return False

# Diese Funktionen können in fusion_existing_all_trades_auto.py importiert werden
if __name__ == "__main__":
    print("🔧 UI Fix Funktionen geladen")
    print("   - fix_pair_selection_soleur(driver, debug=True)")
    print("   - fix_limit_strategy(driver, debug=True)")
    print("   - fix_max_button(driver, debug=True)")
    print("   - fix_bps_plus25(driver, debug=True)")
