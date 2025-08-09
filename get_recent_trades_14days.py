"""
Recent Trades Extractor - Last 14 Days
Extracts all trades with the requested format:
Header: Date; Ticker; Quantity; Price; Order_Type=LIMIT; Limit_Price=0; Open_Close; Realtime_Price_Bitpanda
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from crypto_tickers import crypto_tickers
from config import COMMISSION_RATE, MIN_COMMISSION, ORDER_ROUND_FACTOR
from signal_utils import (
    calculate_support_resistance,
    assign_long_signals_extended,
    update_level_close_long,
    simulate_trades_compound_extended,
    berechne_best_p_tw_long
)
import yfinance as yf

def get_realtime_bitpanda_price(symbol):
    """Get current real-time price (using yfinance as proxy for Bitpanda)"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="1m")
        if not hist.empty:
            return round(hist['Close'].iloc[-1], 6)
        return 0.0
    except Exception as e:
        print(f"❌ Error getting real-time price for {symbol}: {e}")
        return 0.0

def load_crypto_data_yf(symbol, days=365):
    """Load crypto data from Yahoo Finance"""
    try:
        df = yf.download(symbol, period=f"{days}d", interval="1d", auto_adjust=True, progress=False)
        if df is None or df.empty:
            return None
        
        # Fix MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Standardize column names
        df.columns = [str(col).strip().capitalize() for col in df.columns]
        return df
    except Exception as e:
        print(f"❌ Error loading {symbol}: {e}")
        return None

def get_recent_trades_for_ticker(symbol, config, days_back=14):
    """Get recent trades for a single ticker"""
    try:
        print(f"\n📊 Processing {symbol}...")
        
        # Load data
        df = load_crypto_data_yf(symbol, days=90)  # Load 90 days to have enough data for analysis
        if df is None or df.empty:
            print(f"❌ No data for {symbol}")
            return pd.DataFrame()
        
        # Get configuration
        initial_capital = config.get('initialCapitalLong', 10000)
        trade_on = config.get('trade_on', 'Close')
        order_round_factor = config.get('order_round_factor', 0.01)
        commission_rate = COMMISSION_RATE
        
        # Use simple parameters for quick analysis (avoid optimization for speed)
        past_window = 10
        trade_window = 1
        
        # Calculate support/resistance
        supp, res = calculate_support_resistance(df, past_window, trade_window, verbose=False, ticker=symbol)
        
        # Generate extended signals
        ext_signals = assign_long_signals_extended(supp, res, df, trade_window, "1d", trade_on)
        if ext_signals is None or ext_signals.empty:
            print(f"⚠️ No signals for {symbol}")
            return pd.DataFrame()
        
        ext_signals = update_level_close_long(ext_signals, df, trade_on)
        
        # Simulate trades
        equity_curve, matched_trades = simulate_trades_compound_extended(
            ext_signals, df, config,
            starting_capital=initial_capital,
            commission_rate=commission_rate,
            min_commission=MIN_COMMISSION,
            round_factor=order_round_factor
        )
        
        if matched_trades is None or (hasattr(matched_trades, 'empty') and matched_trades.empty):
            print(f"⚠️ No trades for {symbol}")
            return pd.DataFrame()
        
        # Convert to DataFrame if needed
        if not isinstance(matched_trades, pd.DataFrame):
            # Convert list to DataFrame
            trades_df = pd.DataFrame(matched_trades)
        else:
            trades_df = matched_trades.copy()
        
        # Filter for last 14 days
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Ensure date columns are datetime
        if 'Entry Date' in trades_df.columns:
            trades_df['Entry Date'] = pd.to_datetime(trades_df['Entry Date'])
            recent_trades = trades_df[trades_df['Entry Date'] >= cutoff_date].copy()
        elif 'buy_date' in trades_df.columns:
            trades_df['buy_date'] = pd.to_datetime(trades_df['buy_date'])
            recent_trades = trades_df[trades_df['buy_date'] >= cutoff_date].copy()
        else:
            print(f"⚠️ No date column found for {symbol}")
            return pd.DataFrame()
        
        # Add ticker column
        recent_trades['Ticker'] = symbol
        
        print(f"✅ Found {len(recent_trades)} recent trades for {symbol}")
        return recent_trades
        
    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")
        return pd.DataFrame()

