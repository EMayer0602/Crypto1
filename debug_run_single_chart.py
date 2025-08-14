import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

def main(ticker: str):
    if ticker not in crypto_tickers:
        print(f"Ticker not found in crypto_tickers: {ticker}")
        return 1
    cfg = crypto_tickers[ticker]
    result = run_backtest(ticker, cfg)
    if not result or not result.get('success'):
        print("Backtest failed")
        return 2
    print("Backtest done; chart should be saved in reports/")
    return 0

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else 'BTC-EUR'
    raise SystemExit(main(ticker))
