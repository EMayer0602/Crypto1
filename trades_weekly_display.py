#!/usr/bin/env python3
"""
TRADES WEEKLY DISPLAY MODULE
Zeigt Trades der letzten Woche sortiert nach Datum an.
- Limit Orders mit <Open, Close> für vergangene Tage
- Artificial Open, Close für heute
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

def get_last_week_trades(matched_trades: List[Dict], data_df: pd.DataFrame, days_back: int = 14) -> List[Dict]:
    """
    Filtert Trades der letzten 2 Wochen (14 Tage)
    
    Args:
        matched_trades: Liste der matched trades
        data_df: DataFrame mit OHLCV Daten 
        days_back: Anzahl Tage zurück (default 14 für 2 Wochen)
    
    Returns:
        List[Dict]: Gefilterte Trades der letzten 2 Wochen
    """
    try:
        if not matched_trades:
            return []
        
        # Cutoff Date berechnen
        today = datetime.now().date()
        cutoff_date = today - timedelta(days=days_back)
        
        last_week_trades = []
        
        for trade in matched_trades:
            # Buy Date prüfen
            buy_date_str = trade.get('buy_date', '')
            if buy_date_str:
                try:
                    buy_date = pd.to_datetime(buy_date_str).date()
                    if buy_date >= cutoff_date:
                        last_week_trades.append(trade)
                        continue
                except:
                    pass
            
            # Sell Date prüfen für offene Trades
            sell_date_str = trade.get('sell_date', '')
            if sell_date_str:
                try:
                    sell_date = pd.to_datetime(sell_date_str).date()
                    if sell_date >= cutoff_date:
                        last_week_trades.append(trade)
                except:
                    pass
        
        print(f"📅 Gefiltert: {len(last_week_trades)} Trades der letzten {days_back} Tage")
        
        # ✅ EXPLIZIT HEUTE'S TRADES HINZUFÜGEN
        today_trades = get_todays_trades(data_df)
        if today_trades:
            print(f"🤖 Heute's Trades hinzugefügt: {len(today_trades)}")
            last_week_trades.extend(today_trades)
        
        return last_week_trades
        
    except Exception as e:
        print(f"❌ Fehler in get_last_week_trades: {e}")
        return []

def get_todays_trades(data_df: pd.DataFrame) -> List[Dict]:
    """
    Erstellt künstliche Trades für heute basierend auf verfügbaren Daten
    
    Args:
        data_df: DataFrame mit OHLCV Daten
    
    Returns:
        List[Dict]: Liste mit heute's Trades (falls Daten verfügbar)
    """
    try:
        today = datetime.now().date()
        today_datetime = pd.Timestamp(today)
        
        # Prüfe ob heute's Daten verfügbar sind
        if today_datetime in data_df.index:
            today_data = data_df.loc[today_datetime]
            
            # Erstelle künstlichen Trade für heute
            today_trade = {
                'buy_date': today.strftime('%Y-%m-%d'),
                'sell_date': '',  # Offener Trade
                'buy_price': today_data['Open'],
                'sell_price': today_data['Close'],
                'shares': 1.0,  # Dummy Shares
                'pnl': today_data['Close'] - today_data['Open'],  # Intraday P&L
                'is_open': True,  # Trade ist heute geöffnet
                'trade_type': 'artificial',
                'is_today': True
            }
            
            print(f"🤖 Heute's künstlicher Trade erstellt: Open={today_data['Open']:.4f}, Close={today_data['Close']:.4f}")
            return [today_trade]
        else:
            print(f"⚠️ Keine Daten für heute ({today}) verfügbar")
            return []
            
    except Exception as e:
        print(f"❌ Fehler in get_todays_trades: {e}")
        return []

def classify_trade_type(trade_date: datetime, data_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Klassifiziert Trade-Typ basierend auf Datum
    
    Args:
        trade_date: Datum des Trades
        data_df: DataFrame mit OHLCV Daten
    
    Returns:
        Dict mit Trade-Type Info
    """
    today = datetime.now().date()
    trade_date_only = trade_date.date() if hasattr(trade_date, 'date') else trade_date
    
    # Prüfe ob heute
    is_today = (trade_date_only == today)
    
    # Suche Daten für das Datum
    trade_data = None
    if trade_date in data_df.index:
        trade_data = data_df.loc[trade_date]
    
    if is_today:
        # HEUTE = Artificial
        return {
            'type': 'artificial',
            'display_name': 'Artificial',
            'price_format': 'Open={open:.4f}, Close={close:.4f}',
            'is_today': True,
            'data': trade_data
        }
    else:
        # VERGANGENE TAGE = Limit Orders
        return {
            'type': 'limit_order',
            'display_name': 'Limit Order',
            'price_format': '<Open={open:.4f}, Close={close:.4f}>',
            'is_today': False,
            'data': trade_data
        }

