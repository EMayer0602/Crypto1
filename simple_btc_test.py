#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test eines einzelnen Tickers mit neuen Equity Formeln
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import load_crypto_data_yf, run_backtest
from crypto_tickers import crypto_tickers

def simple_test_btc():
    """Test BTC-EUR mit Trade on Open"""
    print("🧪 TESTE BTC-EUR (Trade on Open)")
    print("=" * 50)
    
    symbol = 'BTC-EUR'
    config = crypto_tickers[symbol]
    
    print(f"📊 Symbol: {symbol}")
    print(f"💰 Initial Capital: €{config['initialCapitalLong']}")
    print(f"🔧 Trade on: {config['trade_on']}")
    
    # Lade Daten
    from config import backtest_years
    df = load_crypto_data_yf(symbol, backtest_years)
    
    if df is not None:
        print(f"📅 Data Range: {df.index.min().date()} bis {df.index.max().date()}")
        print(f"📊 Total Days: {len(df)}")
        
        # Führe Backtest durch
        try:
            result = run_backtest(symbol)
            if result:
                print(f"✅ Backtest erfolgreich!")
                print(f"   PnL: {result.get('total_return_pct', 0):.2f}%")
                print(f"   Trades: {result.get('num_trades', 0)}")
                print(f"   Optimal p: {result.get('optimal_past_window', 'N/A')}")
                print(f"   Optimal tw: {result.get('optimal_trade_window', 'N/A')}")
            else:
                print("❌ Backtest fehlgeschlagen")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    simple_test_btc()
