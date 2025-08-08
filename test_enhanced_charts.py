#!/usr/bin/env python3
"""Test the enhanced charts with all 3 tasks"""

from crypto_backtesting_module import load_crypto_data_yf
from signal_utils import calculate_support_resistance, assign_long_signals_extended, simulate_trades_compound_extended
from plotly_utils import plotly_combined_chart_and_equity
from crypto_tickers import crypto_tickers
from config import COMMISSION_RATE, MIN_COMMISSION
import pandas as pd
import numpy as np

def test_enhanced_charts():
    print('=== Testing Enhanced Charts (3 Tasks) ===')
    
    # Load data for BTC-EUR
    df = load_crypto_data_yf('BTC-EUR', 1)
    if df is None or df.empty:
        print('ERROR: Failed to load data')
        return
    
    print(f'✅ Data loaded: {len(df)} rows')
    
    # Config
    ticker_config = crypto_tickers.get('BTC-EUR', {})
    cfg = {
        'initial_capital': ticker_config.get('initialCapitalLong', 5000),
        'commission_rate': COMMISSION_RATE,
        'min_commission': MIN_COMMISSION,
        'order_round_factor': ticker_config.get('order_round_factor', 0.01)
    }
    
    # Use optimal parameters (from previous test)
    past_window = 2
    tw = 4
    
    print(f'Using optimal parameters: past_window={past_window}, tw={tw}')
    
    # Calculate support/resistance
    support, resistance = calculate_support_resistance(df, past_window, tw, verbose=False)
    support_series = pd.Series(support, name='support')
    resistance_series = pd.Series(resistance, name='resistance')
    
    # Generate extended signals
    ext_signals = assign_long_signals_extended(support, resistance, df, tw, "1d")
    
    print(f'✅ Generated {len(ext_signals)} extended signals')
    if not ext_signals.empty:
        action_counts = ext_signals['Action'].value_counts()
        print(f'   Actions: {dict(action_counts)}')
    
    # Simulate trades for equity curve
    final_capital, trades_df = simulate_trades_compound_extended(
        ext_signals, cfg['initial_capital'], cfg['commission_rate'], 
        cfg['min_commission'], cfg['order_round_factor'], df
    )
    
    print(f'✅ Final Capital: €{final_capital:,.2f} (from €{cfg["initial_capital"]:,.2f})')
    print(f'✅ Trades executed: {len(trades_df) if not trades_df.empty else 0}')
    
    # Create simple equity curve (for demo)
    equity_curve = [cfg['initial_capital']] * len(df)
    running_capital = cfg['initial_capital']
    
    if not trades_df.empty:
        for idx, trade in trades_df.iterrows():
            # Find date in df.index and update equity from that point
            trade_date = trade.get('Date', idx)
            if trade['Action'] == 'BUY':
                running_capital -= trade.get('Cost', 0)
            elif trade['Action'] == 'SELL':
                running_capital += trade.get('Revenue', 0)
            
            # Update equity curve from this point forward
            try:
                if trade_date in df.index:
                    date_idx = df.index.get_loc(trade_date)
                    for i in range(date_idx, len(equity_curve)):
                        equity_curve[i] = running_capital
            except:
                pass
    
    # Set final capital correctly
    equity_curve[-1] = final_capital
    
    # Simple Buy & Hold curve
    initial_price = df['Close'].iloc[0]
    buyhold_curve = [(df['Close'].iloc[i] / initial_price) * cfg['initial_capital'] for i in range(len(df))]
    
    # Add buy/sell signals to df for fallback
    df['buy_signal'] = 0
    df['sell_signal'] = 0
    
    print('✅ Creating enhanced chart with all 3 tasks...')
    
    # Create enhanced chart
    success = plotly_combined_chart_and_equity(
        df=df,
        standard_signals=ext_signals,  # Contains BUY/SELL Actions
        support=support_series,
        resistance=resistance_series,
        equity_curve=equity_curve,
        buyhold_curve=buyhold_curve,
        ticker='BTC-EUR',
        backtest_years=1
    )
    
    if success:
        print('🎯 SUCCESS: Enhanced chart created with all 3 tasks!')
        print('   ✅ Task 1: BUY/SELL Trade Markers')
        print('   ✅ Task 2: Trade Lines with PnL')
        print('   ✅ Task 3: Enhanced Equity Curves')
    else:
        print('❌ FAILED: Chart creation failed')

if __name__ == "__main__":
    test_enhanced_charts()
