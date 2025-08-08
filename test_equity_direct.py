from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

# Teste XRP-EUR direkt
result = run_backtest('XRP-EUR', crypto_tickers['XRP-EUR'])

print("\n=== DIRECT BACKTEST RESULT ===")
print(f"Initial Capital: {crypto_tickers['XRP-EUR'].get('initialCapitalLong', 'NOT FOUND')}")
print(f"Result keys: {list(result.keys()) if result else 'NO RESULT'}")

if result and 'equity_curve' in result:
    eq = result['equity_curve']
    print(f"Equity Curve length: {len(eq)}")
    print(f"First 5 values: {eq[:5]}")
    print(f"Last 5 values: {eq[-5:]}")
    print(f"Min value: {min(eq)}")
    print(f"Max value: {max(eq)}")
else:
    print("NO EQUITY CURVE FOUND!")
