#!/usr/bin/env python3
"""
Quick test to verify the equity curve is correctly displayed in charts
"""

import sys
sys.path.append('.')
import pandas as pd
from crypto_backtesting_module import run_backtest
from plotly_utils import plotly_combined_chart_and_equity
from crypto_tickers import crypto_tickers

def test_equity_chart(symbol='XRP-EUR'):
    """Test equity curve display in charts"""
    print(f"🧪 Testing equity chart for {symbol}...")
    
    cfg = crypto_tickers[symbol]
    print(f"💰 Initial Capital: €{cfg.get('initialCapitalLong', 1000)}")
    
    # Run backtest
    print("🔄 Running backtest...")
    result = run_backtest(symbol, cfg)
    
    if not result:
        print("❌ Backtest failed")
        return
    
    print(f"✅ Backtest successful")
    if 'equity_curve' in result:
        equity = result['equity_curve']
        print(f"📊 Equity: {len(equity)} values, €{equity[0]:.0f} -> €{equity[-1]:.0f}")
    
    # Create chart
    print(f"🎨 Creating chart...")
    chart_success = plotly_combined_chart_and_equity(
        df=result['df_bt'],
        standard_signals=result.get('ext_signals', pd.DataFrame()),
        support=pd.Series(dtype=float),
        resistance=pd.Series(dtype=float),
        equity_curve=result.get('equity_curve', []),
        buyhold_curve=result.get('buyhold_curve', []),
        ticker=symbol,
        initial_capital=cfg.get('initialCapitalLong', 1000)
    )
    
    if chart_success:
        print("✅ Chart created successfully!")
        print(f"📊 Chart saved as chart_{symbol.replace('-','_')}.html")
    else:
        print("❌ Chart creation failed")

if __name__ == "__main__":
    test_equity_chart('XRP-EUR')
