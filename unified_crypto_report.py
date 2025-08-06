#!/usr/bin/env python3
"""
UNIFIED Crypto Trading Report
ALLES IN EINEM EINZIGEN REPORT!
- Backtest Optimization
- Trading Summary (letzte 2 Wochen)
- Performance Metrics
- Trading Activity
"""

import pandas as pd
from datetime import datetime, timedelta
import os
from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def generate_unified_crypto_report():
    """
    Generiert EINEN EINZIGEN umfassenden Crypto Trading Report mit:
    - Backtest Optimization Results
    - Trades der letzten 2 Wochen
    - Performance Metrics
    - Trading Activity Summary
    ALLES IN EINEM REPORT!
    """
    
    # Verwende die Ticker-Liste aus crypto_tickers.py
    tickers = list(crypto_tickers.keys())
    
    config = {
        'timeframe': 'daily',
        'lookback_period': 5,
        'csv_path': './',
        'order_round_factor': 0.01  # Standard-Rundungsfaktor
        # Entfernt: 'initial_capital' - wird ticker-spezifisch gesetzt
    }
    
    all_weekly_trades = []
    all_matched_trades = []  # ✅ Neue Liste für matched trades
    strategy_analysis = []
    
    print("🎯 UNIFIED CRYPTO TRADING REPORT")
    print("=" * 80)
    print("📊 Vollständiger Crypto Trading Report (Alles in einem!)")
    print("=" * 80)
    
    for ticker in tickers:
        print(f"\n📊 Analysiere {ticker}...")
        
        # 🎯 NEW: Hole ticker-spezifische Konfiguration
        ticker_config = crypto_tickers.get(ticker, {})
        trade_on = ticker_config.get('trade_on', 'Close')  # Default Close
        
        print(f"   📊 Trade on: {trade_on} price")
        print(f"   💰 Initial Capital: {ticker_config.get('initialCapitalLong', 10000)} EUR")
        print(f"   🔧 Order Round Factor: {ticker_config.get('order_round_factor', 0.01)}")
        
        # Update config mit ticker-spezifischen Einstellungen
        config['trade_on'] = trade_on
        config['initial_capital'] = ticker_config.get('initialCapitalLong', 10000)  # Fallback 10000
        config['order_round_factor'] = ticker_config.get('order_round_factor', config.get('order_round_factor', 0.01))
        
        # Prüfe ob CSV-Datei existiert
        csv_file = f"{ticker}_daily.csv"
        if not os.path.exists(csv_file):
            print(f"⚠️ CSV-Datei für {ticker} nicht gefunden: {csv_file}")
            continue
        
        try:
            # Führe Backtest aus
            result = run_backtest(ticker, config)
            
            # Sammle ALLE Daten in einem Objekt
            strategy_data = {
                'Symbol': ticker,
                'Past_Window': result.get('optimal_past_window', 'N/A'),
                'Trade_Window': result.get('optimal_trade_window', 'N/A'),
                'Optimal_PnL': result.get('optimal_pnl', 'N/A'),
                'Weekly_Trades_Count': result.get('weekly_trades_count', 0),
                'Status': 'Erfolgreich'
            }
            strategy_analysis.append(strategy_data)
            
            # Sammle Extended Trades (letzte 2 Wochen)
            weekly_trades_data = result.get('weekly_trades_data', [])
            if weekly_trades_data:
                all_weekly_trades.extend(weekly_trades_data)
            
            # ✅ Sammle Matched Trades
            matched_trades = result.get('matched_trades', pd.DataFrame())
            if not matched_trades.empty:
                # Konvertiere DataFrame zu Liste für besseres HTML-Handling
                matched_trades_list = []
                for idx, row in matched_trades.iterrows():
                    matched_trades_list.append({
                        'Symbol': ticker,
                        'Buy_Date': row.get('Entry Date', 'N/A'),
                        'Sell_Date': row.get('Exit Date', 'N/A'),
                        'Buy_Price': row.get('Entry Price', 0),
                        'Sell_Price': row.get('Exit Price', 0),
                        'Shares': round(row.get('Shares', 0), 4),  # Rundung hinzugefügt
                        'PnL': row.get('PnL', 0),
                        'Trade_Value': row.get('Net PnL', 0),
                        'Status': row.get('Status', 'Unknown')
                    })
                all_matched_trades.extend(matched_trades_list)
            
            print(f"✅ {ticker}: {result.get('weekly_trades_count', 0)} Trades, PnL: {result.get('optimal_pnl', 'N/A'):.2f}%" if isinstance(result.get('optimal_pnl'), (int, float)) else f"✅ {ticker}: {result.get('weekly_trades_count', 0)} Trades")
            
        except Exception as e:
            print(f"❌ Fehler bei {ticker}: {e}")
            strategy_analysis.append({
                'Symbol': ticker,
                'Past_Window': 'N/A',
                'Trade_Window': 'N/A', 
                'Optimal_PnL': 'N/A',
                'Weekly_Trades_Count': 0,
                'Status': f'Fehler: {str(e)}'
            })
    
    # Generiere EINEN EINZIGEN Report
    print_unified_report(all_weekly_trades, strategy_analysis, all_matched_trades)  # ✅ Matched trades hinzugefügt
    generate_unified_html(all_weekly_trades, strategy_analysis, all_matched_trades)  # ✅ Matched trades hinzugefügt
    generate_unified_csv(all_weekly_trades, strategy_analysis)
    
    return {
        'all_trades': all_weekly_trades,
        'all_matched_trades': all_matched_trades,  # ✅ Matched trades hinzugefügt
        'strategy_analysis': strategy_analysis,
        'total_trades': len(all_weekly_trades)
    }

