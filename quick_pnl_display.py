#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 QUICK PnL DISPLAY - Zeigt nur die Ticker PnL Liste
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from crypto_backtesting_module import run_backtest
import crypto_tickers

def main():
    """Führe schnelle PnL-Anzeige aus"""
    print("🚀 Schnelle PnL-Berechnung...")
    
    tickers = list(crypto_tickers.crypto_tickers.keys())
    
    for ticker in tickers:
        ticker_config = crypto_tickers.crypto_tickers.get(ticker, {})
        
        # Erstelle vollständige Config
        config = {
            'initialCapitalLong': ticker_config.get('initialCapitalLong', 10000),
            'commission_rate': 0.0018,
            'trade_on': ticker_config.get('trade_on', 'Close'),
            'order_round_factor': ticker_config.get('order_round_factor', 0.01),
            'timeframe': 'daily',
            'csv_path': './'
        }
        
        # Führe Backtest aus
        result = run_backtest(ticker, config)
        
        if result and result.get('success', False):
            ticker_short = ticker.replace('-EUR', '').upper()
            optimal_pnl = result.get('optimal_pnl', 0)
            print(f"{ticker_short:<8} {optimal_pnl:>6.0f}%")
    
    print()

if __name__ == "__main__":
    main()
