import os
import sys
import datetime
import time
import logging
import builtins
print = builtins.print
from builtins import AttributeError
import pandas as pd
import pandas_market_calendars as mcal
# Handelskalender initialisieren (z.B. NYSE)
nyse = mcal.get_calendar("NYSE")
import numpy as np
from scipy.signal import argrelextrema
from scipy import stats
#from stats import stats
import mplfinance as mpf
from ib_insync import IB, Stock, LimitOrder, Crypto
import time
import logging
from ib_insync import IB
import datetime
from zoneinfo import ZoneInfo
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas_market_calendars as mcal  # Am Anfang des Skripts einfügen
from ib_insync import MarketOrder
import yfinance as yf
import threading
price_event = threading.Event()
shared_price = {"price": None, "bid": None, "ask": None}
import plotly.io as pio
pio.renderers.default = "browser"
# Globale Parameter
ORDER_ROUND_FACTOR = 1
COMMISSION_RATE = 0.0018  # 0,18% des Umsatzes
MIN_COMMISSION = 1.0      # Mindestprovision
ORDER_SIZE = 100          # Standard-Ordergröße
backtesting_begin = 0      # z.B. 0 für Start bei 0%
backtesting_end = 75       # z.B. 50 für Ende bei 50%
# Ticker-Konfiguration (ganz oben, außerhalb aller Funktionen!)
tickers = {
    "BTC":  {"symbol": "BTC",  "exchange": "PAXOS",    "long": True,  "short": False, "initialCapitalLong": 5000, "initialCapitalShort": 0,    "order_round_factor": 0.01},
    "ETH":  {"symbol": "ETH",  "exchange": "PAXOS",    "long": True,  "short": True,  "initialCapitalLong": 1200, "initialCapitalShort": 1200, "order_round_factor": 0.1},
    "SOL":  {"symbol": "SOL",  "exchange": "PAXOS",    "long": True,  "short": False, "initialCapitalLong": 1800, "initialCapitalShort": 0,    "order_round_factor": 0.1},
    "LINK": {"symbol": "LINK", "exchange": "PAXOS",    "long": True,  "short": False, "initialCapitalLong": 1800, "initialCapitalShort": 0,    "order_round_factor": 0.1},
    "LTC":  {"symbol": "LTC",  "exchange": "PAXOS",    "long": True,  "short": False, "initialCapitalLong": 1800, "initialCapitalShort": 0,    "order_round_factor": 0.1},
    "DOGE": {"symbol": "DOGE", "exchange": "ZEROHASH", "long": True,  "short": False, "initialCapitalLong": 1800, "initialCapitalShort": 0,    "order_round_factor": 0.1},
    "XRP":  {"symbol": "XRP",  "exchange": "ZEROHASH", "long": True,  "short": False, "initialCapitalLong": 1800, "initialCapitalShort": 0,    "order_round_factor": 0.1}

}

# ...jetzt erst die Funktionen wie both_backtesting_multi, trading_multi, etc...

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# =============================================================================
# 1. Historische Daten laden/aktualisieren (mindestens 365 Tage)
# =============================================================================
def update_historical_data_csv(ib, contract, csv_filename):
    """
    Lädt und aktualisiert historische Tagesdaten für einen IB-Kontrakt.
    Gibt ein DataFrame zurück oder None bei Fehler (z.B. fehlende Marktdaten-Berechtigung).
    """
    desired_end = pd.Timestamp.today().normalize()
    desired_start = desired_end - pd.Timedelta(days=365)

    if os.path.exists(csv_filename):
        df = pd.read_csv(csv_filename, parse_dates=['date'], index_col='date')
        df.sort_index(inplace=True)
        current_start = df.index.min()
        current_end = df.index.max()
        # ... älteste Daten nachladen ...
        if current_end < desired_end:
            diff_days = (desired_end - current_end).days
            if diff_days > 0:
                bars_new = ib.reqHistoricalData(
                    contract,
                    endDateTime="",
                    durationStr=f"{diff_days} D",
                    barSizeSetting="1 day", whatToShow="AGGTRADES", useRTH=True
                )
                new_df = pd.DataFrame(bars_new)
                if new_df.empty or 'date' not in new_df.columns:
                    logging.error(f"Keine neuen historischen Daten für {contract.symbol} erhalten. Prüfe Marktdaten-Abo!")
                    return df
                new_df['date'] = pd.to_datetime(new_df['date'])
                new_df.set_index('date', inplace=True)
                df = pd.concat([df, new_df])
                df = df[~df.index.duplicated(keep='last')]
                df.sort_index(inplace=True)
        # ...speichern...
        df.to_csv(csv_filename, index_label="date")
        return df
    else:
        logging.info(f"CSV-Datei {csv_filename} existiert nicht. Lade initial 365 Tage historischer Daten …")
        whatToShow = "AGGTRADES"
        bars = ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr="365 D",
            barSizeSetting="1 day",
            whatToShow=whatToShow,
            useRTH=True
        )

        df = pd.DataFrame(bars)
        if df.empty or 'date' not in df.columns:
            logging.error(f"Keine historischen Daten für {contract.symbol} erhalten. Prüfe Marktdaten-Abo!")
            return None
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df.to_csv(csv_filename, index_label="date")
        logging.info("CSV-Datei erstellt.")
        return df
    
# =============================================================================
# 2. Support/Resistance und Trend
# =============================================================================
def calculate_support_resistance(df, past_window, trade_window):
    """
    Berechnet Support/Resistance basierend auf Close-Preisen.
    Ein Fenster von (past_window+trade_window) wird genutzt; zusätzlich werden das absolute Minimum und Maximum hinzugefügt.
    """
    total_window = int(past_window + trade_window)
    prices = df["Close"].values
    local_min_idx = argrelextrema(prices, np.less, order=total_window)[0]
    support = pd.Series(prices[local_min_idx], index=df.index[local_min_idx])
    local_max_idx = argrelextrema(prices, np.greater, order=total_window)[0]
    resistance = pd.Series(prices[local_max_idx], index=df.index[local_max_idx])
    absolute_low_date = df["Close"].idxmin()
    absolute_low = df["Close"].min()
    if absolute_low_date not in support.index:
        support = pd.concat([support, pd.Series([absolute_low], index=[absolute_low_date])])
    absolute_high_date = df["Close"].idxmax()
    absolute_high = df["Close"].max()
    if absolute_high_date not in resistance.index:
        resistance = pd.concat([resistance, pd.Series([absolute_high], index=[absolute_high_date])])
    support.sort_index(inplace=True)
    resistance.sort_index(inplace=True)
    return support, resistance
  
def compute_trend(df, window=20):
    """Berechnet den einfachen gleitenden Durchschnitt (SMA)."""
    return df["Close"].rolling(window=window).mean()

# =============================================================================
# 3. Helper: Berechnung der Ordergröße (Shares)
# =============================================================================
def calculate_shares(capital, price, round_factor):
    """
    Berechnet die Anzahl der Shares als (Kapital / Preis)
    und rundet das Ergebnis auf das nächstgelegene Vielfache des round_factor.
    """
    raw = capital / price
    shares = round(raw / round_factor) * round_factor
    return shares

# =============================================================================
# 4. Standard-Signale zuordnen (Long und Short)
# =============================================================================
def assign_long_signals(support, resistance, data, trade_window, interval):
    """
    Ermittelt Standard-Long-Signale.
    Gibt ein DataFrame mit Spalten "Long" und "Long Date" zurück.
    """
    data.sort_index(inplace=True)
    sup_df = pd.DataFrame({'Date': support.index, 'Level': support.values, 'Type': 'support'})
    res_df = pd.DataFrame({'Date': resistance.index, 'Level': resistance.values, 'Type': 'resistance'})
    df = pd.concat([sup_df, res_df]).sort_values(by='Date').reset_index(drop=True)
    df['Long'] = None
    df['Long Date'] = pd.NaT
    long_active = False
    for i, row in df.iterrows():
        base_date = row['Date']
        interval_clean = interval.replace(" ", "").lower()
        if interval_clean in ["1d", "1day"]:
            trade_date = base_date + pd.Timedelta(days=trade_window)
        elif interval_clean.endswith("min"):
            minutes = int(interval_clean.replace("min", ""))
            trade_date = base_date + pd.Timedelta(minutes=trade_window * minutes)
        elif interval_clean in ["1h", "1hour"]:
            trade_date = base_date + pd.Timedelta(hours=trade_window)
        else:
            raise ValueError(f"Unsupported interval: {interval}")
        if trade_date not in data.index:
            idx = data.index.searchsorted(trade_date)
            trade_date = data.index[idx] if idx < len(data.index) else pd.NaT
        # ...restlicher Code...
# ...existing code...
        if row['Type'] == 'support' and not long_active:
            df.at[i, 'Long'] = 'buy'
            # Cast auf tz-naive:
            try:
                trade_date = trade_date.tz_localize(None)
            except AttributeError:
                pass
            df.at[i, 'Long Date'] = trade_date
            long_active = True
        elif row['Type'] == 'resistance' and long_active:
            df.at[i, 'Long'] = 'sell'
            if hasattr(trade_date, 'tz_localize'):
                trade_date = trade_date.tz_localize(None)
            df.at[i, 'Long Date'] = trade_date
            long_active = False

    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    df['Long Date'] = pd.to_datetime(df['Long Date'], errors='coerce').dt.tz_localize(None)
    return df

