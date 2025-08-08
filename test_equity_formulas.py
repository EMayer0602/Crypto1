#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der neuen Equity Curve Formeln für Trade on Open vs Close
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import run_backtest

def test_single_ticker():
    """Test a single ticker with new equity formulas"""
    print("🧪 TESTE NEUE EQUITY FORMELN")
    print("=" * 60)
    
    # Test BTC-EUR (Trade on Open)
    print("\n🔶 BTC-EUR (Trade on Open):")
    result_btc = run_backtest('BTC-EUR')
    
    if result_btc:
        print(f"✅ BTC-EUR: PnL = {result_btc.get('total_return_pct', 0):.2f}%")
        print(f"   Initial: €{result_btc.get('initial_capital', 0):.0f}")
        print(f"   Final: €{result_btc.get('final_capital', 0):.0f}")
        print(f"   Trades: {result_btc.get('num_trades', 0)}")
    
    print("\n" + "=" * 60)
    
    # Test ETH-EUR (Trade on Close) 
    print("\n🔷 ETH-EUR (Trade on Close):")
    result_eth = run_backtest('ETH-EUR')
    
    if result_eth:
        print(f"✅ ETH-EUR: PnL = {result_eth.get('total_return_pct', 0):.2f}%")
        print(f"   Initial: €{result_eth.get('initial_capital', 0):.0f}")
        print(f"   Final: €{result_eth.get('final_capital', 0):.0f}")
        print(f"   Trades: {result_eth.get('num_trades', 0)}")
    
    print("\n" + "=" * 60)
    print("🧪 TEST ABGESCHLOSSEN")

if __name__ == "__main__":
    test_single_ticker()
