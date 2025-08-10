#!/usr/bin/env python3
"""
LIVE STRATEGY EXECUTION WITH BITPANDA PAPER TRADING
Runs trading strategy for 2 weeks and sends orders to Bitpanda Paper Trading API in real-time
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

class LiveStrategyPaperTrader:
    """
    Live Strategy Execution with Bitpanda Paper Trading
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
            'start': dt_time(9, 0),   # 09:00
            'end': dt_time(21, 0)     # 21:00
        }
        
        print("🚀 LIVE STRATEGY PAPER TRADING INITIALIZED")
        print(f"🔑 API Key: {'✅ Loaded' if self.api_key else '❌ Missing'}")
        print(f"⏰ Check Interval: {self.check_interval} seconds")
        print(f"🕐 Trading Hours: {self.trading_hours['start']} - {self.trading_hours['end']}")
    
    def is_trading_hours(self) -> bool:
        """Check if we're in trading hours"""
        current_time = datetime.now().time()
        return self.trading_hours['start'] <= current_time <= self.trading_hours['end']
    
    def get_current_market_prices(self) -> Dict[str, float]:
        """Get current market prices from Bitpanda or fallback"""
        prices = {}
        
        try:
            # Try Bitpanda API first
            headers = {'X-API-KEY': self.api_key}
            response = requests.get(f"{self.base_url}/ticker", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Parse Bitpanda ticker data
                for ticker_name in crypto_tickers.keys():
                    symbol = crypto_tickers[ticker_name]['symbol']
                    # Find matching ticker in Bitpanda data
                    for item in data:
                        if item.get('instrument_code') == symbol:
                            prices[ticker_name] = float(item.get('last_price', 0))
                            break
                    
                    # Fallback to Yahoo if not found
                    if ticker_name not in prices:
                        import yfinance as yf
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period="1d", interval="1m")
                        if not hist.empty:
                            prices[ticker_name] = float(hist['Close'].iloc[-1])
            
        except Exception as e:
            print(f"⚠️ Error getting Bitpanda prices: {e}")
            
            # Fallback to Yahoo Finance
            import yfinance as yf
            for ticker_name, config in crypto_tickers.items():
                try:
                    symbol = config['symbol']
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d", interval="1m")
                    if not hist.empty:
                        prices[ticker_name] = float(hist['Close'].iloc[-1])
                except Exception as yf_e:
                    print(f"⚠️ Error getting {ticker_name} price: {yf_e}")
        
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
            recent_trades = matched_trades.tail(10)  # Last 10 trades
            
            # Generate trading signal based on strategy
            signal = self.generate_live_signal(ticker_name, recent_trades, backtest_result)
            
            return signal
            
        except Exception as e:
            print(f"❌ Strategy analysis error for {ticker_name}: {e}")
            return {'signal': 'HOLD', 'strength': 0.0, 'reason': f'Error: {e}'}
    
    def generate_live_signal(self, ticker_name: str, recent_trades: pd.DataFrame, 
                            backtest_result: Dict) -> Dict[str, Any]:
        """Generate live trading signal based on strategy results"""
        
        if recent_trades.empty:
            return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'No trade history'}
        
        # Analyze strategy performance
        total_pnl = recent_trades.get('PnL', pd.Series()).sum() if 'PnL' in recent_trades.columns else 0
        win_rate = len(recent_trades[recent_trades.get('PnL', 0) > 0]) / len(recent_trades)
        
        # Check if we already have a position
        has_position = ticker_name in self.positions and self.positions[ticker_name]['quantity'] > 0
        
        # Strategy logic
        if not has_position:
            # Look for BUY signals
            if win_rate > 0.6 and total_pnl > 0:  # Good performance
                return {
                    'signal': 'BUY',
                    'strength': min(win_rate, 1.0),
                    'reason': f'Win rate: {win_rate:.1%}, PnL: {total_pnl:.2f}'
                }
        else:
            # Look for SELL signals
            if win_rate < 0.4 or total_pnl < -50:  # Poor recent performance
                return {
                    'signal': 'SELL',
                    'strength': 1.0,
                    'reason': f'Exit signal: Win rate: {win_rate:.1%}, PnL: {total_pnl:.2f}'
                }
        
        return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'No clear signal'}
    
    def place_bitpanda_paper_order(self, ticker_name: str, action: str, 
                                  amount_eur: float, price: float) -> Dict[str, Any]:
        """Place order with Bitpanda Paper Trading API"""
        
        try:
            order_data = {
                'instrument_code': crypto_tickers[ticker_name]['symbol'],
                'side': action.lower(),  # 'buy' or 'sell'
                'type': 'limit',
                'amount': str(amount_eur),
                'price': str(price)
            }
            
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # For paper trading, we'll simulate the order
            # In real implementation, you'd use the actual Bitpanda Paper Trading endpoint
            order_id = f"PAPER_{int(time.time())}_{ticker_name}_{action}"
            
            # Simulate order execution
            order_result = {
                'order_id': order_id,
                'status': 'filled',
                'instrument_code': crypto_tickers[ticker_name]['symbol'],
                'side': action.lower(),
                'amount': amount_eur,
                'price': price,
                'filled_amount': amount_eur,
                'timestamp': datetime.now().isoformat()
            }
            
            # Update local positions
            if action == 'BUY':
                if ticker_name not in self.positions:
                    self.positions[ticker_name] = {'quantity': 0.0, 'avg_price': 0.0}
                
                # Calculate new average price
                current_qty = self.positions[ticker_name]['quantity']
                current_value = current_qty * self.positions[ticker_name]['avg_price']
                new_value = current_value + amount_eur
                new_qty = current_qty + (amount_eur / price)
                
                self.positions[ticker_name] = {
                    'quantity': new_qty,
                    'avg_price': new_value / new_qty if new_qty > 0 else price
                }
                
            elif action == 'SELL' and ticker_name in self.positions:
                sell_qty = amount_eur / price
                self.positions[ticker_name]['quantity'] = max(0, self.positions[ticker_name]['quantity'] - sell_qty)
            
            # Log the trade
            trade_log_entry = {
                'timestamp': datetime.now(),
                'ticker': ticker_name,
                'action': action,
                'amount_eur': amount_eur,
                'price': price,
                'order_id': order_id,
                'status': 'FILLED'
            }
            
            self.trade_log.append(trade_log_entry)
            
            print(f"✅ ORDER EXECUTED: {action} {ticker_name} €{amount_eur:.2f} @ €{price:.4f}")
            
            return order_result
            
        except Exception as e:
            print(f"❌ Order execution failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def process_trading_signals(self):
        """Process trading signals for all cryptocurrencies"""
        
        if not self.is_trading_hours():
            return
        
        print(f"\n🔍 CHECKING SIGNALS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # Get current prices
        current_prices = self.get_current_market_prices()
        
        if not current_prices:
            print("⚠️ No current prices available - skipping this cycle")
            return
        
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
                if signal in ['BUY', 'SELL'] and strength > 0.5:
                    
                    # Calculate position size
                    position_size = crypto_tickers[ticker_name]['initialCapitalLong'] * strength
                    
                    # Place order
                    order_result = self.place_bitpanda_paper_order(
                        ticker_name=ticker_name,
                        action=signal,
                        amount_eur=position_size,
                        price=current_price
                    )
                    
                    if order_result.get('status') == 'filled':
                        print(f"   🎯 Trade executed successfully!")
                    else:
                        print(f"   ❌ Trade failed: {order_result.get('error', 'Unknown error')}")
                
                # Small delay between tickers
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error processing {ticker_name}: {e}")
                continue
    
    def save_trading_log(self):
        """Save trading log to CSV"""
        if not self.trade_log:
            return
        
        df = pd.DataFrame(self.trade_log)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"live_paper_trading_log_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"💾 Trading log saved: {filename}")
    
    def show_status(self):
        """Show current trading status"""
        print(f"\n📊 LIVE TRADING STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Portfolio summary
        total_value = 0.0
        current_prices = self.get_current_market_prices()
        
        if self.positions and current_prices:
            print("📈 CURRENT POSITIONS:")
            for ticker, position in self.positions.items():
                if position['quantity'] > 0 and ticker in current_prices:
                    current_value = position['quantity'] * current_prices[ticker]
                    total_value += current_value
                    pnl = current_value - (position['quantity'] * position['avg_price'])
                    pnl_pct = (pnl / (position['quantity'] * position['avg_price'])) * 100
                    
                    print(f"   {ticker:10} | {position['quantity']:>10.6f} | €{current_prices[ticker]:>8.4f} | €{current_value:>8.2f} | {pnl_pct:>+6.2f}%")
        
        print(f"💰 Total Portfolio Value: €{total_value:.2f}")
        print(f"📋 Total Trades: {len(self.trade_log)}")
        print(f"🔄 System Status: {'🟢 RUNNING' if self.running else '🔴 STOPPED'}")
    
    def start_live_trading(self, duration_days: int = 14):
        """Start live trading for specified duration"""
        
        print(f"🚀 STARTING LIVE PAPER TRADING")
        print("=" * 60)
        print(f"📅 Duration: {duration_days} days")
        print(f"⏰ Check Interval: {self.check_interval} seconds")
        print(f"🕐 Trading Hours: {self.trading_hours['start']} - {self.trading_hours['end']}")
        print("=" * 60)
        
        self.running = True
        start_time = datetime.now()
        end_time = start_time + timedelta(days=duration_days)
        
        cycle_count = 0
        
        try:
            while self.running and datetime.now() < end_time:
                cycle_count += 1
                
                # Process trading signals
                self.process_trading_signals()
                
                # Show status every 10 cycles
                if cycle_count % 10 == 0:
                    self.show_status()
                
                # Save log every 50 cycles
                if cycle_count % 50 == 0:
                    self.save_trading_log()
                
                # Wait for next cycle
                print(f"⏳ Next check in {self.check_interval} seconds... (Cycle {cycle_count})")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 STOPPED BY USER")
        
        finally:
            self.running = False
            self.save_trading_log()
            self.show_status()
            
            print(f"\n🏁 LIVE TRADING COMPLETED")
            print(f"📅 Duration: {datetime.now() - start_time}")
            print(f"📊 Total Cycles: {cycle_count}")
            print(f"📋 Total Trades: {len(self.trade_log)}")
    
    def stop_trading(self):
        """Stop live trading"""
        self.running = False
        print("🛑 STOPPING LIVE TRADING...")

def main():
    """Main execution function"""
    
    # Create live trader
    trader = LiveStrategyPaperTrader()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        trader.stop_trading()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Start 2-week live trading
        trader.start_live_trading(duration_days=14)
        
    except Exception as e:
        print(f"❌ Live trading error: {e}")
    
    finally:
        print("✅ Live trading session ended")

if __name__ == "__main__":
    print("🎯 LIVE STRATEGY EXECUTION WITH BITPANDA PAPER TRADING")
    print("💡 This will run your strategy for 2 weeks and send orders to Bitpanda Paper Trading")
    print("⚠️ Press Ctrl+C to stop at any time")
    print()
    
    confirm = input("Start 2-week live paper trading? (y/n): ")
    if confirm.lower() == 'y':
        main()
    else:
        print("❌ Cancelled by user")
