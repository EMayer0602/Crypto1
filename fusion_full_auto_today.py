#!/usr/bin/env python3
"""
Fusion Full Auto (Vorbereitung) – Heutige Trades automatisch in bestehende Bitpanda Fusion GUI eintragen.
---------------------------------------------------------------------------------
Ziel: Laufende Fusion-Instanz wird genutzt. Alle heutigen Strategy-Orders werden
nacheinander vorbereitet (Aktion, Menge, Preis). Letzter Klick (Order senden) bleibt manuell.

Voraussetzungen:
1. Bitpanda Fusion ist bereits geöffnet und eingeloggt.
2. Chrome läuft idealerweise mit:  chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\ChromeFusionProfile
3. Python Pakete installiert (pandas, selenium, yfinance, etc.)

Features:
- Generiert frische heutige Orders (keine 14 Tage)
- Reihenfolge: nach Marktwert (größter zuerst) oder original
- Optional: Automatische Instrument-Navigation (--auto-instrument)
- Optional: Nur bestimmte Paare (--pair BTC-EUR --pair ETH-EUR)
- Keine automatische Order-Ausführung (Sicherheitsbarriere)

Beispiele:
  python fusion_full_auto_today.py            # Standard Reihenfolge
  python fusion_full_auto_today.py --sort value --auto-instrument
  python fusion_full_auto_today.py --pair BTC-EUR --pair ETH-EUR --no-prompt
  python fusion_full_auto_today.py --market   # Market-Orders (Preisfeld ausgelassen)
  python fusion_full_auto_today.py --limit-price-override 91000.5

"""
import sys
import os
import time
import argparse
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Reuse existing logic
from auto_backtest_to_fusion import (
    run_strategy_and_collect,
    ensure_chrome_debug,
    attach_and_fill,
)


def filter_and_sort(orders, pairs=None, sort_mode="original"):
    if pairs:
        orders = [o for o in orders if o.get('pair') in pairs]
    if sort_mode == "value":
        orders = sorted(orders, key=lambda o: o.get('market_value_eur', 0), reverse=True)
    return orders


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pair', action='append', help='Nur diese Handelspaare (mehrfach möglich)')
    p.add_argument('--sort', choices=['original','value'], default='original', help='Sortierung: original oder nach Marktwert')
    p.add_argument('--dry-run', action='store_true', help='Nur anzeigen – kein Browserzugriff')
    p.add_argument('--auto-instrument', action='store_true', help='Versuche Instrument automatisch zu wählen')
    p.add_argument('--no-prompt', action='store_true', help='Keine Pause zwischen Orders')
    p.add_argument('--sleep', type=float, default=1.2, help='Pause zwischen Orders (wenn nicht --no-prompt)')
    p.add_argument('--limit-price-override', type=float, help='Optionaler Preis-Override für Limit')
    p.add_argument('--market', action='store_true', help='Market Vorbereitung (kein Preis setzen)')
    p.add_argument('--max', type=int, default=0, help='Max Anzahl Orders (0=alle)')
    args = p.parse_args()

    print("🚀 FUSION FULL AUTO (Vorbereitung) – Start")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Strategie
    orders = run_strategy_and_collect()
    if not orders:
        print("❌ Keine Orders erzeugt – Ende")
        return 1

    # 2. Filter / Sort
    orders = filter_and_sort(orders, pairs=args.pair, sort_mode=args.sort)
    if args.max and args.max > 0:
        orders = orders[:args.max]

    if not orders:
        print("❌ Keine passenden Orders nach Filter")
        return 2

    print(f"📊 Zu verarbeitende Orders: {len(orders)}")
    for i,o in enumerate(orders,1):
        print(f" {i:2d}. {o['action']} {o['quantity']} {o['ticker']} @ {o['price']} (pair={o['pair']}, value=€{o.get('market_value_eur',0):.2f})")

    if args.dry_run:
        print("\n🧪 Dry-Run – keine GUI Interaktion")
        return 0

    # 3. Chrome Debug Verbindung
    if not ensure_chrome_debug():
        print("❌ Kein Chrome Debug-Port – bitte Chrome mit --remote-debugging-port=9222 starten")
        return 3

    successes = 0
    failures = 0

    for idx, od in enumerate(orders, 1):
        print("\n" + "="*70)
        print(f"➡️  ORDER {idx}/{len(orders)}: {od['action']} {od['quantity']} {od['ticker']} @ {od['price']}")
        print("="*70)

        ok = attach_and_fill(
            {
                'action': od['action'],
                'quantity': od['quantity'],
                'price': od['price'],
                'ticker': od['ticker']
            },
            override_price=args.limit_price_override,
            market=args.market,
            instrument_hint=od.get('pair'),
            auto_instrument=args.auto_instrument
        )
        if ok:
            successes += 1
        else:
            failures += 1

        if not args.no_prompt and idx < len(orders):
            try:
                input("Weiter mit ENTER (oder CTRL+C zum Abbrechen)...")
            except KeyboardInterrupt:
                print("\n⏹️ Manuell abgebrochen")
                break
        else:
            time.sleep(max(0, args.sleep))

    print("\n📊 ZUSAMMENFASSUNG:")
    print(f"✅ Erfolgreich vorbereitet: {successes}")
    print(f"⚠️ Probleme: {failures}")
    print("❌ NICHT gesendet – finalen Klick bitte manuell")

    return 0 if failures == 0 else (4 if successes > 0 else 5)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⏹️ Abgebrochen")
        sys.exit(130)
