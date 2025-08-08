#!/usr/bin/env python3
"""Test optimization results with different parameters"""

from crypto_backtesting_module import optimize_parameters, load_crypto_data_yf
from signal_utils import berechne_best_p_tw_long
from crypto_tickers import crypto_tickers
from config import COMMISSION_RATE, MIN_COMMISSION
import pandas as pd

def test_optimization_results():
    print('=== Testing Optimization Results ===')
    
    # Load BTC-EUR data
    df = load_crypto_data_yf('BTC-EUR', 1)
    if df is None or df.empty:
        print('ERROR: Failed to load data')
        return
    
    print(f'Data loaded: {len(df)} rows')
    
    # Load ticker config
    ticker_config = crypto_tickers.get('BTC-EUR', {})
    cfg = {
        'initial_capital': ticker_config.get('initialCapitalLong', 5000),
        'commission_rate': COMMISSION_RATE,
        'min_commission': MIN_COMMISSION,
        'order_round_factor': ticker_config.get('order_round_factor', 0.01)
    }
    
    print(f'Config: {cfg}')
    
    # Test optimize_parameters
    print('\n=== Testing optimize_parameters ===')
    result = optimize_parameters(df, 'BTC-EUR')
    print(f'optimize_parameters result: {result}')
    
    # Test berechne_best_p_tw_long directly
    print('\n=== Testing berechne_best_p_tw_long ===')
    best_p, best_tw = berechne_best_p_tw_long(df, cfg, 0, len(df), verbose=False, ticker='BTC-EUR')
    print(f'berechne_best_p_tw_long result: Past={best_p}, Trade={best_tw}')
    
    # Test a few specific parameter combinations
    from signal_utils import calculate_support_resistance, assign_long_signals_extended, simulate_trades_compound_extended
    
    print('\n=== Testing specific parameter combinations ===')
    test_combinations = [(2, 1), (5, 2), (10, 3), (15, 5)]
    
    results = []
    for past_window, tw in test_combinations:
        print(f'\nTesting past_window={past_window}, tw={tw}')
        
        support, resistance = calculate_support_resistance(df, past_window, tw, verbose=False)
        signal_df = assign_long_signals_extended(support, resistance, df, tw, "1d")
        
        if not signal_df.empty:
            action_counts = signal_df['Action'].value_counts()
            print(f'  Actions: {dict(action_counts)}')
            
            final_capital, trades_df = simulate_trades_compound_extended(
                signal_df, cfg['initial_capital'], cfg['commission_rate'], 
                cfg['min_commission'], cfg['order_round_factor'], df
            )
            
            profit = final_capital - cfg['initial_capital']
            print(f'  Final capital: {final_capital:.2f} (profit: {profit:.2f})')
            
            results.append({
                'past_window': past_window,
                'tw': tw,
                'final_capital': final_capital,
                'profit': profit,
                'num_trades': len(trades_df) if not trades_df.empty else 0
            })
        else:
            print('  No signals generated')
            results.append({
                'past_window': past_window,
                'tw': tw,
                'final_capital': cfg['initial_capital'],
                'profit': 0,
                'num_trades': 0
            })
    
    print('\n=== Summary of Results ===')
    for result in results:
        print(f"Past={result['past_window']:2d}, TW={result['tw']:2d}: "
              f"Final={result['final_capital']:8.2f}, "
              f"Profit={result['profit']:8.2f}, "
              f"Trades={result['num_trades']:2d}")
    
    # Find best combination
    best_result = max(results, key=lambda x: x['final_capital'])
    print(f"\nBest combination: Past={best_result['past_window']}, TW={best_result['tw']} "
          f"with profit={best_result['profit']:.2f}")

if __name__ == "__main__":
    test_optimization_results()