def assign_short_signals(support, resistance, data, trade_window, interval):
    data.sort_index(inplace=True)
    sup_df = pd.DataFrame({'Date': support.index, 'Level': support.values, 'Type': 'support'})
    res_df = pd.DataFrame({'Date': resistance.index, 'Level': resistance.values, 'Type': 'resistance'})
    df = pd.concat([sup_df, res_df]).sort_values(by='Date').reset_index(drop=True)
    df['Short'] = None
    df['Short Date'] = pd.NaT
    short_active = False
    for i, row in df.iterrows():
        base_date = row['Date']
        interval_clean = interval.replace(" ", "").lower()
        if interval_clean in ["1d", "1day"]:
            trade_date = base_date + pd.Timedelta(days=trade_window)
        elif interval_clean.endswith("min"):
            minutes = int(interval_clean.replace("min", ""))
            trade_date = base_date + pd.Timedelta(minutes=trade_window * minutes)
        elif interval_clean in ["1h", "1hour"]:
            trade_date = base_date + pd.Timedelta(hours=trade_window)
        else:
            raise ValueError(f"Unsupported interval: {interval}")
        if trade_date not in data.index:
            idx = data.index.searchsorted(trade_date)
            trade_date = data.index[idx] if idx < len(data.index) else pd.NaT
        # ...restlicher Code...
        if row['Type'] == 'resistance' and not short_active:
            df.at[i, 'Short'] = 'short'
            if hasattr(trade_date, 'tz_localize'):
                trade_date = trade_date.tz_localize(None)
            df.at[i, 'Short Date'] = trade_date
            short_active = True
        elif row['Type'] == 'support' and short_active:
            df.at[i, 'Short'] = 'cover'
            if hasattr(trade_date, 'tz_localize'):
                trade_date = trade_date.tz_localize(None)
            df.at[i, 'Short Date'] = trade_date
            short_active = False
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    df['Short Date'] = pd.to_datetime(df['Short Date'], errors='coerce').dt.tz_localize(None)
    return df

def is_trading_day(date):
    """
    Prüft, ob das gegebene Datum ein US-Handelstag ist (NYSE).
    date: pd.Timestamp (tz-naiv, Datumsteil)
    """
    schedule = nyse.schedule(start_date=date, end_date=date)
    return not schedule.empty

def get_next_trading_day(current_date, market_df):
    """Findet den nächsten verfügbaren Handelstag.
       Falls current_date NaT ist oder über den maximalen Handelstag hinausgeht, wird NaT zurückgegeben.
    """
    if pd.isna(current_date):
        return pd.NaT
    max_date = market_df.index.max()
    if current_date > max_date:
        return pd.NaT
    while current_date not in market_df.index:
        current_date += pd.Timedelta(days=1)
        if current_date > max_date:
            return pd.NaT
    return current_date


def assign_long_signals_extended(support, resistance, data, trade_window, interval):
    df = assign_long_signals(support, resistance, data, trade_window, interval).copy()
    df["Long Action"] = df["Long"]
    df.rename(columns={"Date": "Date high/low", "Level": "Level high/low", "Type": "Supp/Resist"}, inplace=True)
    df["Long Date detected"] = df["Date high/low"] + pd.Timedelta(days=trade_window)
    # Hier: Nur wenn der Wert vorhanden ist, wird get_next_trading_day aufgerufen
    df["Long Date detected"] = df["Long Date detected"].apply(
        lambda dt: get_next_trading_day(dt, data) if pd.notna(dt) else pd.NaT
    )
    df["Level Close"] = np.nan
    df["Long Trade Day"] = df["Long Date detected"].apply(
        lambda dt: dt.replace(hour=15, minute=50, second=0, microsecond=0) if pd.notna(dt) else pd.NaT
    )
    df["Level trade"] = np.nan
    df = df[["Date high/low", "Level high/low", "Supp/Resist", "Long Action",
             "Long Date detected", "Level Close", "Long Trade Day", "Level trade"]]
    return df


def assign_short_signals_extended(support, resistance, data, trade_window, interval):
    df = assign_short_signals(support, resistance, data, trade_window, interval).copy()
    df["Short Action"] = df["Short"]
    df.rename(columns={"Date": "Date high/low", "Level": "Level high/low", "Type": "Supp/Resist"}, inplace=True)
    df["Short Date detected"] = df["Date high/low"] + pd.Timedelta(days=trade_window)
    df["Short Date detected"] = df["Short Date detected"].apply(lambda dt: get_next_trading_day(dt, data))
    df["Level Close"] = np.nan
    df["Short Trade Day"] = df["Short Date detected"].apply(lambda dt: dt.replace(hour=15, minute=50, second=0, microsecond=0) if pd.notna(dt) else pd.NaT)
    df["Level trade"] = np.nan
    df = df[["Date high/low", "Level high/low", "Supp/Resist", "Short Action",
             "Short Date detected", "Level Close", "Short Trade Day", "Level trade"]]
    return df

def update_level_close_long(extended_df, market_df):
    closes = []
    for _, row in extended_df.iterrows():
        if pd.notna(row["Long Date detected"]):
            trade_day = row["Long Date detected"].normalize()
        else:
            trade_day = pd.NaT
        if pd.isna(trade_day):
            closes.append(np.nan)
        elif trade_day in market_df.index:
            closes.append(market_df.loc[trade_day, "Close"])
        else:
            idx = market_df.index.searchsorted(trade_day)
            closes.append(market_df.iloc[idx]["Close"] if idx < len(market_df.index) else np.nan)
    extended_df["Level Close"] = closes
    return extended_df

def update_level_close_short(extended_df, market_df):
    closes = []
    for _, row in extended_df.iterrows():
        if pd.notna(row["Short Date detected"]):
            trade_day = row["Short Date detected"].normalize()
        else:
            trade_day = pd.NaT
        if pd.isna(trade_day):
            closes.append(np.nan)
        elif trade_day in market_df.index:
            closes.append(market_df.loc[trade_day, "Close"])
        else:
            idx = market_df.index.searchsorted(trade_day)
            closes.append(market_df.iloc[idx]["Close"] if idx < len(market_df.index) else np.nan)
    extended_df["Level Close"] = closes
    return extended_df

# =============================================================================
# 7. Tradesimulation (Long und Short) mit dynamischer Ordergröße
# =============================================================================

def simulate_trades_compound_extended(extended_df, market_df, starting_capital=10000,
                                        commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION,
                                        round_factor=ORDER_ROUND_FACTOR,
                                        artificial_close_price=None, artificial_close_date=None):
    """
    Simuliert Long‑Trades basierend auf den Extended-Long-Signalen.
    Ergänzt offene Trades mit künstlichem Close (z.B. 15:50).
    """
    extended_df = extended_df.sort_values(by="Long Date detected")
    capital = starting_capital
    position_active = False
    trades = []
    buy_price = buy_date = prev_cap = None
    for _, row in extended_df.iterrows():
        action = row.get('Long Action')
        exec_date = row.get('Long Date detected')
        if pd.isna(exec_date):
            continue
        if exec_date in market_df.index:
            price = float(market_df.loc[exec_date, "Close"])
        else:
            idx = market_df.index.searchsorted(exec_date)
            price = float(market_df.iloc[idx]["Close"]) if idx < len(market_df.index) else None
        if price is None:
            continue
        if action == 'buy' and not position_active:
            shares = calculate_shares(capital, price, round_factor)
            if shares < 1e-6:
                continue
            buy_price = price
            buy_date = exec_date
            position_active = True
            prev_cap = capital
        elif action == 'sell' and position_active:
            sell_price = price
            sell_date = exec_date
            profit = (sell_price - buy_price) * shares
            turnover = shares * (buy_price + sell_price)
            fee = max(min_commission, turnover * commission_rate)
            new_cap = prev_cap + profit - fee
            trades.append({
                'buy_date': buy_date,
                'sell_date': sell_date,
                'shares': shares,
                'buy_price': round(buy_price, 2),
                'sell_price': round(sell_price, 2),
                'fee': round(fee, 2),
                'pnl': round(new_cap - prev_cap, 3)
            })
            capital = new_cap
            position_active = False
    # Falls noch Position offen, mit künstlichem Close abschließen
    if position_active and artificial_close_price is not None and artificial_close_date is not None:
        sell_price = artificial_close_price
        sell_date = artificial_close_date
        profit = (sell_price - buy_price) * shares
        turnover = shares * (buy_price + sell_price)
        fee = max(min_commission, turnover * commission_rate)
        new_cap = prev_cap + profit - fee
        trades.append({
            'buy_date': buy_date,
            'sell_date': sell_date,
            'shares': shares,
            'buy_price': round(buy_price, 2),
            'sell_price': round(sell_price, 2),
            'fee': round(fee, 2),
            'pnl': round(new_cap - prev_cap, 3)
        })
        capital = new_cap
    return capital, trades
def simulate_short_trades_compound_extended(extended_df, market_df, starting_capital=10000,
                                             commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION,
                                             round_factor=ORDER_ROUND_FACTOR,
                                             artificial_close_price=None, artificial_close_date=None):
    """
    Simuliert Short‑Trades basierend auf den Extended-Short-Signalen.
    Ergänzt offene Trades mit künstlichem Close (z.B. 15:50).
    """
    extended_df = extended_df.sort_values(by="Short Date detected")
    capital = starting_capital
    position_active = False
    trades = []
    short_price = short_date = prev_cap = None
    for _, row in extended_df.iterrows():
        action = row.get('Short Action')
        exec_date = row.get('Short Date detected')
        if pd.isna(exec_date):
            continue
        if exec_date in market_df.index:
            price = float(market_df.loc[exec_date, "Close"])
        else:
            idx = market_df.index.searchsorted(exec_date)
            price = float(market_df.iloc[idx]["Close"]) if idx < len(market_df.index) else None
        if price is None:
            continue
        if action == 'short' and not position_active:
            shares = calculate_shares(capital, price, round_factor)
            if shares < 1e-6:
                continue
            short_price = price
            short_date = exec_date
            position_active = True
            prev_cap = capital
        elif action == 'cover' and position_active:
            cover_price = price
            cover_date = exec_date
            profit = (short_price - cover_price) * shares
            turnover = shares * (short_price + cover_price)
            fee = max(min_commission, turnover * commission_rate)
            new_cap = prev_cap + profit - fee
            trades.append({
                'short_date': short_date,
                'cover_date': cover_date,
                'shares': shares,
                'short_price': round(short_price, 2),
                'cover_price': round(cover_price, 2),
                'fee': round(fee, 2),
                'pnl': round(new_cap - prev_cap, 3)
            })
            capital = new_cap
            position_active = False
    # Falls noch Position offen, mit künstlichem Close abschließen
    if position_active and artificial_close_price is not None and artificial_close_date is not None:
        cover_price = artificial_close_price
        cover_date = artificial_close_date
        profit = (short_price - cover_price) * shares
        turnover = shares * (short_price + cover_price)
        fee = max(min_commission, turnover * commission_rate)
        new_cap = prev_cap + profit - fee
        trades.append({
            'short_date': short_date,
            'cover_date': cover_date,
            'shares': shares,
            'short_price': round(short_price, 2),
            'cover_price': round(cover_price, 2),
            'fee': round(fee, 2),
            'pnl': round(new_cap - prev_cap, 3)
        })
        capital = new_cap
    return capital, trades


