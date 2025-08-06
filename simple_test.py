from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

symbol = 'BTC-EUR'
config = crypto_tickers[symbol]
result = run_backtest(symbol, config)

print(f"Weekly Trades count: {result.get('weekly_trades_count', 0)}")
weekly_trades_data = result.get('weekly_trades_data', [])
print(f"Weekly trades data length: {len(weekly_trades_data)}")

for i, trade in enumerate(weekly_trades_data):
    print(f"Trade {i+1}: {trade['Symbol']} {trade['Action']} on {trade['Date']} (ExtIdx: {trade['OriginalIndex']})")
