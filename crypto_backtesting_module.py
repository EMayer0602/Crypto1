
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
from config import COMMISSION_RATE, MIN_COMMISSION, ORDER_ROUND_FACTOR, backtesting_begin, backtesting_end, backtest_years
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
CSV_PATH = "C:\\Users\\Edgar.000\\Documents\\____Trading strategies\\Crypto_trading1"
base_dir = "C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading1"
# safe_loader.py

def safe_loader(symbol, csv_path, refresh=True):
    filename = os.path.join(csv_path, f"{symbol}_daily.csv")

    def flatten_csv_header_if_needed(filename):
        with open(filename, "r", encoding="utf-8") as f:
            first = f.readline()
            second = f.readline()
            third = f.readline()
            f.seek(0)
            if first.strip().startswith("Price") and third.strip().startswith("Date"):
                df = pd.read_csv(filename, skiprows=3, header=None)
                df.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
                df.to_csv(filename, index=False)
                print(f"⚒️ Header in {filename} flattened and fixed.")
                return df
            elif first.strip().startswith("Date"):
                return pd.read_csv(filename, parse_dates=["Date"], index_col="Date")
            elif first.strip().startswith("Price"):
                df = pd.read_csv(filename)
                df = df.rename(columns={"Price": "Date"})
                df.to_csv(filename, index=False)
                print(f"⚒️ Header in {filename} fixed (Price->Date).")
                return pd.read_csv(filename, parse_dates=["Date"], index_col="Date")
            else:
                raise ValueError(f"Unrecognized header in {filename}")

    if os.path.exists(filename):
        try:
            df_local = flatten_csv_header_if_needed(filename)
            if "Date" in df_local.columns:
                df_local["Date"] = pd.to_datetime(df_local["Date"])
                df_local.set_index("Date", inplace=True)
            last_local_date = df_local.index.max()
        except Exception as e:
            print(f"⚠️ {symbol} CSV-Problem: {e}. Lösche und lade neu.")
            os.remove(filename)
            df_local = pd.DataFrame()
            last_local_date = None
    else:
        df_local = pd.DataFrame()
        last_local_date = None

    today = pd.Timestamp(datetime.utcnow().date())
    if last_local_date is not None:
        next_date = last_local_date + pd.Timedelta(days=1)
        if next_date > today:
            print(f"{symbol}: Already up to date.")
            return df_local
        start_date = next_date.strftime('%Y-%m-%d')
    else:
        start_date = "2020-01-01"

    df_new = yf.download(symbol, start=start_date, end=None, interval="1d", auto_adjust=True, progress=False)
    if df_new is None or df_new.empty:
        print(f"⚠️ {symbol}: Keine neuen Daten")
        return df_local if not df_local.empty else None

    df_new.index.name = "Date"
    df_new = df_new[["Open", "High", "Low", "Close", "Volume"]].copy()
    if not df_local.empty:
        df_new = df_new[~df_new.index.isin(df_local.index)]

    df_combined = pd.concat([df_local, df_new])
    df_combined.sort_index(inplace=True)
    df_combined.to_csv(filename)
    print(f"✅ {symbol}: aktualisiert bis {df_combined.index.max().date()}")

    return df_combined

def load_crypto_data_yf(ticker: str, data_dir: str = "Crypto_trading1") -> pd.DataFrame:

    file_path = os.path.join(data_dir, f"{ticker}.csv")

    if not os.path.exists(file_path):
        print(f"⚠️ Datei für {ticker} nicht gefunden. Hole komplette Historie von Yahoo...")
        df = yf.download(ticker, period="max", interval="1d")
    else:
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Fehler beim Einlesen von {file_path}: {e}")
            return pd.DataFrame()

        # Index-Spalte entfernen, wenn vorhanden
        if df.columns[0].lower() in ["unnamed: 0", "index"]:
            df = df.drop(columns=[df.columns[0]])

        # Header reparieren falls Spalten fehlen
        required_cols = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
        if len(df.columns) < len(required_cols):
            print(f"🔧 Repariere Header in {ticker}.csv")
            df.columns = required_cols[:len(df.columns)]

        # Date-Spalte als Zeitindex setzen
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df.set_index("Date", inplace=True)
        df = df.sort_index()

        # Falls heute fehlt: Daten ergänzen
        today = pd.Timestamp.now().floor("D")
        if today not in df.index:
            print(f"➕ Hole heutigen Kurs für {ticker} von Yahoo Finance")
            today_data = yf.download(ticker, start=today, interval="1m")
            if not today_data.empty:
                latest = today_data.iloc[-1]
                new_row = pd.DataFrame([{
                    "Open": latest["Open"],
                    "High": latest["High"],
                    "Low": latest["Low"],
                    "Close": latest["Close"],
                    "Adj Close": latest.get("Adj Close", latest["Close"]),
                    "Volume": latest["Volume"]
                }], index=pd.to_datetime([today]))
                df = pd.concat([df, new_row])
                df = df.sort_index()
            else:
                print(f"⚠️ Keine Minuten-Daten für heute verfügbar für {ticker}")

    return df

