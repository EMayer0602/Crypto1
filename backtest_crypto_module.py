# crypto_backtesting_module.py

import yfinance as yf
import pandas as pd
import numpy as np

from config import COMMISSION_RATE, MIN_COMMISSION, ORDER_ROUND_FACTOR, backtesting_begin, backtesting_end, backtest_years
from crypto_tickers import crypto_tickers
from signal_utils import (
    calculate_support_resistance, compute_trend, assign_long_signals,
    assign_long_signals_extended, update_level_close_long,
    simulate_trades_compound_extended, berechne_best_p_tw_long,
    plot_combined_chart_and_equity
)

import os
import time
import yfinance as yf
import pandas as pd

from crypto_backtesting_module import load_crypto_data_yf
'''
def load_crypto_data_yf(symbol, days=365, cache_dir="data_cache"):
    """
    Lädt Tagesdaten aus Yahoo oder Cache. Flacht Spalten ab,
    prüft auf 'Close', konvertiert zu float und löscht NaNs.
    """

    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{symbol}_{days}d.csv")
    max_age = 24 * 3600  # 1 Tag

    # 1) Cache verwenden, wenn frisch
    if os.path.exists(cache_file):
        age = time.time() - os.path.getmtime(cache_file)
        if age < max_age:
            print(f"[CACHE] Lade {symbol} aus {cache_file}")
#            df = pd.read_csv(cache_file)
#            df.index = pd.to_datetime(df.index)
            df = pd.read_csv(cache_file, parse_dates=["Date"])
            df.set_index("Date", inplace=True)

            print(f"[DEBUG] Index-Typ: {type(df.index[0])}")

        else:
            print(f"[CACHE] Veraltet – lade neu von Yahoo")
            df = yf.download(symbol, interval="1d", period=f"{days}d", auto_adjust=True, progress=False)
            df.to_csv(cache_file)
    else:
        print(f"[CACHE] Kein Cache – lade neu von Yahoo")
        df = yf.download(symbol, interval="1d", period=f"{days}d", auto_adjust=True, progress=False)
        df.to_csv(cache_file)

    # 2) Abflachen, wenn nötig
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        print(f"[LOADER] Abgeflachte Spalten: {list(df.columns)}")

    # 3) Close-Spalte sicherstellen
    if "Close" not in df.columns:
        close_cols = [c for c in df.columns if "close" in c.lower()]
        if close_cols:
            df["Close"] = df[close_cols[0]]
            print(f"[LOADER] Close umbenannt aus {close_cols[0]}")
        else:
            print(f"[LOADER] Keine Close-Spalte für {symbol} – breche ab")
            return None

    # 4) Typen erzwingen & NaNs bereinigen
    for col in ("Open", "High", "Low", "Close"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["Close"], inplace=True)
    return df if not df.empty else None
'''



def backtest_single_ticker(ticker, cfg, days=365):
    df = load_crypto_data_yf(cfg["symbol"], days=days)
    print(df.head())
    print(df.index.min(), "→", df.index.max())
    if df is None or df.empty:
        cache_file = os.path.join("data_cache", f"{cfg['symbol']}_{days}d.csv")
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"[CACHE] Gelöscht: {cache_file} – beim nächsten Lauf wird neu geladen")
        print(f"{ticker}: Keine Daten verfügbar – überspringe Ticker")
        return


    df = df.sort_index()

    df.index = pd.to_datetime(df.index)
    if df is None:
        print(f"{ticker}: Keine Daten verfügbar – überspringe Ticker")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        print(f"[LOADER] Spalten abgeflacht: {list(df.columns)}")

    if df is None: 
        print(f"{ticker}: keine Daten."); return

    # 1) Param-Optimierung
    p, tw = berechne_best_p_tw_long(df, cfg, backtesting_begin, backtesting_end)

    # 2) Signale generieren
    supp, res = calculate_support_resistance(df, p, tw)
    std  = assign_long_signals(supp, res, df, tw, "1d")
    ext  = assign_long_signals_extended(supp, res, df, tw, "1d")
    ext  = update_level_close_long(ext, df)

    # 3) Simulation
    cap, trades = simulate_trades_compound_extended(
        ext, df,
        starting_capital=cfg["initialCapitalLong"],
        commission_rate=COMMISSION_RATE,
        min_commission=MIN_COMMISSION,
        round_factor=cfg["order_round_factor"]
    )
    print(f"{ticker}: Final Capital = {cap:.2f} €")
    ext.to_csv(f"extended_{ticker}.csv", index=False)
    pd.DataFrame(trades).to_csv(f"trades_{ticker}.csv", index=False)

    # 4) Equity-Kurve
    close_arr = df["Close"].to_numpy(dtype=float)
    dates     = df.index
    eq_curve  = []
    cash      = cfg["initialCapitalLong"]
    pos, entry = 0, 0
    ti = 0

    for i, date in enumerate(dates):
        price = close_arr[i]
        # buy?
        if ti < len(trades) and pd.to_datetime(trades[ti]["buy_date"])==date:
            pos   = trades[ti]["shares"]
            entry = trades[ti]["buy_price"]
        # sell?
        if ti < len(trades) and pd.to_datetime(trades[ti]["sell_date"])==date:
            cash += trades[ti]["pnl"]
            pos, entry = 0, 0
            ti += 1
        eq_curve.append(cash + pos*(price-entry) if pos>0 else cash)

    # 5) Buy & Hold
    try:
        start = close_arr[0]
    except:
        start = 1.0
    bh_curve = [(cfg["initialCapitalLong"]*(p/start)) for p in close_arr]

    # 6) Plot
    plot_combined_chart_and_equity(
        df, std, pd.DataFrame(), supp, res, compute_trend(df),
        eq_curve, [], bh_curve, ticker
    )

def run_crypto_backtests(days=365):
    for symbol, cfg in crypto_tickers.items():
        print(f"\n=== Backtest für {symbol} ===")
        backtest_single_ticker(symbol, cfg)  # <– symbol übergeben


if __name__ == "__main__":
    run_crypto_backtests()