def display_recent_trades_summary(all_trades_df):
    """Display a nice summary of all recent trades"""
    if all_trades_df.empty:
        print("❌ No recent trades found for any ticker")
        return
    
    print(f"\n{'='*100}")
    print(f"📊 RECENT TRADES SUMMARY - LAST 14 DAYS")
    print(f"{'='*100}")
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 Total Recent Trades: {len(all_trades_df)}")
    
    # Group by ticker
    ticker_summary = all_trades_df.groupby('Ticker').agg({
        'PnL': ['count', 'sum', 'mean'],
        'Net PnL': 'sum' if 'Net PnL' in all_trades_df.columns else 'PnL',
        'Commission': 'sum' if 'Commission' in all_trades_df.columns else 'total_fees'
    }).round(3)
    
    print(f"\n📊 SUMMARY BY TICKER:")
    print(f"{'-'*80}")
    for ticker in all_trades_df['Ticker'].unique():
        ticker_trades = all_trades_df[all_trades_df['Ticker'] == ticker]
        count = len(ticker_trades)
        total_pnl = ticker_trades['Net PnL'].sum() if 'Net PnL' in ticker_trades.columns else ticker_trades['PnL'].sum()
        total_fees = ticker_trades['Commission'].sum() if 'Commission' in ticker_trades.columns else ticker_trades['total_fees'].sum()
        
        print(f"{ticker:10} | Trades: {count:2} | Net PnL: {total_pnl:8.2f}€ | Fees: {total_fees:6.2f}€")
    
    print(f"\n📋 DETAILED TRADES LIST:")
    print(f"{'-'*100}")
    
    # Prepare display DataFrame
    display_df = all_trades_df.copy()
    
    # Select key columns for display
    key_columns = ['Ticker']
    
    # Add date columns
    if 'Entry Date' in display_df.columns:
        key_columns.append('Entry Date')
        display_df['Entry Date'] = pd.to_datetime(display_df['Entry Date']).dt.strftime('%Y-%m-%d')
    if 'Exit Date' in display_df.columns:
        key_columns.append('Exit Date')
        display_df['Exit Date'] = pd.to_datetime(display_df['Exit Date']).dt.strftime('%Y-%m-%d')
    
    # Add price and quantity columns
    price_cols = ['Entry Price', 'Exit Price', 'Quantity']
    for col in price_cols:
        if col in display_df.columns:
            key_columns.append(col)
    
    # Add PnL columns
    pnl_cols = ['PnL', 'Net PnL', 'Commission']
    for col in pnl_cols:
        if col in display_df.columns:
            key_columns.append(col)
    
    # Display the table
    if key_columns:
        display_subset = display_df[key_columns]
        print(display_subset.to_string(index=False, max_rows=None, float_format='{:.4f}'.format))
    else:
        print(display_df.to_string(index=False, max_rows=None))

def save_recent_trades_to_csv(all_trades_df):
    """Save recent trades to CSV file"""
    if all_trades_df.empty:
        print("❌ No trades to save")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"recent_trades_14days_{timestamp}.csv"
    
    try:
        all_trades_df.to_csv(filename, index=False)
        print(f"✅ Recent trades saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")
        return None

