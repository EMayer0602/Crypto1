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

def generate_combined_report(tickers, report_date, capital_plots=None):
    """
    Generiert kombinierten HTML-Report basierend auf Extended Signals (nicht gematchte Trades)
    """
    import pandas as pd
    import os
    from pathlib import Path

    if capital_plots is None:
        capital_plots = {}

    report_html = [
        "<html><head><title>Combined Strategy Report</title>",
        "<style>",
        "body{font-family:Arial,sans-serif; margin:20px; background:#f5f5f5}",
        "h1{color:#2c3e50; text-align:center}",
        "h2{color:#34495e; border-bottom:2px solid #3498db; padding-bottom:5px}",
        "h3{color:#27ae60}",
        "table{border-collapse:collapse; width:100%; margin:10px 0; background:white}",
        "th{background:#3498db; color:white; padding:10px; text-align:center}",
        "td{border:1px solid #bdc3c7; padding:8px; text-align:center}",
        "tr:nth-child(even){background:#ecf0f1}",
        ".stats{background:#fff; padding:15px; border-radius:5px; margin:10px 0}",
        ".positive{color:#27ae60; font-weight:bold}",
        ".negative{color:#e74c3c; font-weight:bold}",
        "</style></head><body>"
    ]
    
    report_html.append(f"<h1>📊 Extended Trading Strategy Report - {report_date}</h1>")
    
    summary_rows = []
    total_signals = 0
    total_buy_signals = 0
    total_sell_signals = 0

    for ticker in tickers:
        # === LADE EXTENDED SIGNALS (NICHT TRADES) ===
        extended_path = f"extended_long_signals_{ticker}.csv"
        
        if not Path(extended_path).exists():
            report_html.append(f"<h2>❌ {ticker}</h2>")
            report_html.append(f"<p><em>Keine Extended Signals gefunden: {extended_path}</em></p>")
            continue

        try:
            ext_signals = pd.read_csv(extended_path)
            
            if ext_signals.empty:
                report_html.append(f"<h2>⚠️ {ticker}</h2>")
                report_html.append(f"<p><em>Extended Signals Datei ist leer.</em></p>")
                continue

            # === SIGNAL STATISTIKEN ===
            buy_signals = ext_signals[ext_signals['Action'] == 'buy'] if 'Action' in ext_signals.columns else pd.DataFrame()
            sell_signals = ext_signals[ext_signals['Action'] == 'sell'] if 'Action' in ext_signals.columns else pd.DataFrame()
            support_levels = ext_signals[ext_signals['Supp/Resist'] == 'support'] if 'Supp/Resist' in ext_signals.columns else pd.DataFrame()
            resistance_levels = ext_signals[ext_signals['Supp/Resist'] == 'resistance'] if 'Supp/Resist' in ext_signals.columns else pd.DataFrame()
            
            # === ABSCHNITT FÜR COIN ===
            report_html.append(f"<h2>💰 {ticker}</h2>")
            
            # === SIGNAL ÜBERSICHT ===
            report_html.append("<div class='stats'>")
            report_html.append("<h3>📊 Signal Statistiken</h3>")
            report_html.append(f"""
            <ul>
                <li>📈 <strong>Gesamt Signale:</strong> {len(ext_signals)}</li>
                <li>🔵 <strong>Buy Signale:</strong> <span class="positive">{len(buy_signals)}</span></li>
                <li>🟠 <strong>Sell Signale:</strong> <span class="negative">{len(sell_signals)}</span></li>
                <li>🟢 <strong>Support Levels:</strong> {len(support_levels)}</li>
                <li>🔴 <strong>Resistance Levels:</strong> {len(resistance_levels)}</li>
            </ul>
            """)
            report_html.append("</div>")
            
            # === LETZTE SIGNALE TABELLE ===
            report_html.append("<h3>� Letzte 15 Extended Signals</h3>")
            recent_signals = ext_signals.tail(15)
            
            # Formatiere die Tabelle für bessere Lesbarkeit
            if not recent_signals.empty:
                # Wähle wichtige Spalten aus
                display_columns = []
                for col in ['Long Date detected', 'Action', 'Supp/Resist', 'Level high/low', 'Date high/low', 'Close']:
                    if col in recent_signals.columns:
                        display_columns.append(col)
                
                if display_columns:
                    display_df = recent_signals[display_columns].copy()
                    
                    # Formatiere Zahlen
                    for col in display_df.columns:
                        if display_df[col].dtype in ['float64', 'float32']:
                            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                    
                    report_html.append(display_df.to_html(index=False, escape=False))
                else:
                    report_html.append(recent_signals.to_html(index=False))
            else:
                report_html.append("<p><em>Keine aktuellen Signale verfügbar.</em></p>")
            
            # === CAPITAL PLOT (FALLS VERFÜGBAR) ===
            if ticker in capital_plots:
                report_html.append("<h3>📈 Kapitalverlauf</h3>")
                report_html.append(f'<img src="data:image/png;base64,{capital_plots[ticker]}" width="700" style="border:1px solid #bdc3c7">')
            
            # === SUMMARY ROW ===
            summary_rows.append([
                ticker, 
                len(ext_signals),
                len(buy_signals), 
                len(sell_signals),
                len(support_levels),
                len(resistance_levels)
            ])
            
            # Update totals
            total_signals += len(ext_signals)
            total_buy_signals += len(buy_signals)
            total_sell_signals += len(sell_signals)
            
        except Exception as e:
            report_html.append(f"<h2>❌ {ticker}</h2>")
            report_html.append(f"<p><em>Fehler beim Laden der Daten: {str(e)}</em></p>")
            continue

    # === GESAMTVERGLEICHSTABELLE ===
    if summary_rows:
        report_html.append("<h2>🧾 Signal Übersicht - Alle Coins</h2>")
        summary_df = pd.DataFrame(summary_rows, columns=[
            "Ticker", 
            "Total Signals", 
            "Buy Signals", 
            "Sell Signals",
            "Support Levels",
            "Resistance Levels"
        ])
        report_html.append(summary_df.to_html(index=False, escape=False))
        
        # === GESAMT STATISTIKEN ===
        report_html.append("<div class='stats'>")
        report_html.append("<h3>🎯 Portfolio Gesamt-Statistiken</h3>")
        report_html.append(f"""
        <ul>
            <li><strong>Analysierte Coins:</strong> {len(tickers)}</li>
            <li><strong>Erfolgreiche Analysen:</strong> {len(summary_rows)}</li>
            <li><strong>Gesamt Signale:</strong> <span class="positive">{total_signals}</span></li>
            <li><strong>Gesamt Buy Signale:</strong> <span class="positive">{total_buy_signals}</span></li>
            <li><strong>Gesamt Sell Signale:</strong> <span class="negative">{total_sell_signals}</span></li>
        </ul>
        """)
        report_html.append("</div>")
    else:
        report_html.append("<h2>⚠️ Keine Daten verfügbar</h2>")
        report_html.append("<p>Keine Extended Signals für die analysierten Tickers gefunden.</p>")

    # === FOOTER ===
    report_html.append(f"<hr><p style='text-align:center; color:#7f8c8d; font-size:12px'>")
    report_html.append(f"Generiert am {report_date} | Crypto Trading Strategy Analysis</p>")
    report_html.append("</body></html>")

    # === SPEICHERN ===
    os.makedirs("reports", exist_ok=True)
    output_path = f"reports/EXTENDED_SIGNALS_REPORT_{report_date}.html"
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_html))
        
        print(f"✅ Extended Signals Report gespeichert: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Fehler beim Speichern des Reports: {e}")
        return None

