#crypto_backtesting_module.py
import warnings
warnings.simplefilter("ignore", category=FutureWarning)
import webbrowser
import os
import csv
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from trade_execution import prepare_orders_from_trades, execute_trade, submit_order_bitpanda, save_all_orders_html_report
from config import COMMISSION_RATE, MIN_COMMISSION, ORDER_ROUND_FACTOR, backtesting_begin, backtesting_end
from crypto_tickers import crypto_tickers
from signal_utils import (
    calculate_support_resistance,
    compute_trend,
    assign_long_signals,
    assign_long_signals_extended,
    update_level_close_long,
    simulate_trades_compound_extended,
    berechne_best_p_tw_long,
    plot_combined_chart_and_equity
)
from plotly_utils import plotly_combined_chart_and_equity
from report_generator import generate_combined_report_from_memory
from datetime import datetime, timedelta

# --- Globale Variablen ---
TRADING_MODE = "paper_trading"
API_KEY = ""
capital_plots = {}
CSV_PATH = "C:\\Users\\Edgar.000\\Documents\\____Trading strategies\\Crypto_trading"
# safe_loader.py

def safe_loader(symbol, csv_path, refresh=True):
    filename = os.path.join(csv_path, f"{symbol}.csv")

    # Lade lokale Datei, falls vorhanden
    if os.path.exists(filename):
        df_local = pd.read_csv(filename, parse_dates=["Date"], index_col="Date")
        last_local_date = df_local.index.max()
    else:
        df_local = pd.DataFrame()
        last_local_date = None

    # Neue Daten holen
    start_date = (last_local_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d') if last_local_date else "2020-01-01"
    df_new = yf.download(symbol, start=start_date, interval="1d", auto_adjust=True, progress=False)

    if df_new is None or df_new.empty:
        print(f"⚠️ {symbol}: Keine neuen Daten")
        return df_local if not df_local.empty else None

    df_new.index.name = "Date"
    df_new = df_new[["Open", "High", "Low", "Close", "Volume"]].copy()
    df_new = df_new[~df_new.index.isin(df_local.index)]

    df_combined = pd.concat([df_local, df_new])
    df_combined.sort_index(inplace=True)
    df_combined.to_csv(filename)
    print(f"✅ {symbol}: aktualisiert bis {df_combined.index.max().date()}")

    return df_combined

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

def load_crypto_data_yf(symbol, csv_path, days=365, interval="1d", refresh=True, reset_index=False):
    filename = os.path.join(csv_path, f"{symbol}.csv")

    # 📂 Lokale Datei verwenden, wenn vorhanden
    if os.path.exists(filename) and not refresh:
        try:
            df_local = pd.read_csv(filename, parse_dates=["Date"])
            print(f"📁 Lokale Datei geladen ({len(df_local)} Zeilen)")
            return df_local
        except Exception as e:
            print(f"⚠️ Fehler beim Laden: {e}")
            return None

    # 📥 Neue Daten laden
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)
    print(f"⬇️ Lade {symbol} von {start_date.date()} bis {end_date.date()}")

    df = yf.download(
        symbol,
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        print(f"⚠️ Keine Daten für {symbol}")
        return None

    df["Price"] = df["Close"]
    df.index.name = "Date"
    df.columns.name = None

    df_out = df[["Price", "Open", "High", "Low", "Close", "Volume"]].copy()

    if reset_index:
        df_out.reset_index(inplace=True)

    # 📦 Speichern mit oder ohne Index
    df_out.to_csv(filename, index=not reset_index)
    print(f"✅ CSV gespeichert: {filename} ({len(df_out)} Zeilen)")

    return df_out



def compute_equity_curve(df, trades, start_capital, long=True):
    equity = []
    cap = start_capital
    pos = 0
    entry_price = 0
    trade_idx = 0

    for date in df.index:
        if trade_idx < len(trades):
            entry_key = "buy_date" if long else "short_date"
            entry_price_key = "buy_price" if long else "short_price"
            if trades[trade_idx].get(entry_key) == date:
                pos = trades[trade_idx]["shares"]
                entry_price = trades[trade_idx][entry_price_key]

        if trade_idx < len(trades):
            exit_key = "sell_date" if long else "cover_date"
            if trades[trade_idx].get(exit_key) == date:
                cap += trades[trade_idx]["pnl"]
                pos = 0
                entry_price = 0
                trade_idx += 1

        if pos > 0:
            current_price = df.loc[date, "Close"]
            delta = (current_price - entry_price) if long else (entry_price - current_price)
            value = cap + pos * delta
        else:
            value = cap

        equity.append(value)

    return equity

def debug_loader_status(ticker, csv_path, days=365):
    import os
    import pandas as pd
    import yfinance as yf

    filename = os.path.join(csv_path, f"{ticker}.csv")
    print(f"\n📦 Debug für Ticker: {ticker}")
    print(f"🗂️ Datei erwartet unter: {filename}")
    if not os.path.exists(filename):
        print("🚫 CSV existiert noch nicht.")
    else:
        try:
            df_local = pd.read_csv(filename, parse_dates=["Date"], index_col="Date")
            print(f"✅ Lokale Datei gefunden, letztes Datum: {df_local.index.max().date()}")
        except Exception as e:
            print(f"❌ Fehler beim Laden der CSV: {e}")
            df_local = None

    print("🌐 Versuche Online-Download von yfinance...")
    try:
        df_online = yf.download(ticker, interval="1d", period=f"{days}d", auto_adjust=True, progress=False)
        if df_online.empty:
            print("⚠️ Keine Daten aus Yahoo erhalten.")
        else:
            print(f"📅 Daten von {df_online.index.min().date()} bis {df_online.index.max().date()}")
            print(f"🧾 Online-Datenanzahl: {len(df_online)} Zeilen")
    except Exception as e:
        print(f"❌ Fehler beim yfinance-Download: {e}")


def backtest_single_ticker(ticker, cfg, days=365):
    # 1) Daten laden
     #   df = load_crypto_data_yf(cfg["symbol"], days=days)
    csv_path = f"data/{cfg['symbol']}.csv"  # optional: Pfad zu lokalem Cache
    df = load_crypto_data_yf(cfg["symbol"], csv_path=CSV_PATH, days=365, refresh=True)
    print(df .index.max())
    if df is None or df.empty:
        print(f"[{ticker}] ⚠️ Keine Daten gefunden.")
        return [], [], 0, [], [], None, None

    # 2) Optimierung innerhalb des Zeitbereichs
    p, tw = berechne_best_p_tw_long(df, cfg, begin=backtesting_begin, end=backtesting_end, verbose=True, ticker=ticker)

    # 3) Signale erzeugen
    support, resistance = calculate_support_resistance(df, p, tw)
    ext_signals = assign_long_signals_extended(support, resistance, df, tw, interval="1d")
    ext_signals = update_level_close_long(ext_signals, df)

    # 4) Künstlicher Close vorbereiten
    last_date = df.index[-1]
    last_price = df["Close"].iloc[-1]

    # 5) Simulation der Trades
    capital, trades = simulate_trades_compound_extended(
        ext_signals, df, cfg,
        commission_rate=COMMISSION_RATE,
        min_commission=MIN_COMMISSION,
        round_factor=cfg.get("order_round_factor", ORDER_ROUND_FACTOR),
        artificial_close_price=last_price,
        artificial_close_date=last_date,
        direction="long"
    )

    # 6) Equity-Kurven berechnen
    eq_curve = []
    bh_curve = []
    prices = df["Close"].to_numpy()
    dates = df.index

    for i, price in enumerate(prices):
        current_date = dates[i].normalize()
        eq = cfg["initialCapitalLong"]
        for t in trades:
            if pd.to_datetime(t["buy_date"]) <= current_date <= pd.to_datetime(t["sell_date"]):
                eq += t["pnl"] / len(prices)
        eq_curve = compute_equity_curve(df_opt, trades, cfg["initialCapitalLong"], long=True)
        bh_curve = cfg["initialCapitalLong"] * (df_opt["Close"] / df_opt["Close"].iloc[0])

    return trades, ext_signals, capital, eq_curve, bh_curve, p, tw

def run_crypto_backtests():

    report_data = {}
    today = pd.Timestamp.now().date()

    for ticker, cfg in crypto_tickers.items():
        if not cfg.get("long", False):
            print(f"[SKIP] {ticker} – Long deaktiviert")
            continue

        print(f"\n🚀 Starte Backtest für {ticker} | trade_on = {cfg.get('trade_on')}")

      #  df = load_crypto_data_yf(cfg["symbol"], days=365)
        df = load_crypto_data_yf(cfg["symbol"], csv_path=CSV_PATH, days=365, refresh=True)
        df = clean_crypto_csv("C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading/BTC-EUR.csv")
        save_crypto_csv(df, "C:/Users/Edgar.000/Documents/Cleaned_BTC-EUR.csv", reset_index=True)

        if df is None or df.empty:
            print(f"[{ticker}] ⚠️ Keine Marktdaten verfügbar.")
            continue

        # Optimierung & Zeitfenster
        p, tw = berechne_best_p_tw_long(df, cfg, begin=backtesting_begin, end=backtesting_end, verbose=True, ticker=ticker)
        n = len(df)
        start = int(n * backtesting_begin / 100)
        end = int(n * backtesting_end / 100)
        df_opt = df.iloc[start:end].copy()

        # Signal & Extended
        support, resistance = calculate_support_resistance(df_opt, p, tw)
        ext_signals = assign_long_signals_extended(support, resistance, df_opt, tw, interval="1d")
        ext_signals = update_level_close_long(ext_signals, df_opt)

        last_date = df_opt.index[-1]
        last_price = df_opt["Close"].iloc[-1]

        # Simulation
        capital, trades = simulate_trades_compound_extended(
            ext_signals, df_opt, cfg,
            commission_rate=COMMISSION_RATE,
            min_commission=MIN_COMMISSION,
            round_factor=cfg.get("order_round_factor", ORDER_ROUND_FACTOR),
            artificial_close_price=last_price,
            artificial_close_date=last_date,
            direction="long"
        )

        eq_curve = compute_equity_curve(df_opt, trades, cfg["initialCapitalLong"], long=True)
        bh_curve = cfg["initialCapitalLong"] * (df_opt["Close"] / df_opt["Close"].iloc[0])
        capital = eq_curve[-1]  # falls du Endwert brauchst
        roi = f"{(capital / cfg['initialCapitalLong'] - 1) * 100:.2f} %"
        
        # 📈 Chart erzeugen + anzeigen + Screenshot
        chart_img_base64 = plotly_combined_chart_and_equity(
            df_opt, ext_signals, support, resistance,
            eq_curve, bh_curve, ticker
        )


        # 📟 Konsole Stats
        wins = sum(t["pnl"] > 0 for t in trades)
        losses = sum(t["pnl"] <= 0 for t in trades)
        total_pnl = sum(t["pnl"] for t in trades)
        volume = sum(t["sell_price"] * t["shares"] for t in trades) if trades else 0
        hitrate = 100 * wins / max(len(trades), 1)
        print(f"🧪 Backtesting-Bereich: {df_opt.index[0].date()} bis {df_opt.index[-1].date()} ({backtesting_begin} % bis {backtesting_end} %)")     
        print(f"· Trades: {len(trades)}")
        print(f"· Gewinne: {wins}, Verluste: {losses}")
        print(f"· Trefferquote: {hitrate:.2f} %")
        print(f"· Gesamtgewinn: {total_pnl:,.2f} €")
        print(f"· Volumen: {volume:,.2f} €")
        print(f"· Beste Parameter: p = {p}, tw = {tw}")

        # 📋 Details
        if trades:
            df_trades = pd.DataFrame(trades)
            print(f"\n📋 MATCHED TRADES ({ticker})")
            print(df_trades.to_string(index=False))
        if ext_signals is not None and not isinstance(ext_signals, list):
            df_ext = pd.DataFrame(ext_signals)
            if not df_ext.empty:
                print(f"\n📍 EXTENDED SIGNALS ({ticker})")
                print(df_ext.to_string(index=False))

        # 💾 Sammeln fürs Report
        report_data[ticker] = {
            "trades": trades,
            "ext_signals": ext_signals,
            "eq_curve": eq_curve,
            "bh_curve": bh_curve,
            "capital": capital,
            "opt_p": p,
            "opt_tw": tw,
            "chart_img_base64": chart_img_base64,
            "roi": roi
        }

    # 🧾 Report erstellen & öffnen
    generate_combined_report_from_memory(report_data, report_date=today)
    # ROI anzeigen
    print("\n📊 ROI je Ticker:")
    for ticker, data in report_data.items():
        print(f"· {ticker}: ROI = {data['roi']}")


def run_crypto_backtests_test(crypto_tickers, days=365, debug=True):
    results = {}
    for ticker, cfg in configs.items():
        print(f"\n🔄 Backtest für {ticker} wird gestartet…")

        trades, signals, capital, equity_curve, bh_curve, p, tw = backtest_single_ticker(ticker, cfg, days=days)

        if equity_curve is None or len(equity_curve) == 0:
            print(f"⚠️ Kein Equity Curve erhalten. Debug-Modus aktiv…")
            if debug:
                debug_loader_status(cfg["symbol"], 
                    csv_path="C:\\Users\\Edgar.000\\Documents\\____Trading strategies\\Crypto_trading",
                    days=days)
            continue

        results[ticker] = {
            "trades": trades,
            "signals": signals,
            "capital": capital,
            "equity_curve": equity_curve,
            "buy_hold_curve": bh_curve,
            "performance": p,
            "trade_window": tw
        }             
        print(f"✅ {ticker}: {len(trades)} Trades – Kapital: {capital:.2f} €")
    
    print("\n🎯 Alle Backtests abgeschlossen.")
    return results

import pandas as pd

def clean_crypto_csv(filepath):
    with open(filepath, "r") as file:
        raw = file.readlines()

    # 🧠 Prüfe, ob es sich um doppelte Header handelt
    if len(raw) >= 3 and "Date" in raw[2]:
        print("🔍 Doppelte Header erkannt – bereinige...")
        raw_clean = raw[2:]  # Nur relevante Zeilen ab Zeile 3
        temp_path = filepath.replace(".csv", "_cleaned.csv")

        with open(temp_path, "w") as f:
            f.writelines(raw_clean)

        df = pd.read_csv(temp_path, parse_dates=["Date"])
        print(f"✅ Bereinigt geladen: {len(df)} Zeilen | Datei: {temp_path}")
    else:
        df = pd.read_csv(filepath, parse_dates=["Date"])
        print(f"ℹ️ Normale CSV geladen: {len(df)} Zeilen")

    return df


def save_crypto_csv(df, filepath, reset_index=False):
    if reset_index:
        df.reset_index(inplace=True)

    df_out = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    df_out.to_csv(filepath, index=False)
    print(f"💾 CSV gespeichert: {filepath}")



if __name__ == "__main__":
    run_crypto_backtests()



