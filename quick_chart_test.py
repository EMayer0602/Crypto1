#!/usr/bin/env python3
"""Quick test for one ticker"""

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

# Test just BTC
ticker = 'BTC-EUR'
config = crypto_tickers[ticker]

print(f"Testing {ticker}...")

result = run_backtest(ticker, config)

if result and 'success' in result and result['success']:
    print(f'✅ {ticker}: Chart created successfully!')
    
    # Extract final capital from trade_statistics
    trade_stats = result.get('trade_statistics', {})
    final_capital = trade_stats.get('💼 Final Capital', 'N/A')
    print(f'   📈 Final Capital: {final_capital}')
    
    if 'optimal_past_window' in result:
        print(f'   🎯 Optimal Parameters: Past={result["optimal_past_window"]}, Trade={result["optimal_trade_window"]}')
        
    # Check if charts were created
    import glob
    chart_files = glob.glob("reports/chart_*.html")
    print(f'   📊 Charts found: {len(chart_files)}')
    
else:
    print(f'❌ {ticker}: Chart creation failed - backtest unsuccessful')
    if result:
        print(f'   Result keys: {list(result.keys())}')
