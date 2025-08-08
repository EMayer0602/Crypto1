#!/usr/bin/env python3
"""
LIVE BACKTEST WITH FULL CHARTS - Die funktionierende Version
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import traceback
import webbrowser

# Imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest

# Plotly für Charts
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("WARNING Plotly nicht verfügbar - Charts werden ohne Plotly erstellt")

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

def create_plotly_chart(ticker, backtest_result, config):
    """Create interactive Plotly chart with all trade markers and equity curve"""
    if not PLOTLY_AVAILABLE:
        return "<p>Plotly nicht verfügbar für Charts</p>"
    
    try:
        print(f"📊 Creating chart for {ticker}...")
        
        # Get trade data from backtest result
        ext_trades = None
        
        # Try different data sources
        for source in ['extended_trades', 'matched_trades', 'trades']:
            if source in backtest_result and not backtest_result[source].empty:
                ext_trades = backtest_result[source].copy()
                print(f"   Using {source} data: {len(ext_trades)} records")
                break
        
        if ext_trades is None or ext_trades.empty:
            return f"<p>❌ Keine Trade-Daten für {ticker} gefunden</p>"
        
        # Ensure Date column
        if 'Date' not in ext_trades.columns:
            ext_trades = ext_trades.reset_index()
        
        if 'Date' not in ext_trades.columns:
            ext_trades['Date'] = ext_trades.index
        
        # Convert Date to datetime
        ext_trades['Date'] = pd.to_datetime(ext_trades['Date'])
        ext_trades = ext_trades.sort_values('Date')
        
        print(f"   Chart data: {len(ext_trades)} records from {ext_trades['Date'].min()} to {ext_trades['Date'].max()}")
        
        # Create subplots: Price chart + Equity chart
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(f"{ticker} Price & Trading Signals", f"{ticker} Equity Curve"),
            vertical_spacing=0.15,
            row_heights=[0.7, 0.3],
            shared_xaxes=True
        )
        
        # 1. PRICE LINE (blue)
        if 'Close' in ext_trades.columns:
            fig.add_trace(
                go.Scatter(
                    x=ext_trades['Date'],
                    y=ext_trades['Close'],
                    mode='lines',
                    name=f'{ticker} Price',
                    line=dict(color='#1f77b4', width=2),
                    hovertemplate=f'{ticker}: €%{{y:.4f}}<br>%{{x|%Y-%m-%d}}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # 2. BUY SIGNALS (green triangles up)
        if 'Action' in ext_trades.columns:
            buy_trades = ext_trades[ext_trades['Action'].isin(['BUY', 'Buy'])]
            if not buy_trades.empty and 'Close' in buy_trades.columns:
                fig.add_trace(
                    go.Scatter(
                        x=buy_trades['Date'],
                        y=buy_trades['Close'],
                        mode='markers',
                        name='🔓 BUY Signal',
                        marker=dict(
                            symbol='triangle-up',
                            size=14,
                            color='#00ff00',
                            line=dict(color='#008000', width=2)
                        ),
                        hovertemplate='BUY: €%{y:.4f}<br>%{x|%Y-%m-%d}<extra></extra>'
                    ),
                    row=1, col=1
                )
                print(f"   ✅ {len(buy_trades)} BUY markers added")
        
        # 3. SELL SIGNALS (red triangles down)
        if 'Action' in ext_trades.columns:
            sell_trades = ext_trades[ext_trades['Action'].isin(['SELL', 'Sell'])]
            if not sell_trades.empty and 'Close' in sell_trades.columns:
                fig.add_trace(
                    go.Scatter(
                        x=sell_trades['Date'],
                        y=sell_trades['Close'],
                        mode='markers',
                        name='🔒 SELL Signal',
                        marker=dict(
                            symbol='triangle-down',
                            size=14,
                            color='#ff0000',
                            line=dict(color='#800000', width=2)
                        ),
                        hovertemplate='SELL: €%{y:.4f}<br>%{x|%Y-%m-%d}<extra></extra>'
                    ),
                    row=1, col=1
                )
                print(f"   ✅ {len(sell_trades)} SELL markers added")
        
        # 4. EQUITY CURVE (orange)
        if 'Equity' in ext_trades.columns:
            equity_data = ext_trades.dropna(subset=['Equity'])
            if not equity_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=equity_data['Date'],
                        y=equity_data['Equity'],
                        mode='lines',
                        name='Portfolio Value',
                        line=dict(color='#ff7f0e', width=3),
                        fill='tonexty',
                        hovertemplate='Equity: €%{y:.2f}<br>%{x|%Y-%m-%d}<extra></extra>'
                    ),
                    row=2, col=1
                )
                print(f"   ✅ Equity curve added with {len(equity_data)} points")
        
        # Layout customization
        fig.update_layout(
            title=dict(
                text=f"📊 {ticker} Trading Analysis & Signals", 
                font=dict(size=18, color='#333')
            ),
            height=800,
            showlegend=True,
            hovermode='x unified',
            template='plotly_white',
            margin=dict(l=60, r=60, t=100, b=60)
        )
        
        # Customize axes
        fig.update_xaxes(
            title_text="Date", 
            row=2, col=1,
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)'
        )
        fig.update_yaxes(
            title_text="Price (€)", 
            row=1, col=1,
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)'
        )
        fig.update_yaxes(
            title_text="Portfolio Value (€)", 
            row=2, col=1,
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)'
        )
        
        print(f"   ✅ Chart created successfully for {ticker}")
        return fig.to_html(include_plotlyjs='cdn', div_id=f"{ticker.replace('-', '_')}_chart")
        
    except Exception as e:
        error_msg = f"Chart error for {ticker}: {str(e)}"
        print(f"   ❌ {error_msg}")
        traceback.print_exc()
        return f'<div style="color: red; padding: 20px; border: 1px solid red;"><h3>Chart Error for {ticker}</h3><p>{error_msg}</p></div>'

def run_live_backtest():
    """Run live backtest for all tickers"""
    print("🚀 LIVE BACKTEST SESSION GESTARTET")
    print("=" * 60)
    
    all_results = {}
    all_trades = []
    successful_tickers = []
    failed_tickers = []
    
    # Process each ticker
    for ticker, config in crypto_tickers.items():
        try:
            print(f"\n📊 Processing {ticker}...")
            
            # Run backtest
            result = run_backtest(ticker, config)
            
            # Calculate PnL from trade_statistics if available
            pnl_perc = 0
            if result and 'trade_statistics' in result and result['trade_statistics']:
                stats = result['trade_statistics']
                # Look for Total Return or Total PnL with emoji keys
                if '📊 Total Return' in stats:
                    pnl_str = stats['📊 Total Return']
                    # Extract percentage number from string like "25.40%"
                    if isinstance(pnl_str, str) and pnl_str.endswith('%'):
                        pnl_perc = float(pnl_str.replace('%', ''))
                    else:
                        pnl_perc = float(pnl_str)
                    print(f"   💰 Total Return from DEBUG: {pnl_perc}%")
                elif '💰 Total PnL' in stats:
                    # If we have Total PnL, calculate percentage
                    total_pnl = stats['💰 Total PnL']
                    pnl_perc = (total_pnl / config['initialCapitalLong']) * 100
                elif 'total_return_pct' in stats:
                    pnl_perc = stats['total_return_pct']
                elif 'net_profit_pct' in stats:
                    pnl_perc = stats['net_profit_pct']
                elif 'return_pct' in stats:
                    pnl_perc = stats['return_pct']
            
            if result and (pnl_perc != 0 or ('matched_trades' in result and not result['matched_trades'].empty)):
                # Add calculated PnL to result for later use
                result['pnl_perc'] = pnl_perc
                all_results[ticker] = result
                successful_tickers.append(ticker)
                
                # Extract recent trades for table
                if 'matched_trades' in result and not result['matched_trades'].empty:
                    trades_df = result['matched_trades']
                    
                    # Get last 14 days of trades for table
                    cutoff_date = datetime.now().date() - timedelta(days=14)
                    
                    for idx, trade in trades_df.iterrows():
                        try:
                            # Handle Entry (BUY)
                            entry_date = pd.to_datetime(trade.get('Entry Date', idx)).date()
                            if entry_date >= cutoff_date:
                                entry_price = trade.get('Entry Price', 0)
                                quantity = trade.get('Quantity', 0)
                                
                                # Use actual shares from matched_trades, formatted properly
                                order_round_factor = config.get('order_round_factor', 0.001)
                                if order_round_factor < 1:
                                    shares_str = f"{quantity:.{len(str(order_round_factor).split('.')[-1]) if '.' in str(order_round_factor) else 3}f}"
                                else:
                                    shares_str = f"{quantity:,.0f}"
                                
                                all_trades.append({
                                    'Ticker': ticker,
                                    'Date': entry_date.strftime('%Y-%m-%d'),
                                    'Action': 'BUY',
                                    'Price': f"{entry_price:.4f}",
                                    'Shares': shares_str,
                                    'Type': 'Entry',
                                    'PnL': 'N/A',
                                    'Status': 'OPEN' if pd.isna(trade.get('Exit Date')) else 'CLOSED'
                                })
                            
                            # Handle Exit (SELL) if exists
                            if not pd.isna(trade.get('Exit Date')):
                                exit_date = pd.to_datetime(trade.get('Exit Date')).date()
                                if exit_date >= cutoff_date:
                                    exit_price = trade.get('Exit Price', 0)
                                    net_pnl = trade.get('Net PnL', 0)
                                    
                                    all_trades.append({
                                        'Ticker': ticker,
                                        'Date': exit_date.strftime('%Y-%m-%d'),
                                        'Action': 'SELL',
                                        'Price': f"{exit_price:.4f}",
                                        'Shares': shares_str,
                                        'Type': 'Exit',
                                        'PnL': f"{net_pnl:.2f}€",
                                        'Status': 'CLOSED'
                                    })
                        except Exception as e:
                            print(f"     Trade extraction error: {e}")
                
                pnl = result.get('pnl_perc', 0)
                print(f"   ✅ {ticker}: {pnl:.1f}% PnL")
            else:
                failed_tickers.append(ticker)
                print(f"   ❌ {ticker}: No valid result")
                
        except Exception as e:
            failed_tickers.append(ticker)
            print(f"   ❌ {ticker}: {e}")
    
    # Generate HTML report
    generate_html_report(all_results, all_trades, successful_tickers, failed_tickers)
    
    # Console summary
    print("\n" + "="*50)
    print("📈 FINAL PnL SUMMARY")
    print("="*50)
    for ticker in successful_tickers:
        pnl = all_results[ticker].get('pnl_perc', 0)
        # Handle string PnL (remove % and convert to float)
        if isinstance(pnl, str):
            pnl_numeric = float(pnl.replace('%', ''))
        else:
            pnl_numeric = pnl
        print(f"{ticker:8} {pnl_numeric:8.0f}%")
    print("="*50)

def generate_html_report(all_results, all_trades, successful_tickers, failed_tickers):
    """Generate comprehensive HTML report with charts"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"LIVE_backtest_report_{timestamp}.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Backtest Report - {timestamp}</title>
        <meta charset="UTF-8">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
            .container {{ max-width: 1600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; text-align: center; font-size: 2.5em; margin-bottom: 30px; border-bottom: 3px solid #3498db; padding-bottom: 15px; }}
            h2 {{ color: #34495e; border-left: 5px solid #3498db; padding-left: 15px; margin-top: 40px; }}
            .summary {{ background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; padding: 25px; border-radius: 12px; margin: 30px 0; }}
            .success {{ color: #27ae60; font-weight: bold; }}
            .error {{ color: #e74c3c; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin: 25px 0; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            th {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; text-align: left; font-weight: 600; }}
            td {{ padding: 12px 15px; border-bottom: 1px solid #ecf0f1; }}
            tr:hover {{ background-color: #f8f9fa; }}
            .chart-container {{ margin: 40px 0; padding: 20px; background: #fafafa; border-radius: 12px; border: 1px solid #e1e8ed; }}
            .pnl-positive {{ color: #27ae60; font-weight: bold; }}
            .pnl-negative {{ color: #e74c3c; font-weight: bold; }}
            .buy-action {{ color: #27ae60; font-weight: bold; }}
            .sell-action {{ color: #e74c3c; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Live Backtest Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h1>
            
            <div class="summary">
                <h3>📊 Session Summary</h3>
                <p><strong>✅ Successful Backtests:</strong> {len(successful_tickers)} tickers</p>
                <p><strong>❌ Failed Backtests:</strong> {len(failed_tickers)} tickers</p>
                <p><strong>📈 Recent Trades:</strong> {len(all_trades)} trades (last 14 days)</p>
            </div>
    """
    
    # PnL Overview Table
    html_content += """
            <h2>💰 PnL Performance Overview</h2>
            <table>
                <tr>
                    <th>Ticker</th>
                    <th>PnL (%)</th>
                    <th>Past Window</th>
                    <th>Trade Window</th>
                    <th>Recent Trades</th>
                    <th>Status</th>
                </tr>
    """
    
    for ticker in successful_tickers:
        result = all_results[ticker]
        pnl = result.get('pnl_perc', 0)
        trades_count = len([t for t in all_trades if t['Ticker'] == ticker])
        
        # Handle string PnL (remove % and convert to float)
        if isinstance(pnl, str):
            pnl_numeric = float(pnl.replace('%', ''))
        else:
            pnl_numeric = pnl
            
        pnl_class = "pnl-positive" if pnl_numeric > 0 else "pnl-negative"
        
        past_window = result.get('best_past_window', 'Optimized')
        trade_window = result.get('best_trade_window', 'Dynamic')
        
        html_content += f"""
                <tr>
                    <td><strong>{ticker}</strong></td>
                    <td class="{pnl_class}">{pnl_numeric:.1f}%</td>
                    <td>{past_window}</td>
                    <td>{trade_window}</td>
                    <td>{trades_count}</td>
                    <td class="success">✅ Active</td>
                </tr>
        """
    
    # Recent Trades Table
    html_content += """
            </table>
            
            <h2>📋 Recent Trading Activity (Last 14 Days)</h2>
            <table>
                <tr>
                    <th>Ticker</th>
                    <th>Date</th>
                    <th>Action</th>
                    <th>Price (€)</th>
                    <th>Shares</th>
                    <th>Type</th>
                    <th>PnL</th>
                    <th>Status</th>
                </tr>
    """
    
    # Sort trades by date (newest first)
    sorted_trades = sorted(all_trades, key=lambda x: x['Date'], reverse=True)
    
    for trade in sorted_trades:
        action_class = "buy-action" if trade['Action'] == 'BUY' else "sell-action"
        html_content += f"""
                <tr>
                    <td><strong>{trade['Ticker']}</strong></td>
                    <td>{trade['Date']}</td>
                    <td class="{action_class}">{trade['Action']}</td>
                    <td>€{trade['Price']}</td>
                    <td>{trade['Shares']}</td>
                    <td>{trade['Type']}</td>
                    <td>{trade['PnL']}</td>
                    <td>{trade['Status']}</td>
                </tr>
        """
    
    html_content += f"""
            </table>
            <p><strong>Total Trades: {len(all_trades)}</strong></p>
            
            <h2>📊 Interactive Trading Charts</h2>
    """
    
    # Add charts for each successful ticker
    for ticker in successful_tickers:
        config = crypto_tickers[ticker]
        chart_html = create_plotly_chart(ticker, all_results[ticker], config)
        
        html_content += f"""
            <div class="chart-container">
                <h3>📈 {ticker} Analysis</h3>
                {chart_html}
            </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Save report
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        file_path = os.path.abspath(filename)
        print(f"\n✅ LIVE BACKTEST REPORT erstellt: {filename}")
        print(f"📁 Pfad: {file_path}")
        print(f"🌐 Browser-URL: file:///{file_path.replace(chr(92), '/')}")
        
        # Open in browser
        webbrowser.open(f'file:///{file_path.replace(chr(92), "/")}')
        print("🚀 Browser geöffnet!")
        
        print("\n📊 HTML-Report erfolgreich erstellt und gespeichert!")
        
    except Exception as e:
        print(f"❌ Report generation error: {e}")

if __name__ == "__main__":
    run_live_backtest()
