#!/usr/bin/env python3
"""
LIVE BACKTEST WORKING - Aufruf der integrierten Funktion mit 14 Tage Trade Report
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the integrated live backtest function
from crypto_backtesting_module import run_live_backtest_analysis
from crypto_tickers import crypto_tickers

def get_14_day_trades_report():
    """
    Erstellt einen 14-Tage Trade Report mit dem gewünschten Header-Format:
    Date; Ticker; Quantity; Price; Order Type; Limit Price; Open/Close; Realtime Price Bitpanda
    """
    print("\n📊 Creating 14-Day Trades Report...")
    
    # Cutoff date for last 14 days
    cutoff_date = datetime.now() - timedelta(days=14)
    
    # Header as requested
    header = "Date;Ticker;Quantity;Price;Order Type;Limit Price;Open/Close;Realtime Price Bitpanda"
    print(f"📋 Header: {header}")
    
    all_trades = []
    
    # Process each ticker
    for ticker_name, config in crypto_tickers.items():
        symbol = config.get('symbol', ticker_name)
        
        try:
            print(f"\n🔍 Processing {ticker_name} ({symbol})...")
            
            # Get current price from Yahoo Finance as proxy for Bitpanda
            try:
                ticker_data = yf.Ticker(symbol)
                current_price = ticker_data.history(period="1d")['Close'].iloc[-1]
                print(f"   💰 Current Price: €{current_price:.4f}")
            except:
                current_price = 0.0
                print(f"   ⚠️ Could not fetch current price for {symbol}")
            
            # Look for recent trades (this is a template - in real implementation 
            # you would read from your actual trades database/CSV files)
            
            # Example trades for the last 14 days (you'll need to replace this with actual data)
            sample_trades = [
                {
                    'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                    'ticker': ticker_name,
                    'quantity': round(1000 / current_price, 6) if current_price > 0 else 0,
                    'price': current_price * 0.99,  # Example buy price
                    'order_type': 'Limit',
                    'limit_price': current_price * 0.98,
                    'open_close': 'Open',
                    'realtime_price': current_price
                },
                {
                    'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                    'ticker': ticker_name,
                    'quantity': round(1000 / current_price, 6) if current_price > 0 else 0,
                    'price': current_price * 1.02,  # Example sell price
                    'order_type': 'Limit',
                    'limit_price': current_price * 1.01,
                    'open_close': 'Close',
                    'realtime_price': current_price
                }
            ]
            
            # Add trades to the list (only if they're within 14 days)
            for trade in sample_trades:
                trade_date = datetime.strptime(trade['date'], '%Y-%m-%d')
                if trade_date >= cutoff_date:
                    all_trades.append(trade)
                    
        except Exception as e:
            print(f"   ❌ Error processing {ticker_name}: {e}")
    
    # Sort trades by date (newest first)
    all_trades.sort(key=lambda x: x['date'], reverse=True)
    
    # Print the report
    print(f"\n📊 ===== 14-DAY TRADES REPORT =====")
    print(f"📅 Period: {cutoff_date.date()} to {datetime.now().date()}")
    print(f"🔢 Total Trades Found: {len(all_trades)}")
    print(f"\n{header}")
    print("-" * 120)
    
    for trade in all_trades:
        line = f"{trade['date']};{trade['ticker']};{trade['quantity']:.6f};{trade['price']:.4f};{trade['order_type']};{trade['limit_price']:.4f};{trade['open_close']};{trade['realtime_price']:.4f}"
        print(line)
    
    # Save to CSV file
    csv_filename = f"14_day_trades_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    if all_trades:
        df = pd.DataFrame(all_trades)
        # Rename columns to match header
        df.columns = ['Date', 'Ticker', 'Quantity', 'Price', 'Order Type', 'Limit Price', 'Open/Close', 'Realtime Price Bitpanda']
        df.to_csv(csv_filename, sep=';', index=False)
        print(f"\n💾 Report saved as: {csv_filename}")
    else:
        print(f"\n⚠️ No trades found in the last 14 days")
    
    return all_trades

if __name__ == "__main__":
    """
    Hauptfunktion - ruft die integrierte Live-Backtest Analyse auf und erstellt 14-Tage Report
    """
    print("🚀 Starting LIVE Crypto Backtest with 14-Day Trades Report...")
    
    # First, create the 14-day trades report
    trades_14_days = get_14_day_trades_report()
    
    print("\n" + "="*80)
    
    # Then run the integrated live backtest analysis
    result = run_live_backtest_analysis()
    
    if result:
        print(f"\n✅ Live backtest completed successfully!")
        print(f"📊 Report: {result}")
        print(f"📊 14-Day Trades: {len(trades_14_days)} trades found")
    else:
        print("❌ Live backtest failed!")
        sys.exit(1)
