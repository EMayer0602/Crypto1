#!/usr/bin/env python3
"""
ACTUAL TRADING SUMMARY 2024 - Based on your real trading files
"""

import pandas as pd
import os
from datetime import datetime
import glob

def analyze_actual_trades():
    """Analyze your actual trading files"""
    print("📊 ACTUAL TRADING SUMMARY 2024")
    print("=" * 60)
    
    all_trades = []
    
    # 1. Analyze Paper Trading Files (your actual orders to Bitpanda)
    print("\n📋 PAPER TRADING ORDERS (Bitpanda):")
    paper_files = glob.glob("bitpanda_paper_trading_*.csv")
    
    for file in paper_files:
        print(f"   📄 {file}")
        try:
            df = pd.read_csv(file, delimiter=';')
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Filter for 2024 if exists
            df_2024 = df[df['Date'].dt.year == 2024] if not df.empty else pd.DataFrame()
            
            for _, row in df.iterrows():  # All data since files are recent
                trade = {
                    'date': row['Date'],
                    'time': row.get('Time', 'N/A'),
                    'ticker': row['Ticker'],
                    'action': row['Action'],
                    'quantity': float(row['Quantity']),
                    'price': float(row['Price']),
                    'value': float(row['Value']),
                    'fees': float(row.get('Fees', 0)),
                    'type': 'PAPER_TRADING',
                    'source': file
                }
                all_trades.append(trade)
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # 2. Analyze 14-Day Trades (your strategy signals)
    print(f"\n📈 STRATEGY SIGNALS (14-Day Trades):")
    strategy_files = glob.glob("14_day_trades_*.csv")
    
    for file in strategy_files:
        print(f"   📄 {file}")
        try:
            df = pd.read_csv(file, delimiter=';')
            df['Date'] = pd.to_datetime(df['Date'])
            
            for _, row in df.iterrows():
                trade = {
                    'date': row['Date'],
                    'ticker': row['Ticker'],
                    'quantity': float(row['Quantity']),
                    'price': float(row['Price']),
                    'value': float(row['Quantity']) * float(row['Price']),
                    'action': row['Open/Close'],
                    'order_type': row.get('Order Type', 'Limit'),
                    'type': 'STRATEGY_SIGNAL',
                    'source': file
                }
                all_trades.append(trade)
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print(f"\n✅ Total trades collected: {len(all_trades)}")
    
    return all_trades

def calculate_trading_performance(trades):
    """Calculate comprehensive trading performance"""
    print(f"\n💰 CALCULATING PERFORMANCE...")
    
    # Separate paper trading from strategy signals
    paper_trades = [t for t in trades if t['type'] == 'PAPER_TRADING']
    strategy_trades = [t for t in trades if t['type'] == 'STRATEGY_SIGNAL']
    
    # Paper Trading Performance
    paper_stats = {}
    if paper_trades:
        paper_df = pd.DataFrame(paper_trades)
        
        paper_stats = {
            'total_orders': len(paper_trades),
            'buy_orders': len(paper_df[paper_df['action'] == 'BUY']),
            'sell_orders': len(paper_df[paper_df['action'] == 'SELL']),
            'total_buy_value': paper_df[paper_df['action'] == 'BUY']['value'].sum(),
            'total_sell_value': paper_df[paper_df['action'] == 'SELL']['value'].sum(),
            'total_fees': paper_df['fees'].sum(),
            'tickers_traded': paper_df['ticker'].unique().tolist(),
            'date_range': {
                'start': paper_df['date'].min(),
                'end': paper_df['date'].max()
            }
        }
        
        paper_stats['net_pnl'] = paper_stats['total_sell_value'] - paper_stats['total_buy_value'] - paper_stats['total_fees']
    
    # Strategy Performance
    strategy_stats = {}
    if strategy_trades:
        strategy_df = pd.DataFrame(strategy_trades)
        
        strategy_stats = {
            'total_signals': len(strategy_trades),
            'open_signals': len(strategy_df[strategy_df['action'] == 'Open']),
            'close_signals': len(strategy_df[strategy_df['action'] == 'Close']),
            'total_signal_value': strategy_df['value'].sum(),
            'tickers_signaled': strategy_df['ticker'].unique().tolist(),
            'date_range': {
                'start': strategy_df['date'].min(),
                'end': strategy_df['date'].max()
            }
        }
    
    return paper_stats, strategy_stats

