#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfacher Test der Equity Curve Formeln
"""

from crypto_tickers import crypto_tickers

def test_config():
    """Test crypto_tickers config"""
    print("🧪 CRYPTO TICKERS CONFIG:")
    print("=" * 50)
    
    for symbol, config in crypto_tickers.items():
        trade_on = config.get('trade_on', 'Unknown')
        initial_cap = config.get('initialCapitalLong', 0)
        print(f"{symbol:<10} | Trade on: {trade_on:<5} | Capital: €{initial_cap}")
    
    print("=" * 50)
    
    # Test Trade on Open vs Close split
    open_tickers = [s for s, c in crypto_tickers.items() if c.get('trade_on') == 'Open']
    close_tickers = [s for s, c in crypto_tickers.items() if c.get('trade_on') == 'Close']
    
    print(f"🔶 Trade on OPEN ({len(open_tickers)}): {', '.join(open_tickers)}")
    print(f"🔷 Trade on CLOSE ({len(close_tickers)}): {', '.join(close_tickers)}")

if __name__ == "__main__":
    test_config()