import os
import pandas as pd
from crypto_tickers import crypto_tickers

def load_and_update_daily_crypto(minute_df, symbol, base_dir):
    # --- MultiIndex flatten falls nötig ---
    if isinstance(minute_df.columns, pd.MultiIndex):
        minute_df.columns = minute_df.columns.get_level_values(0)

    # Spaltennamen vereinheitlichen (Großbuchstaben)
    col_map = {c.lower(): c for c in ['Open', 'High', 'Low', 'Close', 'Volume']}
    minute_df = minute_df.rename(columns={c: col_map.get(c.lower(), c) for c in minute_df.columns})

    # Prüfen ob alle Spalten da sind
    required = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(r in minute_df.columns for r in required):
        raise ValueError(f"[{symbol}] Minutendaten fehlen Spalten: {set(required) - set(minute_df.columns)}")
    print("low_dt type:", type(low_dt))
    print("low_dt:", low_dt)
    # Datumsspalte erzeugen
    if "datetime" in minute_df.columns:
        minute_df['date'] = pd.to_datetime(minute_df['datetime']).dt.date
    else:
        minute_df['date'] = pd.to_datetime(minute_df.index).date

    grouped = minute_df.groupby('date')
    daily = pd.DataFrame({
        "date": grouped["date"].first(),
        "Open": grouped["Open"].first(),
        "High": grouped["High"].max(),
        "Low": grouped["Low"].min(),
        "Close": grouped["Close"].last(),
        "Volume": grouped["Volume"].sum()
    })
    daily = daily.sort_values("date").reset_index(drop=True)

    daily_path = os.path.join(base_dir, f"{symbol}_daily.csv")
    daily[["date", "Open", "High", "Low", "Close", "Volume"]].to_csv(
        daily_path, index=False, header=True
    )
    print(f"[{symbol}] ✅ Tagesdaten gespeichert unter: {daily_path}")
    return daily

# -------------------------
# BATCH für alle Ticker:
# -------------------------

import pandas as pd

def calculate_trade_statistics(trades, equity_curve, initial_capital, trade_fee):
    # Only consider exits
    exits = [t for t in trades if t.get('Action', '').upper() in ('SELL', 'EXIT', 'CLOSE')]
    total_trades = len(exits)
    winning_trades = sum(1 for trade in exits if trade.get('PnL', 0) > 0)
    losing_trades = total_trades - winning_trades
    total_pnl = sum(trade.get('PnL', 0) for trade in exits)
    total_fees = sum(
        round((trade.get('buy_price', 0) + trade.get('sell_price', 0)) * trade.get('shares', 0) * trade_fee / 2, 2)
        for trade in trades
    )
    win_percentage = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    loss_percentage = (losing_trades / total_trades) * 100 if total_trades > 0 else 0

    # Defensive equity_curve handling
    if not isinstance(equity_curve, pd.Series):
        equity_curve = pd.Series(equity_curve)
    equity_curve = pd.to_numeric(equity_curve, errors='coerce').fillna(method='ffill').fillna(0)

    if equity_curve.empty:
        max_drawdown = 0.0
    else:
        peak = equity_curve.cummax()
        # Prevent division by zero
        safe_peak = peak.replace(0, 1e-9)
        drawdown = (peak - equity_curve) / safe_peak
        max_drawdown = drawdown.max()
        if pd.isna(max_drawdown):
            max_drawdown = 0.0

    stats = {
        "Total Trades": total_trades,
        "Winning Trades": winning_trades,
        "Losing Trades": losing_trades,
        "Win Percentage": win_percentage,
        "Loss Percentage": loss_percentage,
        "Total PnL": total_pnl,
        "Total Fees": total_fees,
        "Final Capital": initial_capital + total_pnl,
        "Max Drawdown": max_drawdown * 100
    }
    return stats

