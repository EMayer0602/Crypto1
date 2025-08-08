#!/usr/bin/env python3
"""
CLEAN LIVE BACKTEST - NO EMOJIS VERSION
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
    print("WARNING Plotly nicht verfügbar")

def create_plotly_chart(ticker, backtest_result):
    """Create interactive Plotly chart with buy/sell markers and equity curve"""
    if not PLOTLY_AVAILABLE:
        return "<p>Plotly nicht verfügbar für Charts</p>"
    
    try:
        print(f"Creating chart for {ticker}...")
        
        # Get data from backtest result
        df = backtest_result.get('df_bt')
        matched_trades = backtest_result.get('matched_trades')
        
        if df is None or df.empty:
            return f"<p>ERROR Keine Daten für {ticker} Charts</p>"
        
        # Create subplots: Price chart + Equity chart
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(f"{ticker} Price & Trading Signals", f"{ticker} Equity Curve"),
            vertical_spacing=0.15,
            row_heights=[0.7, 0.3],
            shared_xaxes=True
        )
        
        # 1. PRICE LINE (blue)
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name=f'{ticker} Price',
                line=dict(color='#1f77b4', width=2),
                hovertemplate=f'{ticker}: €%{{y:.4f}}<br>%{{x|%Y-%m-%d}}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 2. BUY/SELL SIGNALS from matched trades
        if matched_trades is not None and not matched_trades.empty:
            # BUY signals (green triangles up)
            buy_dates = []
            buy_prices = []
            sell_dates = []
            sell_prices = []
            equity_dates = []
            equity_values = []
            
            initial_capital = crypto_tickers[ticker]['initialCapitalLong']
            running_capital = initial_capital
            
            for idx, trade in matched_trades.iterrows():
                entry_date = pd.to_datetime(trade.get('Entry Date'))
                entry_price = trade.get('Entry Price', 0)
                
                if entry_date in df.index:
                    buy_dates.append(entry_date)
                    buy_prices.append(entry_price)
                    equity_dates.append(entry_date)
                    equity_values.append(running_capital)
                
                # SELL signal if trade is completed
                if not pd.isna(trade.get('Exit Date')):
                    exit_date = pd.to_datetime(trade.get('Exit Date'))
                    exit_price = trade.get('Exit Price', 0)
                    net_pnl = trade.get('Net PnL', 0)
                    
                    if exit_date in df.index:
                        sell_dates.append(exit_date)
                        sell_prices.append(exit_price)
                        running_capital += net_pnl
                        equity_dates.append(exit_date)
                        equity_values.append(running_capital)
            
            # Add BUY markers
            if buy_dates:
                fig.add_trace(
                    go.Scatter(
                        x=buy_dates,
                        y=buy_prices,
                        mode='markers',
                        name='BUY Signal',
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
            
            # Add SELL markers
            if sell_dates:
                fig.add_trace(
                    go.Scatter(
                        x=sell_dates,
                        y=sell_prices,
                        mode='markers',
                        name='SELL Signal',
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
            
            # Add EQUITY CURVE
            if equity_dates and equity_values:
                fig.add_trace(
                    go.Scatter(
                        x=equity_dates,
                        y=equity_values,
                        mode='lines+markers',
                        name='Portfolio Value',
                        line=dict(color='#ff7f0e', width=3),
                        marker=dict(size=6),
                        hovertemplate='Equity: €%{y:.2f}<br>%{x|%Y-%m-%d}<extra></extra>'
                    ),
                    row=2, col=1
                )
        
        # Layout customization
        fig.update_layout(
            title=dict(
                text=f"{ticker} Trading Analysis & Signals", 
                font=dict(size=18, color='#333')
            ),
            height=800,
            showlegend=True,
            hovermode='x unified',
            template='plotly_white',
            margin=dict(l=60, r=60, t=100, b=60)
        )
        
        # Customize axes
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price (€)", row=1, col=1)
        fig.update_yaxes(title_text="Portfolio Value (€)", row=2, col=1)
        
        print(f"   SUCCESS Chart created for {ticker}")
        return fig.to_html(include_plotlyjs='cdn', div_id=f"{ticker.replace('-', '_')}_chart")
        
    except Exception as e:
        error_msg = f"Chart error for {ticker}: {str(e)}"
        print(f"   ERROR {error_msg}")
        return f'<div style="color: red; padding: 20px; border: 1px solid red;"><h3>Chart Error for {ticker}</h3><p>{error_msg}</p></div>'

def run_live_backtest():
    """Run live backtest for all tickers"""
    print("LIVE BACKTEST SESSION STARTED")
    print("=" * 60)
    
    all_results = {}
    all_trades = []
    successful_tickers = []
    failed_tickers = []
    
    # Process each ticker
    for ticker, config in crypto_tickers.items():
        try:
            print(f"\nProcessing {ticker}...")
            
            # Run backtest
            result = run_backtest(ticker, config)
            
            # Calculate PnL from trade_statistics if available
            pnl_perc = 0
            if result and 'trade_statistics' in result and result['trade_statistics']:
                stats = result['trade_statistics']
                # Look for Total Return or Total PnL with emoji keys
                if 'Total Return' in stats:
                    pnl_value = stats['Total Return']
                elif 'Total PnL' in stats:
                    total_pnl = stats['Total PnL']
                    pnl_perc = (float(total_pnl.replace('€', '').replace(',', '')) / config['initialCapitalLong']) * 100
                else:
                    # Try alternative keys without emojis
                    for key, value in stats.items():
                        if 'Return' in key and '%' in str(value):
                            pnl_value = value
                            break
                
                # Handle string PnL (remove % and convert to float)
                if isinstance(pnl_value, str):
                    pnl_perc = float(pnl_value.replace('%', ''))
                else:
                    pnl_perc = pnl_value
            
            if result and (pnl_perc != 0 or ('matched_trades' in result and not result['matched_trades'].empty)):
                # Add calculated PnL and optimal parameters to result for later use
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
                
                print(f"   SUCCESS {ticker}: {pnl_perc:.1f}% PnL")
            else:
                failed_tickers.append(ticker)
                print(f"   ERROR {ticker}: No valid result")
                
        except Exception as e:
            failed_tickers.append(ticker)
            print(f"   ERROR {ticker}: {e}")
    
    # Console summary
    print("\n" + "="*50)
    print("FINAL PnL SUMMARY")
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
    
    # Generate minimal HTML report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"LIVE_backtest_report_{timestamp}.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Backtest Report - {timestamp}</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .summary {{ background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .pnl-positive {{ color: #00aa00; font-weight: bold; }}
            .pnl-negative {{ color: #cc0000; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Live Backtest Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h1>
        
        <div class="summary">
            <h2>Performance Summary</h2>
            <table>
                <tr><th>Ticker</th><th>PnL</th><th>Trades</th><th>Initial Capital</th><th>Past Window</th><th>Trade Window</th></tr>
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
        initial_capital = crypto_tickers[ticker]['initialCapitalLong']  # FIX: Use from crypto_tickers
        
        # Get optimal parameters
        past_window = result.get('optimal_past_window', 'N/A')
        trade_window = result.get('optimal_trade_window', 'N/A')
        
        html_content += f"""
                <tr>
                    <td><strong>{ticker}</strong></td>
                    <td class="{pnl_class}">{pnl_numeric:.1f}%</td>
                    <td>{trades_count}</td>
                    <td>€{initial_capital:,}</td>
                    <td>{past_window}</td>
                    <td>{trade_window}</td>
                </tr>
        """
    
    html_content += """
            </table>
        </div>
        
        <h2>Interactive Charts</h2>
    """
    
    # Add charts for each ticker
    for ticker in successful_tickers:
        result = all_results[ticker]
        chart_html = create_plotly_chart(ticker, result)
        html_content += f"""
        <div style="margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h3>{ticker} Chart</h3>
            {chart_html}
        </div>
        """
    
    html_content += """
        <h2>Recent Trades (Last 14 Days)</h2>
        <table>
            <tr>
                <th>Ticker</th>
                <th>Date</th>
                <th>Action</th>
                <th>Price</th>
                <th>Shares</th>
                <th>Type</th>
                <th>PnL</th>
                <th>Status</th>
            </tr>
    """
    
    # Sort trades by date (newest first)
    all_trades.sort(key=lambda x: x['Date'], reverse=True)
    
    for trade in all_trades:
        action_class = "pnl-positive" if trade['Action'] == 'BUY' else "pnl-negative"
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
    
    html_content += """
        </table>
        
        <p><em>Generated: """ + timestamp + """</em></p>
    </body>
    </html>
    """
    
    # Save HTML file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nHTML-Report saved: {filename}")
    print(f"Successful tickers: {len(successful_tickers)}")
    print(f"Total trades: {len(all_trades)}")

if __name__ == "__main__":
    run_live_backtest()
