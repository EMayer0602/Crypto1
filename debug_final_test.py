#!/usr/bin/env python3
"""Debug der Equity Curve Berechnung - FOKUS"""

import pandas as pd
from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def debug_final_capital():
    print("🔍 DEBUGGING FINAL CAPITAL & EQUITY CURVE...")
    print("=" * 60)
    
    # Führe Backtest aus
    config = crypto_tickers['BTC-EUR']
    ticker = 'BTC-EUR'
    
    print(f"📊 Testing {ticker} with initial capital: €{config['initialCapitalLong']:,.0f}")
    
    result = run_backtest(ticker, config)
    
    if result and result.get('success'):
        print("✅ Backtest successful!")
        
        # Prüfe Final Capital
        final_cap = result.get('final_capital', 0)
        print(f"📈 Final Capital from result: €{final_cap:,.2f}")
        
        # Prüfe Equity Curve
        equity_curve = result.get('equity_curve', [])
        print(f"📊 Equity curve length: {len(equity_curve)}")
        
        if len(equity_curve) > 0:
            print(f"📊 Equity curve range: €{min(equity_curve):,.0f} - €{max(equity_curve):,.0f}")
            print(f"📊 First 5 equity values: {equity_curve[:5]}")
            print(f"📊 Last 5 equity values: {equity_curve[-5:]}")
        
        # ✅ Prüfe matched_trades im Detail
        matched_trades = result.get('matched_trades', pd.DataFrame())
        print(f"📊 Matched trades shape: {matched_trades.shape}")
        
        if not matched_trades.empty:
            print(f"📊 Matched trades columns: {list(matched_trades.columns)}")
            
            # Zeige nur verfügbare Spalten
            available_cols = [col for col in ['Date', 'Action', 'Price', 'Capital', 'Shares'] if col in matched_trades.columns]
            if available_cols:
                print(f"📊 First 3 matched trades ({available_cols}):")
                print(matched_trades[available_cols].head(3))
            
            if 'Capital' in matched_trades.columns:
                capital_values = matched_trades['Capital'].tolist()
                print(f"📊 Capital progression: €{capital_values[0]:,.0f} -> €{capital_values[-1]:,.0f}")
                print(f"📊 Expected match with equity curve: {abs(capital_values[-1] - equity_curve[-1]) < 100 if equity_curve else 'N/A'}")
        else:
            print(f"❌ No matched trades found!")
            
        # Trade Statistics
        trade_stats = result.get('trade_statistics', {})
        if trade_stats:
            print(f"📊 Trade statistics keys: {list(trade_stats.keys())}")
            final_cap_stat = trade_stats.get('💼 Final Capital', 'N/A')
            print(f"📊 Final Capital from stats: {final_cap_stat}")
    
    else:
        print("❌ Backtest failed")

if __name__ == "__main__":
    debug_final_capital()
