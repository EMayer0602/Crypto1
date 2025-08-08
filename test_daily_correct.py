#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KORREKTE tägliche Equity-Kurve: Berechnet über ganz df mit täglichen Open/Close Änderungen
"""

import pandas as pd

def create_equity_curve_DAILY_CORRECT(matched_trades, initial_capital, df_bt):
    """
    TÄGLICHE Equity-Kurve über ganz df:
    - Am BUY-Tag: Capital = Capital - Fees
    - Während Long: Capital = Capital + Shares * (Close - Open) 
    - Am SELL-Tag: Capital = Capital - Fees
    - Danach konstant bis nächster BUY
    """
    print(f"🔍 DEBUG: TÄGLICHE Equity über {len(df_bt)} Tage")
    
    equity_curve = []
    current_capital = initial_capital
    position_shares = 0
    is_long = False
    trade_index = 0
    
    # Separiere komplette und offene Trades
    completed_trades = [t for t in matched_trades if not t.get('is_open', False)]
    open_trades = [t for t in matched_trades if t.get('is_open', False)]
    
    print(f"📊 {len(completed_trades)} komplette, {len(open_trades)} offene Trades")
    
    for i, date in enumerate(df_bt.index):
        today_open = df_bt.loc[date, 'Open']
        today_close = df_bt.loc[date, 'Close']
        
        # ✅ 1. PRÜFE BUY-SIGNAL (komplette Trades)
        if trade_index < len(completed_trades) and not is_long:
            trade = completed_trades[trade_index]
            buy_date = pd.to_datetime(trade.get('buy_date', '')).date()
            
            if date.date() == buy_date:
                # BUY: Kaufkosten abziehen
                position_shares = trade.get('shares', 0)
                buy_fees = trade.get('buy_fees', 0) if 'buy_fees' in trade else 0
                
                current_capital -= buy_fees  # Fees abziehen
                is_long = True
                
                print(f"   📈 BUY {date.date()}: {position_shares:.4f} shares, Fees: €{buy_fees:.2f}, Capital: €{current_capital:.0f}")
        
        # ✅ 2. WÄHREND LONG-POSITION: Tägliche P&L
        if is_long and position_shares > 0:
            # Capital = Capital + Shares * (Close - Open)
            daily_pnl = position_shares * (today_close - today_open)
            current_capital += daily_pnl
            
            if i < 5 or i > len(df_bt) - 5 or (i % 50 == 0):
                print(f"   📊 LONG {date.date()}: Shares {position_shares:.4f} * (€{today_close:.2f} - €{today_open:.2f}) = €{daily_pnl:.2f}, Capital: €{current_capital:.0f}")
        
        # ✅ 3. PRÜFE SELL-SIGNAL (komplette Trades)
        if trade_index < len(completed_trades) and is_long:
            trade = completed_trades[trade_index]
            sell_date = pd.to_datetime(trade.get('sell_date', '')).date()
            
            if date.date() == sell_date:
                # SELL: Verkaufskosten abziehen
                sell_fees = trade.get('sell_fees', 0) if 'sell_fees' in trade else 0
                
                current_capital -= sell_fees  # Fees abziehen
                position_shares = 0
                is_long = False
                trade_index += 1
                
                print(f"   💰 SELL {date.date()}: Fees: €{sell_fees:.2f}, Capital: €{current_capital:.0f}")
        
        # ✅ 4. HANDLE OFFENE TRADES (nach allen kompletten Trades)
        if trade_index >= len(completed_trades) and not is_long:
            for open_trade in open_trades:
                open_buy_date = pd.to_datetime(open_trade.get('buy_date', '')).date()
                
                if date.date() == open_buy_date:
                    # OPEN BUY: Kaufkosten abziehen
                    position_shares = open_trade.get('shares', 0)
                    buy_fees = open_trade.get('buy_fees', 0) if 'buy_fees' in open_trade else 0
                    
                    current_capital -= buy_fees
                    is_long = True
                    
                    print(f"   🔓 OPEN BUY {date.date()}: {position_shares:.4f} shares, Fees: €{buy_fees:.2f}")
                    break
        
        # Equity-Wert für heute hinzufügen
        equity_curve.append(current_capital)
    
    # Statistiken
    unique_vals = len(set([int(v/100)*100 for v in equity_curve]))
    variation = (max(equity_curve) - min(equity_curve)) / initial_capital * 100
    
    print(f"✅ TÄGLICHE Equity: Start €{equity_curve[0]:.0f} → Ende €{equity_curve[-1]:.0f}")
    print(f"📊 Variation: {variation:.1f}%, Unique Werte: {unique_vals}")
    
    if unique_vals > 100:
        print("   ✅ Equity variiert TÄGLICH korrekt!")
    elif unique_vals > 20:
        print("   ⚠️ Equity variiert teilweise")
    else:
        print("   ❌ Equity variiert zu wenig")
    
    return equity_curve

# Test der neuen Funktion
if __name__ == "__main__":
    import yfinance as yf
    from datetime import timedelta
    
    print("🧪 TESTE KORREKTE TÄGLICHE EQUITY-BERECHNUNG")
    print("=" * 60)
    
    # Lade BTC Daten
    df = yf.download("BTC-EUR", period="3m", interval="1d", auto_adjust=True, progress=False)
    if hasattr(df.columns, 'levels'):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(col).strip().capitalize() for col in df.columns]
    
    # Simuliere einen Trade: 1 Monat Long-Position
    start_date = df.index[30]  # Tag 30
    end_date = df.index[60]    # Tag 60
    
    start_price = df.loc[start_date, 'Open']
    end_price = df.loc[end_date, 'Close']
    
    shares = 5000 / start_price
    pnl = shares * (end_price - start_price)
    buy_fees = 50  # €50 Kaufgebühren
    sell_fees = 50  # €50 Verkaufsgebühren
    
    print(f"📈 Test Trade: {start_date.date()} → {end_date.date()}")
    print(f"   Shares: {shares:.6f}")
    print(f"   Start: €{start_price:.2f}, End: €{end_price:.2f}")
    print(f"   PnL: €{pnl:.2f}, Fees: €{buy_fees + sell_fees}")
    
    # Erstelle Trades Liste mit Fees
    trades = [{
        'buy_date': start_date.strftime('%Y-%m-%d'),
        'sell_date': end_date.strftime('%Y-%m-%d'),
        'buy_price': start_price,
        'sell_price': end_price,
        'shares': shares,
        'pnl': pnl,
        'buy_fees': buy_fees,
        'sell_fees': sell_fees,
        'is_open': False
    }]
    
    # Berechne tägliche Equity-Kurve
    equity_curve = create_equity_curve_DAILY_CORRECT(trades, 5000, df)
    
    # Zeige Ergebnisse
    print(f"\n🎯 ERGEBNISSE:")
    print(f"   Start Equity: €{equity_curve[0]:.0f}")
    print(f"   Equity vor Trade: €{equity_curve[29]:.0f}")
    print(f"   Equity nach BUY: €{equity_curve[30]:.0f}")
    print(f"   Equity vor SELL: €{equity_curve[59]:.0f}")
    print(f"   Equity nach SELL: €{equity_curve[60]:.0f}")
    print(f"   End Equity: €{equity_curve[-1]:.0f}")
    
    # Prüfe Variation während Long-Position
    long_period_equity = equity_curve[30:60]
    long_variation = max(long_period_equity) - min(long_period_equity)
    print(f"   Long-Position Variation: €{long_variation:.0f}")
    
    if long_variation > 100:
        print("   ✅ Tägliche Variation während Long-Position erkannt!")
    else:
        print("   ❌ Zu wenig Variation während Long-Position")