def simulate_trades_compound(signals_df, market_df, starting_capital=10000,
                             commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION,
                             round_factor=ORDER_ROUND_FACTOR):
    """
    Simuliert Long‑Trades mit dynamischer Ordergröße.
    
    Für jede Zeile des Signal-DataFrames:
      - Es wird der Preis zum Ausführungstermin ermittelt (als float).
      - Es werden Shares berechnet (Kapital/Preis) und auf den nächstgelegenen Wert gerundet.
      - Falls dabei 0 (oder ein vernachlässigbarer Wert) herauskommt, wird der Trade übersprungen.
      - Beim 'buy' wird eine Position eröffnet und beim 'sell' wieder geschlossen,
        wobei Gewinn, Turnover, Provision (fee) und pnl berechnet werden.
      
    Gibt das finale Kapital sowie eine Liste der Trades zurück.
    """
    capital = starting_capital
    position_active = False
    trades = []
    for _, row in signals_df.iterrows():
        signal = row.get('Long')
        exec_date = row.get('Long Date')
        if pd.isna(exec_date):
            continue
        # Preis ermitteln und als float interpretieren:
        if exec_date in market_df.index:
            price = float(market_df.loc[exec_date, "Close"])
        else:
            idx = market_df.index.searchsorted(exec_date)
            price = float(market_df.iloc[idx]["Close"]) if idx < len(market_df.index) else None
        if price is None:
            continue
        if signal == 'buy' and not position_active:
            shares = calculate_shares(capital, price, round_factor)
            # Falls shares (oder ein kleiner Schwellenwert) nicht signifikant > 0 sind, überspringen.
            if shares < 1e-6:
                continue
            buy_price = price
            buy_date = exec_date
            position_active = True
            prev_cap = capital
        elif signal == 'sell' and position_active:
            sell_price = price
            sell_date = exec_date
            profit = (sell_price - buy_price) * shares
            turnover = shares * (buy_price + sell_price)
            fee = max(min_commission, turnover * commission_rate)
            new_cap = prev_cap + profit - fee
            trades.append({
                'buy_date': buy_date,
                'sell_date': sell_date,
                'shares': shares,
                'buy_price': round(buy_price, 2),
                'sell_price': round(sell_price, 2),
                'fee': round(fee, 2),
                'pnl': round(new_cap - prev_cap, 3)
            })
            capital = new_cap
            position_active = False
    return capital, trades


def simulate_short_trades_compound(signals_df, market_df, starting_capital=10000,
                                  commission_rate=COMMISSION_RATE, min_commission=MIN_COMMISSION,
                                  round_factor=ORDER_ROUND_FACTOR):
    """
    Simuliert Short‑Trades mit dynamischer Ordergröße.
    
    Für jede Zeile des Signal-DataFrames:
      - Ermittelt den Preis zum Ausführungstermin (als float).
      - Berechnet die zu handelnden Shares (Kapital / Preis) anhand eines Rundungsfaktors.  
      - Falls das Ergebnis vernachlässigbar (also 0) ist, wird der Trade übersprungen.
      - Beim 'short' wird die Short-Position eröffnet und beim 'cover' geschlossen.
      - Es werden Gewinn, Turnover, Provision (fee) und pnl berechnet.
      
    Gibt das finale Kapital und eine Liste der durchgeführten Short-Trades zurück.
    """
    capital = starting_capital
    position_active = False
    trades = []
    for _, row in signals_df.iterrows():
        signal = row.get('Short')
        exec_date = row.get('Short Date')
        if pd.isna(exec_date):
            continue
        # Preis ermitteln als float:
        if exec_date in market_df.index:
            price = float(market_df.loc[exec_date, "Close"])
        else:
            idx = market_df.index.searchsorted(exec_date)
            price = float(market_df.iloc[idx]["Close"]) if idx < len(market_df.index) else None
        if price is None:
            continue
        if signal == 'short' and not position_active:
            shares = calculate_shares(capital, price, round_factor)
            if shares < 1e-6:
                continue  # Überspringe Trade, falls keine signifikante Anzahl an Shares berechnet wurde
            short_price = price
            short_date = exec_date
            position_active = True
            prev_cap = capital
        elif signal == 'cover' and position_active:
            cover_price = price
            cover_date = exec_date
            profit = (short_price - cover_price) * shares
            turnover = shares * (short_price + cover_price)
            fee = max(min_commission, turnover * commission_rate)
            new_cap = prev_cap + profit - fee
            trades.append({
                'short_date': short_date,
                'cover_date': cover_date,
                'shares': shares,
                'short_price': round(short_price, 2),
                'cover_price': round(cover_price, 2),
                'fee': round(fee, 2),
                'pnl': round(new_cap - prev_cap, 3)
            })
            capital = new_cap
            position_active = False
    return capital, trades






# =============================================================================
# 8. Plotten des Candlestick-Charts
# =============================================================================
def plot_chart(csv_filename, past_window=5, trade_window=1, trend_window=20):
    df = pd.read_csv(csv_filename, parse_dates=['date'], index_col='date')
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'}, inplace=True)
    if 'Volume' not in df.columns:
        df['Volume'] = 0
    supp, res = calculate_support_resistance(df, past_window, trade_window)
    trend = compute_trend(df, window=trend_window)
    supp = supp.reindex(df.index)
    res = res.reindex(df.index)
    ap_support = mpf.make_addplot(supp, type='scatter', markersize=25, marker='o', color='green')
    ap_resistance = mpf.make_addplot(res, type='scatter', markersize=25, marker='o', color='red')
    ap_trend = mpf.make_addplot(trend, type='line', color='blue')
    add_plots = [ap_support, ap_resistance, ap_trend]
    mpf.plot(df, type='candle', style='charles', volume=True, addplot=add_plots,
             title='Candlestick Chart mit Support/Resistance und Trend')

# =============================================================================
# 10. Multi-Ticker Modi
# =============================================================================

