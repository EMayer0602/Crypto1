
    
# Import necessary libraries

import datetime
from datetime import datetime, timedelta                   # Import necessary libraries
import os
import datetime
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import numpy as np
from scipy.signal import argrelextrema
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Add this import at the top of your code
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # Import mdates for date formatting
from mplfinance.original_flavor import candlestick_ohlc
import json
# Liste der Ticker-Dateien
csv_dir = r"C:\Users\Edgar.000\Documents\____Trading strategies"
csv_files = [
    "DOGE-EUR.csv",
    "ETH-EUR.csv",
    "LINK-EUR.csv",
    "SOL-EUR.csv",
    "XRP-EUR.csv",
    "BTC-EUR.csv"
]

stock_symbol = 'AAPL'  # Example stock symbol"
past_window=8
trade_window=1
#0Yahoo Finance: Supports intervals like 1d, 1h, 5m.
#Twelve Data API: Supports intervals like 1min, 5min, 15min, 1h, 1day.
#Alpha Vantage: Supports intervals like 1min, 5min, 15min, 30min, 60min.
initial_capital=15000
trade_fee=0.001
share_rounding=0.01
optimize = 0    
#api_key = 'T5TOU0D1VD5O981I' #alpha vantage
#api_key = "e13303cc06754b8ea998da6c07d7ee2c"# Telve  Data
interval = "1d"
#period = "10d"




# Clean up the DataFrame columns to have simple names
def clean_dataframe_columns(df):
    # Get the first level of the MultiIndex columns
    new_columns = [col[0] for col in df.columns]
    
    # Create a new DataFrame with simplified column names
    df_clean = df.copy()
    df_clean.columns = new_columns
    
    return df_clean

def get_data(ticker, period, interval):
    """
    Fetch historical data for the given ticker.
    """
    try:
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=False)
        # Flatten multi-level column names if they exist
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        return data
#        print(data)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Calculate Jurik SMA (20)
def jurik_sma(series, period):
    return series.rolling(window=period).mean()

def round_to_multiple(value, multiple):
    """Round a value to the nearest multiple of a given parameter."""
    if multiple == 0 or multiple is None:
        raise ValueError("The 'multiple' parameter must be greater than 0.")
    return round(value / multiple) * multiple
# Funktion zur Berechnung der Trades

# Identify support and resistance levels
from scipy.signal import argrelextrema

def identify_support_resistance(df, past_window, trade_window):
    """
    Identify support and resistance levels using local extrema with asymmetric windows.

    Parameters:
    - df: DataFrame containing the price data.
    - past_window: Number of intervals to look into the past for extrema.
    - trade_window: Number of intervals to look into the future for extrema.

    Returns:
    - support: Series containing support levels.
    - resistance: Series containing resistance levels.
    """
    # Total window size for extrema detection
    total_window = past_window + trade_window

    # Extract the 'Close' prices as a NumPy array
    prices = df["Close"].values

    # Identify local minima (support levels)
    local_min_idx = argrelextrema(prices, np.less, order=total_window)[0]
    support = pd.Series(prices[local_min_idx], index=df.index[local_min_idx])

    # Identify local maxima (resistance levels)
    local_max_idx = argrelextrema(prices, np.greater, order=total_window)[0]
    resistance = pd.Series(prices[local_max_idx], index=df.index[local_max_idx])

    return support, resistance