def print_unified_report(trades, strategy_data, matched_trades=None):
    """Drucke EINEN vollständigen Report in der Konsole"""
    
    print("\n" + "=" * 80)
    print("📈 UNIFIED CRYPTO TRADING REPORT")
    print("=" * 80)
    
    # Overview
    print(f"📊 Analysierte Ticker: {len(strategy_data)}")
    print(f"📅 Analyse-Zeitraum: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🔍 Betrachtung: Letzte 2 Wochen + Vollständige Backtest-Analyse")
    
    # BACKTEST OPTIMIZATION RESULTS
    print("\n" + "🎯 BACKTEST OPTIMIZATION ERGEBNISSE")
    print("-" * 70)
    print(f"{'Ticker':<10} | {'P_Win':<5} | {'T_Win':<5} | {'PnL':<12} | {'Trades 2W':<8} | {'Status'}")
    print("-" * 70)
    
    for strategy in strategy_data:
        symbol = strategy['Symbol']
        p_win = str(strategy['Past_Window'])[:5]
        t_win = str(strategy['Trade_Window'])[:5]
        
        # Format PnL
        pnl = strategy['Optimal_PnL']
        if pnl != 'N/A' and pnl is not None:
            try:
                pnl_float = float(pnl)
                pnl_str = f"+{pnl_float:.1f}%" if pnl_float > 0 else f"{pnl_float:.1f}%"
            except:
                pnl_str = "N/A"
        else:
            pnl_str = "N/A"
        
        trades_count = strategy.get('Weekly_Trades_Count', 0)
        status = strategy['Status'][:10]
        
        print(f"{symbol:<10} | {p_win:<5} | {t_win:<5} | {pnl_str:<12} | {trades_count:<8} | {status}")
    
    # TRADES DER LETZTEN 2 WOCHEN
    print("\n" + "📊 TRADES DER LETZTEN 2 WOCHEN")
    print("-" * 70)
    
    if trades:
        # Sortiere Trades nach Datum (neueste zuerst)
        trades.sort(key=lambda x: x['Date'], reverse=True)
        
        print(f"📈 Insgesamt {len(trades)} aktive Trades gefunden:")
        print("-" * 70)
        print(f"{'Nr.':<3} | {'Datum':<10} | {'Symbol':<8} | {'Action':<5} | {'Shares':<8} | {'Typ':<10}")
        print("-" * 70)
        
        for i, trade in enumerate(trades):
            trade_num = i + 1
            symbol = trade['Symbol']
            action = trade['Action'].upper()
            date_str = trade['Date'].strftime('%Y-%m-%d')
            shares = trade.get('Shares', 'N/A')
            
            # Rundung für Shares
            if isinstance(shares, (int, float)):
                shares = round(shares, 4)
            
            # Trade-Typ
            today = datetime.now().date()
            current_trade_date = trade['Date'].date()
            trade_type = "Artificial" if current_trade_date == today else "Limit"
            
            # Emoji für Action
            emoji = "🔓" if action == 'BUY' else "🔒" if action == 'SELL' else "📊"
            
            print(f"{trade_num:2d}. | {date_str} | {symbol:<8} | {emoji} {action:<4} | {str(shares):<8} | {trade_type:<10}")
        
        # Trading Activity Summary
        total_buy = sum(1 for trade in trades if trade['Action'].upper() == 'BUY')
        total_sell = sum(1 for trade in trades if trade['Action'].upper() == 'SELL')
        
        print("\n" + "📊 TRADING AKTIVITÄT ÜBERSICHT")
        print("-" * 40)
        print(f"🔓 Total BUY Orders:  {total_buy:2d}")
        print(f"🔒 Total SELL Orders: {total_sell:2d}")
        print(f"📈 Gesamt Trades:     {len(trades):2d}")
        
        # Performance Overview
        print("\n" + "🏆 GESAMTPERFORMANCE ÜBERSICHT")
        print("-" * 40)
        profitable_tickers = [s for s in strategy_data if isinstance(s.get('Optimal_PnL'), (int, float)) and s['Optimal_PnL'] > 0]
        avg_pnl = sum(s['Optimal_PnL'] for s in profitable_tickers) / len(profitable_tickers) if profitable_tickers else 0
        best_performer = max(profitable_tickers, key=lambda x: x['Optimal_PnL']) if profitable_tickers else None
        
        print(f"💰 Profitable Ticker: {len(profitable_tickers)}/{len(strategy_data)}")
        print(f"📊 Durchschnittliche PnL: {avg_pnl:.1f}%")
        if best_performer:
            print(f"🥇 Best Performer: {best_performer['Symbol']} (+{best_performer['Optimal_PnL']:.1f}%)")
        
    else:
        print("📈 Keine aktiven Trades in den letzten 2 Wochen gefunden")
    
    # ✅ MATCHED TRADES ANZEIGE
    if matched_trades and len(matched_trades) > 0:
        print("\n" + "💰 MATCHED TRADES (Vollständige Trade-Paare)")
        print("-" * 80)
        print(f"{'Nr.':<3} | {'Symbol':<8} | {'Buy Date':<10} | {'Sell Date':<10} | {'Shares':<8} | {'PnL':<10}")
        print("-" * 80)
        
        for i, trade in enumerate(matched_trades):
            trade_num = i + 1
            symbol = trade['Symbol']
            buy_date = str(trade['Buy_Date'])[:10] if trade['Buy_Date'] != 'N/A' else 'N/A'
            sell_date = str(trade['Sell_Date'])[:10] if trade['Sell_Date'] != 'N/A' else 'N/A'
            shares = f"{trade['Shares']:.3f}" if isinstance(trade['Shares'], (int, float)) else str(trade['Shares'])
            pnl = f"+{trade['PnL']:.2f}" if isinstance(trade['PnL'], (int, float)) and trade['PnL'] > 0 else f"{trade['PnL']:.2f}" if isinstance(trade['PnL'], (int, float)) else str(trade['PnL'])
            
            print(f"{trade_num:2d}. | {symbol:<8} | {buy_date:<10} | {sell_date:<10} | {shares:<8} | {pnl:<10}")
    
    print("=" * 80)

