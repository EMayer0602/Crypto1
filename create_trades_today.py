#!/usr/bin/env python3
"""
Create trades_today.json from the latest 14-day trades CSV for today's date.

Rules:
- pair = Ticker
- action = from report (lowercase)
- strategy = "Limit"
- amount: for SELL -> "Max.", for BUY -> Quantity from report
- limit_price: for SELL -> "+25bps", for BUY -> "-25bps"
"""

import os
import glob
import json
from datetime import datetime
import argparse
import pandas as pd
from typing import Optional, List, Dict

WORKDIR = os.path.dirname(os.path.abspath(__file__))


def find_latest_report(pattern: str = "14_day_trades_REAL_*.csv") -> Optional[str]:
    files = sorted(glob.glob(os.path.join(WORKDIR, pattern)))
    return files[-1] if files else None


def load_today_trades(csv_path: str, today: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, sep=';')
    # Normalize column names just in case
    cols = {c: c.strip() for c in df.columns}
    df.rename(columns=cols, inplace=True)
    # Expect columns: Date, Ticker, Quantity, ..., Action
    required = {'Date', 'Ticker', 'Quantity', 'Action'}
    if not required.issubset(df.columns):
        raise ValueError("CSV missing required columns: Date, Ticker, Quantity, Action")
    return df[df['Date'].astype(str) == today].copy()


def build_orders(df: pd.DataFrame) -> List[Dict]:
    orders: List[Dict] = []
    for _, row in df.iterrows():
        action = str(row['Action']).strip().lower()
        ticker = str(row['Ticker']).strip()
        qty = float(row['Quantity']) if pd.notna(row['Quantity']) else 0.0

        if action == 'sell':
            amount = "Max."
            limit_price = "+25bps"
        else:
            # Treat anything else as buy
            amount = round(qty, 6)
            limit_price = "-25bps"

        orders.append({
            "pair": ticker,
            "action": action,
            "strategy": "Limit",
            "amount": amount,
            "limit_price": limit_price,
        })
    return orders


def main():
    parser = argparse.ArgumentParser(description="Create trades_today.json from latest 14-day CSV for a given date (default: today)")
    parser.add_argument("--date", dest="date", help="YYYY-MM-DD to extract trades for (default: today)")
    args = parser.parse_args()

    target_date = (args.date or datetime.now().strftime('%Y-%m-%d')).strip()
    latest_csv = find_latest_report()
    if not latest_csv:
        print("No 14-day trades CSV found. Run get_14_day_trades.py first.")
        orders_payload = {"orders": []}
    else:
        try:
            today_df = load_today_trades(latest_csv, target_date)
            orders = build_orders(today_df)
            orders_payload = {"orders": orders}
            print(f"Found {len(orders)} trade(s) for {target_date} in {os.path.basename(latest_csv)}")
        except Exception as e:
            print(f"Error creating trades_today.json: {e}")
            orders_payload = {"orders": []}

    out_path = os.path.join(WORKDIR, 'trades_today.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(orders_payload, f, ensure_ascii=False, indent=2)
    print(f"Saved {out_path}")


if __name__ == '__main__':
    main()
