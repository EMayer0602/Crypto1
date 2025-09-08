import warnings
warnings.simplefilter("ignore", category=FutureWarning)
import traceback
import webbrowser
import os
import csv
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib
import time
from trade_execution import prepare_orders_from_trades, execute_trade, submit_order_bitpanda, save_all_orders_html_report
from config import COMMISSION_RATE, MIN_COMMISSION, ORDER_ROUND_FACTOR, backtesting_begin, backtesting_end, backtest_years
from crypto_tickers import crypto_tickers
from signal_utils import (
    calculate_support_resistance,
    compute_trend,
    assign_long_signals,
    assign_long_signals_extended,
    update_level_close_long,
    simulate_trades_compound_extended,
    berechne_best_p_tw_long,
)
from trades_weekly_display import display_weekly_trades_console, create_weekly_trades_html, add_weekly_trades_to_existing_reports
from plotly_utils import (
    plotly_combined_chart_and_equity,
    display_extended_trades_table,
    format_trading_tables,
    create_trades_dataframe,
    print_statistics_table,
    create_equity_curve_from_matched_trades
)
from report_generator import generate_combined_report_from_memory

# --- Globale Variablen ---
TRADING_MODE = "paper_trading"
API_KEY = ""
capital_plots = {}
CSV_PATH = "C:\\Users\\Edgar.000\\Documents\\____Trading strategies\\Crypto_trading1"
base_dir = "C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading1"

def load_crypto_data_yf(symbol, backtest_years=1, max_retries=3):
    """Load OHLCV daily data for a symbol from local CSV (preferred) or yfinance.
    Trim to the most recent backtest_years years.
    Expected CSV format: <SYMBOL>_daily.csv with columns Date,Open,High,Low,Close,Volume.

    Reproducibility features:
      - If env var STABLE_BACKTEST=1 is set, skip generating an artificial partial bar for the current day.
      - Prints a dataset signature (row count + SHA1 hash of Close series) so results can be compared across runs.
    """
    try:
        csv_filename = f"{symbol}_daily.csv"
        csv_path = os.path.join(os.getcwd(), csv_filename)

        if os.path.exists(csv_path):
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(csv_path))
            print(f"Loading {symbol} from CSV cache ({csv_filename}) - Age: {file_age.days} days")
            df = pd.read_csv(csv_path)
        else:
            print(f"CSV {csv_filename} not found. Downloading from yfinance…")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=int(backtest_years*365)+5)
            df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval='1d', auto_adjust=True, progress=False)
            if df is None or df.empty:
                print(f"❌ No data downloaded for {symbol}")
                return None
            df.reset_index(inplace=True)
            df.rename(columns={c: c.strip() for c in df.columns}, inplace=True)
            df.to_csv(csv_path, index=False)
            print(f"Saved fresh data to {csv_filename}")

        # Standardize columns
        rename_map = {c: c.title() for c in ['open','high','low','close','volume']}
        df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)
        date_col = 'Date' if 'Date' in df.columns else 'date'
        df[date_col] = pd.to_datetime(df[date_col])
        df.set_index(date_col, inplace=True)
        df = df.sort_index()

        # Trim to backtest_years
        cutoff = df.index.max() - timedelta(days=int(backtest_years*365)+2)
        df = df[df.index >= cutoff]

        # Optional: remove today's artificial bar for stable backtests
        if os.environ.get("STABLE_BACKTEST", "0") == "1":
            today = datetime.now().date()
            if df.index.max().date() == today:
                print("🧊 STABLE_BACKTEST active -> dropping today's partial bar for reproducibility")
                df = df[df.index.date < today]

        # Dataset signature
        try:
            close_bytes = b"|".join([f"{v:.8f}".encode() for v in df['Close'].astype(float).values])
            sha = hashlib.sha1(close_bytes).hexdigest()[:12]
            print(f"🆔 Dataset signature {symbol}: rows={len(df)}, sha1={sha}")
        except Exception as sig_err:
            print(f"⚠️ Could not compute dataset signature: {sig_err}")

        return df
    except Exception as e:
        print(f"❌ Error loading data for {symbol}: {e}")
        traceback.print_exc()
        return None

