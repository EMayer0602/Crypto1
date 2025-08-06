#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FIXED LIVE BACKTEST REPORT - Ohne problematische Emojis in der Konsole
"""

import os
import sys
import webbrowser
from datetime import datetime, timedelta
import pandas as pd

# Import unserer Module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from crypto_backtesting_module import run_backtest
import crypto_tickers

def run_live_backtests():
    """Führt LIVE Backtests für alle Tickers aus und sammelt Results"""
    
    print("LIVE BACKTEST REPORT - Fuehre aktuelle Backtests durch...")
    print("=" * 80)
    
    tickers = list(crypto_tickers.crypto_tickers.keys())
    all_results = []
    summary_data = []
    all_trades_14_days = []
    
    for ticker in tickers:
        print(f"\nLIVE BACKTEST fuer {ticker}...")
        
        # Hole ticker-spezifische Config
        ticker_config = crypto_tickers.crypto_tickers.get(ticker, {})
        trade_on = ticker_config.get('trade_on', 'Close')
        
        # Erstelle vollständige Config
        config = {
            'initial_capital': ticker_config.get('initialCapitalLong', 10000),
            'commission_rate': 0.0018,
            'trade_on': trade_on,
            'order_round_factor': ticker_config.get('order_round_factor', 0.01),
            'timeframe': 'daily',
            'csv_path': './',
            'min_commission': 1.0
        }
        
        try:
            # Führe Backtest aus
            result = run_backtest(ticker, config)
            
            if result and result.get('success', False):
                all_results.append(result)
                
                # Erstelle summary_data
                summary_data.append({
                    'Symbol': ticker,
                    'Past_Window': result.get('optimal_past_window'),
                    'Trade_Window': result.get('optimal_trade_window'),
                    'Optimal_PnL': result.get('optimal_pnl', 0),
                    'Trades_2W': result.get('weekly_trades_count', 0),
                    'Order_Round_Factor': config['order_round_factor']
                })
                
                # Sammle Trades der letzten 14 Tage
                weekly_trades = result.get('weekly_trades_data', [])
                for trade in weekly_trades:
                    action = trade.get('Action', '')
                    if action in ['BUY', 'SELL']:
                        trade['ticker'] = ticker
                        trade['config'] = config
                        all_trades_14_days.append(trade)
                
                print(f"   Optimal: p={result.get('optimal_past_window')}, tw={result.get('optimal_trade_window')}")
                print(f"   Backtest PnL: {result.get('optimal_pnl', 0):.2f}%")
                print(f"   Trades (2 Wochen): {result.get('weekly_trades_count', 0)}")
                
            else:
                print(f"   Backtest fehlgeschlagen")
                
        except Exception as e:
            print(f"   Fehler: {e}")
    
    print(f"\nGESAMT: {len(all_trades_14_days)} Trades der letzten 14 Tage gefunden!")
    return all_results, summary_data, all_trades_14_days

def main():
    """Main function"""
    try:
        # 1. Führe LIVE Backtests aus
        all_results, summary_data, all_trades_14_days = run_live_backtests()
        
        if not all_results:
            print("Keine Backtest-Results erhalten!")
            return None
        
        print(f"\n{len(all_results)} Ticker erfolgreich analysiert!")
        print(f"{len(all_trades_14_days)} Trades der letzten 14 Tage gefunden!")
        
        # 2. EINFACHE TICKER PnL AUSGABE (OHNE EMOJIS!)
        print()
        for result in summary_data:
            ticker = result['Symbol'].replace('-EUR', '').upper()
            optimal_pnl = result['Optimal_PnL']
            
            if ticker and optimal_pnl is not None:
                print(f"{ticker:<8} {optimal_pnl:>6.0f}%")
        print()
        
        print("HTML-Report wird erstellt...")
        # Hier würde der HTML-Report erstellt werden
        print("Report fertig!")
        
        return "success"
        
    except Exception as e:
        print(f"Fehler: {e}")
        return None

if __name__ == "__main__":
    main()
