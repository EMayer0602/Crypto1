#!/usr/bin/env python3
"""
Find the most profitable cryptocurrency simulation
Runs backtests for all configured cryptos and ranks them by profitability
"""

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers
from datetime import datetime

def find_most_profitable():
    print("=" * 80)
    print("FINDING MOST PROFITABLE CRYPTOCURRENCY SIMULATION")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = []

    for ticker, config in crypto_tickers.items():
        print(f"\n{'='*80}")
        print(f"Processing {ticker}...")
        print(f"{'='*80}")

        try:
            # Run backtest
            result = run_backtest(ticker, config)

            if result and 'final_capital' in result:
                initial_capital = config.get('initialCapitalLong', 0)
                final_capital = result['final_capital']
                profit = final_capital - initial_capital
                profit_pct = (profit / initial_capital * 100) if initial_capital > 0 else 0

                # Get additional metrics
                num_trades = len(result.get('trades', []))
                win_rate = result.get('win_rate', 0)
                max_drawdown = result.get('max_drawdown', 0)
                sharpe_ratio = result.get('sharpe_ratio', 0)

                results.append({
                    'ticker': ticker,
                    'initial': initial_capital,
                    'final': final_capital,
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'num_trades': num_trades,
                    'win_rate': win_rate,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe_ratio,
                    'result': result
                })

                print(f"✅ SUCCESS")
                print(f"   Initial: €{initial_capital:,.2f}")
                print(f"   Final:   €{final_capital:,.2f}")
                print(f"   Profit:  €{profit:,.2f} ({profit_pct:+.2f}%)")
                print(f"   Trades:  {num_trades}")
            else:
                print(f"❌ FAILED: No valid result returned")

        except Exception as e:
            print(f"❌ ERROR: {e}")

    if not results:
        print("\n❌ No successful backtests. Cannot determine most profitable.")
        return None

    # Sort by profit percentage (descending)
    results.sort(key=lambda x: x['profit_pct'], reverse=True)

    # Print ranking
    print(f"\n\n{'='*80}")
    print("RANKING BY PROFITABILITY")
    print(f"{'='*80}")
    print(f"{'Rank':<6} {'Ticker':<12} {'Initial':>12} {'Final':>12} {'Profit':>12} {'Return':>10} {'Trades':>8}")
    print("-" * 80)

    for i, r in enumerate(results, 1):
        emoji = "🏆" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"{emoji} #{i:<3} {r['ticker']:<12} €{r['initial']:>10,.2f} €{r['final']:>10,.2f} "
              f"€{r['profit']:>10,.2f} {r['profit_pct']:>8.2f}% {r['num_trades']:>8}")

    # Highlight the winner
    winner = results[0]
    print(f"\n{'='*80}")
    print(f"🏆 MOST PROFITABLE SIMULATION: {winner['ticker']}")
    print(f"{'='*80}")
    print(f"Initial Capital:  €{winner['initial']:,.2f}")
    print(f"Final Capital:    €{winner['final']:,.2f}")
    print(f"Total Profit:     €{winner['profit']:,.2f}")
    print(f"Return:           {winner['profit_pct']:+.2f}%")
    print(f"Number of Trades: {winner['num_trades']}")
    if winner['win_rate'] > 0:
        print(f"Win Rate:         {winner['win_rate']:.2f}%")
    if winner['max_drawdown'] != 0:
        print(f"Max Drawdown:     {winner['max_drawdown']:.2f}%")
    print(f"{'='*80}")

    # Print total portfolio performance
    total_initial = sum(r['initial'] for r in results)
    total_final = sum(r['final'] for r in results)
    total_profit = total_final - total_initial
    total_profit_pct = (total_profit / total_initial * 100) if total_initial > 0 else 0

    print(f"\n{'='*80}")
    print("TOTAL PORTFOLIO PERFORMANCE")
    print(f"{'='*80}")
    print(f"Total Initial Capital: €{total_initial:,.2f}")
    print(f"Total Final Capital:   €{total_final:,.2f}")
    print(f"Total Profit:          €{total_profit:,.2f}")
    print(f"Total Return:          {total_profit_pct:+.2f}%")
    print(f"{'='*80}")

    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return winner

if __name__ == "__main__":
    winner = find_most_profitable()
    if winner:
        print(f"\n🎯 Focus on: {winner['ticker']} - Best performer with {winner['profit_pct']:+.2f}% return!")
