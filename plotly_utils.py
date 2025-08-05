import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import pandas as pd
import os
import webbrowser
import time
def display_extended_trades_table(ext_signals, symbol):
    """
    KORRIGIERT: Verwende 'Long Action' statt 'Action'
    """
    if ext_signals is None or len(ext_signals) == 0:
        print("❌ Keine Extended Signals verfügbar!")
        return
    
    # Verfügbare Spalten prüfen
    print(f"� DEBUG: Verfügbare Spalten: {list(ext_signals.columns)}")
    
    # KORRIGIERE die Spalten-Namen:
    action_col = "Long Action" if "Long Action" in ext_signals.columns else "Action"
    
    print(f"📊 EXTENDED SIGNALS ({len(ext_signals)}) - {symbol}")
    print("=" * 140)
    print(f"{'#':<3} {'Date HL':<12} {'Level HL':<10} {'Type':<11} {action_col:<8} {'Close Level':<12} {'Detect Date':<12} {'Trade Day'}")
    print("-" * 140)
    
    for i, row in ext_signals.iterrows():
        action = row.get(action_col, "None")
        print(f"{i+1:<3} {str(row.get('Date high/low', 'N/A')):<12} "
              f"{row.get('Level high/low', 0.0):<10.4f} "
              f"{row.get('Supp/Resist', 'N/A'):<11} "
              f"{action:<8} "
              f"{row.get('Level Close', 0.0):<12.4f} "
              f"{str(row.get('Long Date detected', 'N/A')):<12} "
              f"{str(row.get('Long Trade Day', 'N/A'))}")
    
    print("=" * 140)
    
    # VERWENDE DIE RICHTIGE SPALTE FÜR ZÄHLUNG:
    try:
        buy_count = len(ext_signals[ext_signals[action_col] == 'buy'])
        sell_count = len(ext_signals[ext_signals[action_col] == 'sell'])
        none_count = len(ext_signals[ext_signals[action_col].isin(['None', None])])
        
        print(f"📊 Signal Summary: {buy_count} BUY, {sell_count} SELL, {none_count} None")
    except Exception as e:
        print(f"⚠️ Error counting signals: {e}")
def create_trades_dataframe(trades_text):
    """
    Convert trading text output to pandas DataFrame for better analysis
    """
    trades = []
    
    for line in trades_text.split('\n'):
        if '🔢 BUY:' in line:
            # Parse BUY trade
            try:
                parts = line.split(', ')
                trade_data = {
                    'Action': 'BUY',
                    'Date': parts[0].split('Date=')[1] if 'Date=' in parts[0] else None,
                    'Price': float(parts[2].split('Price=')[1]) if len(parts) > 2 and 'Price=' in parts[2] else None,
                    'Shares': float(parts[4].split('Shares=')[1]) if len(parts) > 4 and 'Shares=' in parts[4] else None,
                    'Capital': float(parts[1].split('Capital=')[1]) if len(parts) > 1 and 'Capital=' in parts[1] else None,
                    'Value': None,
                    'Fees': None,
                    'PnL': None
                }
                trades.append(trade_data)
            except Exception as e:
                print(f"   ⚠️ Error parsing BUY line: {e}")
            
        elif '💰 SELL:' in line:
            # Parse SELL trade
            try:
                parts = line.split(', ')
                trade_data = {
                    'Action': 'SELL',
                    'Date': parts[0].split('Date=')[1] if 'Date=' in parts[0] else None,
                    'Price': float(parts[1].split('Price=')[1]) if len(parts) > 1 and 'Price=' in parts[1] else None,
                    'Shares': None,
                    'Capital': None,
                    'Value': float(parts[2].split('Value=')[1]) if len(parts) > 2 and 'Value=' in parts[2] else None,
                    'Fees': float(parts[3].split('Fees=')[1]) if len(parts) > 3 and 'Fees=' in parts[3] else None,
                    'PnL': float(parts[4].split('PnL=')[1]) if len(parts) > 4 and 'PnL=' in parts[4] else None
                }
                trades.append(trade_data)
            except Exception as e:
                print(f"   ⚠️ Error parsing SELL line: {e}")
    
    if trades:
        df = pd.DataFrame(trades)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return pd.DataFrame()

