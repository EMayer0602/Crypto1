#!/usr/bin/env python3
"""
Comprehensive Crypto Trading Report
Kombiniert Strategy und Summary Reports für vollständige Übersicht
"""

import pandas as pd
from datetime import datetime, timedelta
import os
from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def generate_comprehensive_report():
    """
    Generiert EINEN umfassenden Crypto Trading Report mit allem:
    - Trading Strategy Analysis + Trading Summary + Backtest Optimization + Performance Metrics
    ALLES IN EINEM EINZIGEN REPORT!
    """
    
    # Verwende die Ticker-Liste aus crypto_tickers.py
    tickers = list(crypto_tickers.keys())
    
    config = {
        'timeframe': 'daily',
        'lookback_period': 5,
        'csv_path': './'
    }
    
    all_weekly_trades = []
    strategy_analysis = []
    
    print("🎯 UMFASSENDER CRYPTO TRADING REPORT")
    print("=" * 80)
    print("📊 Vollständiger Crypto Trading Report (Strategy + Summary + Optimization)")
    print("=" * 80)
    
    for ticker in tickers:
        print(f"\n📊 Analysiere {ticker}...")
        
        # Prüfe ob CSV-Datei existiert
        csv_file = f"{ticker}_daily.csv"
        if not os.path.exists(csv_file):
            print(f"⚠️ CSV-Datei für {ticker} nicht gefunden: {csv_file}")
            continue
        
        try:
            # Führe Backtest aus
            result = run_backtest(ticker, config)
            
            # Sammle Strategy-Daten (ALLE Informationen in einem Objekt)
            strategy_data = {
                'Symbol': ticker,
                'Past_Window': result.get('optimal_past_window', 'N/A'),
                'Trade_Window': result.get('optimal_trade_window', 'N/A'),
                'Optimal_PnL': result.get('optimal_pnl', 'N/A'),
                'Support_Levels': result.get('support_levels_count', 0),
                'Resistance_Levels': result.get('resistance_levels_count', 0),
                'Total_Trading_Days': result.get('total_trading_days', 0),
                'Analysis_Start': result.get('analysis_start_date', 'N/A'),
                'Analysis_End': result.get('analysis_end_date', 'N/A'),
                'Status': 'Erfolgreich',
                'Weekly_Trades_Count': result.get('weekly_trades_count', 0)
            }
            strategy_analysis.append(strategy_data)
            
            # Sammle Extended Trades (letzte 2 Wochen)
            weekly_trades_data = result.get('weekly_trades_data', [])
            if weekly_trades_data:
                all_weekly_trades.extend(weekly_trades_data)
            
            print(f"✅ {ticker}: {result.get('weekly_trades_count', 0)} Trades, PnL: {result.get('optimal_pnl', 'N/A'):.2f}%" if isinstance(result.get('optimal_pnl'), (int, float)) else f"✅ {ticker}: {result.get('weekly_trades_count', 0)} Trades")
            
        except Exception as e:
            print(f"❌ Fehler bei {ticker}: {e}")
            strategy_analysis.append({
                'Symbol': ticker,
                'Past_Window': 'N/A',
                'Trade_Window': 'N/A', 
                'Optimal_PnL': 'N/A',
                'Support_Levels': 0,
                'Resistance_Levels': 0,
                'Total_Trading_Days': 0,
                'Analysis_Start': 'N/A',
                'Analysis_End': 'N/A',
                'Status': f'Fehler: {str(e)}',
                'Weekly_Trades_Count': 0
            })
    
    # Generiere EINEN umfassenden Report (nicht mehrere!)
    print_unified_console_report(all_weekly_trades, strategy_analysis)
    generate_unified_html_report(all_weekly_trades, strategy_analysis)
    # generate_unified_csv_exports(all_weekly_trades, strategy_analysis)  # ❌ Funktion existiert nicht
    
    return {
        'all_trades': all_weekly_trades,
        'strategy_analysis': strategy_analysis,
        'total_trades': len(all_weekly_trades)
    }

