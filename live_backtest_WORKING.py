#!/usr/bin/env python3
"""
LIVE BACKTEST WORKING - Runs live analysis and produces a TODAY_ONLY trades CSV
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the integrated live backtest function
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

if __name__ == "__main__":
    """
    Hauptfunktion - erstellt TODAY_ONLY Trades und ruft die integrierte Live-Backtest Analyse auf
    """
    print("🚀 Starting LIVE Crypto Backtest with TODAY-ONLY Trades Report...")

    # First, create the TODAY-ONLY trades report
    today_trades = get_today_only_trades_report()
    
    print("\n" + "="*80)
    
    # Then run the integrated live backtest analysis
    result = run_live_backtest_analysis()
    
    if result:
        print(f"\n✅ Live backtest completed successfully!")
        print(f"📊 Report: {result}")
        print(f"📊 Today Trades: {len(today_trades)} trades found")
    else:
        print("❌ Live backtest failed!")
        sys.exit(1)
