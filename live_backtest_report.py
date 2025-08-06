#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 LIVE BACKTEST REPORT - Direkt aus Backtest-Results (KEIN Merge alter HTML-Dateien!)
Führt Backtests aus und erstellt SOFORT einen aktuellen Report mit den ECHTEN Daten!
"""

import os
import sys
import webbrowser
from datetime import datetime, timedelta
import pandas as pd

# Import unserer Module
sys.path.append(os.path.dirdef main():
    """Main function"""
    try:
        print("LIVE BACKTEST REPORT - Keine alten HTML-Dateien mehr!")
        print("Fuehre AKTUELLE Backtests durch und erstelle SOFORT einen Report!")
        print("=" * 80)s.path.abspath(__file__)))
from crypto_backtesting_module import run_backtest
import crypto_tickers

def run_live_backtests():
    """Führt LIVE Backtests für alle Tickers aus und sammelt Results"""
    
    print("LIVE BACKTEST REPORT - Fuehre aktuelle Backtests durch...")
    print("=" * 80)
    
    tickers = list(crypto_tickers.crypto_tickers.keys())
    all_results = []
    summary_data = []
    all_trades_14_days = []  # ALLE Trades der letzten 14 Tage für ALLE Ticker
    
    # Basis-Config
    base_config = {
        'timeframe': 'daily',
        'lookback_period': 5,
        'csv_path': './',
        'commission_rate': 0.0018,
        'min_commission': 1.0,
        'order_round_factor': 0.01
    }
    
    for ticker in tickers:
        print(f"\nLIVE BACKTEST fuer {ticker}...")
        
        # Hole ticker-spezifische Config (wie repariert)
        ticker_config = crypto_tickers.crypto_tickers.get(ticker, {})
        trade_on = ticker_config.get('trade_on', 'Close')
        
        print(f"   Trade-Ausfuehrung: {trade_on}")
        print(f"   Initial Capital: {ticker_config.get('initialCapitalLong', 10000)} EUR")
        print(f"   Order Round Factor: {ticker_config.get('order_round_factor', 0.01)}")
        
        # Update config mit ticker-spezifischen Einstellungen
        config = base_config.copy()
        config['trade_on'] = trade_on
        config['initial_capital'] = ticker_config.get('initialCapitalLong', 10000)
        config['order_round_factor'] = ticker_config.get('order_round_factor', 0.01)
        
        # Prüfe CSV-Datei
        csv_file = f"{ticker}_daily.csv"
        if not os.path.exists(csv_file):
            print(f"⚠️ CSV nicht gefunden: {csv_file}")
            continue
            
        try:
            # 🎯 FÜHRE AKTUELLEN BACKTEST AUS!
            result = run_backtest(ticker, config)
            
            if result and not result.get('Error'):
                # Sammle Results
                all_results.append({
                    'ticker': ticker,
                    'result': result,
                    'config': config
                })
                
                # 🎯 HOLE ECHTE TRADES aus dem Backtest-Result
                print(f"   🔍 DEBUG: Verfügbare Keys in result: {list(result.keys())}")
                
                actual_trades = []
                
                # 1. Weekly trades (letzte 14 Tage) - HAUPTQUELLE
                weekly_trades = result.get('weekly_trades_data', [])
                print(f"   📊 Weekly trades gefunden: {len(weekly_trades)}")
                
                for trade in weekly_trades:
                    # WICHTIG: weekly_trades haben 'Action' (groß), nicht 'action' (klein)!
                    action = trade.get('Action', '')
                    if action in ['BUY', 'SELL']:
                        print(f"   🔸 Trade: {action} am {trade.get('Date')}")
                        trade['ticker'] = ticker
                        trade['config'] = config
                        actual_trades.append(trade)
                        all_trades_14_days.append(trade)
                    else:
                        print(f"   ⏸️ Skipped: {action} am {trade.get('Date', 'N/A')}")
                
                # 2. Matched trades (falls weekly_trades leer)
                if not weekly_trades:
                    matched_trades = result.get('matched_trades', [])
                    print(f"   📊 Matched trades gefunden: {len(matched_trades)}")
                    
                    for trade in matched_trades:
                        trade['ticker'] = ticker
                        trade['config'] = config
                        actual_trades.append(trade)
                        all_trades_14_days.append(trade)
                
                # 🎯 Berechne ECHTE PnL aus allen Trades
                total_pnl = 0
                for trade in actual_trades:
                    pnl = trade.get('pnl', 0)
                    if isinstance(pnl, (int, float)):
                        total_pnl += pnl
                
                # Summary für Tabelle
                summary_data.append({
                    'Symbol': ticker,
                    'Optimal_Past_Window': result.get('optimal_past_window', 'N/A'),
                    'Optimal_Trade_Window': result.get('optimal_trade_window', 'N/A'),
                    'Optimal_PnL': result.get('optimal_pnl', total_pnl),  # 🎯 Echte PnL aus Backtest
                    'Calculated_PnL': total_pnl,  # 🎯 Berechnete PnL aus Trades
                    'Weekly_Trades': result.get('weekly_trades_count', len(weekly_trades)),
                    'Total_Trades': len(actual_trades),
                    'Initial_Capital': config['initial_capital'],
                    'Trade_On': trade_on,
                    'Order_Round_Factor': config['order_round_factor']
                })
                
                print(f"   Optimal: p={result.get('optimal_past_window')}, tw={result.get('optimal_trade_window')}")
                print(f"   Backtest PnL: {result.get('optimal_pnl', 0):.2f} EUR")
                print(f"   Calculated PnL: {total_pnl:.2f} EUR")
                print(f"   Trades (2 Wochen): {result.get('weekly_trades_count', 0)}")
                print(f"   Total Trades gefunden: {len(actual_trades)}")
                
            else:
                print(f"   Backtest fehlgeschlagen: {result.get('Error', 'Unbekannter Fehler')}")
                
        except Exception as e:
            print(f"   Fehler: {e}")
    
    print(f"\nGESAMT: {len(all_trades_14_days)} Trades der letzten 14 Tage gefunden!")
    return all_results, summary_data, all_trades_14_days

def generate_live_html_report(all_results, summary_data, all_trades_14_days):
    """Erstellt HTML-Report DIREKT aus Live-Backtest Results"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"LIVE_backtest_report_{timestamp}.html"
    
    # Cutoff-Datum (vor 2 Wochen)
    cutoff_date = datetime.now() - timedelta(days=14)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')
    
    html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 LIVE Crypto Backtest Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1600px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        h1 {{ margin: 0; font-size: 2.5em; font-weight: 300; }}
        h2 {{ color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-top: 30px; }}
        .summary-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .summary-table th {{ background: #667eea; color: white; padding: 15px; text-align: left; font-size: 0.9em; }}
        .summary-table td {{ padding: 12px 15px; border-bottom: 1px solid #ddd; }}
        .summary-table tr:nth-child(even) {{ background: #f8f9fa; }}
        .summary-table tr:hover {{ background: #e3f2fd; }}
        .positive {{ color: #27ae60; font-weight: bold; }}
        .negative {{ color: #e74c3c; font-weight: bold; }}
        .trade-section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; }}
        .trade-table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        .trade-table th {{ background: #34495e; color: white; padding: 10px; text-align: left; font-size: 0.8em; }}
        .trade-table td {{ padding: 8px 10px; border-bottom: 1px solid #ddd; font-size: 0.8em; }}
        .ticker-header {{ background: #3498db; color: white; padding: 15px; margin: 20px 0; border-radius: 8px; }}
        .timestamp {{ text-align: center; margin: 20px 0; color: #7f8c8d; font-style: italic; }}
        .pnl-comparison {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 LIVE Crypto Backtest Report</h1>
            <p>Erstellt: {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}</p>
            <p>📅 Trades der letzten 14 Tage (seit {cutoff_str})</p>
            <p>🎯 Alle Daten LIVE aus aktuellen Backtest-Results</p>
        </div>
        
        <div class="content">
            <h2>📊 Optimierungsparameter & PnL Summary</h2>
            <table class="summary-table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Past Window</th>
                        <th>Trade Window</th>
                        <th>Backtest PnL</th>
                        <th>Calculated PnL</th>
                        <th>Trades (14T)</th>
                        <th>Capital</th>
                        <th>Trade On</th>
                        <th>Round Factor</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Summary-Tabelle mit PnL-Vergleich
    total_backtest_pnl = 0
    total_calculated_pnl = 0
    total_trades = 0
    
    for row in summary_data:
        backtest_pnl = row['Optimal_PnL']
        calculated_pnl = row['Calculated_PnL']
        total_backtest_pnl += backtest_pnl
        total_calculated_pnl += calculated_pnl
        total_trades += row['Weekly_Trades']
        
        backtest_class = 'positive' if backtest_pnl > 0 else 'negative' if backtest_pnl < 0 else ''
        calculated_class = 'positive' if calculated_pnl > 0 else 'negative' if calculated_pnl < 0 else ''
        
        html_content += f"""
                    <tr>
                        <td><strong>{row['Symbol']}</strong></td>
                        <td>{row['Optimal_Past_Window']}</td>
                        <td>{row['Optimal_Trade_Window']}</td>
                        <td class="{backtest_class}">{backtest_pnl:+.2f}</td>
                        <td class="{calculated_class}">{calculated_pnl:+.2f}</td>
                        <td>{row['Weekly_Trades']}</td>
                        <td>{row['Initial_Capital']:,.0f}</td>
                        <td>{row['Trade_On']}</td>
                        <td>{row['Order_Round_Factor']}</td>
                    </tr>
"""
    
    # Totals mit Vergleich
    backtest_total_class = 'positive' if total_backtest_pnl > 0 else 'negative' if total_backtest_pnl < 0 else ''
    calculated_total_class = 'positive' if total_calculated_pnl > 0 else 'negative' if total_calculated_pnl < 0 else ''
    
    html_content += f"""
                    <tr style="background: #ecf0f1; font-weight: bold; border-top: 2px solid #34495e;">
                        <td><strong>🎯 GESAMT</strong></td>
                        <td colspan="2">-</td>
                        <td class="{backtest_total_class}"><strong>{total_backtest_pnl:+.2f}</strong></td>
                        <td class="{calculated_total_class}"><strong>{total_calculated_pnl:+.2f}</strong></td>
                        <td><strong>{total_trades}</strong></td>
                        <td colspan="3">-</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="pnl-comparison">
                <strong>🔍 PnL-Vergleich:</strong>
                Backtest PnL: <span class="{backtest_total_class}">{total_backtest_pnl:+.2f} EUR</span> | 
                Calculated PnL: <span class="{calculated_total_class}">{total_calculated_pnl:+.2f} EUR</span> | 
                Differenz: {(total_backtest_pnl - total_calculated_pnl):+.2f} EUR
            </div>
            
            <h2>📈 ALLE Trades der letzten 14 Tage (alle Ticker)</h2>
            <div class="trade-section">
                <div class="ticker-header">
                    <h3>🎯 Komplette Trades-Liste - {len(all_trades_14_days)} Trades</h3>
                </div>
                <table class="trade-table">
                    <thead>
                        <tr>
                            <th>Ticker</th>
                            <th>Datum</th>
                            <th>Action</th>
                            <th>Shares</th>
                            <th>Price (EUR)</th>
                            <th>Capital (EUR)</th>
                            <th>PnL (EUR)</th>
                            <th>Fees (EUR)</th>
                            <th>Trade On</th>
                            <th>Round Factor</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Sortiere Trades nach Datum
    sorted_trades = sorted(all_trades_14_days, key=lambda x: x.get('date', ''), reverse=True)
    
    for trade in sorted_trades:
        if trade.get('action') in ['BUY', 'SELL']:
            pnl = trade.get('pnl', 0)
            pnl_class = 'positive' if pnl > 0 else 'negative' if pnl < 0 else ''
            config = trade.get('config', {})
            
            html_content += f"""
                        <tr>
                            <td><strong>{trade.get('ticker', 'N/A')}</strong></td>
                            <td>{trade.get('date', 'N/A')}</td>
                            <td><strong>{trade.get('action', 'N/A')}</strong></td>
                            <td>{trade.get('shares', 0):,.6f}</td>
                            <td>{trade.get('price', 0):,.4f}</td>
                            <td>{trade.get('capital', 0):,.2f}</td>
                            <td class="{pnl_class}">{pnl:+.2f}</td>
                            <td>{trade.get('fees', 0):.2f}</td>
                            <td>{config.get('trade_on', 'N/A')}</td>
                            <td>{config.get('order_round_factor', 'N/A')}</td>
                        </tr>
"""
    
    html_content += """
                    </tbody>
                </table>
            </div>
"""
    
    # Detaillierte Trades pro Ticker
    html_content += f"""
            <h2>📈 Detaillierte Trades (letzte 2 Wochen)</h2>
"""
    
    for result_data in all_results:
        ticker = result_data['ticker']
        result = result_data['result']
        weekly_trades = result.get('weekly_trades_data', [])
        
        # Hole ticker-spezifische Config für Round Factor
        ticker_config = crypto_tickers.crypto_tickers.get(ticker, {})
        round_factor = ticker_config.get('order_round_factor', 0.01)
        trade_on = ticker_config.get('trade_on', 'Close')
        
        if not weekly_trades:
            continue
            
        html_content += f"""
            <div class="trade-section">
                <div class="ticker-header">
                    <h3>📊 {ticker} - {len(weekly_trades)} Trades (Round Factor: {round_factor}, Trade On: {trade_on})</h3>
                </div>
                <table class="trade-table">
                    <thead>
                        <tr>
                            <th>Datum</th>
                            <th>Action</th>
                            <th>Shares (gerundet mit {round_factor})</th>
                            <th>Price (EUR)</th>
                            <th>Capital (EUR)</th>
                            <th>PnL (EUR)</th>
                            <th>Fees (EUR)</th>
                            <th>Trade On</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        for trade in weekly_trades:
            if trade.get('action') in ['BUY', 'SELL']:  # Nur echte Trades
                pnl = trade.get('pnl', 0)
                pnl_class = 'positive' if pnl > 0 else 'negative' if pnl < 0 else ''
                
                html_content += f"""
                        <tr>
                            <td>{trade.get('date', 'N/A')}</td>
                            <td><strong>{trade.get('action', 'N/A')}</strong></td>
                            <td>{trade.get('shares', 0):,.6f}</td>
                            <td>{trade.get('price', 0):,.4f}</td>
                            <td>{trade.get('capital', 0):,.2f}</td>
                            <td class="{pnl_class}">{pnl:+.2f}</td>
                            <td>{trade.get('fees', 0):.2f}</td>
                            <td><strong>{trade_on}</strong></td>
                        </tr>
"""
        
        html_content += """
                    </tbody>
                </table>
            </div>
"""
    
    html_content += f"""
            <div class="timestamp">
                <p>🎯 Dieser Report wurde LIVE aus aktuellen Backtest-Results generiert!</p>
                <p>💡 Alle Daten sind aktuell und verwenden die optimierten Parameter aus crypto_tickers.py</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    # Speichern
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename

def main():
    """Main-Funktion"""
    try:
        print("🎯 LIVE BACKTEST REPORT - Keine alten HTML-Dateien mehr!")
        print("🚀 Führe AKTUELLE Backtests durch und erstelle SOFORT einen Report!")
        print("=" * 80)
        
        # 1. Führe LIVE Backtests aus und sammle ALLE Trades
        all_results, summary_data, all_trades_14_days = run_live_backtests()
        
        if not all_results:
            print("❌ Keine Backtest-Results erhalten!")
            return None
        
        print(f"\n✅ {len(all_results)} Ticker erfolgreich analysiert!")
        print(f"🎯 {len(all_trades_14_days)} Trades der letzten 14 Tage gefunden!")
        
        # 📊 SIMPLE TICKER PnL OUTPUT (mit KORREKTEN Werten)
        print()
        for result in summary_data:
            ticker = result['Symbol'].replace('-EUR', '').upper()  # Korrekter Key: 'Symbol'
            optimal_pnl = result['Optimal_PnL']  # Korrekter Key: 'Optimal_PnL'
            
            if ticker and optimal_pnl is not None:
                print(f"{ticker:<8} {optimal_pnl:>6.0f}%")
        print()
        
        # 2. Erstelle HTML-Report DIREKT aus Results mit ALLEN Trades
        print("📝 Erstelle HTML-Report aus LIVE-Daten...")
        filename = generate_live_html_report(all_results, summary_data, all_trades_14_days)
        
        print(f"\n🎉 LIVE BACKTEST REPORT erstellt: {filename}")
        print(f"📁 Pfad: {os.path.abspath(filename)}")
        print(f"🎯 Enthält:")
        print(f"   • Optimierungsparameter und PnL für alle {len(all_results)} Ticker")
        print(f"   • ALLE {len(all_trades_14_days)} Trades der letzten 14 Tage")
        print(f"   • PnL-Vergleich: Backtest vs. Calculated")
        print(f"   • Vollständige Trade-Details mit Shares und Round-Faktoren")
        
        # 3. Automatisch öffnen
        try:
            file_url = f"file:///{os.path.abspath(filename).replace(os.sep, '/')}"
            print(f"🌐 Öffne im Browser: {file_url}")
            webbrowser.open(file_url)
            print("✅ Browser geöffnet!")
        except Exception as e:
            print(f"⚠️ Browser-Fehler: {e}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return None

if __name__ == "__main__":
    main()