def format_trade_for_display(trade: Dict, trade_type: Dict, data_df: pd.DataFrame) -> str:
    """
    Formatiert einen Trade für die Anzeige
    
    Args:
        trade: Trade Dictionary
        trade_type: Trade Type Info
        data_df: DataFrame mit OHLCV Daten
    
    Returns:
        str: Formatierte Trade-Zeile
    """
    try:
        # Basis-Info extrahieren
        buy_date = trade.get('buy_date', 'N/A')
        sell_date = trade.get('sell_date', 'N/A')
        buy_price = trade.get('buy_price', 0)
        sell_price = trade.get('sell_price', 0)
        shares = trade.get('shares', 0)
        pnl = trade.get('pnl', 0)
        is_open = trade.get('is_open', False)
        
        # Trade Type Symbol
        type_symbol = "🤖" if trade_type['is_today'] else "📋"
        
        # Preise formatieren basierend auf Trade Type
        if trade_type['is_today']:
            # HEUTE: Artificial Open, Close
            if buy_date != 'N/A':
                try:
                    trade_date = pd.to_datetime(buy_date)
                    if trade_date in data_df.index:
                        row = data_df.loc[trade_date]
                        price_display = f"Artificial Open={row['Open']:.4f}, Close={row['Close']:.4f}"
                    else:
                        price_display = f"Artificial Open={buy_price:.4f}, Close={buy_price:.4f}"
                except:
                    price_display = f"Artificial Open={buy_price:.4f}, Close={buy_price:.4f}"
            else:
                price_display = f"Artificial Open={buy_price:.4f}, Close={sell_price:.4f}"
        else:
            # VERGANGENE TAGE: <Open, Close>
            if buy_date != 'N/A':
                try:
                    trade_date = pd.to_datetime(buy_date)
                    if trade_date in data_df.index:
                        row = data_df.loc[trade_date]
                        price_display = f"<Open={row['Open']:.4f}, Close={row['Close']:.4f}>"
                    else:
                        price_display = f"<Open={buy_price:.4f}, Close={buy_price:.4f}>"
                except:
                    price_display = f"<Open={buy_price:.4f}, Close={buy_price:.4f}>"
            else:
                price_display = f"<Open={buy_price:.4f}, Close={sell_price:.4f}>"
        
        # Status
        status = "OPEN" if is_open else "CLOSED"
        status_symbol = "🔓" if is_open else "🔒"
        
        # PnL Formatierung
        pnl_color = "💚" if pnl > 0 else "❤️" if pnl < 0 else "💙"
        
        # Vollständige Zeile
        if is_open:
            # Offener Trade - nur Buy Info
            line = f"{type_symbol} {trade_type['display_name']} {status_symbol} BUY {buy_date} @ {price_display} | Shares: {shares:.6f} | {status}"
        else:
            # Geschlossener Trade - Buy und Sell
            line = f"{type_symbol} {trade_type['display_name']} {status_symbol} BUY {buy_date} @ {price_display} | SELL {sell_date} @ {sell_price:.4f} | Shares: {shares:.6f} | PnL: {pnl_color}€{pnl:.2f}"
        
        return line
        
    except Exception as e:
        print(f"❌ Fehler in format_trade_for_display: {e}")
        return f"❌ Trade Format Error: {str(e)}"