def plot_optimal_trades_multi(ticker, ib):
    config = tickers[ticker]
    csv_filename = f"{ticker}_data.csv"
    contract = Crypto(config["symbol"], config["exchange"], "USD")

    # Lese oder lade Daten
    if os.path.exists(csv_filename):
        df = pd.read_csv(csv_filename, parse_dates=["date"], index_col="date")
        df.sort_index(inplace=True)
        df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"}, inplace=True)
    else:
        df = update_historical_data_csv(ib, contract, csv_filename)
        if df is None:
            print(f"{ticker}: Keine historischen Daten verfügbar. Überspringe Ticker.")
            return  # <-- statt continue
        df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"}, inplace=True)
    # ...restlicher Code...
    
    if "Volume" not in df.columns:
        df["Volume"] = 0

    # ----------------------------
    # Backtesting Long-Trades
    # ----------------------------
    long_results = []
    for p in range(3, 10):
        for tw in range(1, 6):
            supp_temp, res_temp = calculate_support_resistance(df, p, tw)
            sig = assign_long_signals(supp_temp, res_temp, df, tw, "1d")
            cap, _ = simulate_trades_compound(
                sig, df,
                starting_capital=config["initialCapitalLong"],
                commission_rate=COMMISSION_RATE,
                min_commission=MIN_COMMISSION,
                round_factor=config.get("order_round_factor", ORDER_ROUND_FACTOR)
            )
            long_results.append({"past_window": p, "trade_window": tw, "final_cap": cap})
    long_df = pd.DataFrame(long_results)
    best_long = long_df.loc[long_df["final_cap"].idxmax()]
    best_p_long = int(best_long["past_window"])
    best_tw_long = int(best_long["trade_window"])
    best_sup_long, best_res_long = calculate_support_resistance(df, best_p_long, best_tw_long)
    standard_long = assign_long_signals(best_sup_long, best_res_long, df, best_tw_long, "1d")
    
    # Extended Long-Signale nutzen und aktualisieren
    extended_long = assign_long_signals_extended(best_sup_long, best_res_long, df, best_tw_long, "1d")
    extended_long = update_level_close_long(extended_long, df)
    round_factor_long = config.get("order_round_factor", ORDER_ROUND_FACTOR)
    long_cap, long_trades = simulate_trades_compound_extended(
        extended_long, df,
        starting_capital=config["initialCapitalLong"],
        commission_rate=COMMISSION_RATE,
        min_commission=MIN_COMMISSION,
        round_factor=round_factor_long
    )
    
    print(f"\nBeste Parameter (Long) für {config['symbol']}: past_window={best_p_long}, trade_window={best_tw_long}, Final Capital (Long)={long_cap:.2f}")
    
    # ----------------------------
    # Backtesting Short-Trades
    # ----------------------------
    short_results = []
    for p in range(3, 10):
        for tw in range(1, 4):
            supp_temp, res_temp = calculate_support_resistance(df, p, tw)
            sig = assign_short_signals(supp_temp, res_temp, df, tw, "1d")
            cap, _ = simulate_short_trades_compound(
                sig, df,
                starting_capital=config["initialCapitalShort"],
                commission_rate=COMMISSION_RATE,
                min_commission=MIN_COMMISSION,
                round_factor=config.get("order_round_factor", ORDER_ROUND_FACTOR)
            )
            short_results.append({"past_window": p, "trade_window": tw, "final_cap": cap})
    short_df = pd.DataFrame(short_results)
    best_short = short_df.loc[short_df["final_cap"].idxmax()]
    best_p_short = int(best_short["past_window"])
    best_tw_short = int(best_short["trade_window"])
    best_sup_short, best_res_short = calculate_support_resistance(df, best_p_short, best_tw_short)
    standard_short = assign_short_signals(best_sup_short, best_res_short, df, best_tw_short, "1d")
    
    # Extended Short-Signale nutzen und aktualisieren
    extended_short = assign_short_signals_extended(best_sup_short, best_res_short, df, best_tw_short, "1d")
    extended_short = update_level_close_short(extended_short, df)
    round_factor_short = config.get("order_round_factor", ORDER_ROUND_FACTOR)
    short_cap, short_trades = simulate_short_trades_compound_extended(
        extended_short, df,
        starting_capital=config["initialCapitalShort"],
        commission_rate=COMMISSION_RATE,
        min_commission=MIN_COMMISSION,
        round_factor=round_factor_short
    )
    
    print(f"Beste Parameter (Short) für {config['symbol']}: past_window={best_p_short}, trade_window={best_tw_short}, Final Capital (Short)={short_cap:.2f}")
    
    # ----------------------------
    # Zusätzliche Marker: 4 Arten (Buy, Sell, Short, Cover) mit vertikalen Offsets
    # ----------------------------
    # Definiere einen generellen Offset aufgrund der Preisspanne:
    offset = 0.02 * (df["Close"].max() - df["Close"].min())
    # Wir definieren separate Offsets für die Marker:
    buy_offset = 2*offset      # Buy-Marker sollen nach oben verschoben werden
    sell_offset = -2*offset    # Sell-Marker sollen nach unten verschoben werden
    short_offset = -offset   # Short-Marker sollen nach unten verschoben werden
    cover_offset = offset    # Cover-Marker sollen nach oben verschoben werden

    # Erstelle separate leere Serien für die Marker
    buy_marker = pd.Series(np.nan, index=df.index)
    sell_marker = pd.Series(np.nan, index=df.index)
    short_marker = pd.Series(np.nan, index=df.index)
    cover_marker = pd.Series(np.nan, index=df.index)
    
    # Für Long-Trades: Buy und Sell
    for _, row in standard_long.iterrows():
        if row["Long"] == "buy" and pd.notna(row["Long Date"]):
            buy_marker.loc[row["Long Date"]] = df.loc[row["Long Date"], "Close"] + buy_offset
        elif row["Long"] == "sell" and pd.notna(row["Long Date"]):
            sell_marker.loc[row["Long Date"]] = df.loc[row["Long Date"], "Close"] + sell_offset
    
    # Für Short-Trades: Short und Cover
    for _, row in standard_short.iterrows():
        if row.get("Short") == "short" and pd.notna(row["Short Date"]):
            short_marker.loc[row["Short Date"]] = df.loc[row["Short Date"], "Close"] + short_offset
        elif row.get("Short") == "cover" and pd.notna(row["Short Date"]):
            cover_marker.loc[row["Short Date"]] = df.loc[row["Short Date"], "Close"] + cover_offset
    
    # Definiere Add-Plots für die 4 Trade-Marker
    ap_buy = mpf.make_addplot(buy_marker, type="scatter", markersize=25, marker="^", color="red")
    ap_sell = mpf.make_addplot(sell_marker, type="scatter", markersize=25, marker="v", color="red")
    ap_short = mpf.make_addplot(short_marker, type="scatter", markersize=25, marker="v", color="blue")
    ap_cover = mpf.make_addplot(cover_marker, type="scatter", markersize=25, marker="^", color="blue")
    
    # Zusätzliche Marker: Support/Resistance und Trend
    supp, res = calculate_support_resistance(df, 5, 1)
    ap_support = mpf.make_addplot(supp.reindex(df.index), type="scatter", markersize=25, marker="o", color="green")
    ap_resistance = mpf.make_addplot(res.reindex(df.index), type="scatter", markersize=25, marker="o", color="red")
    ap_trend = mpf.make_addplot(compute_trend(df, 20), type="line", color="blue")
    
    # Alle Add-Plots zusammenführen
    add_plots = [ap_buy, ap_sell, ap_short, ap_cover, ap_support, ap_resistance, ap_trend]
    
    # Titel des Plots
    title_str = (f"{config['symbol']} Optimal Long: past_window={best_p_long}, trade_window={best_tw_long} "
                 f"(Cap={long_cap:.2f})\nOptimal Short: past_window={best_p_short}, trade_window={best_tw_short} "
                 f"(Cap={short_cap:.2f})")
    
    mpf.plot(df, type="candle", style="charles", volume=True, addplot=add_plots, title=title_str)
    
    # Konsolenausgabe
    print(f"\nTicker: {config['symbol']}")
    print("Matched Long Trades:")
    print(pd.DataFrame(long_trades).to_string(index=False))
    # Statistik-Printout einfügen:
    if isinstance(long_trades, pd.DataFrame):
        stats(long_trades.to_dict("records"), "Long")
    else:
        stats(long_trades, "Long")
    print(stats(long_trades, "Long Trades"))
    print("Matched Short Trades:")
    print(pd.DataFrame(short_trades).to_string(index=False))
  # Statistik-Printout einfügen:
    if isinstance(short_trades, pd.DataFrame):
        stats(short_trades.to_dict("records"), "Short")
    else:
        stats(short_trades, "Short")
    print(stats(short_trades, "Short Trades"))#.to_string())
    print("Extended Long Signals:")
    print(extended_long.to_string(index=False))
    print("Extended Short Signals:")
    print(extended_short.to_string(index=False))

# ...existing code...

def both_backtesting_multi(ib):
    for ticker, config in tickers.items():
        print(f"\n=================== Backtesting für {ticker} ===================")
        csv_filename = f"{ticker}_data.csv"
        contract = Crypto(config["symbol"], config["exchange"], "USD")
        if os.path.exists(csv_filename):
            df = pd.read_csv(csv_filename, parse_dates=["date"], index_col="date")
            df.sort_index(inplace=True)
            df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"}, inplace=True)
        else:
            df = update_historical_data_csv(ib, contract, csv_filename)
            if df is None:
                print(f"{ticker}: Keine historischen Daten verfügbar. Überspringe Ticker.")
                continue
            df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"}, inplace=True)

        today = pd.Timestamp.now(tz=ZoneInfo("America/New_York")).normalize().tz_localize(None)
        if today not in df.index:
            print(f"{ticker}: Tagesabschluss für {today.date()} fehlt, hole Realtime-Kurs ...")
            last_price, bid, ask = get_realtime_price(ticker, contract, ib)
            prev_close = df["Close"].iloc[-1]
            if (
                last_price is not None and last_price > 0
                and 0.5 * prev_close < last_price < 2 * prev_close
            ):
                new_row = pd.DataFrame({
                    "Open": last_price,
                    "High": last_price,
                    "Low": last_price,
                    "Close": last_price,
                    "Volume": 0
                }, index=[today])
                df = pd.concat([df, new_row])
                df.sort_index(inplace=True)
                df.to_csv(csv_filename, index_label="date")
                print(f"{ticker}: Realtime-Kurs als neuen Tagesabschluss für {today.date()} hinzugefügt.")
            else:
                print(f"{ticker}: Kein plausibler Realtime-Kurs ({last_price}) für {today.date()} (kein Tagesabschluss ergänzt).")
        last_day = df.index[-1].date()
        minute_df = get_minute_data_for_date(ib, contract, last_day)
        if minute_df is not None and not minute_df.empty:
            minute_filename = f"{ticker}_{last_day}_minute.csv"
            minute_df.to_csv(minute_filename)
            print(f"Minutendaten für {ticker} am {last_day} gespeichert: {minute_filename}")
        else:
            print(f"Keine Minutendaten für {ticker} am {last_day} erhalten.")

        artificial_close_date = df.index[-1]
        artificial_close_price = df.loc[artificial_close_date, "Close"]

        # ----------------------------
        # Backtesting Long-Trades
        # ----------------------------
        if config.get("long", False):
            best_p_long, best_tw_long = berechne_best_p_tw_long(df, config, backtesting_begin, backtesting_end)
            best_sup_long, best_res_long = calculate_support_resistance(df, best_p_long, best_tw_long)
            standard_long = assign_long_signals(best_sup_long, best_res_long, df, best_tw_long, "1d")
            extended_long = assign_long_signals_extended(best_sup_long, best_res_long, df, best_tw_long, "1d")
            extended_long = update_level_close_long(extended_long, df)
            round_factor_long = config.get("order_round_factor", ORDER_ROUND_FACTOR)
            long_cap, long_trades = simulate_trades_compound_extended(
                extended_long, df,
                starting_capital=config["initialCapitalLong"],
                commission_rate=COMMISSION_RATE,
                min_commission=MIN_COMMISSION,
                round_factor=round_factor_long,
                artificial_close_price=artificial_close_price,
                artificial_close_date=artificial_close_date
            )
            print(f"\nBeste Parameter (Long) für {ticker}: past_window={best_p_long}, trade_window={best_tw_long}, Final Capital (Long)={long_cap:.2f}")
        else:
            extended_long = pd.DataFrame()
            long_trades = []
            long_cap = config["initialCapitalLong"]
            standard_long = pd.DataFrame()
            print(f"\nLong-Trades für {ticker} deaktiviert. (long = False)")

        # ----------------------------
        # Backtesting Short-Trades
        # ----------------------------
        if config.get("short", False):
            best_p_short, best_tw_short = berechne_best_p_tw_short(df, config, backtesting_begin, backtesting_end)
            best_sup_short, best_res_short = calculate_support_resistance(df, best_p_short, best_tw_short)
            standard_short = assign_short_signals(best_sup_short, best_res_short, df, best_tw_short, "1d")
            extended_short = assign_short_signals_extended(best_sup_short, best_res_short, df, best_tw_short, "1d")
            extended_short = update_level_close_short(extended_short, df)
            round_factor_short = config.get("order_round_factor", ORDER_ROUND_FACTOR)
            short_cap, short_trades = simulate_short_trades_compound_extended(
                extended_short, df,
                starting_capital=config["initialCapitalShort"],
                commission_rate=COMMISSION_RATE,
                min_commission=MIN_COMMISSION,
                round_factor=round_factor_short,
                artificial_close_price=artificial_close_price,
                artificial_close_date=artificial_close_date
            )
            print(f"Beste Parameter (Short) für {ticker}: past_window={best_p_short}, trade_window={best_tw_short}, Final Capital (Short)={short_cap:.2f}")
        else:
            extended_short = pd.DataFrame()
            short_trades = []
            short_cap = config["initialCapitalShort"]
            standard_short = pd.DataFrame()
            print(f"Short-Trades für {ticker} deaktiviert. (short = False)")
            best_p_long, best_tw_long = berechne_best_p_tw_long(df, config, backtesting_begin, backtesting_end)
            best_sup_long, best_res_long = calculate_support_resistance(df, best_p_long, best_tw_long)

        print("\nMatched Long Trades:")
        print(pd.DataFrame(long_trades).to_string(index=False))
        # Statistik-Printout einfügen:
        if isinstance(long_trades, pd.DataFrame):
            stats(long_trades.to_dict("records"), "Long")
        else:
            stats(long_trades, "Long")
        print("\nMatched Short Trades:")
        print(pd.DataFrame(short_trades).to_string(index=False))
      # Statistik-Printout einfügen:
        if isinstance(short_trades, pd.DataFrame):
            stats(short_trades.to_dict("records"), "Short")
        else:
            stats(short_trades, "Short")
        print(stats(short_trades, "Short Trades"))#.to_string())
        print("\nExtended Long Signals:")
        print(extended_long.to_string(index=False))
        print("\nExtended Short Signals:")
        print(extended_short.to_string(index=False))

        # Compute equity curves before plotting
        dates = df.index
        # Long equity curve
        equity_long = []
        cap = config["initialCapitalLong"]
        pos = 0
        entry_price = 0
        trade_idx = 0
        trades = long_trades
        equity_val = cap
        for date in dates:
            if trade_idx < len(trades) and 'buy_date' in trades[trade_idx] and trades[trade_idx]['buy_date'] == date:
                pos = trades[trade_idx]['shares']
                entry_price = trades[trade_idx]['buy_price']
            if trade_idx < len(trades) and 'sell_date' in trades[trade_idx] and trades[trade_idx]['sell_date'] == date:
                cap += trades[trade_idx]['pnl']
                pos = 0
                entry_price = 0
                trade_idx += 1
            if pos > 0:
                equity_val = cap + pos * (df.loc[date, "Close"] - entry_price)
            else:
                equity_val = cap
            equity_long.append(equity_val)
        # Short equity curve
        equity_short = []
        cap = config["initialCapitalShort"]
        pos = 0
        entry_price = 0
        trade_idx = 0
        trades = short_trades
        equity_val = cap
        for date in dates:
            if trade_idx < len(trades) and 'short_date' in trades[trade_idx] and trades[trade_idx]['short_date'] == date:
                pos = trades[trade_idx]['shares']
                entry_price = trades[trade_idx]['short_price']
            if trade_idx < len(trades) and 'cover_date' in trades[trade_idx] and trades[trade_idx]['cover_date'] == date:
                cap += trades[trade_idx]['pnl']
                pos = 0
                entry_price = 0
                trade_idx += 1
            if pos > 0:
                equity_val = cap + pos * (entry_price - df.loc[date, "Close"])
            else:
                equity_val = cap
            equity_short.append(equity_val)
        equity_combined = [l + s for l, s in zip(equity_long, equity_short)]
        buyhold = [config["initialCapitalLong"] * (p / df["Close"].iloc[0]) for p in df["Close"]]

        plot_combined_chart_and_equity(
            df,
            standard_long,
            standard_short,
            best_sup_long, best_res_long, compute_trend(df, 20),
            equity_long, equity_short, equity_combined, buyhold,
            ticker
        )

