# report_generator.py

import os
import pandas as pd

def save_html_report(ticker, ext_signals, trades, final_capital, buyhold_capital, base64_plot=None, output_dir="reports"):
    import os
    import pandas as pd

    os.makedirs(output_dir, exist_ok=True)
    df_trades = pd.DataFrame(trades)
    ext_df = pd.DataFrame(ext_signals)

    # === Farbcodierung für PnL ===
    if not df_trades.empty:
        df_trades["pnl_color"] = df_trades["pnl"].apply(
            lambda x: f'<span style="color:{"green" if x > 0 else "red"}">{x:,.2f}</span>'
        )

    html = f"""<html>
    <head>
    <title>Strategiereport – {ticker}</title>
    <meta charset="UTF-8">
    <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
    th {{ background-color: #eee; }}
    tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
    </head><body>
    <h1>📊 Strategiereport für {ticker}</h1>
    <p><b>Strategie-Endkapital:</b> {final_capital:,.2f} €</p>
    <p><b>Buy & Hold:</b> {buyhold_capital:,.2f} €</p>
    <p><b>Anzahl Trades:</b> {len(trades)}</p>
    """

    if base64_plot:
        html += f'<h2>📈 Kapitalverlauf</h2><img src="data:image/png;base64,{base64_plot}" width="700">'

    if not df_trades.empty:
        html += "<h2>📋 Gematchte Trades</h2>"
        html += df_trades[["buy_date", "buy_price", "sell_date", "sell_price", "shares", "pnl_color"]].to_html(index=False, escape=False)

    html += "<h2>📊 Erweiterte Signale</h2>"
    html += ext_df.tail(20).to_html(index=False)

    html += f"<p style='font-size:0.9em;color:#888;'>Generiert am {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
    html += "</body></html>"

    path = os.path.join(output_dir, f"report_{ticker}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[REPORT] Einzelreport gespeichert: {path}")


def generate_combined_report(tickers, report_date, capital_plots):
    import pandas as pd
    import os
    from pathlib import Path

    report_html = ["<html><head><title>Combined Strategy Report</title><style>body{font-family:sans-serif} table{border-collapse:collapse;width:100%} th,td{border:1px solid #ccc;padding:6px;text-align:center}</style></head><body>"]
    report_html.append(f"<h1>📊 Strategiebericht für {report_date}</h1>")
#    if ticker in capital_plots:
#        report_html.append("<h3>📈 Kapitalverlauf</h3>")
#        report_html.append(f'<img src="data:image/png;base64,{capital_plots[ticker]}" width="700">')

    summary_rows = []

    for ticker in tickers:
        # === Lade gematchte Trades ===
        trades_path = f"trades_long_{ticker}.csv"
        extended_path = f"extended_long_signals_{ticker}.csv"

        if not Path(trades_path).exists() or not Path(extended_path).exists():
            report_html.append(f"<h2>{ticker}</h2><p><em>Keine Daten gefunden.</em></p>")
            continue

        trades = pd.read_csv(trades_path)
        ext_signals = pd.read_csv(extended_path)

        wins = sum(trades["pnl"] > 0)
        losses = sum(trades["pnl"] <= 0)
        total_pnl = trades["pnl"].sum()
        trade_value = trades["sell_price"].multiply(trades["shares"]).sum()
        hitrate = 100 * wins / max(len(trades), 1)

        # === Abschnitt für Coin ===
        report_html.append(f"<h2>{ticker}</h2>")
        report_html.append("<h3>📋 Gematchte Trades</h3>")
        report_html.append(trades[["buy_date", "buy_price", "sell_date", "sell_price", "shares", "pnl"]].to_html(index=False))

        report_html.append("<h3>📊 Extended Signals</h3>")
        report_html.append(ext_signals.tail(20).to_html(index=False))  # Nur die letzten 20 für Übersicht

        report_html.append("<h3>🎯 Statistik</h3>")
        report_html.append(f"""
        <ul>
            <li>Anzahl Trades: {len(trades)}</li>
            <li>Gewinn-Trades: {wins}</li>
            <li>Verlust-Trades: {losses}</li>
            <li>Trefferquote: {hitrate:.2f} %</li>
            <li>Gesamtgewinn: {total_pnl:,.2f} €</li>
            <li>Gesamtvolumen: {trade_value:,.2f} €</li>
        </ul>
        """)

        summary_rows.append([ticker, len(trades), wins, losses, f"{hitrate:.2f} %", f"{total_pnl:,.2f} €"])

    # === Gesamtvergleichstabelle ===
    report_html.append("<h2>🧾 Gesamtvergleich</h2>")
    summary_df = pd.DataFrame(summary_rows, columns=["Ticker", "Trades", "Wins", "Losses", "Hitrate", "Gesamt-PnL"])
    report_html.append(summary_df.to_html(index=False))

    report_html.append("</body></html>")
    if ticker in capital_plots:
        report_html.append("<h3>📈 Kapitalverlauf</h3>")
        report_html.append(f'<img src="data:image/png;base64,{capital_plots[ticker]}" width="700">')

    # === Speichern ===
    output_path = f"reports/COMBINED_STRATEGY_REPORT_{report_date}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_html))

    print(f"[REPORT] ✅ Kombinierter Bericht gespeichert: {output_path}")

