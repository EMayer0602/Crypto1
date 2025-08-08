#!/usr/bin/env python3
"""Debug why all parameter combinations give the same final capital"""

from crypto_backtesting_module import load_crypto_data_yf
from signal_utils import calculate_support_resistance, assign_long_signals_extended, update_level_close_long, simulate_trades_compound_extended
from crypto_tickers import crypto_tickers
from config import COMMISSION_RATE, MIN_COMMISSION
import pandas as pd

def debug_same_results():
    print('=== Debugging Same Results Problem ===')
    
    # Test BTC-EUR
    ticker = 'BTC-EUR'
    df = load_crypto_data_yf(ticker, 1)
    
    if df is None or df.empty:
        print('❌ Failed to load data')
        return
    
    print(f'✅ Data loaded: {len(df)} rows')
    
    # Get ticker config
    ticker_config = crypto_tickers.get(ticker, {})
    cfg = {
        'initial_capital': ticker_config.get('initialCapitalLong', 5000),
        'commission_rate': COMMISSION_RATE,
        'min_commission': MIN_COMMISSION,
        'order_round_factor': ticker_config.get('order_round_factor', 0.01)
    }
    
    print(f'Config: {cfg}')
    
    # Test a few different combinations manually
    test_combinations = [
        (2, 1),
        (3, 1), 
        (5, 2),
        (7, 3)
    ]
    
    for past_window, tw in test_combinations:
        print(f'\n--- Testing past_window={past_window}, trade_window={tw} ---')
        
        try:
            # Calculate support/resistance
            support, resistance = calculate_support_resistance(df, past_window, tw, verbose=False)
            print(f'   Support levels: {len(support)}')
            print(f'   Resistance levels: {len(resistance)}')
            
            # Generate signals
            signal_df = assign_long_signals_extended(support, resistance, df, tw, "1d")
            print(f'   Signal rows: {len(signal_df)}')
            
            # Check for actual signals
            buy_signals = signal_df[signal_df['Action'] == 'BUY'] if 'Action' in signal_df.columns else pd.DataFrame()
            sell_signals = signal_df[signal_df['Action'] == 'SELL'] if 'Action' in signal_df.columns else pd.DataFrame()
            none_signals = signal_df[signal_df['Action'] == 'None'] if 'Action' in signal_df.columns else pd.DataFrame()
            
            print(f'   BUY signals: {len(buy_signals)}')
            print(f'   SELL signals: {len(sell_signals)}') 
            print(f'   None signals: {len(none_signals)}')
            
            # Update level close
            signal_df = update_level_close_long(signal_df, df)
            
            # Run simulation
            final_capital, trades_df = simulate_trades_compound_extended(
                signal_df, 
                cfg['initial_capital'],
                cfg['commission_rate'],
                cfg['min_commission'],
                cfg['order_round_factor'],
                df
            )
            
            print(f'   Final capital: {final_capital}')
            if trades_df is not None and len(trades_df) > 0:
                print(f'   Executed trades: {len(trades_df)}')
                print(f'   First trade: {trades_df.iloc[0].to_dict()}' if len(trades_df) > 0 else '   No trades')
            else:
                print(f'   No trades executed!')
            
        except Exception as e:
            print(f'   ❌ Error: {e}')
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_same_results()