def calculate_trade_statistics(trades_df):
    """
    Calculate comprehensive trading statistics from trades DataFrame
    """
    if trades_df.empty:
        return {}
    
    # Separate buy and sell trades
    buys = trades_df[trades_df['Action'] == 'BUY'].copy()
    sells = trades_df[trades_df['Action'] == 'SELL'].copy()
    
    if len(buys) == 0 or len(sells) == 0:
        return {}
    
    # Calculate statistics
    total_trades = len(sells)  # Count completed trades (sells)
    winning_trades = len(sells[sells['PnL'] > 0])
    losing_trades = len(sells[sells['PnL'] < 0])
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    total_pnl = sells['PnL'].sum()
    avg_win = sells[sells['PnL'] > 0]['PnL'].mean() if winning_trades > 0 else 0
    avg_loss = sells[sells['PnL'] < 0]['PnL'].mean() if losing_trades > 0 else 0
    
    max_win = sells['PnL'].max()
    max_loss = sells['PnL'].min()
    
    # Calculate returns
    initial_capital = buys['Capital'].iloc[0] if len(buys) > 0 else 10000
    final_capital = initial_capital + total_pnl
    total_return = ((final_capital - initial_capital) / initial_capital * 100) if initial_capital > 0 else 0
    
    # Profit factor
    gross_profit = sells[sells['PnL'] > 0]['PnL'].sum()
    gross_loss = abs(sells[sells['PnL'] < 0]['PnL'].sum())
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
    
    # Average trade
    avg_trade = total_pnl / total_trades if total_trades > 0 else 0
    
    statistics = {
        'Total Trades': total_trades,
        'Winning Trades': winning_trades,
        'Losing Trades': losing_trades,
        'Win Rate (%)': round(win_rate, 2),
        'Total PnL': round(total_pnl, 2),
        'Total Return (%)': round(total_return, 2),
        'Average Win': round(avg_win, 2),
        'Average Loss': round(avg_loss, 2),
        'Max Win': round(max_win, 2),
        'Max Loss': round(max_loss, 2),
        'Profit Factor': round(profit_factor, 2),
        'Average Trade': round(avg_trade, 2),
        'Initial Capital': round(initial_capital, 2),
        'Final Capital': round(final_capital, 2)
    }
    
    return statistics

def print_statistics_table(statistics):
    """
    Print trading statistics in a nice table format
    """
    if not statistics:
        print("   ⚠️ No statistics to display")
        return
    
    print("\n📊 TRADING PERFORMANCE STATISTICS")
    print("=" * 60)
    
    # Trade counts
    print(f"{'Total Trades:':<25} {statistics.get('Total Trades', 0):>10}")
    print(f"{'Winning Trades:':<25} {statistics.get('Winning Trades', 0):>10}")
    print(f"{'Losing Trades:':<25} {statistics.get('Losing Trades', 0):>10}")
    print(f"{'Win Rate:':<25} {statistics.get('Win Rate (%)', 0):>9.1f}%")
    
    print("-" * 60)
    
    # Financial metrics
    print(f"{'Initial Capital:':<25} {statistics.get('Initial Capital', 0):>10.2f}")
    print(f"{'Final Capital:':<25} {statistics.get('Final Capital', 0):>10.2f}")
    print(f"{'Total PnL:':<25} {statistics.get('Total PnL', 0):>10.2f}")
    print(f"{'Total Return:':<25} {statistics.get('Total Return (%)', 0):>9.1f}%")
    
    print("-" * 60)
    
    # Trade analysis
    print(f"{'Average Win:':<25} {statistics.get('Average Win', 0):>10.2f}")
    print(f"{'Average Loss:':<25} {statistics.get('Average Loss', 0):>10.2f}")
    print(f"{'Average Trade:':<25} {statistics.get('Average Trade', 0):>10.2f}")
    print(f"{'Max Win:':<25} {statistics.get('Max Win', 0):>10.2f}")
    print(f"{'Max Loss:':<25} {statistics.get('Max Loss', 0):>10.2f}")
    print(f"{'Profit Factor:':<25} {statistics.get('Profit Factor', 0):>10.2f}")
    
    print("=" * 60)

