#!/usr/bin/env python3
"""
Automatische Pipeline: Strategie -> Heutige Orders -> Fusion GUI Befüllen
=======================================================================

Neu (Multi-Order-Modus):
------------------------
Optional können jetzt ALLE heutigen Orders nacheinander in die bereits offene
Bitpanda Fusion Maske eingetragen werden. Nach jedem vorbereiteten Order
haben Sie die Wahl selbst den finalen Sendeklick auszuführen oder zum nächsten
Order zu springen.

Grund-Prinzip:
1. Strategie ausführen (heutige Orders erzeugen – keine Historie)
2. Auswahl: Einzel-Order (erste / größte) ODER Mehrfachmodus (--all / --max N)
3. Verbindung via bestehendem Chrome (Remote Debugging Port 9222)
4. Für jede Order: Aktion (Kaufen/Verkaufen), Menge, (Limit-)Preis setzen
5. NIEMALS automatisches Absenden – Sicherheitsbarriere

CLI Beispiele:
    python auto_backtest_to_fusion.py --select first
    python auto_backtest_to_fusion.py --select largest --pair BTC-EUR
    python auto_backtest_to_fusion.py --all --max 5 --no-prompt
    python auto_backtest_to_fusion.py --all --pair ETH-EUR --price 1234.5

Relevante Argumente:
--select    first | largest (wenn kein --all genutzt wird)
--pair      Nur Orders eines bestimmten Paares
--dry-run   Nur Analyse & Anzeige – kein Browser Zugriff
--price     Preis-Override (nur für Limit)
--market    Preisfeld überspringen (Market-Order Vorbereitung)
--all       Alle passenden Orders nacheinander vorbereiten
--max N     Obergrenze für Anzahl der Orders im --all Modus
--no-prompt Kein Warten zwischen Orders (nur vorbereiten)
--sleep S   Sekunden Pause zwischen Orders (Default 1.5)

WICHTIG: Das Instrument (z.B. BTC-EUR) muss im Fusion Tab bereits ausgewählt sein.
Ein automatischer Wechsel zwischen Produkten ist (noch) nicht implementiert.
"""

import os
import sys
import time
import glob
import json
import argparse
import logging
import subprocess
from datetime import datetime

# Lokales Verzeichnis sicherstellen
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Strategie-Klasse importieren
from prepare_today_orders import TodayOrderPreparation  # noqa: E402

