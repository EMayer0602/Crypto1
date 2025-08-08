#!/usr/bin/env python3
"""Debug Equity Curve Problem"""

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

print("🔍 DEBUGGING EQUITY CURVE PROBLEM")
print("=" * 50)

# Test BTC-EUR
config = crypto_tickers['BTC-EUR']
print(f"Initial Capital from config: €{config.get('initialCapitalLong', 'DEFAULT')}")

result = run_backtest('BTC-EUR', config)

if result and result.get('success'):
    # Check trade statistics
    trade_stats = result.get('trade_statistics', {})
    print(f"\n📊 TRADE STATISTICS:")
    print(f"   💼 Final Capital: {trade_stats.get('💼 Final Capital', 'N/A')}")
    print(f"   📊 Total Return: {trade_stats.get('📊 Total Return', 'N/A')}")
    print(f"   🔄 Total Trades: {trade_stats.get('🔄 Total Completed Trades', 'N/A')}")
    
    # Check what's being passed to the chart
    if 'df_bt' in result:
        df = result['df_bt']
        print(f"\n📊 DATA FRAME:")
        print(f"   📅 DataFrame length: {len(df)}")
        print(f"   📈 DataFrame columns: {list(df.columns)}")
        
        # Check for equity columns
        equity_cols = [col for col in df.columns if 'equity' in col.lower() or 'capital' in col.lower()]
        print(f"   💰 Equity-related columns: {equity_cols}")
        
        if equity_cols:
            for col in equity_cols:
                series = df[col]
                print(f"      {col}: {series.iloc[0]:.0f} -> {series.iloc[-1]:.0f} (Range: {series.min():.0f} to {series.max():.0f})")
    
    # Check matched trades
    if 'matched_trades' in result:
        trades = result['matched_trades']
        print(f"\n💹 MATCHED TRADES:")
        print(f"   📈 Number of trades: {len(trades)}")
        if len(trades) > 0:
            print(f"   💰 Final capital in last trade: {trades['Capital'].iloc[-1] if 'Capital' in trades.columns else 'N/A'}")
            print(f"   📊 Columns: {list(trades.columns)}")
            
else:
    print("❌ Backtest failed")
