#!/usr/bin/env python3
"""
Live Backtest Clean - Erstellt immer aktuelle Backtest-Reports mit Charts
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import traceback
from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly
import webbrowser

def update_csv_data():
    """Update CSV files before backtest"""
    print("📊 Updating CSV data...")
    
    try:
        # Import update modules
        from get_real_crypto_data import update_crypto_data_coingecko
        
        # Update CSVs for all tickers
        for ticker in crypto_tickers.keys():
            try:
                print(f"   Updating {ticker}...")
                update_crypto_data_coingecko(ticker)
            except Exception as e:
                print(f"   ⚠️  {ticker}: {str(e)}")
        
        print("✅ CSV update completed")
    except Exception as e:
        print(f"⚠️  CSV update error: {str(e)}")

def calculate_shares(ticker, price, initial_capital, order_round_factor):
    """Calculate shares based on order_round_factor"""
    try:
        if price <= 0:
            return "N/A"
        
        raw_shares = initial_capital / price
        # Round according to order_round_factor
        if order_round_factor >= 1:
            shares = int(raw_shares / order_round_factor) * order_round_factor
        else:
            shares = round(raw_shares / order_round_factor) * order_round_factor
        
        return f"{shares:,.{2 if order_round_factor < 1 else 0}f}"
    except:
        return "N/A"

def create_plotly_chart(ticker, backtest_result):
    """Create Plotly chart with price, equity, and trade markers - EXACT COPY FROM WORKING VERSION"""
    try:
        # Get ALL data from backtest result
        if not backtest_result:
            print(f"No backtest result for {ticker}")
            return None
        
        print(f"Creating chart for {ticker}...")
        print(f"Backtest result keys: {backtest_result.keys()}")
        
        # Try to get extended_trades first, fallback to matched_trades
        ext_trades = None
        if 'extended_trades' in backtest_result and not backtest_result['extended_trades'].empty:
            ext_trades = backtest_result['extended_trades'].copy()
        elif 'matched_trades' in backtest_result and not backtest_result['matched_trades'].empty:
            ext_trades = backtest_result['matched_trades'].copy()
        else:
            print(f"No trade data found for {ticker}")
            return None
        
        print(f"Trade data shape: {ext_trades.shape}")
        print(f"Trade data columns: {ext_trades.columns.tolist()}")
        
        # Ensure proper date handling
        if ext_trades.index.name == 'Date' or 'Date' not in ext_trades.columns:
            ext_trades = ext_trades.reset_index()
        
        # Convert Date column properly
        if 'Date' in ext_trades.columns:
            ext_trades['Date'] = pd.to_datetime(ext_trades['Date'])
        else:
            print(f"No Date column found in {ticker} data")
            return None
            
        ext_trades = ext_trades.sort_values('Date')
        
        # Create interactive chart with 2 subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(f"{ticker} Price & Trades", f"{ticker} Equity Curve"),
            vertical_spacing=0.12,
            row_heights=[0.65, 0.35],
            shared_xaxes=True
        )
        
        # 1. PRICE LINE (always visible)
        if 'Close' in ext_trades.columns:
            fig.add_trace(
                go.Scatter(
                    x=ext_trades['Date'],
                    y=ext_trades['Close'],
                    mode='lines',
                    name=f'{ticker} Price',
                    line=dict(color='#1f77b4', width=2),
                    hovertemplate=f'{ticker}: €%{{y:.4f}}<br>%{{x}}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # 2. BUY MARKERS (green triangles up)
        buy_mask = ext_trades['Action'].isin(['BUY', 'Buy']) if 'Action' in ext_trades.columns else pd.Series([False] * len(ext_trades))
        buy_trades = ext_trades[buy_mask]
        
        if not buy_trades.empty and 'Close' in buy_trades.columns:
            fig.add_trace(
                go.Scatter(
                    x=buy_trades['Date'],
                    y=buy_trades['Close'],
                    mode='markers',
                    name='🔓 BUY',
                    marker=dict(
                        symbol='triangle-up',
                        size=12,
                        color='#2ca02c',
                        line=dict(color='#1f5f1f', width=2)
                    ),
                    hovertemplate='BUY: €%{y:.4f}<br>%{x}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # 3. SELL MARKERS (red triangles down)
        sell_mask = ext_trades['Action'].isin(['SELL', 'Sell']) if 'Action' in ext_trades.columns else pd.Series([False] * len(ext_trades))
        sell_trades = ext_trades[sell_mask]
        
        if not sell_trades.empty and 'Close' in sell_trades.columns:
            fig.add_trace(
                go.Scatter(
                    x=sell_trades['Date'],
                    y=sell_trades['Close'],
                    mode='markers',
                    name='🔒 SELL',
                    marker=dict(
                        symbol='triangle-down',
                        size=12,
                        color='#d62728',
                        line=dict(color='#8b0000', width=2)
                    ),
                    hovertemplate='SELL: €%{y:.4f}<br>%{x}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # 4. EQUITY CURVE (orange line)
        if 'Equity' in ext_trades.columns:
            equity_data = ext_trades['Equity'].dropna()
            if not equity_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=ext_trades[ext_trades['Equity'].notna()]['Date'],
                        y=equity_data,
                        mode='lines',
                        name='Portfolio Equity',
                        line=dict(color='#ff7f0e', width=3),
                        hovertemplate='Equity: €%{y:.2f}<br>%{x}<extra></extra>'
                    ),
                    row=2, col=1
                )
        
        # Update layout for better visualization
        fig.update_layout(
            title=dict(
                text=f"📊 {ticker} Trading Analysis", 
                font=dict(size=16, color='#333')
            ),
            height=650,
            showlegend=True,
            hovermode='x unified',
            template='plotly_white',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Customize axes
        fig.update_xaxes(
            title_text="Date", 
            row=2, col=1,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        )
        fig.update_yaxes(
            title_text="Price (€)", 
            row=1, col=1,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        )
        fig.update_yaxes(
            title_text="Equity (€)", 
            row=2, col=1,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        )
        
        print(f"✅ Chart created successfully for {ticker}")
        return fig.to_html(include_plotlyjs='cdn', div_id=f"{ticker.replace('-', '_')}_chart")
        
    except Exception as e:
        print(f"❌ Chart creation error for {ticker}: {str(e)}")
        import traceback
        traceback.print_exc()
        return f'<p>Chart creation failed for {ticker}: {str(e)}</p>'

def run_live_backtest():
    """Run live backtest for all tickers and generate report"""
    print("🚀 STARTING LIVE BACKTEST SESSION")
    print("=" * 80)
    
    # Update CSV data first
    update_csv_data()
    
    all_results = {}
    all_trades = []
    successful_tickers = []
    failed_tickers = []
    
    # Run backtests for each ticker
    for ticker, config in crypto_tickers.items():
        try:
            print(f"\n📊 Processing {ticker}...")
            
            # Run backtest with full debugging
            result = run_backtest(ticker, config)
            
            print(f"   Backtest result keys: {result.keys() if result else 'None'}")
            
            if result and result.get('pnl_perc', 0) != 0:
                all_results[ticker] = result
                successful_tickers.append(ticker)
                
                # Extract ALL trades (not just last 14 days) for proper chart display
                trade_sources = ['extended_trades', 'matched_trades', 'trades']
                ext_trades = None
                
                for source in trade_sources:
                    if source in result and not result[source].empty:
                        ext_trades = result[source]
                        print(f"   Using {source} for {ticker} ({len(ext_trades)} records)")
                        break
                
                if ext_trades is not None:
                    # Filter trades from last 14 days for TABLE display only
                    two_weeks_ago = datetime.now().date() - timedelta(days=14)
                    
                    for idx, trade in ext_trades.iterrows():
                        try:
                            # Handle different date formats
                            trade_date = None
                            if 'Date' in trade:
                                trade_date = pd.to_datetime(trade['Date']).date()
                            elif hasattr(idx, 'date'):
                                trade_date = idx.date()
                            else:
                                trade_date = pd.to_datetime(idx).date()
                            
                            # Only add recent trades to the TRADES TABLE
                            if trade_date >= two_weeks_ago:
                                action = trade.get('Action', 'N/A')
                                if action in ['BUY', 'SELL', 'Buy', 'Sell']:
                                    price = trade.get('Close', 0)
                                    shares = calculate_shares(ticker, price, 
                                                            config['initialCapitalLong'],
                                                            config['order_round_factor'])
                                    
                                    pnl_value = trade.get('PnL', 0)
                                    pnl_display = f"{pnl_value:.2f}€" if pnl_value != 0 else 'N/A'
                                    
                                    all_trades.append({
                                        'Ticker': ticker,
                                        'Date': trade_date.strftime('%Y-%m-%d'),
                                        'Action': action.upper(),
                                        'Price': f"{price:.4f}",
                                        'Shares': shares,
                                        'Type': 'Matched Entry' if action.upper() == 'BUY' else 'Matched Exit',
                                        'PnL': pnl_display,
                                        'Status': 'OPEN' if action.upper() == 'BUY' else 'CLOSED'
                                    })
                        except Exception as e:
                            print(f"   Trade extraction error: {str(e)}")
                
                pnl_perc = result.get('pnl_perc', 0)
                print(f"   ✅ {ticker}: {pnl_perc:.1f}%")
            else:
                failed_tickers.append(ticker)
                print(f"   ❌ {ticker}: No valid backtest result")
                
        except Exception as e:
            failed_tickers.append(ticker)
            print(f"   ❌ {ticker}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Generate HTML report
    generate_html_report(all_results, all_trades, successful_tickers, failed_tickers)

def generate_html_report(all_results, all_trades, successful_tickers, failed_tickers):
    """Generate HTML report with charts"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"LIVE_backtest_report_{timestamp}.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Backtest Report - {timestamp}</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1, h2 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
            .summary {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .success {{ color: #28a745; font-weight: bold; }}
            .error {{ color: #dc3545; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #007bff; color: white; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #f8f9fa; }}
            tr:hover {{ background-color: #e3f2fd; }}
            .chart-container {{ margin: 30px 0; padding: 20px; background: #fafafa; border-radius: 8px; }}
        </style>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>Live Backtest Report - {datetime.now().strftime('%Y%m%d_%H%M%S')}</h1>
            
            <div class="summary">
                <h3>📊 Session Summary</h3>
                <p><span class="success">✅ Successful: {len(successful_tickers)} tickers</span></p>
                <p><span class="error">❌ Failed: {len(failed_tickers)} tickers</span></p>
                <p>📈 Total Trades (14 days): {len(all_trades)}</p>
            </div>
            
            <h2>Ticker PnL Übersicht</h2>
            <table>
                <tr>
                    <th>Ticker</th>
                    <th>PnL (%)</th>
                    <th>Past Window</th>
                    <th>Trade Window</th>
                    <th>Trades (2W)</th>
                </tr>
    """
    
    # Add ticker summary
    for ticker in successful_tickers:
        if ticker in all_results:
            result = all_results[ticker]
            trades_count = len([t for t in all_trades if t['Ticker'] == ticker])
            
            # Get optimization parameters if available
            past_window = result.get('best_past_window', 'None')
            trade_window = result.get('best_trade_window', 'None')
            
            html_content += f"""
                <tr>
                    <td><strong>{ticker}</strong></td>
                    <td class="success">{result.get('pnl_perc', 0):.1f}%</td>
                    <td>{past_window}</td>
                    <td>{trade_window}</td>
                    <td>{trades_count}</td>
                </tr>
            """
    
    html_content += """
            </table>
            
            <h2>Trades der letzten 14 Tage</h2>
            <table>
                <tr>
                    <th>Ticker</th>
                    <th>Datum</th>
                    <th>Aktion</th>
                    <th>Preis (€)</th>
                    <th>Shares</th>
                    <th>Typ</th>
                    <th>PnL</th>
                    <th>Status</th>
                </tr>
    """
    
    # Add trades
    for trade in sorted(all_trades, key=lambda x: x['Date'], reverse=True):
        action_style = "color: green;" if trade['Action'] == 'BUY' else "color: red;"
        html_content += f"""
            <tr>
                <td><strong>{trade['Ticker']}</strong></td>
                <td>{trade['Date']}</td>
                <td style="{action_style}"><strong>{trade['Action']}</strong></td>
                <td>€{trade['Price']}</td>
                <td>{trade['Shares']}</td>
                <td>{trade['Type']}</td>
                <td>{trade['PnL']}</td>
                <td>{trade['Status']}</td>
            </tr>
        """
    
    html_content += f"""
            </table>
            
            <p><strong>Anzahl Trades (14 Tage): {len(all_trades)}</strong></p>
            
            <h2>📊 Trading Charts</h2>
    """
    
    # Add charts for each ticker
    for ticker in successful_tickers:
        if ticker in all_results:
            chart_html = create_plotly_chart(ticker, all_results[ticker])
            if chart_html:
                html_content += f"""
                    <div class="chart-container">
                        <h3>{ticker} Analysis</h3>
                        {chart_html}
                    </div>
                """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Save and open report
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        file_path = os.path.abspath(report_filename)
        print(f"\n✅ LIVE BACKTEST REPORT erstellt: {report_filename}")
        print(f"📁 Pfad: {file_path}")
        print(f"🌐 Öffne im Browser: file:///{file_path.replace(chr(92), '/')}")
        
        # Open in browser
        webbrowser.open(f'file:///{file_path.replace(chr(92), "/")}')
        print("🚀 Browser geöffnet!")
        
        print("\n📊 HTML-Report erfolgreich erstellt und gespeichert!")
        
        # Console summary
        print("\n" + "="*50)
        print("📈 TICKER PnL SUMMARY")
        print("="*50)
        for ticker in successful_tickers:
            if ticker in all_results:
                pnl = all_results[ticker].get('pnl_perc', 0)
                print(f"{ticker:8} {pnl:8.0f}%")
        
    except Exception as e:
        print(f"❌ Report generation error: {str(e)}")

if __name__ == "__main__":
    run_live_backtest()
