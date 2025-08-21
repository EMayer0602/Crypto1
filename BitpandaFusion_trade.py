# BitpandaFusion_trade.py
# "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfile"
# https://web.bitpanda.com/fusion/trade/BTC-EUR
# http://localhost:9222/json/version
# 
# BitpandaFusion_trade_loop.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json, urllib.request, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from fusion_emergency_fixes import fix_pair_selection_target

# Visible preview banner to show activity in the Fusion UI
def _inject_preview_banner(driver, text: str):
        try:
                js = """
                (function(){
                    let el = document.getElementById('fusion-preview-banner');
                    if(!el){
                        el = document.createElement('div');
                        el.id = 'fusion-preview-banner';
                        el.style.position='fixed';
                        el.style.top='10px';
                        el.style.right='10px';
                        el.style.zIndex='999999';
                        el.style.padding='10px 14px';
                        el.style.border='2px solid #ff9800';
                        el.style.background='rgba(255, 152, 0, 0.15)';
                        el.style.color='#ff9800';
                        el.style.font='600 14px system-ui, sans-serif';
                        document.body.appendChild(el);
                    }
                    el.textContent = arguments[0];
                })();
                """
                driver.execute_script(js, text)
        except Exception:
                pass

# === Hilfsfunktionen ===
def _load_orders(path: str) -> list[dict]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        raw = data.get('orders', [])
        if isinstance(raw, list):
            return list(raw)
        if isinstance(raw, dict):
            # Preserve insertion order of keys (Python 3.7+ maintains order)
            return [raw[k] for k in raw.keys()]
        return []
    except Exception:
        return []

def attach_with_service(use_edge: bool, port: int, debug_addr: str | None = None):
    addr = debug_addr or f"127.0.0.1:{port}"
    if use_edge:
        from selenium.webdriver.edge.options import Options as EdgeOptions
        from selenium.webdriver.edge.service import Service as EdgeService
        opts = EdgeOptions()
        opts.add_experimental_option("debuggerAddress", addr)
        return webdriver.Edge(options=opts)
    else:
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.chrome.service import Service as ChromeService
        opts = ChromeOptions()
        opts.add_experimental_option("debuggerAddress", addr)
        return webdriver.Chrome(options=opts)

def switch_to_tab_with_title(driver, title_contains: str, timeout: int = 5):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        try:
            if title_contains.lower() in driver.title.lower():
                return True
        except Exception:
            pass
    WebDriverWait(driver, timeout).until(lambda d: title_contains.lower() in d.title.lower())
    return True

