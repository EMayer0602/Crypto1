#!/usr/bin/env python3
"""
2-WEEK PAPER TRADING WITH STRATEGY SIGNALS
Comprehensive paper trading simulation using real strategy signals
"""

import sys
import os
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import existing modules
from bitpanda_fusion_adapter import BitpandaFusionPaperTrader
from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

class StrategySignalPaperTrading:
    """
    2-Week Paper Trading with Strategy-Generated Signals
    """
    
    def __init__(self, start_date: str = None, days: int = 14):
        """
        Initialize the strategy-based paper trader
        
        Args:
            start_date: Start date for simulation (YYYY-MM-DD)
            days: Number of days to simulate (default: 14)
        """
        self.paper_trader = BitpandaFusionPaperTrader(sandbox=True)
        self.simulation_days = days
        
        # Set simulation period
        if start_date:
            self.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            # Default: Start 14 days ago from today
            self.start_date = (datetime.now() - timedelta(days=days)).date()
        
        self.end_date = self.start_date + timedelta(days=days)
        
        # Tracking
        self.daily_signals = {}
        self.daily_portfolio_values = {}
        self.strategy_performance = {}
        
        print(f"🚀 STRATEGY-BASED PAPER TRADING INITIALIZED")
        print(f"📅 Period: {self.start_date} to {self.end_date}")
        print(f"⏱️ Duration: {days} days")
        print(f"💰 Starting Capital: €16,000")
    
    def generate_strategy_signals(self, date: datetime.date, ticker: str) -> Dict[str, Any]:
        """
        Generate trading signals using the backtesting strategy
        
        Args:
            date: Date for signal generation
            ticker: Cryptocurrency ticker (e.g., "BTC-EUR")
        
        Returns:
            Dict with signal information
        """
        
        try:
            # Get ticker configuration
            if ticker not in crypto_tickers:
                return {'action': 'HOLD', 'strength': 0.0, 'reason': 'Ticker not configured'}
            
            config = crypto_tickers[ticker]
            symbol = config['symbol']
            
            # Run backtest up to the current date
            backtest_result = run_backtest(symbol, config, end_date=date)
            
            if not backtest_result or not backtest_result.get('matched_trades'):
                return {'action': 'HOLD', 'strength': 0.0, 'reason': 'No backtest results'}
            
            # Analyze recent trades for signal generation
            matched_trades = backtest_result['matched_trades']
            
            # Look at the most recent signals
            recent_trades = matched_trades.tail(10)  # Last 10 trades
            
            # Generate signal based on strategy logic
            signal = self.analyze_backtest_for_signal(ticker, recent_trades, date)
            
            return signal
            
        except Exception as e:
            return {'action': 'HOLD', 'strength': 0.0, 'reason': f'Error: {str(e)}'}
    
    def analyze_backtest_for_signal(self, ticker: str, recent_trades: pd.DataFrame, date: datetime.date) -> Dict[str, Any]:
        """
        Analyze backtest results to generate trading signals
        """
        
        if recent_trades.empty:
            return {'action': 'HOLD', 'strength': 0.0, 'reason': 'No recent trades'}
        
        # Strategy logic for signal generation
        try:
            # Check if we should be in a position based on recent signals
            last_trade = recent_trades.iloc[-1]
            
            # Look for entry/exit patterns
            if 'signal' in recent_trades.columns:
                last_signal = last_trade['signal']
                
                if last_signal == 'BUY' or last_signal == 1:
                    # Strong buy signal
                    return {
                        'action': 'BUY',
                        'strength': 0.8,
                        'reason': 'Strategy generated BUY signal',
                        'target_price': last_trade.get('Close', 0),
                        'stop_loss': last_trade.get('Close', 0) * 0.95  # 5% stop loss
                    }
                
                elif last_signal == 'SELL' or last_signal == -1:
                    # Strong sell signal
                    return {
                        'action': 'SELL',
                        'strength': 0.8,
                        'reason': 'Strategy generated SELL signal',
                        'target_price': last_trade.get('Close', 0)
                    }
            
            # Alternative: Look at recent performance
            if 'PnL' in recent_trades.columns:
                recent_pnl = recent_trades['PnL'].tail(5).mean()
                
                if recent_pnl > 0:
                    # Recent trades profitable - continue strategy
                    return {
                        'action': 'BUY',
                        'strength': 0.6,
                        'reason': f'Recent PnL positive: {recent_pnl:.2f}%'
                    }
                elif recent_pnl < -2:
                    # Recent losses - exit positions
                    return {
                        'action': 'SELL',
                        'strength': 0.7,
                        'reason': f'Recent PnL negative: {recent_pnl:.2f}%'
                    }
            
            # Default: Look at price momentum
            if 'Close' in recent_trades.columns:
                price_trend = recent_trades['Close'].pct_change().tail(3).mean()
                
                if price_trend > 0.02:  # 2% upward trend
                    return {
                        'action': 'BUY',
                        'strength': 0.5,
                        'reason': f'Price momentum positive: {price_trend:.3f}'
                    }
                elif price_trend < -0.02:  # 2% downward trend
                    return {
                        'action': 'SELL',
                        'strength': 0.5,
                        'reason': f'Price momentum negative: {price_trend:.3f}'
                    }
            
        except Exception as e:
            print(f"   ⚠️ Signal analysis error for {ticker}: {e}")
        
        return {'action': 'HOLD', 'strength': 0.0, 'reason': 'No clear signal'}
    
    def get_historical_prices(self, ticker: str, date: datetime.date) -> Dict[str, float]:
        """
        Get historical prices for a specific date
        """
        csv_file = f"{ticker}_daily.csv"
        
        if not os.path.exists(csv_file):
            print(f"❌ No historical data for {ticker}")
            return {}
        
        try:
            df = pd.read_csv(csv_file)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            
            # Find the exact date or closest date
            date_mask = df['Date'] == date
            
            if date_mask.any():
                row = df[date_mask].iloc[0]
                return {
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume'])
                }
            else:
                # Find closest date before the target date
                available_dates = df[df['Date'] <= date]['Date']
                if not available_dates.empty:
                    closest_date = available_dates.max()
                    row = df[df['Date'] == closest_date].iloc[0]
                    return {
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': float(row['Volume'])
                    }
        
        except Exception as e:
            print(f"❌ Error getting prices for {ticker} on {date}: {e}")
        
        return {}
    
    def simulate_trading_day(self, current_date: datetime.date) -> Dict[str, Any]:
        """
        Simulate one day of strategy-based trading
        """
        
        print(f"\n📅 SIMULATING TRADING DAY: {current_date}")
        print("-" * 50)
        
        day_results = {
            'date': current_date,
            'signals': {},
            'trades': [],
            'portfolio_value': 0.0,
            'daily_pnl': 0.0
        }
        
        current_prices = {}
        
        # Process each cryptocurrency
        for ticker_name, config in crypto_tickers.items():
            
            # Get historical price for this date
            historical_prices = self.get_historical_prices(ticker_name, current_date)
            
            if not historical_prices:
                print(f"   ⚠️ No price data for {ticker_name} on {current_date}")
                continue
            
            # Use closing price as the trading price
            current_price = historical_prices['close']
            current_prices[ticker_name] = current_price
            
            # Generate strategy signal
            signal = self.generate_strategy_signals(current_date, ticker_name)
            day_results['signals'][ticker_name] = signal
            
            print(f"   📊 {ticker_name}: €{current_price:.4f} | Signal: {signal['action']} ({signal['strength']:.1f})")
            print(f"      💡 Reason: {signal['reason']}")
            
            # Execute trades based on signals
            if signal['action'] == 'BUY' and signal['strength'] > 0.5:
                
                # Calculate position size based on signal strength
                base_position = 1000  # Base position size
                position_size = base_position * signal['strength']
                
                order_result = self.paper_trader.place_paper_order(
                    ticker_name=ticker_name,
                    action='BUY',
                    quantity=position_size,
                    price=current_price,
                    order_type='MARKET'
                )
                
                if order_result['status'] == 'FILLED':
                    day_results['trades'].append(order_result)
                    print(f"      ✅ BUY executed: €{position_size:.2f} @ €{current_price:.4f}")
                
            elif signal['action'] == 'SELL' and signal['strength'] > 0.5:
                
                # Check if we have a position to sell
                if ticker_name in self.paper_trader.paper_portfolio['positions']:
                    position = self.paper_trader.paper_portfolio['positions'][ticker_name]
                    
                    if position['quantity'] > 0:
                        sell_value = position['quantity'] * current_price
                        
                        order_result = self.paper_trader.place_paper_order(
                            ticker_name=ticker_name,
                            action='SELL',
                            quantity=sell_value,
                            price=current_price,
                            order_type='MARKET'
                        )
                        
                        if order_result['status'] == 'FILLED':
                            day_results['trades'].append(order_result)
                            print(f"      ✅ SELL executed: €{sell_value:.2f} @ €{current_price:.4f}")
        
        # Calculate daily portfolio value
        portfolio_value = self.paper_trader.get_portfolio_value(current_prices)
        day_results['portfolio_value'] = portfolio_value['total_value']
        
        # Calculate daily P&L
        if hasattr(self, 'previous_day_value'):
            day_results['daily_pnl'] = portfolio_value['total_value'] - self.previous_day_value
        else:
            day_results['daily_pnl'] = portfolio_value['total_value'] - 16000  # vs starting capital
        
        self.previous_day_value = portfolio_value['total_value']
        
        print(f"   💰 Portfolio Value: €{portfolio_value['total_value']:,.2f}")
        print(f"   📊 Daily P&L: €{day_results['daily_pnl']:+,.2f}")
        
        return day_results
    
    def run_2week_simulation(self) -> Dict[str, Any]:
        """
        Run the complete 2-week paper trading simulation
        """
        
        print("🚀 STARTING 2-WEEK STRATEGY-BASED PAPER TRADING SIMULATION")
        print("=" * 70)
        
        simulation_results = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'daily_results': [],
            'total_trades': 0,
            'final_portfolio': {},
            'performance_summary': {}
        }
        
        # Simulate each trading day
        current_date = self.start_date
        
        while current_date < self.end_date:
            # Skip weekends (optional - crypto trades 24/7, but for simulation)
            if current_date.weekday() < 7:  # Include all days for crypto
                
                day_result = self.simulate_trading_day(current_date)
                simulation_results['daily_results'].append(day_result)
                simulation_results['total_trades'] += len(day_result['trades'])
            
            current_date += timedelta(days=1)
            time.sleep(0.1)  # Small delay between days
        
        # Final portfolio analysis
        final_prices = {}
        for ticker_name in crypto_tickers.keys():
            historical_prices = self.get_historical_prices(ticker_name, self.end_date - timedelta(days=1))
            if historical_prices:
                final_prices[ticker_name] = historical_prices['close']
        
        final_portfolio = self.paper_trader.get_portfolio_value(final_prices)
        simulation_results['final_portfolio'] = final_portfolio
        
        # Performance summary
        starting_capital = 16000.0
        final_value = final_portfolio['total_value']
        total_return = final_value - starting_capital
        total_return_pct = (total_return / starting_capital) * 100
        
        simulation_results['performance_summary'] = {
            'starting_capital': starting_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': simulation_results['total_trades'],
            'daily_avg_return': total_return / self.simulation_days
        }
        
        # Generate comprehensive report
        self.generate_simulation_report(simulation_results)
        
        return simulation_results
    
    def generate_simulation_report(self, results: Dict[str, Any]) -> None:
        """
        Generate comprehensive simulation report
        """
        
        print(f"\n🎯 2-WEEK STRATEGY PAPER TRADING REPORT")
        print("=" * 70)
        
        perf = results['performance_summary']
        
        print(f"📅 Simulation Period: {results['start_date']} to {results['end_date']}")
        print(f"⏱️ Duration: {self.simulation_days} days")
        print(f"📊 Total Trades: {perf['total_trades']}")
        
        print(f"\n💰 PERFORMANCE SUMMARY:")
        print(f"   Starting Capital: €{perf['starting_capital']:,.2f}")
        print(f"   Final Value: €{perf['final_value']:,.2f}")
        print(f"   Total Return: €{perf['total_return']:+,.2f}")
        print(f"   Total Return %: {perf['total_return_pct']:+.2f}%")
        print(f"   Avg Daily Return: €{perf['daily_avg_return']:+.2f}")
        
        # Daily performance chart
        print(f"\n📈 DAILY PERFORMANCE:")
        print("-" * 50)
        print(f"{'Date':12} | {'Value':>12} | {'Daily P&L':>12} | {'Trades':>7}")
        print("-" * 50)
        
        for day_result in results['daily_results']:
            date_str = day_result['date'].strftime('%Y-%m-%d')
            value = day_result['portfolio_value']
            pnl = day_result['daily_pnl']
            trades = len(day_result['trades'])
            
            print(f"{date_str} | €{value:>11,.2f} | €{pnl:>+10.2f} | {trades:>7}")
        
        # Save detailed report to CSV
        self.save_simulation_csv(results)
        
        print(f"\n✅ SIMULATION COMPLETED")
        print(f"📁 Detailed report saved to CSV")
        print("=" * 70)
    
    def save_simulation_csv(self, results: Dict[str, Any]) -> None:
        """
        Save simulation results to CSV
        """
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"strategy_paper_trading_2week_{timestamp}.csv"
        
        # Prepare data for CSV
        csv_data = []
        
        for day_result in results['daily_results']:
            for trade in day_result['trades']:
                csv_data.append({
                    'Date': day_result['date'],
                    'Ticker': trade['ticker'],
                    'Action': trade['action'],
                    'Quantity': trade['quantity_coins'],
                    'Price': trade['price'],
                    'Value': trade['quantity_eur'],
                    'Fees': trade['fees'],
                    'Portfolio_Value': day_result['portfolio_value'],
                    'Daily_PnL': day_result['daily_pnl']
                })
        
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False)
            print(f"📊 Simulation data saved: {filename}")

def main():
    """Main execution function"""
    
    print("🎯 STRATEGY-BASED 2-WEEK PAPER TRADING")
    print("=" * 50)
    
    # You can customize these parameters
    start_date = None  # Use None for automatic (14 days ago)
    simulation_days = 14
    
    # Create and run simulation
    simulator = StrategySignalPaperTrading(start_date=start_date, days=simulation_days)
    results = simulator.run_2week_simulation()
    
    print(f"\n🎉 2-WEEK SIMULATION COMPLETED!")
    print(f"📊 Final Return: {results['performance_summary']['total_return_pct']:+.2f}%")

if __name__ == "__main__":
    main()
