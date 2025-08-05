import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def plot_crypto_backtest(df, signals, trades, symbol):
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Candlestick-artiger Plot
    df = df.sort_index()
    width = 0.6
    for i in range(len(df)):
        color = 'green' if df["Close"].iloc[i] >= df["Open"].iloc[i] else 'red'
        ax1.plot([df.index[i], df.index[i]], [df["Low"].iloc[i], df["High"].iloc[i]], color='black', linewidth=0.5)
        ax1.bar(df.index[i], df["Close"].iloc[i] - df["Open"].iloc[i],
                bottom=df["Open"].iloc[i], color=color, width=width, alpha=0.8)

    # Support/Resistance
    def calculate_support_resistance(df, window=5, prominence=1):
        # Simple support/resistance calculation using rolling min/max
        support = df['Low'].rolling(window=window, center=True).min()
        resistance = df['High'].rolling(window=window, center=True).max()
        # Filter to only keep local minima/maxima as support/resistance
        support_points = support[(df['Low'] == support) & (support.notna())]
        resistance_points = resistance[(df['High'] == resistance) & (resistance.notna())]
        return support_points, resistance_points

    supp, res = calculate_support_resistance(df, 5, 1)
    ax1.scatter(supp.index, supp.values, label="Support", color="limegreen", s=80, marker="o")
    ax1.scatter(res.index, res.values, label="Resistance", color="red", s=80, marker="x")

    # Long-Signale
    for _, row in signals.iterrows():
        if row["Long"] == "buy" and pd.notna(row["Long Date"]):
            ax1.scatter(row["Long Date"], df.loc[row["Long Date"], "Close"] * 1.01, color="blue", marker="^", s=100, label="BUY")
        elif row["Long"] == "sell" and pd.notna(row["Long Date"]):
            ax1.scatter(row["Long Date"], df.loc[row["Long Date"], "Close"] * 0.99, color="orange", marker="v", s=100, label="SELL")

    ax1.set_title(f"Trading-Backtest für {symbol}")
    ax1.set_xlabel("Datum")
    ax1.set_ylabel("Kurs (EUR)")
    ax1.grid(True)
    ax1.legend()

    # X-Achse Formatierung
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