def batch_update_all(base_dir, start_date_daily="2020-01-01", start_date_minute="2024-01-01"):
    for symbol in CRYPTO_SYMBOLS:
        update_daily_csv(symbol, base_dir, start_date_daily)
        update_minute_csv(symbol, base_dir, start_date_minute)

def update_daily_csv(symbol, base_dir, start_date="2024-07-31"):
    """
    Lädt Tagesdaten via yfinance für das Symbol und speichert sie als saubere CSV.
    Header ist IMMER korrekt! Erzeugt Datei {symbol}_daily.csv im base_dir.
    """
    df = yf.download(symbol, start=start_date, interval="1d", auto_adjust=True, progress=False)
    if df is None or df.empty:
        print(f"[{symbol}] ⚠️ Keine Daten gefunden.")
        return None

    # MultiIndex-Problem lösen
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()  # Date als Spalte

    if 'Date' not in df.columns:
        print(f"[{symbol}] ⚠️ 'Date' column not found after reset_index.")
        return None

    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

    # Ensure directory exists
    os.makedirs(base_dir, exist_ok=True)

    # Speichern mit sauberem Header
    out_path = os.path.join(base_dir, f"{symbol}_daily.csv")
    print(base_dir)
    print(out_path)
    df.to_csv(out_path, index=False, header=True)
    print(f"[{symbol}] ✅ Daily CSV gespeichert: {out_path}")
    return df

def update_minute_csv(symbol, base_dir, start_date):
    import os
    import yfinance as yf
    import pandas as pd

    df = yf.download(symbol, start=start_date, interval="1m", auto_adjust=True, progress=False)
    if df is None or df.empty:
        print(f"[{symbol}] ⚠️ Keine Minutendaten gefunden.")
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()

    # Zeitspalte auf "DateTime" bringen
    if "Datetime" in df.columns:
        df = df.rename(columns={"Datetime": "DateTime"})
    elif "Date" in df.columns:
        df = df.rename(columns={"Date": "DateTime"})
    elif "index" in df.columns:
        df = df.rename(columns={"index": "DateTime"})
    else:
        raise ValueError("Keine Zeitspalte gefunden! Spalten sind: " + str(df.columns))

    # Volume erzwingen
    if "Volume" not in df.columns:
        print(f"[{symbol}] ⚠️ Volume fehlt, wird mit NaN ergänzt.")
        df["Volume"] = float("nan")

    # Nur gewünschte Spalten und speichern
    df = df[["DateTime", "Open", "High", "Low", "Close", "Volume"]]
    out_path = os.path.join(base_dir, f"{symbol}_minute.csv")
    df.to_csv(out_path, index=False, header=True)
    print(f"[{symbol}] ✅ Minute CSV gespeichert: {out_path}")
    return df

    df = yf.download(symbol, start=start_date, interval="1m", auto_adjust=True, progress=False)
    if df is None or df.empty:
        print(f"[{symbol}] ⚠️ Keine Minutendaten gefunden.")
        return None

    # MultiIndex-Problem lösen
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()

    # Spaltennamen anpassen
    if "Datetime" not in df.columns:
        if "Date" in df.columns:
            df = df.rename(columns={"Date": "DateTime"})

    # --- Volume-Prüfung: ---
    if "Volume" not in df.columns:
        print(f"[{symbol}] ⚠️ Volume fehlt in den Minutendaten! Füge leere Volume-Spalte hinzu.")
        df["Volume"] = float("nan")

    # Nur die gewünschten Spalten abspeichern
    df = df[["DateTime", "Open", "High", "Low", "Close", "Volume"]]
    out_path = os.path.join(base_dir, f"{symbol}_minute.csv")
    df.to_csv(out_path, index=False, header=True)
    print(f"[{symbol}] ✅ Minute CSV gespeichert: {out_path}")
    return df