def generate_detailed_report(trades, paper_stats, strategy_stats):
    """Generate detailed trading report"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"ACTUAL_TRADING_SUMMARY_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("ACTUAL CRYPTO TRADING SUMMARY\n")
        f.write("=" * 60 + "\n")
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Analysis Period: 2024-2025\n")
        f.write("=" * 60 + "\n\n")
        
        # Paper Trading Summary
        if paper_stats:
            f.write("PAPER TRADING PERFORMANCE (Actual Orders to Bitpanda)\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total Orders Executed: {paper_stats['total_orders']}\n")
            f.write(f"Buy Orders: {paper_stats['buy_orders']}\n")
            f.write(f"Sell Orders: {paper_stats['sell_orders']}\n")
            f.write(f"Total Buy Value: €{paper_stats['total_buy_value']:.2f}\n")
            f.write(f"Total Sell Value: €{paper_stats['total_sell_value']:.2f}\n")
            f.write(f"Total Fees Paid: €{paper_stats['total_fees']:.2f}\n")
            f.write(f"Net P&L: €{paper_stats['net_pnl']:.2f}\n")
            f.write(f"Trading Period: {paper_stats['date_range']['start']} to {paper_stats['date_range']['end']}\n")
            f.write(f"Cryptocurrencies Traded: {', '.join(paper_stats['tickers_traded'])}\n\n")
        
        # Strategy Performance
        if strategy_stats:
            f.write("STRATEGY SIGNAL PERFORMANCE (Trading System)\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total Signals Generated: {strategy_stats['total_signals']}\n")
            f.write(f"Open Signals: {strategy_stats['open_signals']}\n")
            f.write(f"Close Signals: {strategy_stats['close_signals']}\n")
            f.write(f"Total Signal Value: €{strategy_stats['total_signal_value']:.2f}\n")
            f.write(f"Signal Period: {strategy_stats['date_range']['start']} to {strategy_stats['date_range']['end']}\n")
            f.write(f"Cryptocurrencies Signaled: {', '.join(strategy_stats['tickers_signaled'])}\n\n")
        
        # Detailed Transaction Log
        f.write("DETAILED TRANSACTION LOG\n")
        f.write("=" * 60 + "\n")
        
        # Sort trades by date
        sorted_trades = sorted(trades, key=lambda x: x['date'])
        
        current_type = None
        for i, trade in enumerate(sorted_trades, 1):
            if trade['type'] != current_type:
                f.write(f"\n--- {trade['type'].replace('_', ' ')} ---\n")
                current_type = trade['type']
            
            f.write(f"\n#{i}. {trade['date'].strftime('%Y-%m-%d')} | {trade['ticker']}\n")
            f.write(f"    Action: {trade['action']}\n")
            f.write(f"    Quantity: {trade['quantity']:.6f}\n")
            f.write(f"    Price: €{trade['price']:.2f}\n")
            f.write(f"    Value: €{trade['value']:.2f}\n")
            
            if 'fees' in trade and trade['fees'] > 0:
                f.write(f"    Fees: €{trade['fees']:.2f}\n")
            if 'time' in trade and trade['time'] != 'N/A':
                f.write(f"    Time: {trade['time']}\n")
            
            f.write(f"    Source: {trade['source']}\n")
        
        # Summary by Cryptocurrency
        f.write(f"\n" + "=" * 60 + "\n")
        f.write("SUMMARY BY CRYPTOCURRENCY\n")
        f.write("=" * 60 + "\n")
        
        # Group by ticker
        ticker_summary = {}
        for trade in trades:
            ticker = trade['ticker']
            if ticker not in ticker_summary:
                ticker_summary[ticker] = {
                    'total_trades': 0,
                    'total_value': 0,
                    'buy_value': 0,
                    'sell_value': 0,
                    'fees': 0
                }
            
            ticker_summary[ticker]['total_trades'] += 1
            ticker_summary[ticker]['total_value'] += trade['value']
            
            if trade.get('action') == 'BUY':
                ticker_summary[ticker]['buy_value'] += trade['value']
            elif trade.get('action') == 'SELL':
                ticker_summary[ticker]['sell_value'] += trade['value']
            
            if 'fees' in trade:
                ticker_summary[ticker]['fees'] += trade.get('fees', 0)
        
        for ticker, summary in ticker_summary.items():
            f.write(f"\n{ticker}:\n")
            f.write(f"  Total Trades: {summary['total_trades']}\n")
            f.write(f"  Total Value: €{summary['total_value']:.2f}\n")
            f.write(f"  Buy Value: €{summary['buy_value']:.2f}\n")
            f.write(f"  Sell Value: €{summary['sell_value']:.2f}\n")
            if summary['fees'] > 0:
                f.write(f"  Fees: €{summary['fees']:.2f}\n")
            pnl = summary['sell_value'] - summary['buy_value'] - summary['fees']
            f.write(f"  Net P&L: €{pnl:.2f}\n")
    
    print(f"   💾 Report saved: {filename}")
    return filename

def main():
    """Main function"""
    
    # Analyze actual trades
    trades = analyze_actual_trades()
    
    if not trades:
        print("❌ No trading data found!")
        return
    
    # Calculate performance
    paper_stats, strategy_stats = calculate_trading_performance(trades)
    
    # Generate report
    report_file = generate_detailed_report(trades, paper_stats, strategy_stats)
    
    # Show summary
    print(f"\n🎉 TRADING ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"📄 Detailed Report: {report_file}")
    print("=" * 60)
    
    if paper_stats:
        print(f"\n📊 PAPER TRADING SUMMARY:")
        print(f"   Total Orders: {paper_stats['total_orders']}")
        print(f"   Net P&L: €{paper_stats['net_pnl']:.2f}")
        print(f"   Total Fees: €{paper_stats['total_fees']:.2f}")
    
    if strategy_stats:
        print(f"\n📈 STRATEGY SUMMARY:")
        print(f"   Total Signals: {strategy_stats['total_signals']}")
        print(f"   Signal Value: €{strategy_stats['total_signal_value']:.2f}")

if __name__ == "__main__":
    main()
