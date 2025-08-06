"""
Saubere Extended Trades Processing-Logik 
"""

def process_weekly_extended_trades(ext_full, df, symbol, config, cutoff_date):
    """
    Verarbeitet Extended Trades für die letzten 2 Wochen
    """
    from datetime import datetime
    import pandas as pd
    
    weekly_trades = []
    processed_indices = set()  # Duplikat-Kontrolle
    
    if ext_full is None or ext_full.empty:
        return {
            'weekly_trades_html': "<p>Keine Extended Trades verfügbar</p>",
            'weekly_trades_count': 0,
            'weekly_trades_data': []
        }
    
    print(f"🔍 Suche Extended Trades seit {cutoff_date.strftime('%Y-%m-%d')}")
    
    # Iteriere durch alle Extended Trades
    for ext_idx, row in ext_full.iterrows():
        # Duplikat-Check
        if ext_idx in processed_indices:
            continue
            
        action = row.get('Action', '')
        if action in ['buy', 'sell', 'BUY', 'SELL']:
            # Verwende "Long Trade Day" als Trade-Datum
            trade_date = row.get('Long Trade Day')
            if trade_date is None or pd.isna(trade_date):
                continue
            
            # Konvertiere zu Timestamp
            if not isinstance(trade_date, pd.Timestamp):
                trade_date = pd.to_datetime(trade_date)
            
            # Prüfe ob das Datum in den letzten 2 Wochen liegt
            if trade_date >= cutoff_date:
                # Erstelle Trade-Eintrag mit Rundung für Shares
                shares = row.get('shares', None)
                if isinstance(shares, (int, float)):
                    shares = round(shares, 4)
                
                trade_entry = {
                    'Symbol': symbol,
                    'Action': action.upper(),
                    'Date': trade_date,
                    'ExtIndex': ext_idx,
                    'OriginalIndex': ext_idx,
                    'Shares': shares
                }
                weekly_trades.append(trade_entry)
                processed_indices.add(ext_idx)  # Markiere als verarbeitet
                print(f"✅ {action.upper()} am {trade_date.strftime('%Y-%m-%d')} (ExtIdx: {ext_idx})")
    
    # Sortiere Trades nach Datum
    weekly_trades.sort(key=lambda x: x['Date'])
    
    print(f"\n📈 {len(weekly_trades)} Extended Trades der letzten 2 Wochen:")
    
    if not weekly_trades:
        return {
            'weekly_trades_html': "<p>Keine Extended Trades in den letzten 2 Wochen</p>",
            'weekly_trades_count': 0,
            'weekly_trades_data': []
        }
    
    print("-" * 80)
    
    # Console und HTML Output
    html_content = "<table class='trades-table'><tr><th>Trade #</th><th>Symbol</th><th>Action</th><th>Date</th><th>Type</th><th>Price</th></tr>"
    
    for i, trade in enumerate(weekly_trades):
        action = trade['Action']
        date_str = trade['Date'].strftime('%Y-%m-%d')
        
        # Trade-Typ bestimmen
        today = datetime.now().date()
        if trade['Date'].date() == today:
            trade_type = "Artificial"
        else:
            trade_type = "Limit"
        
        # Preisformatierung basierend auf trade_on Setting
        trade_on = config.get('trade_on', 'close').lower()
        try:
            if trade['Date'].date() == today:
                # Heutiger Trade - verwende artificial price
                current_price = df.loc[trade['Date'], 'Close']
                price_str = f"Artificial: {current_price:.4f}"
            else:
                # Vergangener Trade - unterscheide zwischen trade_on Settings
                if trade_on == 'close':
                    # Für trade_on="Close": Nur Close-Preis anzeigen
                    close_price = df.loc[trade['Date'], 'Close']
                    price_str = f"Close: {close_price:.4f}"
                else:
                    # Für trade_on="open": Open/Close Format anzeigen
                    open_price = df.loc[trade['Date'], 'Open']
                    close_price = df.loc[trade['Date'], 'Close']
                    price_str = f"<Open={open_price:.4f}, Close={close_price:.4f}>"
        except (KeyError, IndexError):
            price_str = "Price: N/A"
        
        # Emoji für Action
        if action == 'BUY':
            emoji = "🔓"
        elif action == 'SELL':
            emoji = "🔒"
        else:
            emoji = "📊"
        
        # Console Output
        print(f"  {i+1}. {symbol} | {emoji} {action} | {date_str} | Type: {trade_type} | {price_str}")
        
        # HTML Output
        html_content += f"<tr><td>{i+1}</td><td>{symbol}</td><td>{emoji} {action}</td><td>{date_str}</td><td>{trade_type}</td><td>{price_str}</td></tr>"
    
    html_content += "</table>"
    
    return {
        'weekly_trades_html': html_content,
        'weekly_trades_count': len(weekly_trades),
        'weekly_trades_data': weekly_trades
    }
