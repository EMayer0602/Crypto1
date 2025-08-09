#!/usr/bin/env python3
"""
Focused test to trace exactly what prices are being used
"""

import pandas as pd
from crypto_backtesting_module import load_crypto_data_yf
from signal_utils import assign_long_signals_extended, update_level_close_long
from crypto_tickers import crypto_tickers

def trace_price_usage():
    """Trace exactly which prices are being used"""
    
    print("🔍 TRACING PRICE USAGE")
    print("="*50)
    
    # Load data for BTC-EUR (trade_on: Open)
    symbol = "BTC-EUR"
    config = crypto_tickers[symbol]
    
    print(f"📊 Testing {symbol}")
    print(f"   Config trade_on: '{config['trade_on']}'")
    
    try:
        # Load data
        from config import backtest_years
        df = load_crypto_data_yf(symbol, backtest_years)
        
        # Get a sample of data to compare
        sample_data = df.head(10)[['Open', 'Close']].copy()
        print(f"\n📊 Sample data (first 10 days):")
        for idx, row in sample_data.iterrows():
            print(f"   {idx.date()}: Open=€{row['Open']:.4f}, Close=€{row['Close']:.4f}")
        
        # Create some dummy signals to test with
        from signal_utils import calculate_support_resistance
        
        supp, res = calculate_support_resistance(df, 10)
        
        if len(supp) > 0 and len(res) > 0:
            # Generate extended signals 
            ext_trades = assign_long_signals_extended(
                supp, res, df, 1, "1d", config['trade_on']
            )
            
            # Update level close
            ext_trades = update_level_close_long(ext_trades, df, config['trade_on'])
            
            if not ext_trades.empty:
                print(f"\n📈 Extended trades generated: {len(ext_trades)}")
                
                # Check first few trades
                for idx, trade in ext_trades.head(5).iterrows():
                    date = trade.get('Long Date detected')
                    level_close = trade.get('Level Close', 0)
                    action = trade.get('Action', 'N/A')
                    
                    if pd.notna(date) and action in ['buy', 'sell']:
                        # Convert date to proper format
                        if isinstance(date, str):
                            trade_date = pd.to_datetime(date).normalize()
                        else:
                            trade_date = date.normalize()
                            
                        # Get the actual Open/Close for that date
                        if trade_date in df.index:
                            actual_open = df.loc[trade_date, 'Open']
                            actual_close = df.loc[trade_date, 'Close']
                            
                            print(f"\n   Trade {idx+1}: {trade_date.date()}")
                            print(f"      Action: {action}")
                            print(f"      Level Close: €{level_close:.4f}")
                            print(f"      Actual Open: €{actual_open:.4f}")
                            print(f"      Actual Close: €{actual_close:.4f}")
                            
                            # Check which price matches
                            if abs(level_close - actual_open) < 0.001:
                                print(f"      ✅ USING OPEN PRICE (correct for trade_on='Open')")
                            elif abs(level_close - actual_close) < 0.001:
                                print(f"      ❌ USING CLOSE PRICE (wrong for trade_on='Open')")
                            else:
                                print(f"      ❓ USING DIFFERENT PRICE")
            else:
                print("❌ No extended trades generated")
        else:
            print("❌ No support/resistance levels found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    trace_price_usage()
