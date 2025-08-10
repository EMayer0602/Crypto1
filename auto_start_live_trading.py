#!/usr/bin/env python3
"""
AUTO-START LIVE STRATEGY PAPER TRADING
Automatically starts 2-week live paper trading without user confirmation
"""

import sys
import os
import pandas as pd
import time
import requests
import json
from datetime import datetime, timedelta, time as dt_time
from typing import Dict, List, Optional, Any
import threading
import signal

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest
from bitpanda_secure_api import get_api_key_safely

class AutoLiveStrategyPaperTrader:
    """
    Auto-Start Live Strategy Execution with Bitpanda Paper Trading
    """
    
    def __init__(self):
        """Initialize live trading system"""
        self.api_key = get_api_key_safely()
        self.base_url = "https://api.bitpanda.com/v1"
        self.running = False
        self.positions = {}
        self.trade_log = []
        self.last_signals = {}
        
        # Trading parameters
        self.check_interval = 300  # Check every 5 minutes
        self.trading_hours = {
            'start': dt_time(0, 0),   # 00:00 - 24/7 trading
            'end': dt_time(23, 59)    # 23:59 - 24/7 trading
        }
        
        print("🚀 AUTO-START LIVE STRATEGY PAPER TRADING")
        print("=" * 60)
        print(f"🔑 API Key: {'✅ Loaded' if self.api_key else '❌ Missing'}")
        print(f"⏰ Check Interval: {self.check_interval} seconds")
        print(f"🕐 Trading Hours: 24/7 CONTINUOUS")
        print(f"📅 Duration: 14 days")
        print("=" * 60)
    
    def is_trading_hours(self) -> bool:
        """Check if we're in trading hours - ALWAYS TRUE for crypto 24/7"""
        return True  # Crypto markets never close - trade 24/7
    
    def get_current_market_prices(self) -> Dict[str, float]:
        """Get current market prices"""
        prices = {}
        
        try:
            # Use Yahoo Finance for reliable data
            import yfinance as yf
            for ticker_name, config in crypto_tickers.items():
                try:
                    symbol = config['symbol']
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d", interval="1m")
                    if not hist.empty:
                        prices[ticker_name] = float(hist['Close'].iloc[-1])
                except Exception as e:
                    print(f"⚠️ Error getting {ticker_name} price: {e}")
        
        except Exception as e:
            print(f"⚠️ Error getting market prices: {e}")
        
        return prices
    
    def run_strategy_analysis(self, ticker_name: str) -> Dict[str, Any]:
        """Run strategy analysis for a specific ticker"""
        try:
            config = crypto_tickers[ticker_name]
            symbol = config['symbol']
            
            # Run backtest to get strategy signals
            backtest_result = run_backtest(symbol, config)
            
            if not backtest_result or not backtest_result.get('matched_trades'):
                return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'No backtest data'}
            
            # Analyze recent trades for signals
            matched_trades = backtest_result['matched_trades']
            recent_trades = matched_trades.tail(5)  # Last 5 trades
            
            # Generate trading signal based on strategy
            signal = self.generate_live_signal(ticker_name, recent_trades, backtest_result)
            
            return signal
            
        except Exception as e:
            return {'signal': 'HOLD', 'strength': 0.0, 'reason': f'Error: {e}'}
    
    def generate_live_signal(self, ticker_name: str, recent_trades: pd.DataFrame, 
                            backtest_result: Dict) -> Dict[str, Any]:
        """Generate live trading signal based on strategy results"""
        
        if recent_trades.empty:
            return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'No trade history'}
        
        # Analyze strategy performance
        total_pnl = recent_trades.get('PnL', pd.Series()).sum() if 'PnL' in recent_trades.columns else 0
        profitable_trades = len(recent_trades[recent_trades.get('PnL', 0) > 0])
        win_rate = profitable_trades / len(recent_trades) if len(recent_trades) > 0 else 0
        
        # Check if we already have a position
        has_position = ticker_name in self.positions and self.positions[ticker_name]['quantity'] > 0
        
        # Strategy logic - more aggressive for live trading
        if not has_position:
            # Look for BUY signals
            if win_rate >= 0.4 and len(recent_trades) >= 3:  # Lower threshold for more trades
                return {
                    'signal': 'BUY',
                    'strength': min(win_rate + 0.3, 1.0),  # Boost signal strength
                    'reason': f'Win rate: {win_rate:.1%}, PnL: {total_pnl:.2f}, Trades: {len(recent_trades)}'
                }
        else:
            # Look for SELL signals - take profit or stop loss
            if len(recent_trades) >= 2:  # Sell after some trades
                return {
                    'signal': 'SELL',
                    'strength': 0.8,
                    'reason': f'Exit after {len(recent_trades)} trades, PnL: {total_pnl:.2f}'
                }
        
        return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'Waiting for clear signal'}
    
    def place_paper_order(self, ticker_name: str, action: str, 
                         amount_eur: float, price: float) -> Dict[str, Any]:
        """Place paper trading order"""
        
        order_id = f"AUTO_{int(time.time())}_{ticker_name}_{action}"
        
        # Calculate coin quantity
        config = crypto_tickers[ticker_name]
        round_factor = config['order_round_factor']
        coin_quantity = amount_eur / price
        coin_quantity = round(coin_quantity / round_factor) * round_factor
        
        # Simulate successful execution
        order_result = {
            'order_id': order_id,
            'status': 'filled',
            'ticker': ticker_name,
            'action': action,
            'amount_eur': amount_eur,
            'coin_quantity': coin_quantity,
            'price': price,
            'timestamp': datetime.now(),
            'fees': amount_eur * 0.0015  # 0.15% fee
        }
        
        # Update positions
        if action == 'BUY':
            if ticker_name not in self.positions:
                self.positions[ticker_name] = {'quantity': 0.0, 'avg_price': 0.0, 'total_cost': 0.0}
            
            pos = self.positions[ticker_name]
            new_total_cost = pos['total_cost'] + amount_eur
            new_quantity = pos['quantity'] + coin_quantity
            
            self.positions[ticker_name] = {
                'quantity': new_quantity,
                'avg_price': new_total_cost / new_quantity if new_quantity > 0 else price,
                'total_cost': new_total_cost
            }
            
        elif action == 'SELL' and ticker_name in self.positions:
            pos = self.positions[ticker_name]
            if pos['quantity'] >= coin_quantity:
                pos['quantity'] -= coin_quantity
                if pos['quantity'] > 0:
                    pos['total_cost'] *= (pos['quantity'] / (pos['quantity'] + coin_quantity))
                else:
                    pos['total_cost'] = 0
        
        # Log the trade
        self.trade_log.append(order_result)
        
        print(f"✅ {action} ORDER: {coin_quantity:.6f} {ticker_name} @ €{price:.4f} (€{amount_eur:.2f})")
        
        return order_result
    
    def process_trading_cycle(self):
        """Process one trading cycle"""
        
        if not self.is_trading_hours():
            return
        
        print(f"\n🔍 TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # Get current prices
        current_prices = self.get_current_market_prices()
        
        if not current_prices:
            print("⚠️ No current prices available - skipping cycle")
            return
        
        trades_executed = 0
        
        # Process each cryptocurrency
        for ticker_name in crypto_tickers.keys():
            try:
                if ticker_name not in current_prices:
                    continue
                
                current_price = current_prices[ticker_name]
                
                # Run strategy analysis
                signal_data = self.run_strategy_analysis(ticker_name)
                signal = signal_data['signal']
                strength = signal_data['strength']
                reason = signal_data.get('reason', 'No reason')
                
                print(f"{ticker_name:10} | €{current_price:>8.4f} | {signal:4} | {strength:.2f} | {reason}")
                
                # Execute trades based on signals
                if signal in ['BUY', 'SELL'] and strength > 0.6:  # Lower threshold for more activity
                    
                    # Calculate position size
                    base_size = crypto_tickers[ticker_name]['initialCapitalLong']
                    position_size = base_size * strength
                    
                    # Place order
                    order_result = self.place_paper_order(
                        ticker_name=ticker_name,
                        action=signal,
                        amount_eur=position_size,
                        price=current_price
                    )
                    
                    if order_result.get('status') == 'filled':
                        trades_executed += 1
                
                time.sleep(0.5)  # Small delay between tickers
                
            except Exception as e:
                print(f"❌ Error processing {ticker_name}: {e}")
        
        if trades_executed > 0:
            print(f"📊 {trades_executed} trades executed this cycle")
        
        return trades_executed
    
    def show_portfolio_status(self):
        """Show current portfolio status"""
        
        current_prices = self.get_current_market_prices()
        total_value = 0.0
        
        print(f"\n💼 PORTFOLIO STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        if self.positions and current_prices:
            print("📊 ACTIVE POSITIONS:")
            print(f"{'Ticker':10} | {'Quantity':>12} | {'Price':>10} | {'Value':>10} | {'P&L %':>8}")
            print("-" * 60)
            
            for ticker, pos in self.positions.items():
                if pos['quantity'] > 0 and ticker in current_prices:
                    current_value = pos['quantity'] * current_prices[ticker]
                    cost_basis = pos['quantity'] * pos['avg_price']
                    pnl_pct = ((current_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
                    total_value += current_value
                    
                    print(f"{ticker:10} | {pos['quantity']:>12.6f} | €{current_prices[ticker]:>9.4f} | €{current_value:>9.2f} | {pnl_pct:>+6.2f}%")
        
        print("-" * 60)
        print(f"💰 Total Portfolio Value: €{total_value:.2f}")
        print(f"📋 Total Trades Executed: {len(self.trade_log)}")
    
    def save_trading_log(self):
        """Save trading log periodically"""
        if self.trade_log:
            df = pd.DataFrame(self.trade_log)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"auto_live_paper_trading_{timestamp}.csv"
            df.to_csv(filename, index=False)
            print(f"💾 Log saved: {filename}")
    
    def start_auto_trading(self, duration_days: int = 14):
        """Start automatic 2-week live trading"""
        
        print(f"🚀 AUTO-STARTING 2-WEEK LIVE PAPER TRADING")
        print("=" * 60)
        print(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 End Time: {(datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Check Every: {self.check_interval} seconds")
        print("=" * 60)
        
        self.running = True
        start_time = datetime.now()
        end_time = start_time + timedelta(days=duration_days)
        
        cycle_count = 0
        total_trades = 0
        
        try:
            while self.running and datetime.now() < end_time:
                cycle_count += 1
                
                # Process trading cycle
                trades = self.process_trading_cycle()
                if trades:
                    total_trades += trades
                
                # Show status every 12 cycles (1 hour)
                if cycle_count % 12 == 0:
                    self.show_portfolio_status()
                
                # Save log every 100 cycles
                if cycle_count % 100 == 0:
                    self.save_trading_log()
                
                # Calculate time remaining
                time_remaining = end_time - datetime.now()
                days_remaining = time_remaining.days
                hours_remaining = time_remaining.seconds // 3600
                
                print(f"⏳ Cycle {cycle_count} | {days_remaining}d {hours_remaining}h remaining | Next check in {self.check_interval}s")
                
                # Wait for next cycle
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 STOPPED BY USER")
        
        finally:
            self.running = False
            self.save_trading_log()
            self.show_portfolio_status()
            
            elapsed_time = datetime.now() - start_time
            
            print(f"\n🏁 2-WEEK LIVE PAPER TRADING COMPLETED!")
            print("=" * 60)
            print(f"📅 Actual Duration: {elapsed_time}")
            print(f"🔄 Total Cycles: {cycle_count}")
            print(f"📊 Total Trades: {total_trades}")
            print(f"💰 Final Portfolio Value: Check status above")
            print("=" * 60)

def main():
    """Main auto-start function"""
    
    print("🎯 AUTO-STARTING LIVE STRATEGY PAPER TRADING")
    print("💡 No user confirmation needed - starting immediately")
    print("⚠️ Press Ctrl+C to stop at any time")
    print()
    
    # Create and start trader immediately
    trader = AutoLiveStrategyPaperTrader()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        trader.running = False
        print("\n🛑 Shutdown signal received...")
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start 2-week trading immediately
    trader.start_auto_trading(duration_days=14)

if __name__ == "__main__":
    main()
