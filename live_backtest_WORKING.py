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
    Erstellt einen HEUTE-ONLY Trade Report mit dem gewünschten Header-Format:
    Date; Ticker; Quantity; Price; Order Type; Limit Price; Open/Close; Realtime Price Bitpanda
    
    🎯 MODIFIED: Only outputs trades for TODAY (2025-08-10) - NO historical orders!
    """
    print("\n📊 Creating TODAY-ONLY Trades Report...")
    print("🎯 FILTERING: Only orders for TODAY will be transmitted")
    print("⛔ BLOCKED: All historical orders from 2024 are ignored")
    
    # TODAY ONLY - no historical orders
    today_date = datetime.now().date()
    today_str = today_date.strftime('%Y-%m-%d')
    print(f"📅 Target Date: {today_str} (TODAY ONLY!)")
    
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
            
            # 🎯 GET REAL TRADES FOR TODAY ONLY - FROM ACTUAL BACKTEST RESULTS
            # ⛔ All 2024 orders are blocked and will NOT be transmitted
            
            try:
                # Run backtest to get real trades for today
                from crypto_backtesting_module import run_backtest
                
                if ticker_name in crypto_tickers:
                    config = crypto_tickers[ticker_name]
                    backtest_result = run_backtest(ticker_name, config)
                    
                    if backtest_result and 'matched_trades' in backtest_result:
                        matched_trades = backtest_result['matched_trades']
                        
                        if not matched_trades.empty:
                            # Convert Date column and filter for TODAY only
                            matched_trades['Date'] = pd.to_datetime(matched_trades['Date'])
                            today_mask = matched_trades['Date'].dt.date == today_date
                            today_real_trades = matched_trades[today_mask]
                            
                            if not today_real_trades.empty:
                                print(f"   📊 Found {len(today_real_trades)} real trades for TODAY")
                                
                                # 🎯 TAKE THE 14 NEWEST TRADES (not oldest!)
                                # Sort by Date descending (newest first) and take first 14
                                newest_trades = today_real_trades.sort_values('Date', ascending=False).head(14)
                                
                                print(f"   📅 Taking {len(newest_trades)} NEWEST trades from TODAY")
                                
                                # Convert to the required format
                                for _, trade_row in newest_trades.iterrows():
                                    trade_dict = {
                                        'date': today_str,  # TODAY ONLY!
                                        'ticker': ticker_name,
                                        'quantity': abs(trade_row.get('Quantity', 0)),
                                        'price': trade_row.get('Price', current_price),
                                        'order_type': 'Limit',
                                        'limit_price': trade_row.get('Price', current_price),
                                        'open_close': trade_row.get('Action', 'Open'),
                                        'realtime_price': current_price
                                    }
                                    
                                    all_trades.append(trade_dict)
                                    print(f"   ✅ Added NEWEST trade #{len(all_trades)}: {trade_dict['open_close']} {ticker_name}")
                            else:
                                print(f"   ⚠️ No real trades found for TODAY ({today_str})")
                        else:
                            print(f"   ⚠️ No matched trades in backtest result")
                    else:
                        print(f"   ⚠️ Invalid backtest result for {ticker_name}")
                else:
                    print(f"   ⚠️ {ticker_name} not found in crypto_tickers")
                    
            except Exception as backtest_error:
                print(f"   ❌ Backtest error for {ticker_name}: {backtest_error}")
                print(f"   🔄 Skipping {ticker_name} - no trades added")
                    
        except Exception as e:
            print(f"   ❌ Error processing {ticker_name}: {e}")
    
    # Sort trades by date (NEWEST FIRST for today's trades)
    all_trades.sort(key=lambda x: (x['date'], x.get('timestamp', 0)), reverse=True)
    
    # Print the report
    print(f"\n📊 ===== TODAY-ONLY TRADES REPORT (NEWEST FIRST) =====")
    print(f"🎯 Date Filter: ONLY {today_str} (TODAY)")
    print(f"📅 Selection: NEWEST trades from today only")
    print(f"⛔ Historical Filter: ALL 2024 orders BLOCKED")
    print(f"🔢 Total TODAY Trades: {len(all_trades)}")
    print(f"\n{header}")
    print("-" * 120)
    
    for trade in all_trades:
        line = f"{trade['date']};{trade['ticker']};{trade['quantity']:.6f};{trade['price']:.4f};{trade['order_type']};{trade['limit_price']:.4f};{trade['open_close']};{trade['realtime_price']:.4f}"
        print(line)
    
    # Save to CSV file
    csv_filename = f"TODAY_NEWEST_trades_{today_str.replace('-', '')}_{datetime.now().strftime('%H%M%S')}.csv"
    
    if all_trades:
        df = pd.DataFrame(all_trades)
        # Rename columns to match header
        df.columns = ['Date', 'Ticker', 'Quantity', 'Price', 'Order Type', 'Limit Price', 'Open/Close', 'Realtime Price Bitpanda']
        df.to_csv(csv_filename, sep=';', index=False)
        print(f"\n💾 TODAY's NEWEST trades saved as: {csv_filename}")
        print(f"🎯 Contains ONLY the NEWEST trades for {today_str}")
        print(f"⛔ NO historical orders from 2024 included!")
        print(f"📊 Total trades in file: {len(all_trades)}")
    else:
        print(f"\n⚠️ No real trades found for TODAY ({today_str})")
        print(f"💡 This means no actual trading signals were generated today")
        print(f"🔍 Check if backtest analysis is producing trades")
    
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
