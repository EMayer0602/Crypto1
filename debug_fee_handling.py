#!/usr/bin/env python3
"""
Debug: Fee-Behandlung in Equity Curve vs Matched Trades
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def debug_fee_handling():
    """Debug der Fee-Behandlung"""
    symbol = 'XRP-EUR'
    config = crypto_tickers[symbol]
    
    print(f"🔍 FEE DEBUGGING: {symbol}")
    print("="*50)
    
    try:
        result = run_backtest(symbol, config)
        
        if result and 'matched_trades' in result and 'equity_curve' in result:
            matched_trades = result['matched_trades']
            equity_curve = result['equity_curve']
            initial_capital = config.get('initialCapitalLong', 1000)
            
            print(f"📊 Initial Capital: €{initial_capital}")
            print(f"📊 Commission Rate: {config.get('commission_rate', 0.0018)*100}%")
            
            if len(matched_trades) > 0 and len(equity_curve) > 0:
                equity_final = equity_curve[-1]
                matched_final = matched_trades['Capital'].iloc[-1]
                difference = equity_final - matched_final
                
                print(f"\n💰 FINAL VALUES:")
                print(f"   Equity Curve Final: €{equity_final:.4f}")
                print(f"   Matched Final:      €{matched_final:.4f}")
                print(f"   Difference:         €{difference:.4f}")
                
                # Fee-Analyse
                print(f"\n🔍 FEE ANALYSIS:")
                
                # Berechne theoretische Fees aus Matched Trades
                total_volume = 0
                total_commission = 0
                
                for idx, trade in matched_trades.iterrows():
                    entry_price = trade.get('Entry Price', 0)
                    exit_price = trade.get('Exit Price', 0)
                    quantity = trade.get('Quantity', 0)
                    commission = trade.get('Commission', 0)
                    pnl = trade.get('PnL', 0)
                    net_pnl = trade.get('Net PnL', 0)
                    
                    buy_volume = entry_price * quantity
                    sell_volume = exit_price * quantity
                    trade_volume = buy_volume + sell_volume
                    
                    total_volume += trade_volume
                    total_commission += commission
                    
                    print(f"   Trade {idx+1}:")
                    print(f"     Buy: {quantity:.4f} @ €{entry_price:.4f} = €{buy_volume:.2f}")
                    print(f"     Sell: {quantity:.4f} @ €{exit_price:.4f} = €{sell_volume:.2f}")
                    print(f"     Volume: €{trade_volume:.2f}")
                    print(f"     Commission: €{commission:.4f}")
                    print(f"     PnL: €{pnl:.2f}, Net PnL: €{net_pnl:.2f}")
                
                print(f"\n📊 TOTALS:")
                print(f"   Total Trading Volume: €{total_volume:.2f}")
                print(f"   Total Commissions:    €{total_commission:.4f}")
                print(f"   Commission Rate Used: {total_commission/total_volume*100:.3f}%")
                
                # Prüfe ob Differenz ≈ Commission
                if abs(abs(difference) - total_commission) < 0.01:
                    print(f"\n✅ FOUND IT! Difference ≈ Total Commission!")
                    print(f"   Difference: €{abs(difference):.4f}")
                    print(f"   Total Fees: €{total_commission:.4f}")
                    print(f"   ➡️  Equity curve may be double-counting fees!")
                else:
                    print(f"\n❓ Difference is NOT equal to commission")
                    print(f"   Difference: €{abs(difference):.4f}")
                    print(f"   Total Fees: €{total_commission:.4f}")
                
                # Alternative: Check gegen Initial + Total Net PnL
                total_net_pnl = matched_trades['Net PnL'].sum()
                calculated_final = initial_capital + total_net_pnl
                
                print(f"\n🔍 ALTERNATIVE CALCULATION:")
                print(f"   Initial + Total Net PnL: €{initial_capital} + €{total_net_pnl:.2f} = €{calculated_final:.2f}")
                print(f"   Matched Trades Final:     €{matched_final:.2f}")
                print(f"   Equity Curve Final:       €{equity_final:.2f}")
                
                if abs(equity_final - calculated_final) < 0.01:
                    print(f"   ✅ Equity matches Initial + Net PnL!")
                else:
                    print(f"   ❌ Equity does NOT match Initial + Net PnL")
                    print(f"   Difference: €{abs(equity_final - calculated_final):.4f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_fee_handling()