def format_trading_tables(trades_text, statistics_text=""):
    """
    Parse trading text output and format into separate buy/sell tables
    Returns formatted buy_trades and sell_trades lists
    """
    buy_trades = []
    sell_trades = []
    
    if not trades_text:
        return buy_trades, sell_trades
    
    print("\n📊 FORMATTING TRADING TABLES...")
    
    lines = trades_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        
        if '🔢 BUY:' in line:
            # Parse BUY line: 🔢 BUY: Date=2024-01-15, Capital=10000.00, Price=45.1234, Raw=221.123456, Shares=221.123000
            try:
                parts = line.split(', ')
                buy_data = {}
                
                for part in parts:
                    if 'Date=' in part:
                        buy_data['Date'] = part.split('Date=')[1].strip()
                    elif 'Capital=' in part:
                        buy_data['Capital'] = float(part.split('Capital=')[1].strip())
                    elif 'Price=' in part:
                        buy_data['Price'] = float(part.split('Price=')[1].strip())
                    elif 'Raw=' in part:
                        buy_data['Raw Shares'] = float(part.split('Raw=')[1].strip())
                    elif 'Shares=' in part:
                        buy_data['Shares'] = float(part.split('Shares=')[1].strip())
                
                if buy_data:
                    buy_trades.append(buy_data)
                    
            except Exception as e:
                print(f"   ⚠️ Error parsing BUY line: {e}")
                print(f"   Line: {line}")
        
        elif '💰 SELL:' in line:
            # Parse SELL line: 💰 SELL: Date=2024-02-20, Price=48.5678, Value=1234.567, Fees=12.345, PnL=156.789
            try:
                parts = line.split(', ')
                sell_data = {}
                
                for part in parts:
                    if 'Date=' in part:
                        sell_data['Date'] = part.split('Date=')[1].strip()
                    elif 'Price=' in part:
                        sell_data['Price'] = float(part.split('Price=')[1].strip())
                    elif 'Value=' in part:
                        sell_data['Trade Value'] = float(part.split('Value=')[1].strip())
                    elif 'Fees=' in part:
                        sell_data['Fees'] = float(part.split('Fees=')[1].strip())
                    elif 'PnL=' in part:
                        sell_data['PnL'] = float(part.split('PnL=')[1].strip())
                
                if sell_data:
                    sell_trades.append(sell_data)
                    
            except Exception as e:
                print(f"   ⚠️ Error parsing SELL line: {e}")
                print(f"   Line: {line}")
    
    # Display formatted tables
    if buy_trades:
        print(f"\n📈 BUY TRADES ({len(buy_trades)}):")
        print("-" * 80)
        print(f"{'#':<3} {'Date':<12} {'Capital':<12} {'Price':<10} {'Raw Shares':<12} {'Shares':<12}")
        print("-" * 80)
        
        for i, trade in enumerate(buy_trades, 1):
            print(f"{i:<3} {trade.get('Date', 'N/A'):<12} {trade.get('Capital', 0):<12.2f} "
                  f"{trade.get('Price', 0):<10.4f} {trade.get('Raw Shares', 0):<12.6f} "
                  f"{trade.get('Shares', 0):<12.6f}")
        print("-" * 80)
    
    if sell_trades:
        print(f"\n📉 SELL TRADES ({len(sell_trades)}):")
        print("-" * 80)
        print(f"{'#':<3} {'Date':<12} {'Price':<10} {'Trade Value':<12} {'Fees':<8} {'PnL':<10}")
        print("-" * 80)
        
        for i, trade in enumerate(sell_trades, 1):
            print(f"{i:<3} {trade.get('Date', 'N/A'):<12} {trade.get('Price', 0):<10.4f} "
                  f"{trade.get('Trade Value', 0):<12.2f} {trade.get('Fees', 0):<8.2f} "
                  f"{trade.get('PnL', 0):<10.2f}")
        print("-" * 80)
    
    if statistics_text:
        print(f"\n📊 STATISTICS SUMMARY:")
        print("-" * 40)
        for line in statistics_text.split('\n'):
            if line.strip():
                print(f"   {line}")
        print("-" * 40)
    
    print(f"✅ Formatted {len(buy_trades)} BUY trades and {len(sell_trades)} SELL trades")
    
    return buy_trades, sell_trades