import plotly.graph_objs as go
def plot_equity_curves_and_stats(df, long_trades, short_trades, ticker, start_capital_long, start_capital_short):
    import plotly.graph_objs as go
    import numpy as np

    df = df.sort_index()
    dates = df.index

    # --- Long Equity-Kurve: folgt Ticker nur wenn investiert ---
    equity_long = []
    cap = start_capital_long
    pos = 0
    entry_price = 0
    trade_idx = 0
    trades = long_trades
    equity_val = cap
    for date in dates:
        # Einstieg?
        if trade_idx < len(trades) and 'buy_date' in trades[trade_idx] and trades[trade_idx]['buy_date'] == date:
            pos = trades[trade_idx]['shares']
            entry_price = trades[trade_idx]['buy_price']
        # Ausstieg?
        if trade_idx < len(trades) and 'sell_date' in trades[trade_idx] and trades[trade_idx]['sell_date'] == date:
            cap += trades[trade_idx]['pnl']
            pos = 0
            entry_price = 0
            trade_idx += 1
        # Equity-Berechnung
        if pos > 0:
            equity_val = cap + pos * (df.loc[date, "Close"] - entry_price)
        else:
            equity_val = cap
        equity_long.append(equity_val)

    # --- Short Equity-Kurve: folgt Ticker nur wenn investiert ---
    equity_short = []
    cap = start_capital_short
    pos = 0
    entry_price = 0
    trade_idx = 0
    trades = short_trades
    equity_val = cap
    for date in dates:
        # Einstieg?
        if trade_idx < len(trades) and 'short_date' in trades[trade_idx] and trades[trade_idx]['short_date'] == date:
            pos = trades[trade_idx]['shares']
            entry_price = trades[trade_idx]['short_price']
        # Ausstieg?
        if trade_idx < len(trades) and 'cover_date' in trades[trade_idx] and trades[trade_idx]['cover_date'] == date:
            cap += trades[trade_idx]['pnl']
            pos = 0
            entry_price = 0
            trade_idx += 1
        # Equity-Berechnung
        if pos > 0:
            equity_val = cap + pos * (entry_price - df.loc[date, "Close"])
        else:
            equity_val = cap
        equity_short.append(equity_val)

    # --- Combined Equity-Kurve ---
    equity_combined = [l + s for l, s in zip(equity_long, equity_short)]

    # --- Buy & Hold ---
    buyhold = [start_capital_long * (p / df["Close"].iloc[0]) for p in df["Close"]]

    # --- Plotly-Chart ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=equity_long, mode='lines', name='Long Equity'))
    fig.add_trace(go.Scatter(x=dates, y=equity_short, mode='lines', name='Short Equity'))
    fig.add_trace(go.Scatter(x=dates, y=equity_combined, mode='lines', name='Combined'))
    fig.add_trace(go.Scatter(x=dates, y=buyhold, mode='lines', name='Buy & Hold'))

    fig.update_layout(title=f"Equity Curves für {ticker}",
                     xaxis_title="Datum",
                     yaxis_title="Kapital",
                     legend=dict(x=0, y=1.1, orientation="h"))
    fig.show()

# --- Trade-Statistiken ---
def stats(trades, name):
	# Akzeptiere DataFrame oder Liste von Dicts
	if isinstance(trades, pd.DataFrame):
		if trades.empty or 'pnl' not in trades.columns:
			print(f"\n{name}: Keine Trades.")
			return
		pnls = trades['pnl'].values
	elif isinstance(trades, list):
		if not trades or 'pnl' not in trades[0]:
			print(f"\n{name}: Keine Trades.")
			return
		pnls = [t['pnl'] for t in trades]
	else:
		print(f"\n{name}: Keine Trades.")
		return

	wins = [p for p in pnls if p > 0]
	losses = [p for p in pnls if p <= 0]
	print(f"\n{name}:")
	print(f"  Anzahl Trades: {len(trades)}")
	print(f"  Summe PnL: {sum(pnls):.2f}")
	print(f"  Ø PnL: {np.mean(pnls):.2f}")
	print(f"  Max PnL: {np.max(pnls):.2f}")
	print(f"  Min PnL: {np.min(pnls):.2f}")
	print(f"  Winning Trades: {len(wins)} ({len(wins)/len(trades)*100:.1f}%)")
	print(f"  Losing Trades: {len(losses)} ({len(losses)/len(trades)*100:.1f}%)")

#        stats(long_trades, "Long")
#        stats(short_trades, "Short")
#        print(f"\nBuy & Hold: Start={buyhold[0]:.2f}, Ende={buyhold[-1]:.2f}, Rendite={(buyhold[-1]/buyhold[0]-1)*100:.2f}%")
#        print(f"Combined: Start={equity_combined[0]:.2f}, Ende={equity_combined[-1]:.2f}, Rendite={(equity_combined[-1]/equity_combined[0]-1)*100:.2f}%")


import matplotlib.pyplot as plt

def plot_equity_curve_and_stats(df, trades, ticker, start_capital=10000):
    # Equity-Kurve berechnen
    equity = [start_capital]
    for trade in trades:
        equity.append(equity[-1] + trade['pnl'])
    equity = equity[1:]  # Erste Zeile ist Startkapital
    trade_dates = [trade['sell_date'] if 'sell_date' in trade else trade['cover_date'] for trade in trades]
    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(trade_dates, equity, marker='o', label=f'Equity {ticker}')
    plt.title(f'Equity Curve {ticker}')
    plt.xlabel('Datum')
    plt.ylabel('Kapital')
    plt.legend()
    plt.grid()
    plt.show()
    # Statistiken
    print(f"\n=== Trade-Statistiken für {ticker} ===")
    pnls = [t['pnl'] for t in trades]
    print(f"Anzahl Trades: {len(trades)}")
    print(f"Summe PnL: {sum(pnls):.2f}")
    print(f"Ø PnL: {np.mean(pnls):.2f}")
    print(f"Max PnL: {np.max(pnls):.2f}")
    print(f"Min PnL: {np.min(pnls):.2f}")

# Beispiel: Nach dem Backtesting für alle Ticker
def show_all_equity_curves_and_stats():
    for ticker, config in tickers.items():
        csv_filename = f"{ticker}_data.csv"
        if os.path.exists(csv_filename):
            df = pd.read_csv(csv_filename, parse_dates=["date"], index_col="date")
            df.sort_index(inplace=True)
            df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"}, inplace=True)
            # Beispiel: Long-Trades simulieren
            best_p_long, best_tw_long = berechne_best_p_tw_long(df, config, backtesting_begin, backtesting_end)
            best_sup_long, best_res_long = calculate_support_resistance(df, best_p_long, best_tw_long)
            sig = assign_long_signals(best_sup_long, best_res_long, df, best_tw_long, "1d")
            cap, trades = simulate_trades_compound(sig, df, starting_capital=config["initialCapitalLong"])
            #plot_equity_curve_and_stats(df, trades, ticker, start_capital=config["initialCapitalLong"])

