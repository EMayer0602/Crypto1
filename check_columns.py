from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

symbol = 'BTC-EUR'
config = crypto_tickers[symbol]
result = run_backtest(symbol, config)
ext_full = result.get('ext_signals')  # Richtige Key verwenden

print('Extended Trades Columns:')
print(ext_full.columns.tolist())
print('\nErste 3 Zeilen:')
print(ext_full.head(3).to_string())
print('\nAction values:')
print(ext_full['Action'].unique())
print('\nSample with Trade Day:')
if 'Trade Day' in ext_full.columns:
    print('Trade Day column exists')
    print(ext_full[['Action', 'Trade Day']].head(10))
else:
    print('No Trade Day column. Available date columns:')
    date_cols = [col for col in ext_full.columns if 'date' in col.lower() or 'day' in col.lower()]
    print(date_cols)
    print(ext_full[date_cols + ['Action']].head(5) if date_cols else 'No date columns found')
