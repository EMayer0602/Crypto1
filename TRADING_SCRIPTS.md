## Trading scripts overview

Short, practical index of key scripts and what they do. All commands assume PowerShell in this folder.

- get_august_trades_list.py — Prints a semicolon list for current month (default August if run in Aug)
  - Output columns: Ticker;Date;Action;Shares;Order Type;Limit Price
  - Uses matched_trades from backtest and Bitpanda-preferred live price for Limit Price
  - Run: python get_august_trades_list.py
  - Env overrides: $env:AUGUST_MONTH="8"; $env:AUGUST_YEAR="2025"; python get_august_trades_list.py

- live_backtest_WORKING.py — Generates today-only trades CSV and reports (Yahoo+Bitpanda pipeline)
  - Produces TODAY_ONLY_trades_*.csv and charts in reports/
  - Run: python live_backtest_WORKING.py

- fusion_existing_all_trades_auto.py — Auto-fill Bitpanda Fusion form safely (manual final confirm)
  - Reads TODAY_ONLY_trades_*.csv; strict SELL protection; EUR-only pairs
  - Run: python fusion_existing_all_trades_auto.py
  - Important envs: SELL_CONFIRM, DISABLE_SELLS, STRICT_SELL_PRICE_PROTECT

- trades_weekly_display.py — Newest-first weekly trade snapshot per ticker
  - Run: python trades_weekly_display.py

- debug_equity_calculation.py — Verifies equity curve consistency with Excel-validated logic
  - Run: python debug_equity_calculation.py

- update_yahoo_bitpanda.py / get_real_crypto_data.py — Data update helpers
  - Yahoo daily to T-3; hourly fill for T-2/T-1; today (T) from Bitpanda price
  - Prefer get_real_crypto_data.get_bitpanda_price() for live price

Notes
- CSV/HTML artifacts are ignored by git; scripts recreate missing CSVs.
- Equity curve logic is locked in crypto_backtesting_module.py (do not modify).