def batch_update_all_daily_csv(base_dir, get_minute_df_func):
    """
    Für alle Ticker aus crypto_tickers wird load_and_update_daily_crypto ausgeführt.
    get_minute_df_func(symbol) muss ein DataFrame der Minutendaten zurückgeben.
    """
    for ticker, cfg in crypto_tickers.items():
        symbol = cfg["symbol"]
        print(f"\n⏳ Lade Minutendaten für {symbol} ...")
        try:
            minute_df = get_minute_df_func(symbol)
            if minute_df is None or minute_df.empty:
                print(f"[{symbol}] ⚠️ Keine Minutendaten gefunden, überspringe.")
                continue
            load_and_update_daily_crypto(minute_df, symbol, base_dir)
        except Exception as e:
            print(f"[{symbol}] ❌ Fehler: {e}")

# Beispiel für eine Funktion, die Minutendaten lädt (Dummy!)
def get_minute_df_yfinance(symbol):
    import yfinance as yf
    df = yf.download(symbol, period="5d", interval="1m", progress=False, auto_adjust=True)
    return df if df is not None and not df.empty else None

def get_backtest_data(df, backtest_years, backtesting_begin, backtesting_end):
    """
    Beschränkt den DataFrame zuerst auf die letzten N Jahre/Monate,
    dann auf den gewünschten Prozentbereich.
    Gibt die verwendeten Zeitspannen per print() aus.
    """
    # Schritt 1: Nur die letzten N Jahre/Monate
    df_years = restrict_to_backtest_years(df, backtest_years)
    print(f"[Debug] Zeitraum nach backtest_years: {df_years.index.min().date()} bis {df_years.index.max().date()} (Zeilen: {len(df_years)})")

    # Schritt 2: Prozentualer Bereich
    df_bt = restrict_to_percent_slice(df_years, backtesting_begin, backtesting_end)
    print(f"[Debug] Zeitraum nach Prozent-Schnitt: {df_bt.index.min().date()} bis {df_bt.index.max().date()} (Zeilen: {len(df_bt)})")

    return df_bt

# Hilfsfunktionen:

def load_daily_csv(filename):
    """
    Lädt eine Tagesdaten-CSV mit richtigem Header.
    Erwartet: Date,Open,High,Low,Close,Volume als Spalten.
    Gibt DataFrame mit Date als Index zurück.
    """
    df = pd.read_csv(filename, parse_dates=["Date"])
    df = df.set_index("Date")
    return df

def safe_parse_date(date_str):
    """Versucht, ein Datum im erwarteten Format zu parsen. Fehler werden zu NaT."""
    try:
        return pd.to_datetime(date_str, format="%Y-%m-%d %H:%M:%S")
    except:
        return pd.NaT

def update_daily_crypto_with_today1(minute_df, symbol, daily_path):
    """
    Aggregiert die Minutendaten zu Tagesdaten,
    entfernt doppelte Headerstufen und sichert das Datum gegen Parsingfehler.
    """
    if minute_df is None or minute_df.empty:
        print(f"[{symbol}] ❌ Keine gültigen Minutendaten vorhanden.")
        return

    # 🧽 Schritt 1: Datum bereinigen
    minute_df["Date"] = minute_df["Date"].apply(safe_parse_date)
    minute_df["Date"] = pd.to_datetime(minute_df["Date"]).dt.date

    # 🔁 Schritt 2: Aggregation auf Tagesbasis
    daily_df_new = minute_df.groupby("Date").agg({
        "price": ["first", "max", "min", "last"],
        "volume": "sum"
    })

    # 🧹 Schritt 3: Header flatten
    daily_df_new.columns = ["Open", "High", "Low", "Close", "Volume"]
    daily_df_new.index = pd.to_datetime(daily_df_new.index)

    # 📁 Schritt 4: Vorhandene Datei laden (falls vorhanden)
    if os.path.exists(daily_path):
        daily_df_existing = pd.read_csv(daily_path, parse_dates=["Date"], index_col="Date")
        daily_df_existing.index = pd.to_datetime(daily_df_existing.index)
        daily_df = pd.concat([daily_df_existing, daily_df_new])
        daily_df = daily_df[~daily_df.index.duplicated(keep="last")]  # Duplikate entfernen
    else:
        daily_df = daily_df_new

    # 💾 Schritt 5: Speichern mit sauberem Header
    daily_df.to_csv(daily_path, index=True)
    print(f"[{symbol}] ✅ Tagesdaten erfolgreich aktualisiert.")


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

