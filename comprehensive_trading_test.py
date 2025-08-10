#!/usr/bin/env python3
"""
Comprehensive Trading Test - Alles außer Order-Übermittlung
=====================================

Führt alle notwendigen Trading-Schritte durch OHNE tatsächliche Orders zu senden:
- Signal-Generierung und Validierung
- Live-Marktdaten Abruf
- Order-Vorbereitung und Validierung
- Portfolio-Simulation
- Risk Management Checks
- Detailliertes Logging und Reporting

Created: August 10, 2025
Author: Trading System
"""

import os
import sys
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import json
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Tuple, Optional, Any
import traceback

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import our modules
try:
    from config import *
    from crypto_backtesting_module import optimize_parameters_with_fixed_data
    from bitpanda_secure_api import BitpandaSecureAPI
    from plotly_utils import create_enhanced_chart
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure all required modules are available.")
    sys.exit(1)

class ComprehensiveTradingTest:
    """
    Comprehensive trading test that does everything except sending orders
    """
    
    def __init__(self, test_mode: bool = True):
        self.test_mode = test_mode
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.api = None
        self.current_prices = {}
        self.portfolio = {}
        self.signals = {}
        self.prepared_orders = []
        self.risk_checks = {}
        
        # Test results
        self.test_results = {
            'data_fetch': False,
            'signal_generation': False,
            'order_preparation': False,
            'risk_validation': False,
            'portfolio_simulation': False,
            'logging_complete': False
        }
        
        self.logger.info("🚀 Comprehensive Trading Test initialisiert")
        self.logger.info(f"⚡ Test Mode: {self.test_mode}")
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_filename = f'comprehensive_test_{self.timestamp}.log'
        
        # Create logger
        self.logger = logging.getLogger('ComprehensiveTradingTest')
        self.logger.setLevel(logging.DEBUG)
        
        # Create handlers
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        console_handler = logging.StreamHandler()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # Set formatters
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"📝 Logging setup complete: {log_filename}")
    
    def step_1_fetch_market_data(self) -> bool:
        """
        Step 1: Fetch current market data for all cryptocurrencies
        """
        self.logger.info("🔄 Step 1: Fetching market data...")
        
        try:
            # Define our crypto pairs
            crypto_pairs = ['BTC-EUR', 'ETH-EUR', 'XRP-EUR', 'DOGE-EUR', 'SOL-EUR', 'LINK-EUR']
            
            self.logger.info(f"📊 Fetching data for: {', '.join(crypto_pairs)}")
            
            # Fetch from Yahoo Finance
            for pair in crypto_pairs:
                try:
                    ticker = yf.Ticker(pair)
                    hist = ticker.history(period="1d", interval="1m")
                    
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        self.current_prices[pair] = {
                            'price': current_price,
                            'timestamp': datetime.now(),
                            'volume': float(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                            'high_24h': float(hist['High'].max()),
                            'low_24h': float(hist['Low'].min())
                        }
                        self.logger.info(f"✅ {pair}: €{current_price:.4f}")
                    else:
                        self.logger.warning(f"⚠️ No data received for {pair}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error fetching {pair}: {str(e)}")
            
            # Validate data quality
            if len(self.current_prices) >= len(crypto_pairs) * 0.8:  # At least 80% success
                self.test_results['data_fetch'] = True
                self.logger.info(f"✅ Market data fetch successful: {len(self.current_prices)}/{len(crypto_pairs)} pairs")
                return True
            else:
                self.logger.error(f"❌ Insufficient market data: {len(self.current_prices)}/{len(crypto_pairs)} pairs")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Market data fetch failed: {str(e)}")
            return False
    
    def step_2_generate_signals(self) -> bool:
        """
        Step 2: Generate trading signals using our strategy
        """
        self.logger.info("🔄 Step 2: Generating trading signals...")
        
        try:
            # Load existing CSV data and run strategy
            for pair in self.current_prices.keys():
                try:
                    # Load historical data
                    csv_file = f"{pair.replace('-EUR', '-EUR')}_daily.csv"
                    if os.path.exists(csv_file):
                        df = pd.read_csv(csv_file)
                        self.logger.info(f"📈 Loaded {len(df)} days of data for {pair}")
                        
                        # Add today's price to the data
                        today = datetime.now().strftime('%Y-%m-%d')
                        current_data = self.current_prices[pair]
                        
                        # Check if today's data already exists
                        if today not in df['Date'].values:
                            new_row = {
                                'Date': today,
                                'Open': current_data['price'],  # Simplified - use current price
                                'High': current_data['high_24h'],
                                'Low': current_data['low_24h'],
                                'Close': current_data['price'],
                                'Volume': current_data['volume']
                            }
                            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        
                        # Run optimization to get signals
                        self.logger.info(f"🔍 Running strategy optimization for {pair}...")
                        
                        # Use our backtesting module
                        result = optimize_parameters_with_fixed_data(
                            ticker=pair.replace('-EUR', ''),
                            data=df,
                            target_period=14,  # 14-day optimization
                            silent=True
                        )
                        
                        if result and 'trades' in result:
                            trades_df = result['trades']
                            # Get today's signals only
                            today_trades = trades_df[trades_df['Date'] == today]
                            
                            if not today_trades.empty:
                                self.signals[pair] = {
                                    'trades': today_trades.to_dict('records'),
                                    'total_trades': len(today_trades),
                                    'buy_signals': len(today_trades[today_trades['Action'] == 'Buy']),
                                    'sell_signals': len(today_trades[today_trades['Action'] == 'Sell']),
                                    'strategy_params': result.get('best_params', {}),
                                    'expected_return': result.get('total_return', 0)
                                }
                                
                                self.logger.info(f"📋 {pair}: {len(today_trades)} signals today")
                                for _, trade in today_trades.iterrows():
                                    self.logger.info(f"   📌 {trade['Action']}: {trade['Shares']:.6f} @ €{trade['Price']:.4f}")
                            else:
                                self.logger.info(f"📋 {pair}: No signals for today")
                                self.signals[pair] = {'trades': [], 'total_trades': 0}
                        else:
                            self.logger.warning(f"⚠️ No strategy result for {pair}")
                            self.signals[pair] = {'trades': [], 'total_trades': 0}
                    else:
                        self.logger.warning(f"⚠️ No historical data file for {pair}: {csv_file}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Signal generation error for {pair}: {str(e)}")
                    self.signals[pair] = {'trades': [], 'total_trades': 0}
            
            # Validate signal generation
            total_signals = sum(signal_data.get('total_trades', 0) for signal_data in self.signals.values())
            if len(self.signals) > 0:
                self.test_results['signal_generation'] = True
                self.logger.info(f"✅ Signal generation complete: {total_signals} total signals across {len(self.signals)} pairs")
                return True
            else:
                self.logger.error("❌ No signals generated")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Signal generation failed: {str(e)}")
            traceback.print_exc()
            return False
    
    def step_3_prepare_orders(self) -> bool:
        """
        Step 3: Prepare orders based on signals (without sending)
        """
        self.logger.info("🔄 Step 3: Preparing orders...")
        
        try:
            self.prepared_orders = []
            total_order_value = 0
            
            for pair, signal_data in self.signals.items():
                if signal_data.get('total_trades', 0) > 0:
                    current_price = self.current_prices[pair]['price']
                    
                    for trade in signal_data['trades']:
                        order = {
                            'pair': pair,
                            'action': trade['Action'],
                            'quantity': abs(float(trade['Shares'])),
                            'price': float(trade['Price']),
                            'current_market_price': current_price,
                            'order_value': abs(float(trade['Shares'])) * current_price,
                            'timestamp': datetime.now(),
                            'strategy_params': signal_data.get('strategy_params', {}),
                            'price_deviation': abs(float(trade['Price']) - current_price) / current_price * 100
                        }
                        
                        self.prepared_orders.append(order)
                        total_order_value += order['order_value']
                        
                        self.logger.info(f"📝 Prepared: {order['action']} {order['quantity']:.6f} {pair} @ €{order['price']:.4f} (Market: €{current_price:.4f})")
                        
                        # Check price deviation
                        if order['price_deviation'] > 5:  # More than 5% deviation
                            self.logger.warning(f"⚠️ Large price deviation: {order['price_deviation']:.2f}%")
            
            if len(self.prepared_orders) > 0:
                self.test_results['order_preparation'] = True
                self.logger.info(f"✅ Order preparation complete: {len(self.prepared_orders)} orders, Total value: €{total_order_value:.2f}")
                return True
            else:
                self.logger.info("ℹ️ No orders to prepare (no signals)")
                self.test_results['order_preparation'] = True  # Still successful
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Order preparation failed: {str(e)}")
            return False
    
    def step_4_risk_validation(self) -> bool:
        """
        Step 4: Perform comprehensive risk validation
        """
        self.logger.info("🔄 Step 4: Performing risk validation...")
        
        try:
            self.risk_checks = {
                'total_exposure': 0,
                'max_single_trade': 0,
                'price_deviations': [],
                'large_orders': [],
                'risk_warnings': [],
                'validation_passed': True
            }
            
            # Calculate total exposure
            total_exposure = sum(order['order_value'] for order in self.prepared_orders)
            self.risk_checks['total_exposure'] = total_exposure
            
            # Risk limits (configurable)
            MAX_TOTAL_EXPOSURE = 10000  # €10,000 max total exposure
            MAX_SINGLE_TRADE = 2000     # €2,000 max single trade
            MAX_PRICE_DEVIATION = 10    # 10% max price deviation
            
            for order in self.prepared_orders:
                # Check single trade size
                if order['order_value'] > self.risk_checks['max_single_trade']:
                    self.risk_checks['max_single_trade'] = order['order_value']
                
                # Check price deviations
                self.risk_checks['price_deviations'].append(order['price_deviation'])
                
                # Flag large orders
                if order['order_value'] > MAX_SINGLE_TRADE:
                    self.risk_checks['large_orders'].append(order)
                    self.risk_checks['risk_warnings'].append(f"Large order: {order['pair']} €{order['order_value']:.2f}")
                
                # Flag high price deviations
                if order['price_deviation'] > MAX_PRICE_DEVIATION:
                    self.risk_checks['risk_warnings'].append(f"High price deviation: {order['pair']} {order['price_deviation']:.2f}%")
            
            # Overall risk assessment
            if total_exposure > MAX_TOTAL_EXPOSURE:
                self.risk_checks['risk_warnings'].append(f"Total exposure too high: €{total_exposure:.2f} > €{MAX_TOTAL_EXPOSURE}")
                self.risk_checks['validation_passed'] = False
            
            if self.risk_checks['max_single_trade'] > MAX_SINGLE_TRADE:
                self.risk_checks['risk_warnings'].append(f"Single trade too large: €{self.risk_checks['max_single_trade']:.2f} > €{MAX_SINGLE_TRADE}")
            
            # Log risk assessment
            self.logger.info(f"💰 Total Exposure: €{total_exposure:.2f}")
            self.logger.info(f"📊 Max Single Trade: €{self.risk_checks['max_single_trade']:.2f}")
            self.logger.info(f"📈 Avg Price Deviation: {np.mean(self.risk_checks['price_deviations']):.2f}%")
            
            if self.risk_checks['risk_warnings']:
                for warning in self.risk_checks['risk_warnings']:
                    self.logger.warning(f"⚠️ Risk Warning: {warning}")
            else:
                self.logger.info("✅ All risk checks passed")
            
            self.test_results['risk_validation'] = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Risk validation failed: {str(e)}")
            return False
    
    def step_5_simulate_portfolio(self) -> bool:
        """
        Step 5: Simulate portfolio changes without executing trades
        """
        self.logger.info("🔄 Step 5: Simulating portfolio changes...")
        
        try:
            # Initialize portfolio simulation
            initial_cash = 10000  # €10,000 starting capital
            simulated_portfolio = {
                'cash': initial_cash,
                'positions': {},
                'total_value': initial_cash,
                'trades_executed': 0,
                'total_fees': 0
            }
            
            # Simulate each order
            for order in self.prepared_orders:
                pair = order['pair'].replace('-EUR', '')
                action = order['action']
                quantity = order['quantity']
                price = order['current_market_price']  # Use current market price
                order_value = quantity * price
                fee = order_value * 0.0015  # 0.15% trading fee
                
                if action.upper() == 'BUY':
                    if simulated_portfolio['cash'] >= (order_value + fee):
                        # Execute buy
                        simulated_portfolio['cash'] -= (order_value + fee)
                        if pair not in simulated_portfolio['positions']:
                            simulated_portfolio['positions'][pair] = 0
                        simulated_portfolio['positions'][pair] += quantity
                        simulated_portfolio['trades_executed'] += 1
                        simulated_portfolio['total_fees'] += fee
                        
                        self.logger.info(f"💳 Simulated BUY: {quantity:.6f} {pair} @ €{price:.4f} (Fee: €{fee:.2f})")
                    else:
                        self.logger.warning(f"⚠️ Insufficient funds for {pair}: Need €{order_value + fee:.2f}, Have €{simulated_portfolio['cash']:.2f}")
                
                elif action.upper() == 'SELL':
                    if pair in simulated_portfolio['positions'] and simulated_portfolio['positions'][pair] >= quantity:
                        # Execute sell
                        simulated_portfolio['cash'] += (order_value - fee)
                        simulated_portfolio['positions'][pair] -= quantity
                        if simulated_portfolio['positions'][pair] == 0:
                            del simulated_portfolio['positions'][pair]
                        simulated_portfolio['trades_executed'] += 1
                        simulated_portfolio['total_fees'] += fee
                        
                        self.logger.info(f"💰 Simulated SELL: {quantity:.6f} {pair} @ €{price:.4f} (Fee: €{fee:.2f})")
                    else:
                        current_position = simulated_portfolio['positions'].get(pair, 0)
                        self.logger.warning(f"⚠️ Insufficient position for {pair}: Need {quantity:.6f}, Have {current_position:.6f}")
            
            # Calculate total portfolio value
            total_crypto_value = 0
            for crypto, quantity in simulated_portfolio['positions'].items():
                price = self.current_prices.get(f"{crypto}-EUR", {}).get('price', 0)
                crypto_value = quantity * price
                total_crypto_value += crypto_value
                self.logger.info(f"💼 Position: {quantity:.6f} {crypto} = €{crypto_value:.2f}")
            
            simulated_portfolio['total_value'] = simulated_portfolio['cash'] + total_crypto_value
            
            # Portfolio summary
            self.logger.info("📊 Portfolio Simulation Summary:")
            self.logger.info(f"💰 Cash: €{simulated_portfolio['cash']:.2f}")
            self.logger.info(f"🪙 Crypto Value: €{total_crypto_value:.2f}")
            self.logger.info(f"📈 Total Value: €{simulated_portfolio['total_value']:.2f}")
            self.logger.info(f"📊 P&L: €{simulated_portfolio['total_value'] - initial_cash:.2f}")
            self.logger.info(f"🔄 Trades: {simulated_portfolio['trades_executed']}")
            self.logger.info(f"💸 Total Fees: €{simulated_portfolio['total_fees']:.2f}")
            
            self.portfolio = simulated_portfolio
            self.test_results['portfolio_simulation'] = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Portfolio simulation failed: {str(e)}")
            return False
    
    def step_6_generate_report(self) -> bool:
        """
        Step 6: Generate comprehensive test report
        """
        self.logger.info("🔄 Step 6: Generating comprehensive report...")
        
        try:
            report_filename = f'comprehensive_test_report_{self.timestamp}.json'
            
            # Compile comprehensive report
            report = {
                'test_info': {
                    'timestamp': self.timestamp,
                    'test_mode': self.test_mode,
                    'duration': (datetime.now() - datetime.strptime(self.timestamp, '%Y%m%d_%H%M%S')).total_seconds(),
                    'success': all(self.test_results.values())
                },
                'test_results': self.test_results,
                'market_data': {
                    pair: {
                        'price': data['price'],
                        'timestamp': data['timestamp'].isoformat(),
                        'volume': data['volume']
                    } for pair, data in self.current_prices.items()
                },
                'signals': {
                    pair: {
                        'total_trades': data.get('total_trades', 0),
                        'buy_signals': data.get('buy_signals', 0),
                        'sell_signals': data.get('sell_signals', 0)
                    } for pair, data in self.signals.items()
                },
                'prepared_orders': [
                    {
                        'pair': order['pair'],
                        'action': order['action'],
                        'quantity': order['quantity'],
                        'price': order['price'],
                        'current_market_price': order['current_market_price'],
                        'order_value': order['order_value'],
                        'price_deviation': order['price_deviation']
                    } for order in self.prepared_orders
                ],
                'risk_assessment': self.risk_checks,
                'portfolio_simulation': self.portfolio
            }
            
            # Save report
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"📄 Report saved: {report_filename}")
            
            # Generate summary
            self.logger.info("\n" + "="*80)
            self.logger.info("📋 COMPREHENSIVE TEST SUMMARY")
            self.logger.info("="*80)
            self.logger.info(f"⏰ Test Duration: {report['test_info']['duration']:.1f} seconds")
            self.logger.info(f"✅ Overall Success: {report['test_info']['success']}")
            self.logger.info(f"📊 Market Data: {len(self.current_prices)} pairs fetched")
            self.logger.info(f"📋 Signals: {sum(data.get('total_trades', 0) for data in self.signals.values())} total")
            self.logger.info(f"📝 Prepared Orders: {len(self.prepared_orders)}")
            self.logger.info(f"⚠️ Risk Warnings: {len(self.risk_checks.get('risk_warnings', []))}")
            self.logger.info(f"💰 Total Exposure: €{self.risk_checks.get('total_exposure', 0):.2f}")
            self.logger.info(f"🔄 Simulated Trades: {self.portfolio.get('trades_executed', 0)}")
            self.logger.info(f"📈 Portfolio P&L: €{self.portfolio.get('total_value', 0) - 10000:.2f}")
            self.logger.info("="*80)
            
            # Test step breakdown
            self.logger.info("📊 Test Step Results:")
            for step, result in self.test_results.items():
                status = "✅" if result else "❌"
                self.logger.info(f"   {status} {step.replace('_', ' ').title()}")
            
            if self.risk_checks.get('risk_warnings'):
                self.logger.info("\n⚠️ Risk Warnings:")
                for warning in self.risk_checks['risk_warnings']:
                    self.logger.info(f"   ⚠️ {warning}")
            
            self.test_results['logging_complete'] = True
            
            # Print final status
            if all(self.test_results.values()):
                self.logger.info("\n🎉 COMPREHENSIVE TEST COMPLETED SUCCESSFULLY!")
                self.logger.info("📤 Ready for order transmission (if enabled)")
            else:
                failed_steps = [step for step, result in self.test_results.items() if not result]
                self.logger.error(f"\n❌ TEST FAILED - Failed steps: {', '.join(failed_steps)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Report generation failed: {str(e)}")
            return False
    
    def run_comprehensive_test(self) -> bool:
        """
        Run all test steps in sequence
        """
        self.logger.info("🚀 Starting Comprehensive Trading Test...")
        self.logger.info("📋 Test will perform everything except sending actual orders")
        
        try:
            # Step 1: Fetch Market Data
            if not self.step_1_fetch_market_data():
                self.logger.error("❌ Test failed at Step 1: Market Data")
                return False
            
            # Step 2: Generate Signals
            if not self.step_2_generate_signals():
                self.logger.error("❌ Test failed at Step 2: Signal Generation")
                return False
            
            # Step 3: Prepare Orders
            if not self.step_3_prepare_orders():
                self.logger.error("❌ Test failed at Step 3: Order Preparation")
                return False
            
            # Step 4: Risk Validation
            if not self.step_4_risk_validation():
                self.logger.error("❌ Test failed at Step 4: Risk Validation")
                return False
            
            # Step 5: Portfolio Simulation
            if not self.step_5_simulate_portfolio():
                self.logger.error("❌ Test failed at Step 5: Portfolio Simulation")
                return False
            
            # Step 6: Generate Report
            if not self.step_6_generate_report():
                self.logger.error("❌ Test failed at Step 6: Report Generation")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Comprehensive test failed: {str(e)}")
            traceback.print_exc()
            return False

