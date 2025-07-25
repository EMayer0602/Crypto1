import os
import io
import base64
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from datetime import date

# === Deine Coin-Konfigurationen ===
crypto_tickers = {
    "BTC-EUR": {"symbol": "BTC-EUR", "initialCapitalLong": 10000, "order_round_factor": 0.001},
    "ETH-EUR": {"symbol": "ETH-EUR", "initialCapitalLong": 10000, "order_round_factor": 0.001},
    "DOGE-EUR": {"symbol": "DOGE-EUR", "initialCapitalLong": 10000, "order_round_factor": 0.001},
    "SOL-EUR": {"symbol": "SOL-EUR", "initialCapitalLong": 10000, "order_round_factor": 0.001},
    "LINK-EUR": {"symbol": "LINK-EUR", "initialCapitalLong": 10000, "order_round_factor": 0.001},
    "XRP-EUR": {"symbol": "XRP-EUR", "initialCapitalLong": 10000, "order_round_factor": 0.001}
}

# === Dummy Strategie: Kapitalverlauf simulieren ===
def simulate_dummy_strategy(df, start_capital=10000):
    trades = []
    capital = start_capital
    eq_curve = []
    buyhold_curve = []

    if df.empty:
        return trades, capital, eq_curve, buyhold_curve

    prices = df["Close"].to_numpy()
    dates = df.index

    for i, price in enumerate(prices):
        if i % 30 == 0 and i + 5 < len(prices):
            buy_price = prices[i]
            sell_price = prices[i + 5]
            shares = capital * 0.1 / buy_price
            pnl = (sell_price - buy_price) * shares
            trades.append({
                "buy_date": str(dates[i].date()),
                "sell_date": str(dates[i + 5].date()),
                "buy_price": round(buy_price, 2),
                "sell_price": round(sell_price, 2),
                "shares": round(shares, 4),
                "pnl": round(pnl, 2)
            })
            capital += pnl

        eq_curve.append(capital)
        buyhold_curve.append(start_capital * (price / prices[0]))

    return trades, capital, eq_curve, buyhold_curve

# === Chart als Base64 erzeugen ===
def generate_chart_base64(eq_curve, bh_curve):
    plt.figure(figsize=(8, 3))
    plt.plot(eq_curve, label="Strategie", color="green")
    plt.plot(bh_curve, label="Buy & Hold", linestyle="--", color="gray")
    plt.title("Kapitalverlauf")
    plt.xlabel("Tage")
    plt.ylabel("Euro")
    plt.legend()
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img_data = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()
    plt.close()
    return img_data

# === Coin-Daten laden ===
def load_crypto_data(symbol, days=365):
    df = yf.download(symbol, period=f"{days}d", interval="1d", progress=False)
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.dropna(subset=["Close"])
    return df

# === Kombi-Report generieren ===
def generate_combined_html_report(report_data, filename):
    html = [
        "<html><head><title>Kombi-Strategiebericht</title><style>",
        "body{font-family:sans-serif;margin:40px;}",
        "table{border-collapse:collapse;width:100%} th,td{border:1px solid #ccc;padding:6px;text-align:center}",
        "details{margin-top:20px} summary{cursor:pointer;font-weight:bold;font-size:1.1em}",
        "</style></head><body>",
        f"<h1>📊 Strategiebericht für {date.today()}</h1>"
    ]

    summary = []

    for ticker, entry in report_data.items():
        trades = entry["trades"]
        plot = entry["plot"]
        capital = entry["capital"]
        start_capital = entry["start_capital"]

        html.append(f"<details><summary>{ticker}</summary>")
        html.append(f"<p><b>Endkapital:</b> {capital:,.2f} €</p>")
        html.append(f"<p><b>Buy & Hold:</b> {entry['bh_end']:,.2f} €</p>")

        if plot:
            html.append(f'<img src="data:image/png;base64,{plot}" width="700">')

        if trades:
            df = pd.DataFrame(trades)
            df["pnl_color"] = df["pnl"].apply(
                lambda x: f'<span style="color:{"green" if x > 0 else "red"}">{x:.2f}</span>'
            )
            html.append("<h3>📋 Trades</h3>")
            html.append(df[["buy_date", "buy_price", "sell_date", "sell_price", "shares", "pnl_color"]].to_html(index=False, escape=False))

            wins = sum(t["pnl"] > 0 for t in trades)
            losses = sum(t["pnl"] <= 0 for t in trades)
            hitrate = 100 * wins / max(len(trades), 1)
            total_pnl = sum(t["pnl"] for t in trades)
            volume = sum(t["sell_price"] * t["shares"] for t in trades)

            html.append("<h3>🎯 Statistik</h3>")
            html.append(f"""
            <ul>
                <li>Anzahl Trades: {len(trades)}</li>
                <li>Gewinn-Trades: {wins}</li>
                <li>Verlust-Trades: {losses}</li>
                <li>Trefferquote: {hitrate:.2f} %</li>
                <li>Gesamtgewinn: {total_pnl:,.2f} €</li>
                <li>Gesamtvolumen: {volume:,.2f} €</li>
            </ul>
            """)

            summary.append([ticker, len(trades), wins, losses, f"{hitrate:.2f}%", f"{total_pnl:,.2f} €"])
        else:
            html.append("<p><em>Keine Trades generiert.</em></p>")

        html.append("</details>")

    if summary:
        df_summary = pd.DataFrame(summary, columns=["Ticker", "Trades", "Wins", "Losses", "Hitrate", "Gesamt-PnL"])
        html.append("<h2>🧾 Gesamtvergleich</h2>")
        html.append(df_summary.to_html(index=False))

    html.append("</body></html>")
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/{filename}", "w", encoding="utf-8") as f:
        f.write("\n".join(html))

    print(f"\n[REPORT] ✅ Kombibericht gespeichert unter: reports/{filename}")

# === Hauptablauf ===
def main():
    report_data = {}

    for ticker, cfg in crypto_tickers.items():
        print(f"\n🚀 Backtest für {ticker}")
        df = load_crypto_data(cfg["symbol"])
        trades, final_capital, eq_curve, bh_curve = simulate_dummy_strategy(df, cfg["initialCapitalLong"])
        chart = generate_chart_base64(eq_curve, bh_curve) if eq_curve else ""

        print(f"• Endkapital: {final_capital:,.2f} €")
        print(f"• Trades: {len(trades)}")

        report_data[ticker] = {
            "trades": trades,
            "capital": final_capital,
            "start_capital": cfg["initialCapitalLong"],
            "bh_end": bh_curve[-1] if bh_curve else cfg["initialCapitalLong"],
            "plot": chart
        }

    generate_combined_html_report(report_data, f"COMBINED_STRATEGY_REPORT_{date.today()}.html")

if __name__ == "__main__":
    main()