def load_daily_data_for_backtest(symbol, base_dir):
    filename = f"{symbol}_daily.csv"
    daily_path = os.path.join(base_dir, filename)
    if not os.path.exists(daily_path):
        print(f"[{symbol}] ❌ Datei fehlt: {daily_path}")
        return None
    try:
        df = pd.read_csv(daily_path, parse_dates=["date"])
        return df
    except Exception as e:
        print(f"[{symbol}] ❌ Fehler beim Einlesen: {e}")
        return None

def backtest_single_ticker(ticker, cfg, backtest_years, backtesting_begin, backtesting_end, days=365):
    # 1) Daten laden
    csv_path = f"data/{cfg['symbol']}.csv"
    df = load_crypto_data_yf(cfg["symbol"], data_dir=CSV_PATH)
    if df is None or df.empty:
        print(f"[{ticker}] ⚠️ Keine Daten gefunden.")
        return [], [], 0, [], [], None, None

    # Stelle sicher, dass der Index ein DatetimeIndex ist
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # 2) Beschränke auf letzte Jahre/Monate
    df_years = restrict_to_backtest_years(df, backtest_years)
    print(f"[Debug] Zeitraum nach backtest_years: {df_years.index.min().date()} bis {df_years.index.max().date()} (Zeilen: {len(df_years)})")

    # 3) Prozentbereich aus df_years wählen
    df_bt = restrict_to_percent_slice(df_years, backtesting_begin, backtesting_end)
    print(f"[Debug] Zeitraum nach Prozent-Schnitt: {df_bt.index.min().date()} bis {df_bt.index.max().date()} (Zeilen: {len(df_bt)})")

    # 4) Optimierung innerhalb des Zeitbereichs
    p, tw = berechne_best_p_tw_long(df_bt, cfg, begin=backtesting_begin, end=backtesting_end, verbose=True, ticker=ticker)

    # 5) Signale erzeugen
    support, resistance = calculate_support_resistance(df_bt, p, tw)
    signal_df = assign_long_signals_extended(support, resistance, df_bt, tw, "1d")
    signal_df = update_level_close_long(signal_df, df_bt)
    print(signal_df.to_string(index=False))
    #print(signal_df.columns)
    print(signal_df[signal_df['Action'] != "None"])
    # 6) Künstlicher Close vorbereiten
    last_date = df_bt.index[-1]
    last_price = df_bt["Close"].iloc[-1]

    # 7) Simulation der Trades
    capital, trades = simulate_trades_compound_extended(
        signal_df, df_bt, cfg,
        commission_rate=COMMISSION_RATE,
        min_commission=MIN_COMMISSION,
        round_factor=cfg.get("order_round_factor", ORDER_ROUND_FACTOR),
        artificial_close_price=last_price,
        artificial_close_date=last_date,
        direction="long"
    )
    print("\n--- Matched Trades ---")
    for t in trades:
        print(t)


    # 8) Equity-Kurven berechnen
    eq_curve = compute_equity_curve(df_bt, trades, cfg["initialCapitalLong"], long=True)
    print(f"[Debug] trades={trades}, eq_curve_len={len(eq_curve) if eq_curve is not None else 'None'}")
    stats = calculate_trade_statistics(trades, eq_curve, cfg["initialCapitalLong"], COMMISSION_RATE)
    print("\n--- Trade-Statistik ---")
    for k, v in stats.items():
        print(f"{k:20}: {v}")
    print("[Debug] Stats-Block erreicht und ausgegeben.")
    bh_curve = cfg["initialCapitalLong"] * (df_bt["Close"] / df_bt["Close"].iloc[0])

    return trades, signal_df, capital, eq_curve, bh_curve, p, tw,stats

