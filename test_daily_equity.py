#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test der TÄGLICHEN Equity-Kurve: zeigt den Verlauf jeden Tag mit Marktpreisen
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plotly_utils import create_equity_curve_from_matched_trades
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def test_daily_equity_curve():
    """Test der täglichen Equity-Kurve mit simulierten Daten"""
    
    print(f"🧪 TESTE TÄGLICHE EQUITY-KURVE")
    print("=" * 80)
    
    # Lade echte BTC Daten
    symbol = "BTC-EUR"
    df = yf.download(symbol, period="1y", interval="1d", auto_adjust=True, progress=False)
    
    if df.empty:
        print("❌ Keine Daten geladen")
        return False
    
    # Fix column names
    if hasattr(df.columns, 'levels'):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(col).strip().capitalize() for col in df.columns]
    
    print(f"📊 Daten geladen: {len(df)} Tage von {df.index[0].date()} bis {df.index[-1].date()}")
    
    # Simuliere ein paar Trades
    initial_capital = 5000
    
    # Trade 1: Buy auf 2024-06-01, Sell auf 2024-06-15
    trade1_buy_date = pd.Timestamp('2024-06-01')
    trade1_sell_date = pd.Timestamp('2024-06-15')
    
    # Finde nächstgelegene Daten in DataFrame
    try:
        trade1_buy_price = df.loc[df.index >= trade1_buy_date, 'Close'].iloc[0]
        trade1_sell_price = df.loc[df.index >= trade1_sell_date, 'Close'].iloc[0]
        trade1_shares = initial_capital / trade1_buy_price
        trade1_pnl = trade1_shares * (trade1_sell_price - trade1_buy_price)
        
        print(f"📈 Trade 1: {trade1_buy_date.date()} → {trade1_sell_date.date()}")
        print(f"   Shares: {trade1_shares:.6f}")
        print(f"   Buy: €{trade1_buy_price:.2f}, Sell: €{trade1_sell_price:.2f}")
        print(f"   PnL: €{trade1_pnl:.2f}")
        
        # Trade 2: Buy auf 2024-08-01 (noch offen)
        trade2_buy_date = pd.Timestamp('2024-08-01')
        trade2_buy_price = df.loc[df.index >= trade2_buy_date, 'Close'].iloc[0]
        current_capital = initial_capital + trade1_pnl
        trade2_shares = current_capital / trade2_buy_price
        
        print(f"📈 Trade 2: {trade2_buy_date.date()} (OFFEN)")
        print(f"   Capital nach Trade 1: €{current_capital:.2f}")
        print(f"   Shares: {trade2_shares:.6f}")
        print(f"   Buy: €{trade2_buy_price:.2f}")
        
        # Erstelle Trades Liste
        matched_trades = [
            {
                'buy_date': trade1_buy_date.strftime('%Y-%m-%d'),
                'sell_date': trade1_sell_date.strftime('%Y-%m-%d'),
                'buy_price': trade1_buy_price,
                'sell_price': trade1_sell_price,
                'shares': trade1_shares,
                'pnl': trade1_pnl,
                'is_open': False
            },
            {
                'buy_date': trade2_buy_date.strftime('%Y-%m-%d'),
                'sell_date': '',
                'buy_price': trade2_buy_price,
                'sell_price': 0,
                'shares': trade2_shares,
                'pnl': 0,
                'is_open': True
            }
        ]
        
        # Beschränke DataFrame auf relevanten Zeitraum
        start_date = trade1_buy_date - timedelta(days=30)
        df_test = df[df.index >= start_date].copy()
        
        print(f"\n📊 Test-Zeitraum: {df_test.index[0].date()} bis {df_test.index[-1].date()} ({len(df_test)} Tage)")
        
        # Berechne tägliche Equity-Kurve
        equity_curve = create_equity_curve_from_matched_trades(matched_trades, initial_capital, df_test)
        
        print(f"\n✅ TÄGLICHE EQUITY-KURVE ANALYSE:")
        print(f"   📏 Länge: {len(equity_curve)} Werte")
        print(f"   💰 Start: €{equity_curve[0]:.0f}")
        print(f"   💰 Ende: €{equity_curve[-1]:.0f}")
        print(f"   📈 Min: €{min(equity_curve):.0f}")
        print(f"   📈 Max: €{max(equity_curve):.0f}")
        
        # Prüfe Variabilität
        unique_values = len(set([int(v) for v in equity_curve]))
        print(f"   🔍 Unique Werte: {unique_values}")
        
        if unique_values > 50:
            print(f"   ✅ Equity-Kurve variiert TÄGLICH!")
        elif unique_values > 10:
            print(f"   ⚠️ Equity-Kurve variiert teilweise")
        else:
            print(f"   ❌ Equity-Kurve ist zu konstant")
        
        # Zeige Sample-Werte um Trades herum
        print(f"\n📊 SAMPLE WERTE:")
        sample_dates = [0, len(equity_curve)//4, len(equity_curve)//2, 3*len(equity_curve)//4, -1]
        for i in sample_dates:
            date = df_test.index[i]
            equity = equity_curve[i]
            btc_price = df_test.iloc[i]['Close']
            print(f"   {date.date()}: Equity €{equity:.0f}, BTC €{btc_price:.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Test-Trades: {e}")
        return False

if __name__ == "__main__":
    success = test_daily_equity_curve()
    if success:
        print(f"\n🎯 TÄGLICHE Equity-Kurve Test erfolgreich!")
    else:
        print(f"\n❌ Test fehlgeschlagen!")