def assign_signals(support, resistance, data, trade_window, interval):
    """
    Combine support and resistance levels and assign buy/sell and short/cover signals.

    Parameters:
    - support: Series containing support levels.
    - resistance: Series containing resistance levels.
    - data: DataFrame containing the price data (must include 'Close').
    - trade_window: Number of intervals to delay the signals.
    - interval: The interval as a string (e.g., "5min", "1h", "1d").

    Returns:
    - combined_df: DataFrame with combined levels and assigned signals.
    """
    # Ensure data is sorted in ascending order
    data.sort_index(inplace=True)

    # Combine support and resistance levels
    support_df = pd.DataFrame({'Date': support.index, 'Level': support.values, 'Type': 'support'})
    resistance_df = pd.DataFrame({'Date': resistance.index, 'Level': resistance.values, 'Type': 'resistance'})
    combined_df = pd.concat([support_df, resistance_df]).sort_values(by='Date').reset_index(drop=True)

    # Initialize columns for signals
    combined_df['Long'] = None
    combined_df['Long Date'] = pd.NaT
    combined_df['Short'] = None
    combined_df['Short Date'] = pd.NaT

    # Track the state of long and short positions
    long_active = False
    short_active = False

    for i, row in combined_df.iterrows():
        base_date = row['Date']

        # Calculate trade_date dynamically based on the interval
        if interval.endswith("min") or interval.endswith("m"):  # Handle intervals like "5m", "15m"
            trade_date = base_date + pd.Timedelta(minutes=trade_window * int(interval.replace("min", "").replace("m", "")))
        elif interval.endswith("h"):
            trade_date = base_date + pd.Timedelta(hours=trade_window)
        elif interval in ["1d", "1day"]:
            trade_date = base_date + pd.Timedelta(days=trade_window)
        else:
            raise ValueError(f"Unsupported interval: {interval}")

        # Ensure trade_date exists in data.index
        if trade_date not in data.index:
            trade_date_idx = data.index.searchsorted(trade_date)
            if trade_date_idx < len(data.index):
                trade_date = data.index[trade_date_idx]
            else:
                trade_date = pd.NaT  # If no valid future date is found

        # Assign signals based on position state
        if row['Type'] == 'support':
            if not long_active:  # Only buy if no long position is active
                combined_df.at[i, 'Long'] = 'buy'
                combined_df.at[i, 'Long Date'] = trade_date
                long_active = True
            if short_active:  # Cover short position if active
                combined_df.at[i, 'Short'] = 'cover'
                combined_df.at[i, 'Short Date'] = trade_date
                short_active = False
        elif row['Type'] == 'resistance':
            if long_active:  # Sell only if a long position is active
                combined_df.at[i, 'Long'] = 'sell'
                combined_df.at[i, 'Long Date'] = trade_date
                long_active = False
            if not short_active:  # Only short if no short position is active
                combined_df.at[i, 'Short'] = 'short'
                combined_df.at[i, 'Short Date'] = trade_date
                short_active = True

    # Convert all dates to timezone-naive
    combined_df['Date'] = pd.to_datetime(combined_df['Date']).dt.tz_localize(None)
    combined_df['Long Date'] = pd.to_datetime(combined_df['Long Date'], errors='coerce').dt.tz_localize(None)
    combined_df['Short Date'] = pd.to_datetime(combined_df['Short Date'], errors='coerce').dt.tz_localize(None)

    return combined_df
    """
    Combine support and resistance levels and assign buy/sell and short/cover signals.

    Parameters:
    - support: Series containing support levels.
    - resistance: Series containing resistance levels.
    - data: DataFrame containing the price data (must include 'Close').
    - trade_window: Number of intervals to delay the signals.
    - interval: The interval as a string (e.g., "5min", "1h", "1d").

    Returns:
    - combined_df: DataFrame with combined levels and assigned signals.
    """
    # Ensure data is sorted in ascending order
    data.sort_index(inplace=True)

    # Combine support and resistance levels
    support_df = pd.DataFrame({'Date': support.index, 'Level': support.values, 'Type': 'support'})
    resistance_df = pd.DataFrame({'Date': resistance.index, 'Level': resistance.values, 'Type': 'resistance'})
    combined_df = pd.concat([support_df, resistance_df]).sort_values(by='Date').reset_index(drop=True)

    # Initialize columns for signals
    combined_df['Long'] = None
    combined_df['Long Date'] = pd.NaT
    combined_df['Short'] = None
    combined_df['Short Date'] = pd.NaT

    # Track the state of long and short positions
    long_active = False
    short_active = False

    for i, row in combined_df.iterrows():
        base_date = row['Date']

        # Calculate trade_date dynamically based on the interval
        if interval.endswith("min"):
            trade_date = base_date + pd.Timedelta(minutes=trade_window * int(interval.replace("min", "")))
        elif interval.endswith("h"):
            trade_date = base_date + pd.Timedelta(hours=trade_window)
        elif interval in ["1d", "1day"]:
            trade_date = base_date + pd.Timedelta(days=trade_window)
        else:
            raise ValueError(f"Unsupported interval: {interval}")

        # Ensure trade_date exists in data.index
        if trade_date not in data.index:
            trade_date_idx = data.index.searchsorted(trade_date)
            if trade_date_idx < len(data.index):
                trade_date = data.index[trade_date_idx]
            else:
                trade_date = pd.NaT  # If no valid future date is found

        # Assign signals based on position state
        if row['Type'] == 'support':
            if not long_active:  # Only buy if no long position is active
                combined_df.at[i, 'Long'] = 'buy'
                combined_df.at[i, 'Long Date'] = trade_date
                long_active = True
            if short_active:  # Cover short position if active
                combined_df.at[i, 'Short'] = 'cover'
                combined_df.at[i, 'Short Date'] = trade_date
                short_active = False
        elif row['Type'] == 'resistance':
            if long_active:  # Sell only if a long position is active
                combined_df.at[i, 'Long'] = 'sell'
                combined_df.at[i, 'Long Date'] = trade_date
                long_active = False
            if not short_active:  # Only short if no short position is active
                combined_df.at[i, 'Short'] = 'short'
                combined_df.at[i, 'Short Date'] = trade_date
                short_active = True

    # Convert all dates to timezone-naive
    combined_df['Date'] = pd.to_datetime(combined_df['Date']).dt.tz_localize(None)
    combined_df['Long Date'] = pd.to_datetime(combined_df['Long Date'], errors='coerce').dt.tz_localize(None)
    combined_df['Short Date'] = pd.to_datetime(combined_df['Short Date'], errors='coerce').dt.tz_localize(None)

    return combined_df

def translate_long_trades(combined_df, data, initial_capital, trade_fee):
    """
    Translate support and resistance signals into long trades.

    Parameters:
    - combined_df: DataFrame containing support and resistance signals.
    - data: DataFrame containing price data.
    - initial_capital: Starting capital for the strategy.
    - trade_fee: Percentage fee for each trade.

    Returns:
    - long_trades: List of long trades.
    - total_long_pnl: Total profit and loss from long trades.
    """
    long_trades = []
    long_active = False
    total_long_pnl = 0
    position_price = 0
    shares_long = 0

    for i, row in combined_df.iterrows():
        if pd.isna(row['Long']) or pd.isna(row['Long Date']):
            continue  # Skip rows without long signals

        trade_date = row['Long Date']

        # Adjust trade_date to the next available trading datetime
        if trade_date not in data.index:
            trade_date_idx = data.index.searchsorted(trade_date)
            if trade_date_idx < len(data.index):
                trade_date = data.index[trade_date_idx]
            else:
                continue  # Skip if no valid future date is found

        if row['Long'] == 'buy' and not long_active:
            position_price = data.loc[trade_date, 'Close']
            shares_long = round(initial_capital / position_price, 2)
            entry_fee = position_price * shares_long * trade_fee
            long_trades.append({
                'Action': 'BUY',
                'Date': trade_date,
                'Price': position_price,
                'Shares': shares_long,
                'PnL': -entry_fee  # Subtract entry fee only
            })
            long_active = True
        elif row['Long'] == 'sell' and long_active:
            sell_price = data.loc[trade_date, 'Close']
            pnl = shares_long * (sell_price - position_price)
            exit_fee = sell_price * shares_long * trade_fee
            pnl -= exit_fee  # Subtract exit fee only
            total_long_pnl += pnl
            long_trades.append({
                'Action': 'SELL',
                'Date': trade_date,
                'Price': sell_price,
                'Shares': shares_long,
                'PnL': pnl
            })
            long_active = False

    # Handle unmatched open long trade
    if long_active:
        last_price = data['Close'].iloc[-1]  # Use the last available close price
        pnl = shares_long * (last_price - position_price)  # Calculate PnL
        exit_fee = last_price * shares_long * trade_fee  # Calculate exit fee
        pnl -= exit_fee  # Subtract exit fee
        total_long_pnl += pnl
        long_trades.append({
            'Action': 'SELL',
            'Date': data.index[-1],  # Use the last available date
            'Price': last_price,
            'Shares': shares_long,
            'PnL': pnl
        })

    return long_trades, total_long_pnl

