# signal_utils.py

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from config import COMMISSION_RATE, MIN_COMMISSION, ORDER_ROUND_FACTOR, backtesting_begin, backtesting_end, backtest_years
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def calculate_support_resistance(df, past_window, trade_window):
    """
    Berechnet Support- und Resistance-Levels für ein DataFrame mit 'Close'-Spalte.

    Args:
        df (pd.DataFrame): DataFrame mit mindestens 'Close'-Spalte und DatetimeIndex.
        past_window (int): Fenstergröße für Support/Resistance.
        trade_window (int): Abstand zur nächsten Kerze (z.B. für Backtest).

    Returns:
        support (pd.Series), resistance (pd.Series)
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = pd.to_datetime(df.index)

    close = df['Close'].values

    support_idx = []
    resistance_idx = []

    # Berechne lokale Minima/Maxima
    for i in range(past_window, len(close) - trade_window):
        window = close[i - past_window : i + trade_window + 1]
        if close[i] == np.min(window):
            support_idx.append(i)
        if close[i] == np.max(window):
            resistance_idx.append(i)

    # Support/Resistance als Series mit Zeitstempel als Index, 1D-Vektoren!
    support = pd.Series(close[support_idx].flatten(), index=df.index[support_idx])
    resistance = pd.Series(close[resistance_idx].flatten(), index=df.index[resistance_idx])
    return support, resistance

def compute_trend(df, window=20):
    return df["Close"].rolling(window=window).mean()


def assign_long_signals(support, resistance, df, tw, interval):
    df2 = df.sort_index()
    sup = pd.DataFrame({
        "Date": support.index,
        "Level": support.values,
        "Type": "support"
    })
    res = pd.DataFrame({
        "Date": resistance.index,
        "Level": resistance.values,
        "Type": "resistance"
    })

    sig = pd.concat([sup, res]).sort_values("Date").reset_index(drop=True)
    sig["Long"] = None
    sig["Long Date"] = pd.NaT
    active = False

    for i, row in sig.iterrows():
        dt0 = row["Date"]
        target = dt0 + pd.Timedelta(days=tw)
        idx = df2.index.get_indexer([target], method="nearest")
        trade_dt = df2.index[idx[0]] if idx.size else pd.NaT

        if row["Type"] == "support" and not active:
            sig.at[i, "Long"] = "buy"
            sig.at[i, "Long Date"] = trade_dt
            active = True
        elif row["Type"] == "resistance" and active:
            sig.at[i, "Long"] = "sell"
            sig.at[i, "Long Date"] = trade_dt
            active = False

    return sig

def simulate_trades_compound_extended(
    signal_df, market_df, config,
    commission_rate=0.001,
    min_commission=1.0,
    round_factor=1,
    artificial_close_price=None,
    artificial_close_date=None,
    direction="long"
):
    import pandas as pd
    import numpy as np

    capital = config.get("initialCapitalLong" if direction == "long" else "initialCapitalShort", 10000)
    base = direction.capitalize()
    possible_date_cols = [f"{base} Date detected", f"{base} Date", "Detect Date", "Trade Day"]
    possible_action_cols = [f"{base} Action", "Action"]

    date_col = next((col for col in possible_date_cols if col in signal_df.columns), None)
    action_col = next((col for col in possible_action_cols if col in signal_df.columns), None)

    if not date_col or not action_col:
        print(f"⚠️ Fehlende Spalten für {direction}: {date_col=} {action_col=}")
        return capital, []

    price_mode = config.get("trade_on", "close").lower()
    price_col = "Open" if price_mode == "open" else "Close"
    if price_col not in market_df.columns:
        print(f"⚠️ Preisspalte '{price_col}' fehlt in Marktdaten.")
        return capital, []

    # REMOVED: signal_df = signal_df.dropna(subset=[date_col])
    signal_df = signal_df.sort_values(by=date_col)
    trades = []
    position_active = False
    buy_price = buy_date = prev_cap = shares = None

    # Prepare index: ensure DatetimeIndex, normalized (date only), unique
    market_df = market_df.copy()
    market_df.index = pd.to_datetime(market_df.index).normalize()
    if not market_df.index.is_unique:
        market_df = market_df[~market_df.index.duplicated(keep='first')]

    for _, row in signal_df.iterrows():
        action = str(row.get(action_col)).lower()
        exec_date = pd.to_datetime(row.get(date_col)).normalize() if pd.notna(row.get(date_col)) else None

        if action not in ("buy", "sell", "short", "cover") or exec_date is None:
            continue

        # Robust price lookup: always scalar, never Series/array
        price = np.nan
        if exec_date in market_df.index:
            price = market_df.loc[exec_date, price_col]
        else:
            idx = market_df.index.get_indexer([exec_date], method='nearest')[0]
            if idx >= 0 and idx < len(market_df):
                price = market_df.iloc[idx][price_col]

        # If price is a Series or array, get first element
        if isinstance(price, (pd.Series, np.ndarray)):
            price = price.iloc[0] if isinstance(price, pd.Series) else price[0]

        # Allow NaN prices for extended trades
        # if price is None or pd.isna(price):
        #     continue

        # BUY or SHORT
        if action in ("buy", "short") and not position_active:
            shares = calculate_shares(capital, price, round_factor)
            if shares < 1e-6:
                continue
            buy_price = price
            buy_date = exec_date
            prev_cap = capital
            position_active = True

        # SELL or COVER
        elif action in ("sell", "cover") and position_active:
            sell_price = price
            sell_date = exec_date
            profit = (sell_price - buy_price) * shares if direction == "long" else (buy_price - sell_price) * shares
            turnover = shares * ((buy_price if buy_price is not None else 0) + (sell_price if sell_price is not None else 0))
            fee = max(min_commission, turnover * commission_rate)
            new_cap = prev_cap + profit - fee

            trades.append({
                "buy_date": buy_date,
                "sell_date": sell_date,
                "shares": round(shares, 4),
                "buy_price": None if buy_price is None or pd.isna(buy_price) else round(buy_price, 2),
                "sell_price": None if sell_price is None or pd.isna(sell_price) else round(sell_price, 2),
                "fee": round(fee, 2),
                "pnl": None if new_cap is None or prev_cap is None else round(new_cap - prev_cap, 2)
            })

            capital = new_cap
            position_active = False

    # Artificial close if still in a position
    if position_active and artificial_close_price is not None and artificial_close_date is not None:
        sell_price = artificial_close_price
        sell_date = pd.to_datetime(artificial_close_date).normalize()
        profit = (sell_price - buy_price) * shares if direction == "long" else (buy_price - sell_price) * shares
        turnover = shares * ((buy_price if buy_price is not None else 0) + (sell_price if sell_price is not None else 0))
        fee = max(min_commission, turnover * commission_rate)
        new_cap = prev_cap + profit - fee

        trades.append({
            "buy_date": buy_date,
            "sell_date": sell_date,
            "shares": round(shares, 4),
            "buy_price": None if buy_price is None or pd.isna(buy_price) else round(buy_price, 2),
            "sell_price": None if sell_price is None or pd.isna(sell_price) else round(sell_price, 2),
            "fee": round(fee, 2),
            "pnl": None if new_cap is None or prev_cap is None else round(new_cap - prev_cap, 2)
        })

        capital = new_cap

    return capital, trades

def assign_long_signals_extended(support, resistance, df, tw, interval):
    sig = assign_long_signals(support, resistance, df, tw, interval)
    sig = sig.rename(columns={
        "Date": "Date HL",
        "Level": "Level HL",
        "Type": "HL Type"
    })

    sig["Action"] = sig["Long"]
    sig["Detect Date"] = sig["Date HL"] + pd.Timedelta(days=tw)
    sig["Trade Day"] = sig["Detect Date"].apply(
        lambda d: d.normalize() + pd.Timedelta(hours=15, minutes=45)
        if pd.notna(d) else pd.NaT
    )
    sig["Close Level"] = np.nan

    return sig[[
        "Date HL", "Level HL", "HL Type", "Action",
        "Detect Date", "Trade Day", "Close Level"
    ]]

def calculate_shares(capital, price, round_factor=1):
    """
    Berechnet die Anzahl kaufbarer Einheiten für das gegebene Kapital und Rundung.
    """
    if price <= 0 or capital <= 0:
        return 0
    raw = capital / price
    return round(raw / round_factor) * round_factor


def update_level_close_long(ext, df):
    closes = []
    for _, row in ext.iterrows():
        dt = row["Detect Date"]
        if pd.isna(dt):
            closes.append(np.nan)
        else:
            dt0 = dt.normalize()
            try:
                val = df.at[dt0, "Close"]
                closes.append(float(val))
            except:
                closes.append(np.nan)
    ext["Close Level"] = closes
    return ext


def plot_combined_chart_and_equity(df, standard, _dummy, supp, res, trend,
                                   equity_long, _empty, buyhold, ticker):
    offset = 0.02 * (df["Close"].max() - df["Close"].min())
    buy_off = 2 * offset
    sell_off = -2 * offset

    # Marker vorbereiten
    buy_m = pd.Series(np.nan, index=df.index)
    sell_m = pd.Series(np.nan, index=df.index)

    for _, row in standard.iterrows():
        dt = row.get("Long Date")
        if row.get("Long") == "buy" and pd.notna(dt):
            try:
                px = df.at[dt.normalize(), "Close"]
                buy_m.at[dt.normalize()] = float(px) + buy_off
            except:
                pass
        elif row.get("Long") == "sell" and pd.notna(dt):
            try:
                px = df.at[dt.normalize(), "Close"]
                sell_m.at[dt.normalize()] = float(px) + sell_off
            except:
                pass

    # Equity- & Buy&Hold als Arrays
    eq = np.array([float(v) for v in equity_long], dtype=float)
    bh = np.array([float(v) for v in buyhold], dtype=float)
    dates = df.index
    opens = df["Open"].to_numpy(dtype=float)
    highs = df["High"].to_numpy(dtype=float)
    lows = df["Low"].to_numpy(dtype=float)
    closes = df["Close"].to_numpy(dtype=float)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                   sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})

    # Chart 1: Candlestick + Trend + Zonen
    for i, dt in enumerate(dates):
        color = "green" if closes[i] >= opens[i] else "red"
        ax1.plot([dt, dt], [lows[i], highs[i]], color="black", lw=0.5)
        ax1.bar(dt, closes[i] - opens[i], bottom=opens[i],
                color=color, width=0.6, alpha=0.7)

    ax1.plot(trend.index, trend.values, label="Trend", color="blue", lw=2)
    ax1.scatter(supp.index, supp.values, label="Support",
                color="limegreen", marker="o", s=60)
    ax1.scatter(res.index, res.values, label="Resistance",
                color="red", marker="x", s=60)
    ax1.scatter(buy_m.index, buy_m.values, label="Buy",
                color="blue", marker="^", s=80)
    ax1.scatter(sell_m.index, sell_m.values, label="Sell",
                color="orange", marker="v", s=80)

    ax1.set_title(f"{ticker} – Candlestick mit Signalen & Zonen")
    ax1.legend()
    ax1.grid(True)

    # Chart 2: Equity vs Buy&Hold
    ax2.plot(dates, eq, label="Strategie", color="blue")
    ax2.plot(dates, bh, label="Buy & Hold", color="gray", linestyle="--")
    ax2.set_title("Kapitalentwicklung")
    ax2.set_ylabel("Kapital (€)")
    ax2.legend()
    ax2.grid(True)

    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def berechne_best_p_tw_long(df, config, begin=0, end=100, verbose=True, ticker=None):
    """
    Optimiert die Parameter (past_window, trade_window) für Long-Trades
    innerhalb des definierten Zeitbereichs.

    Parameters:
    - df: DataFrame mit Preisdaten
    - config: Ticker-Konfiguration (Capital etc.)
    - begin: Start in Prozent (z. B. 25)
    - end: Ende in Prozent (z. B. 98)
    - verbose: Konsole-Ausgabe
    - ticker: Ticker-Name (für Print & CSV)

    Returns:
    - p: optimales vergangenes Fenster
    - tw: optimales Trade-Fenster
    """
    round_factor = config.get("order_round_factor", 1)
    commission_rate = 0.001
    min_commission = 1.0

    n = len(df)
    start_idx = int(n * begin / 100)
    end_idx = int(n * end / 100)
    df_opt = df.iloc[start_idx:end_idx].copy()

    optimierungsergebnisse = []

    for past_window in range(3, 10):
        for trade_window in range(1, 6):
            support, resistance = calculate_support_resistance(df_opt, past_window, trade_window)
            signal_df = assign_long_signals_extended(support, resistance, df_opt, trade_window, "1d")
            signal_df = update_level_close_long(signal_df, df_opt)

            final_capital, _ = simulate_trades_compound_extended(
                signal_df, df_opt, config,
                commission_rate=commission_rate,
                min_commission=min_commission,
                round_factor=round_factor,
                direction="long"
            )

            optimierungsergebnisse.append({
                "past_window": past_window,
                "trade_window": trade_window,
                "final_cap": final_capital
            })

    df_result = pd.DataFrame(optimierungsergebnisse).sort_values("final_cap", ascending=False)

    if verbose:
        label = ticker or "Unbekannter Ticker"
        print(f"\n📊 Optimierung Long für {label}")
        print(df_result.to_string(index=False))
        print(f"→ Beste Kombination: {df_result.iloc[0].to_dict()}")

    if ticker:
        df_result.to_csv(f"opt_long_{ticker}.csv", index=False)

    best_row = df_result.iloc[0]
    return int(best_row["past_window"]), int(best_row["trade_window"])
	