# Am Ende von both_backtesting_multi(ib) oder als eigenen Modus aufrufen:
# show_all_equity_curves_and_stats()
def get_today_minute_data(ib, contract):
    """
    Holt die Minutendaten für den aktuellen Tag von IB.
    Gibt ein DataFrame mit Spalten open, high, low, close, volume zurück.
    """
    now = datetime.datetime.now(ZoneInfo("America/New_York"))
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=15, minute=45, second=0, microsecond=0)
    # Beide tz-naiv machen:
    today = today.replace(tzinfo=None)
    end_time = end_time.replace(tzinfo=None)
    contract = Crypto(config["symbol"], config["exchange"], "USD")
    whatToShow = "AGGTRADES"

    bars = ib.reqHistoricalData(
        contract,
        endDateTime="",
        durationStr="365 D",
        barSizeSetting="1 day",
        whatToShow=whatToShow,
        useRTH=True
    )
    df = pd.DataFrame(bars)
    if df.empty:
        return None
    df['date'] = pd.to_datetime(df['date'])
    # Entferne Zeitzone (macht alles tz-naive)
    df['date'] = df['date'].dt.tz_localize(None)
    df.set_index('date', inplace=True)
    df = df[(df.index >= today) & (df.index <= end_time)]
    return df

def trading_multi(ib):
    print("=== Trading-Testlauf für Datum:", pd.Timestamp.now(tz=ZoneInfo("America/New_York")).normalize())
    for ticker, config in tickers.items():
        print(f"\n--- {ticker}: Starte Trading-Check ---")
        csv_filename = f"{ticker}_data.csv"
        contract = Crypto(config["symbol"], config["exchange"], "USD")
        # Lade Tagesdaten
        if os.path.exists(csv_filename):
            daily_df = pd.read_csv(csv_filename, parse_dates=["date"], index_col="date")
            daily_df.sort_index(inplace=True)
            daily_df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"}, inplace=True)
        else:
            print(f"{ticker}: Keine Tagesdaten gefunden, lade neu ...")
            daily_df = update_historical_data_csv(ib, contract, csv_filename)
            if daily_df is None:
                print(f"{ticker}: Keine historischen Tagesdaten verfügbar. Überspringe Ticker.")
                continue
            daily_df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"}, inplace=True)

        # --- NEU: Fehlt ein Tag? Dann aktualisiere bis gestern ---
        today = pd.Timestamp.now(tz=ZoneInfo("America/New_York")).normalize().tz_localize(None)
        if not is_trading_day(today):
            print(f"{ticker}: {today.date()} ist kein Handelstag. Kein Update/Trade.")
            continue        
        yesterday = today - pd.Timedelta(days=1)
        last_daily = daily_df.index.max()
        if last_daily < yesterday:
            print(f"{ticker}: Aktualisiere Tagesdaten bis {yesterday.date()} ...")
            daily_df = update_historical_data_csv(ib, contract, csv_filename)
            if daily_df is None:
                print(f"{ticker}: Keine historischen Tagesdaten verfügbar. Überspringe Ticker.")
                continue
            daily_df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"}, inplace=True)

        # Realtime-Kurs von IB holen (mit Fallback auf Yahoo)
        print(f"{ticker}: Fordere Realtime-Kurs an ...")
        last_price, bid, ask = get_realtime_price(ticker, contract, ib)
        print(f"{ticker}: Realtime-Kurse (inkl. Fallback): Last={last_price}, Bid={bid}, Ask={ask}")

        if last_price is None or last_price <= 0 or (hasattr(last_price, 'isnan') and last_price.isnan()):
            print(f"{ticker}: Kein Kurs verfügbar. Kein Trade.")
            continue

        # --- NEU: Füge Realtime-Kurs als neuen Tagesabschluss hinzu (nur wenn noch nicht vorhanden) ---
        if today not in daily_df.index:
            new_row = pd.DataFrame({
                "Open": last_price,
                "High": last_price,
                "Low": last_price,
                "Close": last_price,
                "Volume": 0
            }, index=[today])
            daily_df = pd.concat([daily_df, new_row])
            daily_df.sort_index(inplace=True)
            daily_df.to_csv(csv_filename, index_label="date")
            print(f"{ticker}: Realtime-Kurs als neuen Tagesabschluss für {today.date()} hinzugefügt.")

        # Support/Resistance berechnen (Debug)
        print(f"{ticker}: Berechne Support/Resistance ...")
        best_p_long, best_tw_long = berechne_best_p_tw_long(daily_df, config, backtesting_begin, backtesting_end)
        long_support, long_resistance = calculate_support_resistance(daily_df, best_p_long, best_tw_long)
        long_signals_df = assign_long_signals(long_support, long_resistance, daily_df, best_tw_long, "1d")
        long_support, long_resistance = calculate_support_resistance(daily_df, best_p_long, best_tw_long)
        long_signals_df = assign_long_signals(long_support, long_resistance, daily_df, best_tw_long, "1d")

        # Prüfe, ob heute ein neues Signal entstanden ist
# ...existing code...
        # Prüfe, ob heute ein neues Signal entstanden ist
        long_today = long_signals_df[long_signals_df["Long Date"] == today]
        print(f"{ticker}: Long-Signale heute: {len(long_today)}")
        if not long_today.empty:
            last_long = long_today.iloc[-1]
            pos_long = sum(pos.position for pos in ib.positions() if pos.contract.symbol == ticker and pos.position > 0)
            shares = calculate_shares(config["initialCapitalLong"], last_price, config.get("order_round_factor", ORDER_ROUND_FACTOR))
            min_size = config.get("order_round_factor", 0.01)
            shares = round(shares / min_size) * min_size  # auf Tick-Size runden
            print(f"{ticker}: Signal={last_long['Long']}, Shares={shares}, Position={pos_long}")
            if shares < min_size:
                print(f"{ticker}: Ordergröße zu klein ({shares}), keine Order gesendet.")
                continue
            if last_long["Long"] == "buy" and pos_long == 0:
                print(f"{ticker}: MARKET BUY {shares} @ {last_price}")
                order1 = MarketOrder("BUY", shares)
                ib.placeOrder(contract, order1)
                time.sleep(2)
                limit_price = round(last_price * 0.995, 2)
                tick_size = min_size
                limit_price = round(round(limit_price / tick_size) * tick_size, 2)
                print(f"{ticker}: LIMIT BUY {shares} @ {limit_price}")
                order2 = LimitOrder("BUY", shares, limit_price, outsideRth=True)
                ib.placeOrder(contract, order2)
            elif last_long["Long"] == "sell" and pos_long > 0:
                print(f"{ticker}: MARKET SELL {shares} @ {last_price}")
                order1 = MarketOrder("SELL", shares)
                ib.placeOrder(contract, order1)
                time.sleep(2)
                limit_price = round(last_price * 1.005, 2)
                tick_size = min_size
                limit_price = round(round(limit_price / tick_size) * tick_size, 2)
                print(f"{ticker}: LIMIT SELL {shares} @ {limit_price}")
                order2 = LimitOrder("SELL", shares, limit_price, outsideRth=True)
                ib.placeOrder(contract, order2)
        else:
            print(f"{ticker}: Kein Long-Trade heute.")
# ...existing code...

        # Gleiches für Short (optional)
        best_p_short, best_tw_short = berechne_best_p_tw_short(daily_df, config, backtesting_begin, backtesting_end)
        short_support, short_resistance = calculate_support_resistance(daily_df, best_p_short, best_tw_short)
        short_signals_df = assign_short_signals(short_support, short_resistance, daily_df, best_tw_short, "1d")

        short_support, short_resistance = calculate_support_resistance(daily_df, best_p_short, best_tw_short)
        short_signals_df = assign_short_signals(short_support, short_resistance, daily_df, best_tw_short, "1d")

        short_today = short_signals_df[short_signals_df["Short Date"] == today]
        print(f"{ticker}: Short-Signale heute: {len(short_today)}")
# ...existing code...
        if not short_today.empty:
            last_short = short_today.iloc[-1]
            pos_short = sum(pos.position for pos in ib.positions() if pos.contract.symbol == ticker and pos.position < 0)
            shares = calculate_shares(config["initialCapitalShort"], last_price, config.get("order_round_factor", ORDER_ROUND_FACTOR))
            min_size = config.get("order_round_factor", 0.01)
            shares = round(shares / min_size) * min_size  # auf Tick-Size runden
            print(f"{ticker}: Signal={last_short['Short']}, Shares={shares}, Position={pos_short}")
            if shares < min_size:
                print(f"{ticker}: Ordergröße zu klein ({shares}), keine Order gesendet.")
                continue
            if last_short["Short"] == "short" and pos_short == 0:
                print(f"{ticker}: MARKET SHORT {shares} @ {last_price}")
                order1 = MarketOrder("SELL", shares)
                ib.placeOrder(contract, order1)
                time.sleep(2)
                limit_price = round(last_price * 1.005, 2)  # 0.5% über Market
                tick_size = min_size
                limit_price = round(round(limit_price / tick_size) * tick_size, 2)
                print(f"{ticker}: LIMIT SHORT {shares} @ {limit_price}")
                order2 = LimitOrder("SELL", shares, limit_price)
                ib.placeOrder(contract, order2)
            elif last_short["Short"] == "cover" and pos_short < 0:
                print(f"{ticker}: MARKET COVER {shares} @ {last_price}")
                order1 = MarketOrder("BUY", shares)
                ib.placeOrder(contract, order1)
                time.sleep(2)
                limit_price = round(last_price * 0.995, 2)  # 0.5% unter Market
                tick_size = min_size
                limit_price = round(round(limit_price / tick_size) * tick_size, 2)
                print(f"{ticker}: LIMIT COVER {shares} @ {limit_price}")
                order2 = LimitOrder("BUY", shares, limit_price)
                ib.placeOrder(contract, order2)
# ...existing code...
        else:
            print(f"{ticker}: Kein Short-Trade heute.")