def translate_short_trades(combined_df, data, initial_capital, trade_fee):
    """
    Translate support and resistance signals into short trades.

    Parameters:
    - combined_df: DataFrame containing support and resistance signals.
    - data: DataFrame containing price data.
    - initial_capital: Starting capital for the strategy.
    - trade_fee: Percentage fee for each trade.

    Returns:
    - short_trades: List of short trades.
    - total_short_pnl: Total profit and loss from short trades.
    """
    short_trades = []
    short_active = False
    total_short_pnl = 0
    position_price = 0
    shares_short = 0

    for i, row in combined_df.iterrows():
        if pd.isna(row['Short']) or pd.isna(row['Short Date']):
            continue  # Skip rows without short signals

        trade_date = row['Short Date']

        # Adjust trade_date to the next available trading datetime
        if trade_date not in data.index:
            trade_date_idx = data.index.searchsorted(trade_date)
            if trade_date_idx < len(data.index):
                trade_date = data.index[trade_date_idx]
            else:
                continue  # Skip if no valid future date is found

        if row['Short'] == 'short' and not short_active:
            position_price = data.loc[trade_date, 'Close']
            shares_short = round(initial_capital / position_price, 2)
            shares_short = round_to_multiple(shares_short, share_rounding)
            entry_fee = position_price * shares_short * trade_fee
            short_trades.append({
                'Action': 'SHORT',
                'Date': trade_date,
                'Price': position_price,
                'Shares': shares_short,
                'PnL': -entry_fee  # Subtract entry fee only
            })
            short_active = True
        elif row['Short'] == 'cover' and short_active:
            cover_price = data.loc[trade_date, 'Close']
            pnl = shares_short * (position_price - cover_price)
            exit_fee = cover_price * shares_short * trade_fee
            pnl -= exit_fee  # Subtract exit fee only
            total_short_pnl += pnl
            short_trades.append({
                'Action': 'COVER',
                'Date': trade_date,
                'Price': cover_price,
                'Shares': shares_short,
                'PnL': pnl
            })
            short_active = False

    # Handle unmatched open short trade
    if short_active:
        last_price = data['Close'].iloc[-1]  # Use the last available close price
        pnl = shares_short * (position_price - last_price)  # Calculate PnL
        exit_fee = last_price * shares_short * trade_fee  # Calculate exit fee
        pnl -= exit_fee  # Subtract exit fee
        total_short_pnl += pnl
        short_trades.append({
            'Action': 'COVER',
            'Date': data.index[-1],  # Use the last available date
            'Price': last_price,
            'Shares': shares_short,
            'PnL': pnl
        })

    return short_trades, total_short_pnl

def calculate_trade_statistics(trades, equity_curve, initial_capital, trade_fee):
    """
    Calculate trade statistics from a list of trades and equity curve.

    Parameters:
    - trades: List of trades with PnLs.
    - equity_curve: Pandas Series representing the equity curve over time.
    - initial_capital: Starting capital for the strategy.
    - trade_fee: Percentage fee for each trade (e.g., 0.001 for 0.1%).

    Returns:
    - stats: Dictionary containing trade statistics.
    """
    total_trades = len(trades) // 2  # Each trade has a pair (entry and exit)
    winning_trades = sum(1 for trade in trades if trade['PnL'] > 0)
    losing_trades = total_trades - winning_trades
    total_pnl = sum(trade['PnL'] for trade in trades)  # Sum up PnL from all trades

    # Calculate total fees
    total_fees = sum(
        round(trade['Price'] * trade['Shares'] * trade_fee, 2)
        for trade in trades
    )

    win_percentage = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    loss_percentage = (losing_trades / total_trades) * 100 if total_trades > 0 else 0

    # Calculate Max Drawdown
    peak = equity_curve.cummax()
    drawdown = (peak - equity_curve) / peak
    max_drawdown = drawdown.max()

    stats = {
        "Total Trades": total_trades,
        "Winning Trades": winning_trades,
        "Losing Trades": losing_trades,
        "Win Percentage": win_percentage,
        "Loss Percentage": loss_percentage,
        "Total PnL": total_pnl,  # Correctly sum up PnL
        "Total Fees": total_fees,  # Include total fees
        "Final Capital": initial_capital + total_pnl,
        "Max Drawdown": max_drawdown * 100  # Convert to percentage
    }

    # Debugging: Print PnL and fees for each trade
    '''print("\nDebugging Trades PnL and Fees:")
    for trade in trades:
        fee = round(trade['Price'] * trade['Shares'] * trade_fee, 2)
        print(f"Action: {trade['Action']}, Date: {trade['Date']}, Price: {trade['Price']}, Shares: {trade['Shares']}, PnL: {trade['PnL']}, Fee: {fee}")

    # Debugging: Ensure Total PnL matches the sum of individual trade PnLs
    calculated_total_pnl = sum(trade['PnL'] for trade in trades)
    print(f"\nCalculated Total PnL: {calculated_total_pnl}")
    print(f"Total Fees: {total_fees}")
    assert calculated_total_pnl == total_pnl, "Mismatch in Total PnL!"
'''
    return stats