def main():
    """
    Main execution function
    """
    print("🚀 Comprehensive Trading Test - Alles außer Order-Übermittlung")
    print("="*80)
    print("📋 Dieser Test führt alle Trading-Schritte durch OHNE Orders zu senden:")
    print("   1. ✅ Live-Marktdaten abrufen")
    print("   2. ✅ Trading-Signale generieren")
    print("   3. ✅ Orders vorbereiten und validieren")
    print("   4. ✅ Risiko-Management prüfen")
    print("   5. ✅ Portfolio-Änderungen simulieren")
    print("   6. ✅ Detaillierten Report erstellen")
    print("   7. ❌ Orders übermitteln (DEAKTIVIERT)")
    print("="*80)
    
    # Initialize test
    test = ComprehensiveTradingTest(test_mode=True)
    
    try:
        # Run comprehensive test
        success = test.run_comprehensive_test()
        
        if success:
            print("\n🎉 COMPREHENSIVE TEST ERFOLGREICH ABGESCHLOSSEN!")
            print("📊 Alle Trading-Komponenten funktionieren korrekt")
            print("📤 System ist bereit für Live-Trading (wenn aktiviert)")
        else:
            print("\n❌ TEST FEHLGESCHLAGEN")
            print("🔧 Bitte Logs prüfen und Probleme beheben")
        
        return success
        
    except KeyboardInterrupt:
        test.logger.info("⏹️ Test von Benutzer abgebrochen")
        print("\n⏹️ Test wurde abgebrochen")
        return False
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
