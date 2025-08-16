#!/usr/bin/env python3
"""
Generate a semicolon-separated trade list for the current August (or current month),
for all configured tickers, using matched trades from the backtest and the live
Bitpanda-like price (via Yahoo Finance proxy) as Limit Price.

Header:
Ticker;Date;Action;Shares;Order Type;Limit Price

Notes:
- Action values are Buy/Sell
- Order Type is always 'limit'
- Limit Price is fetched live per symbol at runtime
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd

# Ensure local imports resolve
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest
from get_real_crypto_data import get_bitpanda_price


def get_live_price_safe(symbol: str) -> float:
    """Fetch a Bitpanda-preferred live price; fallback to last daily close if needed."""
    # Prefer Bitpanda live (with Yahoo intraday fallback internally)
    try:
        price = get_bitpanda_price(symbol)
        if price is not None:
            return float(price)
    except Exception:
        pass
    # Final fallback: last known daily close via yfinance (lazy import)
    try:
        import yfinance as yf
        hist = yf.Ticker(symbol).history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except Exception:
        return 0.0
    return 0.0


def first_day_of_month(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, 1)


def last_day_of_month(dt: datetime) -> datetime:
    # Move to first of next month then subtract one day
    if dt.month == 12:
        next_month = datetime(dt.year + 1, 1, 1)
    else:
        next_month = datetime(dt.year, dt.month + 1, 1)
    return next_month - timedelta(days=1)


def collect_august_trades():
    now = datetime.now()
    # Use current month window; if you specifically want August, run during August or set AUGUST_YEAR/MONTH env
    month = int(os.environ.get("AUGUST_MONTH", now.month))
    year = int(os.environ.get("AUGUST_YEAR", now.year))

    start = datetime(year, month, 1)
    end = last_day_of_month(start)

    header = "Ticker;Date;Action;Shares;Order Type;Limit Price"
    lines = [header]

    summary_count = 0

    for ticker_name, config in crypto_tickers.items():
        symbol = config.get('symbol', ticker_name)
        try:
            result = run_backtest(symbol, config)
            if not result:
                continue
            mt = result.get('matched_trades')
            if mt is None or getattr(mt, 'empty', True):
                continue

            # Normalize columns
            # Expect: 'Entry Date', 'Exit Date', 'Quantity'
            for col in ('Entry Date', 'Exit Date'):
                if col in mt.columns:
                    mt[col] = pd.to_datetime(mt[col], errors='coerce')

            live_price = get_live_price_safe(symbol)

            # Emit BUY entries in window
            if 'Entry Date' in mt.columns:
                buys = mt[(mt['Entry Date'] >= start) & (mt['Entry Date'] <= end)].copy()
                for _, row in buys.iterrows():
                    date_str = row['Entry Date'].strftime('%Y-%m-%d') if pd.notna(row['Entry Date']) else ''
                    qty = float(row.get('Quantity', 0) or 0)
                    lines.append(f"{ticker_name};{date_str};Buy;{qty:.6f};limit;{live_price:.4f}")
                    summary_count += 1

            # Emit SELL entries in window
            if 'Exit Date' in mt.columns:
                sells = mt[(mt['Exit Date'] >= start) & (mt['Exit Date'] <= end)].copy()
                for _, row in sells.iterrows():
                    date_str = row['Exit Date'].strftime('%Y-%m-%d') if pd.notna(row['Exit Date']) else ''
                    qty = float(row.get('Quantity', 0) or 0)
                    lines.append(f"{ticker_name};{date_str};Sell;{qty:.6f};limit;{live_price:.4f}")
                    summary_count += 1

        except Exception as e:
            print(f"[WARN] {ticker_name}: {e}")

    # Sort by Date desc, then Ticker, then Action
    def sort_key(line: str):
        if line.startswith('Ticker;'):
            return (datetime.min, '')
        parts = line.split(';')
        # Ticker;Date;Action;Shares;Order Type;Limit Price
        try:
            d = datetime.strptime(parts[1], '%Y-%m-%d')
        except Exception:
            d = datetime.min
        return (-int(d.strftime('%Y%m%d') or 0), parts[0], parts[2])

    # keep header first, sort the rest
    head, body = lines[0], lines[1:]
    body_sorted = sorted(body, key=lambda x: sort_key(x))
    lines = [head] + body_sorted

    # Print
    print("\n" + header)
    print("-" * 80)
    for ln in body_sorted:
        print(ln)
    print(f"\nTotal lines (without header): {summary_count}")

    # Save to CSV
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_name = f"august_trades_{year:04d}{month:02d}_{ts}.csv"
    with open(out_name, 'w', encoding='utf-8') as f:
        for ln in lines:
            f.write(ln + "\n")
    print(f"Saved: {out_name}")


if __name__ == '__main__':
    collect_august_trades()