TRY_ENABLE_DEBUG = True
DEBUG_PORT = 9222
LOG_FILE = os.path.join(BASE_DIR, "fusion_order_preparation.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def run_strategy_and_collect():
    print("🚀 Starte Strategie-Ausführung für heutige Orders...")
    prep = TodayOrderPreparation()
    ok = prep.run()
    if not ok:
        print("❌ Strategie fehlgeschlagen – keine Orders")
        return []
    return prep.today_orders


def find_latest_orders_files(pattern_prefix="TODAY_ORDERS_"):
    files_json = sorted(glob.glob(os.path.join(BASE_DIR, f"{pattern_prefix}*.json")), reverse=True)
    files_csv = sorted(glob.glob(os.path.join(BASE_DIR, f"{pattern_prefix}*.csv")), reverse=True)
    return files_json, files_csv


def choose_order(orders, mode="first", pair=None):
    if pair:
        orders = [o for o in orders if o.get('pair') == pair]
        if not orders:
            print(f"⚠️ Keine Orders für Paar {pair} gefunden")
            return None
    if not orders:
        return None
    if mode == "largest":
        return max(orders, key=lambda o: o.get('market_value_eur', 0))
    return orders[0]


def ensure_chrome_debug():
    """Versucht Debug-Port zu aktivieren falls nicht vorhanden."""
    try:
        import socket
        with socket.create_connection(("127.0.0.1", DEBUG_PORT), timeout=1):
            print(f"✅ Chrome Debug-Port {DEBUG_PORT} erreichbar")
            return True
    except Exception:
        pass

    if not TRY_ENABLE_DEBUG:
        print("⚠️ Debug-Port nicht erreichbar und Auto-Aktivierung deaktiviert")
        return False

    print("🔧 Versuche Chrome mit Debug-Port zu starten...")
    chrome_paths = [
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "chrome.exe"
    ]
    for path in chrome_paths:
        try:
            subprocess.Popen([
                path,
                f"--remote-debugging-port={DEBUG_PORT}",
                f"--user-data-dir={os.path.join(BASE_DIR, 'chrome_debug_profile')}",
                "--disable-web-security"
            ])
            time.sleep(3)
            import socket as s2
            with s2.create_connection(("127.0.0.1", DEBUG_PORT), timeout=3):
                print("✅ Chrome mit Debug-Port gestartet")
                return True
        except Exception:
            continue
    print("❌ Chrome Debug-Modus konnte nicht aktiviert werden")
    return False


def navigate_to_instrument(driver, pair):
    """Versucht das gewünschte Instrument (Pair) im Fusion UI auszuwählen.
    Sehr defensiv – scheitert lautlos, wenn Selektoren nicht gefunden werden.
    pair Beispiel: BTC-EUR -> wir suchen nach BTC.
    """
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        base = pair.split('-')[0].strip().upper()
        print(f"🔍 Versuche Instrument zu wechseln auf: {base} ({pair})")

        # Möglichen Such-/Instrument-Button öffnen (heuristisch)
        open_triggers = [
            "//button[contains(translate(.,'SUCHE','suche'),'suche') or contains(translate(.,'SEARCH','search'),'search')]",
            "//div[contains(@class,'search') and (@role='button' or @tabindex)]",
            "//button[contains(.,'Markt') or contains(.,'Märkte')]",
        ]
        for sel in open_triggers:
            try:
                elems = driver.find_elements(By.XPATH, sel)
                for e in elems:
                    if e.is_displayed():
                        e.click();
                        break
            except Exception:
                continue

        time.sleep(0.5)

        search_selectors = [
            "//input[contains(@placeholder,'Such') or contains(@placeholder,'Search')]",
            "//input[contains(@aria-label,'Such') or contains(@aria-label,'Search')]",
            "//input[@type='text' and (contains(@class,'search') or contains(@class,'Search'))]",
            "//input[contains(@data-testid,'search')]",
        ]
        search_box = None
        for sel in search_selectors:
            try:
                boxes = driver.find_elements(By.XPATH, sel)
                for b in boxes:
                    if b.is_displayed() and b.is_enabled():
                        search_box = b
                        break
                if search_box:
                    break
            except Exception:
                continue

        if not search_box:
            print("⚠️ Kein Suchfeld gefunden – Instrument-Wechsel übersprungen")
            return False

        try:
            search_box.click();
            time.sleep(0.2)
            search_box.clear();
        except Exception:
            pass

        try:
            search_box.send_keys(base)
            time.sleep(0.6)
            search_box.send_keys(Keys.ENTER)
            print("✅ Suchbegriff gesendet (ENTER)")
            time.sleep(0.8)
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].value = arguments[1];", search_box, base)
                print("✅ Suchbegriff per Script gesetzt (ohne ENTER)")
                return True
            except Exception:
                print("⚠️ Konnte Suchfeld nicht befüllen")
                return False
    except Exception as e:
        print(f"⚠️ Instrument-Navigation Fehler: {e}")
        return False


