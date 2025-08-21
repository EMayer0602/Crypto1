#!/usr/bin/env python3
"""
LIVE BACKTEST WORKING

Single-run orchestrator that executes the full workflow in sequence:
1) Update price CSVs (Yahoo advanced + live today) via get_real_crypto_data.py
2) Generate 14-day trades report via get_14_day_trades.py
3) Create trades_today.json via create_trades_today.py
4) Preview/place orders in Bitpanda Fusion UI via BitpandaFusion_trade.py

Also retains a helper to print a TODAY_ONLY CSV from live backtest results.
"""

import sys
import os
import json
import argparse
import subprocess
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Console encoding hardening (avoid UnicodeEncodeError on Windows consoles)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Import helpers (only those used directly below)
from crypto_backtesting_module import run_live_backtest_analysis
from crypto_tickers import crypto_tickers
from get_real_crypto_data import get_bitpanda_price

def get_today_only_trades_report():
    """
    Create a TODAY-ONLY trades CSV in the canonical Bitpanda format:
    Date;Ticker;Quantity;Price;Order Type;Limit Price;Open/Close;Realtime Price Bitpanda

    Rules:
    - Only include entries where Entry Date is today (as Open)
    - Only include exits where Exit Date is today AND Status == 'CLOSED' (as Close)
    - Exclude artificial OPEN rows (no real exit signal)
    - Use get_bitpanda_price for realtime price and as Limit Price
    """
    print("\n📊 Creating TODAY-ONLY Trades Report...")
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    header = "Date;Ticker;Quantity;Price;Order Type;Limit Price;Open/Close;Realtime Price Bitpanda"
    print(f"📋 Header: {header}")

    all_trades = []

    from crypto_backtesting_module import run_backtest

    for ticker_name, cfg in crypto_tickers.items():
        symbol = cfg.get('symbol', ticker_name)
        try:
            print(f"\n🔍 Processing {ticker_name} ({symbol})...")
            live_price = get_bitpanda_price(symbol) or 0.0
            if live_price:
                print(f"   💰 Bitpanda live price: €{live_price:.4f}")
            else:
                # Safe fallback via Yahoo if needed
                try:
                    live_price = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]
                    print(f"   💰 Fallback live price: €{live_price:.4f}")
                except Exception:
                    live_price = 0.0
                    print("   ⚠️ No live price available")

            result = run_backtest(ticker_name, cfg)
            if not result or 'matched_trades' not in result:
                print("   ⚠️ No backtest result/matched_trades")
                continue

            mt = result['matched_trades']
            if mt is None or getattr(mt, 'empty', True):
                print("   ⚠️ matched_trades empty")
                continue

            # Ensure datetime types
            if 'Entry Date' in mt.columns:
                mt = mt.copy()
                mt['Entry Date'] = pd.to_datetime(mt['Entry Date'], errors='coerce')
            if 'Exit Date' in mt.columns:
                mt['Exit Date'] = pd.to_datetime(mt['Exit Date'], errors='coerce')

            # Entries today (OPEN)
            if 'Entry Date' in mt.columns:
                entries_today = mt[mt['Entry Date'].dt.date == today]
                for _, row in entries_today.iterrows():
                    qty = float(row.get('Quantity', 0) or 0)
                    entry_price = float(row.get('Entry Price', live_price) or 0)
                    all_trades.append({
                        'date': today_str,
                        'ticker': ticker_name,
                        'quantity': abs(qty),
                        'price': entry_price,
                        'order_type': 'Limit',
                        'limit_price': live_price or entry_price,
                        'open_close': 'Open',
                        'realtime_price': live_price or entry_price
                    })
                    print(f"   ✅ Open {ticker_name}: {qty:.6f} @ €{entry_price:.4f}")

            # Exits today (CLOSE) — only real CLOSED rows
            if 'Exit Date' in mt.columns:
                exits_today = mt[(mt['Exit Date'].dt.date == today) & (mt.get('Status', 'CLOSED') == 'CLOSED') if 'Status' in mt.columns else (mt['Exit Date'].dt.date == today)]
                for _, row in exits_today.iterrows():
                    qty = float(row.get('Quantity', 0) or 0)
                    exit_price = float(row.get('Exit Price', live_price) or 0)
                    all_trades.append({
                        'date': today_str,
                        'ticker': ticker_name,
                        'quantity': abs(qty),
                        'price': exit_price,
                        'order_type': 'Limit',
                        'limit_price': live_price or exit_price,
                        'open_close': 'Close',
                        'realtime_price': live_price or exit_price
                    })
                    print(f"   ✅ Close {ticker_name}: {qty:.6f} @ €{exit_price:.4f}")

        except Exception as e:
            print(f"   ❌ Error processing {ticker_name}: {e}")

    # Sort newest first (same-day)
    all_trades.sort(key=lambda t: (t['ticker'], t['open_close'] == 'Close'), reverse=True)

    print(f"\n📊 ===== TODAY-ONLY TRADES REPORT =====")
    print(f"🎯 Date Filter: ONLY {today_str}")
    print(f"🔢 Total TODAY Trades: {len(all_trades)}")
    print(f"\n{header}")
    print("-" * 120)
    for tr in all_trades:
        print(f"{tr['date']};{tr['ticker']};{tr['quantity']:.6f};{tr['price']:.4f};{tr['order_type']};{tr['limit_price']:.4f};{tr['open_close']};{tr['realtime_price']:.4f}")

    # Save to canonical filename
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"TODAY_ONLY_trades_{ts}.csv"
    if all_trades:
        df = pd.DataFrame(all_trades, columns=['date','ticker','quantity','price','order_type','limit_price','open_close','realtime_price'])
        df.columns = ['Date','Ticker','Quantity','Price','Order Type','Limit Price','Open/Close','Realtime Price Bitpanda']
        df.to_csv(csv_filename, sep=';', index=False)
        print(f"\n💾 Saved: {csv_filename}")
    else:
        print("\nℹ️ No today trades found.")

    return all_trades

