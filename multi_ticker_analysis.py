#!/usr/bin/env python3
"""
Multi-Ticker Analysis für Extended Trades der letzten 2 Wochen
Erstellt eine zusammengefasste Tabelle aller Ticker für Bitpanda API Vorbereitung
"""

import pandas as pd
from datetime import datetime, timedelta
import os
from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def analyze_all_tickers():
    """
    Analysiere alle verfügbaren Ticker und erstelle eine zusammengefasste 
    Tabelle aller Extended Trades der letzten 2 Wochen
    """
    
    # Verwende die Ticker-Liste aus crypto_tickers.py
    tickers = list(crypto_tickers.keys())
    
    # ✅ REPARIERT: Verwende DIESELBE Config-Logik wie unified_crypto_report.py
    # Basis-Config mit Standard-Werten
    base_config = {
        'timeframe': 'daily',
        'lookback_period': 5,
        'csv_path': './',
        'commission_rate': 0.0018,
        'min_commission': 1.0,
        'order_round_factor': 0.01
    }
    
    all_weekly_trades = []
    ticker_summaries = []
    optimization_summaries = []  # Neue Liste für Optimierungsparameter
    
    print("🔍 MULTI-TICKER ANALYSE - Extended Trades der letzten 2 Wochen")
    print("=" * 80)
    
    for ticker in tickers:
        print(f"\n📊 Analysiere {ticker}...")
        
        # ✅ REPARIERT: Hole ticker-spezifische Config (wie in unified_crypto_report.py)
        ticker_config = crypto_tickers.get(ticker, {})
        trade_on = ticker_config.get('trade_on', 'Close')  # Default Close
        
        print(f"   🎯 Trade-Ausführung: {trade_on} price")
        print(f"   💰 Initial Capital: {ticker_config.get('initialCapitalLong', 10000)} EUR")
        print(f"   🔧 Order Round Factor: {ticker_config.get('order_round_factor', 0.01)}")
        
        # Update config mit ticker-spezifischen Einstellungen
        config = base_config.copy()  # Start mit Basis-Config
        config['trade_on'] = trade_on
        config['initial_capital'] = ticker_config.get('initialCapitalLong', 10000)  # Fallback 10000
        config['order_round_factor'] = ticker_config.get('order_round_factor', config.get('order_round_factor', 0.01))
        
        # Prüfe ob CSV-Datei existiert
        csv_file = f"{ticker}_daily.csv"
        if not os.path.exists(csv_file):
            print(f"⚠️ CSV-Datei für {ticker} nicht gefunden: {csv_file}")
            ticker_summaries.append({
                'Symbol': ticker,
                'Status': 'CSV nicht gefunden',
                'Trades': 0,
                'Last_Trade_Date': None
            })
            continue
        
        try:
            # ✅ REPARIERT: Führe Backtest mit korrekter ticker-spezifischer Config aus
            result = run_backtest(ticker, config)
            
            # Extrahiere die Trades der letzten 2 Wochen
            weekly_trades_data = result.get('weekly_trades_data', [])
            weekly_trades_count = result.get('weekly_trades_count', 0)
            
            # Sammle Optimierungsparameter
            optimization_data = {
                'Symbol': ticker,
                'Past_Window': result.get('optimal_past_window', 'N/A'),
                'Trade_Window': result.get('optimal_trade_window', 'N/A'),
                'Optimal_PnL': result.get('optimal_pnl', 'N/A'),
                'Status': 'Erfolgreich'
            }
            optimization_summaries.append(optimization_data)
            
            # Sammle alle Trades für die zusammengefasste Tabelle
            if weekly_trades_data:
                all_weekly_trades.extend(weekly_trades_data)
            
            # Zusammenfassung pro Ticker
            if weekly_trades_data:
                last_trade_date = max([trade['Date'] for trade in weekly_trades_data])
            else:
                last_trade_date = None
                
            ticker_summaries.append({
                'Symbol': ticker,
                'Status': 'Erfolgreich',
                'Trades': weekly_trades_count,
                'Last_Trade_Date': last_trade_date
            })
            
            print(f"✅ {ticker}: {weekly_trades_count} Trades gefunden")
            
        except Exception as e:
            print(f"❌ Fehler bei {ticker}: {e}")
            ticker_summaries.append({
                'Symbol': ticker,
                'Status': f'Fehler: {str(e)}',
                'Trades': 0,
                'Last_Trade_Date': None
            })
            optimization_summaries.append({
                'Symbol': ticker,
                'Past_Window': 'N/A',
                'Trade_Window': 'N/A', 
                'Optimal_PnL': 'N/A',
                'Status': f'Fehler: {str(e)}'
            })
    
    # Erstelle zusammengefasste Tabelle
    print("\n" + "=" * 80)
    print("📈 ZUSAMMENGEFASSTE TABELLE - ALLE EXTENDED TRADES DER LETZTEN 2 WOCHEN")
    print("=" * 80)
    
    if all_weekly_trades:
        # Sortiere Trades nach Datum (neueste zuerst)
        all_weekly_trades.sort(key=lambda x: x['Date'], reverse=True)
        
        print(f"📊 Insgesamt {len(all_weekly_trades)} Trades gefunden:")
        print("-" * 80)
        
        # VOLLSTÄNDIGE Trades-Liste in der Konsole anzeigen
        print(f"📋 ALLE {len(all_weekly_trades)} TRADES DER LETZTEN 2 WOCHEN:")
        print("-" * 80)
        print(f"{'Nr.':<3} | {'Datum':<10} | {'Symbol':<8} | {'Action':<5} | {'Typ':<10} | {'Index':<6}")
        print("-" * 80)
        
        for i, trade in enumerate(all_weekly_trades):
            trade_num = i + 1
            symbol = trade['Symbol']
            action = trade['Action'].upper()
            date_str = trade['Date'].strftime('%Y-%m-%d')
            
            # Trade-Typ
            today = datetime.now().date()
            current_trade_date = trade['Date'].date()
            if current_trade_date == today:
                trade_type = "Artificial"
            else:
                trade_type = "Limit"
            
            # Emoji für Action
            if action == 'BUY':
                emoji = "🔓"
            elif action == 'SELL':
                emoji = "🔒"
            else:
                emoji = "📊"
            
            # Original Index
            orig_index = trade.get('OriginalIndex', 'N/A')
            
            print(f"{trade_num:2d}. | {date_str} | {symbol:<8} | {emoji} {action:<4} | {trade_type:<10} | {orig_index}")
        
        # HTML-Tabelle für Report
        html_table = create_consolidated_html_table(all_weekly_trades)
        
        # CSV-Export für Bitpanda API
        export_to_csv(all_weekly_trades)
        
        # HTML-Report speichern (mit Optimierungsergebnissen)
        save_html_report(html_table, optimization_summaries)
        
    else:
        print("📈 Keine Extended Trades in den letzten 2 Wochen gefunden")
        html_table = "<p>Keine Extended Trades in den letzten 2 Wochen gefunden</p>"
    
    # Ticker-Zusammenfassung
    print("\n" + "=" * 80)
    print("📋 TICKER-ZUSAMMENFASSUNG")
    print("=" * 80)
    
    total_buy = sum(1 for trade in all_weekly_trades if trade['Action'].upper() == 'BUY')
    total_sell = sum(1 for trade in all_weekly_trades if trade['Action'].upper() == 'SELL')
    
    for summary in ticker_summaries:
        status_emoji = "✅" if summary['Status'] == 'Erfolgreich' else "❌"
        last_trade = summary['Last_Trade_Date'].strftime('%Y-%m-%d') if summary['Last_Trade_Date'] else 'Keine'
        print(f"{status_emoji} {summary['Symbol']:8s} | Trades: {summary['Trades']:2d} | Letzter Trade: {last_trade}")
    
    # NEUE DETAILLIERTE ZUSAMMENFASSUNG
    print("\n" + "=" * 80)
    print("📊 TRADING-AKTIVITÄT ÜBERSICHT (Letzte 2 Wochen)")
    print("=" * 80)
    print(f"🔓 Total BUY Orders:  {total_buy:2d}")
    print(f"🔒 Total SELL Orders: {total_sell:2d}")
    print(f"📈 Gesamt Trades:     {len(all_weekly_trades):2d}")
    print("-" * 40)
    
    # Aktivste Ticker
    if all_weekly_trades:
        ticker_activity = {}
        for trade in all_weekly_trades:
            symbol = trade['Symbol']
            if symbol not in ticker_activity:
                ticker_activity[symbol] = {'buy': 0, 'sell': 0}
            ticker_activity[symbol][trade['Action'].lower()] += 1
        
        print("🏆 Aktivste Ticker:")
        sorted_tickers = sorted(ticker_activity.items(), 
                               key=lambda x: x[1]['buy'] + x[1]['sell'], 
                               reverse=True)
        
        for symbol, activity in sorted_tickers[:3]:  # Top 3
            total_activity = activity['buy'] + activity['sell']
            print(f"   {symbol:8s}: {total_activity} Trades (🔓{activity['buy']} | 🔒{activity['sell']})")
        
        # Letzte 5 Trades chronologisch (nur zur Übersicht)
        recent_trades = sorted(all_weekly_trades, key=lambda x: x['Date'], reverse=True)[:5]
        print(f"\n🕒 Neueste 5 Trades (zur Übersicht):")
        for trade in recent_trades:
            action_emoji = "🔓" if trade['Action'].upper() == 'BUY' else "🔒"
            date_str = trade['Date'].strftime('%m-%d')
            print(f"   {date_str} | {trade['Symbol']:8s} | {action_emoji} {trade['Action']:4s}")
    
    print("=" * 80)
    
    # NEUE BACKTEST-OPTIMIERUNG ZUSAMMENFASSUNG
    print("\n" + "=" * 80)
    print("🎯 BACKTEST-OPTIMIERUNG ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"{'Ticker':<10} | {'Past_Window':<12} | {'Trade_Window':<13} | {'Optimal_PnL':<15} | {'Status':<10}")
    print("-" * 80)
    
    for opt in optimization_summaries:
        symbol = opt['Symbol']
        past_w = str(opt['Past_Window'])
        trade_w = str(opt['Trade_Window'])
        pnl = str(opt['Optimal_PnL'])
        status = "✅" if opt['Status'] == 'Erfolgreich' else "❌"
        
        # Formatierung der PnL
        if pnl != 'N/A' and pnl != 'None' and pnl is not None:
            try:
                pnl_float = float(pnl)
                if pnl_float > 0:
                    pnl = f"+{pnl_float:.2f}%"
                else:
                    pnl = f"{pnl_float:.2f}%"
            except (ValueError, TypeError):
                pnl = "N/A"
        else:
            pnl = "N/A"
        
        print(f"{symbol:<10} | {past_w:<12} | {trade_w:<13} | {pnl:<15} | {status}")
    
    print("=" * 80)
    
    return {
        'all_trades': all_weekly_trades,
        'ticker_summaries': ticker_summaries,
        'optimization_summaries': optimization_summaries,  # Neu hinzugefügt
        'html_table': html_table,
        'total_trades': len(all_weekly_trades)
    }

def save_html_report(html_content, optimization_summaries):
    """Speichere den HTML-Report in einer Datei"""
    filename = f"trading_summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    # Erstelle die Backtest-Optimierung HTML-Tabelle
    optimization_html = create_optimization_html_table(optimization_summaries)
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading Summary Report - Letzte 2 Wochen</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .stat-box {{ display: inline-block; margin: 10px; padding: 15px; border: 2px solid #3498db; border-radius: 10px; text-align: center; }}
            .stat-number {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
            .summary-stats {{ text-align: center; margin: 20px 0; }}
            .trades-table, .activity-table, .optimization-table {{ width: 100%; }}
        </style>
    </head>
    <body>
        <h1>📊 Crypto Trading Summary Report</h1>
        <p><strong>Zeitraum:</strong> Letzte 2 Wochen (Extended Trades)</p>
        <p><strong>Generiert:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        {optimization_html}
        {html_content}
    </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"📄 HTML-Report gespeichert: {filename}")

def create_optimization_html_table(optimization_summaries):
    """Erstelle HTML-Tabelle für Backtest-Optimierungsergebnisse"""
    
    html = """
    <div class="optimization-summary">
        <h2>🎯 Backtest-Optimierung Zusammenfassung</h2>
        <table class="optimization-table">
            <tr>
                <th>Ticker</th>
                <th>Past Window</th>
                <th>Trade Window</th>
                <th>Optimal PnL</th>
                <th>Status</th>
            </tr>
    """
    
    for opt in optimization_summaries:
        symbol = opt['Symbol']
        past_w = str(opt['Past_Window'])
        trade_w = str(opt['Trade_Window'])
        pnl = str(opt['Optimal_PnL'])
        status_icon = "✅" if opt['Status'] == 'Erfolgreich' else "❌"
        
        # Formatierung der PnL
        if pnl != 'N/A' and pnl != 'None' and pnl is not None:
            try:
                pnl_float = float(pnl)
                if pnl_float > 0:
                    pnl = f"+{pnl_float:.2f}%"
                    pnl_color = "green"
                else:
                    pnl = f"{pnl_float:.2f}%"
                    pnl_color = "red"
            except (ValueError, TypeError):
                pnl = "N/A"
                pnl_color = "gray"
        else:
            pnl = "N/A"
            pnl_color = "gray"
        
        html += f"""
            <tr>
                <td><strong>{symbol}</strong></td>
                <td>{past_w}</td>
                <td>{trade_w}</td>
                <td style="color: {pnl_color}; font-weight: bold;">{pnl}</td>
                <td>{status_icon}</td>
            </tr>
        """
    
    html += """
        </table>
    </div>
    """
    
    return html

def create_consolidated_html_table(trades):
    """Erstelle HTML-Tabelle für alle Trades mit Zusammenfassung"""
    
    total_buy = sum(1 for trade in trades if trade['Action'].upper() == 'BUY')
    total_sell = sum(1 for trade in trades if trade['Action'].upper() == 'SELL')
    
    # Aktivste Ticker ermitteln
    ticker_activity = {}
    for trade in trades:
        symbol = trade['Symbol']
        if symbol not in ticker_activity:
            ticker_activity[symbol] = {'buy': 0, 'sell': 0}
        ticker_activity[symbol][trade['Action'].lower()] += 1
    
    html = f"""
    <div class="trading-summary">
        <h2>📊 Trading-Aktivität Übersicht (Letzte 2 Wochen)</h2>
        <div class="summary-stats">
            <div class="stat-box">
                <h3>🔓 Total BUY</h3>
                <div class="stat-number">{total_buy}</div>
            </div>
            <div class="stat-box">
                <h3>🔒 Total SELL</h3>
                <div class="stat-number">{total_sell}</div>
            </div>
            <div class="stat-box">
                <h3>� Gesamt Trades</h3>
                <div class="stat-number">{len(trades)}</div>
            </div>
        </div>
        
        <h3>🏆 Aktivste Ticker</h3>
        <table class="activity-table">
            <tr><th>Symbol</th><th>Total</th><th>BUY</th><th>SELL</th></tr>
    """
    
    # Top Ticker
    sorted_tickers = sorted(ticker_activity.items(), 
                           key=lambda x: x[1]['buy'] + x[1]['sell'], 
                           reverse=True)
    
    for symbol, activity in sorted_tickers:
        total_activity = activity['buy'] + activity['sell']
        html += f"""
            <tr>
                <td>{symbol}</td>
                <td>{total_activity}</td>
                <td>{activity['buy']}</td>
                <td>{activity['sell']}</td>
            </tr>
        """
    
    html += """
        </table>
    </div>
    
    <div class="consolidated-trades">
        <h3>🔗 Detaillierte Trade-Liste</h3>
        <table class="trades-table">
            <tr>
                <th>Nr.</th>
                <th>Symbol</th>
                <th>Action</th>
                <th>Datum</th>
                <th>Typ</th>
                <th>Info</th>
            </tr>
    """
    
    for i, trade in enumerate(trades):
        trade_num = i + 1
        symbol = trade['Symbol']
        action = trade['Action'].upper()
        date_str = trade['Date'].strftime('%Y-%m-%d')
        
        # Trade-Typ
        today = datetime.now().date()
        current_trade_date = trade['Date'].date()
        trade_type = "Artificial" if current_trade_date == today else "Limit"
        
        # Emoji
        emoji = "🔓" if action == 'BUY' else "🔒" if action == 'SELL' else "📊"
        
        info = f"Index: {trade.get('OriginalIndex', 'N/A')}"
        
        html += f"""
            <tr>
                <td>{trade_num}</td>
                <td>{symbol}</td>
                <td>{emoji} {action}</td>
                <td>{date_str}</td>
                <td>{trade_type}</td>
                <td>{info}</td>
            </tr>
        """
    
    html += """
        </table>
    </div>
    """
    
    return html

def export_to_csv(trades):
    """Exportiere Trades als CSV für Bitpanda API Vorbereitung"""
    
    if not trades:
        return
    
    # Erstelle DataFrame
    trade_data = []
    for trade in trades:
        trade_data.append({
            'Symbol': trade['Symbol'],
            'Action': trade['Action'].upper(),
            'Date': trade['Date'].strftime('%Y-%m-%d'),
            'Type': 'Artificial' if trade['Date'].date() == datetime.now().date() else 'Limit',
            'OriginalIndex': trade.get('OriginalIndex', ''),
            'Long_Signal_Extended': trade.get('Long Signal Extended', False),
            'Timestamp': trade['Date'].strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(trade_data)
    
    # Sortiere nach Datum (neueste zuerst)
    df = df.sort_values('Date', ascending=False)
    
    # Exportiere
    filename = f"extended_trades_last_2_weeks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    
    print(f"\n💾 Trades exportiert nach: {filename}")
    print(f"📊 {len(df)} Trades für Bitpanda API Vorbereitung")

if __name__ == "__main__":
    result = analyze_all_tickers()
    print(f"\n🎯 Analyse abgeschlossen: {result['total_trades']} Trades gesamt")
