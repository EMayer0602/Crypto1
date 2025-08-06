#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DEBUG PnL Extraction - Teste einen einzelnen Ticker um zu sehen, was der Backtest wirklich zurückgibt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from crypto_backtesting_module import run_backtest
import crypto_tickers

def debug_single_ticker(ticker="BTC-EUR"):
    """Debug einen einzelnen Ticker"""
    
    print(f"DEBUG BACKTEST für {ticker}")
    print("=" * 60)
    
    # Hole Config
    ticker_config = crypto_tickers.crypto_tickers.get(ticker, {})
    
    config = {
        'initial_capital': ticker_config.get('initialCapitalLong', 10000),
        'commission_rate': 0.0018,
        'trade_on': ticker_config.get('trade_on', 'Close'),
        'order_round_factor': ticker_config.get('order_round_factor', 0.01),
        'timeframe': 'daily',
        'csv_path': './',
        'min_commission': 1.0
    }
    
    print(f"Config: {config}")
    print()
    
    # Führe Backtest aus
    result = run_backtest(ticker, config)
    
    if result and result.get('success', False):
        print("RESULT KEYS:")
        for key in result.keys():
            print(f"  {key}: {type(result[key])}")
        print()
        
        print("TRADE STATISTICS:")
        trade_stats = result.get('trade_statistics', {})
        for key, value in trade_stats.items():
            print(f"  {key}: {value}")
        print()
        
        print("OPTIMIZATION RESULTS:")
        print(f"  optimal_past_window: {result.get('optimal_past_window')}")
        print(f"  optimal_trade_window: {result.get('optimal_trade_window')}")
        print(f"  optimal_pnl: {result.get('optimal_pnl')}")
        print()
        
        # Extrahiere Total Return
        total_return_str = trade_stats.get('📊 Total Return', '0.00%')
        print(f"TOTAL RETURN STRING: '{total_return_str}'")
        
        if isinstance(total_return_str, str) and '%' in total_return_str:
            total_return_percent = float(total_return_str.replace('%', ''))
            print(f"PARSED TOTAL RETURN: {total_return_percent}%")
        
        # Extrahiere Total PnL
        total_pnl_str = trade_stats.get('💰 Total PnL', '€0.00')
        print(f"TOTAL PnL STRING: '{total_pnl_str}'")
        
        initial_capital = config['initial_capital']
        print(f"INITIAL CAPITAL: {initial_capital}")
        
        if isinstance(total_pnl_str, str) and '€' in total_pnl_str:
            total_pnl = float(total_pnl_str.replace('€', '').replace(',', ''))
            manual_return = (total_pnl / initial_capital) * 100
            print(f"MANUAL CALCULATION: PnL={total_pnl}, Return={manual_return:.2f}%")
        
    else:
        print("BACKTEST FAILED!")

if __name__ == "__main__":
    debug_single_ticker("BTC-EUR")