def calculate_equity_curve(df, trades, initial_capital, start_date, trade_fee):
    """
    Calculate the equity curve based on trades and close prices, including trade fees.

    Parameters:
    - df: DataFrame containing the price data (must include 'Close').
    - trades: List of trades with entry and exit dates.
    - initial_capital: Starting capital for the strategy.
    - start_date: The date from which to start calculating the equity curve.
    - trade_fee: Percentage fee for each trade (e.g., 0.001 for 0.1%).

    Returns:
    - equity_curve: Pandas Series representing the equity curve over time.
    """
    if not trades:
        return pd.Series(initial_capital, index=df.index)

    # Ensure the DataFrame is sorted by date
    df.sort_index(inplace=True)

    # Initialize the equity curve
    equity_curve = pd.Series(initial_capital, index=df.index, dtype=float)
    current_capital = initial_capital
    current_position = None
    shares = 0

    # Process each date in the DataFrame
    for i, date in enumerate(df.index):
        current_price = df.loc[date, "Close"]
        previous_price = df.loc[df.index[i - 1], "Close"] if i > 0 else current_price

        # Update equity based on the current position
        if current_position:
            if current_position["type"] == "Long":
                # Update equity for long position
                equity_curve.loc[date] = equity_curve.loc[df.index[i - 1]] + shares * (current_price - previous_price)
            elif current_position["type"] == "Short":
                # Update equity for short position
                equity_curve.loc[date] = equity_curve.loc[df.index[i - 1]] + shares * (previous_price - current_price)
        else:
            equity_curve.loc[date] = current_capital

        # Check if a trade occurs on this date
        for trade in trades:
            if trade["Date"] == date:
                if trade["Action"] in ["BUY", "SHORT"]:
                    # Open a position
                    shares = trade["Shares"]
                    trade_fee_cost = trade["Price"] * shares * trade_fee
                    current_capital -= trade_fee_cost  # Subtract entry fee immediately
                    equity_curve.loc[date] -= trade_fee_cost  # Subtract fee from equity curve
                    current_position = {
                        "entry_date": trade["Date"],
                        "entry_price": trade["Price"],
                        "type": "Long" if trade["Action"] == "BUY" else "Short",
                    }
                elif trade["Action"] in ["SELL", "COVER"] and current_position:
                    # Close the position
                    trade_fee_cost = trade["Price"] * shares * trade_fee
                    if current_position["type"] == "Long":
                        pnl = shares * (trade["Price"] - current_position["entry_price"])
                    elif current_position["type"] == "Short":
                        pnl = shares * (current_position["entry_price"] - trade["Price"])
                    current_capital += pnl - trade_fee_cost  # Add PnL and subtract exit fee
                    equity_curve.loc[date] = current_capital  # Update equity curve directly
                    current_position = None
                    shares = 0

    # Fill forward any missing values in the equity curve
    equity_curve.ffill(inplace=True)

    return equity_curve
 
def generate_equity_curve(trades, initial_capital):
    """
    Generate an equity curve from a list of trades.

    Parameters:
    - trades: List of trades with PnLs.
    - initial_capital: Starting capital for the strategy.

    Returns:
    - equity_curve: Pandas Series representing the equity curve over time.
    """
    equity = initial_capital
    equity_curve = {}

    for trade in trades:
        equity += trade['PnL']
        equity_curve[trade['Date']] = equity

    return pd.Series(equity_curve).sort_index()
def plot_candlesticks_with_jurik_plotly(data, jurik_column='Jurik_SMA_20'):
    """
    Plot candlestick chart with Jurik SMA using Plotly.

    Parameters:
    - data: DataFrame containing OHLC data and Jurik SMA.
    - jurik_column: Column name for the Jurik SMA.
    """
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02)

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Candlesticks",
            increasing_line_color='green',
            decreasing_line_color='red'
        ),
        row=1, col=1
    )

    # Add Jurik SMA
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[jurik_column],
            mode='lines',
            name='Jurik SMA (20)',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )

    # Update layout
    fig.update_layout(
        title="Candlestick Chart with Jurik SMA",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_dark"
    )

    # Open in browser
    fig.show()

def plot_equity_curves_plotly(long_equity_curve, short_equity_curve):
    """
    Plot equity curves for long and short trades using Plotly.

    Parameters:
    - long_equity_curve: Pandas Series representing the long equity curve.
    - short_equity_curve: Pandas Series representing the short equity curve.
    """
    fig = go.Figure()

    # Add long equity curve
    fig.add_trace(
        go.Scatter(
            x=long_equity_curve.index,
            y=long_equity_curve.values,
            mode='lines',
            name='Long Equity Curve',
            line=dict(color='blue', width=2)
        )
    )

    # Add short equity curve
    fig.add_trace(
        go.Scatter(
            x=short_equity_curve.index,
            y=short_equity_curve.values,
            mode='lines',
            name='Short Equity Curve',
            line=dict(color='red', width=2)
        )
    )

    # Update layout
    fig.update_layout(
        title="Equity Curves",
        xaxis_title="Date",
        yaxis_title="Equity",
        template="plotly_dark"
    )

    # Open in browser
    fig.show()


def plot_candlesticks_with_jurik(data, jurik_column='Jurik_SMA_20'):
    """
    Plot candlestick chart with Jurik SMA.

    Parameters:
    - data: DataFrame containing OHLC data and Jurik SMA.
    - jurik_column: Column name for the Jurik SMA.
    """
    # Prepare data for candlestick chart
    ohlc_data = data[['Open', 'High', 'Low', 'Close']].copy()
    ohlc_data['Date'] = data.index
    ohlc_data['Date'] = mdates.date2num(ohlc_data['Date'])

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    candlestick_ohlc(ax, ohlc_data[['Date', 'Open', 'High', 'Low', 'Close']].values, width=0.6, colorup='green', colordown='red')

    # Plot Jurik SMA
    ax.plot(data.index, data[jurik_column], label='Jurik SMA (20)', color='blue', linewidth=1.5)

    # Format the x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45)

    # Add labels, legend, and grid
    ax.set_title('Candlestick Chart with Jurik SMA')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid()

    plt.tight_layout()
