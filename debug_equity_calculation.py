#!/usr/bin/env python3
"""Debug der Equity Curve Berechnung"""

import pandas as pd
from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers
import numpy as np

def test_equity_curve_calculation():
    print("🔍 TESTING EQUITY CURVE CALCULATION...")
    print("=" * 60)
    
    # Führe Backtest aus
    config = crypto_tickers['BTC-EUR']
    ticker = 'BTC-EUR'
    
    print(f"📊 Testing {ticker} with initial capital: €{config['initialCapitalLong']:,.0f}")
    
    result = run_backtest(ticker, config)
    
    if result and result.get('success'):
        print("✅ Backtest successful!")
        
        # Prüfe Final Capital
        final_cap = result.get('final_capital', 0)
        print(f"📈 Final Capital from result: €{final_cap:,.2f}")
        
        # Prüfe Equity Curve
        equity_curve = result.get('equity_curve', [])
        print(f"📊 Equity curve length: {len(equity_curve)}")
        
        if len(equity_curve) > 0:
            print(f"📊 First 10 equity values: {equity_curve[:10]}")
            print(f"📊 Last 10 equity values: {equity_curve[-10:]}")
            
            # Prüfe ob Equity Curve sich ändert
            if len(set(equity_curve)) == 1:
                print("❌ PROBLEM: Equity curve ist komplett flach!")
            else:
                print(f"✅ Equity curve variiert von €{min(equity_curve):,.2f} bis €{max(equity_curve):,.2f}")
        
        # Prüfe Extended Signals / Trades
        ext_signals = result.get('extended_signals', pd.DataFrame())
        print(f"📊 Extended signals: {len(ext_signals)} rows")
        
        if len(ext_signals) > 0:
            print("📊 Sample extended signals:")
            print(ext_signals.head(10))
            print(f"\n📊 Extended signals columns: {list(ext_signals.columns)}")
            
            # Zähle BUY/SELL Signale
            if 'Action' in ext_signals.columns:
                buy_count = len(ext_signals[ext_signals['Action'] == 'BUY'])
                sell_count = len(ext_signals[ext_signals['Action'] == 'SELL'])
                print(f"📊 BUY signals: {buy_count}, SELL signals: {sell_count}")
            
            if 'Long Action' in ext_signals.columns:
                buy_count2 = len(ext_signals[ext_signals['Long Action'] == 'BUY'])
                sell_count2 = len(ext_signals[ext_signals['Long Action'] == 'SELL'])
                print(f"📊 'Long Action' BUY signals: {buy_count2}, SELL signals: {sell_count2}")
        
        # ✅ Prüfe matched_trades im Detail
        matched_trades = result.get('matched_trades', pd.DataFrame())
        print(f"📊 Matched trades shape: {matched_trades.shape}")
        
        if not matched_trades.empty:
            print(f"📊 Matched trades columns: {list(matched_trades.columns)}")
            print(f"📊 First 3 matched trades:")
            print(matched_trades.head(3))
            
            if 'Capital' in matched_trades.columns:
                print(f"📊 Final Capital from matched trades: €{matched_trades['Capital'].iloc[-1]:,.2f}")
        else:
            print(f"❌ No matched trades found!")
        
        # Manuelle Equity Curve Berechnung basierend auf matched_trades
        if not matched_trades.empty and 'Capital' in matched_trades.columns:
            print(f"\n✅ USING MATCHED TRADES FOR EQUITY:")
            equity_from_matched = matched_trades['Capital'].tolist()
            print(f"📊 Matched trades equity range: €{min(equity_from_matched):,.0f} - €{max(equity_from_matched):,.0f}")
            print(f"📊 This should match the backtest equity curve!")
            
            # Vergleiche
            if len(equity_curve) > 0:
                print(f"📊 Backtest equity range: €{min(equity_curve):,.0f} - €{max(equity_curve):,.0f}")
                if abs(equity_from_matched[-1] - equity_curve[-1]) > 100:
                    print("❌ MISMATCH: Matched trades and backtest equity don't match!")
                else:
                    print("✅ SUCCESS: Matched trades and backtest equity match!")
        
        return  # Skip manual calculation for now
        df = pd.read_csv(csv_file)
        df['Date'] = pd.to_datetime(df['Date'])
        
        initial_capital = config['initialCapitalLong']
        current_capital = initial_capital
        shares = 0
        invested = False
        commission_rate = 0.001  # 0.1%
        
        manual_equity = []
        
        print(f"Starting with €{initial_capital:,.2f}")
        
        # Simuliere jeden Tag
        for i, row in df.iterrows():
            date = row['Date']
            open_price = row['Open']
            close_price = row['Close']
            
            # Prüfe ob es ein Trade-Signal an diesem Tag gibt
            trade_signal = None
            if len(ext_signals) > 0 and 'Date' in ext_signals.columns:
                signal_match = ext_signals[ext_signals['Date'] == date]
                if not signal_match.empty:
                    trade_signal = signal_match.iloc[0]['Action']
            
            # Berechne Tagesergebnis
            if trade_signal == 'BUY' and not invested:
                # Kaufe Shares
                fee = current_capital * commission_rate
                investable = current_capital - fee
                shares = investable / open_price
                current_capital = 0
                invested = True
                print(f"📅 {date.date()} BUY: {shares:.4f} shares @ €{open_price:.2f}, fee: €{fee:.2f}")
            
            elif trade_signal == 'SELL' and invested:
                # Verkaufe Shares
                proceeds = shares * open_price
                fee = proceeds * commission_rate
                current_capital = proceeds - fee
                shares = 0
                invested = False
                print(f"📅 {date.date()} SELL: proceeds: €{proceeds:.2f}, fee: €{fee:.2f}, capital: €{current_capital:.2f}")
            
            # Berechne aktuellen Equity Wert
            if invested:
                equity_value = shares * close_price
            else:
                equity_value = current_capital
            
            manual_equity.append(equity_value)
            
            if i < 5 or i >= len(df) - 5:  # Erste und letzte 5 Tage
                status = "INVESTED" if invested else "CASH"
                print(f"📅 {date.date()} {status}: Equity = €{equity_value:.2f}")
        
        print(f"\n📈 Manual calculation final equity: €{manual_equity[-1]:,.2f}")
        print(f"📊 Manual equity range: €{min(manual_equity):,.2f} - €{max(manual_equity):,.2f}")
        
        # Vergleiche mit der Backtest Equity Curve
        if len(equity_curve) > 0:
            print(f"📊 Backtest equity range: €{min(equity_curve):,.2f} - €{max(equity_curve):,.2f}")
            if abs(manual_equity[-1] - equity_curve[-1]) > 100:
                print("❌ PROBLEM: Manual and backtest equity curves don't match!")
            else:
                print("✅ Manual and backtest equity curves match!")
    
    else:
        print("❌ Backtest failed")

if __name__ == "__main__":
    test_equity_curve_calculation()