def analyze_trading_results(trades_text):
    """
    Complete analysis of trading results with tables and statistics
    """
    print("\n🔍 ANALYZING TRADING RESULTS...")
    
    # Format trades as tables
    buy_trades, sell_trades = format_trading_tables(trades_text)
    
    # Create DataFrame for analysis
    trades_df = create_trades_dataframe(trades_text)
    
    if not trades_df.empty:
        # Calculate statistics
        statistics = calculate_trade_statistics(trades_df)
        
        # Print statistics table
        print_statistics_table(statistics)
        
        # Return for further use
        return trades_df, statistics
    else:
        print("   ⚠️ No valid trades found for analysis")
        return pd.DataFrame(), {}
# Replace everything from line 330 onwards with this:

def plotly_combined_chart_and_equity(
    df,
    standard_signals,
    support,
    resistance,
    equity_curve,
    buyhold_curve,
    ticker,
    backtest_years=None
):
    """
    VOLLSTÄNDIGE Plotly Chart mit ALLEN MARKERN und 2.5x höherer Equity Y-Achse
    """
    print(f"   📊 Creating Enhanced Plotly Chart for {ticker}...")
    
    try:
        # Data validation
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                '_'.join([str(level) for level in col if level and str(level) != 'nan']).strip()
                for col in df.columns.values
            ]
        
        # Ensure OHLC columns
        required_cols = ["Open", "High", "Low", "Close"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"   ❌ Missing columns: {missing_cols}")
            return False
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=[0.5, 0.5],
            subplot_titles=(f"{ticker} - Candlestick with All Markers", "Equity Curves")
        )
        
        # 1. CANDLESTICK CHART
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=f"{ticker}",
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            row=1, col=1
        )
        
        # 2. ✅ SUPPORT MARKERS (Grüne Kreise) - 2% BELOW LOW
        if hasattr(support, 'index') and len(support) > 0:
            try:
                support_clean = support.dropna()
                if not support_clean.empty:
                    # Calculate support positions: 2% below Low at each date
                    support_y_positions = []
                    for date in support_clean.index:
                        if date in df.index:
                            low_price = df.loc[date, 'Low']
                            support_y_positions.append(low_price * 0.98)  # 2% below Low
                        else:
                            support_y_positions.append(support_clean.loc[date])  # Fallback
                    
                    fig.add_trace(
                        go.Scatter(
                            x=support_clean.index,
                            y=support_y_positions,  # ✅ 2% below Low
                            mode="markers",
                            name="🟢 Support",
                            marker=dict(
                                color="lime",
                                size=10,
                                symbol="circle-open",
                                line=dict(width=3, color="green")
                            ),
                            showlegend=True,
                            hovertemplate="<b>SUPPORT</b><br>Date: %{x}<br>Level: %{y:.2f}<extra></extra>"
                        ),
                        row=1, col=1
                    )
                    print(f"   ✅ {len(support_clean)} SUPPORT markers added (2% below Low)")
            except Exception as e:
                print(f"   ❌ Support plotting error: {e}")
        
        # 3. ✅ RESISTANCE MARKERS (Rote X) - 2% ABOVE HIGH
        if hasattr(resistance, 'index') and len(resistance) > 0:
            try:
                resistance_clean = resistance.dropna()
                if not resistance_clean.empty:
                    # Calculate resistance positions: 2% above High at each date
                    resistance_y_positions = []
                    for date in resistance_clean.index:
                        if date in df.index:
                            high_price = df.loc[date, 'High']
                            resistance_y_positions.append(high_price * 1.02)  # 2% above High
                        else:
                            resistance_y_positions.append(resistance_clean.loc[date])  # Fallback
                    
                    fig.add_trace(
                        go.Scatter(
                            x=resistance_clean.index,
                            y=resistance_y_positions,  # ✅ 2% above High
                            mode="markers",
                            name="🔴 Resistance",
                            marker=dict(
                                color="red",
                                size=10,
                                symbol="x",
                                line=dict(width=3, color="darkred")
                            ),
                            showlegend=True,
                            hovertemplate="<b>RESISTANCE</b><br>Date: %{x}<br>Level: %{y:.2f}<extra></extra>"
                        ),
                        row=1, col=1
                    )
                    print(f"   ✅ {len(resistance_clean)} RESISTANCE markers added (2% above High)")
            except Exception as e:
                print(f"   ❌ Resistance plotting error: {e}")
        
        # 4. ✅ BUY/SELL SIGNALS aus DataFrame
        buy_markers_added = 0
        sell_markers_added = 0
        
        if 'buy_signal' in df.columns and 'sell_signal' in df.columns:
            # ✅ BUY signals (Blaue Dreiecke nach oben) - 5% BELOW LOW
            buy_mask = df['buy_signal'].notna() & (df['buy_signal'] == 1)
            if buy_mask.any():
                buy_signals = df[buy_mask]
                buy_dates = buy_signals.index
                buy_prices = buy_signals['Low'] * 0.95  # ✅ 5% below Low
                fig.add_trace(
                    go.Scatter(
                        x=buy_dates,
                        y=buy_prices,
                        mode="markers",
                        name="🔵 BUY",
                        marker=dict(
                            color="blue",
                            size=10,
                            symbol="triangle-up",
                            line=dict(width=1, color="blue")
                        ),
                        showlegend=True,
                        hovertemplate="<b>BUY SIGNAL</b><br>Date: %{x}<br>Price: %{y:.2f}<extra></extra>"
                    ),
                    row=1, col=1
                )
                buy_markers_added = len(buy_dates)
            
            # ✅ SELL signals (Orange Dreiecke nach unten) - 5% ABOVE HIGH
            sell_mask = df['sell_signal'].notna() & (df['sell_signal'] == 1)
            if sell_mask.any():
                sell_signals = df[sell_mask]
                sell_dates = sell_signals.index
                sell_prices = sell_signals['High'] * 1.05  # ✅ 5% above High
                fig.add_trace(
                    go.Scatter(
                        x=sell_dates,
                        y=sell_prices,
                        mode="markers",
                        name="🟠 SELL",
                        marker=dict(
                            color="orange",
                            size=10,
                            symbol="triangle-down",
                            line=dict(width=1, color="darkorange")
                        ),
                        showlegend=True,
                        hovertemplate="<b>SELL SIGNAL</b><br>Date: %{x}<br>Price: %{y:.2f}<extra></extra>"
                    ),
                    row=1, col=1
                )
                sell_markers_added = len(sell_dates)
        
        print(f"   📊 TRADE markers: {buy_markers_added} BUY (5% below Low), {sell_markers_added} SELL (5% above High)")
        
        # 5. EQUITY CURVES
        if len(equity_curve) > 0:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=equity_curve,
                    mode="lines",
                    name="💼 Strategy",
                    line=dict(color="green", width=2)
                ),
                row=2, col=1
            )
        
        if len(buyhold_curve) > 0:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=buyhold_curve,
                    mode="lines",
                    name="📈 Buy & Hold",
                    line=dict(color="orange", width=2)
                ),
                row=2, col=1
            )
        
        # ✅ EQUITY Y-ACHSE 2.5x VERGRÖSSERN
        if len(equity_curve) > 0 or len(buyhold_curve) > 0:
            # Sammle alle Equity-Werte
            all_equity_values = []
            if len(equity_curve) > 0:
                all_equity_values.extend(equity_curve)
            if len(buyhold_curve) > 0:
                all_equity_values.extend(buyhold_curve)
            
            if all_equity_values:
                min_equity = min(all_equity_values)
                max_equity = max(all_equity_values)
                equity_range = max_equity - min_equity
                equity_center = (min_equity + max_equity) / 2
                # 0.5x größerer Y-Achsen-Bereich
                expansion_factor = 1
                expanded_range = equity_range * expansion_factor
                
                new_y_min = equity_center - expanded_range / 2
                new_y_max = equity_center + expanded_range / 2
                
                # Stelle sicher, dass Y-Min nicht negativ wird (wenn Original positiv)
                if min_equity >= 0 and new_y_min < 0:
                    new_y_min = 0
                    new_y_max = expanded_range
                
                # Anwenden der erweiterten Y-Achse
                fig.update_yaxes(
                    range=[new_y_min, new_y_max],
                    row=2, col=1
                )
                
                print(f"   📊 Equity Y-Axis expanded: €{new_y_min:,.0f} to €{new_y_max:,.0f}")
        
        # LAYOUT OPTIMIERUNG
        fig.update_layout(
            title=f"📊 {ticker} - Complete Trading Analysis",
            height=1100,
            template="plotly_dark",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # X-Axis ohne Rangeslider für oberes Chart
        fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
        
        # Y-Axis Labels
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Capital", row=2, col=1)
        
        # CHART SPEICHERN UND ÖFFNEN
        chart_filename = f"chart_{ticker.replace('-', '_')}.html"
        chart_path = os.path.join("reports", chart_filename)
        
        # Stelle sicher, dass reports Ordner existiert
        os.makedirs("reports", exist_ok=True)
        
        # Chart speichern
        fig.write_html(chart_path)
        print(f"   💾 Chart saved: {chart_path}")
        
        # Chart im Browser öffnen
        try:
            abs_path = os.path.abspath(chart_path)
            webbrowser.open(f"file://{abs_path}")
            print(f"   🌐 Chart opened in browser: {ticker}")
            time.sleep(1)  # Kurze Pause zwischen Charts
        except Exception as e:
            print(f"   ❌ Browser opening failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Chart creation failed for {ticker}: {e}")
        import traceback
        traceback.print_exc()
        return False

def open_all_charts_in_sequence():
    """
    Öffnet alle Charts der Reihe nach im Browser
    """
    import glob
    
    chart_files = glob.glob("reports/chart_*.html")
    print(f"\n🌐 Opening {len(chart_files)} charts in sequence...")
    
    for i, chart_path in enumerate(sorted(chart_files)):
        try:
            abs_path = os.path.abspath(chart_path)
            webbrowser.open(f"file://{abs_path}")
            chart_name = os.path.basename(chart_path)
            print(f"   {i+1}/{len(chart_files)} ✅ Opened: {chart_name}")
            time.sleep(2)  # 2 Sekunden zwischen Charts
        except Exception as e:
            print(f"   ❌ Failed to open {chart_path}: {e}")
    
    print(f"🎯 All {len(chart_files)} charts opened!")

def create_equity_curve_from_matched_trades(matched_trades, initial_capital, df_bt):
    """
    Create equity curve from matched trades
    """
    equity_curve = []
    current_capital = initial_capital
    position_shares = 0
    position_price = 0
    trade_index = 0
    completed_trades = [t for t in matched_trades if not t.get('is_open', False)]
    
    for date in df_bt.index:
        # Check for buy signal
        if trade_index < len(completed_trades):
            trade = completed_trades[trade_index]
            buy_date = pd.to_datetime(trade.get('buy_date', ''))
            
            if date.date() == buy_date.date() and position_shares == 0:
                position_shares = trade.get('shares', 0)
                position_price = trade.get('buy_price', 0)
                # Don't subtract capital here - we track total portfolio value
        
        # Check for sell signal
        if trade_index < len(completed_trades) and position_shares > 0:
            trade = completed_trades[trade_index]
            sell_date = pd.to_datetime(trade.get('sell_date', ''))
            
            if date.date() == sell_date.date():
                # Update capital with realized PnL
                current_capital += trade.get('pnl', 0)
                position_shares = 0
                position_price = 0
                trade_index += 1
        
        # Calculate current equity (cash + position value)
        if position_shares > 0:
            current_price = df_bt.loc[date, 'Close']
            # Cash portion after buying
            cash_portion = current_capital - (position_shares * position_price)
            # Current position value
            position_value = position_shares * current_price
            equity = cash_portion + position_value
        else:
            equity = current_capital
        
        equity_curve.append(equity)
    
    # Handle open position if exists
    open_trades = [t for t in matched_trades if t.get('is_open', False)]
    if open_trades and equity_curve:
        open_trade = open_trades[0]
        open_shares = open_trade.get('shares', 0)
        open_price = open_trade.get('buy_price', 0)
        current_price = df_bt['Close'].iloc[-1]
        
        # Adjust final equity for open position
        cash_after_buy = equity_curve[-1] - (open_shares * open_price)
        open_position_value = open_shares * current_price
        equity_curve[-1] = cash_after_buy + open_position_value
    
    return equity_curve

def test_chart_opening():
    """Test function to manually open charts"""
    import glob
    chart_files = glob.glob("reports/chart_*.html")
    
    print(f"Found {len(chart_files)} chart files:")
    for chart in chart_files:
        print(f"  - {chart}")
        
    if chart_files:
        try:
            latest_chart = max(chart_files, key=os.path.getctime)
            os.startfile(os.path.abspath(latest_chart))
            print(f"✅ Opened latest chart: {latest_chart}")
        except Exception as e:
            print(f"❌ Failed to open chart: {e}")

# Call this function manually if needed:
# test_chart_opening()

def add_buy_sell_markers_to_df(df_bt, matched_trades):
    """
    Add buy/sell markers to dataframe for plotting
    FIXED: Better date matching and debugging
    """
    df_with_markers = df_bt.copy()
    df_with_markers['buy_signal'] = None
    df_with_markers['sell_signal'] = None
    df_with_markers['buy_price'] = None
    df_with_markers['sell_price'] = None
    
    print(f"🔍 DEBUG: Adding markers to df with {len(df_bt)} rows")
    print(f"🔍 DEBUG: Processing {len(matched_trades)} matched trades")
    print(f"🔍 DEBUG: df_bt index type: {type(df_bt.index)}")
    print(f"🔍 DEBUG: df_bt date range: {df_bt.index.min()} to {df_bt.index.max()}")
    
    buy_markers_added = 0
    sell_markers_added = 0
    
    for i, trade in enumerate(matched_trades):
        # Skip open trades for sell markers, but add buy markers
        buy_date_str = trade.get('buy_date', '')
        sell_date_str = trade.get('sell_date', '')
        is_open = trade.get('is_open', False)
        
        print(f"   🔍 Trade {i+1}: BUY {buy_date_str} -> SELL {sell_date_str} {'(OPEN)' if is_open else ''}")
        
        # Process BUY marker (for all trades)
        try:
            buy_date = pd.to_datetime(buy_date_str)
            
            # Method 1: Direct date match
            if buy_date in df_with_markers.index:
                df_with_markers.loc[buy_date, 'buy_signal'] = 1
                df_with_markers.loc[buy_date, 'buy_price'] = trade.get('buy_price', 0)
                buy_markers_added += 1
                print(f"     ✅ BUY marker added for {buy_date.date()}")
            else:
                # Method 2: Find nearest date
                nearest_buy_idx = df_with_markers.index.get_indexer([buy_date], method='nearest')[0]
                if nearest_buy_idx >= 0:
                    nearest_buy_date = df_with_markers.index[nearest_buy_idx]
                    df_with_markers.loc[nearest_buy_date, 'buy_signal'] = 1
                    df_with_markers.loc[nearest_buy_date, 'buy_price'] = trade.get('buy_price', 0)
                    buy_markers_added += 1
                    print(f"     ✅ BUY marker added for {nearest_buy_date.date()} (nearest to {buy_date.date()})")
                else:
                    print(f"     ❌ BUY date {buy_date.date()} not found")
                    
        except Exception as e:
            print(f"     ❌ Error processing BUY for trade {i+1}: {e}")
        
        # Process SELL marker (only for completed trades)
        if not is_open and sell_date_str:
            try:
                sell_date = pd.to_datetime(sell_date_str)
                
                # Method 1: Direct date match
                if sell_date in df_with_markers.index:
                    df_with_markers.loc[sell_date, 'sell_signal'] = 1
                    df_with_markers.loc[sell_date, 'sell_price'] = trade.get('sell_price', 0)
                    sell_markers_added += 1
                    print(f"     ✅ SELL marker added for {sell_date.date()}")
                else:
                    # Method 2: Find nearest date
                    nearest_sell_idx = df_with_markers.index.get_indexer([sell_date], method='nearest')[0]
                    if nearest_sell_idx >= 0:
                        nearest_sell_date = df_with_markers.index[nearest_sell_idx]
                        df_with_markers.loc[nearest_sell_date, 'sell_signal'] = 1
                        df_with_markers.loc[nearest_sell_date, 'sell_price'] = trade.get('sell_price', 0)
                        sell_markers_added += 1
                        print(f"     ✅ SELL marker added for {nearest_sell_date.date()} (nearest to {sell_date.date()})")
                    else:
                        print(f"     ❌ SELL date {sell_date.date()} not found")
                        
            except Exception as e:
                print(f"     ❌ Error processing SELL for trade {i+1}: {e}")
    
    print(f"🎯 MARKERS SUMMARY: {buy_markers_added} BUY, {sell_markers_added} SELL added to dataframe")
    
    # Verify markers were added
    buy_count = df_with_markers['buy_signal'].notna().sum()
    sell_count = df_with_markers['sell_signal'].notna().sum()
    print(f"🔍 VERIFICATION: {buy_count} BUY signals, {sell_count} SELL signals in dataframe")
    
    return df_with_markers

def analyze_trading_results(trades_df, initial_capital=10000):
    """
    Simple trading results analysis function
    """
    if trades_df.empty:
        return {}
    
    # Basic analysis
    total_trades = len(trades_df)
    
    # Try to find PnL column
    pnl_col = None
    for col in ['PnL', 'pnl', 'profit_loss', 'P&L']:
        if col in trades_df.columns:
            pnl_col = col
            break
    
    if pnl_col:
        total_pnl = trades_df[pnl_col].sum()
        winning_trades = len(trades_df[trades_df[pnl_col] > 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    else:
        total_pnl = 0
        winning_trades = 0
        win_rate = 0
    
    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'win_rate': win_rate,
        'total_pnl': total_pnl,
        'final_capital': initial_capital + total_pnl
    }

