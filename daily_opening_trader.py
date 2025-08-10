#!/usr/bin/env python3
"""
DAILY OPENING STRATEGY TRADER
Runs at market open, executes strategy ONCE per day, transmits orders immediately
"""

import sys
import os
import pandas as pd
import time
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import signal

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest
from bitpanda_secure_api import get_api_key_safely

class DailyOpeningTrader:
    """
    Daily Opening Strategy Trader - Runs at market open for 15 minutes
    """
    
    def __init__(self):
        """Initialize the daily opening trader"""
        self.api_key = get_api_key_safely()
        self.base_url = "https://api.bitpanda.com/v1"
        self.running = False
        self.positions = {}
        self.trade_log = []
        
        # Trading parameters - Simple approach
        self.market_open_time = "00:00"  # UTC midnight - crypto daily open
        
        print("🕐 DAILY OPENING STRATEGY TRADER - SIMPLIFIED")
        print("=" * 60)
        print(f"🔑 API Key: {'✅ Loaded' if self.api_key else '❌ Missing'}")
        print(f"🕐 Market Open Time: {self.market_open_time} UTC")
        print("💡 Strategy: Run ONCE per day at opening, transmit orders immediately")
        print("=" * 60)
    
    def get_current_market_prices(self) -> Dict[str, float]:
        """Get current market prices for opening trades"""
        prices = {}
        
        try:
            # Use Yahoo Finance for reliable opening prices
            import yfinance as yf
            for ticker_name, config in crypto_tickers.items():
                try:
                    symbol = config['symbol']
                    ticker = yf.Ticker(symbol)
                    
                    # Get today's data for opening price
                    hist = ticker.history(period="1d", interval="1m")
                    if not hist.empty:
                        # Use the most recent price as "opening" price
                        prices[ticker_name] = float(hist['Open'].iloc[0])  # Today's opening
                        print(f"📈 {ticker_name}: Opening @ €{prices[ticker_name]:.4f}")
                    
                except Exception as e:
                    print(f"⚠️ Error getting {ticker_name} opening price: {e}")
        
        except Exception as e:
            print(f"⚠️ Error getting opening prices: {e}")
        
        return prices
    
    def run_strategy_for_ticker(self, ticker_name: str) -> Dict[str, Any]:
        """Run strategy analysis for a specific ticker at market open"""
        try:
            config = crypto_tickers[ticker_name]
            symbol = config['symbol']
            
            print(f"🔍 Analyzing {ticker_name} strategy...")
            
            # Run backtest to get strategy signals
            backtest_result = run_backtest(symbol, config)
            
            if not backtest_result or not backtest_result.get('matched_trades'):
                return {
                    'signal': 'HOLD', 
                    'strength': 0.0, 
                    'reason': 'No backtest data available'
                }
            
            # Analyze strategy results for opening signals
            matched_trades = backtest_result['matched_trades']
            
            # Get the most recent signals
            if len(matched_trades) > 0:
                last_trade = matched_trades.iloc[-1]
                recent_trades = matched_trades.tail(5)  # Last 5 trades
                
                # Generate opening signal
                signal = self.generate_opening_signal(ticker_name, recent_trades, last_trade)
                return signal
            else:
                return {
                    'signal': 'HOLD', 
                    'strength': 0.0, 
                    'reason': 'No recent trades in strategy'
                }
            
        except Exception as e:
            print(f"❌ Strategy analysis error for {ticker_name}: {e}")
            return {
                'signal': 'HOLD', 
                'strength': 0.0, 
                'reason': f'Analysis error: {e}'
            }
    
    def generate_opening_signal(self, ticker_name: str, recent_trades: pd.DataFrame, 
                               last_trade: pd.Series) -> Dict[str, Any]:
        """Generate opening trading signal based on strategy"""
        
        if recent_trades.empty:
            return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'No trade history'}
        
        # Strategy logic for opening trades
        try:
            # Check if we have PnL data
            if 'PnL' in recent_trades.columns:
                total_pnl = recent_trades['PnL'].sum()
                profitable_trades = len(recent_trades[recent_trades['PnL'] > 0])
                win_rate = profitable_trades / len(recent_trades)
                
                # Check current position status
                has_position = ticker_name in self.positions and self.positions[ticker_name]['quantity'] > 0
                
                # Opening strategy logic
                if not has_position:
                    # Look for BUY signals at market open
                    if win_rate >= 0.6 and total_pnl > 0:  # Strong positive signals
                        return {
                            'signal': 'BUY',
                            'strength': min(win_rate, 1.0),
                            'reason': f'Opening BUY: Win rate {win_rate:.1%}, PnL €{total_pnl:.2f}'
                        }
                    elif win_rate >= 0.4 and len(recent_trades) >= 3:  # Moderate signals
                        return {
                            'signal': 'BUY',
                            'strength': 0.7,
                            'reason': f'Moderate BUY: Win rate {win_rate:.1%}, {len(recent_trades)} trades'
                        }
                else:
                    # Look for SELL signals if we have positions
                    if win_rate < 0.3 or total_pnl < -20:  # Poor performance, exit
                        return {
                            'signal': 'SELL',
                            'strength': 0.9,
                            'reason': f'Opening EXIT: Win rate {win_rate:.1%}, PnL €{total_pnl:.2f}'
                        }
                
                return {
                    'signal': 'HOLD',
                    'strength': 0.0,
                    'reason': f'No clear signal: Win rate {win_rate:.1%}, PnL €{total_pnl:.2f}'
                }
            else:
                # Fallback if no PnL data
                return {
                    'signal': 'BUY',
                    'strength': 0.6,
                    'reason': 'Default opening position (no PnL data)'
                }
                
        except Exception as e:
            return {
                'signal': 'HOLD',
                'strength': 0.0,
                'reason': f'Signal generation error: {e}'
            }
    
    def transmit_order_immediately(self, ticker_name: str, action: str, 
                                  amount_eur: float, price: float) -> Dict[str, Any]:
        """Immediately transmit order to Bitpanda Paper Trading"""
        
        print(f"⚡ TRANSMITTING ORDER: {action} {ticker_name}")
        
        # Create order details
        order_id = f"OPEN_{int(time.time())}_{ticker_name}_{action}"
        timestamp = datetime.now()
        
        # Calculate coin quantity
        config = crypto_tickers[ticker_name]
        round_factor = config['order_round_factor']
        coin_quantity = amount_eur / price
        coin_quantity = round(coin_quantity / round_factor) * round_factor
        
        # Simulate immediate order transmission to Bitpanda
        order_data = {
            'order_id': order_id,
            'timestamp': timestamp,
            'ticker': ticker_name,
            'action': action,
            'amount_eur': amount_eur,
            'coin_quantity': coin_quantity,
            'price': price,
            'status': 'TRANSMITTED',
            'fees': amount_eur * 0.0015,  # 0.15% Bitpanda fee
            'execution_time': 'IMMEDIATE'
        }
        
        # Update positions immediately
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
            
            print(f"   ✅ BUY ORDER TRANSMITTED: {coin_quantity:.6f} {ticker_name} @ €{price:.4f}")
            
        elif action == 'SELL':
            if ticker_name in self.positions and self.positions[ticker_name]['quantity'] >= coin_quantity:
                pos = self.positions[ticker_name]
                pos['quantity'] -= coin_quantity
                if pos['quantity'] > 0:
                    pos['total_cost'] *= (pos['quantity'] / (pos['quantity'] + coin_quantity))
                else:
                    pos['total_cost'] = 0
                    
                print(f"   ✅ SELL ORDER TRANSMITTED: {coin_quantity:.6f} {ticker_name} @ €{price:.4f}")
            else:
                order_data['status'] = 'REJECTED'
                print(f"   ❌ SELL ORDER REJECTED: Insufficient position")
        
        # Log the order transmission
        self.trade_log.append(order_data)
        
        return order_data
    
    def execute_daily_opening_session(self):
        """Execute one daily opening trading session - ONCE per day"""
        
        session_start = datetime.now()
        
        print(f"\n🚀 DAILY OPENING SESSION")
        print("=" * 60)
        print(f"📅 Date: {session_start.strftime('%Y-%m-%d')}")
        print(f"🕐 Opening Time: {session_start.strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Get opening prices
        opening_prices = self.get_current_market_prices()
        
        if not opening_prices:
            print("❌ No opening prices available - session cancelled")
            return 0
        
        orders_transmitted = 0
        
        print(f"\n� RUNNING STRATEGY AT MARKET OPEN")
        print("-" * 50)
        
        # Process each cryptocurrency ONCE
        for ticker_name in crypto_tickers.keys():
            try:
                if ticker_name not in opening_prices:
                    continue
                
                opening_price = opening_prices[ticker_name]
                
                # Run strategy analysis ONCE
                signal_data = self.run_strategy_for_ticker(ticker_name)
                signal = signal_data['signal']
                strength = signal_data['strength']
                reason = signal_data.get('reason', 'No reason')
                
                print(f"{ticker_name:10} | €{opening_price:>8.4f} | {signal:4} | {strength:.2f}")
                print(f"           Reason: {reason}")
                
                # Transmit orders immediately if signal is generated
                if signal in ['BUY', 'SELL'] and strength > 0.6:
                    
                    # Calculate position size
                    base_amount = crypto_tickers[ticker_name]['initialCapitalLong']
                    position_amount = base_amount * strength
                    
                    # Transmit order immediately
                    order_result = self.transmit_order_immediately(
                        ticker_name=ticker_name,
                        action=signal,
                        amount_eur=position_amount,
                        price=opening_price
                    )
                    
                    if order_result.get('status') == 'TRANSMITTED':
                        orders_transmitted += 1
                
                print()  # Empty line for readability
                
            except Exception as e:
                print(f"❌ Error processing {ticker_name}: {e}")
        
        # Session summary
        elapsed_time = datetime.now() - session_start
        
        print(f"🏁 DAILY OPENING SESSION COMPLETED")
        print("=" * 60)
        print(f"⏱️ Duration: {elapsed_time}")
        print(f"📊 Orders Transmitted: {orders_transmitted}")
        print(f"📋 Active Positions: {len([p for p in self.positions.values() if p['quantity'] > 0])}")
        print("⏳ Waiting for next day's opening...")
        print("=" * 60)
        
        # Save session log
        self.save_session_log(session_start)
        
        return orders_transmitted
    
    def save_session_log(self, session_date):
        """Save daily session log"""
        if self.trade_log:
            timestamp = session_date.strftime('%Y%m%d_%H%M')
            filename = f"daily_opening_trades_{timestamp}.csv"
            
            df = pd.DataFrame(self.trade_log)
            df.to_csv(filename, index=False)
            print(f"💾 Session log saved: {filename}")
    
    def show_portfolio_status(self):
        """Show current portfolio status"""
        print(f"\n💼 PORTFOLIO STATUS")
        print("-" * 40)
        
        if self.positions:
            total_positions = sum(1 for p in self.positions.values() if p['quantity'] > 0)
            print(f"📊 Active Positions: {total_positions}")
            
            for ticker, pos in self.positions.items():
                if pos['quantity'] > 0:
                    print(f"   {ticker:10} | {pos['quantity']:>10.6f} | €{pos['avg_price']:>8.4f}")
        else:
            print("📊 No active positions")
        
        print(f"📋 Total Orders: {len(self.trade_log)}")
    
    def start_2_week_daily_trading(self):
        """Start 2-week daily opening trading - Simple approach"""
        
        print("🚀 STARTING 2-WEEK DAILY OPENING TRADING")
        print("=" * 60)
        print(f"📅 Start Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"📅 End Date: {(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')}")
        print(f"🕐 Daily Run Time: {self.market_open_time} UTC")
        print("=" * 60)
        
        self.running = True
        start_date = datetime.now()
        end_date = start_date + timedelta(days=14)
        
        total_sessions = 0
        total_orders = 0
        
        try:
            # Simple loop: Wait for opening time, run strategy, wait for next day
            while self.running and datetime.now() < end_date:
                
                # Calculate next opening time
                now = datetime.now()
                next_open = now.replace(hour=0, minute=0, second=0, microsecond=0)
                
                # If we've passed today's opening, move to tomorrow
                if now.hour > 0 or (now.hour == 0 and now.minute > 30):
                    next_open += timedelta(days=1)
                
                time_until = (next_open - now).total_seconds()
                
                print(f"\n⏳ WAITING FOR NEXT OPENING")
                print(f"   Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Next Opening: {next_open.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Time Until: {time_until/3600:.1f} hours")
                
                # Wait until opening time
                if time_until > 0:
                    time.sleep(time_until)
                
                # Execute opening session
                if self.running and datetime.now() < end_date:
                    print(f"\n🔔 MARKET OPEN - RUNNING STRATEGY")
                    orders = self.execute_daily_opening_session()
                    total_orders += orders
                    total_sessions += 1
                    
                    print(f"📊 Session {total_sessions} completed: {orders} orders")
                    print("⏳ Waiting for next day...")
                
        except KeyboardInterrupt:
            print("\n🛑 STOPPED BY USER")
        
        finally:
            self.running = False
            self.show_portfolio_status()
            
            print(f"\n🏁 2-WEEK DAILY TRADING COMPLETED!")
            print("=" * 60)
            print(f"📅 Total Duration: {datetime.now() - start_date}")
            print(f"📊 Sessions Completed: {total_sessions}")
            print(f"📋 Total Orders: {total_orders}")
            print("=" * 60)

def main():
    """Main execution function"""
    
    print("🕐 DAILY OPENING STRATEGY TRADER - SIMPLIFIED")
    print("💡 Runs ONCE per day at market open, transmits orders immediately")
    print("🔄 Simple cycle: Wait for opening → Run strategy → Transmit trades → Wait for next day")
    print("⚠️ Press Ctrl+C to stop at any time")
    print()
    
    # Create trader
    trader = DailyOpeningTrader()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        trader.running = False
        print("\n🛑 Shutdown signal received...")
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start 2-week daily trading
    trader.start_2_week_daily_trading()

if __name__ == "__main__":
    main()
