#!/usr/bin/env python3
"""
Script um die Weekly Trades Sektion in crypto_backtesting_module.py zu reparieren
"""

def fix_weekly_trades_section():
    """
    Repariert die doppelten/kaputten Weekly Trades Sektionen
    """
    
    # Lesen der aktuellen Datei
    with open('crypto_backtesting_module.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Finden der START und END Marker
    start_marker = "# ✅ EINFACHE TRADES LISTE DER LETZTEN 2 WOCHEN"
    end_marker = "        return result"
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("❌ Start marker nicht gefunden")
        return False
        
    # Finden des ersten return result nach dem start marker
    temp_content = content[start_idx:]
    end_idx = temp_content.find(end_marker)
    if end_idx == -1:
        print("❌ End marker nicht gefunden")
        return False
    
    # Korrigierte Sektion
    correct_section = '''        # ✅ EXTENDED TRADES LISTE DER LETZTEN 2 WOCHEN
        print(f"\\n📅 TRADES DER LETZTEN 2 WOCHEN - {symbol}")
        print("="*80)
        if ext_full is not None and not ext_full.empty:
            print(f"🔍 DEBUG: Extended Trades Spalten: {list(ext_full.columns)}")
            print(f"🔍 DEBUG: Anzahl Extended Trades: {len(ext_full)}")
            
            # Einfach die letzten 14 Tage filtern mit den extended trades
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=14)
            
            # Filter extended trades der letzten 2 Wochen 
            recent_ext_trades = ext_full[
                pd.to_datetime(ext_full.index) >= cutoff_date
            ].copy()
            
            if not recent_ext_trades.empty:
                print(f"📈 {len(recent_ext_trades)} Extended Trades in den letzten 2 Wochen:")
                print("-" * 80)
                
                for idx, (date, trade) in enumerate(recent_ext_trades.iterrows()):
                    trade_date = date.strftime('%Y-%m-%d')
                    
                    # Extended trades structure
                    action = trade.get('Long Action', 'N/A')
                    if action == 'N/A':
                        action = trade.get('Action', 'N/A')
                    
                    price = trade.get('Close', 0)
                    
                    today = datetime.now().date()
                    current_trade_date = pd.to_datetime(date).date()
                    
                    if current_trade_date == today:
                        type_desc = "Artificial"
                    else:
                        type_desc = "Limit"
                    
                    if action in ['BUY', 'Buy']:
                        action_emoji = "🔓 BUY"
                    elif action in ['SELL', 'Sell']:
                        action_emoji = "🔒 SELL"
                    else:
                        action_emoji = f"📊 {action}"
                    
                    print(f"  {idx+1}. {symbol} | {action_emoji} | {trade_date} | Type: {type_desc} | Price: {price:.4f}")
                    
                # Für HTML Report
                result['weekly_trades_html'] = f"<h3>Extended Trades der letzten 2 Wochen: {len(recent_ext_trades)}</h3>"
                result['weekly_trades_count'] = len(recent_ext_trades)
            else:
                print("📈 Keine Extended Trades in den letzten 2 Wochen")
                result['weekly_trades_html'] = "<h3>Keine Extended Trades in den letzten 2 Wochen</h3>"
                result['weekly_trades_count'] = 0
        else:
            print("⚠️ Keine Extended Trades verfügbar")
            result['weekly_trades_html'] = ""
            result['weekly_trades_count'] = 0

        return result'''
    
    # Ersetzen des korrekten Teils
    new_content = content[:start_idx] + correct_section + content[start_idx + end_idx + len(end_marker):]
    
    # Schreiben der korrigierten Datei
    with open('crypto_backtesting_module.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Weekly Trades Sektion repariert!")
    return True

if __name__ == "__main__":
    fix_weekly_trades_section()