def run_live_backtest_analysis():
    """
    UNIFIED LIVE BACKTEST ANALYSIS - Kombiniert beide Reports
    Führt alle Backtests aus und erstellt vereinigten HTML-Report mit Strategy und Live Analysis
    """
    try:
        import webbrowser
        from datetime import datetime, timedelta
        
        print("🚀 UNIFIED LIVE CRYPTO BACKTEST STARTING...")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Update CSV files with intelligent update logic
        try:
            from smart_csv_update import smart_update_csv_files
            print("\n🧠 Intelligent CSV update (only necessary data)...")
            smart_update_csv_files()
            print("✅ Smart CSV update completed!")
        except Exception as e:
            print(f"❌ Smart CSV update failed, falling back to full update: {e}")
            # Fallback to old method
            try:
                from get_real_crypto_data import update_csv_files_with_realtime_data
                print("\n🔄 Fallback: Full CSV update...")
                update_csv_files_with_realtime_data()
                print("✅ Fallback CSV update completed!")
            except Exception as e2:
                print(f"❌ Both update methods failed: {e2}")
        
        # Optional: repair last two daily bars (keep today's artificial)
        if os.environ.get('REPAIR_RECENT', '0') == '1':
            try:
                print("\n🛠️ Repairing recent daily bars (REPAIR_RECENT=1)…")
                import subprocess, sys
                subprocess.run([sys.executable, 'repair_recent_daily_data.py'], check=False)
            except Exception as _rep_err:
                print(f"⚠️ Repair step failed: {_rep_err}")

        # Run backtests for all tickers
        all_results = {}
        
        print(f"\n📋 Processing {len(crypto_tickers)} tickers...")
        for i, (ticker, config) in enumerate(crypto_tickers.items(), 1):
            print(f"\n[{i}/{len(crypto_tickers)}] Processing {ticker}...")
            result = run_backtest(ticker, config)
            all_results[ticker] = result
        
        # Create UNIFIED comprehensive HTML report
        print("\n📝 Creating UNIFIED comprehensive HTML report...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Enhanced HTML template with styling
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🚀 UNIFIED Crypto Trading Analysis Report {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; line-height: 1.6; }}
                .container {{ max-width: 1400px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; }}
                .header {{ text-align: center; color: #2c3e50; margin-bottom: 30px; background: linear-gradient(45deg, #3498db, #2ecc71); color: white; padding: 20px; border-radius: 10px; }}
                .summary {{ background-color: #e8f4fd; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                .ticker-section {{ margin-bottom: 40px; border-bottom: 3px solid #eee; padding-bottom: 20px; page-break-inside: avoid; }}
                .ticker-header {{ color: #27ae60; font-size: 24px; margin-bottom: 15px; background: #ecf0f1; padding: 15px; border-radius: 8px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                .metric {{ background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid #dee2e6; }}
                .metric-value {{ font-size: 20px; font-weight: bold; color: #2c3e50; }}
                .metric-label {{ font-size: 14px; color: #7f8c8d; margin-top: 5px; }}
                .trades-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .trades-table th, .trades-table td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                .trades-table th {{ background-color: #3498db; color: white; font-weight: bold; text-align: center; }}
                .trades-table tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .trades-table tr:hover {{ background-color: #d5dbdb; }}
                .buy-row {{ background-color: #d5f4e6; }}
                .sell-row {{ background-color: #ffeaa7; }}
                .chart-section {{ margin: 20px 0; text-align: center; background: #f8f9fa; padding: 15px; border-radius: 8px; }}
                .strategy-section {{ background: #fff3cd; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ffc107; }}
                .signal-badge {{ display: inline-block; margin: 3px; padding: 6px 12px; border-radius: 15px; color: white; font-size: 12px; font-weight: bold; }}
                .buy-signal {{ background: #3498db; }}
                .sell-signal {{ background: #e74c3c; }}
                .support-signal {{ background: #27ae60; }}
                .resistance-signal {{ background: #e67e22; }}
                .positive {{ color: #27ae60; font-weight: bold; }}
                .negative {{ color: #e74c3c; font-weight: bold; }}
                .neutral {{ color: #f39c12; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 UNIFIED Crypto Trading Analysis Report</h1>
                    <h2>📊 Live Analysis + Strategy Overview</h2>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
        """
        
        # Enhanced Summary section with Strategy Analysis
        total_pnl = 0
        total_trades = 0
        successful_backtests = 0
        best_performer = {"ticker": "N/A", "pnl": 0}
        worst_performer = {"ticker": "N/A", "pnl": 0}
        
        for ticker, result in all_results.items():
            if result and isinstance(result, dict) and result.get('success'):
                final_capital = result.get('final_capital', 0)
                initial_capital = result.get('config', {}).get('initialCapitalLong', 10000)
                pnl_pct = ((final_capital / initial_capital - 1) * 100) if initial_capital > 0 else 0
                total_pnl += pnl_pct
                successful_backtests += 1
                
                # Track best and worst performers
                if pnl_pct > best_performer["pnl"]:
                    best_performer = {"ticker": ticker, "pnl": pnl_pct}
                if pnl_pct < worst_performer["pnl"]:
                    worst_performer = {"ticker": ticker, "pnl": pnl_pct}
                
                trades_df = result.get('matched_trades', pd.DataFrame())
                if not trades_df.empty:
                    total_trades += len(trades_df)
        
        avg_pnl = total_pnl / successful_backtests if successful_backtests > 0 else 0
        
        html_content += f"""
                <div class="summary">
                    <h2>📊 Unified Portfolio Summary</h2>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value">{successful_backtests}</div>
                            <div class="metric-label">Active Tickers</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value {'positive' if avg_pnl > 0 else 'negative' if avg_pnl < 0 else 'neutral'}">{avg_pnl:.2f}%</div>
                            <div class="metric-label">Average Return</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{total_trades}</div>
                            <div class="metric-label">Total Trades</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value {'positive' if best_performer['pnl'] > 0 else 'neutral'}">{best_performer['ticker']}</div>
                            <div class="metric-label">Best Performer ({best_performer['pnl']:.2f}%)</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value {'negative' if worst_performer['pnl'] < 0 else 'neutral'}">{worst_performer['ticker']}</div>
                            <div class="metric-label">Worst Performer ({worst_performer['pnl']:.2f}%)</div>
                        </div>
                    </div>
                </div>
        """
        
        # Enhanced Ticker sections with Strategy + Live Analysis
        for ticker, result in all_results.items():
            if not result or not isinstance(result, dict) or not result.get('success'):
                continue
                
            config = result.get('config', {})
            initial_capital = config.get('initialCapitalLong', 10000)
            final_capital = result.get('final_capital', initial_capital)
            total_return_pct = ((final_capital / initial_capital - 1) * 100) if initial_capital > 0 else 0
            
            matched_trades = result.get('matched_trades', pd.DataFrame())
            ext_signals = result.get('ext_signals', pd.DataFrame())
            optimal_p = result.get('optimal_past_window', 'N/A')
            optimal_tw = result.get('optimal_trade_window', 'N/A')
            
            # Calculate win rate
            winning_trades = 0
            losing_trades = 0
            if not matched_trades.empty and 'Net PnL' in matched_trades.columns:
                winning_trades = len(matched_trades[matched_trades['Net PnL'] > 0])
                losing_trades = len(matched_trades[matched_trades['Net PnL'] < 0])
            win_rate = (winning_trades / (winning_trades + losing_trades) * 100) if (winning_trades + losing_trades) > 0 else 0
            
            html_content += f"""
                <div class="ticker-section">
                    <h2 class="ticker-header">💎 {ticker} - Complete Analysis</h2>
                    
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value">€{initial_capital:,.0f}</div>
                            <div class="metric-label">Initial Capital</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">€{final_capital:,.2f}</div>
                            <div class="metric-label">Final Capital</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value {'positive' if total_return_pct > 0 else 'negative' if total_return_pct < 0 else 'neutral'}">{total_return_pct:.2f}%</div>
                            <div class="metric-label">Total Return</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{len(matched_trades)}</div>
                            <div class="metric-label">Total Trades</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">p={optimal_p}, tw={optimal_tw}</div>
                            <div class="metric-label">Optimal Parameters</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value {'positive' if win_rate > 50 else 'negative' if win_rate < 50 else 'neutral'}">{win_rate:.1f}%</div>
                            <div class="metric-label">Win Rate ({winning_trades}W/{losing_trades}L)</div>
                        </div>
                    </div>
            """
            
            # Strategy Analysis Section
            if not ext_signals.empty:
                # Signal Counts
                buy_signals = ext_signals[ext_signals['Action'] == 'buy'] if 'Action' in ext_signals.columns else pd.DataFrame()
                sell_signals = ext_signals[ext_signals['Action'] == 'sell'] if 'Action' in ext_signals.columns else pd.DataFrame()
                support_levels = ext_signals[ext_signals['Supp/Resist'] == 'support'] if 'Supp/Resist' in ext_signals.columns else pd.DataFrame()
                resistance_levels = ext_signals[ext_signals['Supp/Resist'] == 'resistance'] if 'Supp/Resist' in ext_signals.columns else pd.DataFrame()
                
                html_content += f"""
                    <div class="strategy-section">
                        <h3>🎯 Strategy Analysis - Extended Signals</h3>
                        <div style='margin:15px 0'>
                            <span class='signal-badge buy-signal'>🔵 {len(buy_signals)} BUY</span>
                            <span class='signal-badge sell-signal'>🟠 {len(sell_signals)} SELL</span>
                            <span class='signal-badge support-signal'>🟢 {len(support_levels)} SUPPORT</span>
                            <span class='signal-badge resistance-signal'>🔴 {len(resistance_levels)} RESISTANCE</span>
                        </div>
                """
                
                # Recent Signals (last 5)
                recent_signals = ext_signals.tail(5) if not ext_signals.empty else pd.DataFrame()
                if not recent_signals.empty:
                    html_content += """
                        <h4>📍 Latest 5 Extended Signals</h4>
                        <table class="trades-table">
                            <tr>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Action</th>
                                <th>Level</th>
                                <th>Signal</th>
                            </tr>
                    """
                    
                    for _, signal in recent_signals.iterrows():
                        date = signal.get('Long Date detected', 'N/A')
                        sig_type = signal.get('Supp/Resist', 'N/A')
                        action = signal.get('Action', 'N/A')
                        level = signal.get('Level high/low', 0)
                        extended = signal.get('Long Signal Extended', False)
                        
                        html_content += f"""
                            <tr>
                                <td>{date}</td>
                                <td>{sig_type}</td>
                                <td><strong>{action.upper() if action != 'N/A' else 'NONE'}</strong></td>
                                <td>€{level:.4f}</td>
                                <td>{'✅' if extended else '❌'}</td>
                            </tr>
                        """
                    
                    html_content += "</table>"
                html_content += "</div>"
            
            # Create interactive chart using robust function
            try:
                print(f"\n📊 Creating chart for {ticker}...")
                
                df = result.get('df')
                ext_signals = result.get('ext_signals', pd.DataFrame())
                equity_curve = result.get('equity_curve', [])
                buyhold_curve = result.get('buyhold_curve', [])
                
                # Extract Support/Resistance from ext_signals
                support_series = pd.Series(dtype=float)
                resistance_series = pd.Series(dtype=float)
                
                if not ext_signals.empty:
                    # Support levels
                    support_data = ext_signals[ext_signals['Supp/Resist'] == 'support']
                    if not support_data.empty:
                        support_dates = pd.to_datetime(support_data['Date high/low'])
                        support_levels = support_data['Level high/low'].values
                        support_series = pd.Series(support_levels, index=support_dates)
                    
                    # Resistance levels
                    resistance_data = ext_signals[ext_signals['Supp/Resist'] == 'resistance']
                    if not resistance_data.empty:
                        resistance_dates = pd.to_datetime(resistance_data['Date high/low'])
                        resistance_levels = resistance_data['Level high/low'].values
                        resistance_series = pd.Series(resistance_levels, index=resistance_dates)
                
                if df is not None and not df.empty and len(equity_curve) > 0:
                    chart_success = plotly_combined_chart_and_equity(
                        df=df,
                        standard_signals=ext_signals,
                        support=support_series,
                        resistance=resistance_series,
                        equity_curve=equity_curve,
                        buyhold_curve=buyhold_curve,
                        ticker=ticker,
                        backtest_years=backtest_years,
                        initial_capital=initial_capital
                    )
                    
                    if chart_success:
                        chart_filename = f"chart_{ticker.replace('-', '_')}.html"
                        html_content += f"""
                            <div class="chart-section">
                                <h3>📈 Interactive Chart</h3>
                                <p>📊 <a href="{chart_filename}" target="_blank">🔗 Click here to view interactive chart for {ticker}</a></p>
                            </div>
                        """
                        print(f"   ✅ Chart created for {ticker}")
                    else:
                        html_content += f"""
                            <div class="chart-section">
                                <h3>❌ Chart Error</h3>
                                <p>Failed to create chart for {ticker}</p>
                            </div>
                        """
                        print(f"   ❌ Chart failed for {ticker}")
                else:
                    print(f"   ⚠️ No data available for chart: {ticker}")
                    
            except Exception as e:
                print(f"   ❌ Chart error for {ticker}: {e}")
                html_content += f"""
                    <div class="chart-section">
                        <h3>❌ Chart Error</h3>
                        <p>Error creating chart for {ticker}: {str(e)}</p>
                    </div>
                """
            
            # Enhanced Recent trades (last 14 days) with Shares and Commission
            if not matched_trades.empty:
                # Filter for last 14 days
                cutoff_date = datetime.now() - timedelta(days=14)
                matched_trades['Entry Date'] = pd.to_datetime(matched_trades['Entry Date'])
                recent_trades = matched_trades[matched_trades['Entry Date'] >= cutoff_date]
                
                if not recent_trades.empty:
                    html_content += f"""
                        <h3>📅 Recent Live Trades (Last 14 Days)</h3>
                        <table class="trades-table">
                            <tr>
                                <th>Entry Date</th>
                                <th>Exit Date</th>
                                <th>Action</th>
                                <th>Entry Price</th>
                                <th>Exit Price</th>
                                <th>Shares/Quantity</th>
                                <th>Commission</th>
                                <th>Gross PnL</th>
                                <th>Net PnL</th>
                                <th>Status</th>
                            </tr>
                    """
                    
                    for _, trade in recent_trades.iterrows():
                        status = trade.get('Status', 'CLOSED')
                        row_class = "buy-row" if status == "OPEN" else "sell-row"
                        
                        # Extract trade details
                        entry_date = trade.get('Entry Date', 'N/A')
                        exit_date = trade.get('Exit Date', 'N/A') if status == 'CLOSED' else 'Current'
                        entry_price = trade.get('Entry Price', 0)
                        exit_price = trade.get('Exit Price', 0)
                        quantity = trade.get('Quantity', 0)
                        commission = trade.get('Commission', 0)
                        gross_pnl = trade.get('PnL', 0)
                        net_pnl = trade.get('Net PnL', 0)
                        
                        # Determine action based on status and PnL
                        if status == "OPEN":
                            action = "🔓 BUY (OPEN)"
                        else:
                            action = "🔒 BUY → SELL"
                        
                        html_content += f"""
                            <tr class="{row_class}">
                                <td>{entry_date}</td>
                                <td>{exit_date}</td>
                                <td><strong>{action}</strong></td>
                                <td>€{entry_price:.4f}</td>
                                <td>€{exit_price:.4f}</td>
                                <td>{quantity:,.4f}</td>
                                <td>€{commission:.2f}</td>
                                <td class="{'positive' if gross_pnl > 0 else 'negative' if gross_pnl < 0 else 'neutral'}">€{gross_pnl:,.2f}</td>
                                <td class="{'positive' if net_pnl > 0 else 'negative' if net_pnl < 0 else 'neutral'}">€{net_pnl:,.2f}</td>
                                <td>{status}</td>
                            </tr>
                        """
                    
                    html_content += "</table>"
                    
                    # Trade Summary
                    total_net_pnl = recent_trades['Net PnL'].sum() if 'Net PnL' in recent_trades.columns else 0
                    total_commission = recent_trades['Commission'].sum() if 'Commission' in recent_trades.columns else 0
                    total_quantity = recent_trades['Quantity'].sum() if 'Quantity' in recent_trades.columns else 0
                    
                    html_content += f"""
                        <div class="summary" style="margin-top:15px;">
                            <h4>📊 14-Day Trading Summary</h4>
                            <div class="metrics">
                                <div class="metric">
                                    <div class="metric-value">{len(recent_trades)}</div>
                                    <div class="metric-label">Recent Trades</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value {'positive' if total_net_pnl > 0 else 'negative' if total_net_pnl < 0 else 'neutral'}">€{total_net_pnl:,.2f}</div>
                                    <div class="metric-label">Net PnL</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value">€{total_commission:.2f}</div>
                                    <div class="metric-label">Total Fees</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-value">{total_quantity:,.4f}</div>
                                    <div class="metric-label">Total Volume</div>
                                </div>
                            </div>
                        </div>
                    """
                else:
                    html_content += "<p>ℹ️ No trades in the last 14 days</p>"
            else:
                html_content += "<p>ℹ️ No trades found</p>"
            
            html_content += "</div>"
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Save UNIFIED HTML report in reports folder
        os.makedirs("reports", exist_ok=True)  # ✅ Ensure reports folder exists
        report_filename = f"reports/UNIFIED_crypto_report_{timestamp}.html"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ UNIFIED HTML report saved: {report_filename}")
        
        # Open in browser
        try:
            webbrowser.open(f'file://{os.path.abspath(report_filename)}')
            print("🌐 Report opened in browser")
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
        
        # Summary console output
        print(f"\n{'='*80}")
        print("📊 FINAL TICKER PnL SUMMARY")
        print(f"{'='*80}")
        
        for ticker, result in all_results.items():
            if result and isinstance(result, dict) and result.get('success'):
                final_capital = result.get('final_capital', 0)
                initial_capital = result.get('config', {}).get('initialCapitalLong', 10000)
                pnl = ((final_capital / initial_capital - 1) * 100) if initial_capital > 0 else 0
                print(f"{ticker:12} | PnL: {pnl:8.2f}%")
            else:
                print(f"{ticker:12} | PnL: {'ERROR':>8}")
        
        print(f"\n✅ ALL DONE! Report saved: {report_filename}")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return report_filename
        
    except Exception as e:
        print(f"❌ Live backtest analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_backtest_frame(df, begin_percent=None, end_percent=None):
    """
    Erstellt df_bt aus dem Prozentbereich der Daten
    Verwendet config.py Werte als Standard
    """
    if df is None or df.empty:
        return None
    
    # Verwende config.py Werte wenn nicht explizit angegeben
    if begin_percent is None:
        begin_percent = backtesting_begin
    if end_percent is None:
        end_percent = backtesting_end
    
    n = len(df)
    start_idx = int(n * begin_percent / 100)
    end_idx = int(n * end_percent / 100)
    
    # Sicherstellen, dass Indizes gültig sind
    start_idx = max(0, min(start_idx, n - 1))
    end_idx = max(start_idx + 1, min(end_idx, n))
    
    df_bt = df.iloc[start_idx:end_idx].copy()
    
    print(f"\n📊 === BACKTEST DATA RANGE ===")
    print(f"📈 Gesamte Daten: {n} Zeilen")
    print(f"📅 Vollständiger Zeitraum: {df.index.min().date()} bis {df.index.max().date()}")
    print(f"🧪 Backtest-Bereich: {begin_percent}% - {end_percent}% der Daten")
    print(f"📅 Backtest-Zeitraum: {df_bt.index.min().date()} bis {df_bt.index.max().date()}")
    print(f"📊 Backtest-Zeilen: {len(df_bt)} (Index {start_idx} bis {end_idx})")
    
    return df_bt

def load_and_update_daily_crypto(minute_df, symbol, base_dir):
    # --- MultiIndex flatten falls nötig ---
    if isinstance(minute_df.columns, pd.MultiIndex):
        minute_df.columns = minute_df.columns.get_level_values(0)

    # Spaltennamen vereinheitlichen (Großbuchstaben)
    col_map = {c.lower(): c for c in ['Open', 'High', 'Low', 'Close', 'Volume']}
    minute_df = minute_df.rename(columns={c: col_map.get(c.lower(), c) for c in minute_df.columns})

    # Prüfen ob alle Spalten da sind
    required = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(r in minute_df.columns for r in required):
        raise ValueError(f"[{symbol}] Minutendaten fehlen Spalten: {set(required) - set(minute_df.columns)}")

    # Datumsspalte erzeugen
    if "datetime" in minute_df.columns:
        minute_df['date'] = pd.to_datetime(minute_df['datetime']).dt.date
    else:
        minute_df['date'] = pd.to_datetime(minute_df.index).date

    grouped = minute_df.groupby('date')
    daily = pd.DataFrame({
        "date": grouped["date"].first(),
        "Open": grouped["Open"].first(),
        "High": grouped["High"].max(),
        "Low": grouped["Low"].min(),
        "Close": grouped["Close"].last(),
        "Volume": grouped["Volume"].sum()
    })
    daily = daily.sort_values("date").reset_index(drop=True)

    daily_path = os.path.join(base_dir, f"{symbol}_daily.csv")
    daily[["date", "Open", "High", "Low", "Close", "Volume"]].to_csv(
        daily_path, index=False, header=True
    )
    print(f"[{symbol}] ✅ Tagesdaten gespeichert unter: {daily_path}")
    return daily

def flatten_and_rename_columns(df, new_columns=None):
    # Flacht MultiIndex ab und setzt neue Spaltennamen
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[1].capitalize() for col in df.columns]
    else:
        df.columns = [str(col).strip().capitalize() for col in df.columns]
    if new_columns is not None:
        df.columns = new_columns
    return df

def load_daily_csv(filename):
    """
    Lädt eine Tagesdaten-CSV mit richtigem Header.
    Erwartet: Date,Open,High,Low,Close,Volume als Spalten.
    Gibt DataFrame mit Date als Index zurück.
    """
    df = pd.read_csv(filename, parse_dates=["Date"])
    df = df.set_index("Date")
    return df

def safe_parse_date(date_str):
    """Versucht, ein Datum im erwarteten Format zu parsen. Fehler werden zu NaT."""
    try:
        return pd.to_datetime(date_str, format="%Y-%m-%d %H:%M:%S")
    except:
        return pd.NaT

def clean_crypto_csv(filepath):
    with open(filepath, "r") as file:
        raw = file.readlines()

    # 🧠 Prüfe, ob es sich um doppelte Header handelt
    if len(raw) >= 3 and "Date" in raw[2]:
        print("🔍 Doppelte Header erkannt – bereinige...")
        raw_clean = raw[2:]  # Nur relevante Zeilen ab Zeile 3
        temp_path = filepath.replace(".csv", "_cleaned.csv")

        with open(temp_path, "w") as f:
            f.writelines(raw_clean)

        df = pd.read_csv(temp_path, parse_dates=["Date"])
        print(f"✅ Bereinigt geladen: {len(df)} Zeilen | Datei: {temp_path}")
    else:
        df = pd.read_csv(filepath, parse_dates=["Date"])
        print(f"ℹ️ Normale CSV geladen: {len(df)} Zeilen")

    return df

def debug_loader_status(ticker, csv_path, days=365):
    import os
    import pandas as pd
    import yfinance as yf

    filename = os.path.join(csv_path, f"{ticker}.csv")
    print(f"\n📦 Debug für Ticker: {ticker}")
    print(f"🗂️ Datei erwartet unter: {filename}")
    if not os.path.exists(filename):
        print("🚫 CSV existiert noch nicht.")
    else:
        try:
            df_local = pd.read_csv(filename, parse_dates=["Date"], index_col="Date")
            print(f"✅ Lokale Datei gefunden, letztes Datum: {df_local.index.max().date()}")
        except Exception as e:
            print(f"❌ Fehler beim Laden der CSV: {e}")
            df_local = None

    print("🌐 Versuche Online-Download von yfinance...")
    try:
        df_online = yf.download(ticker, interval="1d", period=f"{days}d", auto_adjust=True, progress=False)
        if df_online.empty:
            print("⚠️ Keine Daten aus Yahoo erhalten.")
        else:
            print(f"📅 Daten von {df_online.index.min().date()} bis {df_online.index.max().date()}")
            print(f"🧾 Online-Datenanzahl: {len(df_online)} Zeilen")
    except Exception as e:
        print(f"❌ Fehler beim yfinance-Download: {e}")


def calculate_trade_statistics(matched_trades, equity_curve, initial_capital, commission_rate):
    """Calculate comprehensive trade statistics"""
    print("calculate_trade_statistics called")
    
    if not matched_trades:
        return {
            'Total Trades': 0,
            'Winning Trades': 0,
            'Losing Trades': 0,
            'Win Percentage': 0.0,
            'Loss Percentage': 0.0,
            'Total PnL': 0.0,
            'Total Fees': 0.0,
            'Final Capital': initial_capital,
            'Max Drawdown': 0.0
        }
    
    # Basic trade statistics
    total_trades = len(matched_trades)
    winning_trades = sum(1 for trade in matched_trades if trade['pnl'] > 0)
    losing_trades = total_trades - winning_trades
    
    win_percentage = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    loss_percentage = (losing_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate PnL and fees - use Net PnL if available
    if isinstance(matched_trades, pd.DataFrame):
        if 'Net PnL' in matched_trades.columns:
            total_net_pnl = matched_trades['Net PnL'].sum()
            total_pnl = matched_trades['PnL'].sum() if 'PnL' in matched_trades.columns else total_net_pnl
        else:
            total_pnl = sum(trade.get('pnl', 0) for trade in matched_trades.to_dict('records'))
            total_net_pnl = total_pnl
        
        if 'Commission' in matched_trades.columns:
            total_fees = matched_trades['Commission'].sum()
        else:
            total_fees = sum(trade.get('total_fees', 0) for trade in matched_trades.to_dict('records'))
        
        winning_trades = len(matched_trades[matched_trades['Net PnL' if 'Net PnL' in matched_trades.columns else 'PnL'] > 0])
    else:
        # Fallback for list format
        total_pnl = sum(trade['pnl'] for trade in matched_trades)
        total_fees = sum(trade['total_fees'] for trade in matched_trades)
        total_net_pnl = total_pnl - total_fees
        winning_trades = sum(1 for trade in matched_trades if trade['pnl'] > 0)
    
    final_capital = initial_capital + total_net_pnl
    
    # Calculate max drawdown using Net PnL
    max_drawdown = 0.0
    peak = initial_capital
    current_capital = initial_capital
    
    if isinstance(matched_trades, pd.DataFrame) and 'Net PnL' in matched_trades.columns:
        for _, row in matched_trades.iterrows():
            current_capital += row['Net PnL']
            if current_capital > peak:
                peak = current_capital
            drawdown = (peak - current_capital) / peak * 100 if peak > 0 else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
    else:
        for trade in matched_trades:
            current_capital += (trade.get('pnl', 0) - trade.get('total_fees', 0))
            if current_capital > peak:
                peak = current_capital
            drawdown = (peak - current_capital) / peak * 100 if peak > 0 else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
    
    stats = {
        'Total Trades': total_trades,
        'Winning Trades': winning_trades,
        'Losing Trades': losing_trades,
        'Win Percentage': round(win_percentage, 2),
        'Loss Percentage': round(loss_percentage, 2),
        'Total PnL': round(total_pnl, 3),
        'Total Net PnL': round(total_net_pnl, 3),
        'Total Fees': round(total_fees, 3),
        'Final Capital': round(final_capital, 3),
        'Max Drawdown': round(max_drawdown, 2)
    }
    
    print(f"calculate_trade_statistics returning: {stats}")
    return stats

def backtest_single_ticker(cfg, symbol):
    import pandas as pd

    # Get ticker config for trade_on setting
    from crypto_tickers import crypto_tickers
    ticker_config = crypto_tickers.get(symbol, {})
    trade_on = ticker_config.get('trade_on', 'Close')

    # Daten laden
    df = load_crypto_data_yf(symbol)
    if df is None or df.empty:
        print(f"⚠️ Keine Daten für {symbol}")
        return None

    # Spalten abflachen und prüfen
    df = flatten_and_rename_columns(df)
    expected_cols = {"Open", "High", "Low", "Close", "Volume"}
    if not expected_cols.issubset(set(df.columns)):
        print(f"⚠️ Fehlende Spalten für {symbol}: {set(df.columns)}")
        return None

    # Backtest-Zeitraum filtern (letzte N Jahre)
    backtest_years = cfg.get("backtest_years", [1])
    years = backtest_years[-1] if isinstance(backtest_years, list) else backtest_years
    end_date = df.index.max()
    start_date = end_date - pd.DateOffset(years=years)
    df_bt = df[(df.index >= start_date) & (df.index <= end_date)]

    # Prozentwerte für Start/Ende aus Konfiguration
    start_percent = cfg.get("backtest_start_percent", 0.25)
    end_percent = cfg.get("backtest_end_percent", 0.95)
    n = len(df_bt.index)
    start_idx = int(n * start_percent)
    end_idx = int(n * end_percent)
    start_idx = max(0, min(start_idx, n - 1))
    end_idx = max(0, min(end_idx, n - 1))

    # Parameter-Optimierung
    p, tw = berechne_best_p_tw_long(
        df_bt, cfg,
        start_idx, end_idx,
        verbose=False,
        ticker=symbol
    )

    # Support/Resistance
    supp_bt, res_bt = calculate_support_resistance(df_bt, p, tw, verbose=False, ticker=symbol)

    # Signale
    std_bt = assign_long_signals(supp_bt, res_bt, df_bt, tw, "1d")
    ext_bt = assign_long_signals_extended(supp_bt, res_bt, df_bt, tw, "1d", trade_on)
    ext_bt = update_level_close_long(ext_bt, df_bt, trade_on)

    # Trades simulieren
    cap_bt, trades_bt = simulate_trades_compound_extended(
        ext_bt, df_bt, cfg,
        starting_capital=cfg.get("initialCapitalLong", 10000),
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1)
    )

    # Buy & Hold-Kurve
    bh_curve_bt = [cfg.get("initialCapitalLong", 10000) * (p / df_bt["Close"].iloc[0]) for p in df_bt["Close"]]

    # Plot (use Plotly charts aligned with live_backtest_WORKING.py)
    try:
        # Build strategy equity curve from trades using the VALIDATED function
        from plotly_utils import create_equity_curve_from_matched_trades, plotly_combined_chart_and_equity

        initial_capital_bt = cfg.get("initialCapitalLong", 10000)

        # Normalize trades_bt to list[dict] if it's a DataFrame-like
        if isinstance(trades_bt, pd.DataFrame):
            trades_list_bt = trades_bt.to_dict('records')
        else:
            trades_list_bt = trades_bt or []

        equity_curve_bt = create_equity_curve_from_matched_trades(
            trades_list_bt,
            initial_capital_bt,
            df_bt,
            trade_on
        )

        # Call the unified Plotly chart function
        plotly_combined_chart_and_equity(
            df=df_bt,
            standard_signals=ext_bt,   # extended signals with real trade actions
            support=supp_bt,
            resistance=res_bt,
            equity_curve=equity_curve_bt,
            buyhold_curve=bh_curve_bt,
            ticker=symbol,
            backtest_years=backtest_years,
            initial_capital=initial_capital_bt
        )
    except Exception as e:
        print(f"⚠️ Plotly chart generation failed for {symbol}: {e}")

    return cap_bt, trades_bt, std_bt, supp_bt, res_bt, bh_curve_bt

def load_daily_data_for_backtest(symbol, base_dir):
    filename = f"{symbol}_daily.csv"
    daily_path = os.path.join(base_dir, filename)
    if not os.path.exists(daily_path):
        print(f"[{symbol}] ❌ Datei fehlt: {daily_path}")
        return None
    try:
        df = pd.read_csv(daily_path, parse_dates=["date"])
        return df
    except Exception as e:
        print(f"[{symbol}] ❌ Fehler beim Einlesen: {e}")
        return None

def batch_update_all(base_dir, start_date_daily="2020-01-01", start_date_minute="2024-01-01"):
    for symbol in crypto_tickers:
        update_daily_csv(symbol, base_dir, start_date_daily)
        update_minute_csv(symbol, base_dir, start_date_minute)

def update_daily_csv(symbol, base_dir, start_date="2024-07-31"):
    """
    Lädt Tagesdaten via yfinance für das Symbol und speichert sie als saubere CSV.
    Header ist IMMER korrekt! Erzeugt Datei {symbol}_daily.csv im base_dir.
    """
    df = yf.download(symbol, start=start_date, interval="1d", auto_adjust=True, progress=False)
    if df is None or df.empty:
        print(f"[{symbol}] ⚠️ Keine Daten gefunden.")
        return None

    # MultiIndex-Problem lösen
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()  # Date als Spalte

    if 'Date' not in df.columns:
        print(f"[{symbol}] ⚠️ 'Date' column not found after reset_index.")
        return None

    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

    # Ensure directory exists
    os.makedirs(base_dir, exist_ok=True)

    # Speichern mit sauberem Header
    out_path = os.path.join(base_dir, f"{symbol}_daily.csv")
    df.to_csv(out_path, index=False, header=True)
    print(f"[{symbol}] ✅ Daily CSV gespeichert: {out_path}")
    return df

def update_minute_csv(symbol, base_dir, start_date):
    import os
    import yfinance as yf
    import pandas as pd

    df = yf.download(symbol, start=start_date, interval="1m", auto_adjust=True, progress=False)
    if df is None or df.empty:
        print(f"[{symbol}] ⚠️ Keine Minutendaten gefunden.")
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()

    # Zeitspalte auf "DateTime" bringen
    if "Datetime" in df.columns:
        df = df.rename(columns={"Datetime": "DateTime"})
    elif "Date" in df.columns:
        df = df.rename(columns={"Date": "DateTime"})
    elif "index" in df.columns:
        df = df.rename(columns={"index": "DateTime"})
    else:
        raise ValueError("Keine Zeitspalte gefunden! Spalten sind: " + str(df.columns))

    # Volume erzwingen
    if "Volume" not in df.columns:
        print(f"[{symbol}] ⚠️ Volume fehlt, wird mit NaN ergänzt.")
        df["Volume"] = float("nan")

    # Nur gewünschte Spalten und speichern
    df = df[["DateTime", "Open", "High", "Low", "Close", "Volume"]]
    out_path = os.path.join(base_dir, f"{symbol}_minute.csv")
    df.to_csv(out_path, index=False, header=True)
    print(f"[{symbol}] ✅ Minute CSV gespeichert: {out_path}")
    return df

def batch_update_all_daily_csv(base_dir, get_minute_df_func):
    """
    Für alle Ticker aus crypto_tickers wird load_and_update_daily_crypto ausgeführt.
    get_minute_df_func(symbol) muss ein DataFrame der Minutendaten zurückgeben.
    """
    for ticker, cfg in crypto_tickers.items():
        symbol = cfg["symbol"]
        print(f"\n⏳ Lade Minutendaten für {symbol} ...")
        try:
            minute_df = get_minute_df_func(symbol)
            if minute_df is None or minute_df.empty:
                print(f"[{symbol}] ⚠️ Keine Minutendaten gefunden, überspringe.")
                continue
            load_and_update_daily_crypto(minute_df, symbol, base_dir)
        except Exception as e:
            print(f"[{symbol}] ❌ Fehler: {e}")

def get_minute_df_yfinance(symbol):
    import yfinance as yf
    df = yf.download(symbol, period="5d", interval="1m", progress=False, auto_adjust=True)
    return df if df is not None and not df.empty else None

def update_daily_crypto_with_today1(minute_df, symbol, daily_path):
    """
    Aggregiert die Minutendaten zu Tagesdaten,
    entfernt doppelte Headerstufen und sichert das Datum gegen Parsingfehler.
    """
    if minute_df is None or minute_df.empty:
        print(f"[{symbol}] ❌ Keine gültigen Minutendaten vorhanden.")
        return

    # 🧽 Schritt 1: Datum bereinigen
    minute_df["Date"] = minute_df["Date"].apply(safe_parse_date)
    minute_df["Date"] = pd.to_datetime(minute_df["Date"]).dt.date

    # 🔁 Schritt 2: Aggregation auf Tagesbasis
    daily_df_new = minute_df.groupby("Date").agg({
        "price": ["first", "max", "min", "last"],
        "volume": "sum"
    })

    # 🧹 Schritt 3: Header flatten
    daily_df_new.columns = ["Open", "High", "Low", "Close", "Volume"]
    daily_df_new.index = pd.to_datetime(daily_df_new.index)

    # 📁 Schritt 4: Vorhandene Datei laden (falls vorhanden)
    if os.path.exists(daily_path):
        daily_df_existing = pd.read_csv(daily_path, parse_dates=["Date"], index_col="Date")
        daily_df_existing.index = pd.to_datetime(daily_df_existing.index)
        daily_df = pd.concat([daily_df_existing, daily_df_new])
        daily_df = daily_df[~daily_df.index.duplicated(keep="last")]  # Duplikate entfernen
    else:
        daily_df = daily_df_new

    # 💾 Schritt 5: Speichern mit sauberem Header
    daily_df.to_csv(daily_path, index=True)
    print(f"[{symbol}] ✅ Tagesdaten erfolgreich aktualisiert.")

def update_daily_crypto_with_today():
    base_dir = "C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading1/"
    os.makedirs(CSV_PATH, exist_ok=True)

    for ticker, cfg in crypto_tickers.items():
        symbol = cfg["symbol"]
        print(f"\n📈 Lade {symbol}...")

        try:
            # Lade Tagesdaten aus Yahoo
            df = yf.download(symbol, interval="1d", period="30d", auto_adjust=True, progress=False)

            if df is None or df.empty:
                print(f"[{symbol}] ⚠️ Keine Daten erhalten")
                continue

            df.columns = [str(c).strip().capitalize() for c in df.columns]
            df = df.dropna(subset=["Open", "High", "Low", "Close"])
            df["Date"] = df.index
            df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

            # Speichern als *_daily.csv
            file_path = os.path.join(CSV_PATH, f"{symbol}_daily.csv")
            df.to_csv(file_path, index=False)
            print(f"[{symbol}] ✅ Gespeichert: {file_path}")

        except Exception as e:
            print(f"[{symbol}] ❌ Fehler beim Abrufen: {e}")

def get_backtest_data(df, backtest_years, backtesting_begin, backtesting_end):
    """
    Beschränkt den DataFrame zuerst auf die letzten N Jahre/Monate,
    dann auf den gewünschten Prozentbereich.
    Gibt die verwendeten Zeitspannen per print() aus.
    """
    # Schritt 1: Nur die letzten N Jahre/Monate
    df_years = restrict_to_backtest_years(df, backtest_years)
    print(f"[Debug] Zeitraum nach backtest_years: {df_years.index.min().date()} bis {df_years.index.max().date()} (Zeilen: {len(df_years)})")

    # Schritt 2: Prozentualer Bereich
    df_bt = restrict_to_percent_slice(df_years, backtesting_begin, backtesting_end)
    print(f"[Debug] Zeitraum nach Prozent-Schnitt: {df_bt.index.min().date()} bis {df_bt.index.max().date()} (Zeilen: {len(df_bt)})")

    return df_bt

def restrict_to_backtest_years(df, backtest_years):    
    # Nimmt die letzten N Jahre oder Monate (backtest_years = [0, 2] für 2 Jahre)
    max_years = backtest_years[1] if isinstance(backtest_years, list) else backtest_years
    if max_years < 1:
        min_timestamp = df.index.max() - pd.DateOffset(months=int(max_years*12))
    else:
        min_timestamp = df.index.max() - pd.DateOffset(years=int(max_years))
    return df[df.index >= min_timestamp]

def restrict_to_percent_slice(df, begin, end):
    n = len(df)
    # Calculate start and end indices based on percentage
    start_idx = int(n * begin / 100)
    end_idx = int(n * end / 100)
    return df.iloc[start_idx:end_idx]

def capture_trades_output(matched_trades, open_trade_info=None, initial_capital=10000.0):
    """
    Convert matched_trades list to the formatted string output that can be analyzed
    Also handles the last open trade if provided
    """
    trades_text = ""
    
    if (matched_trades is None or (hasattr(matched_trades, 'empty') and matched_trades.empty) or len(matched_trades) == 0) and not open_trade_info:
        return trades_text
    
    # Process completed matched trades
    if isinstance(matched_trades, pd.DataFrame):
        trades_list = matched_trades.to_dict('records')
    else:
        trades_list = matched_trades or []
        
    for i, trade in enumerate(trades_list):
        # Extract trade data
        buy_date = trade.get('buy_date', trade.get('Entry Date', 'N/A'))
        sell_date = trade.get('sell_date', trade.get('Exit Date', 'N/A'))
        buy_price = trade.get('buy_price', trade.get('Entry Price', 0))
        sell_price = trade.get('sell_price', trade.get('Exit Price', 0))
        shares = trade.get('shares', trade.get('Quantity', 0))
        trade_value = trade.get('trade_value', 0)
        total_fees = trade.get('total_fees', trade.get('Commission', 0))
        pnl = trade.get('pnl', trade.get('PnL', 0))
        
        # Calculate capital (approximate running capital using Net PnL)
        if i == 0:
            capital = initial_capital  # Use provided initial capital
        else:
            # Calculate running capital from previous trades (use NET PnL after fees)
            if isinstance(matched_trades, pd.DataFrame) and 'Net PnL' in matched_trades.columns:
                # Use Net PnL from DataFrame for completed trades
                previous_trades = matched_trades.iloc[:i]
                completed_previous = previous_trades[previous_trades['Status'] == 'CLOSED'] if 'Status' in previous_trades.columns else previous_trades
                previous_net_pnl = completed_previous['Net PnL'].sum()
            else:
                # Fallback to gross PnL if Net PnL not available
                previous_net_pnl = sum(t.get('pnl', 0) for t in matched_trades[:i])
            capital = initial_capital + previous_net_pnl
        
        # Calculate raw shares (before rounding)
        raw_shares = capital / buy_price if buy_price > 0 else shares
        
        # Add BUY line
        trades_text += f"🔢 BUY: Date={buy_date}, Capital={capital:.2f}, Price={buy_price:.4f}, Raw={raw_shares:.6f}, Shares={shares:.6f}\n"
        
        # Add SELL line
        trades_text += f"💰 SELL: Date={sell_date}, Price={sell_price:.4f}, Value={trade_value:.3f}, Fees={total_fees:.3f}, PnL={pnl:.3f}\n"
    
    # Handle open trade (last BUY without matching SELL)
    if open_trade_info:
        buy_date = open_trade_info.get('buy_date', 'N/A')
        buy_price = open_trade_info.get('buy_price', 0)
        shares = open_trade_info.get('shares', 0)
        
        # Calculate capital after all completed trades (use NET PnL after fees)
        if isinstance(matched_trades, pd.DataFrame) and 'Net PnL' in matched_trades.columns:
            # Use Net PnL from DataFrame
            completed_trades = matched_trades[matched_trades['Status'] == 'CLOSED'] if 'Status' in matched_trades.columns else matched_trades
            total_net_pnl = completed_trades['Net PnL'].sum()
        else:
            # Fallback to gross PnL if Net PnL not available
            total_net_pnl = sum(t.get('pnl', 0) for t in matched_trades)
        
        capital = initial_capital + total_net_pnl
        
        # Calculate raw shares
        raw_shares = capital / buy_price if buy_price > 0 else shares
        
        # Add open BUY line
        trades_text += f"🔢 BUY: Date={buy_date}, Capital={capital:.2f}, Price={buy_price:.4f}, Raw={raw_shares:.6f}, Shares={shares:.6f}\n"
        trades_text += f"📊 OPEN POSITION: {shares:.6f} shares @ {buy_price:.4f} (Not yet closed)\n"
    
    return trades_text

def get_crypto_data_enhanced(symbol, backtest_years, update_today=True):
    """
    Enhanced crypto data loading with today's data included
    FIXED: Ensures today's candle is always included
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - pd.DateOffset(years=backtest_years)
        
        print(f"📅 Loading data for {symbol} from {start_date.date()} to {end_date.date()}")
        
        # Download with extended period to ensure today is included
        df = yf.download(
            symbol, 
            start=start_date.strftime('%Y-%m-%d'),
            end=(end_date + pd.DateOffset(days=1)).strftime('%Y-%m-%d'),  # +1 day to include today
            interval="1d", 
            auto_adjust=True, 
            progress=False
        )
        
        if df is None or df.empty:
            print(f"❌ No data received for {symbol}")
            return None
        
        # Fix MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ensure standard column names
        df.columns = [str(col).strip().capitalize() for col in df.columns]
        
        # Add today's partial candle if market is open and update_today=True
        if update_today:
            today = datetime.now().date()
            latest_date = df.index.max().date()
            
            if latest_date < today:
                print(f"📈 Latest data: {latest_date}, trying to add today: {today}")
                
                # Try to get today's data
                today_df = yf.download(
                    symbol,
                    start=today.strftime('%Y-%m-%d'),
                    interval="1d",
                    auto_adjust=True,
                    progress=False
                )
                
                if not today_df.empty:
                    if isinstance(today_df.columns, pd.MultiIndex):
                        today_df.columns = today_df.columns.get_level_values(0)
                    today_df.columns = [str(col).strip().capitalize() for col in today_df.columns]
                    
                    # Combine dataframes
                    df = pd.concat([df, today_df])
                    df = df[~df.index.duplicated(keep='last')]  # Remove duplicates
                    print(f"✅ Added today's data! New latest date: {df.index.max().date()}")
                else:
                    print(f"⚠️ No data available for today yet")
            else:
                print(f"✅ Data already includes today: {latest_date}")
        
        # Ensure required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing columns for {symbol}: {missing_cols}")
            return None
        
        print(f"✅ Loaded {len(df)} days of data for {symbol} (from {df.index.min().date()} to {df.index.max().date()})")
        return df
        
    except Exception as e:
        print(f"❌ Error loading data for {symbol}: {e}")
        return None
    """
    Enhanced crypto data loading with today's data included
    FIXED: Ensures today's candle is always included
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - pd.DateOffset(years=backtest_years)
        
        print(f"� Loading data for {symbol} from {start_date.date()} to {end_date.date()}")
        
        # Download with extended period to ensure today is included
        df = yf.download(
            symbol, 
            start=start_date.strftime('%Y-%m-%d'),
            end=(end_date + pd.DateOffset(days=1)).strftime('%Y-%m-%d'),  # +1 day to include today
            interval="1d", 
            auto_adjust=True, 
            progress=False
        )
        
        if df is None or df.empty:
            print(f"❌ No data received for {symbol}")
            return None
        
        # Fix MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ensure standard column names
        df.columns = [str(col).strip().capitalize() for col in df.columns]
        
        # Add today's partial candle if market is open and update_today=True
        if update_today:
            today = datetime.now().date()
            latest_date = df.index.max().date()
            
            if latest_date < today:
                print(f"� Latest data: {latest_date}, trying to add today: {today}")
                
                # Try to get today's data
                today_df = yf.download(
                    symbol,
                    start=today.strftime('%Y-%m-%d'),
                    interval="1d",
                    auto_adjust=True,
                    progress=False
                )
                
                if not today_df.empty:
                    if isinstance(today_df.columns, pd.MultiIndex):
                        today_df.columns = today_df.columns.get_level_values(0)
                    today_df.columns = [str(col).strip().capitalize() for col in today_df.columns]
                    
                    # Combine dataframes
                    df = pd.concat([df, today_df])
                    df = df[~df.index.duplicated(keep='last')]  # Remove duplicates
                    print(f"✅ Added today's data! New latest date: {df.index.max().date()}")
                else:
                    print(f"⚠️ No data available for today yet")
            else:
                print(f"✅ Data already includes today: {latest_date}")
        
        # Ensure required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing columns for {symbol}: {missing_cols}")
            return None
        
        print(f"✅ Loaded {len(df)} days of data for {symbol} (from {df.index.min().date()} to {df.index.max().date()})")
        return df
        
    except Exception as e:
        print(f"❌ Error loading data for {symbol}: {e}")
        return None

def display_matched_trades_table_enhanced():
    raise NotImplementedError

def run_backtest(symbol, config):
    """
    Führt einen vollständigen Backtest für ein Symbol durch
    """
    try:
        # Konfiguration extrahieren
        initial_capital = config.get('initialCapitalLong', 10000)  # FIXED: Use correct key
        trade_on = config.get('trade_on', 'close').lower()
        order_round_factor = config.get('order_round_factor', 0.01)
        commission_rate = config.get('commission_rate', 0.0018)

        print(f"\n=== Backtest fuer {symbol} ===")
        print(f"Initial Capital: {initial_capital}")
        print(f"Trade on: {trade_on.title()} price")
        print(f"Order Round Factor: {order_round_factor}")
        print(f"Commission Rate: {commission_rate*100}%")
        print(f"DEBUG: initial_capital = {initial_capital} (from config key 'initialCapitalLong')")  # DEBUG

        # Daten laden - aus config.py
        from config import backtest_years
        print(f"Backtest Zeitraum: {backtest_years} Jahr(e) (aus config.py)")
        df = load_crypto_data_yf(symbol, backtest_years)
        if df is None or df.empty:
            print(f"Keine Daten für {symbol}")
            return False

        print(f"Dataset: {len(df)} Zeilen ({df.index[0].date()} bis {df.index[-1].date()})")
        if os.environ.get("STABLE_BACKTEST", "0") == "1":
            print("🔒 Stable mode ON (STABLE_BACKTEST=1). No partial current-day bar included.")
        
        # ✅ CREATE BACKTEST FRAME (25% - 95% of data)
        df_bt = create_backtest_frame(df, backtesting_begin, backtesting_end)
        if df_bt is None or df_bt.empty:
            print(f"❌ Backtest Frame creation failed for {symbol}")
            return False

        # Alias for clarity (user referred to df_tw)
        df_tw = df_bt
        print(f"📊 Backtest Frame: {len(df_bt)} Zeilen ({df_bt.index[0].date()} bis {df_bt.index[-1].date()})")
        print(f"📊 Backtest Range: {backtesting_begin}% - {backtesting_end}% der Daten")

        # 1. DAILY DATA (nur TAIL)
        print(f"\n📊 1. DAILY DATA - TAIL (5 Zeilen) - {symbol}")
        print("="*80)
        print(df.tail().to_string())

        # Parameteroptimierung nur auf Slice
        optimal_results = optimize_parameters(df_bt, symbol)
        optimal_past_window = optimal_results.get('optimal_past_window', 10)
        optimal_trade_window = optimal_results.get('optimal_trade_window', 1)

        # =============================
        # PARAMETER ANWENDUNG – SLICE
        # =============================
        print(f"\n🔧 Applying optimal parameters on BACKTEST SLICE (in-sample) {backtesting_begin}%–{backtesting_end}% …")
        supp_slice, res_slice = calculate_support_resistance(
            df_bt, optimal_past_window, optimal_trade_window, verbose=False, ticker=symbol
        )
        print(f"   ➜ Slice Support Levels: {len(supp_slice)}, Resistance Levels: {len(res_slice)}")

        ext_slice = assign_long_signals_extended(
            supp_slice, res_slice, df_bt, optimal_trade_window, "1d", trade_on.title()
        )
        if ext_slice is None or ext_slice.empty:
            print("   ⚠️ No slice extended signals produced")
        else:
            print(f"   ➜ Slice Extended Signals: {len(ext_slice)}")

        matched_trades_slice = simulate_matched_trades(
            ext_slice if ext_slice is not None else pd.DataFrame(),
            initial_capital,
            commission_rate,
            df_bt,
            order_round_factor,
            trade_on.title()
        ) if ext_slice is not None and not ext_slice.empty else pd.DataFrame()
        slice_stats = calculate_trade_statistics(ext_slice, matched_trades_slice, initial_capital) if not matched_trades_slice.empty else {}

        # ======================================
        # PARAMETER ANWENDUNG – VOLLER DATENSATZ
        # ======================================
        print(f"\n🔧 Applying optimal parameters on FULL DATASET (trading over full df)…")
        supp_full, res_full = calculate_support_resistance(
            df, optimal_past_window, optimal_trade_window, verbose=False, ticker=symbol
        )

        # 2. BACKTEST RESULTS MIT OPTIMALEN PARAMETERN (FULL)
        print(f"\n📊 2. BACKTEST RESULTS - {symbol}")
        print("="*80)
        print(f"   📈 Optimal Past Window: {optimal_past_window}")
        print(f"   📈 Optimal Trade Window: {optimal_trade_window}")
        print(f"   📊 Support Levels (FULL): {len(supp_full)} | (SLICE): {len(supp_slice)}")
        print(f"   📊 Resistance Levels (FULL): {len(res_full)} | (SLICE): {len(res_slice)}")
        print(f"   📅 Analysis Period: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"   📊 Total Trading Days: {len(df)}")

        # Extended Signals generieren mit kompletten df
        print(f"\n📊 Generiere Extended Signals (FULL) für {symbol}...")
        ext_full = assign_long_signals_extended(
            supp_full, res_full, df, optimal_trade_window, "1d", trade_on.title()
        )
        
        if ext_full is None or ext_full.empty:
            print(f"❌ Keine Extended Signals für {symbol}")
            return False

        # 🔧 NORMALIZE EXTENDED SIGNALS COLUMNS TO MATCH LIVE RUNNER
        try:
            ef = ext_full.copy()
            # Prefer 'Long Action'; create it from 'Action' if missing
            if 'Long Action' not in ef.columns and 'Action' in ef.columns:
                ef['Long Action'] = ef['Action']
            # Prefer 'Long Date detected'; create fallback from common date columns
            if 'Long Date detected' not in ef.columns:
                if 'Date detected' in ef.columns:
                    ef['Long Date detected'] = ef['Date detected']
                elif 'Date' in ef.columns:
                    ef['Long Date detected'] = ef['Date']
            # Coerce numeric level fields used for plotting
            for c in ['Level Close', 'Level high/low']:
                if c in ef.columns:
                    try:
                        ef[c] = pd.to_numeric(ef[c], errors='coerce')
                    except Exception:
                        pass
            ext_full = ef
            print("🔧 Normalized extended signal columns for live compatibility")
        except Exception as _norm_err:
            print(f"⚠️ Could not normalize extended signals: {_norm_err}")
        
        # 3. EXTENDED TRADES - KOMPLETTE TABELLE
        print(f"\n📊 3. EXTENDED TRADES - KOMPLETTE TABELLE (FULL {len(ext_full)} Trades) - {symbol}")
        print("="*120)
        if not ext_full.empty:
            display_df = ext_full.copy()
            if 'Level high/low' in display_df.columns:
                display_df['Level high/low'] = display_df['Level high/low'].round(2)
            if 'Level Close' in display_df.columns:
                display_df['Level Close'] = display_df['Level Close'].round(2)
            print(display_df.to_string(index=True, max_rows=None))
        else:
            print("❌ Keine Extended Trades vorhanden")

        # 4. MATCHED TRADES - SIMULATION (mit kompletten df)
        print(f"\n📊 4. MATCHED TRADES - SIMULATION (FULL) - {symbol}")
        print("="*120)
        matched_trades = simulate_matched_trades(ext_full, initial_capital, commission_rate, df, order_round_factor, trade_on.title())
        if not matched_trades.empty:
            print(matched_trades.to_string(index=True, max_rows=None))
        else:
            print("❌ Keine Matched Trades generiert")
        
        # 5. TRADE STATISTICS
        print(f"\n📊 5. TRADE STATISTICS (FULL) - {symbol}")
        print("="*80)
        trade_stats = calculate_trade_statistics(ext_full, matched_trades, initial_capital)
        for key, value in trade_stats.items():
            print(f"   {key}: {value}")
        if slice_stats:
            print(f"\n📊 📌 SLICE TRADE STATISTICS (In-Sample {backtesting_begin}%–{backtesting_end}%)")
            for key, value in slice_stats.items():
                print(f"   {key}: {value}")
        
        # Tabelle anzeigen
        display_extended_trades_table(ext_full, symbol)
        
        # ✅ EXTRACT FINAL CAPITAL FROM TRADE STATISTICS
        final_capital_value = initial_capital  # Fallback
        if '💼 Final Capital' in trade_stats:
            final_capital_str = trade_stats['💼 Final Capital'].replace('€', '').replace(',', '')
            try:
                final_capital_value = float(final_capital_str)
            except ValueError:
                final_capital_value = initial_capital
        
        # ✅ BERECHNE TÄGLICH EQUITY CURVE MIT EXISTIERENDER FUNKTION
        equity_curve_values = []
        if not matched_trades.empty:
            # Konvertiere matched_trades DataFrame zu Liste für die Funktion
            trades_list = []
            for _, trade in matched_trades.iterrows():
                trade_dict = {
                    'buy_date': trade['Entry Date'],
                    'sell_date': trade['Exit Date'],
                    'buy_price': trade['Entry Price'],
                    'sell_price': trade['Exit Price'],
                    'shares': trade['Quantity'],
                    'pnl': trade['Net PnL'],
                    'is_open': trade.get('Status', '') == 'OPEN'
                }
                trades_list.append(trade_dict)
            
            # Verwende existierende Funktion - ✅ INCLUDE TRADE_ON
            equity_curve_values = create_equity_curve_from_matched_trades(
                trades_list, initial_capital, df, trade_on
            )
            
            print(f"📊 Täglich Equity Curve: {len(equity_curve_values)} Werte")
            print(f"📊 Start: €{equity_curve_values[0]:.0f}, Ende: €{equity_curve_values[-1]:.0f}")
            print(f"📊 Sample: Tag 1-5: {[f'€{v:.0f}' for v in equity_curve_values[:5]]}")
            print(f"📊 Sample: Letzte 5: {[f'€{v:.0f}' for v in equity_curve_values[-5:]]}")
            
            # Prüfe ob die Curve variiert
            unique_values = len(set([int(v) for v in equity_curve_values]))
            print(f"📊 Unique Werte in Equity Curve: {unique_values}")
            if unique_values > 10:
                print("✅ Equity Curve variiert korrekt!")
            else:
                print("⚠️ WARNING: Equity Curve hat wenig Variation")
        else:
            # Fallback: konstante Equity Curve
            equity_curve_values = [initial_capital] * len(df)
            print(f"⚠️ Fallback Equity Curve: {len(equity_curve_values)} Werte mit €{initial_capital:.0f}")
        
        # ✅ BERECHNE BUY & HOLD CURVE
        buyhold_curve_values = []
        if len(df) > 0 and "Close" in df.columns:
            start_price = df['Close'].iloc[0]
            if start_price > 0:
                for price in df['Close']:
                    current_return = price / start_price
                    buyhold_curve_values.append(initial_capital * current_return)
                print(f"📈 Buy&Hold Curve: {len(buyhold_curve_values)} Werte")
                print(f"📈 B&H Start: €{buyhold_curve_values[0]:.0f}, Ende: €{buyhold_curve_values[-1]:.0f}")
            else:
                buyhold_curve_values = [initial_capital] * len(df)
                print(f"⚠️ Fallback Buy&Hold Curve: konstant €{initial_capital:.0f}")
        else:
            buyhold_curve_values = [initial_capital] * len(df)
            print(f"⚠️ Fallback Buy&Hold Curve: konstant €{initial_capital:.0f}")
        
        # Result erstellen mit korrekten Informationen
        # Slice final capital (if available)
        slice_final_cap = None
        if slice_stats and '💼 Final Capital' in slice_stats:
            try:
                slice_final_cap = float(slice_stats['💼 Final Capital'].replace('€','').replace(',',''))
            except Exception:
                slice_final_cap = None

        result = {
            'success': True,
            'symbol': symbol,
            'config': config,
            'df': df,
            'df_bt': df_bt,
            'backtest_range': {
                'start_percent': backtesting_begin,
                'end_percent': backtesting_end,
                'start_date': df_bt.index[0].date(),
                'end_date': df_bt.index[-1].date(),
                'days': len(df_bt)
            },
            'slice_support_levels': len(supp_slice),
            'slice_resistance_levels': len(res_slice),
            'slice_ext_signals': ext_slice,
            'slice_matched_trades': matched_trades_slice,
            'slice_trade_statistics': slice_stats,
            'slice_final_capital': slice_final_cap,
            'dataset_info': {
                'total_days': len(df),
                'start_date': df.index[0].date(),
                'end_date': df.index[-1].date()
            },
            'signals': {
                'total': len(ext_full) if ext_full is not None else 0,
                'long_signals': len(ext_full[ext_full['Long Signal Extended'] == True]) if ext_full is not None and 'Long Signal Extended' in ext_full.columns else 0,
            },
            'ext_signals': ext_full,
            'matched_trades': matched_trades,
            'trade_statistics': trade_stats,
            'support_levels': len(supp_full),
            'resistance_levels': len(res_full),
            'optimal_past_window': optimal_past_window,
            'optimal_trade_window': optimal_trade_window,
            'final_capital': final_capital_value,
            'equity_curve': equity_curve_values,
            'buyhold_curve': buyhold_curve_values
        }

        print(f"\n📅 TRADES DER LETZTEN 2 WOCHEN - {symbol}")
        print("="*80)
        if ext_full is not None and not ext_full.empty:
            recent_ext_trades = ext_full.tail(50)
            print(recent_ext_trades[['Action','Long Signal Extended']].tail(10).to_string())
        else:
            print("⚠️ Keine Extended Trades verfügbar")

        return result

    except Exception as e:
        print(f"❌ Fehler für {symbol}: {e}")
        traceback.print_exc()
        return False

def optimize_parameters(df, symbol):
    """Runs brute-force optimization on the provided dataframe (slice df_bt).
    Returns optimal past & trade window maximizing final capital.
    """
    try:
        from crypto_tickers import crypto_tickers
        from config import COMMISSION_RATE, MIN_COMMISSION

        ticker_config = crypto_tickers.get(symbol, {})
        if not ticker_config:
            print(f"⚠️ Ticker {symbol} nicht in crypto_tickers gefunden, verwende Defaults")

        default_capitals = {
            'BTC-EUR': 5000,
            'ETH-EUR': 3000,
            'DOGE-EUR': 2000,
            'SOL-EUR': 2000,
            'LINK-EUR': 1500,
            'XRP-EUR': 1000
        }
        default_capital = default_capitals.get(symbol, 5000)

        cfg = {
            'initial_capital': ticker_config.get('initialCapitalLong', default_capital),
            'commission_rate': COMMISSION_RATE,
            'min_commission': MIN_COMMISSION,
            'order_round_factor': ticker_config.get('order_round_factor', 0.01)
        }

        print(f"   💰 Initial Capital: €{cfg['initial_capital']}")
        print(f"   💸 Commission Rate: {cfg['commission_rate']*100}%")
        print(f"   🔧 Round Factor: {cfg['order_round_factor']}")

        start_idx = 0
        end_idx = len(df)
        p, tw = berechne_best_p_tw_long(df, cfg, start_idx, end_idx, verbose=True, ticker=symbol)
        return {
            'optimal_past_window': p,
            'optimal_trade_window': tw,
            'method': 'berechne_best_p_tw_long'
        }
    except Exception as e:
        print(f"❌ Parameter-Optimierung fehlgeschlagen: {e}")
        return {
            'optimal_past_window': 5,
            'optimal_trade_window': 2,
            'method': 'fallback'
        }

def simulate_matched_trades(ext_full, initial_capital, commission_rate, data_df=None, order_round_factor=1.0, trade_on='Close'):
    """
    Simuliert Matched Trades basierend auf Extended Signals
    Inkludiert offene Trades mit heutigem artificial price
    """
    try:
        if ext_full is None or ext_full.empty:
            return pd.DataFrame()
        
        matched = []
        position = None
        capital = initial_capital
        today = pd.Timestamp.now().date()
        
        # The 'Level Close' column contains the actual trading price (Open or Close) based on trade_on
        # This is set by update_level_close_long function
        price_column = 'Level Close'
        
        for idx, row in ext_full.iterrows():
            if row['Action'] == 'buy' and position is None:
                # Öffne Long Position
                position = {
                    'entry_date': row['Long Date detected'],
                    'entry_price': row[price_column],
                    'entry_idx': idx
                }
            elif row['Action'] == 'sell' and position is not None:
                # Schließe Position
                entry_price = position['entry_price']
                exit_price = row[price_column]
                
                # Calculate quantity using order_round_factor
                raw_quantity = capital / entry_price
                quantity = round(raw_quantity / order_round_factor) * order_round_factor
                
                pnl = (exit_price - entry_price) * quantity
                commission = (entry_price + exit_price) * quantity * commission_rate
                net_pnl = pnl - commission
                capital += net_pnl
                
                matched.append({
                    'Entry Date': position['entry_date'],
                    'Entry Price': round(entry_price, 2),
                    'Exit Date': row['Long Date detected'],
                    'Exit Price': round(exit_price, 2),
                    'Quantity': round(quantity, 4),
                    'PnL': round(pnl, 2),
                    'Commission': round(commission, 2),
                    'Net PnL': round(net_pnl, 2),
                    'Capital': round(capital, 2),
                    'Status': 'CLOSED'
                })
                position = None
        
        # ✅ OFFENE POSITION MIT HEUTIGEM ARTIFICIAL PRICE HINZUFÜGEN
        if position is not None and data_df is not None:
            entry_price = position['entry_price']
            
            # Calculate quantity using order_round_factor
            raw_quantity = capital / entry_price
            quantity = round(raw_quantity / order_round_factor) * order_round_factor
            
            # Heutigen artificial price finden
            today_timestamp = pd.Timestamp(today)
            artificial_price = entry_price  # Fallback
            
            if today_timestamp in data_df.index:
                artificial_price = data_df.loc[today_timestamp, 'Close']
                print(f"🤖 Offene Position: Heute's artificial price = €{artificial_price:.4f}")
            else:
                # Letzter verfügbarer Preis
                artificial_price = data_df['Close'].iloc[-1]
                print(f"🤖 Offene Position: Letzter verfügbarer Preis = €{artificial_price:.4f}")
            
            # Unrealized PnL berechnen
            unrealized_pnl = (artificial_price - entry_price) * quantity
            entry_commission = entry_price * quantity * commission_rate
            net_unrealized_pnl = unrealized_pnl - entry_commission
            
            matched.append({
                'Entry Date': position['entry_date'],
                'Entry Price': round(entry_price, 2),
                'Exit Date': today.strftime('%Y-%m-%d'),
                'Exit Price': round(artificial_price, 2),
                'Quantity': round(quantity, 4),
                'PnL': round(unrealized_pnl, 2),
                'Commission': round(entry_commission, 2),
                'Net PnL': round(net_unrealized_pnl, 2),
                'Capital': round(capital + net_unrealized_pnl, 2),  # ✅ FIXED: Use Net PnL instead of raw PnL
                'Status': 'OPEN',
                'Type': 'Artificial'
            })
            print(f"🔓 Offener Trade hinzugefügt: Entry={entry_price:.2f}, Current={artificial_price:.2f}, PnL={unrealized_pnl:.2f}, Net PnL={net_unrealized_pnl:.2f}")
        
        return pd.DataFrame(matched)
        
    except Exception as e:
        print(f"❌ Fehler in simulate_matched_trades: {e}")
        return pd.DataFrame()

def calculate_trade_statistics(ext_full, matched_trades, initial_capital):
    """
    Berechnet umfassende Trade-Statistiken
    """
    try:
        print(f"🔍 DEBUG: calculate_trade_statistics called with initial_capital = {initial_capital}")  # DEBUG
        stats = {}
        
        # Extended Signals Stats
        if ext_full is not None and not ext_full.empty:
            buy_signals = len(ext_full[ext_full['Action'] == 'buy'])
            sell_signals = len(ext_full[ext_full['Action'] == 'sell'])
            stats['📊 Total Extended Signals'] = len(ext_full)
            stats['📈 Buy Signals'] = buy_signals
            stats['📉 Sell Signals'] = sell_signals
        else:
            stats['📊 Total Extended Signals'] = 0
            stats['📈 Buy Signals'] = 0
            stats['📉 Sell Signals'] = 0
        
        # Matched Trades Stats
        if matched_trades is not None and not matched_trades.empty:
            total_trades = len(matched_trades)
            winning_trades = len(matched_trades[matched_trades['Net PnL'] > 0])
            losing_trades = len(matched_trades[matched_trades['Net PnL'] < 0])
            
            stats['🔄 Total Completed Trades'] = total_trades
            stats['✅ Winning Trades'] = winning_trades
            stats['❌ Losing Trades'] = losing_trades
            stats['📊 Win Rate'] = f"{(winning_trades/total_trades*100):.1f}%" if total_trades > 0 else "0%"
            
            if total_trades > 0:
                total_pnl = matched_trades['Net PnL'].sum()
                avg_win = matched_trades[matched_trades['Net PnL'] > 0]['Net PnL'].mean() if winning_trades > 0 else 0
                avg_loss = matched_trades[matched_trades['Net PnL'] < 0]['Net PnL'].mean() if losing_trades > 0 else 0
                final_capital = matched_trades['Capital'].iloc[-1] if len(matched_trades) > 0 else initial_capital
                
                stats['💰 Total PnL'] = f"€{total_pnl:.2f}"
                stats['📈 Average Win'] = f"€{avg_win:.2f}"
                stats['📉 Average Loss'] = f"€{avg_loss:.2f}"
                stats['💼 Final Capital'] = f"€{final_capital:.2f}"
                stats['📊 Total Return'] = f"{((final_capital/initial_capital-1)*100):.2f}%"
        else:
            stats['🔄 Total Completed Trades'] = 0
            stats['✅ Winning Trades'] = 0
            stats['❌ Losing Trades'] = 0
            stats['📊 Win Rate'] = "0%"
            stats['💰 Total PnL'] = "€0.00"
            stats['💼 Final Capital'] = f"€{initial_capital:.2f}"
            stats['📊 Total Return'] = "0.00%"
        
        return stats
        
    except Exception as e:
        print(f"❌ Fehler in calculate_trade_statistics: {e}")
        return {'Error': str(e)}

# REMOVE DUPLICATE FUNCTIONS BELOW THIS POINT
# The corrected functions are already defined above

# ✅ FIX 3: Main-Block korrigieren
if __name__ == "__main__":
    print("🚀 Running simple backtests for all configured tickers...")
    any_fail = False
    for sym, cfg in crypto_tickers.items():
        try:
            ok = run_backtest(sym, cfg)
            if ok is False:
                any_fail = True
        except Exception as e:
            any_fail = True
            print(f"❌ Fehler beim Backtest {sym}: {e}")
        print(f"   📅 Session Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📊 Configuration: {backtest_years} years")
        print("="*80)
    # Always generate unified report & charts
    try:
        print("\n🧪 Generating unified live backtest analysis (charts & HTML report)...")
        run_live_backtest_analysis()
    except Exception as e:
        any_fail = True
        print(f"⚠️ Unified analysis failed: {e}")
    if any_fail:
        print("\n❌ BACKTEST SESSION HAD FAILURES – see above.")
    else:
        print("\n✅ All backtests completed successfully.")
    print("🚀 Thank you for using Crypto Backtesting Suite!")
    print("="*80)