def daytrading_multi(ib, intervals=["5 mins", "15 mins", "30 mins", "1 hour"], days_back=10):
    """
    Lädt und speichert OHLCV-Daten für verschiedene Zeitintervalle für alle Ticker.
    Nutzt für das letzte Intervall den aktuellen Realtime-Kurs von IB (mit YF-Fallback).
    """
    for ticker, config in tickers.items():
        contract = Crypto(config["symbol"], config["exchange"], "USD")
        for interval in intervals:
            # IB-Parameter
            bar_size = interval
            duration = f"{days_back} D"
            print(f"\n[{ticker}] Lade {bar_size} Daten für {duration} ...")
            contract = Crypto(config["symbol"], config["exchange"], "USD")
            whatToShow = "AGGTRADES"

            bars = ib.reqHistoricalData(
                contract,
                endDateTime="",
                durationStr="365 D",
                barSizeSetting="1 day",
                whatToShow=whatToShow,
                useRTH=True
            )
            df = pd.DataFrame(bars)
            if df.empty:
                print(f"Keine Daten für {ticker} ({bar_size}) erhalten.")
                continue
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            # Einheitliche Spaltennamen
            df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}, inplace=True)
            # Speichern
            fname = f"{ticker}_{bar_size.replace(' ', '').replace('hour','h').replace('min','m')}.csv"
            df.to_csv(fname)
            print(f"Gespeichert: {fname} ({len(df)} Zeilen)")

            # --- NEU: Realtime-Kurs für das aktuelle Intervall holen ---
            last_price, bid, ask = get_realtime_price(ticker, contract, ib)
            print(f"{ticker} ({interval}): Realtime-Kurse: Last={last_price}, Bid={bid}, Ask={ask}")

            # Intervall-String für Signalzuordnung anpassen
            interval_str = (
                bar_size.replace(" ", "")
                        .replace("mins", "min")
                        .replace("min", "min")
                        .replace("hour", "h")
            )
            # Beispiel: Berechne Support/Resistance und Signale
            if len(df) > 10:

                best_p_long, best_tw_long = berechne_best_p_tw_long(df, config, backtesting_begin, backtesting_end)
                best_sup_long, best_res_long = calculate_support_resistance(df, best_p_long, best_tw_long)
                sig_long = assign_long_signals(best_sup_long, best_res_long, df, best_tw_long, interval_str)

                best_p_short, best_tw_short = berechne_best_p_tw_short(df, config, backtesting_begin, backtesting_end)
                best_sup_short, best_res_short = calculate_support_resistance(df, best_p_short, best_tw_short)
                sig_short = assign_short_signals(best_sup_short, best_res_short, df, best_tw_short, interval_str)

                print(f"Long-Signale ({bar_size}):\n", sig_long.tail(3))
                print(f"Short-Signale ({bar_size}):\n", sig_short.tail(3))
                

def wait_and_trade_at_1540(ib):
    print("Warte auf 15:45 New York Zeit für Trading ... (Beenden mit STRG+C)")
    while True:
        now = datetime.datetime.now(ZoneInfo("America/New_York"))
        # Prüfe, ob es 15:40 <= jetzt < 15:50 ist (Trading-Fenster)
        if now.hour == 15 and 45 <= now.minute < 50 :
            print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} NY: Starte Trading!")
            trading_multi(ib, force=True)
            # Warte bis nach 15:45, damit nicht mehrfach getradet wird
            while True:
                now2 = datetime.datetime.now(ZoneInfo("America/New_York"))
                if now2.minute >= 49 or now2.hour > 15:
                    break
                time.sleep(10)
            print("Trading abgeschlossen, warte auf nächsten Tag ...")
        else:
            # Noch nicht im Trading-Fenster, warte 30 Sekunden
            time.sleep(30)

def live_trading_loop(ib, intervals=["5 mins", "15 mins", "30 mins", "1 hour"], order_time="15:45"):
    """
    Hält die IB-Verbindung offen und prüft regelmäßig, ob ein neues Intervall abgeschlossen ist
    oder ob es Zeit für die End-of-Day-Order ist. Holt dann Daten und platziert ggf. Orders.
    """
    print("Starte Live-Trading-Loop. Beende mit STRG+C.")
    last_checked = {ticker: {iv: None for iv in intervals} for ticker in tickers}
    try:
        while True:
            now = datetime.datetime.now(ZoneInfo("America/New_York"))
            # --- End-of-Day-Trading um 15:50 ---
            if now.strftime("%H:%M") == order_time:
                print(f"\n[{now.strftime('%H:%M')}] Prüfe End-of-Day-Trading ...")
                trading_multi(ib)
                time.sleep(60)  # Warte eine Minute, um Doppel-Orders zu vermeiden

            # --- Daytrading für alle Intervalle ---
            for ticker, config in tickers.items():
                contract = Crypto(config["symbol"], config["exchange"], "USD")
                for interval in intervals:
                    # Prüfe, ob ein neues Intervall abgeschlossen ist
                    if interval.endswith("mins"):
                        interv_min = int(interval.split()[0])
                        if now.minute % interv_min == 0 and (last_checked[ticker][interval] != now.replace(second=0, microsecond=0)):
                            print(f"\n[{now.strftime('%H:%M')}] {ticker}: Prüfe {interval} Intervall ...")
                            contract = Crypto(config["symbol"], config["exchange"], "USD")
                            whatToShow = "AGGTRADES"

                            bars = ib.reqHistoricalData(
                                contract,
                                endDateTime="",
                                durationStr="365 D",
                                barSizeSetting="1 day",
                                whatToShow=whatToShow,
                                useRTH=True
                            )
                            df = pd.DataFrame(bars)
                            if not df.empty:
                                df['date'] = pd.to_datetime(df['date'])
                                df.set_index('date', inplace=True)
                                df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}, inplace=True)
                                best_p_long, best_tw_long = berechne_best_p_tw_long(df, config, backtesting_begin, backtesting_end)
                                best_sup_long, best_res_long = calculate_support_resistance(df, best_p_long, best_tw_long)
                                sig_long = assign_long_signals(best_sup_long, best_res_long, df, best_tw_long, interval.replace(" ", ""))
                                best_p_short, best_tw_short = berechne_best_p_tw_short(df, config, backtesting_begin, backtesting_end)
                                best_sup_short, best_res_short = calculate_support_resistance(df, best_p_short, best_tw_short)
                                sig_short = assign_short_signals(best_sup_short, best_res_short, df, best_tw_short, interval.replace(" ", ""))

                                print(f"Long-Signale ({interval}):\n", sig_long.tail(1))
                                print(f"Short-Signale ({interval}):\n", sig_short.tail(1))
                            last_checked[ticker][interval] = now.replace(second=0, microsecond=0)
                    elif interval.endswith("hour"):
                        if now.minute == 0 and (last_checked[ticker][interval] != now.replace(second=0, microsecond=0)):
                            print(f"\n[{now.strftime('%H:%M')}] {ticker}: Prüfe {interval} Intervall ...")
                            contract = Crypto(config["symbol"], config["exchange"], "USD")
                            whatToShow = "AGGTRADES"

                            bars = ib.reqHistoricalData(
                                contract,
                                endDateTime="",
                                durationStr="365 D",
                                barSizeSetting="1 day",
                                whatToShow=whatToShow,
                                useRTH=True
                            )
                            df = pd.DataFrame(bars)
                            if not df.empty:
                                df['date'] = pd.to_datetime(df['date'])
                                df.set_index('date', inplace=True)
                                best_p_long, best_tw_long = berechne_best_p_tw_long(df, config, backtesting_begin, backtesting_end)
                                best_sup_long, best_res_long = calculate_support_resistance(df, best_p_long, best_tw_long)
                                sig_long = assign_long_signals(best_sup_long, best_res_long, df, best_tw_long, interval.replace(" ", ""))
                                best_p_short, best_tw_short = berechne_best_p_tw_short(df, config, backtesting_begin, backtesting_end)
                                best_sup_short, best_res_short = calculate_support_resistance(df, best_p_short, best_tw_short)
                                sig_short = assign_short_signals(best_sup_short, best_res_short, df, best_tw_short, interval.replace(" ", ""))

                                print(f"Long-Signale ({interval}):\n", sig_long.tail(1))
                                print(f"Short-Signale ({interval}):\n", sig_short.tail(1))
                            last_checked[ticker][interval] = now.replace(second=0, microsecond=0)
            time.sleep(30)  # Prüfe alle 30 Sekunden
    except KeyboardInterrupt:
        print("Live-Trading-Loop beendet.")
        ib.disconnect()

def download_ib_minute_data(ib, symbol, exchange, currency, date, end_time="15:45:00", n_bars=100, filename=None):
    """
    Lädt n_bars Minutendaten für ein Symbol bis zu einer bestimmten Uhrzeit an einem Tag.
    Speichert als CSV, falls filename angegeben.
    Gibt ein DataFrame zurück oder None bei Fehler.
    """
    from ib_insync import Stock
    import pandas as pd
    import datetime

    contract = Crypto(symbol, exchange, currency)
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    date_str = date.strftime("%Y%m%d")
    end_datetime = f"{date_str} {end_time}"

    # IB verlangt durationStr in Sekunden (z.B. "1200 S" für 20 Minuten)
    duration_seconds = n_bars * 60
    durationStr = f"{duration_seconds} S"

    print(f"Lade {n_bars} Minutendaten für {symbol} bis {end_time} am {date_str} ...")
    contract = Crypto(config["symbol"], config["exchange"], "USD")
    whatToShow = "AGGTRADES"

    bars = ib.reqHistoricalData(
        contract,
        endDateTime="",
        durationStr="365 D",
        barSizeSetting="1 day",
        whatToShow=whatToShow,
        useRTH=True
    )
    if not bars:
        print("Keine Daten erhalten. Prüfe Marktdaten-Abo und Datum.")
        return None

    df = pd.DataFrame(bars)
    if df.empty:
        print("Leeres DataFrame erhalten.")
        return None

    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.tz_localize(None)
    df.set_index('date', inplace=True)
    if filename:
        df.to_csv(filename)
        print(f"Gespeichert: {filename} ({len(df)} Zeilen)")
    return df


def get_minute_data_for_date(ib, contract, date):
    """
    Holt Minutendaten für einen bestimmten Tag (date: 'YYYYMMDD' oder datetime.date).
    Gibt None zurück, wenn keine Daten geliefert werden (z.B. wegen fehlendem Marktdaten-Abo).
    """
    if isinstance(date, datetime.date):
        date_str = date.strftime("%Y%m%d")
    else:
        date_str = str(date)
    end_time = f"{date_str} 15:45:00"
    bars = ib.reqHistoricalData(
        contract,
        endDateTime=end_time,
        durationStr="1 D",
        barSizeSetting="1 min",
        whatToShow="AGGTRADES",
        useRTH=True
    )
    if not bars:
        logging.warning(f"Keine Minutendaten von IB für {contract.symbol} am {date_str}. Prüfe Marktdaten-Abo und HMDS.")
        return None
    df = pd.DataFrame(bars)
    if df.empty:
        logging.warning(f"Leeres DataFrame für {contract.symbol} am {date_str}.")
        return None
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.tz_localize(None)
    df.set_index('date', inplace=True)
    return df



