#!/usr/bin/env python3

"""
QUICK TEST: Test ob der korrigierte Backtest funktioniert
"""

import sys
import os
sys.path.append(os.getcwd())

def quick_test():
    print("🧪 QUICK BACKTEST TEST...")
    
    try:
        from crypto_tickers import crypto_tickers
        from crypto_backtesting_module import run_backtest
        
        # Test BTC-EUR
        symbol = "BTC-EUR"
        config = crypto_tickers[symbol]
        
        print(f"📊 Testing {symbol} with trade_on={config['trade_on']}")
        
        result = run_backtest(symbol, config)
        
        if result and result != False:
            print("✅ SUCCESS: Backtest completed!")
            
            # Zeige Zusammenfassung
            if 'matched_trades' in result and not result['matched_trades'].empty:
                trades = result['matched_trades']
                print(f"📈 Trades: {len(trades)}")
                print(f"💰 Total PnL: €{trades['PnL'].sum():.2f}")
                print(f"🎯 Trade On: {trades['Trade On'].iloc[0] if len(trades) > 0 else 'N/A'}")
            else:
                print("⚠️ No trades found")
        else:
            print("❌ FAILED: Backtest failed")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()
