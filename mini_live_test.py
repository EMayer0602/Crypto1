#!/usr/bin/env python3
"""Mini test to run live backtest and check results"""

import os
import sys
from datetime import datetime

# Set working directory
os.chdir(r"c:\Users\Edgar.000\Documents\____Trading strategies\Crypto_trading1")
sys.path.append(os.getcwd())

print("🚀 Starting MINI LIVE BACKTEST...")

try:
    from crypto_tickers import crypto_tickers
    from crypto_backtesting_module import run_backtest
    
    # Test just BTC
    ticker = 'BTC-EUR'
    config = crypto_tickers[ticker]
    
    print(f"Testing {ticker} with initial capital: {config['initialCapitalLong']}")
    
    result = run_backtest(ticker, config)
    
    if result and 'trade_statistics' in result:
        stats = result['trade_statistics']
        
        # Extract PnL  
        if '📊 Total Return' in stats:
            pnl_value = stats['📊 Total Return']
            if isinstance(pnl_value, str):
                pnl_numeric = float(pnl_value.replace('%', ''))
            else:
                pnl_numeric = pnl_value
                
            print(f"✅ {ticker}: {pnl_numeric:.1f}% PnL")
            
            # Generate minimal HTML report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"MINI_backtest_report_{timestamp}.html"
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Mini Backtest Result</title></head>
            <body>
                <h1>Mini Live Backtest Report</h1>
                <p><strong>{ticker}</strong>: {pnl_numeric:.1f}% PnL</p>
                <p>Initial Capital: €{config['initialCapitalLong']:,}</p>
                <p>Final Capital: {stats.get('💼 Final Capital', 'N/A')}</p>
                <p>Generated: {timestamp}</p>
            </body>
            </html>
            """
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
                
            print(f"✅ Report saved: {filename}")
            
        else:
            print("❌ No Total Return found")
    else:
        print("❌ No valid result")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