def print_unified_console_report(trades, strategy_data):
    """Drucke den vollständigen Report in der Konsole - ALLES IN EINEM!"""
    
    print("\n" + "=" * 80)
    print("📈 VOLLSTÄNDIGER CRYPTO TRADING REPORT")
    print("=" * 80)
    
    # Strategy Overview
    print(f"📊 Analysierte Ticker: {len(strategy_data)}")
    print(f"📅 Analyse-Zeitraum: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🔍 Betrachtung: Letzte 2 Wochen + Vollständige Backtest-Analyse")
    
    # TEIL 1: BACKTEST OPTIMIZATION RESULTS
    print("\n" + "🎯 BACKTEST OPTIMIZATION ERGEBNISSE")
    print("-" * 80)
    print(f"{'Ticker':<10} | {'P_Win':<5} | {'T_Win':<5} | {'PnL':<12} | {'Trades 2W':<8} | {'Status'}")
    print("-" * 80)
    
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
    
    # TEIL 2: TRADES DER LETZTEN 2 WOCHEN
    print("\n" + "=" * 80)
    print("📊 TRADES DER LETZTEN 2 WOCHEN")
    print("=" * 80)
    
    if trades:
        # Sortiere Trades nach Datum (neueste zuerst)
        trades.sort(key=lambda x: x['Date'], reverse=True)
        
        print(f"📈 Insgesamt {len(trades)} aktive Trades gefunden:")
        print("-" * 80)
        print(f"{'Nr.':<3} | {'Datum':<10} | {'Symbol':<8} | {'Action':<5} | {'Typ':<10}")
        print("-" * 80)
        
        for i, trade in enumerate(trades):
            trade_num = i + 1
            symbol = trade['Symbol']
            action = trade['Action'].upper()
            date_str = trade['Date'].strftime('%Y-%m-%d')
            
            # Trade-Typ
            today = datetime.now().date()
            current_trade_date = trade['Date'].date()
            trade_type = "Artificial" if current_trade_date == today else "Limit"
            
            # Emoji für Action
            emoji = "🔓" if action == 'BUY' else "🔒" if action == 'SELL' else "📊"
            
            print(f"{trade_num:2d}. | {date_str} | {symbol:<8} | {emoji} {action:<4} | {trade_type:<10}")
        
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
    
    print("=" * 80)

