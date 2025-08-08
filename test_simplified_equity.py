#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test der neuen Equity-Kurve: nur Werte bei Buy/Sell Dates mit Shares/Quantity
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers
import pandas as pd

def test_simplified_equity():
    """Test der vereinfachten Equity-Kurve für einen Ticker"""
    
    # Test mit BTC-EUR
    symbol = "BTC-EUR"
    config = crypto_tickers.get(symbol, {})
    
    print(f"🧪 TESTE VEREINFACHTE EQUITY-KURVE für {symbol}")
    print("=" * 80)
    
    # Führe Backtest durch
    result = run_backtest(symbol, config)
    
    if result and isinstance(result, dict):
        print(f"\n✅ Backtest erfolgreich für {symbol}")
        
        # Zeige Equity-Kurve Details
        equity_curve = result.get('equity_curve', [])
        matched_trades = result.get('matched_trades', pd.DataFrame())
        
        print(f"\n📊 EQUITY-KURVE ANALYSE:")
        print(f"   📏 Länge: {len(equity_curve)} Werte")
        print(f"   💰 Start: €{equity_curve[0]:.0f}")
        print(f"   💰 Ende: €{equity_curve[-1]:.0f}")
        print(f"   📈 Min: €{min(equity_curve):.0f}")
        print(f"   📈 Max: €{max(equity_curve):.0f}")
        
        # Prüfe Variabilität
        unique_values = len(set([int(v) for v in equity_curve]))
        print(f"   🔍 Unique Werte: {unique_values}")
        
        if unique_values > 1:
            print(f"   ✅ Equity-Kurve variiert korrekt!")
        else:
            print(f"   ⚠️ Equity-Kurve ist konstant (keine Trades?)")
        
        # Zeige Sample-Werte
        if len(equity_curve) >= 10:
            sample_indices = [0, len(equity_curve)//4, len(equity_curve)//2, 3*len(equity_curve)//4, -1]
            sample_values = [equity_curve[i] for i in sample_indices]
            print(f"   📊 Sample Werte: {[f'€{v:.0f}' for v in sample_values]}")
        
        # Zeige Trades
        if not matched_trades.empty:
            print(f"\n📈 MATCHED TRADES ({len(matched_trades)}):")
            for idx, trade in matched_trades.iterrows():
                print(f"   {idx+1}. {trade.get('Entry Date', 'N/A')} → {trade.get('Exit Date', 'N/A')}: "
                      f"{trade.get('Quantity', 0):.6f} shares, PnL: €{trade.get('Net PnL', 0):.2f}")
        else:
            print(f"\n⚠️ Keine Matched Trades gefunden")
        
        return True
    else:
        print(f"❌ Backtest fehlgeschlagen für {symbol}")
        return False

if __name__ == "__main__":
    success = test_simplified_equity()
    if success:
        print(f"\n🎯 Test erfolgreich abgeschlossen!")
    else:
        print(f"\n❌ Test fehlgeschlagen!")
