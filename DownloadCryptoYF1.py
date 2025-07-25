import os
import time
import pandas as pd
import yfinance as yf
import requests

# === Tickerlisten ===
update_tickers_yf = [
    "BTC-EUR", "ETH-EUR", "SOL-EUR", "ADA-EUR", "LINK-EUR", "XRP-EUR"
]
update_tickers_bitget = [
    "BTCUSDT", "ETHUSDT", "ADAUSDT","SOLUSDT", "XRPUSDT", "LINKUSDT"
]

def save_clean_csv(df, filename):
    # Falls der DataFrame einen MultiIndex bei den Spalten hat, diesen flach machen.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(1)
    
    # Den Index (Datum) in eine Spalte umwandeln.
    df = df.reset_index()

    # Falls "Adj Close" vorhanden, aber "Close" fehlt, umbenennen.
    if "Adj Close" in df.columns and "Close" not in df.columns:
        df.rename(columns={"Adj Close": "Close"}, inplace=True)

    # Erwartete Spalten: Wir wollen, dass nur diese in der CSV stehen.
    expected_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]
    missing = [col for col in expected_cols if col not in df.columns]
    if missing:
        print(f"Warnung: Erwartete Spalten fehlen: {missing}")
        print(f"Vorhandene Spalten: {list(df.columns)}")
    else:
        df = df[expected_cols]
    
    # In CSV speichern (ohne zusätzlichen Index)
    df.to_csv(filename, index=False)
    print(f"Header von {filename}:")
    with open(filename, "r", encoding="utf-8") as f:
        # Zeige beispielsweise die ersten 3 Zeilen an
        for _ in range(3):
            print(f.readline().strip())

def download_yf(ticker, period="5y", interval="1d", start=None, auto_adjust=False):
    # Setze auto_adjust auf False, um die Standardspalten zu erhalten.
    if start:
        df = yf.download(ticker, start=start, interval=interval, auto_adjust=auto_adjust)
    else:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=auto_adjust)
    return df

def download_bitget_perp(symbol, start=None, end=None):
    base_url = "https://api.bitget.com/api/mix/v1/market/candles"
    granularity = 86400  # 1 Tag in Sekunden als Zahl
    limit = 1000
    # Wir definieren ein Fenster von ca. 1 Jahr in Millisekunden
    window = 365 * 24 * 60 * 60 * 1000

    if end is None:
        end = int(time.time() * 1000)
    if start is None:
        # Abruf der Daten der letzten 5 Jahre
        start = end - 5 * 365 * 24 * 60 * 60 * 1000

    all_data = []
    current_start = start
    while current_start < end:
        current_end = min(current_start + window - 1, end)
        params = {
            "symbol": symbol,
            "granularity": granularity,
            "startTime": current_start,
            "endTime": current_end,
            "limit": limit,
            "productType": "umcbl"  # USDT-M Perpetual
        }
        resp = requests.get(base_url, params=params)
        if resp.status_code != 200:
            print(f"{symbol}: Fehler beim Bitget-Perp-Download ({resp.status_code}) with params:")
            print(params)
            break
        
        # Achte darauf, ob resp.json() ein Dictionary oder eine Liste ist.
        json_data = resp.json()
        if isinstance(json_data, dict):
            data = json_data.get("data", [])
        else:
            data = json_data

        if not data:
            print(f"{symbol}: Keine Daten im Intervall {current_start} bis {current_end}")
            current_start = current_end + 1
            continue
        all_data.extend(data)
        # Setze current_start auf den Zeitpunkt nach dem letzten abgefragten Candle
        last_ts = int(data[-1][0])
        if last_ts >= current_end:
            current_start = last_ts + 1
        else:
            current_start = current_end + 1
        time.sleep(1)
        
    if not all_data:
        return pd.DataFrame()
    # Bitget liefert Daten in folgender Reihenfolge:
    # [timestamp, open, high, low, close, volume, turnover]
    df = pd.DataFrame(all_data, columns=["Date", "Open", "High", "Low", "Close", "Volume", "Turnover"])
    df["Date"] = pd.to_datetime(df["Date"], unit="ms")
    df.set_index("Date", inplace=True)
    df = df.sort_index()
    # Wähle nur die benötigten Spalten
    df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    return df

def update_csv(ticker, source, filename):
    if source == "yf":
        df = download_yf(ticker, period="5y", interval="1d", auto_adjust=False)
    elif source == "bitget":
        # Für Bitget: Falls das gewünschte Produkt "umcbl" ist, muss das Symbol als "BTCUSDT_UMCBL" etc. vorliegen.
        adjusted_ticker = ticker if ticker.endswith("_UMCBL") else ticker + "_UMCBL"
        df = download_bitget_perp(adjusted_ticker)
    else:
        print(f"Unbekannte Datenquelle: {source}")
        return

    if df.empty:
        print(f"Keine Daten für {ticker} von {source}.")
    else:
        save_clean_csv(df, filename)

# --- Verarbeitung der Yahoo Finance-Ticker ---
for ticker in update_tickers_yf:
    filename = f"{ticker.lower().replace('-', '')}_yf.csv"
    try:
        update_csv(ticker, "yf", filename)
    except Exception as e:
        print(f"Fehler bei {ticker} von yf: {e}")
    time.sleep(10)  # Längere Pause zur Vermeidung von Rate Limit-Fehlern

# --- Verarbeitung der Bitget-Ticker ---
for ticker in update_tickers_bitget:
    filename = f"{ticker.lower()}_bitget.csv"
    try:
        update_csv(ticker, "bitget", filename)
    except Exception as e:
        print(f"Fehler bei {ticker} von bitget: {e}")
    time.sleep(2)
