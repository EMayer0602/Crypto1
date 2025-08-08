#!/usr/bin/env python3
"""Debug script to test berechne_best_p_tw_long in detail"""

from signal_utils import berechne_best_p_tw_long, calculate_support_resistance, assign_long_signals_extended, update_level_close_long, simulate_trades_compound_extended
from crypto_backtesting_module import load_crypto_data_yf
import pandas as pd
import traceback

def debug_optimization():
    print('=== Debugging berechne_best_p_tw_long ===')
    
    # Load data
    df = load_crypto_data_yf('BTC-EUR', 1)
    if df is None or df.empty:
        print('❌ Failed to load data')
        return
    
    print(f'✅ Data loaded: {len(df)} rows')
    
    # Test configuration
    cfg = {
        'initial_capital': 10000,
        'commission_rate': 0.0018,
        'min_commission': 1.0,
        'order_round_factor': 0.01
    }
    
    start_idx = 0
    end_idx = len(df)
    
    print(f'Testing optimization with cfg: {cfg}')
    print(f'Data range: {start_idx} to {end_idx} (length: {end_idx - start_idx})')
    
    # Test one iteration manually
    print('\n=== Manual test of one optimization iteration ===')
    past_window = 5
    tw = 2
    
    try:
        df_opt = df.iloc[start_idx:end_idx].copy()
        print(f'✅ df_opt created: {len(df_opt)} rows')
        
        support, resistance = calculate_support_resistance(df_opt, past_window, tw, verbose=True)
        print(f'✅ Support/Resistance calculated: {len(support)} support, {len(resistance)} resistance levels')
        
        signal_df = assign_long_signals_extended(support, resistance, df_opt, tw, "1d")
        print(f'✅ Signals assigned: {len(signal_df)} rows')
        
        signal_df = update_level_close_long(signal_df, df_opt)
        print(f'✅ Level close updated: {len(signal_df)} rows')
        
        # Check if signal_df has any trades
        buy_signals = signal_df[signal_df['Action'] == 'BUY']
        sell_signals = signal_df[signal_df['Action'] == 'SELL']
        print(f'📊 Trade signals: {len(buy_signals)} BUY, {len(sell_signals)} SELL')
        
        if len(buy_signals) > 0 or len(sell_signals) > 0:
            print('   Sample signals:')
            if len(buy_signals) > 0:
                print(f'   First BUY: {buy_signals.iloc[0].name} - {buy_signals.iloc[0]["Action"]}')
            if len(sell_signals) > 0:
                print(f'   First SELL: {sell_signals.iloc[0].name} - {sell_signals.iloc[0]["Action"]}')
        
        final_capital, trades_df = simulate_trades_compound_extended(
            signal_df, 
            cfg.get("initial_capital", 10000),
            cfg.get("commission_rate", 0.001),
            cfg.get("min_commission", 1.0),
            cfg.get("order_round_factor", 1),
            df_opt
        )
        
        print(f'✅ Simulation completed: Final capital = {final_capital}')
        if trades_df is not None:
            print(f'   Trades: {len(trades_df)} executed')
        
    except Exception as e:
        print(f'❌ Manual test failed: {e}')
        traceback.print_exc()
        return
    
    # Now test the full optimization
    print('\n=== Testing full optimization ===')
    try:
        p, tw = berechne_best_p_tw_long(df, cfg, start_idx, end_idx, verbose=True, ticker='BTC-EUR')
        print(f'✅ Full optimization result: Past={p}, Trade={tw}')
    except Exception as e:
        print(f'❌ Full optimization failed: {e}')
        traceback.print_exc()

if __name__ == "__main__":
    debug_optimization()
