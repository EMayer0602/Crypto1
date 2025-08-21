# Crypto Data Pipeline (Yahoo + Bitpanda)

This document explains the updated data-loading pipeline and how to use it in daily workflows. CoinGecko is no longer used for the backtest/update path.

## Overview

- Daily data source:
  - T-3 and older: Yahoo Finance daily candles (1d)
  - T-2 and T-1 (if missing): Yahoo Finance hourly (1h) aggregated to daily
  - Today (T): Bitpanda live price preferred; fallback to Yahoo intraday last close
- Files written: SYMBOL_daily.csv (kept up to date per symbol)
- Auto-download: Missing CSVs are automatically downloaded from Yahoo (1y+ range)
- Compatibility: Used by the live backtest and the smart CSV updater

## Common scenarios

- Run daily before backtests
  - Use the smart updater first (minimal changes), or the full Yahoo-advanced updater
- Yesterday is artificial/absent
  - Smart updater backfills yesterday from Yahoo hourly (fallback daily)
- Gaps in last 30 days
  - Smart updater fetches only missing dates from Yahoo daily
- Live price unavailable
  - Today’s row is skipped; historical rows are still updated normally

## Key functions

- get_real_crypto_data.update_csv_files_with_yahoo_advanced(symbols=None)
  - Loads daily data up to T-3, fills T-2/T-1 from hourly if needed, and sets today from a live price proxy (Bitpanda preferred)
  - Saves merged data to SYMBOL_daily.csv

- get_real_crypto_data.update_csv_files_with_realtime_data()
  - Wrapper calling the Yahoo-advanced update (no CoinGecko)
  - Used as a fallback by the live backtest if the smart updater fails

- get_real_crypto_data.get_bitpanda_price(symbol)
  - Public helper returning the latest live price from Bitpanda (fallback to Yahoo intraday)

- smart_csv_update.smart_update_csv_files()
  - Minimal-update mode:
    - Today: inserts today from Bitpanda live price
    - Yesterday: if artificial or absent, backfills from Yahoo hourly/daily
    - Gaps (last 30 days): fills missing dates from Yahoo daily

## How to use

- Orchestrated single‑run (recommended):
  - Run `python live_backtest_WORKING.py`
  - This updates data, generates the 14‑day report, creates `trades_today.json`, and starts the Fusion preview (if Chrome is ready).

- Minimal update + run backtest:
  1) `smart_csv_update.smart_update_csv_files()`
  2) `crypto_backtesting_module.run_live_backtest_analysis()`
  - The live backtest entrypoint can fall back to the full updater automatically.

- Full update only:
  - Run get_real_crypto_data.update_csv_files_with_yahoo_advanced()

## Notes

- CoinGecko code remains in get_real_crypto_data.py but isn’t used in the current pipeline.
- SYMBOL_daily.csv files are auto-created if missing.
- If you see a cosmetic odd character in a log line when setting today’s close, it’s harmless and can be cleaned up later.
- `trades_today.json` is consumed by `BitpandaFusion_trade.py` for safe preview; when there are no orders for today, the Fusion step is skipped by the orchestrator.
