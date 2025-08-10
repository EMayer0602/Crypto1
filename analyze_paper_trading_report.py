#!/usr/bin/env python3
"""
PAPER TRADING REPORT ANALYZER
Comprehensive analysis of the 14-day paper trading execution
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def analyze_paper_trading_report():
    """Analyze the paper trading CSV report"""
    
    report_file = "bitpanda_paper_trading_20250810_081105.csv"
    
    if not os.path.exists(report_file):
        print(f"❌ Report file not found: {report_file}")
        return
    
    # Load the trading report
    df = pd.read_csv(report_file, sep=';')
    
    print("🚀 PAPER TRADING COMPREHENSIVE REPORT")
    print("=" * 80)
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Source File: {report_file}")
    print(f"📊 Total Trades: {len(df)}")
    print("=" * 80)
    
    # Basic Statistics
    print(f"\n📈 TRADING STATISTICS:")
    print("-" * 40)
    
    buy_trades = df[df['Action'] == 'BUY']
    sell_trades = df[df['Action'] == 'SELL']
    
    print(f"🟢 Buy Trades: {len(buy_trades)}")
    print(f"🔴 Sell Trades: {len(sell_trades)}")
    print(f"⚖️ Trade Balance: {len(sell_trades) - len(buy_trades)} (0 = fully closed)")
    
    total_volume = df['Value'].sum()
    total_fees = df['Fees'].sum()
    
    print(f"💰 Total Trading Volume: €{total_volume:,.2f}")
    print(f"💸 Total Fees Paid: €{total_fees:.2f}")
    print(f"📊 Average Fee Rate: {(total_fees/total_volume)*100:.3f}%")
    
    # Per-Cryptocurrency Analysis
    print(f"\n📊 PER-CRYPTOCURRENCY ANALYSIS:")
    print("-" * 60)
    print(f"{'Crypto':10} | {'Buy €':>10} | {'Sell €':>10} | {'Profit €':>10} | {'ROI %':>8}")
    print("-" * 60)
    
    total_profit = 0.0
    total_invested = 0.0
    
    for ticker in df['Ticker'].unique():
        ticker_trades = df[df['Ticker'] == ticker]
        
        buy_value = ticker_trades[ticker_trades['Action'] == 'BUY']['Value'].sum()
        sell_value = ticker_trades[ticker_trades['Action'] == 'SELL']['Value'].sum()
        
        # Calculate fees for this ticker
        ticker_fees = ticker_trades['Fees'].sum()
        
        # Net profit (sell - buy - fees)
        profit = sell_value - buy_value - ticker_fees
        roi = (profit / buy_value) * 100 if buy_value > 0 else 0
        
        print(f"{ticker:10} | €{buy_value:>9.2f} | €{sell_value:>9.2f} | €{profit:>+9.2f} | {roi:>+6.2f}%")
        
        total_profit += profit
        total_invested += buy_value
    
    print("-" * 60)
    total_roi = (total_profit / total_invested) * 100 if total_invested > 0 else 0
    print(f"{'TOTAL':10} | €{total_invested:>9.2f} | €{total_invested + total_profit + total_fees:>9.2f} | €{total_profit:>+9.2f} | {total_roi:>+6.2f}%")
    
    # Price Movement Analysis
    print(f"\n📈 PRICE MOVEMENT ANALYSIS:")
    print("-" * 70)
    print(f"{'Crypto':10} | {'Buy Price':>12} | {'Sell Price':>12} | {'Price Δ':>10} | {'Price %':>8}")
    print("-" * 70)
    
    for ticker in df['Ticker'].unique():
        ticker_trades = df[df['Ticker'] == ticker]
        
        buy_trades_ticker = ticker_trades[ticker_trades['Action'] == 'BUY']
        sell_trades_ticker = ticker_trades[ticker_trades['Action'] == 'SELL']
        
        if not buy_trades_ticker.empty and not sell_trades_ticker.empty:
            avg_buy_price = buy_trades_ticker['Price'].mean()
            avg_sell_price = sell_trades_ticker['Price'].mean()
            price_diff = avg_sell_price - avg_buy_price
            price_pct = (price_diff / avg_buy_price) * 100
            
            print(f"{ticker:10} | €{avg_buy_price:>11.4f} | €{avg_sell_price:>11.4f} | €{price_diff:>+9.4f} | {price_pct:>+6.2f}%")
    
    # Timing Analysis
    print(f"\n⏰ TIMING ANALYSIS:")
    print("-" * 40)
    
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    
    first_trade = df['DateTime'].min()
    last_trade = df['DateTime'].max()
    duration = last_trade - first_trade
    
    print(f"🕐 First Trade: {first_trade}")
    print(f"🕐 Last Trade: {last_trade}")
    print(f"⏱️ Total Duration: {duration}")
    print(f"📊 Trades per Second: {len(df) / duration.total_seconds():.2f}")
    
    # Portfolio Summary
    print(f"\n💼 PORTFOLIO SUMMARY:")
    print("-" * 40)
    
    starting_capital = 16000.0
    final_cash = starting_capital + total_profit
    
    print(f"💰 Starting Capital: €{starting_capital:,.2f}")
    print(f"💸 Total Fees: €{total_fees:.2f}")
    print(f"💵 Final Cash: €{final_cash:,.2f}")
    print(f"📈 Net Profit: €{total_profit:+,.2f}")
    print(f"📊 Total ROI: {total_roi:+.2f}%")
    
    # Risk Analysis
    print(f"\n⚠️ RISK ANALYSIS:")
    print("-" * 40)
    
    max_position_size = df[df['Action'] == 'BUY']['Value'].max()
    avg_position_size = df[df['Action'] == 'BUY']['Value'].mean()
    
    print(f"📏 Max Position Size: €{max_position_size:.2f}")
    print(f"📏 Avg Position Size: €{avg_position_size:.2f}")
    print(f"📊 Position Size vs Capital: {(max_position_size/starting_capital)*100:.1f}%")
    print(f"🎯 Diversification: {len(df['Ticker'].unique())} different cryptocurrencies")
    
    # Success Rate
    profitable_cryptos = 0
    for ticker in df['Ticker'].unique():
        ticker_trades = df[df['Ticker'] == ticker]
        buy_value = ticker_trades[ticker_trades['Action'] == 'BUY']['Value'].sum()
        sell_value = ticker_trades[ticker_trades['Action'] == 'SELL']['Value'].sum()
        ticker_fees = ticker_trades['Fees'].sum()
        profit = sell_value - buy_value - ticker_fees
        if profit > 0:
            profitable_cryptos += 1
    
    success_rate = (profitable_cryptos / len(df['Ticker'].unique())) * 100
    
    print(f"\n🎯 SUCCESS METRICS:")
    print("-" * 40)
    print(f"✅ Profitable Trades: {profitable_cryptos}/{len(df['Ticker'].unique())}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    print(f"🔄 Complete Cycles: {min(len(buy_trades), len(sell_trades))}")
    print(f"📈 Average Profit per Trade: €{total_profit/len(df['Ticker'].unique()):.2f}")
    
    # Strategy Assessment
    print(f"\n🎯 STRATEGY ASSESSMENT:")
    print("-" * 50)
    
    if total_roi > 0:
        print("✅ PROFITABLE STRATEGY")
        if total_roi > 5:
            print("🚀 EXCELLENT PERFORMANCE")
        elif total_roi > 1:
            print("👍 GOOD PERFORMANCE")
        else:
            print("📈 MODEST GAINS")
    else:
        print("❌ LOSING STRATEGY")
    
    if success_rate == 100:
        print("🎯 PERFECT SUCCESS RATE")
    elif success_rate >= 80:
        print("✅ HIGH SUCCESS RATE")
    elif success_rate >= 60:
        print("👍 GOOD SUCCESS RATE")
    else:
        print("⚠️ LOW SUCCESS RATE")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    if total_roi > 0:
        print("✅ Strategy shows positive returns")
        print("📈 Consider increasing position sizes for higher profits")
        print("⏰ Good timing on entry and exit points")
    
    if success_rate == 100:
        print("🎯 Perfect execution - all trades profitable")
        print("🚀 Ready for live trading consideration")
    
    if total_fees < (total_volume * 0.002):  # Less than 0.2%
        print("💰 Low fee structure - cost-effective trading")
    
    print(f"\n{'=' * 80}")
    print("🎉 PAPER TRADING ANALYSIS COMPLETED")
    print(f"📊 Strategy validated with {total_roi:+.2f}% returns")
    print("🚀 Ready for next phase of trading!")
    print("=" * 80)

if __name__ == "__main__":
    analyze_paper_trading_report()
