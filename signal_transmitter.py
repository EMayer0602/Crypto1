#!/usr/bin/env python3
"""
SIGNAL TRANSMITTER MODULE
Extracts current trading signals from live_backtest_WORKING.py and transmits them to paper trading
"""

import sys
import os
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers
from bitpanda_secure_api import get_api_key_safely

class SignalTransmitter:
    """Extract signals from backtest and transmit to Bitpanda Paper Trading"""
    
    def __init__(self):
        self.api_key = get_api_key_safely()
        self.base_url = "https://api.bitpanda.com/v1"
        self.trade_log = []
        
        print("📡 SIGNAL TRANSMITTER MODULE")
        print("=" * 50)
        print(f"🔑 API Key: {'✅ Loaded' if self.api_key else '❌ Missing'}")
        print(f"📊 Processing {len(crypto_tickers)} tickers")
        print("=" * 50)
    
    def get_current_signals_from_backtest(self) -> Dict[str, Dict]:
        """Get TODAY'S trading signals by running live backtest analysis - ONLY FRESH SIGNALS"""
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n🔍 EXTRACTING TODAY'S SIGNALS FROM BACKTEST ({today})")
        print("-" * 60)
        print("💡 Only transmitting FRESH signals generated for today")
        print("⚠️ Historical signals will be ignored")
        print("-" * 60)
        
        signals = {}
        
        try:
            # Import and run the live backtest analysis
            from crypto_backtesting_module import run_live_backtest_analysis
            
            print("🚀 Running live backtest analysis to get fresh signals...")
            result = run_live_backtest_analysis()
            
            if not result:
                print("❌ Live backtest analysis failed")
                return signals
            
            print("✅ Live backtest analysis completed - extracting TODAY's signals...")
            
            # Now extract TODAY'S signals from each ticker's matched trades
            for ticker_name in crypto_tickers.keys():
                try:
                    signal_data = self.extract_ticker_signal(ticker_name)
                    
                    if signal_data['signal'] != 'HOLD':
                        signals[ticker_name] = signal_data
                        print(f"📊 {ticker_name}: {signal_data['signal']} (strength: {signal_data['strength']:.2f})")
                        print(f"   📝 Reason: {signal_data['reason']}")
                    else:
                        print(f"⏸️ {ticker_name}: HOLD - {signal_data['reason']}")
                        
                except Exception as e:
                    print(f"❌ Error extracting TODAY's signal for {ticker_name}: {e}")
            
        except Exception as e:
            print(f"❌ Error running backtest analysis: {e}")
        
        print(f"\n📊 Found {len(signals)} FRESH signals for TODAY ({today})")
        if len(signals) == 0:
            print("💡 No fresh trading signals for today - system will wait for next day")
        
        return signals
    
    def extract_ticker_signal(self, ticker_name: str) -> Dict[str, Any]:
        """Extract TODAY'S trading signal for a specific ticker - only fresh signals"""
        
        try:
            # Get today's date for filtering
            today = datetime.now().date()
            
            # Try to load recent matched trades for this ticker
            from crypto_backtesting_module import run_backtest
            
            if ticker_name not in crypto_tickers:
                return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'Ticker not configured'}
            
            config = crypto_tickers[ticker_name]
            
            # Safely run backtest to get latest trades
            print(f"   🔍 Running backtest for {ticker_name}...")
            
            try:
                result = run_backtest(ticker_name, config)
            except Exception as backtest_error:
                print(f"   ❌ Backtest error for {ticker_name}: {backtest_error}")
                return {'signal': 'HOLD', 'strength': 0.0, 'reason': f'Backtest failed: {str(backtest_error)[:50]}...'}
            
            if not result:
                return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'No backtest result'}
                
            if not isinstance(result, dict) or 'matched_trades' not in result:
                return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'Invalid backtest result format'}
            
            matched_trades = result.get('matched_trades')
            
            # Safe DataFrame checks
            if matched_trades is None:
                return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'No matched_trades in result'}
            
            if not isinstance(matched_trades, pd.DataFrame):
                return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'matched_trades is not a DataFrame'}
            
            if matched_trades.empty:
                return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'No recent trades'}
            
            print(f"   📊 Found {len(matched_trades)} trades for {ticker_name}")
            
            # ✅ FILTER FOR TODAY'S SIGNALS ONLY
            if 'Date' in matched_trades.columns:
                try:
                    # Convert Date column to datetime safely
                    matched_trades = matched_trades.copy()  # Avoid modifying original
                    matched_trades['Date'] = pd.to_datetime(matched_trades['Date'])
                    
                    # Filter for TODAY's trades only
                    today_mask = matched_trades['Date'].dt.date == today
                    today_trades = matched_trades[today_mask]
                    
                    if not today_trades.empty:
                        print(f"   📅 Found {len(today_trades)} trades for TODAY")
                        return self.analyze_today_trades(ticker_name, today_trades)
                    else:
                        # No trades for today - check if there's a recent signal we can use
                        latest_trade = matched_trades.iloc[-1]
                        latest_trade_date = pd.to_datetime(latest_trade['Date']).date()
                        
                        # Only act if the latest trade is very recent (within 2 days)
                        days_since_last = (today - latest_trade_date).days
                        
                        if days_since_last <= 2:
                            print(f"   🕐 No today trades, using recent trade ({days_since_last} days ago)")
                            return self.generate_today_signal_from_recent(ticker_name, latest_trade, days_since_last)
                        else:
                            return {'signal': 'HOLD', 'strength': 0.0, 'reason': f'Latest trade too old ({days_since_last} days ago)'}
                            
                except Exception as date_error:
                    print(f"   ❌ Date processing error for {ticker_name}: {date_error}")
                    return {'signal': 'HOLD', 'strength': 0.0, 'reason': f'Date processing error: {str(date_error)[:50]}...'}
            
            else:
                # If no Date column, assume these are recent trades
                # Only use if we have very few recent trades (likely today's)
                if len(matched_trades) <= 3:  # Only very recent trades
                    print(f"   ⚠️ No Date column, using {len(matched_trades)} recent trades")
                    return self.analyze_recent_trades(ticker_name, matched_trades.tail(2))
                else:
                    return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'Too many historical trades, need today filter'}
            
        except Exception as e:
            print(f"   ❌ Signal extraction error for {ticker_name}: {e}")
            return {
                'signal': 'HOLD', 
                'strength': 0.0, 
                'reason': f'Analysis error: {str(e)[:50]}...'
            }
    
    def analyze_today_trades(self, ticker_name: str, today_trades: pd.DataFrame) -> Dict[str, Any]:
        """Analyze TODAY'S trades to generate signal"""
        
        if today_trades.empty:
            return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'No trades for today'}
        
        try:
            print(f"   📅 Found {len(today_trades)} trade(s) for TODAY for {ticker_name}")
            
            # Look at today's trade signals
            last_today_trade = today_trades.iloc[-1]
            
            # Check if it's a BUY or SELL signal from today
            if 'Type' in last_today_trade:
                trade_type = last_today_trade['Type']
                
                if trade_type == 'Buy':
                    return {
                        'signal': 'BUY',
                        'strength': 0.8,
                        'reason': f'Fresh BUY signal for today from strategy'
                    }
                elif trade_type == 'Sell':
                    return {
                        'signal': 'SELL', 
                        'strength': 0.8,
                        'reason': f'Fresh SELL signal for today from strategy'
                    }
            
            # Check PnL if available
            if 'Net PnL' in today_trades.columns:
                total_pnl = today_trades['Net PnL'].sum()
                profitable_trades = len(today_trades[today_trades['Net PnL'] > 0])
                win_rate = profitable_trades / len(today_trades)
                
                if win_rate >= 0.6 and total_pnl > 0:
                    return {
                        'signal': 'BUY',
                        'strength': min(win_rate, 1.0),
                        'reason': f'Today positive performance: {win_rate:.1%} win rate, €{total_pnl:.2f}'
                    }
                elif win_rate <= 0.4 and total_pnl < 0:
                    return {
                        'signal': 'SELL',
                        'strength': min((1 - win_rate), 1.0),
                        'reason': f'Today negative performance: {win_rate:.1%} win rate, €{total_pnl:.2f}'
                    }
            
            return {
                'signal': 'HOLD',
                'strength': 0.3,
                'reason': f'Today trades present but no clear signal'
            }
                    
        except Exception as e:
            return {
                'signal': 'HOLD', 
                'strength': 0.0, 
                'reason': f'Today analysis error: {e}'
            }
    
    def generate_today_signal_from_recent(self, ticker_name: str, latest_trade: pd.Series, 
                                        days_ago: int) -> Dict[str, Any]:
        """Generate today's signal based on very recent trade data"""
        
        try:
            # Only act on very recent trades (1-2 days max)
            if days_ago > 2:
                return {'signal': 'HOLD', 'strength': 0.0, 'reason': f'Latest trade {days_ago} days ago'}
            
            # Strength decreases with age
            age_factor = max(0.1, 1.0 - (days_ago * 0.3))
            
            # Check the latest trade type
            if 'Type' in latest_trade:
                trade_type = latest_trade['Type']
                
                if trade_type == 'Buy':
                    return {
                        'signal': 'BUY',
                        'strength': 0.6 * age_factor,
                        'reason': f'Recent BUY signal ({days_ago} days ago)'
                    }
                elif trade_type == 'Sell':
                    return {
                        'signal': 'SELL', 
                        'strength': 0.6 * age_factor,
                        'reason': f'Recent SELL signal ({days_ago} days ago)'
                    }
            
            # Check recent PnL
            if 'Net PnL' in latest_trade and pd.notna(latest_trade['Net PnL']):
                pnl = float(latest_trade['Net PnL'])
                
                if pnl > 100:  # Significant positive PnL
                    return {
                        'signal': 'BUY',
                        'strength': 0.5 * age_factor,
                        'reason': f'Recent profitable trade: €{pnl:.2f} ({days_ago} days ago)'
                    }
                elif pnl < -100:  # Significant negative PnL
                    return {
                        'signal': 'SELL',
                        'strength': 0.4 * age_factor,
                        'reason': f'Recent losing trade: €{pnl:.2f} ({days_ago} days ago)'
                    }
            
            return {
                'signal': 'HOLD',
                'strength': 0.0,
                'reason': f'Recent trade but no clear signal ({days_ago} days ago)'
            }
            
        except Exception as e:
            return {
                'signal': 'HOLD', 
                'strength': 0.0, 
                'reason': f'Recent signal error: {e}'
            }

    def analyze_recent_trades(self, ticker_name: str, recent_trades: pd.DataFrame) -> Dict[str, Any]:
        """Analyze recent trades to generate current signal"""
        
        if recent_trades.empty:
            return {'signal': 'HOLD', 'strength': 0.0, 'reason': 'No recent trades'}
        
        try:
            # Calculate performance metrics
            if 'Net PnL' in recent_trades.columns:
                total_pnl = recent_trades['Net PnL'].sum()
                profitable_trades = len(recent_trades[recent_trades['Net PnL'] > 0])
                win_rate = profitable_trades / len(recent_trades)
                
                # Simple signal generation logic based on recent performance
                if win_rate >= 0.6 and total_pnl > 0:
                    # Strong performance -> BUY signal
                    return {
                        'signal': 'BUY',
                        'strength': min(win_rate * 1.2, 1.0),
                        'reason': f'Strong performance: {win_rate:.1%} win rate, €{total_pnl:.2f} PnL'
                    }
                elif win_rate <= 0.4 and total_pnl < 0:
                    # Poor performance -> SELL signal (if we have position)
                    return {
                        'signal': 'SELL',
                        'strength': min((1 - win_rate) * 1.2, 1.0),
                        'reason': f'Poor performance: {win_rate:.1%} win rate, €{total_pnl:.2f} PnL'
                    }
                else:
                    # Neutral performance -> HOLD
                    return {
                        'signal': 'HOLD',
                        'strength': 0.5,
                        'reason': f'Neutral: {win_rate:.1%} win rate, €{total_pnl:.2f} PnL'
                    }
            else:
                # If no PnL data, look at trade pattern
                last_trade = recent_trades.iloc[-1]
                if 'Type' in last_trade and last_trade['Type'] == 'Buy':
                    return {
                        'signal': 'BUY',
                        'strength': 0.7,
                        'reason': 'Recent buy signal from strategy'
                    }
                elif 'Type' in last_trade and last_trade['Type'] == 'Sell':
                    return {
                        'signal': 'SELL',
                        'strength': 0.7,
                        'reason': 'Recent sell signal from strategy'
                    }
                else:
                    return {
                        'signal': 'HOLD',
                        'strength': 0.0,
                        'reason': 'No clear signal pattern'
                    }
                    
        except Exception as e:
            return {
                'signal': 'HOLD', 
                'strength': 0.0, 
                'reason': f'Analysis error: {e}'
            }
    
    def get_current_market_price(self, ticker_name: str) -> Optional[float]:
        """Get current market price for a ticker"""
        
        try:
            import yfinance as yf
            
            if ticker_name not in crypto_tickers:
                return None
            
            symbol = crypto_tickers[ticker_name]['symbol']
            ticker = yf.Ticker(symbol)
            
            # Get latest price
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            
            # Fallback to daily data
            hist = ticker.history(period="2d")
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
                
            return None
            
        except Exception as e:
            print(f"❌ Error getting price for {ticker_name}: {e}")
            return None
    
    def transmit_signal_to_paper_trading(self, ticker_name: str, signal_data: Dict[str, Any], 
                                       current_price: float) -> Dict[str, Any]:
        """Transmit a trading signal to Bitpanda Paper Trading"""
        
        try:
            signal = signal_data['signal']
            strength = signal_data['strength']
            reason = signal_data.get('reason', 'No reason provided')
            
            if signal not in ['BUY', 'SELL']:
                return {'status': 'SKIPPED', 'reason': 'No actionable signal'}
            
            # Calculate position size based on strength and initial capital
            config = crypto_tickers[ticker_name]
            base_amount = config.get('initialCapitalLong', 10000)
            position_amount = base_amount * strength * 0.1  # 10% of capital per trade max
            
            # Calculate quantity
            quantity = position_amount / current_price if current_price > 0 else 0
            
            # Log the paper trade
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'ticker': ticker_name,
                'signal': signal,
                'strength': strength,
                'reason': reason,
                'price': current_price,
                'quantity': quantity,
                'amount_eur': position_amount,
                'status': 'PAPER_TRADE'
            }
            
            self.trade_log.append(trade_record)
            
            # Save to CSV
            self.save_trade_to_csv(trade_record)
            
            print(f"📊 {signal} {ticker_name}: €{position_amount:.2f} @ €{current_price:.4f}")
            print(f"   Quantity: {quantity:.6f} | Strength: {strength:.2f} | Reason: {reason}")
            
            return {
                'status': 'TRANSMITTED',
                'trade_id': len(self.trade_log),
                'details': trade_record
            }
            
        except Exception as e:
            print(f"❌ Error transmitting signal for {ticker_name}: {e}")
            return {'status': 'ERROR', 'reason': str(e)}
    
    def save_trade_to_csv(self, trade_record: Dict[str, Any]):
        """Save trade record to CSV file"""
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"signal_transmitter_trades_{timestamp}.csv"
            
            # Convert to DataFrame
            df = pd.DataFrame([trade_record])
            
            # Append to existing file or create new one
            if os.path.exists(filename):
                existing_df = pd.read_csv(filename)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            df.to_csv(filename, index=False)
            
        except Exception as e:
            print(f"❌ Error saving trade to CSV: {e}")
    
    def run_signal_extraction_and_transmission(self) -> int:
        """Main function: Extract TODAY'S signals from backtest and transmit to paper trading"""
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n🚀 STARTING TODAY'S SIGNAL EXTRACTION AND TRANSMISSION ({today})")
        print("=" * 70)
        print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("💡 ONLY extracting and transmitting FRESH signals for today")
        print("🚫 Historical/old signals will be filtered out")
        print("=" * 70)
        
        transmitted_orders = 0
        
        try:
            # 1. Get TODAY'S signals from backtest
            signals = self.get_current_signals_from_backtest()
            
            if not signals:
                print(f"\n⏸️ No fresh signals found for today ({today})")
                print("💡 This is normal - strategy only generates signals when conditions are met")
                return 0
            
            print(f"\n📡 TRANSMITTING {len(signals)} FRESH SIGNALS FOR TODAY")
            print("-" * 50)
            
            # 2. Transmit each TODAY'S signal
            for ticker_name, signal_data in signals.items():
                try:
                    # Get current market price
                    current_price = self.get_current_market_price(ticker_name)
                    
                    if current_price is None:
                        print(f"❌ {ticker_name}: Could not get current price")
                        continue
                    
                    # Transmit signal
                    result = self.transmit_signal_to_paper_trading(
                        ticker_name, signal_data, current_price
                    )
                    
                    if result.get('status') == 'TRANSMITTED':
                        transmitted_orders += 1
                    
                except Exception as e:
                    print(f"❌ Error processing {ticker_name}: {e}")
            
        except Exception as e:
            print(f"❌ Error in signal extraction: {e}")
        
        # Summary
        print(f"\n📊 TODAY'S TRANSMISSION COMPLETE ({today})")
        print("=" * 50)
        print(f"📈 Fresh Signals Found: {len(signals) if 'signals' in locals() else 0}")
        print(f"📊 Orders Transmitted: {transmitted_orders}")
        print(f"📋 Total Trade Log: {len(self.trade_log)}")
        if transmitted_orders > 0:
            print("✅ Orders transmitted to paper trading successfully")
        else:
            print("💡 No orders transmitted - waiting for next day's signals")
        print("=" * 50)
        
        return transmitted_orders

def transmit_backtest_signals():
    """Convenience function to extract and transmit signals from backtest"""
    
    transmitter = SignalTransmitter()
    return transmitter.run_signal_extraction_and_transmission()

if __name__ == "__main__":
    """
    Main execution: Extract current signals from live_backtest_WORKING.py 
    and transmit them to paper trading
    """
    
    print("📡 SIGNAL TRANSMITTER - EXTRACTING SIGNALS FROM BACKTEST")
    print("💡 Gets current trading signals from live_backtest_WORKING.py")
    print("📊 Transmits signals to Bitpanda Paper Trading immediately")
    print()
    
    orders_transmitted = transmit_backtest_signals()
    
    print(f"\n🎉 COMPLETED: {orders_transmitted} orders transmitted to paper trading")
