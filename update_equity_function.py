#!/usr/bin/env python3
"""
Update the equity function in plotly_utils.py
"""

import re

def update_equity_function():
    print("🔄 Updating create_equity_curve_from_matched_trades function...")
    
    # Read the file
    with open('plotly_utils.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The new function implementation
    new_function = '''def create_equity_curve_from_matched_trades(matched_trades, initial_capital, df_bt):
    """
    KORREKTE TÄGLICHE Equity über ganz df:
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
                # BUY: Schätze Fees basierend auf Trade-Daten
                position_shares = trade.get('shares', 0)
                buy_price = trade.get('buy_price', 0)
                total_pnl = trade.get('pnl', 0)
                sell_price = trade.get('sell_price', 0)
                
                # Schätze Fees: Total PnL = Shares * (Sell - Buy) - Fees
                theoretical_pnl = position_shares * (sell_price - buy_price)
                estimated_fees = theoretical_pnl - total_pnl if theoretical_pnl > total_pnl else 0
                buy_fees = estimated_fees / 2  # Verteile auf Buy und Sell
                
                current_capital -= buy_fees  # Fees abziehen
                is_long = True
                
                if i < 5 or i > len(df_bt) - 5:
                    print(f"   📈 BUY {date.date()}: {position_shares:.4f} shares, Fees: €{buy_fees:.2f}, Capital: €{current_capital:.0f}")
        
        # ✅ 2. WÄHREND LONG-POSITION: Tägliche P&L
        if is_long and position_shares > 0:
            # Capital = Capital + Shares * (Close - Open)
            daily_pnl = position_shares * (today_close - today_open)
            current_capital += daily_pnl
            
            if i < 3 or i > len(df_bt) - 3 or (i % 100 == 0):
                print(f"   📊 LONG {date.date()}: {position_shares:.4f} * (€{today_close:.2f} - €{today_open:.2f}) = €{daily_pnl:.2f}, Capital: €{current_capital:.0f}")
        
        # ✅ 3. PRÜFE SELL-SIGNAL (komplette Trades)
        if trade_index < len(completed_trades) and is_long:
            trade = completed_trades[trade_index]
            sell_date = pd.to_datetime(trade.get('sell_date', '')).date()
            
            if date.date() == sell_date:
                # SELL: Verwende geschätzte Fees
                total_pnl = trade.get('pnl', 0)
                buy_price = trade.get('buy_price', 0)
                sell_price = trade.get('sell_price', 0)
                theoretical_pnl = position_shares * (sell_price - buy_price)
                estimated_fees = theoretical_pnl - total_pnl if theoretical_pnl > total_pnl else 0
                sell_fees = estimated_fees / 2
                
                current_capital -= sell_fees  # Fees abziehen
                position_shares = 0
                is_long = False
                trade_index += 1
                
                if i < 5 or i > len(df_bt) - 5:
                    print(f"   💰 SELL {date.date()}: Fees: €{sell_fees:.2f}, Capital: €{current_capital:.0f}")
        
        # ✅ 4. HANDLE OFFENE TRADES (nach allen kompletten Trades)
        if trade_index >= len(completed_trades) and not is_long:
            for open_trade in open_trades:
                open_buy_date = pd.to_datetime(open_trade.get('buy_date', '')).date()
                
                if date.date() == open_buy_date:
                    # OPEN BUY: Schätze Buy-Fees
                    position_shares = open_trade.get('shares', 0)
                    buy_price = open_trade.get('buy_price', 0)
                    estimated_buy_fees = position_shares * buy_price * 0.001  # 0.1% geschätzt
                    
                    current_capital -= estimated_buy_fees
                    is_long = True
                    
                    if i < 5 or i > len(df_bt) - 5:
                        print(f"   🔓 OPEN BUY {date.date()}: {position_shares:.4f} shares, Fees: €{estimated_buy_fees:.2f}")
                    break
        
        # Equity-Wert für heute hinzufügen
        equity_curve.append(current_capital)
    
    # Statistiken
    unique_vals = len(set([int(v/50)*50 for v in equity_curve]))
    variation = (max(equity_curve) - min(equity_curve)) / initial_capital * 100
    
    print(f"✅ TÄGLICHE Equity: Start €{equity_curve[0]:.0f} → Ende €{equity_curve[-1]:.0f}")
    print(f"📊 Variation: {variation:.1f}%, Unique Werte: {unique_vals}")
    
    if unique_vals > 50:
        print("   ✅ Equity variiert TÄGLICH korrekt!")
    elif unique_vals > 10:
        print("   ⚠️ Equity variiert teilweise")
    else:
        print("   ❌ Equity variiert zu wenig")
    
    return equity_curve'''
    
    # Pattern to match the entire function
    pattern = r'def create_equity_curve_from_matched_trades\(matched_trades, initial_capital, df_bt\):.*?(?=\n\ndef |\nclass |\Z)'
    
    # Replace the function
    new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    if new_content != content:
        # Write the updated content back
        with open('plotly_utils.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Function updated successfully!")
        return True
    else:
        print("❌ Function not found or not replaced")
        return False

if __name__ == "__main__":
    success = update_equity_function()
    if success:
        print("🎯 plotly_utils.py updated with new equity function!")
    else:
        print("❌ Failed to update function")
