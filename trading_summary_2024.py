#!/usr/bin/env python3
"""
TRADING SUMMARY 2024 - Actual Trading Performance Report
Shows buy/sell transactions, P&L, and trading statistics
"""

import pandas as pd
import os
import sys
from datetime import datetime
import glob

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers

class TradingSummary2024:
    """Generate actual trading performance summary for 2024"""
    
    def __init__(self):
        self.year = 2024
        self.trades = []
        self.performance = {}
        
        print("📊 TRADING SUMMARY 2024")
        print("=" * 60)
        print("📈 Analyzing actual buy/sell transactions and performance")
        print("=" * 60)
    
    def find_trading_files(self):
        """Find all files that contain actual trading data"""
        print("\n🔍 SEARCHING FOR TRADING FILES...")
        
        trading_patterns = [
            "*trades*.csv",
            "*paper_trading*.csv",
            "*backtest_report*.csv", 
            "*14_day*.csv",
            "*matched_trades*.csv",
            "*live_trading*.csv"
        ]
        
        found_files = []
        for pattern in trading_patterns:
            files = glob.glob(pattern)
            for file in files:
                if '2024' in file or self._contains_2024_data(file):
                    found_files.append(file)
                    print(f"   📄 Found: {file}")
        
        if not found_files:
            print("   ⚠️ No trading files found - checking backtest modules...")
            self._extract_from_backtest_modules()
        
        return found_files
    
    def _contains_2024_data(self, filename):
        """Check if file contains 2024 trading data"""
        try:
            df = pd.read_csv(filename, nrows=10)  # Check first 10 rows
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols:
                df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='coerce')
                return df[date_cols[0]].dt.year.eq(2024).any()
        except:
            pass
        return False
    
    def _extract_from_backtest_modules(self):
        """Extract trading data from backtest modules"""
        print("   🔧 Extracting from backtest modules...")
        
        try:
            from crypto_backtesting_module import run_live_backtest_analysis
            
            # Run backtest to get recent trading data
            result = run_live_backtest_analysis()
            
            if result and isinstance(result, dict):
                for ticker_name, ticker_data in result.items():
                    if isinstance(ticker_data, dict) and 'matched_trades' in ticker_data:
                        trades_df = ticker_data['matched_trades']
                        if not trades_df.empty:
                            self._process_trades_dataframe(trades_df, f"backtest_{ticker_name}")
            
        except Exception as e:
            print(f"   ⚠️ Backtest extraction error: {e}")
    
    def analyze_trading_files(self, files):
        """Analyze trading files to extract buy/sell transactions"""
        print("\n📋 ANALYZING TRADING TRANSACTIONS...")
        
        for file in files:
            try:
                print(f"   📊 Processing: {file}")
                df = pd.read_csv(file)
                self._process_trades_dataframe(df, file)
                
            except Exception as e:
                print(f"   ❌ Error processing {file}: {e}")
    
    def _process_trades_dataframe(self, df, source_file):
        """Process DataFrame to extract trading transactions"""
        if df.empty:
            return
        
        # Look for trading indicators
        trade_indicators = ['action', 'side', 'type', 'buy', 'sell', 'open', 'close']
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        
        if not date_cols:
            return
        
        date_col = date_cols[0]
        
        try:
            df[date_col] = pd.to_datetime(df[date_col])
            df_2024 = df[df[date_col].dt.year == 2024]
            
            for _, row in df_2024.iterrows():
                trade = self._extract_trade_info(row, source_file)
                if trade:
                    self.trades.append(trade)
                    
        except Exception as e:
            print(f"      ⚠️ Processing error: {e}")
    
    def _extract_trade_info(self, row, source_file):
        """Extract trading information from a row"""
        trade = {
            'date': row.get('Date', row.get('date', 'Unknown')),
            'source': source_file,
            'ticker': 'Unknown',
            'action': 'Unknown',
            'quantity': 0.0,
            'price': 0.0,
            'value': 0.0
        }
        
        # Extract ticker
        for col in row.index:
            if any(ticker in str(col).upper() for ticker in ['BTC', 'ETH', 'XRP', 'DOGE', 'SOL', 'LINK']):
                trade['ticker'] = col
                break
        
        # Extract action
        for col in row.index:
            col_lower = str(col).lower()
            if 'action' in col_lower or 'side' in col_lower:
                trade['action'] = str(row[col])
                break
            elif 'buy' in col_lower:
                trade['action'] = 'BUY'
                break
            elif 'sell' in col_lower:
                trade['action'] = 'SELL'
                break
        
        # Extract quantity and price
        for col in row.index:
            col_lower = str(col).lower()
            if 'quantity' in col_lower or 'amount' in col_lower:
                try:
                    trade['quantity'] = float(row[col])
                except:
                    pass
            elif 'price' in col_lower:
                try:
                    trade['price'] = float(row[col])
                except:
                    pass
        
        # Calculate value
        if trade['quantity'] > 0 and trade['price'] > 0:
            trade['value'] = trade['quantity'] * trade['price']
        
        return trade if trade['action'] != 'Unknown' else None
    
    def calculate_performance(self):
        """Calculate trading performance metrics"""
        print("\n💰 CALCULATING TRADING PERFORMANCE...")
        
        if not self.trades:
            print("   ⚠️ No trades found for performance calculation")
            return
        
        # Group trades by ticker
        ticker_performance = {}
        total_buys = 0
        total_sells = 0
        total_buy_value = 0
        total_sell_value = 0
        
        for trade in self.trades:
            ticker = trade['ticker']
            if ticker not in ticker_performance:
                ticker_performance[ticker] = {
                    'buys': 0,
                    'sells': 0,
                    'buy_value': 0,
                    'sell_value': 0,
                    'quantity_held': 0
                }
            
            if 'BUY' in trade['action'].upper():
                ticker_performance[ticker]['buys'] += 1
                ticker_performance[ticker]['buy_value'] += trade['value']
                ticker_performance[ticker]['quantity_held'] += trade['quantity']
                total_buys += 1
                total_buy_value += trade['value']
                
            elif 'SELL' in trade['action'].upper():
                ticker_performance[ticker]['sells'] += 1
                ticker_performance[ticker]['sell_value'] += trade['value']
                ticker_performance[ticker]['quantity_held'] -= trade['quantity']
                total_sells += 1
                total_sell_value += trade['value']
        
        # Calculate P&L
        for ticker in ticker_performance:
            perf = ticker_performance[ticker]
            perf['realized_pnl'] = perf['sell_value'] - perf['buy_value']
            perf['avg_buy_price'] = perf['buy_value'] / max(perf['buys'], 1)
            perf['avg_sell_price'] = perf['sell_value'] / max(perf['sells'], 1)
        
        self.performance = {
            'total_trades': len(self.trades),
            'total_buys': total_buys,
            'total_sells': total_sells,
            'total_buy_value': total_buy_value,
            'total_sell_value': total_sell_value,
            'net_pnl': total_sell_value - total_buy_value,
            'ticker_performance': ticker_performance
        }
        
        print(f"   📊 Total Trades: {self.performance['total_trades']}")
        print(f"   📈 Buy Orders: {self.performance['total_buys']}")
        print(f"   📉 Sell Orders: {self.performance['total_sells']}")
        print(f"   💶 Net P&L: €{self.performance['net_pnl']:.2f}")
    
    def generate_summary_report(self):
        """Generate comprehensive trading summary report"""
        print("\n📋 GENERATING TRADING SUMMARY REPORT...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"TRADING_SUMMARY_2024_{timestamp}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            # Header
            f.write("CRYPTO TRADING SUMMARY 2024\n")
            f.write("=" * 60 + "\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Trading Year: 2024\n")
            f.write("=" * 60 + "\n\n")
            
            # Overall Performance
            f.write("OVERALL TRADING PERFORMANCE\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Transactions: {self.performance.get('total_trades', 0)}\n")
            f.write(f"Buy Orders: {self.performance.get('total_buys', 0)}\n")
            f.write(f"Sell Orders: {self.performance.get('total_sells', 0)}\n")
            f.write(f"Total Buy Value: €{self.performance.get('total_buy_value', 0):.2f}\n")
            f.write(f"Total Sell Value: €{self.performance.get('total_sell_value', 0):.2f}\n")
            f.write(f"Net Profit/Loss: €{self.performance.get('net_pnl', 0):.2f}\n\n")
            
            # Per-Ticker Performance
            if 'ticker_performance' in self.performance:
                f.write("PER-CRYPTOCURRENCY PERFORMANCE\n")
                f.write("-" * 40 + "\n")
                
                for ticker, perf in self.performance['ticker_performance'].items():
                    f.write(f"\n{ticker}:\n")
                    f.write(f"  Buy Orders: {perf['buys']}\n")
                    f.write(f"  Sell Orders: {perf['sells']}\n")
                    f.write(f"  Buy Value: €{perf['buy_value']:.2f}\n")
                    f.write(f"  Sell Value: €{perf['sell_value']:.2f}\n")
                    f.write(f"  Realized P&L: €{perf['realized_pnl']:.2f}\n")
                    f.write(f"  Quantity Held: {perf['quantity_held']:.6f}\n")
                    
                    if perf['buys'] > 0:
                        f.write(f"  Avg Buy Price: €{perf['avg_buy_price']:.2f}\n")
                    if perf['sells'] > 0:
                        f.write(f"  Avg Sell Price: €{perf['avg_sell_price']:.2f}\n")
            
            # Detailed Transaction Log
            f.write("\n" + "=" * 60 + "\n")
            f.write("DETAILED TRANSACTION LOG\n")
            f.write("=" * 60 + "\n")
            
            for i, trade in enumerate(self.trades, 1):
                f.write(f"\nTransaction #{i}:\n")
                f.write(f"  Date: {trade['date']}\n")
                f.write(f"  Ticker: {trade['ticker']}\n")
                f.write(f"  Action: {trade['action']}\n")
                f.write(f"  Quantity: {trade['quantity']:.6f}\n")
                f.write(f"  Price: €{trade['price']:.2f}\n")
                f.write(f"  Value: €{trade['value']:.2f}\n")
                f.write(f"  Source: {trade['source']}\n")
        
        print(f"   💾 Trading summary saved as: {report_filename}")
        return report_filename

def main():
    """Main function to generate trading summary"""
    
    try:
        # Create trading summary instance
        summary = TradingSummary2024()
        
        # Find and analyze trading files
        trading_files = summary.find_trading_files()
        summary.analyze_trading_files(trading_files)
        
        # Calculate performance
        summary.calculate_performance()
        
        # Generate report
        report_file = summary.generate_summary_report()
        
        print(f"\n🎉 TRADING SUMMARY COMPLETE!")
        print("=" * 60)
        print(f"📄 Report: {report_file}")
        print("=" * 60)
        
        # Show quick summary
        if summary.performance:
            print(f"\n📊 QUICK SUMMARY:")
            print(f"Total Trades: {summary.performance.get('total_trades', 0)}")
            print(f"Net P&L: €{summary.performance.get('net_pnl', 0):.2f}")
            print(f"Buy Value: €{summary.performance.get('total_buy_value', 0):.2f}")
            print(f"Sell Value: €{summary.performance.get('total_sell_value', 0):.2f}")
        
    except Exception as e:
        print(f"\n❌ Error generating trading summary: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
