#!/usr/bin/env python3

"""
TEST SCRIPT: Open vs Close Trading
Testet ob das "trade_on" Parameter unterschiedliche Ergebnisse liefert
"""

import pandas as pd
import os
from crypto_tickers import crypto_tickers
from crypto_backtesting_module import simulate_real_trades

def test_trade_on_difference():
    """
    Testet BTC-EUR mit Open vs Close Trading
    """
    print("🧪 TESTING TRADE_ON PARAMETER...")
    print("="*60)
    
    # Lade BTC Daten
    symbol = "BTC-EUR"
    csv_file = f"{symbol}_daily.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ {csv_file} nicht gefunden")
        return
    
    # Lade DataFrame
    df = pd.read_csv(csv_file)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
    
    print(f"📊 Loaded {len(df)} rows of {symbol} data")
    print(f"📅 From {df.index[0]} to {df.index[-1]}")
    
    # Erstelle Test-Signale (Buy am ersten Tag, Sell nach 10 Tagen)
    test_signals = pd.DataFrame({
        'Long Date detected': [df.index[10], df.index[20]],
        'Action': ['buy', 'sell']
    })
    
    print(f"\n🎯 Test Signals:")
    for i, row in test_signals.iterrows():
        print(f"   {row['Action'].upper()} on {row['Long Date detected'].strftime('%Y-%m-%d')}")
    
    # Test mit OPEN Trading
    print(f"\n{'='*30} OPEN TRADING {'='*30}")
    config_open = crypto_tickers[symbol].copy()
    config_open['trade_on'] = 'Open'
    
    trades_open, final_cap_open = simulate_real_trades(test_signals, df, config_open)
    
    # Test mit CLOSE Trading
    print(f"\n{'='*30} CLOSE TRADING {'='*30}")
    config_close = crypto_tickers[symbol].copy()
    config_close['trade_on'] = 'Close'
    
    trades_close, final_cap_close = simulate_real_trades(test_signals, df, config_close)
    
    # Vergleiche Ergebnisse
    print(f"\n{'='*30} COMPARISON {'='*30}")
    print(f"OPEN Trading:")
    if not trades_open.empty:
        print(f"   Entry Price: €{trades_open.iloc[0]['Entry Price']:.2f}")
        print(f"   Exit Price:  €{trades_open.iloc[0]['Exit Price']:.2f}")
        print(f"   PnL:         €{trades_open.iloc[0]['PnL']:.2f}")
        print(f"   Final Cap:   €{final_cap_open:.2f}")
    
    print(f"\nCLOSE Trading:")
    if not trades_close.empty:
        print(f"   Entry Price: €{trades_close.iloc[0]['Entry Price']:.2f}")
        print(f"   Exit Price:  €{trades_close.iloc[0]['Exit Price']:.2f}")
        print(f"   PnL:         €{trades_close.iloc[0]['PnL']:.2f}")
        print(f"   Final Cap:   €{final_cap_close:.2f}")
    
    # Prüfe Unterschied
    if not trades_open.empty and not trades_close.empty:
        price_diff = abs(trades_open.iloc[0]['Entry Price'] - trades_close.iloc[0]['Entry Price'])
        pnl_diff = abs(trades_open.iloc[0]['PnL'] - trades_close.iloc[0]['PnL'])
        
        print(f"\nDIFFERENCES:")
        print(f"   Entry Price Diff: €{price_diff:.2f}")
        print(f"   PnL Difference:   €{pnl_diff:.2f}")
        
        if price_diff > 0.01:
            print("✅ SUCCESS: trade_on parameter works correctly!")
        else:
            print("❌ PROBLEM: No difference detected!")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_trade_on_difference()
