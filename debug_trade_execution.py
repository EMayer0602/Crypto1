#!/usr/bin/env python3
"""Debug warum keine Trades ausgeführt werden"""

from crypto_backtesting_module import load_crypto_data_yf
from signal_utils import calculate_support_resistance, assign_long_signals_extended, simulate_trades_compound_extended
from crypto_tickers import crypto_tickers
from config import COMMISSION_RATE, MIN_COMMISSION
import pandas as pd

def debug_trades():
    print('=== Debug warum keine Trades ausgeführt werden ===')
    
    # Load BTC-EUR data
    df = load_crypto_data_yf('BTC-EUR', 1)
    if df is None or df.empty:
        print('❌ Failed to load data')
        return
    
    print(f'✅ Data loaded: {len(df)} rows')
    
    # Test mit einer spezifischen Kombination
    past_window = 5
    tw = 2
    
    # Ticker config
    ticker_config = crypto_tickers.get('BTC-EUR', {})
    cfg = {
        'initial_capital': ticker_config.get('initialCapitalLong', 5000),
        'commission_rate': COMMISSION_RATE,
        'min_commission': MIN_COMMISSION,
        'order_round_factor': ticker_config.get('order_round_factor', 0.01)
    }
    
    print(f'Config: {cfg}')
    
    # Generate signals
    support, resistance = calculate_support_resistance(df, past_window, tw, verbose=False)
    signals_df = assign_long_signals_extended(support, resistance, df, tw, "1d")
    
    print(f'\n=== Signals Analysis ===')
    print(f'Total signals: {len(signals_df)}')
    if len(signals_df) > 0:
        print('Columns:', list(signals_df.columns))
        
        # Action analysis
        action_counts = signals_df['Action'].value_counts()
        print(f'Actions: {dict(action_counts)}')
        
        # Show first few signals
        print('\n=== First 5 Signals ===')
        cols_to_show = ['Action', 'Level Close', 'Long Trade Day']
        for i, (idx, row) in enumerate(signals_df.head(5).iterrows()):
            print(f'Signal {i+1}: Action={row["Action"]}, Price={row["Level Close"]}, Date={row["Long Trade Day"]}')
    
    # Simulate trades
    print(f'\n=== Trade Simulation ===')
    final_capital, trades_df = simulate_trades_compound_extended(
        signals_df, 
        cfg['initial_capital'], 
        cfg['commission_rate'], 
        cfg['min_commission'], 
        cfg['order_round_factor'], 
        df
    )
    
    print(f'Initial Capital: {cfg["initial_capital"]}')
    print(f'Final Capital: {final_capital}')
    print(f'Number of trades: {len(trades_df)}')
    
    if len(trades_df) > 0:
        print('\n=== Trades ===')
        print(trades_df)
    else:
        print('❌ No trades executed!')
        
        # Debug warum keine trades
        print('\n=== Debug: Checking signals in detail ===')
        for i, (idx, row) in enumerate(signals_df.iterrows()):
            action = row.get('Action', '').lower()
            price = row.get('Level Close', 0)
            print(f'Row {i}: Action="{action}" (type: {type(action)}), Price={price} (type: {type(price)})')
            
            if action == 'buy':
                shares = round((cfg['initial_capital'] * 0.95) / price, 8)
                print(f'  → BUY: würde {shares} shares kaufen für {shares * price} EUR')
            elif action == 'sell':
                print(f'  → SELL signal (aber position=0)')
            
            if i >= 3:  # Only show first few
                break

if __name__ == "__main__":
    debug_trades()