def _run_script(script_name: str, args=None, timeout=None) -> tuple[int, str, str]:
    """Run a Python script (UTF-8 forced) and return (code, stdout, stderr).

    Forces UTF-8 so child scripts with emojis / non-CP1252 chars don't crash on Windows.
    """
    if args is None:
        args = []
    script_path = os.path.join(BASE_DIR, script_name)
    if not os.path.exists(script_path):
        return (127, "", f"Script not found: {script_path}")
    cmd = [sys.executable, script_path] + list(args)
    env = os.environ.copy()
    # Force UTF-8 for stdout/stderr encoding inside child
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")
    try:
        proc = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env
        )
        return (proc.returncode, proc.stdout, proc.stderr)
    except subprocess.TimeoutExpired as e:
        return (124, e.stdout or "", e.stderr or f"Timeout running {script_name}")
    except Exception as e:
        return (1, "", str(e))

def _load_orders_json(path: str) -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            orders = data.get("orders", [])
            return orders if isinstance(orders, list) else []
        return []
    except Exception:
        return []

def orchestrate_single_run(skip_fusion: bool = False):
    """Run full single-run workflow end-to-end."""
    print("🚀 Starting orchestrated LIVE workflow (data ➜ 14-day report ➜ trades_today.json ➜ Fusion)…")

    # 1) Update price CSVs
    print("\n[1/4] 📈 Updating CSVs with Yahoo advanced + live price (get_real_crypto_data.py)…")
    code, out, err = _run_script("get_real_crypto_data.py")
    if out:
        print(out.strip())
    if err:
        print(err.strip())
    if code != 0:
        print(f"❌ get_real_crypto_data.py failed with code {code}. Continuing, but data may be stale.")

    # 2) Generate 14-day trades report
    print("\n[2/4] 🧮 Generating 14-day trades report (get_14_day_trades.py)…")
    code, out, err = _run_script("get_14_day_trades.py")
    if out:
        print(out.strip())
    if err:
        print(err.strip())
    if code != 0:
        print(f"❌ get_14_day_trades.py failed with code {code}. Aborting.")
        return False

    # 3) Create trades_today.json
    print("\n[3/4] 🗂️ Creating trades_today.json from latest 14-day report (create_trades_today.py)…")
    code, out, err = _run_script("create_trades_today.py")
    if out:
        print(out.strip())
    if err:
        print(err.strip())
    if code != 0:
        print(f"❌ create_trades_today.py failed with code {code}. Aborting before Fusion.")
        return False

    # 4) Fusion preview (optional or skipped)
    orders_path = os.path.join(BASE_DIR, "trades_today.json")
    orders = _load_orders_json(orders_path)
    if not orders:
        print("ℹ️ No orders found in trades_today.json. Skipping Fusion preview.")
        print("✅ Orchestrated LIVE workflow completed (no orders).")
        return True
    print(f"✅ trades_today.json contains {len(orders)} order(s).")

    if skip_fusion:
        print("ℹ️ --skip-fusion specified. Not launching Fusion.")
        print("✅ Orchestrated LIVE workflow completed (Fusion skipped).")
        return True

    print("\n[4/4] 🕹️ Launching Fusion order preview (BitpandaFusion_trade.py)…")
    print("   Tip: Start Chrome with remote debugging first:")
    print("   \"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe\" --remote-debugging-port=9222 --user-data-dir=\"C:\\ChromeProfile\"")
    code, out, err = _run_script("BitpandaFusion_trade.py")
    if out:
        print(out.strip())
    if err:
        print(err.strip())
    if code != 0:
        print(f"❌ BitpandaFusion_trade.py exited with code {code}.")
        return False

    print("\n✅ Orchestrated LIVE workflow completed.")
    return True


