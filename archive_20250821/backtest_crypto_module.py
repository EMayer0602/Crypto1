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

def backtest_single_ticker(cfg, symbol):
    import pandas as pd

    # Daten laden
    df = load_crypto_data_yf(symbol)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[1].capitalize() for col in df.columns]

    # Backtest-Zeitraum filtern (letzte N Jahre)
    backtest_years = cfg.get("backtest_years", [1])
    years = backtest_years[-1] if isinstance(backtest_years, list) else backtest_years
    end_date = df.index.max()
    start_date = end_date - pd.DateOffset(years=years)
    df_bt = df[(df.index >= start_date) & (df.index <= end_date)]

    # Prozentwerte für Start/Ende aus Konfiguration
    start_percent = cfg.get("backtest_start_percent", 0.25)
    end_percent = cfg.get("backtest_end_percent", 0.95)
    n = len(df_bt.index)
    start_idx = int(n * start_percent)
    end_idx = int(n * end_percent)
    start_idx = max(0, min(start_idx, n - 1))
    end_idx = max(0, min(end_idx, n - 1))

    # Parameter-Optimierung
    p, tw = berechne_best_p_tw_long(
        df_bt, cfg,
        start_idx, end_idx,
        verbose=False,
        ticker=symbol
    )

    # Support/Resistance
    supp_bt, res_bt = calculate_support_resistance(df_bt, p, tw, verbose=False, ticker=symbol)

    # Signale
    std_bt = assign_long_signals(supp_bt, res_bt, df_bt, tw, "1d")
    ext_bt = assign_long_signals_extended(supp_bt, res_bt, df_bt, tw, "1d")
    ext_bt = update_level_close_long(ext_bt, df_bt)

    # Trades simulieren
    cap_bt, trades_bt = simulate_trades_compound_extended(
        ext_bt, df_bt, cfg,
        starting_capital=cfg.get("initialCapitalLong", 10000),
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1)
    )

    # Buy & Hold-Kurve
    bh_curve_bt = [cfg.get("initialCapitalLong", 10000) * (p / df_bt["Close"].iloc[0]) for p in df_bt["Close"]]

    # Plot
    plot_combined_chart_and_equity(
        df_bt,
        std_bt,
        supp_bt,
        res_bt,
        trades_bt,
        bh_curve_bt,
        symbol,
        initial_capital=cfg.get("initialCapitalLong", 10000),
        backtest_years=backtest_years
    )

    return cap_bt, trades_bt, std_bt, supp_bt, res_bt, bh_curve_bt
    import pandas as pd

    # Daten laden
    df = load_crypto_data_yf(symbol)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[1].capitalize() for col in df.columns]

    # Backtest-Zeitraum filtern (letzte N Jahre)
    backtest_years = cfg.get("backtest_years", [1])
    years = backtest_years[-1] if isinstance(backtest_years, list) else backtest_years
    end_date = df.index.max()
    start_date = end_date - pd.DateOffset(years=years)
    df_bt = df[(df.index >= start_date) & (df.index <= end_date)]

    # Prozentwerte für Start/Ende aus Konfiguration
    start_percent = cfg.get("backtest_start_percent", 0.25)
    end_percent = cfg.get("backtest_end_percent", 0.95)
    n = len(df_bt.index)
    start_idx = int(n * start_percent)
    end_idx = int(n * end_percent)
    start_idx = max(0, min(start_idx, n - 1))
    end_idx = max(0, min(end_idx, n - 1))

    # Parameter-Optimierung
    p, tw = berechne_best_p_tw_long(
        df_bt, cfg,
        start_idx, end_idx,
        verbose=False,
        ticker=symbol
    )

    # Support/Resistance
    supp_bt, res_bt = calculate_support_resistance(df_bt, p, tw, verbose=False, ticker=symbol)

    # Signale
    std_bt = assign_long_signals(supp_bt, res_bt, df_bt, tw, "1d")
    ext_bt = assign_long_signals_extended(supp_bt, res_bt, df_bt, tw, "1d")
    ext_bt = update_level_close_long(ext_bt, df_bt)

    # Trades simulieren
    cap_bt, trades_bt = simulate_trades_compound_extended(
        ext_bt, df_bt, cfg,
        starting_capital=cfg.get("initialCapitalLong", 10000),
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1)
    )

    # Buy & Hold-Kurve
    bh_curve_bt = [cfg.get("initialCapitalLong", 10000) * (p / df_bt["Close"].iloc[0]) for p in df_bt["Close"]]

    # Plot
    plotly_combined_chart_and_equity(
        df_bt,
        std_bt,
        supp_bt,
        res_bt,
        trades_bt,
        bh_curve_bt,
        symbol,
        initial_capital=cfg.get("initialCapitalLong", 10000),
        backtest_years=backtest_years
    )

    return cap_bt, trades_bt, std_bt, supp_bt, res_bt, bh_curve_bt
def run_crypto_backtests(days=365):
    for symbol, cfg in crypto_tickers.items():
        print(f"\n=== Backtest für {symbol} ===")
        backtest_single_ticker(symbol, cfg)  # <– symbol übergeben


if __name__ == "__main__":
    run_crypto_backtests()
