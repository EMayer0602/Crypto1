#!/usr/bin/env python3
"""Detailed test to see the full optimization results"""

from signal_utils import berechne_best_p_tw_long
from crypto_backtesting_module import load_crypto_data_yf
import pandas as pd

def detailed_optimization_test():
    print('=== Detailed Optimization Test ===')
    
    # Test only BTC-EUR with full detail
    ticker = 'BTC-EUR'
    df = load_crypto_data_yf(ticker, 1)
    
    if df is None or df.empty:
        print('❌ Failed to load data')
        return
    
    print(f'✅ Data loaded: {len(df)} rows')
    
    cfg = {
        'initial_capital': 10000,
        'commission_rate': 0.0018,
        'min_commission': 1.0,
        'order_round_factor': 0.01
    }
    
    # Manual optimization loop to see all results
    from signal_utils import calculate_support_resistance, assign_long_signals_extended, update_level_close_long, simulate_trades_compound_extended
    
    print(f'\n=== Testing all combinations for {ticker} ===')
    results = []
    
    for past_window in range(2, 8):  # Smaller range for testing
        for tw in range(1, 6):
            try:
                print(f'Testing past_window={past_window}, trade_window={tw}', end='... ')
                
                support, resistance = calculate_support_resistance(df, past_window, tw, verbose=False)
                signal_df = assign_long_signals_extended(support, resistance, df, tw, "1d")
                signal_df = update_level_close_long(signal_df, df)

                final_capital, _ = simulate_trades_compound_extended(
                    signal_df, 
                    cfg.get("initial_capital", 10000),
                    cfg.get("commission_rate", 0.001),
                    cfg.get("min_commission", 1.0),
                    cfg.get("order_round_factor", 1),
                    df
                )
                
                results.append({
                    "past_window": past_window,
                    "trade_window": tw,
                    "final_capital": final_capital
                })
                
                print(f'Final Capital: {final_capital:.2f}')
                
            except Exception as e:
                print(f'Error: {e}')
                continue
    
    # Show all results sorted by performance
    df_results = pd.DataFrame(results)
    df_sorted = df_results.sort_values("final_capital", ascending=False)
    
    print(f'\n=== All Results for {ticker} ===')
    print(df_sorted.to_string(index=False))
    
    # Show top 5
    print(f'\n=== Top 5 Combinations ===')
    print(df_sorted.head().to_string(index=False))

if __name__ == "__main__":
    detailed_optimization_test()
