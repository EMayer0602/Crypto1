#!/usr/bin/env python3
"""
Schnelle Diagnose der €78.68 Differenz zwischen Equity Curve und Matched Trades
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Import our modules
sys.path.append(os.getcwd())
from crypto_backtesting_module import run_backtest
from plotly_utils import create_equity_curve_from_matched_trades
import crypto_tickers

def diagnose_difference():
    """Analysiert die Differenz zwischen Equity Curve und Matched Trades"""
    
    print("🔍 DIAGNOSE DER €78.68 DIFFERENZ")
    print("="*50)
    
    # Verwende XRP-EUR als Beispiel
    symbol = 'XRP-EUR'
    config = crypto_tickers.get_ticker_config(symbol)
    
    print(f"📊 Analysiere {symbol}")
    print(f"   Initial Capital: €{config['initial_capital']}")
    print(f"   Trade on: {config['trade_on']}")
    print(f"   Commission: {config['commission_rate']*100:.2f}%")
    
    # Lade Daten und führe Backtest durch
    from crypto_backtesting_module import load_crypto_data_yf
    df = load_crypto_data_yf(symbol)
    
    if df is None or df.empty:
        print("❌ Keine Daten verfügbar")
        return
    
    print(f"   Daten: {len(df)} Tage von {df.index[0].date()} bis {df.index[-1].date()}")
    
    # Backtest mit optimalen Parametern
    result = run_backtest(df, symbol)
    
    if 'matched_trades' not in result or result['matched_trades'] is None:
        print("❌ Keine Matched Trades verfügbar")
        return
    
    matched_trades = result['matched_trades']
    print(f"   Matched Trades: {len(matched_trades)}")
    
    # Analysiere die letzten paar Trades
    if len(matched_trades) >= 3:
        print("\n🔍 LETZTE 3 MATCHED TRADES:")
        print("-"*80)
        last_3 = matched_trades.tail(3)
        
        for idx, (_, trade) in enumerate(last_3.iterrows(), 1):
            print(f"  Trade {idx}: {trade['Action']} | "
                  f"Price: {trade['Price']:.4f} | "
                  f"Shares: {trade['Shares']:.4f} | "
                  f"Commission: €{trade['Commission']:.2f} | "
                  f"Net PnL: €{trade['Net PnL']:.2f} | "
                  f"Capital: €{trade['Capital']:.2f}")
    
    # Berechne Equity Curve neu
    print("\n📈 EQUITY CURVE NEU BERECHNEN:")
    print("-"*40)
    
    equity_curve = create_equity_curve_from_matched_trades(
        df, matched_trades, config['initial_capital'], config['trade_on']
    )
    
    print(f"   Equity Curve Länge: {len(equity_curve)}")
    print(f"   Erste 3 Werte: {equity_curve[:3].tolist()}")
    print(f"   Letzte 3 Werte: {equity_curve[-3:].tolist()}")
    
    # Finale Werte
    final_matched = matched_trades['Capital'].iloc[-1]
    final_equity = equity_curve[-1]
    
    print(f"\n🎯 FINALE WERTE:")
    print(f"   Matched Trades Final: €{final_matched:.2f}")
    print(f"   Equity Curve Final: €{final_equity:.2f}")
    print(f"   Differenz: €{final_equity - final_matched:.2f}")
    
    # Suche nach Muster
    difference = final_equity - final_matched
    total_trades = len(matched_trades)
    avg_diff_per_trade = difference / total_trades if total_trades > 0 else 0
    
    print(f"\n🔍 MUSTER ANALYSE:")
    print(f"   Total Trades: {total_trades}")
    print(f"   Durchschn. Diff pro Trade: €{avg_diff_per_trade:.4f}")
    
    # Prüfe ob es mit Rundung zu tun hat
    commission_rate = config['commission_rate']
    avg_commission = matched_trades['Commission'].mean()
    
    print(f"   Durchschn. Commission: €{avg_commission:.4f}")
    print(f"   Ist Differenz ≈ Commission? {abs(difference - avg_commission) < 1}")
    
    return {
        'difference': difference,
        'final_matched': final_matched,
        'final_equity': final_equity,
        'total_trades': total_trades,
        'avg_diff_per_trade': avg_diff_per_trade
    }

if __name__ == "__main__":
    try:
        result = diagnose_difference()
        print(f"\n✅ Diagnose abgeschlossen")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