# === Order‑Handling ===
def trade_order(driver, order, timeout=20):
    wait = WebDriverWait(driver, timeout)
    # Fast, high-frequency wait for micro interactions
    short_wait_sec = float(os.environ.get('FUSION_SHORT_WAIT_SEC', '1.2'))
    poll_sec = float(os.environ.get('FUSION_POLL_SEC', '0.05'))
    wait_short = WebDriverWait(driver, short_wait_sec, poll_frequency=poll_sec)
    tab_click_delay = float(os.environ.get('FUSION_TAB_CLICK_DELAY_SEC', '0.08'))

    # Normalize keys from possible order schema variants
    action   = (order.get("action") or order.get("side") or "").lower()
    strategy = (order.get("strategy") or order.get("type") or "Limit")
    amount   = order.get("amount", order.get("qty", None))
    limit_price = order.get("limit_price", order.get("bps", None))

    # 1) Strategie ermitteln/setzen (neues Dropdown oder Fallback Tabs)
    def _get_strategy_dropdown_wrapper():
        try:
            return driver.find_element(By.CSS_SELECTOR, "[data-testid='strategy-select']")
        except Exception:
            return None

    def _get_current_strategy_label(wrapper_el):
        try:
            # Text im Auswahlfeld (zeigt entweder ausgewählte Strategie oder "Strategie auswählen")
            sel = wrapper_el.find_element(By.CSS_SELECTOR, "[data-testid='base-select-button']")
            txt = (sel.text or "").strip()
            return txt
        except Exception:
            return ""

    def _set_strategy_dropdown(desired: str) -> bool:
        desired = (desired or "").strip().lower()
        wrapper = _get_strategy_dropdown_wrapper()
        if not wrapper:
            return False
        # Map gewünschte Strategie auf mögliche exakte Beschriftungen (de/en)
        label_map = {
            "limit": ["limit"],
            "market": ["markt", "market", "marktpreis"],
            "market+": ["markt", "market", "marktpreis"],
            "stop-limit": ["stop limit", "stop-limit"],
            "stop_limit": ["stop limit", "stop-limit"],
        }
        def _norm(txt: str) -> str:
            return " ".join((txt or "").strip().lower().split())
        labels = [_norm(x) for x in label_map.get(desired, [desired])]
        labels_set = set(labels)

        # Fast path: already selected? (exact match only)
        cur_label = _norm(_get_current_strategy_label(wrapper))
        data_val = _norm(wrapper.get_attribute('data-value') or '')
        if cur_label in labels_set and cur_label and "auswählen" not in cur_label:
            print(f"[strategy] Already set: '{cur_label}'")
            return True
        if data_val and data_val in labels_set:
            print(f"[strategy] Already set (data-value): '{data_val}'")
            return True

        try:
            base_btn = wrapper.find_element(By.CSS_SELECTOR, "[data-testid='base-select-button']")
        except Exception:
            print("[strategy] base select button not found")
            return False

        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", base_btn)
        except Exception:
            pass

        # Open dropdown quickly
        try:
            base_btn.click()
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", base_btn)
            except Exception:
                pass

        # Prefer: wait for the search input to be visible in the same wrapper, then type exact canonical label and Enter
        option_clicked = False
        search_input = None
        try:
            # Scope to same wrapper to avoid hidden clones
            dropdown = wrapper.find_element(By.CSS_SELECTOR, "#dropdown-Strategy")
        except Exception:
            dropdown = None
        try:
            search_input = wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#Strategy-input")))
        except Exception:
            search_input = None
        # Map a canonical label to type to avoid localization traps
        typed_map = {
            "limit": "limit",
            "market": "market",
            "market+": "market",
            "stop-limit": "stop limit",
            "stop_limit": "stop limit",
        }
        to_type = typed_map.get(desired, (labels[0] if labels else desired))
        if search_input is not None and to_type:
            try:
                search_input.clear()
                search_input.send_keys(to_type)
                search_input.send_keys(Keys.ENTER)
                option_clicked = True
            except Exception:
                option_clicked = False

        # Fallback: try to click a visible matching option if typing path failed
        if not option_clicked and dropdown is not None:
            try:
                dropdown_menu = dropdown.find_element(By.CSS_SELECTOR, "#Strategy-menu")
            except Exception:
                dropdown_menu = dropdown
            for lab in labels:
                try:
                    candidates = dropdown_menu.find_elements(By.XPATH, ".//*[@role='option' or self::button or self::div or self::li]")
                except Exception:
                    candidates = []
                for c in candidates:
                    try:
                        t = _norm(c.text)
                        if not t or t not in labels_set:
                            continue
                        try:
                            c.click()
                        except Exception:
                            try:
                                driver.execute_script("arguments[0].click();", c)
                            except Exception:
                                continue
                        option_clicked = True
                        break
                    except Exception:
                        continue
                if option_clicked:
                    break

        # Verify selection changed quickly via data-value or label
        try:
            wait_short.until(lambda d: (_norm(wrapper.get_attribute('data-value') or '') in labels_set) or (_norm(_get_current_strategy_label(wrapper)) in labels_set))
        except Exception:
            pass

        new_label = _norm(_get_current_strategy_label(wrapper))
        data_val = _norm(wrapper.get_attribute('data-value') or '')
        if new_label in labels_set and new_label and "auswählen" not in new_label:
            print(f"[strategy] Selected via dropdown: '{new_label}'")
            return True
        if data_val and data_val in labels_set:
            print(f"[strategy] Selected via dropdown (data-value): '{data_val}'")
            return True
        print(f"[strategy] Dropdown select failed. current='{new_label}', data-value='{data_val}' desired={list(labels_set)}")
        return False

    # 1a) Tab-basiertes Umschalten (Legacy)
    def _switch_strategy(desired: str):
        """Switch to 'Markt' tab for Market orders, do nothing for Limit orders."""
        desired = desired.strip().lower()
        if desired == 'limit':
            print("[switch_strategy] No tab switch needed for Limit order (default view).")
            return True
        if desired == 'market':
            labels = ['markt', 'market']
            print(f"[switch_strategy] Looking for tab: {labels}")
            try:
                el = None
                tabs = driver.find_elements(By.XPATH, "//*[@role='tab'] | //button[contains(@class,'tab')] | //*[contains(@class,'tab')]")
                print(f"[switch_strategy] Found {len(tabs)} tab candidates.")
                for i, t in enumerate(tabs):
                    try:
                        tab_text = (t.text or '').strip().lower()
                        print(f"  Tab {i}: text='{tab_text}', class='{t.get_attribute('class')}', aria-selected='{t.get_attribute('aria-selected')}'")
                        for label in labels:
                            if label in tab_text:
                                el = t
                                print(f"[switch_strategy] Found tab by label: '{tab_text}'")
                                break
                        if el:
                            break
                    except Exception:
                        pass
                if el is None:
                    print(f"[switch_strategy] Tab 'market' not found.")
                    return False
                # Check if already active/selected
                cls = (el.get_attribute('class') or '')
                aria = (el.get_attribute('aria-selected') or '').lower()
                if 'active' in cls or 'selected' in cls or aria == 'true':
                    print(f"[switch_strategy] Tab 'market' already active.")
                    return True
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                except Exception:
                    pass
                # Try clicking multiple times if needed
                for attempt in range(3):
                    try:
                        el.click()
                    except Exception:
                        try:
                            driver.execute_script("arguments[0].click();", el)
                        except Exception:
                            pass
                    time.sleep(tab_click_delay)
                    # Confirm switch
                    cls = (el.get_attribute('class') or '')
                    aria = (el.get_attribute('aria-selected') or '').lower()
                    if 'active' in cls or 'selected' in cls or aria == 'true':
                        print(f"[switch_strategy] Tab 'market' switched after {attempt+1} attempt(s).")
                        return True
                print(f"[switch_strategy] Tab 'market' NOT switched after retries.")
                return False
            except Exception as e:
                print(f"[switch_strategy] Exception: {e}")
                return False
        print(f"[switch_strategy] Unknown strategy '{desired}', no action taken.")
        return False

    # 1b) Strategie setzen: zuerst Dropdown probieren, dann Fallback Tabs
    desired_strategy = (strategy or "Limit").strip()
    print(f"[strategy] Desired: {desired_strategy}")
    if not _set_strategy_dropdown(desired_strategy):
        # Fallback: altes Tab-Verhalten
        if desired_strategy.lower() in ("market", "market+"):
            _switch_strategy('market')
        else:
            _switch_strategy('limit')

    # 2) Kaufen/Verkaufen
    btn_label = "Kaufen" if action == "buy" else "Verkaufen"
    btn = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{btn_label}')]")))
    if "active" not in (btn.get_attribute("class") or ""):
        btn.click()

    # 3) Menge setzen
    if amount not in (None, "Max."):
        qty = wait.until(EC.visibility_of_element_located((By.ID, "OrderQty")))
        qty.clear()
        qty.send_keys(str(amount))
    elif action == "sell" and (amount is None or str(amount).lower() == "max."):
        try:
            btn_max = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Max.')]")))
            btn_max.click()
        except Exception:
            pass

    # 4) Limit‑Preis/BPS setzen (nur für Limit/Stop-Limit)
    def _norm_txt(s: str) -> str:
        return " ".join((s or "").strip().lower().split())

    def _click_limit_price(label: str) -> bool:
        label_norm = _norm_txt(label)
        # Synonym map: label group to candidate strings
        groups = {
            "bid": ["gebot", "geldkurs", "bid"],
            "ask": ["brief", "briefkurs", "ask", "angebot"],
            "mid": ["mittel", "mid", "mittelkurs", "mittlerer preis"],
        }
        # Expand candidates: if user passed a known member, include its group; else use provided as-is
        candidates = {label_norm}
        for vals in groups.values():
            if label_norm in vals:
                candidates.update(vals)
        # Search strategies: prefer exact text on visible/clickable buttons
        def _cands_xpath_eq(txt: str) -> str:
            return f"//button[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ', 'abcdefghijklmnopqrstuvwxyzäöü'))='{txt}']"
        def _cands_xpath_contains(txt: str) -> str:
            return f"//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ', 'abcdefghijklmnopqrstuvwxyzäöü'), '{txt}')]"
        def _generic_xpath_eq(txt: str) -> str:
            return f"//*[@role='button' or self::button or contains(@class,'button')][normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ', 'abcdefghijklmnopqrstuvwxyzäöü'))='{txt}']"
        def _generic_xpath_contains(txt: str) -> str:
            return f"//*[@role='button' or self::button or contains(@class,'button')][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ', 'abcdefghijklmnopqrstuvwxyzäöü'), '{txt}')]"

        # Try exact matches first for each candidate, then contains
        xbuilders = [_cands_xpath_eq, _generic_xpath_eq, _cands_xpath_contains, _generic_xpath_contains]
        for txt in candidates:
            for xb in xbuilders:
                xp = xb(txt)
                try:
                    el = wait_short.until(EC.element_to_be_clickable((By.XPATH, xp)))
                except Exception:
                    el = None
                if not el:
                    continue
                try:
                    el.click()
                except Exception:
                    try:
                        driver.execute_script("arguments[0].click();", el)
                    except Exception:
                        continue
                print(f"[limit_price] Selected: '{txt}' via xpath: {xp}")
                return True
        print(f"[limit_price] No match for label '{label}' (candidates={sorted(candidates)})")
        return False

    strategy_norm = (strategy or "").strip().lower()
    if strategy_norm in ("limit", "stop-limit", "stop_limit") and limit_price:
        try:
            _click_limit_price(str(limit_price))
        except Exception:
            pass

    # 5) Wenn Market gewünscht, JETZT auf Market(+) umschalten (nachdem Menge/Max gesetzt wurde)
    if (strategy or "").lower() == "market":
        _switch_strategy('market')

    # 6) Senden‑Button nur markieren (Preview)
    try:
        send_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Senden')]")))
        driver.execute_script("arguments[0].style.border='3px solid #ff9800'", send_btn)
    except Exception:
        pass