def restrict_to_backtest_years(df, backtest_years):    
    # Nimmt die letzten N Jahre oder Monate (backtest_years = [0, 2] für 2 Jahre)
    max_years = backtest_years[1]
    if max_years < 1:
        min_timestamp = df.index.max() - pd.DateOffset(months=int(max_years*12))
    else:
        min_timestamp = df.index.max() - pd.DateOffset(years=int(max_years))
    return df[df.index >= min_timestamp]

def restrict_to_percent_slice(df, begin, end):
    n = len(df)
    start_idx = int(n * begin / 100)
    end_idx = int(n * end / 100)
    return df.iloc[start_idx:end_idx]

def run_crypto_backtests(
    crypto_tickers,
    backtest_years=[0,2],           # z.B. die letzten 2 Jahre
    backtesting_begin=0,            # Prozentbereich: ab
    backtesting_end=100             # Prozentbereich: bis
):
    today_str = datetime.now().strftime("%Y-%m-%d")
    results = []

    for ticker, cfg in crypto_tickers.items():
        symbol = cfg["symbol"]
        csv_path = f"C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading1/{symbol}_daily.csv"

        # 📥 CSV laden
        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            print(f"[{ticker}] ❌ Datei fehlt: {csv_path}")
            continue

        # Spalten standardisieren
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        if "Close" not in df.columns:
            print(f"[{ticker}] ⚠️ 'Close'-Spalte fehlt → übersprungen")
            continue

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date", "Close"])
        df = df.sort_values("Date")
        df = df.set_index("Date")

        # Heute ergänzen, falls nicht vorhanden
        if today_str not in df.index.strftime("%Y-%m-%d"):
            try:
                import yfinance as yf
                df1m = yf.download(symbol, interval="1m", period="1d", progress=False, auto_adjust=True)
            except Exception as e:
                print(f"[{ticker}] ⚠️ Fehler beim Abrufen von yfinance: {e}")
                df1m = None

            if df1m is not None and not df1m.empty:
                df1m.columns = [str(c).strip().capitalize() for c in df1m.columns]
                required_cols = ["Open", "High", "Low", "Close"]

                if all(col in df1m.columns for col in required_cols):
                    df1m = df1m.dropna(subset=required_cols)
                    if not df1m.empty:
                        new_row = {
                            "Date": today_str,
                            "Open": df1m["Open"].iloc[0],
                            "High": df1m["High"].max(),
                            "Low": df1m["Low"].min(),
                            "Close": df1m["Close"].iloc[-1],
                            "Volume": df1m["Volume"].sum() if "Volume" in df1m.columns else None
                        }
                        df = pd.concat([df, pd.DataFrame([new_row]).set_index("Date")], axis=0)
                        print(f"[{ticker}] ➕ Tageskurs ergänzt: {new_row['Close']:.2f} EUR")
                    else:
                        print(f"[{ticker}] ⚠️ Minuten-Daten leer nach dropna")
                else:
                    missing = set(required_cols) - set(df1m.columns)
                    print(f"[{ticker}] ⚠️ Minuten-Daten unvollständig: {missing}")
            else:
                print(f"[{ticker}] ⚠️ Keine Minuten-Daten verfügbar")

        # Beschneiden auf Zeitraum/Prozentbereich
        df_years = restrict_to_backtest_years(df, backtest_years)
        print(f"[{ticker}] Zeitraum nach backtest_years: {df_years.index.min().date()} bis {df_years.index.max().date()} (Zeilen: {len(df_years)})")

        df_bt = restrict_to_percent_slice(df_years, backtesting_begin, backtesting_end)
        print(f"[{ticker}] Zeitraum nach Prozent-Schnitt: {df_bt.index.min().date()} bis {df_bt.index.max().date()} (Zeilen: {len(df_bt)})")

        valid_close = df_bt["Close"].dropna()
        if valid_close.empty:
            print(f"[{ticker}] ⚠️ Keine gültigen 'Close'-Werte → übersprungen")
            continue

        start_price = valid_close.iloc[0]
        end_price = valid_close.iloc[-1]
        pct_change = (end_price / start_price - 1) * 100

        results.append({
            "Ticker": ticker,
            "Start": round(start_price, 2),
            "End": round(end_price, 2),
            "Total Return %": round(pct_change, 2),
            "Latest Close": round(end_price, 2)
        })

        print(f"[{ticker}] ✅ Backtest: {pct_change:.2f}%")

    # 📊 Ergebnisse nur wenn vorhanden
    if results:
        df_results = pd.DataFrame(results)
        df_results.set_index("Ticker", inplace=True)

        print("\n📊 Strategie-Ergebnisse:")
        print(df_results.sort_values(by="Total Return %", ascending=False))

        # 🔽 Ergebnisse speichern
        export_dir = "C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading1/"
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, f"backtest_results_{today_str}.csv")
        df_results.to_csv(export_path)
        print(f"\n📁 Ergebnisse gespeichert unter: {export_path}")

        return df_results
    else:
        print("\n🚫 Keine gültigen Ergebnisse erzeugt")
        return pd.DataFrame()

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


