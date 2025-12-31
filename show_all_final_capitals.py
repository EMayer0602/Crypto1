#!/usr/bin/env python3
"""Show final capital for all cryptocurrency versions"""

from crypto_backtesting_module import run_backtest, load_crypto_data_yf
from crypto_tickers import crypto_tickers

def show_all_final_capitals():
    print("=" * 70)
    print("FINAL CAPITAL FOR ALL CRYPTOCURRENCY VERSIONS")
    print("=" * 70)

    results = []
    total_initial = 0
    total_final = 0

    for ticker, config in crypto_tickers.items():
        print(f"\n{'='*70}")
        print(f"Processing {ticker}...")
        print(f"{'='*70}")

        try:
            # Run backtest
            result = run_backtest(ticker, config)

            if result and 'final_capital' in result:
                initial_capital = config.get('initialCapitalLong', 0)
                final_capital = result['final_capital']
                profit = final_capital - initial_capital
                profit_pct = (profit / initial_capital * 100) if initial_capital > 0 else 0

                results.append({
                    'ticker': ticker,
                    'initial': initial_capital,
                    'final': final_capital,
                    'profit': profit,
                    'profit_pct': profit_pct
                })

                total_initial += initial_capital
                total_final += final_capital

                print(f"  Initial Capital: €{initial_capital:,.2f}")
                print(f"  Final Capital:   €{final_capital:,.2f}")
                print(f"  Profit:          €{profit:,.2f} ({profit_pct:+.2f}%)")
            else:
                print(f"  ERROR: No result returned for {ticker}")
                results.append({
                    'ticker': ticker,
                    'initial': config.get('initialCapitalLong', 0),
                    'final': 0,
                    'profit': 0,
                    'profit_pct': 0
                })
        except Exception as e:
            print(f"  ERROR processing {ticker}: {e}")
            results.append({
                'ticker': ticker,
                'initial': config.get('initialCapitalLong', 0),
                'final': 0,
                'profit': 0,
                'profit_pct': 0
            })

    # Print summary
    print(f"\n\n{'='*70}")
    print("SUMMARY - ALL CRYPTOCURRENCIES")
    print(f"{'='*70}")
    print(f"{'Ticker':<12} {'Initial':>12} {'Final':>12} {'Profit':>12} {'Return':>10}")
    print("-" * 70)

    for r in results:
        print(f"{r['ticker']:<12} €{r['initial']:>10,.2f} €{r['final']:>10,.2f} "
              f"€{r['profit']:>10,.2f} {r['profit_pct']:>8.2f}%")

    print("-" * 70)
    total_profit = total_final - total_initial
    total_profit_pct = (total_profit / total_initial * 100) if total_initial > 0 else 0

    print(f"{'TOTAL':<12} €{total_initial:>10,.2f} €{total_final:>10,.2f} "
          f"€{total_profit:>10,.2f} {total_profit_pct:>8.2f}%")
    print("=" * 70)

if __name__ == "__main__":
    show_all_final_capitals()
