#!/usr/bin/env python3
"""
Schneller Check: Werden überhaupt Trades generiert?
"""

import pandas as pd
import sys
import os

sys.path.append(os.getcwd())
from crypto_backtesting_module import run_backtest, load_crypto_data_yf

def quick_trade_check():
    """Prüft ob Trades generiert werden"""
    print("🔍 QUICK TRADE CHECK")
    print("="*30)
    
    # Test mit XRP-EUR
    symbol = 'XRP-EUR'
    print(f"📊 Teste {symbol}")
    
    # Lade nur letzte 30 Tage für schnellen Test
    df = load_crypto_data_yf(symbol)
    if df is None or df.empty:
        print("❌ Keine Daten")
        return
        
    df_short = df.tail(50)  # Nur letzte 50 Tage
    print(f"   Test mit {len(df_short)} Tagen")
    
    try:
        result = run_backtest(df_short, symbol)
        
        print(f"   Matched Trades: {len(result.get('matched_trades', []))}")
        print(f"   Optimal p: {result.get('optimal_p', 'N/A')}")
        print(f"   Optimal tw: {result.get('optimal_tw', 'N/A')}")
        print(f"   Final Capital: €{result.get('final_capital', 0):.2f}")
        
        if 'matched_trades' in result and len(result['matched_trades']) > 0:
            trades = result['matched_trades']
            print(f"   Erste 3 Trades:")
            for i, (_, trade) in enumerate(trades.head(3).iterrows()):
                print(f"     {i+1}. {trade.get('Action', 'N/A')} @ €{trade.get('Price', 0):.4f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_trade_check()