def format_trades_with_requested_headers(all_trades_df):
    """
    Format trades according to requested header:
    Date; Ticker; Quantity; Price; Order_Type=LIMIT; Limit_Price=0; Open_Close; Realtime_Price_Bitpanda
    """
    if all_trades_df.empty:
        return pd.DataFrame()
    
    formatted_trades = []
    
    for _, trade in all_trades_df.iterrows():
        # Get real-time price
        realtime_price = get_realtime_bitpanda_price(trade['Ticker'])
        
        # Handle different column names from the simulation
        entry_date = trade.get('Entry Date', trade.get('buy_date', datetime.now()))
        exit_date = trade.get('Exit Date', trade.get('sell_date', None))
        entry_price = trade.get('Entry Price', trade.get('buy_price', 0))
        exit_price = trade.get('Exit Price', trade.get('sell_price', 0))
        quantity = trade.get('Quantity', trade.get('shares', 0))
        
        # Ensure date is string format
        if pd.notna(entry_date):
            if isinstance(entry_date, str):
                entry_date_str = entry_date[:10]  # YYYY-MM-DD
            else:
                entry_date_str = entry_date.strftime('%Y-%m-%d')
        else:
            entry_date_str = datetime.now().strftime('%Y-%m-%d')
        
        # BUY trade (OPEN position)
        formatted_trades.append({
            'Date': entry_date_str,
            'Ticker': trade['Ticker'],
            'Quantity': round(quantity, 6),
            'Price': round(entry_price, 6),
            'Order_Type': 'LIMIT',
            'Limit_Price': 0,  # 0 for market orders as requested
            'Open_Close': 'OPEN',
            'Realtime_Price_Bitpanda': realtime_price
        })
        
        # SELL trade (CLOSE position) - only if exit exists
        if pd.notna(exit_date) and exit_price > 0:
            if isinstance(exit_date, str):
                exit_date_str = exit_date[:10]  # YYYY-MM-DD
            else:
                exit_date_str = exit_date.strftime('%Y-%m-%d')
            
            formatted_trades.append({
                'Date': exit_date_str,
                'Ticker': trade['Ticker'],
                'Quantity': round(quantity, 6),
                'Price': round(exit_price, 6),
                'Order_Type': 'LIMIT',
                'Limit_Price': 0,  # 0 for market orders as requested  
                'Open_Close': 'CLOSE',
                'Realtime_Price_Bitpanda': realtime_price
            })
    
    formatted_df = pd.DataFrame(formatted_trades)
    
    # Sort by date
    if not formatted_df.empty:
        formatted_df = formatted_df.sort_values('Date', ascending=False)
    
    return formatted_df

def main():
    """Main function to get recent trades for all tickers with requested format"""
    print("🚀 EXTRACTING RECENT TRADES (LAST 14 DAYS)")
    print("📋 Header Format: Date; Ticker; Quantity; Price; Order_Type=LIMIT; Limit_Price=0; Open_Close; Realtime_Price_Bitpanda")
    print(f"{'='*100}")
    
    all_recent_trades = []
    
    # Process each ticker
    for ticker, config in crypto_tickers.items():
        try:
            recent_trades = get_recent_trades_for_ticker(ticker, config, days_back=14)
            if not recent_trades.empty:
                all_recent_trades.append(recent_trades)
        except Exception as e:
            print(f"❌ Error with {ticker}: {e}")
            continue
    
    # Combine all trades
    if all_recent_trades:
        combined_trades_df = pd.concat(all_recent_trades, ignore_index=True)
        
        # Format with requested headers
        formatted_trades_df = format_trades_with_requested_headers(combined_trades_df)
        
        if not formatted_trades_df.empty:
            print(f"\n📊 FORMATTED TRADES WITH REQUESTED HEADERS")
            print(f"{'='*120}")
            print(formatted_trades_df.to_string(index=False))
            
            # Save to CSV with requested format
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"Recent_Trades_14days_Formatted_{timestamp}.csv"
            
            try:
                formatted_trades_df.to_csv(filename, index=False, sep=';')  # Use semicolon as requested
                print(f"\n✅ FORMATTED TRADES SAVED: {filename}")
                print(f"📊 Total trade entries: {len(formatted_trades_df)}")
                print(f"📈 Unique tickers: {formatted_trades_df['Ticker'].nunique()}")
                
                # Show summary by ticker
                print(f"\n� SUMMARY BY TICKER:")
                summary = formatted_trades_df.groupby('Ticker').agg({
                    'Quantity': 'sum',
                    'Date': 'count'
                }).rename(columns={'Date': 'Trade_Entries'})
                print(summary.to_string())
                
                return filename
                
            except Exception as e:
                print(f"❌ Error saving CSV: {e}")
                return None
        else:
            print("❌ No trades found after formatting")
            return None
    else:
        print("❌ No recent trades found for any ticker")
        return None

if __name__ == "__main__":
    main()