def legacy_analysis_run(skip_fusion: bool = False) -> bool:
    """Extended legacy behavior now also runs 14-day report + trades_today + optional Fusion.

    Steps:
      1) TODAY-ONLY trades CSV (original legacy feature)
      2) Live backtest analysis (original legacy feature)
      3) Generate 14-day trades report (get_14_day_trades.py)
      4) Create trades_today.json (create_trades_today.py)
      5) Launch BitpandaFusion_trade.py (unless --skip-fusion)
    """
    print("🚀 Starting LEGACY+EXTENDED flow (today-only + analysis + 14-day ➜ trades_today ➜ Fusion)…")

    # 1) Today-only CSV
    today_trades = get_today_only_trades_report()

    # 2) Live backtest analysis
    print("\n" + "="*80)
    result = run_live_backtest_analysis()
    if not result:
        print("❌ Live backtest failed (legacy portion). Continuing with requested additional steps…")

    # 3) 14-day trades report
    print("\n[LEGACY+EXT] 🧮 Generating 14-day trades report (get_14_day_trades.py)…")
    code, out, err = _run_script("get_14_day_trades.py")
    if out:
        print(out.strip())
    if err:
        print(err.strip())
    if code != 0:
        print(f"❌ get_14_day_trades.py failed with code {code}. Aborting remaining steps.")
        return False

    # 4) create trades_today.json
    print("\n[LEGACY+EXT] 🗂️ Creating trades_today.json (create_trades_today.py)…")
    code, out, err = _run_script("create_trades_today.py")
    if out:
        print(out.strip())
    if err:
        print(err.strip())
    if code != 0:
        print(f"❌ create_trades_today.py failed with code {code}. Skipping Fusion.")
        return False

    # 5) Fusion
    if skip_fusion:
        print("ℹ️ --skip-fusion specified. Not launching Fusion (legacy+extended).")
        print("✅ LEGACY+EXTENDED flow completed (Fusion skipped).")
        return True

    orders_path = os.path.join(BASE_DIR, "trades_today.json")
    orders = _load_orders_json(orders_path)
    if not orders:
        print("ℹ️ No orders in trades_today.json. Fusion launch skipped.")
        print("✅ LEGACY+EXTENDED flow completed (no orders).")
        return True
    print(f"✅ trades_today.json contains {len(orders)} order(s). Launching Fusion preview…")

    code, out, err = _run_script("BitpandaFusion_trade.py")
    if out:
        print(out.strip())
    if err:
        print(err.strip())
    if code != 0:
        print(f"❌ BitpandaFusion_trade.py exited with code {code}.")
        return False

    print("\n✅ LEGACY+EXTENDED flow completed.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LIVE Backtest Orchestrator (data -> report -> trades_today -> Fusion)")
    parser.add_argument("--orchestrate", action="store_true", help="Run full data→report→trades_today→Fusion workflow")
    parser.add_argument("--skip-fusion", action="store_true", help="Skip Fusion preview in orchestrated mode")
    parser.add_argument("--legacy", action="store_true", help="Run legacy behavior (today-only CSV + live backtest analysis)")
    args = parser.parse_args()

    if args.legacy:
        # Explicitly run the extended legacy flow (now includes 14-day & Fusion steps)
        ok = legacy_analysis_run(skip_fusion=args.skip_fusion)
        sys.exit(0 if ok else 1)
    else:
        # Default: orchestrated single-run workflow
        ok = orchestrate_single_run(skip_fusion=args.skip_fusion)
        if not ok:
            print("\n⚠️ Orchestration issues encountered. Running legacy analysis as fallback…")
            ok = legacy_analysis_run()
        sys.exit(0 if ok else 1)
