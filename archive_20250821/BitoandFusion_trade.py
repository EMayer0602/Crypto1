# BitpandaFusion_trade.py
# "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfile"
# https://web.bitpanda.com/fusion/trade/BTC-EUR
# http://localhost:9222/json/version
# 
# BitpandaFusion_trade_loop.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEFAULT_TIMEOUT = 15

@dataclass
class Order:
    pair: str
    amount: str
    action: str
    strategy: str

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
from dataclasses import dataclass
from typing import Optional, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

DEFAULT_TIMEOUT = 15

@dataclass
class Order:
    pair: str
    amount: str
    action: str
    strategy: str

# -------------------------------
# Helpers
# -------------------------------

def wait(driver, timeout=DEFAULT_TIMEOUT):
    return WebDriverWait(driver, timeout)

def ensure_tab(driver, label: str):
    """
    Aktiviert den Tab 'Limit' oder 'Market' anhand sichtbaren Labels.
    """
    # Exakte Beschriftung
    try:
        tab = wait(driver).until(EC.element_to_be_clickable(
            (By.XPATH, f"//button[normalize-space(text())='{label}']")))
        tab.click()
        time.sleep(0.25)
        return
    except TimeoutException:
        pass
    # role=tab Fallback
    tab = driver.find_elements(By.XPATH, f"//*[@role='tab' and (normalize-space(text())='{label}' or .//*[normalize-space(text())='{label}'])]")
    if tab:
        tab[0].click()
        time.sleep(0.25)
        return
    raise NoSuchElementException(f"Tab '{label}' nicht gefunden")

def select_action(driver, action: str):
    """
    Stellt Buy/Sell ein (Kaufen/Verkaufen).
    """
    action = action.lower().strip()
    labels = ["Buy", "Kaufen"] if action == "buy" else ["Sell", "Verkaufen"]
    for lab in labels:
        try:
            btn = wait(driver).until(EC.element_to_be_clickable(
                (By.XPATH, f"//button[normalize-space(text())='{lab}']")))
            btn.click()
            time.sleep(0.2)
            return
        except TimeoutException:
            continue
    # Fallback: segmentierte Controls
    seg = driver.find_elements(By.XPATH, "//*[@role='tab' or @role='radio' or contains(@class,'segmented')]//*[normalize-space(text())='Buy' or normalize-space(text())='Kaufen' or normalize-space(text())='Sell' or normalize-space(text())='Verkaufen']")
    if seg:
        seg[0].click()
        time.sleep(0.2)
        return
    raise NoSuchElementException("Buy/Sell-Umschalter nicht gefunden")

def select_pair(driver, pair: str):
    """
    Öffnet die Pair-Suche und wählt das gewünschte Paar aus.
    """
    # Trigger öffnen
    triggers = [
        "//button[contains(@aria-label,'Pair') or contains(@aria-label,'Handelspaar')]",
        "//button[contains(@class,'pair') or contains(@class,'asset') or contains(@class,'market')]",
        "//*[contains(@class,'pair') and (self::button or self::div)]",
    ]
    opened = False
    for xp in triggers:
        elems = driver.find_elements(By.XPATH, xp)
        if elems:
            try:
                wait(driver).until(EC.element_to_be_clickable(elems[0]))
                elems[0].click()
                opened = True
                break
            except Exception:
                continue
    if not opened:
        # Fallback: globale Suche/Lupe
        try:
            search_icon = driver.find_elements(By.XPATH, "//button[.//*[name()='svg'] or contains(@class,'search')]")
            if search_icon:
                search_icon[0].click()
                opened = True
        except Exception:
            pass
    if not opened:
        raise NoSuchElementException("Pair-Dropdown/Suchdialog konnte nicht geöffnet werden.")

    time.sleep(0.3)

    # Suchfeld
    si = None
    for xp in [
        "//input[@type='search']",
        "//input[contains(@placeholder,'Search') or contains(@placeholder,'Suchen')]",
        "//div[contains(@role,'dialog')]//input",
    ]:
        cand = driver.find_elements(By.XPATH, xp)
        if cand:
            si = cand[0]
            break
    if not si:
        raise NoSuchElementException("Suchfeld im Pair-Dialog nicht gefunden.")
    try:
        si.clear()
    except Exception:
        pass
    si.send_keys(pair)
    time.sleep(0.4)

    # Ergebnis wählen
    option = None
    for xp in [
        f"//li[.//*[normalize-space(text())='{pair}'] or normalize-space(text())='{pair}']",
        "//li[.//text()]"
    ]:
        cand = driver.find_elements(By.XPATH, xp)
        if cand:
            option = cand[0]
            break
    if not option:
        raise NoSuchElementException(f"Kein Ergebnis für Pair '{pair}' gefunden.")
    wait(driver).until(EC.element_to_be_clickable(option))
    option.click()
    time.sleep(0.3)

def find_amount_input(driver) -> Optional[object]:
    """
    Sucht das Betragsfeld (für BUY).
    """
    for xp in [
        "//input[@name='amount']",
        "//input[@type='number']",
        "//input[@inputmode='decimal']",
        "//input[contains(@aria-label,'Amount') or contains(@aria-label,'Betrag')]",
        "//input[contains(@placeholder,'Amount') or contains(@placeholder,'Betrag')]",
    ]:
        els = driver.find_elements(By.XPATH, xp)
        if els:
            return els[0]
    return None

