#!/usr/bin/env python3
"""
PAPER TRADING EXECUTION - 14 DAY TRADES REPLAY
Führt die letzten 14 Tage Trades im Paper Trading aus
"""

import sys
import os
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import existing Bitpanda adapter
from bitpanda_fusion_adapter import BitpandaFusionPaperTrader

class TradeReplayPaperTrading:
    """
    Replay 14-day trades in Paper Trading
    """
    
    def __init__(self):
        """Initialize the paper trader"""
        self.paper_trader = BitpandaFusionPaperTrader(sandbox=True)
        self.trade_file = "14_day_trades_report_20250810_075205.csv"
        
    def load_14_day_trades(self) -> pd.DataFrame:
        """Load the 14-day trades CSV"""
        
        if not os.path.exists(self.trade_file):
            print(f"❌ Trade file not found: {self.trade_file}")
            return pd.DataFrame()
            
        try:
            # Load CSV with semicolon separator
            df = pd.read_csv(self.trade_file, sep=';')
            
            print(f"📊 Loaded {len(df)} trades from {self.trade_file}")
            print(f"📅 Date range: {df['Date'].min()} to {df['Date'].max()}")
            
            # Convert Date column
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Sort by date for chronological execution
            df = df.sort_values('Date')
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading trades: {e}")
            return pd.DataFrame()
    
    def execute_historical_trades(self, trades_df: pd.DataFrame) -> None:
        """Execute trades chronologically in paper trading"""
        
        if trades_df.empty:
            print("❌ No trades to execute")
            return
            
        print(f"\n🎯 EXECUTING {len(trades_df)} HISTORICAL TRADES")
        print("=" * 60)
        
        executed_trades = 0
        total_volume = 0.0
        
        for idx, trade in trades_df.iterrows():
            try:
                date = trade['Date'].strftime('%Y-%m-%d')
                ticker = trade['Ticker']
                quantity = float(trade['Quantity'])
                price = float(trade['Price'])
                order_type = trade['Order Type']
                open_close = trade['Open/Close']
                realtime_price = float(trade['Realtime Price Bitpanda'])
                
                # Determine action based on Open/Close
                action = "BUY" if open_close == "Open" else "SELL"
                
                # Calculate EUR value
                eur_value = quantity * price
                total_volume += eur_value
                
                print(f"\n📅 {date} | {action:4} | {ticker:8} | {quantity:>10.6f} @ €{price:>10.4f}")
                print(f"   💰 EUR Value: €{eur_value:>8.2f} | Real-time: €{realtime_price:>8.4f}")
                
                # Execute the trade
                order_result = self.paper_trader.place_paper_order(
                    ticker_name=ticker,
                    action=action,
                    quantity=eur_value,  # EUR value
                    price=price,
                    order_type="LIMIT"
                )
                
                if order_result['status'] == 'FILLED':
                    executed_trades += 1
                    print(f"   ✅ Order executed: {order_result['order_id']}")
                else:
                    print(f"   ❌ Order rejected: {order_result.get('reason', 'Unknown')}")
                
                # Small delay between trades
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   ❌ Error executing trade: {e}")
                continue
        
        print(f"\n{'=' * 60}")
        print(f"📊 TRADE EXECUTION SUMMARY")
        print(f"✅ Executed: {executed_trades}/{len(trades_df)} trades")
        print(f"💰 Total Volume: €{total_volume:,.2f}")
        print("=" * 60)
    
    def generate_execution_report(self) -> None:
        """Generate final execution report"""
        
        current_prices = self.paper_trader.get_current_prices()
        portfolio = self.paper_trader.get_portfolio_value(current_prices)
        
        print(f"\n📊 PAPER TRADING EXECUTION REPORT")
        print("=" * 60)
        print(f"📅 Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Portfolio Summary
        print(f"\n💰 FINAL PORTFOLIO:")
        print(f"   💵 Cash: €{portfolio['cash']:,.2f}")
        print(f"   📈 Positions Value: €{portfolio['positions_value']:,.2f}")
        print(f"   🎯 Total Value: €{portfolio['total_value']:,.2f}")
        
        initial_capital = 16000.0
        performance = portfolio['total_value'] - initial_capital
        performance_pct = (performance / initial_capital) * 100
        
        print(f"   📊 Performance: €{performance:+,.2f} ({performance_pct:+.2f}%)")
        
        # Active Positions
        if portfolio['positions']:
            print(f"\n📊 ACTIVE POSITIONS:")
            print(f"   {'Ticker':10} | {'Quantity':>12} | {'Price':>10} | {'Value':>10} | {'P&L':>8}")
            print("-" * 60)
            
            for ticker, pos in portfolio['positions'].items():
                pnl_pct = (pos['pnl'] / pos['current_value']) * 100 if pos['current_value'] > 0 else 0
                print(f"   {ticker:10} | {pos['quantity']:>12.6f} | €{pos['current_price']:>9.4f} | €{pos['current_value']:>9.2f} | {pnl_pct:>+6.2f}%")
        
        # Trade History Summary
        if self.paper_trader.trade_history:
            print(f"\n📋 TRADE HISTORY ({len(self.paper_trader.trade_history)} trades):")
            
            buy_trades = [t for t in self.paper_trader.trade_history if t['action'] == 'BUY']
            sell_trades = [t for t in self.paper_trader.trade_history if t['action'] == 'SELL']
            
            print(f"   🟢 Buy Orders: {len(buy_trades)}")
            print(f"   🔴 Sell Orders: {len(sell_trades)}")
            
            total_fees = sum(t['fees'] for t in self.paper_trader.trade_history)
            print(f"   💸 Total Fees: €{total_fees:.2f}")
        
        # Save the execution report
        self.paper_trader.save_bitpanda_report()
        
    def run_14_day_replay(self) -> None:
        """Main function to run the 14-day trade replay"""
        
        print("🚀 14-DAY TRADES PAPER TRADING REPLAY")
        print("=" * 60)
        print("📊 Replaying historical trades in paper trading environment")
        print("💰 Starting with €16,000 virtual capital")
        print("=" * 60)
        
        # Load trades
        trades_df = self.load_14_day_trades()
        
        if trades_df.empty:
            print("❌ No trades to replay")
            return
            
        # Show initial portfolio
        current_prices = self.paper_trader.get_current_prices()
        initial_portfolio = self.paper_trader.get_portfolio_value(current_prices)
        
        print(f"\n💰 INITIAL PORTFOLIO:")
        print(f"   Cash: €{initial_portfolio['cash']:,.2f}")
        print(f"   Total Value: €{initial_portfolio['total_value']:,.2f}")
        
        # Execute trades
        self.execute_historical_trades(trades_df)
        
        # Generate final report
        self.generate_execution_report()
        
        print(f"\n✅ 14-DAY TRADE REPLAY COMPLETED!")
        print(f"📁 Trade report saved as CSV")

def main():
    """Main execution function"""
    replay_trader = TradeReplayPaperTrading()
    replay_trader.run_14_day_replay()

if __name__ == "__main__":
    main()