def generate_unified_html(trades, strategy_data, matched_trades=None):
    """Generiere EINEN HTML-Report mit allem drin"""
    
    filename = f"unified_crypto_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    # Calculate summary statistics
    total_buy = sum(1 for trade in trades if trade['Action'].upper() == 'BUY')
    total_sell = sum(1 for trade in trades if trade['Action'].upper() == 'SELL')
    profitable_tickers = [s for s in strategy_data if isinstance(s.get('Optimal_PnL'), (int, float)) and s['Optimal_PnL'] > 0]
    avg_pnl = sum(s['Optimal_PnL'] for s in profitable_tickers) / len(profitable_tickers) if profitable_tickers else 0
    best_performer = max(profitable_tickers, key=lambda x: x['Optimal_PnL']) if profitable_tickers else None
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Unified Crypto Trading Report</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f8f9fa; }}
            h1 {{ color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; border-left: 4px solid #3498db; padding-left: 15px; }}
            h3 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #3498db; color: white; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .summary-box {{ display: inline-block; margin: 10px; padding: 20px; border: 2px solid #3498db; border-radius: 10px; text-align: center; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .summary-number {{ font-size: 28px; font-weight: bold; color: #2c3e50; }}
            .summary-stats {{ text-align: center; margin: 30px 0; }}
            .positive-pnl {{ color: #27ae60; font-weight: bold; }}
            .negative-pnl {{ color: #e74c3c; font-weight: bold; }}
            .status-success {{ color: #27ae60; }}
            .status-error {{ color: #e74c3c; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .report-header {{ text-align: center; padding: 20px; background-color: white; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="report-header">
                <h1>📊 Unified Crypto Trading Report</h1>
                <p><strong>🎯 Vollständiger Crypto Trading Report (Alles in einem!)</strong></p>
                <p><strong>📅 Generiert:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>📈 Zeitraum:</strong> Letzte 2 Wochen + Vollständige Backtest-Analyse</p>
            </div>
            
            <div class="summary-stats">
                <div class="summary-box">
                    <h3>📊 Analysierte Ticker</h3>
                    <div class="summary-number">{len(strategy_data)}</div>
                </div>
                <div class="summary-box">
                    <h3>🔓 Total BUY</h3>
                    <div class="summary-number">{total_buy}</div>
                </div>
                <div class="summary-box">
                    <h3>🔒 Total SELL</h3>
                    <div class="summary-number">{total_sell}</div>
                </div>
                <div class="summary-box">
                    <h3>💰 Profitable Ticker</h3>
                    <div class="summary-number">{len(profitable_tickers)}/{len(strategy_data)}</div>
                </div>
                <div class="summary-box">
                    <h3>📊 Avg. PnL</h3>
                    <div class="summary-number">{avg_pnl:.1f}%</div>
                </div>
            </div>
            
            <h2>🎯 Backtest Optimization Ergebnisse</h2>
            <table>
                <tr>
                    <th>Ticker</th>
                    <th>Past Window</th>
                    <th>Trade Window</th>
                    <th>Optimal PnL</th>
                    <th>Trades (2W)</th>
                    <th>Status</th>
                </tr>
    """
    
    # Strategy Analysis Table
    for strategy in strategy_data:
        symbol = strategy['Symbol']
        past_w = strategy['Past_Window']
        trade_w = strategy['Trade_Window']
        pnl = strategy['Optimal_PnL']
        trades_count = strategy.get('Weekly_Trades_Count', 0)
        status = strategy['Status']
        
        # Format PnL
        if pnl != 'N/A' and pnl is not None:
            try:
                pnl_float = float(pnl)
                if pnl_float > 0:
                    pnl_display = f'+{pnl_float:.2f}%'
                    pnl_class = 'positive-pnl'
                else:
                    pnl_display = f'{pnl_float:.2f}%'
                    pnl_class = 'negative-pnl'
            except:
                pnl_display = 'N/A'
                pnl_class = ''
        else:
            pnl_display = 'N/A'
            pnl_class = ''
        
        status_class = 'status-success' if 'Erfolgreich' in status else 'status-error'
        
        html_content += f"""
                <tr>
                    <td><strong>{symbol}</strong></td>
                    <td>{past_w}</td>
                    <td>{trade_w}</td>
                    <td class="{pnl_class}">{pnl_display}</td>
                    <td>{trades_count}</td>
                    <td class="{status_class}">{status}</td>
                </tr>
        """
    
    # Trades Table
    html_content += f"""
            </table>
            
            <h2>📊 Trades der letzten 2 Wochen</h2>
            <table>
                <tr>
                    <th>Nr.</th>
                    <th>Datum</th>
                    <th>Symbol</th>
                    <th>Action</th>
                    <th>Shares</th>
                    <th>Typ</th>
                </tr>
    """
    
    if trades:
        trades.sort(key=lambda x: x['Date'], reverse=True)
        
        for i, trade in enumerate(trades):
            trade_num = i + 1
            symbol = trade['Symbol']
            action = trade['Action'].upper()
            date_str = trade['Date'].strftime('%Y-%m-%d')
            shares = trade.get('Shares', 'N/A')
            
            # Rundung für Shares
            if isinstance(shares, (int, float)):
                shares = round(shares, 4)
            
            # Trade-Typ
            today = datetime.now().date()
            current_trade_date = trade['Date'].date()
            trade_type = "Artificial" if current_trade_date == today else "Limit"
            
            # Emoji für Action
            emoji = "🔓" if action == 'BUY' else "🔒" if action == 'SELL' else "📊"
            
            html_content += f"""
                    <tr>
                        <td>{trade_num}</td>
                        <td>{date_str}</td>
                        <td><strong>{symbol}</strong></td>
                        <td>{emoji} {action}</td>
                        <td>{shares}</td>
                        <td>{trade_type}</td>
                    </tr>
            """
    else:
        html_content += """
                <tr>
                    <td colspan="6" style="text-align: center; color: #888;">Keine aktiven Trades in den letzten 2 Wochen gefunden</td>
                </tr>
        """
    
    # Performance Summary
    html_content += f"""
            </table>
    """
    
    # ✅ MATCHED TRADES TABELLE
    if matched_trades and len(matched_trades) > 0:
        html_content += f"""
            <h2>💰 Matched Trades (Vollständige Trade-Paare)</h2>
            <table>
                <tr>
                    <th>Nr.</th>
                    <th>Symbol</th>
                    <th>Buy Date</th>
                    <th>Sell Date</th>
                    <th>Shares</th>
                    <th>Buy Price</th>
                    <th>Sell Price</th>
                    <th>PnL</th>
                </tr>
        """
        
        for i, trade in enumerate(matched_trades):
            trade_num = i + 1
            symbol = trade['Symbol']
            buy_date = str(trade['Buy_Date'])[:10] if trade['Buy_Date'] != 'N/A' else 'N/A'
            sell_date = str(trade['Sell_Date'])[:10] if trade['Sell_Date'] != 'N/A' else 'N/A'
            shares = f"{trade['Shares']:.3f}" if isinstance(trade['Shares'], (int, float)) else str(trade['Shares'])
            buy_price = f"€{trade['Buy_Price']:.2f}" if isinstance(trade['Buy_Price'], (int, float)) else str(trade['Buy_Price'])
            sell_price = f"€{trade['Sell_Price']:.2f}" if isinstance(trade['Sell_Price'], (int, float)) else str(trade['Sell_Price'])
            
            # Format PnL
            if isinstance(trade['PnL'], (int, float)):
                if trade['PnL'] > 0:
                    pnl_display = f"+€{trade['PnL']:.2f}"
                    pnl_class = 'positive-pnl'
                else:
                    pnl_display = f"€{trade['PnL']:.2f}"
                    pnl_class = 'negative-pnl'
            else:
                pnl_display = str(trade['PnL'])
                pnl_class = ''
            
            html_content += f"""
                    <tr>
                        <td>{trade_num}</td>
                        <td><strong>{symbol}</strong></td>
                        <td>{buy_date}</td>
                        <td>{sell_date}</td>
                        <td>{shares}</td>
                        <td>{buy_price}</td>
                        <td>{sell_price}</td>
                        <td class="{pnl_class}">{pnl_display}</td>
                    </tr>
            """
        
        html_content += """
            </table>
        """
    
    html_content += f"""
            <h2>🏆 Performance Übersicht</h2>
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <p><strong>🔓 Total BUY Orders:</strong> {total_buy}</p>
                <p><strong>🔒 Total SELL Orders:</strong> {total_sell}</p>
                <p><strong>📈 Gesamt Trades:</strong> {len(trades)}</p>
                <p><strong>💰 Profitable Ticker:</strong> {len(profitable_tickers)}/{len(strategy_data)}</p>
                <p><strong>📊 Durchschnittliche PnL:</strong> {avg_pnl:.1f}%</p>
    """
    
    if best_performer:
        html_content += f"""
                <p><strong>🥇 Best Performer:</strong> {best_performer['Symbol']} (+{best_performer['Optimal_PnL']:.1f}%)</p>
        """
    
    html_content += """
            </div>
        </div>
    </body>
    </html>
    """
    
    # Schreibe HTML-Report
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Unified HTML Report generiert: {filename}")
    return filename

def generate_unified_csv(trades, strategy_data):
    """Generiere EINEN CSV-Export mit allem"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Strategy CSV
    strategy_filename = f"unified_strategy_{timestamp}.csv"
    strategy_df = pd.DataFrame(strategy_data)
    strategy_df.to_csv(strategy_filename, index=False)
    print(f"✅ Unified Strategy CSV generiert: {strategy_filename}")
    
    # Trades CSV
    if trades:
        trades_filename = f"unified_trades_{timestamp}.csv"
        # Ensure 'Shares' column is present in all rows and round values
        for t in trades:
            if 'Shares' not in t:
                t['Shares'] = None
            elif isinstance(t['Shares'], (int, float)):
                t['Shares'] = round(t['Shares'], 4)
        trades_df = pd.DataFrame(trades)
        # Reorder columns to put Shares after OriginalIndex if present
        cols = list(trades_df.columns)
        if 'Shares' in cols:
            base_cols = ['Symbol', 'Action', 'Date', 'ExtIndex', 'OriginalIndex', 'Shares']
            # Add any extra columns at the end
            extra_cols = [c for c in cols if c not in base_cols]
            trades_df = trades_df[base_cols + extra_cols if extra_cols else base_cols]
        trades_df.to_csv(trades_filename, index=False)
        print(f"✅ Unified Trades CSV generiert: {trades_filename}")
    else:
        print("📈 Keine Trades für CSV-Export verfügbar")
    
    return strategy_filename

if __name__ == "__main__":
    print("🚀 Starte Unified Crypto Trading Report...")
    result = generate_unified_crypto_report()
    print(f"✅ Report abgeschlossen! {result['total_trades']} Trades analysiert.")
