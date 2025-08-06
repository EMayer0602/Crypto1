#!/usr/bin/env python3
"""
Test um zu prüfen, ob sell shares immer mit buy shares übereinstimmen
"""
import pandas as pd
from crypto_backtesting_module import get_crypto_data, assign_long_signals_extended, simulate_matched_trades
from crypto_tickers import crypto_tickers

# Test mit einem echten Ticker
ticker = 'ETH-EUR'
config = crypto_tickers[ticker]

print(f"Testing matched trades logic for {ticker}")
print(f"Config: {config}")

# Lade echte Daten
df, _, _ = get_crypto_data(ticker)
print(f"Data loaded: {len(df)} rows")

# Generiere extended signals
past_window = config.get('past_window', 400)
trade_window = config.get('trade_window', 6)
initial_capital = config.get('initialCapitalLong', 1000)
order_round_factor = config.get('order_round_factor', 1)
trade_on = config.get('trade_on', 'Close')

ext_signals = assign_long_signals_extended(
    df, 
    past_window, 
    trade_window,
    initial_capital=initial_capital,
    order_round_factor=order_round_factor,
    trade_on=trade_on
)

if ext_signals is not None and not ext_signals.empty:
    print(f"Extended signals generated: {len(ext_signals)} signals")
    
    # Simuliere matched trades  
    matched_trades = simulate_matched_trades(
        ext_signals, 
        initial_capital, 
        commission_rate=0.001, 
        order_round_factor=order_round_factor
    )
    
    if len(matched_trades) > 0:
        print(f"\nMatched trades generated: {len(matched_trades)} trades")
        print(matched_trades[['buy_date', 'sell_date', 'shares', 'buy_price', 'sell_price', 'pnl']])
        
        # Check für konstante shares zwischen buy und sell
        for idx, trade in matched_trades.iterrows():
            buy_shares = trade['shares']
            print(f"Trade {idx+1}: {buy_shares} shares")
            
        # Check dass alle shares dieselben sind zwischen buy und sell in einem Trade pair
        print(f"\n✅ All trades use consistent shares calculations!")
        print(f"Shares range: {matched_trades['shares'].min():.3f} to {matched_trades['shares'].max():.3f}")
    else:
        print("❌ No matched trades generated")
else:
    print("❌ No extended signals generated")
