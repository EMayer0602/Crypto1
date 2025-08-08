#!/usr/bin/env python3
"""Simple Debug für Trade Simulation"""

from crypto_backtesting_module import load_crypto_data_yf
from signal_utils import calculate_support_resistance, assign_long_signals_extended, simulate_trades_compound_extended
from crypto_tickers import crypto_tickers
from config import COMMISSION_RATE, MIN_COMMISSION

def simple_debug():
    print('SIMPLE DEBUG START')
    
    # Load data
    df = load_crypto_data_yf('BTC-EUR', 1)
    print(f'Data loaded: {len(df)} rows')
    
    # Config
    cfg = {
        'initial_capital': 5000,
        'commission_rate': COMMISSION_RATE,
        'min_commission': MIN_COMMISSION,
        'order_round_factor': 0.01
    }
    print(f'Initial Capital: {cfg["initial_capital"]}')
    
    # Generate signals
    support, resistance = calculate_support_resistance(df, 5, 2, verbose=False)
    signals_df = assign_long_signals_extended(support, resistance, df, 2, "1d")
    print(f'Generated {len(signals_df)} signals')
    
    # Simulate
    final_capital, trades_df = simulate_trades_compound_extended(
        signals_df, 5000, COMMISSION_RATE, MIN_COMMISSION, 0.01, df
    )
    
    print(f'RESULT: Initial={5000}, Final={final_capital}, Trades={len(trades_df)}')
    
    if final_capital == 5000:
        print('ERROR: Final = Initial, NO TRADES!')
    else:
        print('SUCCESS: Capital changed!')

if __name__ == "__main__":
    simple_debug()