def generate_combined_report_from_memory(all_results, portfolio_csv_path=None):
    """
    Generiert HTML-Report direkt aus den Backtest-Ergebnissen im Speicher
    """
    from datetime import datetime
    import os
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report_html = [
        "<html><head><title>Crypto Trading Strategy Report</title>",
        "<style>",
        "body{font-family:Arial,sans-serif; margin:20px; background:#f5f5f5}",
        "h1{color:#2c3e50; text-align:center; background:linear-gradient(45deg,#3498db,#2ecc71); color:white; padding:20px; border-radius:10px}",
        "h2{color:#34495e; border-bottom:2px solid #3498db; padding-bottom:5px}",
        "h3{color:#27ae60; background:#ecf0f1; padding:10px; border-radius:5px}",
        "table{border-collapse:collapse; width:100%; margin:10px 0; background:white; box-shadow:0 2px 5px rgba(0,0,0,0.1)}",
        "th{background:#3498db; color:white; padding:12px; text-align:center; font-weight:bold}",
        "td{border:1px solid #bdc3c7; padding:10px; text-align:center}",
        "tr:nth-child(even){background:#ecf0f1}",
        "tr:hover{background:#d5dbdb}",
        ".stats{background:#fff; padding:20px; border-radius:10px; margin:15px 0; box-shadow:0 2px 5px rgba(0,0,0,0.1)}",
        ".positive{color:#27ae60; font-weight:bold}",
        ".negative{color:#e74c3c; font-weight:bold}",
        ".neutral{color:#f39c12; font-weight:bold}",
        ".signal-box{display:inline-block; margin:5px; padding:8px 12px; border-radius:20px; color:white; font-size:12px}",
        ".buy-signal{background:#3498db}",
        ".sell-signal{background:#e74c3c}",
        ".support-signal{background:#27ae60}",
        ".resistance-signal{background:#e67e22}",
        "</style></head><body>"
    ]
    
    report_html.append(f"<h1>� Crypto Trading Strategy Report</h1>")
    report_html.append(f"<p style='text-align:center; font-size:18px; color:#7f8c8d'>Generated: {timestamp}</p>")
    
    # === PORTFOLIO ÜBERSICHT ===
    report_html.append("<div class='stats'>")
    report_html.append("<h2>💼 Portfolio Overview</h2>")
    
    total_symbols = len(all_results)
    successful_analyses = sum(1 for result in all_results.values() if isinstance(result, dict))
    
    report_html.append(f"""
    <ul style='font-size:16px'>
        <li><strong>📊 Analyzed Symbols:</strong> <span class="positive">{total_symbols}</span></li>
        <li><strong>✅ Successful Analyses:</strong> <span class="positive">{successful_analyses}</span></li>
        <li><strong>📅 Analysis Period:</strong> Multi-year backtest</li>
        <li><strong>💰 Initial Capital per Symbol:</strong> €10,000</li>
    </ul>
    """)
    report_html.append("</div>")
    
    # === INDIVIDUAL SYMBOL ANALYSIS ===
    summary_rows = []
    
    for symbol, result in all_results.items():
        if not isinstance(result, dict):
            continue
            
        report_html.append(f"<h2>💰 {symbol}</h2>")
        
        # === EXTENDED SIGNALS ANALYSIS ===
        ext_signals = result.get('ext_signals', pd.DataFrame())
        matched_trades = result.get('matched_trades', pd.DataFrame())
        
        if not ext_signals.empty:
            # Signal Counts
            buy_signals = ext_signals[ext_signals['Action'] == 'buy'] if 'Action' in ext_signals.columns else pd.DataFrame()
            sell_signals = ext_signals[ext_signals['Action'] == 'sell'] if 'Action' in ext_signals.columns else pd.DataFrame()
            support_levels = ext_signals[ext_signals['Supp/Resist'] == 'support'] if 'Supp/Resist' in ext_signals.columns else pd.DataFrame()
            resistance_levels = ext_signals[ext_signals['Supp/Resist'] == 'resistance'] if 'Supp/Resist' in ext_signals.columns else pd.DataFrame()
            
            report_html.append("<div class='stats'>")
            report_html.append("<h3>📊 Signal Analysis</h3>")
            
            # Signal Badges
            report_html.append("<div style='margin:10px 0'>")
            report_html.append(f"<span class='signal-box buy-signal'>🔵 {len(buy_signals)} BUY Signals</span>")
            report_html.append(f"<span class='signal-box sell-signal'>🟠 {len(sell_signals)} SELL Signals</span>")
            report_html.append(f"<span class='signal-box support-signal'>🟢 {len(support_levels)} Support Levels</span>")
            report_html.append(f"<span class='signal-box resistance-signal'>🔴 {len(resistance_levels)} Resistance Levels</span>")
            report_html.append("</div>")
            
            # Latest Signals Table
            report_html.append("<h4>� Latest 10 Extended Signals</h4>")
            recent_signals = ext_signals.tail(10)
            
            if not recent_signals.empty:
                # Format the signals table nicely
                display_columns = []
                for col in ['Long Date detected', 'Action', 'Supp/Resist', 'Level high/low', 'Long Signal Extended']:
                    if col in recent_signals.columns:
                        display_columns.append(col)
                
                if display_columns:
                    display_df = recent_signals[display_columns].copy()
                    
                    # Format numbers
                    if 'Level high/low' in display_df.columns:
                        display_df['Level high/low'] = display_df['Level high/low'].apply(
                            lambda x: f"€{x:,.2f}" if pd.notna(x) else ""
                        )
                    
                    report_html.append(display_df.to_html(index=False, escape=False))
                else:
                    report_html.append(recent_signals.to_html(index=False))
            
            report_html.append("</div>")
        
        # === MATCHED TRADES ANALYSIS ===
        if not matched_trades.empty:
            report_html.append("<div class='stats'>")
            report_html.append("<h3>💼 Trading Performance</h3>")
            
            # Calculate trade statistics
            total_trades = len(matched_trades)
            if 'PnL' in matched_trades.columns:
                profitable_trades = sum(matched_trades['PnL'] > 0)
                losing_trades = sum(matched_trades['PnL'] <= 0)
                total_pnl = matched_trades['PnL'].sum()
                avg_pnl = matched_trades['PnL'].mean()
                win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
                
                pnl_class = "positive" if total_pnl > 0 else "negative" if total_pnl < 0 else "neutral"
                
                report_html.append(f"""
                <ul style='font-size:14px'>
                    <li><strong>📊 Total Trades:</strong> {total_trades}</li>
                    <li><strong>✅ Winning Trades:</strong> <span class="positive">{profitable_trades}</span></li>
                    <li><strong>❌ Losing Trades:</strong> <span class="negative">{losing_trades}</span></li>
                    <li><strong>🎯 Win Rate:</strong> <span class="{pnl_class}">{win_rate:.1f}%</span></li>
                    <li><strong>💰 Total P&L:</strong> <span class="{pnl_class}">€{total_pnl:,.2f}</span></li>
                    <li><strong>📈 Average P&L per Trade:</strong> <span class="{pnl_class}">€{avg_pnl:.2f}</span></li>
                </ul>
                """)
                
                # Recent Trades Table
                report_html.append("<h4>📋 Latest 5 Trades</h4>")
                recent_trades = matched_trades.tail(5)
                
                trade_columns = []
                for col in ['Entry Date', 'Entry Price', 'Exit Date', 'Exit Price', 'Shares', 'PnL']:
                    if col in recent_trades.columns:
                        trade_columns.append(col)
                
                if trade_columns:
                    display_trades = recent_trades[trade_columns].copy()
                    
                    # Format numbers
                    for col in ['Entry Price', 'Exit Price']:
                        if col in display_trades.columns:
                            display_trades[col] = display_trades[col].apply(lambda x: f"€{x:.2f}" if pd.notna(x) else "")
                    
                    if 'PnL' in display_trades.columns:
                        display_trades['PnL'] = display_trades['PnL'].apply(lambda x: f"€{x:,.2f}" if pd.notna(x) else "")
                    
                    if 'Shares' in display_trades.columns:
                        display_trades['Shares'] = display_trades['Shares'].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
                    
                    report_html.append(display_trades.to_html(index=False, escape=False))
                
            report_html.append("</div>")
        
        # === DATASET INFO ===
        dataset_info = result.get('dataset_info', {})
        if dataset_info:
            report_html.append("<div class='stats'>")
            report_html.append("<h3>� Dataset Information</h3>")
            report_html.append(f"""
            <ul style='font-size:14px'>
                <li><strong>Period:</strong> {dataset_info.get('start_date', 'N/A')} to {dataset_info.get('end_date', 'N/A')}</li>
                <li><strong>Total Days:</strong> {dataset_info.get('total_days', 'N/A')}</li>
                <li><strong>Data Points:</strong> {dataset_info.get('data_points', 'N/A')}</li>
            </ul>
            """)
            report_html.append("</div>")
        
        # Add to summary
        signal_count = len(ext_signals) if not ext_signals.empty else 0
        trade_count = len(matched_trades) if not matched_trades.empty else 0
        pnl_total = matched_trades['PnL'].sum() if not matched_trades.empty and 'PnL' in matched_trades.columns else 0
        
        summary_rows.append([
            symbol,
            signal_count,
            len(buy_signals) if 'buy_signals' in locals() else 0,
            len(sell_signals) if 'sell_signals' in locals() else 0,
            trade_count,
            f"€{pnl_total:,.2f}" if trade_count > 0 else "€0.00"
        ])
    
    # === SUMMARY TABLE ===
    if summary_rows:
        report_html.append("<h2>🧾 Summary Table</h2>")
        summary_df = pd.DataFrame(summary_rows, columns=[
            "Symbol", 
            "Total Signals", 
            "Buy Signals", 
            "Sell Signals",
            "Executed Trades",
            "Total P&L"
        ])
        report_html.append(summary_df.to_html(index=False, escape=False))
    
    # === FOOTER ===
    report_html.append(f"""
    <hr style='margin:30px 0'>
    <div style='text-align:center; color:#7f8c8d; font-size:12px; padding:20px'>
        <p>📊 <strong>Crypto Trading Strategy Analysis Report</strong></p>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
           🚀 Enhanced Backtesting System | 
           💼 Paper Trading Mode</p>
    </div>
    """)
    
    report_html.append("</body></html>")
    
    # === SAVE REPORT ===
    os.makedirs("reports", exist_ok=True)
    output_path = f"reports/CRYPTO_STRATEGY_REPORT_{timestamp}.html"
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_html))
        
        print(f"✅ Comprehensive Report saved: {output_path}")
        
        # Open in browser
        import webbrowser
        abs_path = os.path.abspath(output_path)
        webbrowser.open(f"file://{abs_path}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error saving report: {e}")
        return None
