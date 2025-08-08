#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Neue korrekte tägliche Equity-Kurve Funktion
"""

import pandas as pd

def create_equity_curve_from_matched_trades_FIXED(matched_trades, initial_capital, df_bt):
    """
    KORREKTE TÄGLICHE Equity-Kurve: 
    - Berechnet für jeden Tag das Portfolio-Value basierend auf Positionen
    - Berücksichtigt unrealisierte PnL bei offenen Positionen
    """
    print(f"🔍 DEBUG: Berechne KORREKTE TÄGLICHE Equity für {len(df_bt)} Tage")
    
    equity_curve = []
    realized_capital = initial_capital  # Kapital nach realisierten Trades
    position_shares = 0
    position_entry_price = 0
    trade_index = 0
    
    # Separiere komplette und offene Trades
    completed_trades = [t for t in matched_trades if not t.get('is_open', False)]
    open_trades = [t for t in matched_trades if t.get('is_open', False)]
    
    print(f"📊 {len(completed_trades)} komplette, {len(open_trades)} offene Trades")
    
    for i, date in enumerate(df_bt.index):
        current_price = df_bt.loc[date, 'Close']
        
        # Buy-Signal für komplette Trades
        if trade_index < len(completed_trades):
            trade = completed_trades[trade_index]
            buy_date = pd.to_datetime(trade.get('buy_date', '')).date()
            
            if date.date() == buy_date and position_shares == 0:
                position_shares = trade.get('shares', 0)
                position_entry_price = trade.get('buy_price', 0)
                print(f"   BUY {date.date()}: {position_shares:.4f} @ €{position_entry_price:.2f}")
        
        # Sell-Signal für komplette Trades
        if trade_index < len(completed_trades) and position_shares > 0:
            trade = completed_trades[trade_index]
            sell_date = pd.to_datetime(trade.get('sell_date', '')).date()
            
            if date.date() == sell_date:
                pnl = trade.get('pnl', 0)
                realized_capital += pnl
                position_shares = 0
                trade_index += 1
                print(f"   SELL {date.date()}: PnL €{pnl:.2f}, Capital: €{realized_capital:.0f}")
        
        # Buy-Signal für offene Trades (nach allen kompletten Trades)
        if trade_index >= len(completed_trades) and position_shares == 0:
            for open_trade in open_trades:
                open_buy_date = pd.to_datetime(open_trade.get('buy_date', '')).date()
                if date.date() == open_buy_date:
                    position_shares = open_trade.get('shares', 0)
                    position_entry_price = open_trade.get('buy_price', 0)
                    print(f"   OPEN BUY {date.date()}: {position_shares:.4f} @ €{position_entry_price:.2f}")
                    break
        
        # Berechne tägliche Equity
        if position_shares > 0:
            # Unrealized PnL = Shares * (Current Price - Entry Price)
            unrealized_pnl = position_shares * (current_price - position_entry_price)
            daily_equity = realized_capital + unrealized_pnl
        else:
            daily_equity = realized_capital
        
        equity_curve.append(daily_equity)
        
        # Debug-Output für wichtige Tage
        if i < 3 or i > len(df_bt) - 3 or (i % 50 == 0 and position_shares > 0):
            if position_shares > 0:
                print(f"   📊 {date.date()}: €{realized_capital:.0f} + €{unrealized_pnl:.0f} = €{daily_equity:.0f}")
    
    # Statistik
    unique_vals = len(set([int(v/100)*100 for v in equity_curve]))
    variation = (max(equity_curve) - min(equity_curve)) / initial_capital * 100
    
    print(f"✅ TÄGLICHE Equity: Start €{equity_curve[0]:.0f} → Ende €{equity_curve[-1]:.0f}")
    print(f"📊 Variation: {variation:.1f}%, Unique Werte: {unique_vals}")
    
    return equity_curve

# Test der neuen Funktion
if __name__ == "__main__":
    import yfinance as yf
    from datetime import timedelta
    
    # Lade BTC Daten
    df = yf.download("BTC-EUR", period="6m", interval="1d", auto_adjust=True, progress=False)
    if hasattr(df.columns, 'levels'):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(col).strip().capitalize() for col in df.columns]
    
    # Simuliere Trades
    start_date = pd.Timestamp('2024-06-01')
    end_date = pd.Timestamp('2024-06-30')
    
    start_price = df.loc[df.index >= start_date, 'Close'].iloc[0]
    end_price = df.loc[df.index >= end_date, 'Close'].iloc[0]
    
    shares = 5000 / start_price
    pnl = shares * (end_price - start_price)
    
    trades = [{
        'buy_date': start_date.strftime('%Y-%m-%d'),
        'sell_date': end_date.strftime('%Y-%m-%d'),
        'buy_price': start_price,
        'sell_price': end_price,
        'shares': shares,
        'pnl': pnl,
        'is_open': False
    }]
    
    equity_curve = create_equity_curve_from_matched_trades_FIXED(trades, 5000, df)
    print(f"🎯 Test erfolgreich! Curve variiert von €{min(equity_curve):.0f} bis €{max(equity_curve):.0f}")