def set_amount(driver, amount: str):
    inp = find_amount_input(driver)
    if not inp:
        raise NoSuchElementException("Amount/Betrag-Feld nicht gefunden.")
    try:
        inp.clear()
    except Exception:
        # Fallback: Ctrl+A + Backspace
        inp.click()
        inp.send_keys("\uE009" + "a")
        inp.send_keys("\uE003")
    inp.send_keys(amount)
    time.sleep(0.1)

def click_max(driver):
    """
    Klickt den 'Max.'-Button für SELL.
    """
    labels = ["Max.", "Max", "MAX", "100%"]
    # Erst exakter Text
    for lab in labels:
        try:
            btn = wait(driver).until(EC.element_to_be_clickable(
                (By.XPATH, f"//button[normalize-space(text())='{lab}']")))
            btn.click()
            time.sleep(0.15)
            return
        except TimeoutException:
            continue
    # Fallback: aria-label o.ä.
    cand = driver.find_elements(By.XPATH, "//*[self::button or self::a][contains(@aria-label,'Max')]")
    if cand:
        cand[0].click()
        time.sleep(0.15)
        return
    # Letzter Fallback: Buttons in der Nähe vom Amount-Feld
    amt = find_amount_input(driver)
    if amt:
        sib = driver.find_elements(By.XPATH, "//button[contains(.,'Max') or contains(.,'100%')]")
        if sib:
            sib[0].click()
            time.sleep(0.15)
            return
    raise NoSuchElementException("Max.-Button für SELL nicht gefunden")

def submit(driver):
    """
    Finaler Submit.
    """
    labels = [
        "Place order", "Order platzieren", "Jetzt kaufen", "Jetzt verkaufen",
        "Buy", "Sell", "Kaufen", "Verkaufen", "Submit", "Bestätigen"
    ]
    for lab in labels:
        try:
            btn = wait(driver).until(EC.element_to_be_clickable(
                (By.XPATH, f"//button[normalize-space(text())='{lab}']")))
            btn.click()
            return
        except TimeoutException:
            continue
    # Fallback auf primären Button
    cand = driver.find_elements(By.XPATH, "//button[contains(@class,'primary') or contains(@class,'submit') or contains(@class,'confirm')]")
    if cand:
        cand[0].click()
        return
    raise NoSuchElementException("Submit/Bestätigen-Button nicht gefunden")

# -------------------------------
# Hauptablauf
# -------------------------------

def trade_order(driver, order: Order):
    """
    Limit-Flow:
      - Pair wählen
      - Action (Buy/Sell)
      - Tab 'Limit'
      - BUY: amount setzen, SELL: Max.
      - bei strategy=market: kurz vor dem Absenden auf 'Market' umschalten
      - SELL (robust): nach Umschalten erneut Max. klicken, falls die Menge resettet wird
    """
    # Pair + Action
    select_pair(driver, order.pair)
    select_action(driver, order.action)
    ensure_tab(driver, "Limit")

    # Menge setzen
    if order.action.lower().strip() == "sell":
        click_max(driver)
    else:
        if not order.amount:
            raise ValueError("Für BUY wird 'amount' benötigt.")
        set_amount(driver, order.amount)

    # Market erst ganz am Ende
    if order.strategy.lower().strip() == "market":
        ensure_tab(driver, "Market")
        # Manche UIs resetten dabei die Menge → SELL zur Sicherheit erneut Max.
        if order.action.lower().strip() == "sell":
            try:
                click_max(driver)
            except Exception:
                # Wenn nicht nötig/verfügbar, einfach weiter
                pass
        time.sleep(0.2)

    submit(driver)

# -------------------------------
# I/O und Bootstrap
# -------------------------------

def load_orders(path: str = "orders.json") -> List[Order]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    orders: List[Order] = []
    for d in data:
        orders.append(Order(
            pair=str(d["pair"]).strip(),
            amount=str(d.get("amount", "")).strip(),
            action=str(d["action"]).strip(),
            strategy=str(d.get("strategy", "limit")).strip()
        ))
    return orders

def setup_driver(headless: bool = False):
    opts = ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=opts)
    return driver

def main():
    orders = load_orders("orders.json")
    driver = setup_driver(headless=False)
    try:
        # WICHTIG: Kein driver.get() – du startest im bereits geöffneten Trading-Tab
        input("Im Trading-Tab bereit sein (eingeloggt, richtiger Bereich). Drücke Enter zum Start...")
        for idx, o in enumerate(orders, 1):
            print(f"[{idx}/{len(orders)}] {o.action.upper()} {o.pair} via {o.strategy.upper()} (amount='{o.amount}')")
            try:
                trade_order(driver, o)
                print("→ Order abgeschickt.")
                time.sleep(1.0)
            except Exception as e:
                print(f"Fehler bei Order {idx}: {e}")
                # Optional: Screenshot/Retries ergänzen
                continue
        print("Fertig.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