def plot_combined_chart_and_equity(df, standard_long, standard_short, supp, res, trend, equity_long, equity_short, equity_combined, buyhold, ticker):
    # Marker-Serien erzeugen (wie in plot_optimal_trades_multi)
    offset = 0.02 * (df["Close"].max() - df["Close"].min())
    buy_offset = 2*offset
    sell_offset = -2*offset
    short_offset = -offset
    cover_offset = offset

    buy_marker = pd.Series(np.nan, index=df.index)
    sell_marker = pd.Series(np.nan, index=df.index)
    short_marker = pd.Series(np.nan, index=df.index)
    cover_marker = pd.Series(np.nan, index=df.index)

    for _, row in standard_long.iterrows():
        if row["Long"] == "buy" and pd.notna(row["Long Date"]):
            buy_marker.loc[row["Long Date"]] = df.loc[row["Long Date"], "Close"] + buy_offset
        elif row["Long"] == "sell" and pd.notna(row["Long Date"]):
            sell_marker.loc[row["Long Date"]] = df.loc[row["Long Date"], "Close"] + sell_offset
    for _, row in standard_short.iterrows():
        if row.get("Short") == "short" and pd.notna(row["Short Date"]):
            short_marker.loc[row["Short Date"]] = df.loc[row["Short Date"], "Close"] + short_offset
        elif row.get("Short") == "cover" and pd.notna(row["Short Date"]):
            cover_marker.loc[row["Short Date"]] = df.loc[row["Short Date"], "Close"] + cover_offset

    # Subplots: 2 rows, shared x
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        row_heights=[0.6, 0.4],
                        subplot_titles=(f"{ticker} Candlestick mit Markern", "Equity-Kurven"))

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="Candlestick"
    ), row=1, col=1)

    # Marker als Scatter
    fig.add_trace(go.Scatter(x=buy_marker.index, y=buy_marker.values, mode='markers',
                             marker=dict(symbol='triangle-up', color='red', size=12), name='Buy'), row=1, col=1)
    fig.add_trace(go.Scatter(x=sell_marker.index, y=sell_marker.values, mode='markers',
                             marker=dict(symbol='triangle-down', color='red', size=12), name='Sell'), row=1, col=1)
    fig.add_trace(go.Scatter(x=short_marker.index, y=short_marker.values, mode='markers',
                             marker=dict(symbol='triangle-down', color='blue', size=12), name='Short'), row=1, col=1)
    fig.add_trace(go.Scatter(x=cover_marker.index, y=cover_marker.values, mode='markers',
                             marker=dict(symbol='triangle-up', color='blue', size=12), name='Cover'), row=1, col=1)
    # Support/Resistance
    fig.add_trace(go.Scatter(x=supp.index, y=supp.values, mode='markers',
                             marker=dict(symbol='circle', color='green', size=10), name='Support'), row=1, col=1)
    fig.add_trace(go.Scatter(x=res.index, y=res.values, mode='markers',
                             marker=dict(symbol='circle', color='orange', size=10), name='Resistance'), row=1, col=1)
    # Trend
    fig.add_trace(go.Scatter(x=trend.index, y=trend.values, mode='lines', line=dict(color='black', width=2), name='Trend'), row=1, col=1)

    # Equity-Kurven
    fig.add_trace(go.Scatter(x=df.index, y=equity_long, mode='lines', name='Long Equity'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=equity_short, mode='lines', name='Short Equity'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=equity_combined, mode='lines', name='Combined'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=buyhold, mode='lines', name='Buy & Hold'), row=2, col=1)

    #fig.update_layout(height=900, title=f"{ticker}: Candlestick & Equity-Kurven")
    fig.update_layout(
    height=900,
    title=f"{ticker}: Candlestick & Equity-Kurven",
        xaxis=dict(
            rangeslider=dict(visible=False)  # Kein Slider unter Chart 1
        ),
    xaxis2=dict(
        rangeslider=dict(
            visible=True,
            thickness=0.03,  # sehr dünn
            bgcolor="#eee"
        ),
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(step="all")
            ]
        ),
        showline=True,
        showgrid=True,
    ),
    margin=dict(b=30, t=60),  # wenig Platz unten
)                                          
    fig.show()
# Beispiel-Funktion für deinen Preis-Thread
def yahoo_price_thread(symbol):
    import time
    while not price_event.is_set():
        # ...hole Preis von Yahoo...
        last_price, bid, ask = get_yf_price(symbol)
        if last_price is not None and last_price > 0:
            shared_price["price"] = last_price
            shared_price["bid"] = bid
            shared_price["ask"] = ask
            price_event.set()  # Thread kann jetzt stoppen!
            break
        time.sleep(1)

# Mapping für Yahoo-Finance-Symbole
YF_SYMBOLS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "LTC": "LTC-USD",
    "XRP": "XRP-USD",
    "ADA": "ADA-USD",
    "DOGE": "DOGE-USD",
    "BRRR": "BRRR"
    }

def get_yf_price(symbol):
    yf_symbol = YF_SYMBOLS.get(symbol, symbol)
    ticker = yf.Ticker(yf_symbol)
    data = ticker.history(period="1d", interval="1m")
    if not data.empty:
        last_row = data.iloc[-1]
        last_price = last_row['Close']
        bid = last_price  # YF liefert kein Bid/Ask, nur Close
        ask = last_price
        return float(last_price), float(bid), float(ask)
    else:
        return None, None, None


def get_realtime_price(ticker, ib_contract, ib):
    try:
        ticker_data = ib.reqMktData(ib_contract, '', False, False)
        ib.sleep(1)
        last = ticker_data.last
        bid = ticker_data.bid
        ask = ticker_data.ask
        if last is not None:
            return float(last), float(bid), float(ask)
    except Exception as e:
        print(f"IB Preisfehler für {ticker}: {e}")
    # Fallback: Yahoo Finance (mit Mapping!)
    last, bid, ask = get_yf_price(ticker)
    return last, bid, ask

def get_backtesting_slice(df, backtesting_begin=0, backtesting_end=50):
    n = len(df)
    start_idx = int(n * backtesting_begin / 100)
    end_idx = int(n * backtesting_end / 100)
    return df.iloc[start_idx:end_idx]

def berechne_best_p_tw_long(df, config, backtesting_begin=0, backtesting_end=50):
    df_opt = get_backtesting_slice(df, backtesting_begin, backtesting_end)
    print(f"Optimierung Long von {df_opt.index.min().date()} bis {df_opt.index.max().date()} "
          f"({len(df_opt)} Zeilen, {backtesting_begin}% bis {backtesting_end}% der Daten)")
    long_results = []
    for p in range(3, 10):
        for tw in range(1, 6):
            supp_temp, res_temp = calculate_support_resistance(df_opt, p, tw)
            sig = assign_long_signals(supp_temp, res_temp, df_opt, tw, "1d")
            cap, _ = simulate_trades_compound(
                sig, df_opt,
                starting_capital=config["initialCapitalLong"],
                commission_rate=COMMISSION_RATE,
                min_commission=MIN_COMMISSION,
                round_factor=config.get("order_round_factor", ORDER_ROUND_FACTOR)
            )
            long_results.append({"past_window": p, "trade_window": tw, "final_cap": cap})
    long_df = pd.DataFrame(long_results)
    best_long = long_df.loc[long_df["final_cap"].idxmax()]
    best_p_long = int(best_long["past_window"])
    best_tw_long = int(best_long["trade_window"])
    return best_p_long, best_tw_long

def berechne_best_p_tw_short(df, config, backtesting_begin=0, backtesting_end=50):
    df_opt = get_backtesting_slice(df, backtesting_begin, backtesting_end)
    print(f"Optimierung Short von {df_opt.index.min().date()} bis {df_opt.index.max().date()} "
          f"({len(df_opt)} Zeilen, {backtesting_begin}% bis {backtesting_end}% der Daten)")
    short_results = []
    for p in range(3, 10):
        for tw in range(1, 4):
            supp_temp, res_temp = calculate_support_resistance(df_opt, p, tw)
            sig = assign_short_signals(supp_temp, res_temp, df_opt, tw, "1d")
            cap, _ = simulate_short_trades_compound(
                sig, df_opt,
                starting_capital=config["initialCapitalShort"],
                commission_rate=COMMISSION_RATE,
                min_commission=MIN_COMMISSION,
                round_factor=config.get("order_round_factor", ORDER_ROUND_FACTOR)
            )
            short_results.append({"past_window": p, "trade_window": tw, "final_cap": cap})
    short_df = pd.DataFrame(short_results)
    best_short = short_df.loc[short_df["final_cap"].idxmax()]
    best_p_short = int(best_short["past_window"])
    best_tw_short = int(best_short["trade_window"])
    return best_p_short, best_tw_short
    

# =============================================================================
# 11. Main: Moduswahl über Kommandozeilenparameter
# =============================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        print("Bitte 'optimalplot', 'bothbacktesting', 'trading', 'daytrading' oder 'live' als Modus angeben.")
        sys.exit(1)
    
    ib = IB()
    ib.connect("127.0.0.1", 7497, clientId=5)
    
    if mode == "optimalplot":
        for ticker in tickers.keys():
            print(f"\nStarte optimalplot für {ticker} ...")
            plot_optimal_trades_multi(ticker, ib)
        ib.disconnect()
    elif mode == "bothbacktesting":
        both_backtesting_multi(ib)
        #show_all_equity_curves_and_stats()
        ib.disconnect()
    elif mode == "trading":
        trading_multi(ib)
       # wait_and_trade_at_1540(ib)
    elif mode == "daytrading":
        #intervals = sys.argv[2:] if len(sys.argv) > 2 else ["5 mins", "15 mins", "30 mins", "1 hour"]
        daytrading_multi(ib, intervals=intervals)
        print("Daytrading abgeschlossen. Verbindung bleibt bestehen. Beenden mit STRG+C.")
        while True:
            time.sleep(60)
    elif mode == "live":
        intervals = sys.argv[2:] if len(sys.argv) > 2 else ["5 mins", "15 mins", "30 mins", "1 hour"]
        live_trading_loop(ib, intervals=intervals)
        # KEIN ib.disconnect() hier!
    else:
        print("Unbekannter Modus. Bitte 'optimalplot', 'bothbacktesting', 'trading', 'daytrading' oder 'live' angeben.")
        ib.disconnect()