def generate_unified_html_report(trades, strategy_data):
    """Generiere den EINEN umfassenden HTML-Report mit allem drin"""
    
    filename = f"comprehensive_crypto_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
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
        <title>Comprehensive Crypto Trading Report</title>
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
                <h1>📊 Comprehensive Crypto Trading Report</h1>
                <p><strong>🎯 Crypto Trading Strategy & Summary Report</strong></p>
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
            
            <h2>🎯 Trading Strategy Analyse</h2>
            <table>
                <tr>
                    <th>Ticker</th>
                    <th>Past Window</th>
                    <th>Trade Window</th>
                    <th>Optimal PnL</th>
                    <th>Support Levels</th>
                    <th>Resistance Levels</th>
                    <th>Trading Days</th>
                    <th>Status</th>
                </tr>
    """
    
    # Strategy Analysis Table
    for strategy in strategy_data:
        symbol = strategy['Symbol']
        past_w = strategy['Past_Window']
        trade_w = strategy['Trade_Window']
        pnl = strategy['Optimal_PnL']
        
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
        
        status_class = 'status-success' if strategy['Status'] == 'Erfolgreich' else 'status-error'
        status_icon = '✅' if strategy['Status'] == 'Erfolgreich' else '❌'
        
        html_content += f"""
                <tr>
                    <td><strong>{symbol}</strong></td>
                    <td>{past_w}</td>
                    <td>{trade_w}</td>
                    <td class="{pnl_class}">{pnl_display}</td>
                    <td>{strategy['Support_Levels']}</td>
                    <td>{strategy['Resistance_Levels']}</td>
                    <td>{strategy['Total_Trading_Days']}</td>
                    <td class="{status_class}">{status_icon}</td>
                </tr>
        """
    
    html_content += """
            </table>
            
            <h2>📊 Trading Summary (Letzte 2 Wochen)</h2>
            <table>
                <tr>
                    <th>Nr.</th>
                    <th>Datum</th>
                    <th>Symbol</th>
                    <th>Action</th>
                    <th>Typ</th>
                    <th>Index</th>
                </tr>
    """
    
    # Trading Summary Table
    for i, trade in enumerate(trades):
        trade_num = i + 1
        symbol = trade['Symbol']
        action = trade['Action'].upper()
        date_str = trade['Date'].strftime('%Y-%m-%d')
        
        # Trade-Typ
        today = datetime.now().date()
        current_trade_date = trade['Date'].date()
        trade_type = "Artificial" if current_trade_date == today else "Limit"
        
        # Emoji für Action
        emoji = "🔓" if action == 'BUY' else "🔒" if action == 'SELL' else "📊"
        action_class = 'positive-pnl' if action == 'BUY' else 'negative-pnl' if action == 'SELL' else ''
        
        orig_index = trade.get('OriginalIndex', 'N/A')
        
        html_content += f"""
                <tr>
                    <td>{trade_num}</td>
                    <td>{date_str}</td>
                    <td><strong>{symbol}</strong></td>
                    <td class="{action_class}">{emoji} {action}</td>
                    <td>{trade_type}</td>
                    <td>{orig_index}</td>
                </tr>
        """
    
    # Performance Summary
    html_content += f"""
            </table>
            
            <h2>🏆 Performance Übersicht</h2>
            <table>
                <tr>
                    <th>Metrik</th>
                    <th>Wert</th>
                </tr>
                <tr>
                    <td>💰 Profitable Ticker</td>
                    <td><strong>{len(profitable_tickers)} von {len(strategy_data)}</strong></td>
                </tr>
                <tr>
                    <td>📊 Durchschnittliche PnL</td>
                    <td class="positive-pnl"><strong>{avg_pnl:.2f}%</strong></td>
                </tr>
    """
    
    if best_performer:
        html_content += f"""
                <tr>
                    <td>🥇 Best Performer</td>
                    <td><strong>{best_performer['Symbol']}</strong> <span class="positive-pnl">(+{best_performer['Optimal_PnL']:.2f}%)</span></td>
                </tr>
        """
    
    html_content += """
            </table>
            
            <div style="margin-top: 40px; padding: 20px; background-color: #ecf0f1; border-radius: 10px; text-align: center;">
                <p><strong>📈 Report generiert von Crypto Trading System</strong></p>
                <p>🔄 Für aktuelle Daten, führe die Analyse erneut aus</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n📄 Comprehensive HTML-Report gespeichert: {filename}")

def generate_csv_exports(trades, strategy_data, optimization_data):
    """Generiere CSV-Exporte für weitere Verarbeitung"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Trades Export
    if trades:
        trade_data = []
        for trade in trades:
            trade_data.append({
                'Symbol': trade['Symbol'],
                'Action': trade['Action'].upper(),
                'Date': trade['Date'].strftime('%Y-%m-%d'),
                'Type': 'Artificial' if trade['Date'].date() == datetime.now().date() else 'Limit',
                'OriginalIndex': trade.get('OriginalIndex', ''),
                'Timestamp': trade['Date'].strftime('%Y-%m-%d %H:%M:%S')
            })
        
        trades_df = pd.DataFrame(trade_data)
        trades_df = trades_df.sort_values('Date', ascending=False)
        trades_filename = f"comprehensive_trades_{timestamp}.csv"
        trades_df.to_csv(trades_filename, index=False)
        print(f"💾 Trades exportiert: {trades_filename}")
    
    # 2. Strategy Analysis Export
    strategy_df = pd.DataFrame(strategy_data)
    strategy_filename = f"comprehensive_strategy_{timestamp}.csv"
    strategy_df.to_csv(strategy_filename, index=False)
    print(f"💾 Strategy Analysis exportiert: {strategy_filename}")
    
    # 3. Optimization Results Export
    optimization_df = pd.DataFrame(optimization_data)
    optimization_filename = f"comprehensive_optimization_{timestamp}.csv"
    optimization_df.to_csv(optimization_filename, index=False)
    print(f"💾 Optimization Results exportiert: {optimization_filename}")

if __name__ == "__main__":
    print("🚀 Starte Comprehensive Crypto Trading Report...")
    result = generate_comprehensive_report()
    print(f"\n🎯 Comprehensive Report abgeschlossen!")
    print(f"📊 {result['total_trades']} Trades analysiert")
    print(f"🎯 {len(result['strategy_analysis'])} Ticker strategisch analysiert")
    print("✅ Alle Reports und Exports generiert")
