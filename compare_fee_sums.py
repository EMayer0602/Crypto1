#!/usr/bin/env python3
"""
Vergleiche die Summe der Fees: Equity Curve vs Matched Trades
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers
from plotly_utils import create_equity_curve_from_matched_trades

def calculate_fee_comparison():
    """Berechne und vergleiche die Fees beider Systeme"""
    symbol = 'XRP-EUR'
    config = crypto_tickers[symbol]
    
    print(f"🔍 FEE SUMMEN VERGLEICH: {symbol}")
    print("="*60)
    
    try:
        result = run_backtest(symbol, config)
        
        if result and 'matched_trades' in result:
            matched_trades = result['matched_trades']
            initial_capital = config.get('initialCapitalLong', 1000)
            commission_rate = config.get('commission_rate', 0.0018)
            
            print(f"📊 Initial Capital: €{initial_capital}")
            print(f"📊 Commission Rate: {commission_rate*100}%")
            
            if len(matched_trades) > 0:
                print(f"\n💰 MATCHED TRADES FEE ANALYSIS:")
                print("-" * 50)
                
                # 1. FEES AUS MATCHED TRADES
                total_matched_fees = 0
                total_matched_pnl = 0
                total_matched_net_pnl = 0
                
                for idx, trade in matched_trades.iterrows():
                    entry_price = trade.get('Entry Price', 0)
                    exit_price = trade.get('Exit Price', 0) 
                    quantity = trade.get('Quantity', 0)
                    commission = trade.get('Commission', 0)
                    pnl = trade.get('PnL', 0)
                    net_pnl = trade.get('Net PnL', 0)
                    
                    total_matched_fees += commission
                    total_matched_pnl += pnl
                    total_matched_net_pnl += net_pnl
                    
                    print(f"Trade {idx+1}: Entry=€{entry_price:.4f}, Exit=€{exit_price:.4f}")
                    print(f"         Qty={quantity:.4f}, Commission=€{commission:.4f}")
                    print(f"         PnL=€{pnl:.2f}, Net PnL=€{net_pnl:.2f}")
                
                print(f"\n📊 MATCHED TRADES TOTALS:")
                print(f"   Total Commission (from trades): €{total_matched_fees:.4f}")
                print(f"   Total PnL:                      €{total_matched_pnl:.2f}")
                print(f"   Total Net PnL:                  €{total_matched_net_pnl:.2f}")
                print(f"   Fee Difference: PnL - Net PnL:  €{total_matched_pnl - total_matched_net_pnl:.4f}")
                
                # 2. BERECHNE THEORETISCHE FEES
                print(f"\n🧮 THEORETICAL FEE CALCULATION:")
                print("-" * 50)
                
                theoretical_fees = 0
                for idx, trade in matched_trades.iterrows():
                    entry_price = trade.get('Entry Price', 0)
                    exit_price = trade.get('Exit Price', 0)
                    quantity = trade.get('Quantity', 0)
                    
                    buy_volume = entry_price * quantity
                    sell_volume = exit_price * quantity
                    buy_fee = buy_volume * commission_rate
                    sell_fee = sell_volume * commission_rate
                    total_trade_fee = buy_fee + sell_fee
                    
                    theoretical_fees += total_trade_fee
                    
                    print(f"Trade {idx+1}:")
                    print(f"   Buy: €{buy_volume:.2f} * {commission_rate:.4f} = €{buy_fee:.4f}")
                    print(f"   Sell: €{sell_volume:.2f} * {commission_rate:.4f} = €{sell_fee:.4f}")
                    print(f"   Total: €{total_trade_fee:.4f}")
                
                print(f"\n📊 THEORETICAL TOTALS:")
                print(f"   Theoretical Total Fees: €{theoretical_fees:.4f}")
                print(f"   Matched Trades Fees:    €{total_matched_fees:.4f}")
                print(f"   Difference:             €{abs(theoretical_fees - total_matched_fees):.4f}")
                
                # 3. EQUITY CURVE FEE SCHÄTZUNG
                print(f"\n📈 EQUITY CURVE FEE ESTIMATION:")
                print("-" * 50)
                
                # Simuliere Equity-Kurve und zähle Fee-Abzüge
                from plotly_utils import create_equity_curve_from_matched_trades
                
                # Get the dataframe used for equity calculation
                if 'df' in result:
                    df = result['df']
                    trade_on = config.get('trade_on', 'Close')
                    
                    # Erstelle modifizierte Version der Funktion die Fees trackt
                    equity_fees = calculate_equity_fees(matched_trades, initial_capital, df, trade_on, commission_rate)
                    
                    print(f"   Estimated Equity Fees: €{equity_fees:.4f}")
                    print(f"   vs Matched Fees:       €{total_matched_fees:.4f}")
                    print(f"   Fee Difference:        €{abs(equity_fees - total_matched_fees):.4f}")
                
                # 4. FINAL CAPITAL COMPARISON
                print(f"\n🎯 FINAL CAPITAL COMPARISON:")
                print("-" * 50)
                
                matched_final = matched_trades['Capital'].iloc[-1] if 'Capital' in matched_trades.columns else 0
                equity_final = result.get('equity_curve', [])[-1] if result.get('equity_curve') else 0
                
                # Verschiedene Berechnungsmethoden
                method1_final = initial_capital + total_matched_net_pnl
                method2_final = initial_capital + total_matched_pnl - total_matched_fees
                
                print(f"   Initial Capital:           €{initial_capital}")
                print(f"   Method 1 (Init + Net PnL): €{method1_final:.2f}")
                print(f"   Method 2 (Init+PnL-Fees):  €{method2_final:.2f}")
                print(f"   Matched Trades Final:      €{matched_final:.2f}")
                print(f"   Equity Curve Final:        €{equity_final:.2f}")
                
                print(f"\n🔍 DIFFERENCES:")
                if equity_final > 0 and matched_final > 0:
                    diff = equity_final - matched_final
                    print(f"   Equity - Matched: €{diff:.4f}")
                    
                    if abs(abs(diff) - total_matched_fees) < 0.1:
                        print(f"   ✅ BINGO! Difference ≈ Total Fees!")
                        print(f"   ➡️  Equity curve is likely double-counting fees")
                    elif abs(diff) < 0.01:
                        print(f"   ✅ PERFECT MATCH!")
                    else:
                        print(f"   ❓ Difference not explained by simple fee error")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def calculate_equity_fees(matched_trades, initial_capital, df, trade_on, commission_rate):
    """Schätze die Fees die in der Equity-Kurven-Berechnung verwendet werden"""
    total_estimated_fees = 0
    
    for idx, trade in matched_trades.iterrows():
        # Schätze Fees wie in der Equity-Funktion
        buy_price = trade.get('buy_price', trade.get('Entry Price', 0))
        sell_price = trade.get('sell_price', trade.get('Exit Price', 0))
        shares = trade.get('shares', trade.get('Quantity', 0))
        
        # Theoretische PnL und geschätzte Fees (wie in Equity-Funktion)
        theoretical_pnl = shares * (sell_price - buy_price)
        actual_pnl = trade.get('pnl', trade.get('PnL', 0))
        
        # Geschätzte Total Fees (wie in der Equity-Funktion berechnet)
        estimated_total_fees = theoretical_pnl - actual_pnl if theoretical_pnl > actual_pnl else 0
        total_estimated_fees += estimated_total_fees
        
        print(f"   Trade {idx+1}: Theoretical PnL=€{theoretical_pnl:.2f}, Actual PnL=€{actual_pnl:.2f}")
        print(f"              Estimated Fees=€{estimated_total_fees:.4f}")
    
    return total_estimated_fees

if __name__ == "__main__":
    calculate_fee_comparison()