def attach_and_fill(trade, override_price=None, market=False, instrument_hint=None, auto_instrument=False):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

    print("🔗 Verbinde zu bestehendem Chrome...")
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUG_PORT}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    print("✅ Verbunden")

    # Fusion Tab finden
    fusion_found = False
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        url = driver.current_url.lower()
        title = driver.title.lower()
        if any(k in url for k in ["bitpanda", "fusion"]) or any(k in title for k in ["bitpanda", "fusion"]):
            fusion_found = True
            print(f"✅ Fusion Tab aktiv: {driver.title}")
            break
    if not fusion_found:
        print("❌ Kein Fusion Tab gefunden – abbrechen")
        return False

    # Optional Instrument Navigation vor Order-Eingabe
    if auto_instrument and instrument_hint:
        navigate_to_instrument(driver, instrument_hint)

    action_text = 'Kaufen' if trade['action'].lower().startswith('b') else 'Verkaufen'
    # Optional: Prüfen ob der aktuell ausgewählte Instrument-Text passt
    if instrument_hint:
        try:
            # Sehr defensiver Versuch einen Header / Symbolnamen zu finden
            headers = driver.find_elements(By.XPATH, "//h1|//h2|//div[contains(@class,'instrument')]|//span")
            header_texts = [h.text.strip() for h in headers if h.is_displayed() and len(h.text.strip()) < 30]
            if header_texts and not any(instrument_hint.replace('-','').split('-')[0][:3].upper() in t.upper() for t in header_texts):
                print(f"⚠️ Hinweis: Instrument '{instrument_hint}' scheint evtl. nicht aktiv – bitte prüfen.")
        except Exception:
            pass
    print(f"📋 Order zum Eintragen: {action_text} {trade['quantity']} {trade['ticker']} @ {override_price or trade['price']}")

    steps_ok = 0

    # 1. Aktion Button
    print(f"🟢 Versuche Aktion-Button '{action_text}' zu klicken...")
    btn_selectors = [
        f"//button[contains(text(), '{action_text}')]",
        f"//div[contains(text(), '{action_text}') and (@role='button' or contains(@class,'btn'))]",
        f"[data-testid*='{action_text.lower()}']",
    ]
    for sel in btn_selectors:
        try:
            elems = driver.find_elements(By.XPATH, sel) if sel.startswith("//") else driver.find_elements(By.CSS_SELECTOR, sel)
            for e in elems:
                if e.is_displayed() and e.is_enabled():
                    try:
                        e.click(); steps_ok += 1; print("   ✅ Aktion gewählt"); raise StopIteration
                    except Exception:
                        driver.execute_script("arguments[0].click();", e); steps_ok += 1; print("   ✅ Aktion Script-Klick"); raise StopIteration
        except StopIteration:
            break
        except Exception:
            continue

    # 2. Strategie/Order Typ (Limit)
    if not market:
        print("⚡ Versuche 'Limit' auszuwählen...")
        try:
            dropdowns = driver.find_elements(By.XPATH, "//div[contains(@class,'dropdown') or contains(text(),'Strategie')][@role='button' or @tabindex]")
            if dropdowns:
                dropdowns[0].click(); time.sleep(0.5)
                limit_opts = driver.find_elements(By.XPATH, "//div[contains(translate(.,'LIMIT','limit'),'limit')]")
                for opt in limit_opts:
                    if opt.is_displayed():
                        opt.click(); steps_ok += 1; print("   ✅ Limit gewählt"); break
        except Exception:
            print("   ⚠️ Limit Auswahl nicht gefunden")
    else:
        print("⏭️ Market Modus – überspringe Limit Auswahl")

    # 3. Quantity
    print("📈 Menge eintragen...")
    try:
        qty_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder,'Anzahl') or contains(@name,'amount')]")
        for inp in qty_inputs:
            if inp.is_displayed() and inp.is_enabled():
                try:
                    inp.clear(); inp.send_keys(str(trade['quantity'])); steps_ok += 1; print("   ✅ Menge gesetzt"); break
                except Exception:
                    driver.execute_script("arguments[0].value = arguments[1];", inp, str(trade['quantity'])); steps_ok += 1; print("   ✅ Menge per Script gesetzt"); break
    except Exception:
        print("   ❌ Keine Menge-Felder gefunden")

    # 4. Preis (nur wenn nicht Market)
    if not market:
        print("💰 Preis eintragen...")
        price_to_use = override_price or trade['price']
        try:
            price_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder,'Preis') or contains(@name,'price')]")
            for inp in price_inputs:
                if inp.is_displayed() and inp.is_enabled():
                    try:
                        inp.clear(); inp.send_keys(str(price_to_use)); steps_ok += 1; print("   ✅ Preis gesetzt"); break
                    except Exception:
                        driver.execute_script("arguments[0].value = arguments[1];", inp, str(price_to_use)); steps_ok += 1; print("   ✅ Preis per Script gesetzt"); break
        except Exception:
            print("   ❌ Kein Preisfeld gefunden")
    else:
        print("⏭️ Market – Preisfeld ausgelassen")

    logging.info(f"Prepared order: action={trade['action']} qty={trade['quantity']} price={trade['price']} ticker={trade['ticker']} steps_ok={steps_ok}")
    print("\n==============================================")
    print(f"✅ Schritte erfolgreich: {steps_ok}")
    if steps_ok >= 3:
        print("🎯 ORDER IST BEREIT (NICHT GESENDET)")
    else:
        print("⚠️ Unvollständig – bitte manuell prüfen")
    print("❌ Automatisches Senden ist deaktiviert")
    print("==============================================")
    return steps_ok >= 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--select', choices=['first','largest'], default='first')
    parser.add_argument('--pair', help='Nur dieses Handelspaar berücksichtigen (z.B. BTC-EUR)')
    parser.add_argument('--dry-run', action='store_true', help='Keine GUI-Aktion – nur Auswahl anzeigen')
    parser.add_argument('--price', type=float, help='Override Preis (Limit)')
    parser.add_argument('--market', action='store_true', help='Market Order vorbereiten (Preis überspringen)')
    parser.add_argument('--all', action='store_true', help='Alle passenden Orders vorbereiten')
    parser.add_argument('--max', type=int, default=0, help='Maximum Anzahl Orders im --all Modus (0 = unbegrenzt)')
    parser.add_argument('--no-prompt', action='store_true', help='Kein Enter-Warten zwischen Orders')
    parser.add_argument('--sleep', type=float, default=1.5, help='Pause (Sekunden) zwischen Orders')
    parser.add_argument('--auto-instrument', action='store_true', help='Versucht vor jeder Order das Instrument automatisch zu wählen')
    args = parser.parse_args()

    # 1. Strategie laufen lassen (immer frisch, damit nicht alte Daten)
    orders = run_strategy_and_collect()
    if not orders:
        print("❌ Keine Orders generiert – Ende")
        return 1

    # Filter nach Pair falls gesetzt
    if args.pair:
        orders = [o for o in orders if o.get('pair') == args.pair]
        if not orders:
            print(f"❌ Keine Orders für {args.pair}")
            return 2

    # Einzelmodus
    if not args.all:
        chosen = choose_order(orders, mode=args.select, pair=None)
        if not chosen:
            print("❌ Keine passende Order gefunden")
            return 2
        print("\n📌 AUSGEWÄHLTE ORDER:")
        print(json.dumps(chosen, indent=2))
        if args.dry_run:
            print("\n🧪 Dry-Run beendet – keine GUI-Eingabe erfolgt")
            return 0
        if not ensure_chrome_debug():
            print("❌ Kein Chrome Debug – bitte Chrome mit --remote-debugging-port=9222 starten")
            return 3
        ok = attach_and_fill({
            'action': chosen['action'],
            'quantity': chosen['quantity'],
            'price': chosen['price'],
            'ticker': chosen['ticker']
        }, override_price=args.price, market=args.market, instrument_hint=chosen.get('pair'), auto_instrument=args.auto_instrument)
        if ok:
            print("\n🎉 Erfolgreich vorbereitet – prüfen & manuell senden")
            return 0
        print("\n⚠️ Teilweise / fehlgeschlagen – bitte manuell abschließen")
        return 4

    # Mehrfachmodus
    print("\n🔁 MEHRFACH-MODUS: Bereite mehrere Orders vor")
    print(f"Gesamt verfügbare Orders: {len(orders)}")
    limited_orders = orders
    if args.max and args.max > 0:
        limited_orders = orders[:args.max]
        print(f"Begrenzt auf erste {len(limited_orders)} Orders (max={args.max})")

    if args.dry_run:
        print("\n🧪 Dry-Run Übersicht der zu verarbeitenden Orders:")
        for i,o in enumerate(limited_orders,1):
            print(f" {i:2d}. {o['action']} {o['quantity']} {o['ticker']} @ {o['price']} (pair={o['pair']})")
        print("-- Ende Dry-Run --")
        return 0

    if not ensure_chrome_debug():
        print("❌ Kein Chrome Debug – bitte Chrome mit --remote-debugging-port=9222 starten")
        return 3

    successes = 0
    failures = 0
    for idx, ord_data in enumerate(limited_orders, 1):
        print("\n" + "="*70)
        print(f"➡️  ORDER {idx}/{len(limited_orders)}: {ord_data['action']} {ord_data['quantity']} {ord_data['ticker']} @ {ord_data['price']}")
        print("="*70)
        ok = attach_and_fill({
            'action': ord_data['action'],
            'quantity': ord_data['quantity'],
            'price': ord_data['price'],
            'ticker': ord_data['ticker']
        }, override_price=args.price, market=args.market, instrument_hint=ord_data.get('pair'), auto_instrument=args.auto_instrument)
        if ok:
            successes += 1
        else:
            failures += 1
        if not args.no_prompt and idx < len(limited_orders):
            try:
                input("Weiter mit ENTER (oder CTRL+C zum Abbrechen)...")
            except KeyboardInterrupt:
                print("\n⏹️ Benutzerabbruch – stoppe Mehrfachmodus")
                break
        time.sleep(max(0, args.sleep))

    print("\n📊 MEHRFACHMODUS ZUSAMMENFASSUNG:")
    print(f"✅ Erfolgreich vorbereitet: {successes}")
    print(f"⚠️ Probleme: {failures}")
    print("(NICHT gesendet – manueller Klick erforderlich)")
    return 0 if failures == 0 else (4 if successes>0 else 5)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⏹️ Abgebrochen")
        sys.exit(130)
