#!/usr/bin/env python3
"""
EMERGENCY FIX für alle 3 Probleme:
1. SOL-EUR nicht umgeschaltet
2. MAX nicht gewählt  
3. BPS nicht gewählt

Diese Datei ersetzt fusion_ui_fixes.py komplett
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time

def fix_pair_selection_target(driver, pair_text, strategy="Limit", debug=False, timeout=12):
    """Switch the right-panel pair to pair_text. Verify using the right combobox input value first to avoid false positives.
    Note: This helper only switches the pair; it does NOT change the order type.
    """
    wait = WebDriverWait(driver, timeout)
    dash = (pair_text or '').strip().upper()
    slash = dash.replace('-', '/')

    # 1️⃣ Prefer verifying the right-side combobox input value
    input_el = _find_right_symbol_input(driver, debug=debug)
    if input_el is not None and _verify_pair_input(input_el, dash, slash, debug=debug):
        if debug:
            print(f"   🔍 {dash} ist bereits aktiv (Combobox).")
        return True

    # 2️⃣ Use combobox-first selection: type and pick pair for this specific input
    if input_el is not None:
        ok = _open_and_type_pair(driver, input_el, dash, slash, debug=debug)
        if ok:
            # verify via input value first; fall back to header check
            if _verify_pair_input(input_el, dash, slash, debug=debug) or _verify_pair_header(driver, dash, slash, debug=debug):
                if debug:
                    print(f"   ✅ Pair {dash} gewählt (Combobox).")
                return True

    # 3️⃣ Legacy fallback: open header selector, search, and click entry
    header_xpath = (
        f"//div[contains(@class,'gWWQO') and normalize-space()='{dash}']"
        f"|//*[normalize-space()='{dash}' or normalize-space()='{slash}']"
    )
    try:
        selector_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//div[contains(@class,'gWWQO') and normalize-space()!='']/ancestor::button[1]"
        )))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", selector_btn)
        selector_btn.click()
    except TimeoutException:
        if debug:
            print("   ❌ Markt-Selector nicht gefunden.")
        return False

    try:
        search_input = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "input[data-testid='symbol-selector-input']"
        )))
        search_input.clear()
        search_input.send_keys(dash)
    except TimeoutException:
        if debug:
            print("   ❌ Suchfeld nicht gefunden.")
        return False

    entry_xpath = (
        f"//*[@role='option' and (normalize-space()='{dash}' or normalize-space()='{slash}')]"
        f"|//*[self::li or self::div or self::span][normalize-space()='{dash}' or normalize-space()='{slash}']"
    )
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            entry = wait.until(EC.element_to_be_clickable((By.XPATH, entry_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", entry)
            entry.click()
            break
        except StaleElementReferenceException:
            if debug:
                print("   🔄 Pair-Eintrag stale, retry …")
            time.sleep(0.2)
        except TimeoutException:
            if debug:
                print(f"   ❌ Kein klickbarer Eintrag {dash}")
            return False

    try:
        # Verify via input first if available, else header
        if (input_el and _verify_pair_input(input_el, dash, slash, debug=debug)) or _verify_pair_header(driver, dash, slash, debug=debug):
            if debug:
                print(f"   ✅ Pair {dash} gewählt.")
        else:
            if debug:
                print(f"   ❌ Header/Input aktualisiert sich nicht auf {dash}.")
            return False
    except TimeoutException:
        if debug:
            print(f"   ❌ Header aktualisiert sich nicht auf {dash}.")
        return False

    return True

def _set_market_type(driver, wait, debug):
    """Hilfsfunktion für Ordertyp-Umschaltung auf Market/Market+ (robust, de/en)."""
    xp_market = (
        "//*[self::button or @role='tab' or contains(@class,'tab')]"
        "[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'MARKET+')"
        " or normalize-space(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))='MARKET'"
        " or contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'MARKET')"
        " or contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'MARKT+')"
        " or normalize-space(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'))='MARKT'"
        " or contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'MARKT')]"
    )
    try:
        try:
            market_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp_market)))
        except TimeoutException:
            market_btn = wait.until(EC.presence_of_element_located((By.XPATH, xp_market)))
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", market_btn)
        except Exception:
            pass
        try:
            if market_btn.is_enabled():
                market_btn.click()
            else:
                raise Exception('Market button not enabled')
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", market_btn)
            except Exception:
                pass
        # Optional bestätigen that it's active/selected
        try:
            wait.until(lambda d: "active" in (market_btn.get_attribute("class") or '') or
                                  "selected" in (market_btn.get_attribute("class") or ''))
        except Exception:
            pass
        if debug:
            print("   ✅ Ordertyp auf Market gesetzt.")
    except TimeoutException:
        if debug:
            print("   ❌ Market-Button nicht klickbar.")

def _visible_els(driver, xp: str):
    try:
        els = driver.find_elements(By.XPATH, xp)
    except Exception:
        return []
    out = []
    for el in els:
        try:
            if el and el.is_displayed():
                out.append(el)
        except Exception:
            continue
    return out

def _find_right_symbol_input(driver, debug=False):
    # Prefer the right-most visible symbol selector input
    xp = "//input[@data-testid='symbol-selector-input' and @role='combobox']"
    cands = _visible_els(driver, xp)
    if not cands:
        # try without role attr
        cands = _visible_els(driver, "//input[@data-testid='symbol-selector-input']")
    if not cands:
        return None
    try:
        # compute right-most by boundingClientRect().x
        rects = driver.execute_script(
            "return arguments[0].map(el=>{const r=el.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};});",
            cands,
        )
    except Exception:
        rects = None
    best = None
    best_x = -1
    for idx, el in enumerate(cands):
        x = 0
        try:
            if rects and idx < len(rects):
                x = float(rects[idx].get('x', 0))
            else:
                x = driver.execute_script("const r=arguments[0].getBoundingClientRect(); return r.x;", el) or 0
        except Exception:
            x = 0
        if x > best_x:
            best_x = x
            best = el
    if debug:
        try:
            driver.execute_script("arguments[0].style.outline='2px solid #00bcd4'", best)
        except Exception:
            pass
    return best

def _open_and_type_pair(driver, input_el, pair_dash: str, pair_slash: str, debug=False) -> bool:
    from selenium.webdriver.common.keys import Keys
    try:
        input_el.click()
    except Exception:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", input_el)
            input_el.click()
        except Exception:
            return False
    # clear with Ctrl+A, Delete
    try:
        input_el.send_keys(Keys.CONTROL, 'a')
        input_el.send_keys(Keys.DELETE)
    except Exception:
        pass
    # type dash variant first
    try:
        input_el.send_keys(pair_dash)
    except Exception:
        return False
    # small open hint
    try:
        input_el.send_keys(Keys.ARROW_DOWN)
    except Exception:
        pass
    # pick from dropdown – scope to this input's menu via aria-controls when available
    menu_id = None
    try:
        menu_id = (input_el.get_attribute('aria-controls') or '').strip()
    except Exception:
        menu_id = None
    if menu_id:
        options_xp = (
            f"//*[@id='{menu_id}']//*[self::li or @role='option']"
            + f"[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{pair_dash.upper()}') or contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{pair_slash.upper()}')]"
        )
    else:
        options_xp = (
            "//ul[contains(@id,'downshift') and contains(@id,'menu')]//*[self::li or @role='option']"
            + f"[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{pair_dash.upper()}') or contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '{pair_slash.upper()}')]"
        )
    try:
        opts = _visible_els(driver, options_xp)
        if opts:
            opts[0].click()
            return True
    except Exception:
        pass
    # fallback: press ENTER to accept first suggestion
    try:
        input_el.send_keys(Keys.ENTER)
    except Exception:
        pass
    # verification will confirm success
    return True

def _verify_pair_input(input_el, dash: str, slash: str, debug=False) -> bool:
    try:
        val = (input_el.get_attribute('value') or '').strip().upper()
        if debug:
            print(f"   🔎 Input-Verify: value='{val}' vs '{dash}'/'{slash}'")
        if not val:
            return False
        return val == dash or val == slash or dash in val or slash in val
    except Exception:
        return False

def _verify_pair_header(driver, dash: str, slash: str, debug=False) -> bool:
    """Check visible headers/buttons for the currently selected pair label."""
    try:
        # common header/button areas
        header_xp = [
            "//header//*[self::button or @role='button' or contains(@class,'pair') or contains(@class,'asset') or contains(@class,'ticker') or contains(@class,'header')]",
            "//*[@data-testid and (contains(@data-testid,'pair') or contains(@data-testid,'asset') or contains(@data-testid,'ticker'))]",
            "//button[contains(.,'/') or contains(.,'-')]",
        ]
        txts = []
        for xp in header_xp:
            try:
                for el in driver.find_elements(By.XPATH, xp):
                    try:
                        if not el.is_displayed():
                            continue
                        t = (el.text or '').strip().upper()
                        if t:
                            txts.append(t)
                    except Exception:
                        continue
            except Exception:
                continue
        found = any((dash == t) or (slash == t) or (dash in t) or (slash in t) for t in txts)
        if debug:
            print(f"   🔍 Header-Check: found={found} candidates={txts[:4]}")
        if found:
            return True
        # Fallback: scan visible DOM for the pair label in generic containers (handles Box/Flex wrappers)
        try:
            js = """
            const dash = arguments[0].toUpperCase();
            const slash = arguments[1].toUpperCase();
            const els = [...document.querySelectorAll('*')];
            for (const el of els) {
              if (!el || !el.offsetParent) continue;
              const txt = (el.innerText||'').trim().toUpperCase();
              if (!txt) continue;
              // Consider top-level token before newline as main label
              const top = txt.split('\n')[0];
              if (top === dash || top === slash || top.includes(dash) || top.includes(slash)) {
                return true;
              }
            }
            return false;
            """
            dom_found = driver.execute_script(js, dash, slash)
            if debug:
                print(f"   🔍 DOM Fallback-Check: {dom_found}")
            return bool(dom_found)
        except Exception:
            return False
    except Exception:
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
            # SELL: +25bps für besseren Preis (über Markt)
            target_bps = ["+25bps", "+25 bps", "+25"]
            sign = "+"
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
        js_result = driver.execute_script(
            """
            const sign = arguments[0] || '';
            const buttons = [...document.querySelectorAll('button')];
            const bpsBtn = buttons.find(b => 
                b.offsetParent &&
                (b.innerText||'').includes(sign + '25') &&
                (b.innerText||'').toLowerCase().includes('bps') &&
                !b.disabled
            );
            if (bpsBtn) { bpsBtn.click(); return true; }
            return false;
            """,
            sign,
        )

        if js_result:
            if debug:
                print(f"   ✅ BPS via JS aktiviert")

        return js_result
        
    except Exception as e:
        if debug:
            print(f"❌ BPS ERROR: {e}")
        return False

def emergency_complete_fix(driver, action="SELL", target_pair=None, debug=False):
    """Führt alle Fixes in korrekter Reihenfolge aus"""
    try:
        if debug:
            print("🚨 EMERGENCY COMPLETE FIX - ALLE PROBLEME BEHEBEN")
        
        success_count = 0
        
        # 1. Ziel-Paar auswählen (falls angegeben)
        if target_pair and fix_pair_selection_target(driver, target_pair, debug):
            success_count += 1
            if debug:
                print("✅ 1/4 Pair-Select erfolgreich")
        
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
