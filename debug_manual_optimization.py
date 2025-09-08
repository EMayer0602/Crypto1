#!/usr/bin/env python3
"""Manual test: run XRP-EUR backtest with FORCED parameters (past_window=6, trade_window=2)

This bypasses the automatic optimization to let you inspect the exact outcome
for the chosen parameter pair. It mirrors the core steps in run_backtest:
 1. Load data (limited to backtest_years in config)
 2. Build backtest frame (25%-95%) ONLY for consistency (not used for SR calc here)
 3. Calculate support/resistance on FULL dataset with forced p, tw (same as run_backtest does post-optimization)
 4. Generate extended signals
 5. Simulate matched trades & statistics
 6. Print summary including final capital

Safe to modify or extend for other parameter experiments.
"""
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import (
	load_crypto_data_yf,
	create_backtest_frame,
	calculate_support_resistance,
	assign_long_signals_extended,
	simulate_matched_trades,
	calculate_trade_statistics,
)
from config import backtest_years, backtesting_begin, backtesting_end

FORCED_P = 6
FORCED_TW = 2
SYMBOL = "XRP-EUR"

def main():
	cfg = crypto_tickers[SYMBOL]
	initial_capital = cfg.get("initialCapitalLong", 1000)
	trade_on = cfg.get("trade_on", "Close")
	order_round_factor = cfg.get("order_round_factor", 1)
	commission_rate = cfg.get("commission_rate", 0.0018)  # fallback

	print(f"\n🚀 Manual Forced Parameter Backtest: {SYMBOL} (p={FORCED_P}, tw={FORCED_TW})")
	print(f"   Initial Capital: €{initial_capital}")
	print(f"   Trade On: {trade_on}")
	print(f"   Order Round Factor: {order_round_factor}")
	print(f"   Commission Rate: {commission_rate*100:.3f}%")
	print(f"   Backtest Years (data limit): {backtest_years}")
	print(f"   Backtest Slice Percent Range (info): {backtesting_begin}-{backtesting_end}\n")

	# 1. Load data
	df = load_crypto_data_yf(SYMBOL, backtest_years)
	if df is None or df.empty:
		print("❌ No data loaded")
		return
	print(f"✅ Data Loaded: {len(df)} rows {df.index[0].date()} → {df.index[-1].date()}")

	# 2. Create backtest frame (mirrors main logic, though we compute SR on full df)
	df_bt = create_backtest_frame(df, backtesting_begin, backtesting_end)
	if df_bt is None or df_bt.empty:
		print("⚠️ Backtest frame creation failed (continuing with full data)")
	else:
		print(f"🔍 Backtest Frame: {len(df_bt)} rows {df_bt.index[0].date()} → {df_bt.index[-1].date()}")

	# 3. Support / Resistance on FULL df (same as run_backtest after optimization)
	supp, res = calculate_support_resistance(df, FORCED_P, FORCED_TW, verbose=False, ticker=SYMBOL)
	print(f"📊 Support levels: {len(supp)} | Resistance levels: {len(res)}")

	# 4. Extended signals
	ext = assign_long_signals_extended(supp, res, df, FORCED_TW, "1d", trade_on.title())
	if ext is None or ext.empty:
		print("❌ No extended signals produced")
		return
	print(f"📈 Extended Signals: {len(ext)} rows")

	# 5. Simulate trades
	matched = simulate_matched_trades(ext, initial_capital, commission_rate, df, order_round_factor, trade_on.title())
	print(f"💱 Matched Trades: {len(matched)} (including open if present)")
	if not matched.empty:
		print("   First 3 trades:")
		print(matched.head(3).to_string(index=False))

	# 6. Statistics
	stats = calculate_trade_statistics(ext, matched, initial_capital)
	print("\n📊 Trade Statistics (Forced Params)")
	for k, v in stats.items():
		print(f"   {k}: {v}")

	final_cap = stats.get('💼 Final Capital', 'N/A')
	print(f"\n✅ RESULT SUMMARY: {SYMBOL} p={FORCED_P} tw={FORCED_TW} → Final Capital {final_cap}")

	# Lightweight comparison: If automatic optimal differs, show delta (optional)
	try:
		from crypto_backtesting_module import optimize_parameters
		auto_params = optimize_parameters(df_bt if df_bt is not None else df, SYMBOL)
		auto_p = auto_params.get('optimal_past_window')
		auto_tw = auto_params.get('optimal_trade_window')
		print(f"\nℹ️ Current automatic optimal (for reference): p={auto_p}, tw={auto_tw}")
		if auto_p == FORCED_P and auto_tw == FORCED_TW:
			print("   ➜ Forced params match current optimal.")
		else:
			print("   ➜ Forced params DIFFER from current optimal.")
	except Exception as e:
		print(f"⚠️ Could not fetch automatic optimal for comparison: {e}")

if __name__ == "__main__":
	main()