def save_crypto_csv(df: pd.DataFrame, ticker: str, data_dir: str = "Crypto_trading1"):
    file_path = os.path.join(data_dir, f"{ticker}.csv")
    df.reset_index().to_csv(file_path, index=False)
    print(f"✅ Gespeichert: {file_path}")
0

def update_daily_crypto_with_today():
    base_dir = "C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading1/"
    os.makedirs(CSV_PATH, exist_ok=True)

    for ticker, cfg in crypto_tickers.items():
        symbol = cfg["symbol"]
        print(f"\n📈 Lade {symbol}...")

        try:
            # Lade Tagesdaten aus Yahoo
            df = yf.download(symbol, interval="1d", period="30d", auto_adjust=True, progress=False)

            if df is None or df.empty:
                print(f"[{symbol}] ⚠️ Keine Daten erhalten")
                continue

            df.columns = [str(c).strip().capitalize() for c in df.columns]
            df = df.dropna(subset=["Open", "High", "Low", "Close"])
            df["Date"] = df.index
            df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

            # Speichern als *_cleaned.csv
            file_path = os.path.joinCSV_PATH(CSV_PATH, f"{symbol}_cleaned.csv")
            df.to_csv(file_path, index=False)
            print(f"[{symbol}] ✅ Gespeichert: {file_path}")

        except Exception as e:
            print(f"[{symbol}] ❌ Fehler beim Abrufen: {e}")
    
def main():
    # Für jedes Symbol die zugehörige Konfiguration verwenden
    for symbol, cfg in crypto_tickers.items():
        print(f"\n===== {symbol} =====")
        # Backtest durchführen
        trades, signal_df, capital, eq_curve, bh_curve, p, tw, stats = backtest_single_ticker(
            symbol, cfg, backtest_years, backtesting_begin, backtesting_end
        )

        # OHLC-Daten laden
        df = load_crypto_data_yf(symbol, data_dir=CSV_PATH)
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        standard_signals = signal_df

        # Support/Resistance berechnen
        support, resistance = calculate_support_resistance(df, p, tw)
        print("✅ Backtest abgeschlossen.")

        # Extended Trades ausgeben
        print("\n--- Extended Trades ---")
        if not signal_df.empty:
            print(signal_df)
        else:
            print("Keine extended trades gefunden.")

        # Matched Trades ausgeben
        print("\n--- Matched Trades ---")
        if trades:
            df_trades = pd.DataFrame(trades)
            print(df_trades)
        else:
            print("Keine matched trades gefunden.")

        # Statistiken ausgeben
        print("\n--- Statistiken ---")
        if stats:
            for k, v in stats.items():
                print(f"{k:20}: {v}")
        else:
            print("Keine Statistiken berechnet.")

        # Plot erzeugen
        img_base64 = plotly_combined_chart_and_equity(
            df,
            standard_signals,
            support,
            resistance,
            eq_curve,
            bh_curve,
            symbol
        )
        print(f"{symbol}: Plotly chart generated.")

if __name__ == "__main__":
    main()