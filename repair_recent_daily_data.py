#!/usr/bin/env python3
"""
Repair last 3 days of daily data for all configured tickers.
- Keep today's (artificial) bar as-is.
- Replace yesterday and the day before yesterday with real Yahoo Finance daily values.
- If daily is missing/unavailable, reconstruct from hourly (60m) data.

Usage:
  python repair_recent_daily_data.py [--tickers BTC-EUR,ETH-EUR]

Writes updates back to <SYMBOL>_daily.csv in the project root.
"""
import argparse
import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# Ensure consistent float formatting on save
PD_FLOAT_FORMAT = '%.8f'


def load_daily_csv(symbol: str) -> pd.DataFrame:
    fname = f"{symbol}_daily.csv"
    if not os.path.exists(fname):
        raise FileNotFoundError(f"Daily CSV not found: {fname}")
    df = pd.read_csv(fname)
    # Normalize columns
    rename_map = {c: c.title() for c in ['open','high','low','close','volume']}
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
    date_col = 'Date' if 'Date' in df.columns else 'date'
    df[date_col] = pd.to_datetime(df[date_col])
    # Normalize to midnight naive dates
    df[date_col] = df[date_col].dt.tz_localize(None)
    df[date_col] = df[date_col].dt.normalize()
    df.set_index(date_col, inplace=True)
    df = df.sort_index()
    # keep only relevant cols
    cols = [c for c in ['Open','High','Low','Close','Volume'] if c in df.columns]
    return df[cols]


def save_daily_csv(symbol: str, df: pd.DataFrame):
    out = df.copy()
    out = out.sort_index()
    out = out[['Open','High','Low','Close','Volume']]
    out.reset_index(names='Date', inplace=True)
    out.to_csv(f"{symbol}_daily.csv", index=False, float_format=PD_FLOAT_FORMAT)


def fetch_daily_bar(symbol: str, day: pd.Timestamp):
    # Yahoo daily is date-range exclusive on end; request day -> day+1
    start = day.strftime('%Y-%m-%d')
    end = (day + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    # Try method 1: download with explicit day range
    df = yf.download(symbol, start=start, end=end, interval='1d', auto_adjust=True, progress=False)
    if df is not None and not df.empty:
        row = df.iloc[0]
        return {
            'Open': float(row['Open']),
            'High': float(row['High']),
            'Low': float(row['Low']),
            'Close': float(row['Close']),
            'Volume': float(row.get('Volume', 0.0))
        }
    # Try method 2: history(period='5d') and pick exact date
    try:
        hist = yf.Ticker(symbol).history(period='7d', interval='1d', auto_adjust=True)
        if hist is not None and not hist.empty:
            hist = hist.copy()
            hist.index = pd.to_datetime(hist.index).tz_localize(None).normalize()
            if day in hist.index:
                row = hist.loc[day]
                return {
                    'Open': float(row['Open']),
                    'High': float(row['High']),
                    'Low': float(row['Low']),
                    'Close': float(row['Close']),
                    'Volume': float(row.get('Volume', 0.0))
                }
    except Exception:
        pass
    return None


def fetch_hourly_ohlc(symbol: str, day: pd.Timestamp):
    # Hourly from day 00:00 to next day 00:00
    start_dt = pd.Timestamp(day.date())
    end_dt = start_dt + pd.Timedelta(days=1)
    for interval in ['60m', '30m', '15m']:
        df = yf.download(symbol, start=start_dt.strftime('%Y-%m-%d %H:%M:%S'), end=end_dt.strftime('%Y-%m-%d %H:%M:%S'), interval=interval, auto_adjust=True, progress=False)
        if df is not None and not df.empty:
            o = float(df['Open'].iloc[0])
            h = float(df['High'].max())
            l = float(df['Low'].min())
            c = float(df['Close'].iloc[-1])
            v = float(df['Volume'].sum()) if 'Volume' in df.columns else 0.0
            return {'Open': o, 'High': h, 'Low': l, 'Close': c, 'Volume': v}
    return None


def repair_two_days(symbol: str) -> bool:
    print(f"\n=== {symbol} ===")
    try:
        daily = load_daily_csv(symbol)
    except Exception as e:
        print(f"  ❌ Load daily failed: {e}")
        return False

    today = pd.Timestamp(datetime.now().date()).normalize()
    yday = today - pd.Timedelta(days=1)
    bby = today - pd.Timedelta(days=2)

    # Guard: keep today's row untouched
    targets = [bby, yday]

    changed = False
    for day in targets:
        print(f"  ↻ Repairing {day.date()} ...")
        bar = fetch_daily_bar(symbol, day)
        if bar is None:
            print("    ℹ️ Daily not available, trying hourly synthesis …")
            bar = fetch_hourly_ohlc(symbol, day)
        if bar is None:
            print("    ❌ Could not fetch hourly either; skipping this day.")
            continue
        else:
            print(f"    ✔ Got bar: O={bar['Open']:.4f} H={bar['High']:.4f} L={bar['Low']:.4f} C={bar['Close']:.4f}")
        # Upsert
        if day in daily.index:
            print("    ✎ Replacing existing bar")
            for k,v in bar.items():
                daily.loc[day, k] = v
        else:
            print("    ➕ Inserting missing bar")
            add = pd.DataFrame([bar], index=[day])
            daily = pd.concat([daily, add])
        changed = True

    if changed:
        save_daily_csv(symbol, daily)
        print("  ✅ Saved updated daily CSV")
        try:
            # Re-open and show last 5 rows for verification
            ver = load_daily_csv(symbol)
            tail = ver.tail(5).reset_index()
            print("  ↪ Last 5 rows after save:")
            for _, r in tail.iterrows():
                print(f"    {r['Date'].date()}, {r['Open']}, {r['High']}, {r['Low']}, {r['Close']}, {r['Volume']}")
        except Exception as _e:
            print(f"  ⚠️ Post-save verify failed: {_e}")
    else:
        print("  ℹ️ No changes made")
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tickers', type=str, default='', help='Comma-separated tickers (default: all from crypto_tickers.py)')
    args = ap.parse_args()

    if args.tickers:
        tickers = [t.strip() for t in args.tickers.split(',') if t.strip()]
    else:
        try:
            from crypto_tickers import crypto_tickers
            tickers = list(crypto_tickers.keys())
        except Exception:
            print("❌ Could not import crypto_tickers; provide --tickers")
            return 1

    any_changed = False
    for sym in tickers:
        try:
            if repair_two_days(sym):
                any_changed = True
        except Exception as e:
            print(f"❌ Error for {sym}: {e}")

    print("\nDone.")
    return 0 if any_changed else 0


if __name__ == '__main__':
    raise SystemExit(main())
