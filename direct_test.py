#!/usr/bin/env python3
"""Direct test of berechne_best_p_tw_long logic"""

from crypto_backtesting_module import load_crypto_data_yf
from signal_utils import calculate_support_resistance, assign_long_signals_extended, simulate_trades_compound_extended, update_level_close_long
from crypto_tickers import crypto_tickers
from config import COMMISSION_RATE, MIN_COMMISSION

def direct_test():
    print('=== DIRECT TEST OF BERECHNE_BEST_P_TW_LONG LOGIC ===')
    
    # Load data
    df = load_crypto_data_yf('BTC-EUR', 1)
    if df is None or df.empty:
        print('ERROR: Failed to load data')
        return
    
    print(f'Data loaded: {len(df)} rows')
    
    # Config
    ticker_config = crypto_tickers.get('BTC-EUR', {})
    cfg = {
        'initial_capital': ticker_config.get('initialCapitalLong', 5000),
        'commission_rate': COMMISSION_RATE,
        'min_commission': MIN_COMMISSION,
        'order_round_factor': ticker_config.get('order_round_factor', 0.01)
    }
    
    print(f'Config: {cfg}')
    
    # Test specific parameter combination
    past_window = 5
    tw = 2
    
    print(f'\n=== Testing past_window={past_window}, tw={tw} ===')
    
    try:
        df_opt = df.copy()
        
        # 1. Calculate support/resistance
        print('1. Calculating support/resistance...')
        support, resistance = calculate_support_resistance(df_opt, past_window, tw, verbose=True)
        
        # 2. Generate signals
        print('2. Generating signals...')
        signal_df = assign_long_signals_extended(support, resistance, df_opt, tw, "1d")
        print(f'   Signals generated: {len(signal_df)}')
        
        if not signal_df.empty:
            action_counts = signal_df['Action'].value_counts()
            print(f'   Action counts: {dict(action_counts)}')
        
        # 3. Update Level Close (CRITICAL STEP!)
        print('3. Updating Level Close...')
        signal_df = update_level_close_long(signal_df, df_opt)
        
        # Check for NaN values in Level Close
        nan_count = signal_df['Level Close'].isna().sum()
        print(f'   NaN values in Level Close: {nan_count}/{len(signal_df)}')
        
        if nan_count > 0:
            print('   WARNING: NaN values detected!')
            print(signal_df[signal_df['Level Close'].isna()][['Long Date detected', 'Level Close']])
        
        # 4. Simulate trades
        print('4. Simulating trades...')
        final_capital, trades_df = simulate_trades_compound_extended(
            signal_df, 
            cfg.get("initial_capital", 10000),
            cfg.get("commission_rate", 0.001),
            cfg.get("min_commission", 1.0),
            cfg.get("order_round_factor", 1),
            df_opt
        )
        
        print(f'Final Capital: {final_capital}')
        print(f'Initial Capital: {cfg["initial_capital"]}')
        print(f'Profit: {final_capital - cfg["initial_capital"]}')
        print(f'Trades executed: {len(trades_df) if not trades_df.empty else 0}')
        
        return final_capital
        
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
        return cfg["initial_capital"]

if __name__ == "__main__":
    direct_test()
