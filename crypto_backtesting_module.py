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
CSV_PATH = "C:\\Users\\Edgar.000\\Documents\\____Trading strategies\\Crypto_trading1"
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

def load_crypto_data_yf(ticker: str, data_dir: str = "Crypto_trading1") -> pd.DataFrame:
    import os
    import pandas as pd
    import yfinance as yf

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

def load_and_update_daily_crypto(minute_df, symbol, daily_path):
    print(f"[{symbol}] 🔄 Aktualisiere Tagesdaten aus Minutendaten...")

    # Prüfe, ob Tagesdatei existiert
    if not os.path.exists(daily_path):
        print(f"[{symbol}] ⚠️ Tagesdatei nicht gefunden. Erstelle neue: {daily_path}")
        daily_df = pd.DataFrame()
    else:
        daily_df = pd.read_csv(daily_path, parse_dates=["date"])

    # Berechne neue Tagesdaten aus Minutendaten
    minute_df["date"] = pd.to_datetime(minute_df["datetime"]).dt.date
    grouped = minute_df.groupby("date")
    new_daily = pd.DataFrame({
        "date": grouped["datetime"].first().dt.date,
        "open": grouped["open"].first(),
        "high": grouped["high"].max(),
        "low": grouped["low"].min(),
        "close": grouped["close"].last(),
        "volume": grouped["volume"].sum()
    })

    # Kombiniere bestehende mit neuen Daten
    combined = pd.concat([daily_df, new_daily]).drop_duplicates("date", keep="last")
    combined = combined.sort_values("date").reset_index(drop=True)

    # Speichere aktualisierte Datei
    combined.to_csv(daily_path, index=False)
    return combined


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
    today_str = datetime.now().strftime("%Y-%m-%d")
    results = []

    for ticker, cfg in crypto_tickers.items():
        symbol = cfg["symbol"]
        csv_path = f"C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading1/{symbol}_cleaned.csv"

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

        # Heute ergänzen, falls nicht vorhanden
        if today_str not in df["Date"].dt.strftime("%Y-%m-%d").values:
            df1m = yf.download(symbol, interval="1m", period="1d", progress=False, auto_adjust=True)

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
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        print(f"[{ticker}] ➕ Tageskurs ergänzt: {new_row['Close']:.2f} EUR")
                    else:
                        print(f"[{ticker}] ⚠️ Minuten-Daten leer nach dropna")
                else:
                    missing = set(required_cols) - set(df1m.columns)
                    print(f"[{ticker}] ⚠️ Minuten-Daten unvollständig: {missing}")
            else:
                print(f"[{ticker}] ⚠️ Keine Minuten-Daten verfügbar")

        # ROI berechnen
        df = df.sort_values("Date")
        valid_close = df["Close"].dropna()
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


def update_daily_crypto_with_today():
    base_dir = "C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading1/"
    os.makedirs(base_dir, exist_ok=True)

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
            file_path = os.path.join(base_dir, f"{symbol}_cleaned.csv")
            df.to_csv(file_path, index=False)
            print(f"[{symbol}] ✅ Gespeichert: {file_path}")

        except Exception as e:
            print(f"[{symbol}] ❌ Fehler beim Abrufen: {e}")
    

# main.pydef main():
def main():
    print("🔄 Aktualisiere Tagesdaten aus Minutendaten...")
    for ticker, cfg in crypto_tickers.items():
        symbol = cfg["symbol"]
        try:
            minute_df = yf.download(symbol, period="5d", interval="1m")
            load_and_update_daily_crypto(f"data/daily_{symbol}.csv", minute_df)
        except Exception as e:
            print(f"[{symbol}] ⚠️ Fehler beim Aktualisieren der Tagesdaten: {e}")

    print("✅ Tagesdaten aktualisiert.")

    print("📥 Lade alle bereinigten Crypto-Daten...")
    data_dict = {}
    for ticker, cfg in crypto_tickers.items():
        symbol = cfg["symbol"]
        df = load_crypto_data_yf(symbol)
        if isinstance(df, pd.DataFrame) and not df.empty:
            data_dict[ticker] = df

    print(f"📊 Geladene Ticker: {list(data_dict.keys())}")

    print("🚀 Starte Backtests...")
    results = run_crypto_backtests()
    print("✅ Backtests abgeschlossen.")

    # Optional: Ergebnisse speichern
    # save_results_to_file(results)

if __name__ == "__main__":
    main()