def generate_combined_report_from_memory(report_data, report_date):
    import pandas as pd
    import os
    import webbrowser

    html = [
        "<html><head><title>Strategiebericht</title><style>",
        "body{font-family:sans-serif;margin:40px;}",
        "table{border-collapse:collapse;width:100%} th, td{border:1px solid #ccc;padding:6px;text-align:center}",
        "details{margin-top:20px} summary{cursor:pointer;font-weight:bold;font-size:1.1em}",
        "</style></head><body>",
        f"<h1>📊 Strategiebericht für {report_date}</h1>"
    ]

    summary_rows = []

    for ticker, entry in report_data.items():
        trades         = pd.DataFrame(entry.get("trades", []))
        ext_signals    = pd.DataFrame(entry.get("ext_signals", []))
        capital        = entry.get("capital", 0)
        opt_p          = entry.get("opt_p", "-")
        opt_tw         = entry.get("opt_tw", "-")
        chart_img      = entry.get("chart_img_base64", "")
        roi            = entry.get("roi", "")

        html.append(f"<details><summary>{ticker}</summary>")
        html.append(f"<p><b>Endkapital:</b> {capital:,.2f} €</p>")
        html.append(f"<p><b>Optimale Parameter:</b> p = {opt_p}, tw = {opt_tw}</p>")
        html.append(f"<p><b>ROI:</b> {roi}</p>")

        if chart_img:
            html.append('<h3>📈 Kapitalverlauf</h3>')
            html.append(f'<img src="data:image/png;base64,{chart_img}" width="800">')

        if not trades.empty:
            trades["pnl_color"] = trades["pnl"].apply(
                lambda x: f'<span style="color:{"green" if x > 0 else "red"}">{x:,.2f}</span>'
            )
            html.append("<h3>📋 Gematchte Trades</h3>")
            html.append(trades[["buy_date", "buy_price", "sell_date", "sell_price", "shares", "pnl_color"]].to_html(index=False, escape=False))

            wins = sum(trades["pnl"] > 0)
            losses = sum(trades["pnl"] <= 0)
            total_pnl = trades["pnl"].sum()
            volume = trades["sell_price"].multiply(trades["shares"]).sum()
            hitrate = 100 * wins / max(len(trades), 1)

            html.append("<h3>📊 Statistik</h3>")
            html.append(f"<ul><li>Trades: {len(trades)}</li><li>Gewinne: {wins}</li><li>Verluste: {losses}</li><li>Trefferquote: {hitrate:.2f}%</li><li>Gewinn: {total_pnl:,.2f} €</li><li>Volumen: {volume:,.2f} €</li></ul>")
            summary_rows.append([ticker, len(trades), wins, losses, f"{hitrate:.2f} %", f"{total_pnl:,.2f} €", roi])
        else:
            html.append("<p><em>Keine Trades vorhanden.</em></p>")

        if not ext_signals.empty:
            html.append("<h3>📍 Erweiterte Signale</h3>")
            html.append(ext_signals.to_html(index=False))
        else:
            html.append("<p><em>Keine erweiterten Signale.</em></p>")

        html.append("</details>")

    if summary_rows:
        df_summary = pd.DataFrame(summary_rows, columns=["Ticker", "Trades", "Wins", "Losses", "Hitrate", "Gesamt-PnL", "ROI"])
        html.append("<h2>📈 Gesamtvergleich</h2>")
        html.append(df_summary.to_html(index=False))

    html.append("</body></html>")
    os.makedirs("reports", exist_ok=True)
    output_path = f"reports/COMBINED_STRATEGY_REPORT_{report_date}.html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(html))

    print(f"[REPORT] ✅ Kombibericht gespeichert unter: {output_path}")
    webbrowser.open(f"file://{os.path.abspath(output_path)}")