def display_weekly_trades_console(matched_trades: List[Dict], data_df: pd.DataFrame, symbol: str, days_back: int = 14):
    """
    Zeigt Trades der letzten 2 Wochen in der Konsole an
    
    Args:
        matched_trades: Liste der matched trades
        data_df: DataFrame mit OHLCV Daten
        symbol: Ticker Symbol
        days_back: Anzahl Tage zurück (14 für 2 Wochen)
    """
    try:
        print(f"\n{'='*80}")
        print(f"📅 TRADES DER LETZTEN 2 WOCHEN ({days_back} TAGE) - {symbol}")
        print(f"{'='*80}")
        
        # Trades der letzten 2 Wochen filtern
        last_week_trades = get_last_week_trades(matched_trades, data_df, days_back)
        
        if not last_week_trades:
            print(f"❌ Keine Trades in den letzten {days_back} Tagen gefunden")
            return

        # Nach Datum sortieren (neueste zuerst)
        last_week_trades.sort(key=lambda t: pd.to_datetime(t.get('buy_date', '1900-01-01')), reverse=True)
        
        # Heute bestimmen
        today = datetime.now().date()
        
        print(f"📊 Insgesamt {len(last_week_trades)} Trades gefunden:")
        print(f"📋 Limit Orders: Vergangene Tage mit <Open, Close>")
        print(f"🤖 Artificial: Heutiger Tag mit Artificial Open, Close")
        print(f"-" * 80)
        
        # Trades anzeigen
        limit_count = 0
        artificial_count = 0
        
        for i, trade in enumerate(last_week_trades, 1):
            # Trade-Typ bestimmen
            buy_date_str = trade.get('buy_date', '')
            if buy_date_str:
                try:
                    trade_date = pd.to_datetime(buy_date_str)
                    trade_type = classify_trade_type(trade_date, data_df)
                    
                    # Zähler
                    if trade_type['is_today']:
                        artificial_count += 1
                    else:
                        limit_count += 1
                    
                    # Formatierte Zeile anzeigen
                    formatted_line = format_trade_for_display(trade, trade_type, data_df)
                    print(f"{i:3d}. {formatted_line}")
                    
                except Exception as e:
                    print(f"{i:3d}. ❌ Fehler beim Verarbeiten von Trade: {e}")
            else:
                print(f"{i:3d}. ❌ Ungültiger Trade (kein buy_date)")
        
        # Zusammenfassung
        print(f"-" * 80)
        print(f"📊 ZUSAMMENFASSUNG:")
        print(f"   📋 Limit Orders (vergangene Tage): {limit_count}")
        print(f"   🤖 Artificial (heute): {artificial_count}")
        print(f"   📈 Total: {len(last_week_trades)} Trades")
        
    except Exception as e:
        print(f"❌ Fehler in display_weekly_trades_console: {e}")
        import traceback
        traceback.print_exc()