def preview_pause_and_clear(driver, ms: int = 1000):
    # Keep UI visible briefly and clear the qty field for the next order
    try:
        time.sleep(max(0, int(ms)) / 1000.0)
    except Exception:
        pass
    try:
        qty = driver.find_element(By.ID, "OrderQty")
        qty.clear()
    except Exception:
        pass

# === Loop über Orders ===
def main_loop():
    driver = attach_with_service(use_edge=False, port=9222)
    switch_to_tab_with_title(driver, "Fusion")

    orders = _load_orders("trades_today.json")
    if not orders:
        print("❌ Keine Orders gefunden.")
        return

    total = len(orders)
    for idx, order in enumerate(orders, start=1):
        print(f"➡️  Starte Order {idx}/{total}: {order}")
        pair = order.get("pair") or order.get("symbol") or order.get("asset")
        if not pair:
            print("⚠️ Überspringe Order ohne 'pair'.")
            continue
        strategy = (order.get("strategy") or order.get("type") or "Limit")
        _inject_preview_banner(driver, f"Fusion Preview {idx}/{total}: Wechsel zu {pair}…")
        ok = fix_pair_selection_target(driver, pair, strategy="Limit", debug=True)
        if not ok:
            _inject_preview_banner(driver, f"Fusion ABORT: Pair {pair} nicht gewechselt")
            print(f"❌ Paarwechsel auf {pair} fehlgeschlagen – Order übersprungen")
            continue
        _inject_preview_banner(driver, f"Fusion Preview {idx}/{total}: {pair} – Vorbereitung…")
        trade_order(driver, order)
        _inject_preview_banner(driver, f"Fusion Preview ready {idx}/{total}: {pair} (NO SUBMIT)")
        # Short, deterministic pause and clear instead of waiting for reset (preview-only)
        pause_ms = int(os.environ.get('FUSION_PREVIEW_PAUSE_MS', '1000'))
        preview_pause_and_clear(driver, ms=pause_ms)

    print("✅ Alle Orders abgearbeitet.")

if __name__ == "__main__":
    main_loop()
