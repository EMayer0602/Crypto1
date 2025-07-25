# plotly_utils.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import base64
import os
import webbrowser

def plotly_combined_chart_and_equity(
    df,
    standard_signals,
    support,
    resistance,
    equity_curve,
    buyhold_curve,
    ticker
):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
    import base64
    import os
    import webbrowser

    trend = df["Close"].rolling(window=20).mean()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name="Candlestick"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=trend.index, y=trend,
        mode="lines", name="Trend", line=dict(color="blue", width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=support.index, y=support,
        mode="markers", name="Support", marker=dict(color="green", size=6)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=resistance.index, y=resistance,
        mode="markers", name="Resistance", marker=dict(color="red", size=6, symbol="x")
    ), row=1, col=1)

    action_col = next((col for col in ["Long", "Action", "Long Action"] if col in standard_signals.columns), None)
    date_col = next((col for col in ["Long Date", "Detect Date", "Trade Day"] if col in standard_signals.columns), None)

    if action_col and date_col:
        buys = standard_signals[standard_signals[action_col].str.lower() == "buy"]
        sells = standard_signals[standard_signals[action_col].str.lower() == "sell"]

        if not buys.empty:
            fig.add_trace(go.Scatter(x=buys[date_col],
                y=df.loc[buys[date_col], "Close"], mode="markers",
                name="Buy", marker=dict(color="blue", symbol="triangle-up", size=10)
            ), row=1, col=1)

        if not sells.empty:
            fig.add_trace(go.Scatter(x=sells[date_col],
                y=df.loc[sells[date_col], "Close"], mode="markers",
                name="Sell", marker=dict(color="orange", symbol="triangle-down", size=10)
            ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=equity_curve,
        mode="lines", name="Strategie", line=dict(color="green", width=2)
    ), row=2, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=buyhold_curve,
        mode="lines", name="Buy & Hold", line=dict(color="gray", dash="dash", width=2)
    ), row=2, col=1)

    fig.update_layout(
        title=f"{ticker} – Strategie & Kapitalverlauf",
        template="plotly_white",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=-0.25),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    fig.update_yaxes(title_text="Kurs (EUR)", row=1, col=1)
    fig.update_yaxes(title_text="Kapital (€)", row=2, col=1)

    os.makedirs("reports", exist_ok=True)
    html_path = f"reports/chart_{ticker}.html"
    pio.write_html(fig, file=html_path, auto_open=False)
    webbrowser.open(f"file://{os.path.abspath(html_path)}")

    img_bytes = pio.to_image(fig, format="png", width=900, height=400)
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return img_base64