def create_weekly_trades_html(matched_trades: List[Dict], data_df: pd.DataFrame, symbol: str, days_back: int = 14) -> str:
    """
    Erstellt HTML für Trades der letzten 2 Wochen
    
    Args:
        matched_trades: Liste der matched trades
        data_df: DataFrame mit OHLCV Daten
        symbol: Ticker Symbol
        days_back: Anzahl Tage zurück (14 für 2 Wochen)
    
    Returns:
        str: HTML Content für Weekly Trades
    """
    try:
        # Trades der letzten 2 Wochen filtern
        last_week_trades = get_last_week_trades(matched_trades, data_df, days_back)
        
        if not last_week_trades:
            return f"""
            <h3>📅 Trades der letzten {days_back} Tage - {symbol}</h3>
            <p style=\"color: orange;\">❌ Keine Trades in den letzten {days_back} Tagen gefunden</p>
            """

        # Nach Datum sortieren (neueste zuerst)
        last_week_trades.sort(key=lambda t: pd.to_datetime(t.get('buy_date', '1900-01-01')), reverse=True)
        
        # HTML Table erstellen
        html_content = f"""
        <h3>📅 Trades der letzten 2 Wochen ({days_back} Tage) - {symbol}</h3>
        <p>📋 <strong>Limit Orders:</strong> Vergangene Tage mit &lt;Open, Close&gt;</p>
        <p>🤖 <strong>Artificial:</strong> Heutiger Tag mit Artificial Open, Close</p>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <thead>
        <tr style="background-color: #f0f0f0;">
            <th style="border: 1px solid #ddd; padding: 8px;">#</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Typ</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Status</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Buy Datum</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Preise</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Sell Datum</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Shares</th>
            <th style="border: 1px solid #ddd; padding: 8px;">PnL</th>
        </tr>
        </thead>
        <tbody>
        """
        
        # Trades verarbeiten
        limit_count = 0
        artificial_count = 0
        
        for i, trade in enumerate(last_week_trades, 1):
            buy_date_str = trade.get('buy_date', 'N/A')
            sell_date_str = trade.get('sell_date', 'N/A')
            buy_price = trade.get('buy_price', 0)
            sell_price = trade.get('sell_price', 0)
            shares = trade.get('shares', 0)
            pnl = trade.get('pnl', 0)
            is_open = trade.get('is_open', False)
            
            # Trade-Typ bestimmen
            trade_type = {'is_today': False, 'display_name': 'Limit Order'}
            if buy_date_str != 'N/A':
                try:
                    trade_date = pd.to_datetime(buy_date_str)
                    trade_type = classify_trade_type(trade_date, data_df)
                    
                    if trade_type['is_today']:
                        artificial_count += 1
                    else:
                        limit_count += 1
                except:
                    pass
            
            # Type Symbol und Style
            if trade_type['is_today']:
                type_symbol = "🤖"
                type_name = "Artificial"
                row_style = "background-color: #fff3cd;"
            else:
                type_symbol = "📋"
                type_name = "Limit Order"
                row_style = "background-color: #d1ecf1;"
            
            # Status
            status = "🔓 OPEN" if is_open else "🔒 CLOSED"
            status_style = "color: orange;" if is_open else "color: green;"
            
            # Preise formatieren
            if trade_type['is_today']:
                try:
                    trade_date = pd.to_datetime(buy_date_str)
                    if trade_date in data_df.index:
                        row = data_df.loc[trade_date]
                        price_display = f"Artificial O={row['Open']:.4f}, C={row['Close']:.4f}"
                    else:
                        price_display = f"Artificial O={buy_price:.4f}, C={buy_price:.4f}"
                except:
                    price_display = f"Artificial O={buy_price:.4f}, C={buy_price:.4f}"
            else:
                try:
                    trade_date = pd.to_datetime(buy_date_str)
                    if trade_date in data_df.index:
                        row = data_df.loc[trade_date]
                        price_display = f"&lt;O={row['Open']:.4f}, C={row['Close']:.4f}&gt;"
                    else:
                        price_display = f"&lt;O={buy_price:.4f}, C={buy_price:.4f}&gt;"
                except:
                    price_display = f"&lt;O={buy_price:.4f}, C={buy_price:.4f}&gt;"
            
            # PnL Style
            if pnl > 0:
                pnl_style = "color: green; font-weight: bold;"
                pnl_text = f"€{pnl:.2f}"
            elif pnl < 0:
                pnl_style = "color: red; font-weight: bold;"
                pnl_text = f"€{pnl:.2f}"
            else:
                pnl_style = "color: blue;"
                pnl_text = "€0.00" if not is_open else "-"
            
            # Table Row
            html_content += f"""
            <tr style="{row_style}">
                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{i}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{type_symbol} {type_name}</td>
                <td style="border: 1px solid #ddd; padding: 8px; {status_style}">{status}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{buy_date_str}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{price_display}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{sell_date_str if not is_open else '-'}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{shares:.6f}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right; {pnl_style}">{pnl_text}</td>
            </tr>
            """
        
        # Tabelle schließen
        html_content += """
        </tbody>
        </table>
        """
        
        # Zusammenfassung
        html_content += f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px;">
        <h4>📊 Zusammenfassung:</h4>
        <ul>
            <li>📋 <strong>Limit Orders (vergangene Tage):</strong> {limit_count}</li>
            <li>🤖 <strong>Artificial (heute):</strong> {artificial_count}</li>
            <li>📈 <strong>Total Trades:</strong> {len(last_week_trades)}</li>
        </ul>
        </div>
        """
        
        return html_content
        
    except Exception as e:
        print(f"❌ Fehler in create_weekly_trades_html: {e}")
        return f"<p style='color: red;'>❌ Fehler beim Erstellen der Weekly Trades HTML: {str(e)}</p>"

def add_weekly_trades_to_existing_reports(symbol: str, matched_trades: List[Dict], data_df: pd.DataFrame):
    """
    Fügt Weekly Trades zu existierenden Reports hinzu
    
    Args:
        symbol: Ticker Symbol
        matched_trades: Liste der matched trades
        data_df: DataFrame mit OHLCV Daten
    """
    try:
        print(f"\n🔄 Erweitere Reports um Weekly Trades für {symbol}...")
        
        # 1. Console Output
        display_weekly_trades_console(matched_trades, data_df, symbol)
        
        # 2. HTML Content erstellen
        weekly_html = create_weekly_trades_html(matched_trades, data_df, symbol)
        
        # 3. Suche nach existierenden HTML Reports
        current_dir = os.getcwd()
        html_files = [f for f in os.listdir(current_dir) if f.endswith('.html') and symbol.replace('-', '').lower() in f.lower()]
        
        if html_files:
            for html_file in html_files:
                try:
                    # HTML lesen
                    with open(html_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Weekly Trades einfügen (vor dem schließenden </body> Tag)
                    if '</body>' in content:
                        # Einfügen vor </body>
                        insert_pos = content.rfind('</body>')
                        new_content = content[:insert_pos] + weekly_html + '\n' + content[insert_pos:]
                        
                        # Zurückschreiben
                        with open(html_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"✅ Weekly Trades zu {html_file} hinzugefügt")
                    else:
                        print(f"⚠️ Kein </body> Tag in {html_file} gefunden")
                        
                except Exception as e:
                    print(f"❌ Fehler beim Aktualisieren von {html_file}: {e}")
        else:
            print(f"ℹ️ Keine HTML Reports für {symbol} gefunden")
            
            # Standalone HTML Report erstellen
            standalone_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Weekly Trades - {symbol}</title>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h1>Weekly Trades Report - {symbol}</h1>
                {weekly_html}
                <p style="font-size: 12px; color: #666; margin-top: 30px;">
                    Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </body>
            </html>
            """
            
            # Standalone Report speichern
            filename = f"weekly_trades_{symbol.replace('-', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(standalone_html)
            
            print(f"✅ Standalone Weekly Trades Report erstellt: {filename}")
        
    except Exception as e:
        print(f"❌ Fehler in add_weekly_trades_to_existing_reports: {e}")
        import traceback
        traceback.print_exc()

# Test-Funktion
if __name__ == "__main__":
    print("🧪 TEST: Weekly Trades Display Module")
    
    # Dummy test data
    test_trades = [
        {
            'buy_date': '2025-08-04',
            'sell_date': '2025-08-05',
            'buy_price': 100.0,
            'sell_price': 105.0,
            'shares': 0.1,
            'pnl': 0.5,
            'is_open': False
        },
        {
            'buy_date': '2025-08-05',
            'sell_date': '',
            'buy_price': 105.0,
            'sell_price': 0,
            'shares': 0.1,
            'pnl': 0,
            'is_open': True
        }
    ]
    
    # Dummy DataFrame
    test_df = pd.DataFrame({
        'Open': [100, 102, 105],
        'High': [103, 107, 108],
        'Low': [99, 101, 104],
        'Close': [102, 105, 107],
        'Volume': [1000, 1200, 800]
    }, index=pd.date_range('2025-08-03', periods=3))
    
    print("📊 Test Display...")
    display_weekly_trades_console(test_trades, test_df, "TEST-EUR")
    
    print("\n📄 Test HTML...")
    html = create_weekly_trades_html(test_trades, test_df, "TEST-EUR")
    print("HTML Length:", len(html))
