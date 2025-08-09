#!/usr/bin/env python3

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))

from crypto_backtesting_module import load_crypto_data_yf, calculate_support_resistance, assign_long_signals_extended, update_level_close_long, simulate_matched_trades
from crypto_tickers import crypto_tickers

def test_open_vs_close_prices():
    print("🔍 COMPARING OPEN VS CLOSE PRICES IN MATCHED TRADES")
    print("="*80)
    
    symbol = 'XRP-EUR'  # We'll test both Open and Close modes with the same data
    config = crypto_tickers[symbol]
    
    # Load data
    df = load_crypto_data_yf(symbol, 1)
    if df is None or df.empty:
        print("❌ No data loaded")
        return
    
    # Calculate support/resistance
    supp, res = calculate_support_resistance(df, 10, 1, verbose=False)
    
    # Test with both Open and Close
    for trade_mode in ['Open', 'Close']:
        print(f"\n📊 Testing with trade_on = '{trade_mode}'")
        print("-"*60)
        
        # Generate extended trades
        ext = assign_long_signals_extended(supp, res, df, 1, "1d", trade_mode)
        ext = update_level_close_long(ext, df, trade_mode)
        
        if ext.empty:
            print("❌ No extended trades generated")
            continue
        
        # Show sample extended trade with actual Open/Close values from df
        sample_trade = ext[ext['Action'] == 'buy'].head(1)
        if not sample_trade.empty:
            trade_date = sample_trade.iloc[0]['Long Date detected']
            level_close = sample_trade.iloc[0]['Level Close']
            
            # Get actual Open/Close from original data
            if pd.Timestamp(trade_date) in df.index:
                actual_open = df.loc[pd.Timestamp(trade_date), 'Open']
                actual_close = df.loc[pd.Timestamp(trade_date), 'Close']
                
                print(f"📅 Sample BUY signal on {trade_date}")
                print(f"🔢 Actual Open price:  €{actual_open:.4f}")
                print(f"🔢 Actual Close price: €{actual_close:.4f}")
                print(f"🎯 Level Close value:  €{level_close:.4f}")
                
                if trade_mode == 'Open':
                    expected = actual_open
                    print(f"✅ Expected: Open price (€{expected:.4f})")
                else:
                    expected = actual_close
                    print(f"✅ Expected: Close price (€{expected:.4f})")
                
                if abs(level_close - expected) < 0.0001:
                    print("✅ CORRECT: Level Close matches expected price!")
                else:
                    print(f"❌ ERROR: Level Close (€{level_close:.4f}) != Expected (€{expected:.4f})")
        
        # Generate matched trades
        matched = simulate_matched_trades(ext, config['initialCapitalLong'], 0.0018, df, config['order_round_factor'], trade_mode)
        
        if not matched.empty:
            print(f"✅ Generated {len(matched)} matched trades using {trade_mode} prices")
            first_trade = matched.iloc[0]
            print(f"📋 First matched trade: Entry=€{first_trade['Entry Price']}, Exit=€{first_trade['Exit Price']}")
        else:
            print("❌ No matched trades generated")

if __name__ == "__main__":
    test_open_vs_close_prices()