#    plt.show()
    
def plot_equity_curves(long_equity_curve, short_equity_curve):
    """
    Plot equity curves for long and short trades.

    Parameters:
    - long_equity_curve: Pandas Series representing the long equity curve.
    - short_equity_curve: Pandas Series representing the short equity curve.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(long_equity_curve, label="Long Equity Curve", color="blue", linewidth=1.5)
    plt.plot(short_equity_curve, label="Short Equity Curve", color="red", linewidth=1.5)
    plt.title("Equity Curves")
    plt.xlabel("Date")
    plt.ylabel("Equity")
    plt.legend()
    plt.grid()
    plt.tight_layout()
#    plt.show()
#import plotly.io as pio
#pio.renderers.default = 'browser'

# Import necessary libraries
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_combined_charts(data, long_equity_curve, short_equity_curve, combined_df, long_trades, short_trades, stock_symbol, initial_capital):
    """
    Plot a single figure with two charts:
    1. Candlestick chart with markers.
    2. Equity curve chart with long, short, combined, and buy-and-hold equity curves.

    Parameters:
    - data: DataFrame containing OHLC data.
    - long_equity_curve: Pandas Series representing the long equity curve.
    - short_equity_curve: Pandas Series representing the short equity curve.
    - combined_df: DataFrame containing support and resistance levels.
    - long_trades: List of long trades.
    - short_trades: List of short trades.
    - stock_symbol: The stock symbol to include in the chart legend.
    - initial_capital: Starting capital for the strategy.
    """
    # Calculate combined equity curve
    combined_equity_curve = (long_equity_curve + short_equity_curve - initial_capital).ffill()

    # Calculate Buy and Hold equity curve
    buy_and_hold_equity_curve = data['Close'] / data['Close'].iloc[0] * initial_capital

    # Calculate percentage increase of combined equity
    final_equity = combined_equity_curve.iloc[-1]
    percent_increase = ((final_equity - initial_capital) / initial_capital) * 100

    # Create a subplot with 2 rows
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.6, 0.4],  # Allocate more space for the candlestick chart
        subplot_titles=(f"{stock_symbol} Candlestick Chart",
                        f"{stock_symbol} Equity Curves (Final Equity: {final_equity:.2f}, +{percent_increase:.2f}%)")
    )

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=f"{stock_symbol} Candlesticks",
            increasing_line_color='green',
            decreasing_line_color='red'
        ),
        row=1, col=1
    )
    # Add support markers below Low
    fig.add_trace(
        go.Scatter(
            x=combined_df.loc[combined_df['Type'] == 'support', 'Date'],
            y=data.loc[combined_df.loc[combined_df['Type'] == 'support', 'Date'], 'Low'] * 0.96,  # Offset below Low
            mode='markers',
            name='Support',
            marker=dict(color='green', size=10, symbol='triangle-up')
        ),
        row=1, col=1
    )
    # Add resistance markers above High
    fig.add_trace(
        go.Scatter(
            x=combined_df.loc[combined_df['Type'] == 'resistance', 'Date'],
            y=data.loc[combined_df.loc[combined_df['Type'] == 'resistance', 'Date'], 'High'] * 1.04,  # Offset above High
            mode='markers',
            name='Resistance',
            marker=dict(color='red', size=10, symbol='triangle-down')
        ),
        row=1, col=1
    )

    # Add markers for long trades
    fig.add_trace(
        go.Scatter(
            x=[trade['Date'] for trade in long_trades if trade['Action'] == 'BUY'],
            y=[data.loc[trade['Date'], 'High'] * 1.03 for trade in long_trades if trade['Action'] == 'BUY'],  # Offset above High
            mode='markers',
            name='Buy Long',
            marker=dict(color='green', size=10, symbol='circle')
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=[trade['Date'] for trade in long_trades if trade['Action'] == 'SELL'],
            y=[data.loc[trade['Date'], 'Low'] * 0.97 for trade in long_trades if trade['Action'] == 'SELL'],  # Offset below Low
            mode='markers',
            name='Sell Long',
            marker=dict(color='darkgreen', size=10, symbol='x')
        ),
        row=1, col=1
    )

    # Add markers for short trades
    fig.add_trace(
        go.Scatter(
            x=[trade['Date'] for trade in short_trades if trade['Action'] == 'SHORT'],
            y=[data.loc[trade['Date'], 'High'] * 1.02 for trade in short_trades if trade['Action'] == 'SHORT'],  # Offset above High
            mode='markers',
            name='Short',
            marker=dict(color='red', size=10, symbol='circle')
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=[trade['Date'] for trade in short_trades if trade['Action'] == 'COVER'],
            y=[data.loc[trade['Date'], 'Low'] * 0.98 for trade in short_trades if trade['Action'] == 'COVER'],  # Offset below Low
            mode='markers',
            name='Cover Short',
            marker=dict(color='darkred', size=10, symbol='x')
        ),
        row=1, col=1
    )

    # Add long equity curve
    fig.add_trace(
        go.Scatter(
            x=long_equity_curve.index,
            y=long_equity_curve.values,
            mode='lines',
            name=f"{stock_symbol} Long Equity Curve",
            line=dict(color='green', width=2)
        ),
        row=2, col=1
    )

    # Add short equity curve
    fig.add_trace(
        go.Scatter(
            x=short_equity_curve.index,
            y=short_equity_curve.values,
            mode='lines',
            name=f"{stock_symbol} Short Equity Curve",
            line=dict(color='red', width=2)
        ),
        row=2, col=1
    )

    # Add combined equity curve
    fig.add_trace(
        go.Scatter(
            x=combined_equity_curve.index,
            y=combined_equity_curve.values,
            mode='lines',
            name=f"{stock_symbol} Combined Equity Curve",
            line=dict(color='purple', width=2, dash='dot')
        ),
        row=2, col=1
    )

    # Add Buy and Hold equity curve
    fig.add_trace(
        go.Scatter(
            x=buy_and_hold_equity_curve.index,
            y=buy_and_hold_equity_curve.values,
            mode='lines',
            name=f"{stock_symbol} Buy and Hold Equity Curve",
            line=dict(color='orange', width=2, dash='dash')
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        title=f"{stock_symbol} Candlestick Chart and Equity Curves",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis2_title="Date",
        yaxis2_title="Equity",
        template="plotly_white",
        height=1000,  # Adjust the height of the figure
        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider=dict(visible=True, thickness=0.05)
    )

    # Open in browser
    fig.show()
from tabulate import tabulate

def backtest_strategy(data, past_window, trade_window, initial_capital, trade_fee):
    """
    Backtest the strategy with given past_window and trade_window.

    Parameters:
    - data: DataFrame containing the price data.
    - past_window: Number of days to look into the past for extrema.
    - trade_window: Number of days to look into the future for extrema.
    - initial_capital: Starting capital for the strategy.

    Returns:
    - metrics: Dictionary containing performance metrics (e.g., total PnL, win percentage).
    """
    # Identify support and resistance levels
    support, resistance = identify_support_resistance(data, past_window, trade_window)

    # Combine support and resistance into a single DataFrame
    combined_df = assign_signals(support, resistance, data, trade_window,interval)
    print(combined_df)
    # Translate combined_df into long and short trades
    long_trades, total_long_pnl = translate_long_trades(combined_df, data, initial_capital, trade_fee)
    short_trades, total_short_pnl = translate_short_trades(combined_df, data, initial_capital, trade_fee)

    # Print results
#    print("\nLong Trades:")
#    for trade in long_trades:
#        print(trade)

#    print("\nShort Trades:")
#    for trade in short_trades:
#       print(trade)

 #   print(f"\nTotal Long PnL: {total_long_pnl}")
 #   print(f"Total Short PnL: {total_short_pnl}")

    # Validate dates in combined_df
#    valid_long_dates = combined_df['Long Date'].isin(data.index)
#    valid_short_dates = combined_df['Short Date'].isin(data.index)

#    if not valid_long_dates.all():
#        print("Invalid Long Dates:")
 #       print(combined_df.loc[~valid_long_dates, ['Long Date']])

 #   if not valid_short_dates.all():
 #       print("Invalid Short Dates:")
 #       print(combined_df.loc[~valid_short_dates, ['Short Date']])

    # Calculate equity curves
    long_equity_curve = calculate_equity_curve(data, long_trades, initial_capital, data.index[0], trade_fee)
    short_equity_curve = calculate_equity_curve(data, short_trades, initial_capital, data.index[0], trade_fee)

    # Calculate trade statistics
    long_stats = calculate_trade_statistics(long_trades, long_equity_curve, initial_capital, trade_fee)
    short_stats = calculate_trade_statistics(short_trades, short_equity_curve, initial_capital, trade_fee)

    # Combine metrics
    metrics = {
        "past_window": past_window,
        "trade_window": trade_window,
        "total_pnl": total_long_pnl + total_short_pnl,
        "long_win_percentage": long_stats["Win Percentage"],
        "short_win_percentage": short_stats["Win Percentage"],
        "total_trades": long_stats["Total Trades"] + short_stats["Total Trades"],
        "max_drawdown": max(long_stats["Max Drawdown"], short_stats["Max Drawdown"]),
    }

    return metrics

def optimize_strategy(data, past_window_range, trade_window_range, initial_capital, trade_fee):
    """
    Optimize the strategy by testing different past_window and trade_window values.

    Parameters:
    - data: DataFrame containing the price data.
    - past_window_range: Range of values for past_window (e.g., range(5, 15)).
    - trade_window_range: Range of values for trade_window (e.g., range(1, 5)).
    - initial_capital: Starting capital for the strategy.

    Returns:
        - best_metrics: Dictionary containing the best-performing parameters and metrics.
    - all_metrics: List of all metrics for each combination.
    """
    all_metrics = []

    # Iterate over all combinations of past_window and trade_window
    for past_window in past_window_range:
        for trade_window in trade_window_range:
            metrics = backtest_strategy(data, past_window, trade_window, initial_capital, trade_fee)
            all_metrics.append(metrics)

    # Find the best-performing combination (e.g., highest total PnL)
    best_metrics = max(all_metrics, key=lambda x: x["total_pnl"])

    return best_metrics, all_metrics
from twelvedata import TDClient

def fetch_twelve_data(symbol, interval, api_key, outputsize):
    """
    Fetch data using Twelve Data API.

    Parameters:
    - symbol: The symbol to fetch data for (e.g., "BTC/USD" or "AAPL").
    - interval: The interval for the data (e.g., "5min").
    - api_key: Your Twelve Data API key.
    - outputsize: Number of data points to fetch (e.g., 500, 1000, etc.).

    Returns:
    - data: A pandas DataFrame containing the fetched data.
    """

    try:
        td = TDClient(apikey=api_key)
        ts = td.time_series(symbol=symbol, interval=interval, outputsize=outputsize)
        data = ts.as_pandas()
        return data
    except Exception as e:
        print(f"Error fetching data from Twelve Data: {e}")
        return None
    

from alpha_vantage.timeseries import TimeSeries
def get_stock_data(stock_source, symbol, interval, api_key=None, outputsize=500, period=None):
    """
    Fetch stock data from Yahoo Finance, Twelve Data API, or Alpha Vantage based on the stock_source parameter.

    Parameters:
    - stock_source: 0 for Yahoo Finance, 1 for Twelve Data API, 2 for Alpha Vantage intraday, 4 for Alpha Vantage daily.
    - symbol: The stock symbol to fetch data for (e.g., "BTC/USD" or "AAPL").
    - interval: The interval for the data (e.g., "5min", "1h", "1d").
    - api_key: Your API key (required for Twelve Data API and Alpha Vantage).
    - outputsize: Number of data points to fetch (used for Twelve Data API and Alpha Vantage).
    - period: Time period for Yahoo Finance data (e.g., "1y").

    Returns:
    - data: A pandas DataFrame containing the fetched data with standardized column names.
    """
    if stock_source == 0:
        # Fetch data from Yahoo Finance
        print("Fetching data from Yahoo Finance...")
        try:
            # Convert period to days
            if period.endswith("y"):  # Years
                period_in_days = int(period[:-1]) * 365
            elif period.endswith("d"):  # Days
                period_in_days = int(period[:-1])
            else:
                raise ValueError(f"Unsupported period format: {period}")

            print(f"Period in days: {period_in_days}")

            # Define start and end dates for historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_in_days)

            # Download data using yfinance
            data = yf.download(symbol, start=start_date, end=end_date, interval=interval, auto_adjust=False)

            # Ensure the index is in datetime format
            if not data.empty:
                data.index = pd.to_datetime(data.index)

                # Remove timezone information
                data.index = data.index.tz_localize(None)

                # Flatten multi-level column names if they exist
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = ['_'.join(col).strip() for col in data.columns.values]

                data.columns = [col.rsplit('_', 1)[0] if '_' in col else col for col in data.columns]

                print("Data fetched successfully from Yahoo Finance:")
                print(data.head())
                return data
            else:
                print("Error: No data fetched from Yahoo Finance.")
                return None
        except Exception as e:
            print(f"Error fetching data from Yahoo Finance: {e}")
            return None 

        #print(data)

    elif stock_source == 1:
        if interval == "1d":
            interval = "1day"
        # Fetch data from Twelve Data API
        print("Fetching data from Twelve Data API...")
        try:
            td = TDClient(apikey='e13303cc06754b8ea998da6c07d7ee2c')
            ts = td.time_series(symbol=symbol, interval=interval, outputsize=outputsize)
            data = ts.as_pandas()
            if data.empty:
                print("Error: No data fetched from Twelve Data API.")
                return None
            # Standardize column names
            data.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)
            data.index.name = 'Date'
            return data
        except Exception as e:
            print(f"Error fetching data from Twelve Data API: {e}")
            return None

    elif stock_source == 2:
        # Fetch data from Alpha Vantage (intraday)
        print("Fetching intraday data from Alpha Vantage...")
        try:
            ts = TimeSeries(key='T5TOU0D1VD5O981I', output_format='pandas')
            if interval in ["1min", "5min", "15min", "30min", "60min"]:
                data, meta_data = ts.get_intraday(symbol=symbol, interval=interval, outputsize="full" if outputsize > 100 else "compact")
            else:
                print("Error: Unsupported interval for Alpha Vantage intraday.")
                return None

            if data.empty:
                print("Error: No data fetched from Alpha Vantage.")
                return None
            # Standardize column names
            data.rename(columns={
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. volume': 'Volume'
            }, inplace=True)
            data.index.name = 'Date'
            return data
        except Exception as e:
            print(f"Error fetching data from Alpha Vantage: {e}")
            return None

    elif stock_source == 3:
        # Fetch daily data from Alpha Vantage
        print("Fetching daily data from Alpha Vantage...")
        try:
            ts = TimeSeries(key='T5TOU0D1VD5O981I', output_format='pandas')
            data, meta_data = ts.get_daily(symbol=symbol, outputsize="full" if outputsize > 100 else "compact")
            if data.empty:
                print("Error: No data fetched from Alpha Vantage.")
                return None
            # Standardize column names
            data.rename(columns={
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. volume': 'Volume'
            }, inplace=True)
            data.index.name = 'Date'
            return data
        except Exception as e:
            print(f"Error fetching daily data from Alpha Vantage: {e}")
            return None

    else:
        print("Error: Invalid stock_source value. Use 0 for Yahoo Finance, 1 for Twelve Data API, 2 for Alpha Vantage intraday, or 4 for Alpha Vantage daily.")
        return None

from tabulate import tabulate

def run_full_backtest_and_plot(data, ticker, past_window, trade_window, initial_capital, trade_fee, interval):
    # 1. Signale und Trades
    support, resistance = identify_support_resistance(data, past_window, trade_window)
    combined_df = assign_signals(support, resistance, data, trade_window, interval)
    long_trades, total_long_pnl = translate_long_trades(combined_df, data, initial_capital, trade_fee)
    short_trades, total_short_pnl = translate_short_trades(combined_df, data, initial_capital, trade_fee)
    long_equity_curve = calculate_equity_curve(data, long_trades, initial_capital, data.index[0], trade_fee)
    short_equity_curve = calculate_equity_curve(data, short_trades, initial_capital, data.index[0], trade_fee)
    # 2. Trade-Listen speichern
    pd.DataFrame(long_trades).to_csv(f"{ticker}_long_trades.csv", index=False)
    pd.DataFrame(short_trades).to_csv(f"{ticker}_short_trades.csv", index=False)
    # 2b. Trade-Listen als Tabelle im DOS-Fenster ausgeben
    print(f"\nLong Trades für {ticker}:")
    if long_trades:
        print(tabulate(long_trades, headers="keys", tablefmt="psql"))
    else:
        print("Keine Long Trades.")
    print(f"\nShort Trades für {ticker}:")
    if short_trades:
        print(tabulate(short_trades, headers="keys", tablefmt="psql"))
    else:
        print("Keine Short Trades.")
    # 3. Trade-Statistiken ausgeben
    long_stats = calculate_trade_statistics(long_trades, long_equity_curve, initial_capital, trade_fee)
    short_stats = calculate_trade_statistics(short_trades, short_equity_curve, initial_capital, trade_fee)
    print(f"\nTrade-Statistiken für {ticker}:")
    print(tabulate([
        ["Long", long_stats["Total Trades"], long_stats["Win Percentage"], long_stats["Total PnL"], long_stats["Max Drawdown"]],
        ["Short", short_stats["Total Trades"], short_stats["Win Percentage"], short_stats["Total PnL"], short_stats["Max Drawdown"]],
    ], headers=["Typ", "Trades", "Win %", "Total PnL", "Max Drawdown %"], tablefmt="psql"))
    # 4. Chart erzeugen
    plot_combined_charts(data, long_equity_curve, short_equity_curve, combined_df, long_trades, short_trades, ticker, initial_capital)

# Main execution

# Main execution
if __name__ == "__main__":
    # Liste der Ticker-Dateien
    trade_period = 12  # Zeitraum in Monaten (z.B. 12 = 1 Jahr, 60 = 5 Jahre)    
    csv_dir = r"C:\Users\Edgar.000\Documents\____Trading strategies"
    csv_files = [
        "ADA-EUR_5y.csv",
        "DOGE-EUR_5y.csv",
        "ETH-EUR_5y.csv",
        "LINK-EUR_5y.csv",
        "SOL-EUR_5y.csv",
        "XRP-EUR_5y.csv",
        "BTC-EUR_5y.csv"
        #"adausdt_bitget.csv",
        #"btcusdt_bitget.csv",
        #"ethusdt_bitget.csv",
        #"linkusdt_bitget.csv",
        #"solusdt_bitget.csv",
        #"xrpusdt_bitget.csv"
    ]

    optimize = 1  # 1 = Optimierung/Backtesting, 0 = Nur mit optimalen Parametern laufen

    past_window_range = range(5, 15)
    trade_window_range = range(1, 5)
    initial_capital = 1500
    trade_fee = 0.0025
    interval = "1d"
    optimal_params = {}

    for csv_file in csv_files:
        ticker = csv_file.replace(".csv", "")
        file_path = os.path.join(csv_dir, csv_file)
        print(f"\n--- {ticker} ---")
        try:
            data = pd.read_csv(
                file_path,
                index_col=0,
                parse_dates=True,
                na_values=["null", "NaN", ""]
            )
            data.index = pd.to_datetime(data.index, errors='coerce')
            data = data[~data.index.isna()]
            for col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            if 'close' in data.columns:
                data.rename(columns={'close': 'Close', 'open': 'Open', 'high': 'High', 'low': 'Low', 'volume': 'Volume'}, inplace=True)
            # Zeitraum filtern:
            if trade_period > 0:
                start_date = data.index.max() - pd.DateOffset(months=trade_period)
                data = data[data.index >= start_date]
            print(f"{ticker} Spalten: {data.columns}")
            print(data.head())
            if data.empty or 'Close' not in data.columns:
                print(f"Keine gültigen Daten für {ticker}!")
                continue

            if optimize:
                best_pnl = -np.inf
                best_params = (None, None)
                for past_window in past_window_range:
                    for trade_window in trade_window_range:
                        try:
                            support, resistance = identify_support_resistance(data, past_window, trade_window)
                            combined_df = assign_signals(support, resistance, data, trade_window, interval)
                            long_trades, total_long_pnl = translate_long_trades(combined_df, data, initial_capital, trade_fee)
                            short_trades, total_short_pnl = translate_short_trades(combined_df, data, initial_capital, trade_fee)
                            total_pnl = total_long_pnl + total_short_pnl
                                        # Schrittweise Ergebnisse anzeigen:
                            print(f"Ticker: {ticker} | past_window: {past_window} | trade_window: {trade_window} | PnL: {total_pnl:.2f}")
                            if total_pnl > best_pnl:
                                best_pnl = total_pnl
                                best_params = (past_window, trade_window)
                        except Exception as e:
                            print(f"Fehler bei Parametern past_window={past_window}, trade_window={trade_window}: {e}")
                if best_params[0] is None or best_params[1] is None:
                    print(f"Keine gültigen Parameter für {ticker} gefunden!")
                    continue
                print(f"Optimale Parameter für {ticker}: past_window={best_params[0]}, trade_window={best_params[1]}, PnL={best_pnl:.2f}")
                optimal_params[ticker] = {"past_window": best_params[0], "trade_window": best_params[1]}
                run_full_backtest_and_plot(
                    data, ticker, best_params[0], best_params[1], initial_capital, trade_fee, interval
                )
                long_equity_curve = calculate_equity_curve(data, long_trades, initial_capital, data.index[0], trade_fee)
                short_equity_curve = calculate_equity_curve(data, short_trades, initial_capital, data.index[0], trade_fee)
                long_stats = calculate_trade_statistics(long_trades, long_equity_curve, initial_capital, trade_fee)
                short_stats = calculate_trade_statistics(short_trades, short_equity_curve, initial_capital, trade_fee)
                print(f"Ticker: {ticker} | past_window: {past_window} | trade_window: {trade_window} | PnL: {total_pnl:.2f} | Long Win%: {long_stats['Win Percentage']:.1f} | Short Win%: {short_stats['Win Percentage']:.1f}")
            else:
                # Ohne Optimierung: Nutze Standardwerte
                run_full_backtest_and_plot(
                    data, ticker, past_window, trade_window, initial_capital, trade_fee, interval
                )
        except Exception as e:
            print(f"Fehler bei {ticker}: {e}")