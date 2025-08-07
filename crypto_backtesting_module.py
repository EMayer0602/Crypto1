import warnings
import traceback
warnings.simplefilter("ignore", category=FutureWarning)
import webbrowser
import os
import csv
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from trade_execution import prepare_orders_from_trades, execute_trade, submit_order_bitpanda, save_all_orders_html_report
from config import COMMISSION_RATE, MIN_COMMISSION, ORDER_ROUND_FACTOR, backtesting_begin, backtesting_end, backtest_years
from crypto_tickers import crypto_tickers
from signal_utils import (
    calculate_support_resistance,
    compute_trend,
    assign_long_signals,
    assign_long_signals_extended,
    update_level_close_long,
    simulate_trades_compound_extended,
    berechne_best_p_tw_long,
    plot_combined_chart_and_equity
)
# Am Anfang der Datei bei den anderen Imports hinzufügen:
from trades_weekly_display import display_weekly_trades_console, create_weekly_trades_html

# FIXED: Remove non-existent function
from plotly_utils import (
    plotly_combined_chart_and_equity,
    display_extended_trades_table,
    format_trading_tables,
    create_trades_dataframe,
    print_statistics_table
)
from report_generator import generate_combined_report_from_memory

# Import Weekly Trades Display Module
from trades_weekly_display import (
    display_weekly_trades_console,
    create_weekly_trades_html,
    add_weekly_trades_to_existing_reports
)

# --- Globale Variablen ---
TRADING_MODE = "paper_trading"
API_KEY = ""
capital_plots = {}
CSV_PATH = "C:\\Users\\Edgar.000\\Documents\\____Trading strategies\\Crypto_trading1"
base_dir = "C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading1"

def load_crypto_data_yf(symbol, backtest_years=1, max_retries=3):
    """
    Lädt Crypto-Daten aus existierenden CSV-Dateien
    """
    try:
        # CSV-Datei Namen basierend auf existierendem Format
        csv_filename = f"{symbol}_daily.csv"
        csv_path = os.path.join(os.getcwd(), csv_filename)
        
        # Prüfe ob CSV existiert
        if os.path.exists(csv_path):
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(csv_path))
            print(f"📂 Lade {symbol} aus CSV-Cache ({csv_filename}) - Alter: {file_age.days} Tage")
            
            try:
                df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                print(f"✅ CSV geladen: {len(df)} Zeilen ({df.index[0].date()} bis {df.index[-1].date()})")
                return df
            except Exception as e:
                print(f"❌ CSV-Lesefehler: {e}")
                return None
        else:
            print(f"❌ CSV nicht gefunden: {csv_filename}")
            # Fallback: Lade von Yahoo Finance
            print(f"⬇️ Lade {symbol} von Yahoo Finance...")
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * backtest_years)
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if df.empty:
                print(f"❌ Keine Daten für {symbol}")
                return None
                
            print(f"✅ Download erfolgreich: {len(df)} Zeilen")
            return df
        
    except Exception as e:
        print(f"❌ Fehler beim Laden von {symbol}: {e}")
        return None

def flatten_crypto_header(df):
    # MultiIndex abflachen falls nötig
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # "Price" Spalte entfernen falls vorhanden
    if "Price" in df.columns:
        df = df.drop(columns=["Price"])
    
    # WICHTIG: Duplikate entfernen!
    df = df[~df.index.duplicated(keep='last')]
    
    # Nur OHLCV Spalten behalten
    expected_cols = ["Open", "High", "Low", "Close", "Volume"]
    df = df[expected_cols]
    
    # Index als Date setzen falls nötig
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    df.index.name = "Date"
    
    # Display - NUR die ersten 5 Zeilen!
    print(f"Data shape: {df.shape}")
    print(f"Date range: {df.index.min()} to {df.index.max()}")
    print(df.reset_index().head(5).to_string(index=False))  # <-- LIMIT auf 5!
    
    return df

def save_crypto_csv(df, ticker, data_dir):
    df_out = df.reset_index()
    file_path = os.path.join(data_dir, f"{ticker}_daily.csv")
    df_out.to_csv(file_path, index=False)
    print(f"✅ Gespeichert: {file_path}")

def safe_loader(symbol, csv_path, refresh=True):
    filename = os.path.join(csv_path, f"{symbol}_daily.csv")

    def flatten_csv_header_if_needed(filename):
        with open(filename, "r", encoding="utf-8") as f:
            first = f.readline()
            second = f.readline()
            third = f.readline()
            f.seek(0)
            if first.strip().startswith("Price") and third.strip().startswith("Date"):
                df = pd.read_csv(filename, skiprows=3, header=None)
                df.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
                df.to_csv(filename, index=False)
                print(f"⚒️ Header in {filename} flattened and fixed.")
                return df
            elif first.strip().startswith("Date"):
                return pd.read_csv(filename, parse_dates=["Date"], index_col="Date")
            elif first.strip().startswith("Price"):
                df = pd.read_csv(filename)
                df = df.rename(columns={"Price": "Date"})
                df.to_csv(filename, index=False)
                print(f"⚒️ Header in {filename} fixed (Price->Date).")
                return pd.read_csv(filename, parse_dates=["Date"], index_col="Date")
            else:
                raise ValueError(f"Unrecognized header in {filename}")

    if os.path.exists(filename):
        try:
            df_local = flatten_csv_header_if_needed(filename)
            if "Date" in df_local.columns:
                df_local["Date"] = pd.to_datetime(df_local["Date"])
                df_local.set_index("Date", inplace=True)
            last_local_date = df_local.index.max()
        except Exception as e:
            print(f"⚠️ {symbol} CSV-Problem: {e}. Lösche und lade neu.")
            os.remove(filename)
            df_local = pd.DataFrame()
            last_local_date = None
    else:
        df_local = pd.DataFrame()
        last_local_date = None

    today = pd.Timestamp(datetime.utcnow().date())
    if last_local_date is not None:
        next_date = last_local_date + pd.Timedelta(days=1)
        if next_date > today:
            print(f"{symbol}: Already up to date.")
            return df_local
        start_date = next_date.strftime('%Y-%m-%d')
    else:
        start_date = "2024-07-01"

    df_new = yf.download(symbol, start=start_date, end=None, interval="1d", auto_adjust=True, progress=False)
    if df_new is None or df_new.empty:
        print(f"⚠️ {symbol}: Keine neuen Daten")
        return df_local if not df_local.empty else None

    df_new.index.name = "Date"
    df_new = df_new[["Open", "High", "Low", "Close", "Volume"]].copy()
    if not df_local.empty:
        df_new = df_new[~df_new.index.isin(df_local.index)]

    df_combined = pd.concat([df_local, df_new])
    df_combined.sort_index(inplace=True)
    df_combined.to_csv(filename)
    print(f"✅ {symbol}: aktualisiert bis {df_combined.index.max().date()}")

    return df_combined

# Nach den imports, vor den anderen Funktionen:

def compute_equity_curve(df, trades, start_capital, long=True):
    '''
    Berechnet die Equity-Kurve exakt entlang df.index.
    Nutzt reale Entry/Exit und täglich aktuelle Close-Preise.
    Wenn investiert, folgt es dem Close-Preis.
    '''
    equity = []
    cap = start_capital
    pos = 0
    entry_price = 0
    trade_idx = 0

    for date in df.index:
        # Entry? - Angepasst an matched_trades Struktur
        if trade_idx < len(trades):
            # Unterstütze beide Strukturen: matched_trades und original trades
            entry_key = "Entry Date" if "Entry Date" in trades[trade_idx] else ("buy_date" if long else "short_date")
            entry_price_key = "Entry Price" if "Entry Price" in trades[trade_idx] else ("buy_price" if long else "short_price")
            
            try:
                entry_date = pd.Timestamp(trades[trade_idx].get(entry_key))
                if entry_date == date:
                    # Shares aus matched_trades oder berechne basierend auf Capital
                    if "Shares" in trades[trade_idx]:
                        pos = trades[trade_idx]["Shares"]
                    elif "shares" in trades[trade_idx]:
                        pos = trades[trade_idx]["shares"]
                    else:
                        # Fallback: Berechne Shares aus Entry Price und verfügbarem Capital
                        entry_price_val = trades[trade_idx][entry_price_key]
                        pos = cap / entry_price_val if entry_price_val > 0 else 0
                    
                    entry_price = trades[trade_idx][entry_price_key]
                    print(f"   📈 ENTRY {date.strftime('%Y-%m-%d')}: {pos:.4f} shares @ €{entry_price:.2f}")
            except (KeyError, ValueError, TypeError):
                pass

        # Exit? - Angepasst an matched_trades Struktur (aber nicht bei offenen Trades)
        if trade_idx < len(trades):
            exit_key = "Exit Date" if "Exit Date" in trades[trade_idx] else ("sell_date" if long else "cover_date")
            trade_status = trades[trade_idx].get("Status", "CLOSED")
            
            try:
                exit_date = pd.Timestamp(trades[trade_idx].get(exit_key))
                # Nur bei geschlossenen Trades als Exit behandeln
                if exit_date == date and trade_status == "CLOSED":
                    # PnL aus matched_trades oder berechne
                    if "PnL" in trades[trade_idx]:
                        pnl = trades[trade_idx]["PnL"]
                    elif "pnl" in trades[trade_idx]:
                        pnl = trades[trade_idx]["pnl"]
                    else:
                        # Fallback: Berechne PnL aus Exit Price
                        exit_price = trades[trade_idx].get("Exit Price", df.loc[date, "Close"])
                        pnl = pos * (exit_price - entry_price) if long else pos * (entry_price - exit_price)
                    
                    cap += pnl
                    print(f"   📉 EXIT  {date.strftime('%Y-%m-%d')}: PnL €{pnl:.2f}, New Capital €{cap:.2f}")
                    pos = 0
                    entry_price = 0
                    trade_idx += 1
                elif trade_status == "OPEN" and exit_date <= date:
                    # Bei offenen Trades: Wechsle zum nächsten Trade ohne Exit
                    trade_idx += 1
            except (KeyError, ValueError, TypeError):
                pass

        # Kapitalwert berechnen - FOLGT CLOSE-PREIS WENN INVESTIERT
        if pos > 0:
            current_price = df.loc[date, "Close"]
            # Unrealized P&L basierend auf aktuellem Close-Preis
            delta = (current_price - entry_price) if long else (entry_price - current_price)
            unrealized_pnl = pos * delta
            value = cap + unrealized_pnl
        else:
            # Nicht investiert - nur Cash
            value = cap

        equity.append(value)

    return equity  # ← exakt gleich lang wie df.index

def debug_equity_alignment(df, equity_curve):
    '''
    Prüft, ob die Equity-Kurve exakt die gleiche Länge und Zeitachse wie df.index hat.
    Gibt Warnungen bei Diskrepanzen.
    '''
    n_df = len(df.index)
    n_eq = len(equity_curve)
    print(f"   ✅ Candlestick-Zeilen: {n_df}")
    print(f"   ✅ Equity-Zeilen:      {n_eq}")

    if n_df != n_eq:
        print(f"   ❌ Unterschiedliche Länge! Equity-Kurve hat {n_eq - n_df:+d} Zeilen Abweichung.")
        return False

    mismatches = []
    for i, dt in enumerate(df.index):
        if pd.isna(dt) or not isinstance(dt, pd.Timestamp):
            mismatches.append((i, "NaT oder kein Timestamp in df.index"))

    if mismatches:
        print(f"   ⚠️ {len(mismatches)} problematische Zeilen:")
        for i, reason in mismatches[:5]:
            print(f"     Zeile {i}: {reason}")
        return False
    else:
        print("   ✅ Alles ok. Index ist zeilensynchron und verwendbar für Plotly.")
        return True

def main_backtest_with_analysis():
    """
    Hauptfunktion für Enhanced Backtest Analysis mit realistischen Equity Curves
    """
    try:
        print("🚀 Starting Enhanced Backtest Analysis...")
        print(f"📅 Backtest Period: {backtest_years} years")
        print(f"🎯 Optimization Range: 25% - 95%")
        print(f"💰 Initial Capital: €10000")
        
        all_results = {}
        successful_symbols = []
        failed_symbols = []
        
        # Process each crypto ticker
        for symbol, config in crypto_tickers.items():
            print(f"\n{'='*60}")
            print(f"🔄 Processing {symbol}...")
            
            try:
                result = run_backtest(symbol, config)
                
                if result and result != False:
                    all_results[symbol] = result
                    successful_symbols.append(symbol)
                    print(f"✅ Successfully processed {symbol}")
                else:
                    failed_symbols.append(symbol)
                    print(f"❌ Failed to process {symbol}")
                    
            except Exception as e:
                print(f"❌ Error processing {symbol}: {e}")
                failed_symbols.append(symbol)
                continue
        
        # Summary Report
        print(f"\n{'='*80}")
        print("📊 BACKTEST SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Successfully processed {len(successful_symbols)} symbols")
        if successful_symbols:
            print(f"   Symbols: {', '.join(successful_symbols)}")
        
        if failed_symbols:
            print(f"❌ Failed symbols ({len(failed_symbols)}): {', '.join(failed_symbols)}")
        
        if not all_results:
            print("❌ No successful backtests completed!")
            return False, {}
        
        # Portfolio statistics
        print(f"\n📊 Generating comprehensive analysis...")
        portfolio_stats = {}
        total_initial_capital = 0
        total_final_capital = 0
        
        for symbol, result in all_results.items():
            if isinstance(result, dict) and 'config' in result:
                initial_cap = result['config'].get('initial_capital', 10000)
                total_initial_capital += initial_cap
                
                if 'trade_statistics' in result:
                    stats = result['trade_statistics']
                    if '💼 Final Capital' in stats:
                        try:
                            final_cap_str = stats['💼 Final Capital'].replace('€', '').replace(',', '')
                            final_capital = float(final_cap_str)
                            total_final_capital += final_capital
                        except:
                            total_final_capital += initial_cap
                    else:
                        total_final_capital += initial_cap
                else:
                    total_final_capital += initial_cap
        
        portfolio_stats['Total Initial Capital'] = f"€{total_initial_capital:,.2f}"
        portfolio_stats['Total Final Capital'] = f"€{total_final_capital:,.2f}"
        portfolio_stats['Total Portfolio Return'] = f"{((total_final_capital/total_initial_capital-1)*100):.2f}%" if total_initial_capital > 0 else "0.00%"
        portfolio_stats['Number of Assets'] = len(all_results)
        
        print(f"\n💼 PORTFOLIO SUMMARY:")
        for key, value in portfolio_stats.items():
            print(f"   {key}: {value}")
        
        # Detailed symbol analysis
        print(f"\n📈 DETAILED SYMBOL ANALYSIS:")
        for symbol, result in all_results.items():
            if isinstance(result, dict):
                print(f"\n📊 {symbol}:")
                if 'trade_statistics' in result:
                    for key, value in result['trade_statistics'].items():
                        print(f"   {key}: {value}")
                
                if 'dataset_info' in result:
                    info = result['dataset_info']
                    print(f"   📅 Period: {info['start_date']} to {info['end_date']} ({info['total_days']} days)")
                
                if 'optimal_parameters' in result:
                    params = result['optimal_parameters']
                    pnl_info = ""
                    if 'optimal_pnl' in params:
                        pnl_info = f", PnL=€{params['optimal_pnl']:.2f}"
                    print(f"   🎯 Optimal Parameters: Past_Window={params.get('optimal_past_window', 'N/A')}, Trade_Window={params.get('optimal_trade_window', 'N/A')}{pnl_info}")
        
        # Save CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        portfolio_csv_path = f"portfolio_summary_{timestamp}.csv"
        
        summary_data = []
        for symbol, result in all_results.items():
            if isinstance(result, dict):
                row = {
                    'Symbol': symbol,
                    'Initial_Capital': result.get('config', {}).get('initial_capital', 0),
                    'Support_Levels': result.get('support_levels', 0),
                    'Resistance_Levels': result.get('resistance_levels', 0)
                }
                summary_data.append(row)
        
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_csv(portfolio_csv_path, index=False)
            print(f"📁 Portfolio Summary saved: {portfolio_csv_path}")
        
        # Generate HTML Report
        try:
            generate_combined_report_from_memory(all_results, portfolio_csv_path)
            print(f"📄 HTML Report generated")
        except Exception as e:
            print(f"⚠️ HTML report error: {e}")
        
        # ✅ CHARTS ERSTELLEN - MIT REALISTISCHEN EQUITY CURVES
        print(f"\n🌐 Creating Interactive Charts with Real Equity Curves...")
        chart_count = 0
        
        for symbol, result in all_results.items():
            try:
                if not isinstance(result, dict) or 'df_bt' not in result:
                    continue
                
                print(f"\n📊 Creating chart for {symbol}...")
                
                # Data preparation
                df = result['df_bt'].copy()
                ext_signals = result.get('ext_signals', pd.DataFrame())
                matched_trades = result.get('matched_trades', pd.DataFrame())
                
                # Extract Support/Resistance
                support_series = pd.Series(dtype=float)
                resistance_series = pd.Series(dtype=float)
                
                if not ext_signals.empty:
                    # Support levels
                    support_data = ext_signals[ext_signals['Supp/Resist'] == 'support']
                    if not support_data.empty:
                        support_dates = pd.to_datetime(support_data['Date high/low'])
                        support_levels = support_data['Level high/low'].values
                        support_series = pd.Series(support_levels, index=support_dates)
                    
                    # Resistance levels
                    resistance_data = ext_signals[ext_signals['Supp/Resist'] == 'resistance']
                    if not resistance_data.empty:
                        resistance_dates = pd.to_datetime(resistance_data['Date high/low'])
                        resistance_levels = resistance_data['Level high/low'].values
                        resistance_series = pd.Series(resistance_levels, index=resistance_dates)
                
                # Add buy/sell signals to DataFrame
                df['buy_signal'] = 0
                df['sell_signal'] = 0
                
                if not ext_signals.empty:
                    # Buy signals
                    buy_signals = ext_signals[ext_signals['Action'] == 'buy']
                    for _, row in buy_signals.iterrows():
                        try:
                            trade_date = pd.to_datetime(row['Long Date detected'])
                            if trade_date in df.index:
                                df.loc[trade_date, 'buy_signal'] = 1
                        except:
                            continue
                    
                    # Sell signals
                    sell_signals = ext_signals[ext_signals['Action'] == 'sell']
                    for _, row in sell_signals.iterrows():
                        try:
                            trade_date = pd.to_datetime(row['Long Date detected'])
                            if trade_date in df.index:
                                df.loc[trade_date, 'sell_signal'] = 1
                        except:
                            continue
                
                # ✅ EQUITY CURVES BERECHNUNG
                initial_capital = result.get('config', {}).get('initial_capital', 10000)
                
                # 1. Strategy Equity Curve aus matched_trades
                if not matched_trades.empty:
                    print(f"   💼 Computing strategy equity curve from {len(matched_trades)} trades...")
                    
                    # Convert matched_trades DataFrame to list of dicts
                    trades_list = []
                    for _, trade in matched_trades.iterrows():
                        trade_dict = trade.to_dict()
                        trades_list.append(trade_dict)
                    
                    # Debug erste paar Trades
                    print(f"   🔍 First trade example:")
                    if len(trades_list) > 0:
                        first_trade = trades_list[0]
                        for key, value in first_trade.items():
                            if key in ['Entry Date', 'Exit Date', 'Entry Price', 'Exit Price', 'Shares', 'PnL']:
                                print(f"     {key}: {value}")
                    
                    # Berechne Strategy Equity Curve
                    equity_curve = compute_equity_curve(df, trades_list, initial_capital, long=True)
                    
                    # Debug equity alignment
                    equity_ok = debug_equity_alignment(df, equity_curve)
                    
                    if not equity_ok:
                        print(f"   ⚠️ Using fallback equity curve")
                        equity_curve = [initial_capital] * len(df)
                else:
                    print(f"   ⚠️ No matched trades - using constant equity")
                    equity_curve = [initial_capital] * len(df)
                
                # 2. ✅ BUY & HOLD EQUITY CURVE
                print(f"   📈 Computing buy & hold equity curve...")
                buyhold_curve = []  # ✅ INITIALISIERE HIER!
                
                if len(df) > 0 and "Close" in df.columns:
                    start_price = df['Close'].iloc[0]
                    if start_price > 0:
                        for price in df['Close']:
                            current_return = price / start_price
                            buyhold_curve.append(initial_capital * current_return)
                        
                        # Debug buy & hold alignment
                        buyhold_ok = debug_equity_alignment(df, buyhold_curve)
                        
                        if not buyhold_ok:
                            buyhold_curve = [initial_capital] * len(df)
                    else:
                        buyhold_curve = [initial_capital] * len(df)
                else:
                    buyhold_curve = [initial_capital] * len(df)
                
                # 3. ✅ STATISTICS
                final_strategy = equity_curve[-1] if equity_curve else initial_capital
                final_buyhold = buyhold_curve[-1] if buyhold_curve else initial_capital
                strategy_return = ((final_strategy / initial_capital - 1) * 100) if initial_capital > 0 else 0
                buyhold_return = ((final_buyhold / initial_capital - 1) * 100) if initial_capital > 0 else 0
                
                print(f"   🟢 Support: {len(support_series)}, 🔴 Resistance: {len(resistance_series)}")
                print(f"   🔵 Buy: {len(df[df['buy_signal'] == 1])}, 🟠 Sell: {len(df[df['sell_signal'] == 1])}")
                print(f"   💼 Strategy: €{initial_capital:,.0f} → €{final_strategy:,.0f} ({strategy_return:+.1f}%)")
                print(f"   📈 Buy&Hold: €{initial_capital:,.0f} → €{final_buyhold:,.0f} ({buyhold_return:+.1f}%)")
                
                # 4. ✅ CHART ERSTELLEN
                chart_success = plotly_combined_chart_and_equity(
                    df=df,
                    standard_signals=ext_signals,
                    support=support_series,
                    resistance=resistance_series,
                    equity_curve=equity_curve,
                    buyhold_curve=buyhold_curve,
                    ticker=symbol,
                    backtest_years=backtest_years
                )
                
                if chart_success:
                    print(f"   ✅ Chart created for {symbol}")
                    chart_count += 1
                    time.sleep(2)  # Pause zwischen Charts
                else:
                    print(f"   ❌ Chart failed for {symbol}")
                    
            except Exception as e:
                print(f"   ❌ Chart error for {symbol}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n🎯 Created {chart_count} interactive charts with real equity curves!")
        print(f"📊 Each chart includes:")
        print(f"   🟢 Support levels (green circles)")
        print(f"   🔴 Resistance levels (red X)")
        print(f"   🔵 Buy signals (blue triangles ↑)")
        print(f"   🟠 Sell signals (orange triangles ↓)")
        print(f"   💼 Strategy equity curve (real trades)")
        print(f"   📈 Buy & Hold comparison")
        
        # Trading Mode Info
        if TRADING_MODE == 'paper_trading':
            print(f"\n📝 PAPER TRADING MODE - No real orders executed")
        
        return all_results, portfolio_stats
        
    except Exception as e:
        print(f"❌ Main backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return False, {}

def create_backtest_frame(df, begin_percent=None, end_percent=None):
    """
    Erstellt df_bt aus dem Prozentbereich der Daten
    Verwendet config.py Werte als Standard
    """
    if df is None or df.empty:
        return None
    
    # Verwende config.py Werte wenn nicht explizit angegeben
    if begin_percent is None:
        begin_percent = backtesting_begin
    if end_percent is None:
        end_percent = backtesting_end
    
    n = len(df)
    start_idx = int(n * begin_percent / 100)
    end_idx = int(n * end_percent / 100)
    
    # Sicherstellen, dass Indizes gültig sind
    start_idx = max(0, min(start_idx, n - 1))
    end_idx = max(start_idx + 1, min(end_idx, n))
    
    df_bt = df.iloc[start_idx:end_idx].copy()
    
    print(f"\n📊 === BACKTEST DATA RANGE ===")
    print(f"📈 Gesamte Daten: {n} Zeilen")
    print(f"📅 Vollständiger Zeitraum: {df.index.min().date()} bis {df.index.max().date()}")
    print(f"🧪 Backtest-Bereich: {begin_percent}% - {end_percent}% der Daten")
    print(f"📅 Backtest-Zeitraum: {df_bt.index.min().date()} bis {df_bt.index.max().date()}")
    print(f"📊 Backtest-Zeilen: {len(df_bt)} (Index {start_idx} bis {end_idx})")
    
    return df_bt

def load_and_update_daily_crypto(minute_df, symbol, base_dir):
    # --- MultiIndex flatten falls nötig ---
    if isinstance(minute_df.columns, pd.MultiIndex):
        minute_df.columns = minute_df.columns.get_level_values(0)

    # Spaltennamen vereinheitlichen (Großbuchstaben)
    col_map = {c.lower(): c for c in ['Open', 'High', 'Low', 'Close', 'Volume']}
    minute_df = minute_df.rename(columns={c: col_map.get(c.lower(), c) for c in minute_df.columns})

    # Prüfen ob alle Spalten da sind
    required = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(r in minute_df.columns for r in required):
        raise ValueError(f"[{symbol}] Minutendaten fehlen Spalten: {set(required) - set(minute_df.columns)}")

    # Datumsspalte erzeugen
    if "datetime" in minute_df.columns:
        minute_df['date'] = pd.to_datetime(minute_df['datetime']).dt.date
    else:
        minute_df['date'] = pd.to_datetime(minute_df.index).date

    grouped = minute_df.groupby('date')
    daily = pd.DataFrame({
        "date": grouped["date"].first(),
        "Open": grouped["Open"].first(),
        "High": grouped["High"].max(),
        "Low": grouped["Low"].min(),
        "Close": grouped["Close"].last(),
        "Volume": grouped["Volume"].sum()
    })
    daily = daily.sort_values("date").reset_index(drop=True)

    daily_path = os.path.join(base_dir, f"{symbol}_daily.csv")
    daily[["date", "Open", "High", "Low", "Close", "Volume"]].to_csv(
        daily_path, index=False, header=True
    )
    print(f"[{symbol}] ✅ Tagesdaten gespeichert unter: {daily_path}")
    return daily

def flatten_and_rename_columns(df, new_columns=None):
    # Flacht MultiIndex ab und setzt neue Spaltennamen
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[1].capitalize() for col in df.columns]
    else:
        df.columns = [str(col).strip().capitalize() for col in df.columns]
    if new_columns is not None:
        df.columns = new_columns
    return df

def load_daily_csv(filename):
    """
    Lädt eine Tagesdaten-CSV mit richtigem Header.
    Erwartet: Date,Open,High,Low,Close,Volume als Spalten.
    Gibt DataFrame mit Date als Index zurück.
    """
    df = pd.read_csv(filename, parse_dates=["Date"])
    df = df.set_index("Date")
    return df

def safe_parse_date(date_str):
    """Versucht, ein Datum im erwarteten Format zu parsen. Fehler werden zu NaT."""
    try:
        return pd.to_datetime(date_str, format="%Y-%m-%d %H:%M:%S")
    except:
        return pd.NaT

def clean_crypto_csv(filepath):
    with open(filepath, "r") as file:
        raw = file.readlines()

    # 🧠 Prüfe, ob es sich um doppelte Header handelt
    if len(raw) >= 3 and "Date" in raw[2]:
        print("🔍 Doppelte Header erkannt – bereinige...")
        raw_clean = raw[2:]  # Nur relevante Zeilen ab Zeile 3
        temp_path = filepath.replace(".csv", "_cleaned.csv")

        with open(temp_path, "w") as f:
            f.writelines(raw_clean)

        df = pd.read_csv(temp_path, parse_dates=["Date"])
        print(f"✅ Bereinigt geladen: {len(df)} Zeilen | Datei: {temp_path}")
    else:
        df = pd.read_csv(filepath, parse_dates=["Date"])
        print(f"ℹ️ Normale CSV geladen: {len(df)} Zeilen")

    return df

def debug_loader_status(ticker, csv_path, days=365):
    import os
    import pandas as pd
    import yfinance as yf

    filename = os.path.join(csv_path, f"{ticker}.csv")
    print(f"\n📦 Debug für Ticker: {ticker}")
    print(f"🗂️ Datei erwartet unter: {filename}")
    if not os.path.exists(filename):
        print("🚫 CSV existiert noch nicht.")
    else:
        try:
            df_local = pd.read_csv(filename, parse_dates=["Date"], index_col="Date")
            print(f"✅ Lokale Datei gefunden, letztes Datum: {df_local.index.max().date()}")
        except Exception as e:
            print(f"❌ Fehler beim Laden der CSV: {e}")
            df_local = None

    print("🌐 Versuche Online-Download von yfinance...")
    try:
        df_online = yf.download(ticker, interval="1d", period=f"{days}d", auto_adjust=True, progress=False)
        if df_online.empty:
            print("⚠️ Keine Daten aus Yahoo erhalten.")
        else:
            print(f"📅 Daten von {df_online.index.min().date()} bis {df_online.index.max().date()}")
            print(f"🧾 Online-Datenanzahl: {len(df_online)} Zeilen")
    except Exception as e:
        print(f"❌ Fehler beim yfinance-Download: {e}")


def calculate_trade_statistics(matched_trades, equity_curve, initial_capital, commission_rate):
    """Calculate comprehensive trade statistics"""
    print("calculate_trade_statistics called")
    
    if not matched_trades:
        return {
            'Total Trades': 0,
            'Winning Trades': 0,
            'Losing Trades': 0,
            'Win Percentage': 0.0,
            'Loss Percentage': 0.0,
            'Total PnL': 0.0,
            'Total Fees': 0.0,
            'Final Capital': initial_capital,
            'Max Drawdown': 0.0
        }
    
    # Basic trade statistics
    total_trades = len(matched_trades)
    winning_trades = sum(1 for trade in matched_trades if trade['pnl'] > 0)
    losing_trades = total_trades - winning_trades
    
    win_percentage = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    loss_percentage = (losing_trades / total_trades * 100) if total_trades > 0 else 0
    
    total_pnl = sum(trade['pnl'] for trade in matched_trades)
    total_fees = sum(trade['total_fees'] for trade in matched_trades)
    final_capital = initial_capital + total_pnl
    
    # Calculate max drawdown
    max_drawdown = 0.0
    peak = initial_capital
    current_capital = initial_capital
    
    for trade in matched_trades:
        current_capital += trade['pnl']
        if current_capital > peak:
            peak = current_capital
        drawdown = (peak - current_capital) / peak * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    stats = {
        'Total Trades': total_trades,
        'Winning Trades': winning_trades,
        'Losing Trades': losing_trades,
        'Win Percentage': round(win_percentage, 2),
        'Loss Percentage': round(loss_percentage, 2),
        'Total PnL': round(total_pnl, 3),
        'Total Fees': round(total_fees, 3),
        'Final Capital': round(final_capital, 3),
        'Max Drawdown': round(max_drawdown, 2)
    }
    
    print(f"calculate_trade_statistics returning: {stats}")
    return stats

def backtest_single_ticker(cfg, symbol):
    import pandas as pd

    # Daten laden
    df = load_crypto_data_yf(symbol)
    if df is None or df.empty:
        print(f"⚠️ Keine Daten für {symbol}")
        return None

    # Spalten abflachen und prüfen
    df = flatten_and_rename_columns(df)
    expected_cols = {"Open", "High", "Low", "Close", "Volume"}
    if not expected_cols.issubset(set(df.columns)):
        print(f"⚠️ Fehlende Spalten für {symbol}: {set(df.columns)}")
        return None

    # Backtest-Zeitraum filtern (letzte N Jahre)
    backtest_years = cfg.get("backtest_years", [1])
    years = backtest_years[-1] if isinstance(backtest_years, list) else backtest_years
    end_date = df.index.max()
    start_date = end_date - pd.DateOffset(years=years)
    df_bt = df[(df.index >= start_date) & (df.index <= end_date)]

    # Prozentwerte für Start/Ende aus Konfiguration
    start_percent = cfg.get("backtest_start_percent", 0.25)
    end_percent = cfg.get("backtest_end_percent", 0.95)
    n = len(df_bt.index)
    start_idx = int(n * start_percent)
    end_idx = int(n * end_percent)
    start_idx = max(0, min(start_idx, n - 1))
    end_idx = max(0, min(end_idx, n - 1))

    # Parameter-Optimierung
    p, tw = berechne_best_p_tw_long(
        df_bt, cfg,
        start_idx, end_idx,
        verbose=False,
        ticker=symbol
    )

    # Support/Resistance
    supp_bt, res_bt = calculate_support_resistance(df_bt, p, tw, verbose=False, ticker=symbol)

    # Signale
    std_bt = assign_long_signals(supp_bt, res_bt, df_bt, tw, "1d")
    ext_bt = assign_long_signals_extended(supp_bt, res_bt, df_bt, tw, "1d")
    ext_bt = update_level_close_long(ext_bt, df_bt)

    # Trades simulieren
    cap_bt, trades_bt = simulate_trades_compound_extended(
        ext_bt, df_bt, cfg,
        starting_capital=cfg.get("initialCapitalLong", 10000),
        commission_rate=cfg.get("commission_rate", 0.001),
        min_commission=cfg.get("min_commission", 1.0),
        round_factor=cfg.get("order_round_factor", 1)
    )

    # Buy & Hold-Kurve
    bh_curve_bt = [cfg.get("initialCapitalLong", 10000) * (p / df_bt["Close"].iloc[0]) for p in df_bt["Close"]]

    # Plot
    plot_combined_chart_and_equity(
        df_bt,
        std_bt,
        supp_bt,
        res_bt,
        trades_bt,
        bh_curve_bt,
        symbol,
        initial_capital=cfg.get("initialCapitalLong", 10000),
        backtest_years=backtest_years
    )

    return cap_bt, trades_bt, std_bt, supp_bt, res_bt, bh_curve_bt

def load_daily_data_for_backtest(symbol, base_dir):
    filename = f"{symbol}_daily.csv"
    daily_path = os.path.join(base_dir, filename)
    if not os.path.exists(daily_path):
        print(f"[{symbol}] ❌ Datei fehlt: {daily_path}")
        return None
    try:
        df = pd.read_csv(daily_path, parse_dates=["date"])
        return df
    except Exception as e:
        print(f"[{symbol}] ❌ Fehler beim Einlesen: {e}")
        return None

def batch_update_all(base_dir, start_date_daily="2020-01-01", start_date_minute="2024-01-01"):
    for symbol in crypto_tickers:
        update_daily_csv(symbol, base_dir, start_date_daily)
        update_minute_csv(symbol, base_dir, start_date_minute)

def update_daily_csv(symbol, base_dir, start_date="2024-07-31"):
    """
    Lädt Tagesdaten via yfinance für das Symbol und speichert sie als saubere CSV.
    Header ist IMMER korrekt! Erzeugt Datei {symbol}_daily.csv im base_dir.
    """
    df = yf.download(symbol, start=start_date, interval="1d", auto_adjust=True, progress=False)
    if df is None or df.empty:
        print(f"[{symbol}] ⚠️ Keine Daten gefunden.")
        return None

    # MultiIndex-Problem lösen
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()  # Date als Spalte

    if 'Date' not in df.columns:
        print(f"[{symbol}] ⚠️ 'Date' column not found after reset_index.")
        return None

    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

    # Ensure directory exists
    os.makedirs(base_dir, exist_ok=True)

    # Speichern mit sauberem Header
    out_path = os.path.join(base_dir, f"{symbol}_daily.csv")
    df.to_csv(out_path, index=False, header=True)
    print(f"[{symbol}] ✅ Daily CSV gespeichert: {out_path}")
    return df

def update_minute_csv(symbol, base_dir, start_date):
    import os
    import yfinance as yf
    import pandas as pd

    df = yf.download(symbol, start=start_date, interval="1m", auto_adjust=True, progress=False)
    if df is None or df.empty:
        print(f"[{symbol}] ⚠️ Keine Minutendaten gefunden.")
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()

    # Zeitspalte auf "DateTime" bringen
    if "Datetime" in df.columns:
        df = df.rename(columns={"Datetime": "DateTime"})
    elif "Date" in df.columns:
        df = df.rename(columns={"Date": "DateTime"})
    elif "index" in df.columns:
        df = df.rename(columns={"index": "DateTime"})
    else:
        raise ValueError("Keine Zeitspalte gefunden! Spalten sind: " + str(df.columns))

    # Volume erzwingen
    if "Volume" not in df.columns:
        print(f"[{symbol}] ⚠️ Volume fehlt, wird mit NaN ergänzt.")
        df["Volume"] = float("nan")

    # Nur gewünschte Spalten und speichern
    df = df[["DateTime", "Open", "High", "Low", "Close", "Volume"]]
    out_path = os.path.join(base_dir, f"{symbol}_minute.csv")
    df.to_csv(out_path, index=False, header=True)
    print(f"[{symbol}] ✅ Minute CSV gespeichert: {out_path}")
    return df

def batch_update_all_daily_csv(base_dir, get_minute_df_func):
    """
    Für alle Ticker aus crypto_tickers wird load_and_update_daily_crypto ausgeführt.
    get_minute_df_func(symbol) muss ein DataFrame der Minutendaten zurückgeben.
    """
    for ticker, cfg in crypto_tickers.items():
        symbol = cfg["symbol"]
        print(f"\n⏳ Lade Minutendaten für {symbol} ...")
        try:
            minute_df = get_minute_df_func(symbol)
            if minute_df is None or minute_df.empty:
                print(f"[{symbol}] ⚠️ Keine Minutendaten gefunden, überspringe.")
                continue
            load_and_update_daily_crypto(minute_df, symbol, base_dir)
        except Exception as e:
            print(f"[{symbol}] ❌ Fehler: {e}")

def get_minute_df_yfinance(symbol):
    import yfinance as yf
    df = yf.download(symbol, period="5d", interval="1m", progress=False, auto_adjust=True)
    return df if df is not None and not df.empty else None

def update_daily_crypto_with_today1(minute_df, symbol, daily_path):
    """
    Aggregiert die Minutendaten zu Tagesdaten,
    entfernt doppelte Headerstufen und sichert das Datum gegen Parsingfehler.
    """
    if minute_df is None or minute_df.empty:
        print(f"[{symbol}] ❌ Keine gültigen Minutendaten vorhanden.")
        return

    # 🧽 Schritt 1: Datum bereinigen
    minute_df["Date"] = minute_df["Date"].apply(safe_parse_date)
    minute_df["Date"] = pd.to_datetime(minute_df["Date"]).dt.date

    # 🔁 Schritt 2: Aggregation auf Tagesbasis
    daily_df_new = minute_df.groupby("Date").agg({
        "price": ["first", "max", "min", "last"],
        "volume": "sum"
    })

    # 🧹 Schritt 3: Header flatten
    daily_df_new.columns = ["Open", "High", "Low", "Close", "Volume"]
    daily_df_new.index = pd.to_datetime(daily_df_new.index)

    # 📁 Schritt 4: Vorhandene Datei laden (falls vorhanden)
    if os.path.exists(daily_path):
        daily_df_existing = pd.read_csv(daily_path, parse_dates=["Date"], index_col="Date")
        daily_df_existing.index = pd.to_datetime(daily_df_existing.index)
        daily_df = pd.concat([daily_df_existing, daily_df_new])
        daily_df = daily_df[~daily_df.index.duplicated(keep="last")]  # Duplikate entfernen
    else:
        daily_df = daily_df_new

    # 💾 Schritt 5: Speichern mit sauberem Header
    daily_df.to_csv(daily_path, index=True)
    print(f"[{symbol}] ✅ Tagesdaten erfolgreich aktualisiert.")

def update_daily_crypto_with_today():
    base_dir = "C:/Users/Edgar.000/Documents/____Trading strategies/Crypto_trading1/"
    os.makedirs(CSV_PATH, exist_ok=True)

    for ticker, cfg in crypto_tickers.items():
        symbol = cfg["symbol"]
        print(f"\n📈 Lade {symbol}...")

        try:
            # Lade Tagesdaten aus Yahoo
            df = yf.download(symbol, interval="1d", period="30d", auto_adjust=True, progress=False)

            if df is None or df.empty:
                print(f"[{symbol}] ⚠️ Keine Daten erhalten")
                continue

            df.columns = [str(c).strip().capitalize() for c in df.columns]
            df = df.dropna(subset=["Open", "High", "Low", "Close"])
            df["Date"] = df.index
            df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

            # Speichern als *_daily.csv
            file_path = os.path.join(CSV_PATH, f"{symbol}_daily.csv")
            df.to_csv(file_path, index=False)
            print(f"[{symbol}] ✅ Gespeichert: {file_path}")

        except Exception as e:
            print(f"[{symbol}] ❌ Fehler beim Abrufen: {e}")

def get_backtest_data(df, backtest_years, backtesting_begin, backtesting_end):
    """
    Beschränkt den DataFrame zuerst auf die letzten N Jahre/Monate,
    dann auf den gewünschten Prozentbereich.
    Gibt die verwendeten Zeitspannen per print() aus.
    """
    # Schritt 1: Nur die letzten N Jahre/Monate
    df_years = restrict_to_backtest_years(df, backtest_years)
    print(f"[Debug] Zeitraum nach backtest_years: {df_years.index.min().date()} bis {df_years.index.max().date()} (Zeilen: {len(df_years)})")

    # Schritt 2: Prozentualer Bereich
    df_bt = restrict_to_percent_slice(df_years, backtesting_begin, backtesting_end)
    print(f"[Debug] Zeitraum nach Prozent-Schnitt: {df_bt.index.min().date()} bis {df_bt.index.max().date()} (Zeilen: {len(df_bt)})")

    return df_bt

def restrict_to_backtest_years(df, backtest_years):    
    # Nimmt die letzten N Jahre oder Monate (backtest_years = [0, 2] für 2 Jahre)
    max_years = backtest_years[1] if isinstance(backtest_years, list) else backtest_years
    if max_years < 1:
        min_timestamp = df.index.max() - pd.DateOffset(months=int(max_years*12))
    else:
        min_timestamp = df.index.max() - pd.DateOffset(years=int(max_years))
    return df[df.index >= min_timestamp]

def restrict_to_percent_slice(df, begin, end):
    n = len(df)
    # Calculate start and end indices based on percentage
    start_idx = int(n * begin / 100)
    end_idx = int(n * end / 100)
    return df.iloc[start_idx:end_idx]

def capture_trades_output(matched_trades, open_trade_info=None):
    """
    Convert matched_trades list to the formatted string output that can be analyzed
    Also handles the last open trade if provided
    """
    trades_text = ""
    
    if not matched_trades and not open_trade_info:
        return trades_text
    
    # Process completed matched trades
    for i, trade in enumerate(matched_trades):
        # Extract trade data
        buy_date = trade.get('buy_date', 'N/A')
        sell_date = trade.get('sell_date', 'N/A')
        buy_price = trade.get('buy_price', 0)
        sell_price = trade.get('sell_price', 0)
        shares = trade.get('shares', 0)
        trade_value = trade.get('trade_value', 0)
        total_fees = trade.get('total_fees', 0)
        pnl = trade.get('pnl', 0)
        
        # Calculate capital (approximate running capital)
        if i == 0:
            capital = 10000.0  # Initial capital
        else:
            # Calculate running capital from previous trades
            previous_pnl = sum(t.get('pnl', 0) for t in matched_trades[:i])
            capital = 10000.0 + previous_pnl
        
        # Calculate raw shares (before rounding)
        raw_shares = capital / buy_price if buy_price > 0 else shares
        
        # Add BUY line
        trades_text += f"🔢 BUY: Date={buy_date}, Capital={capital:.2f}, Price={buy_price:.4f}, Raw={raw_shares:.6f}, Shares={shares:.6f}\n"
        
        # Add SELL line
        trades_text += f"💰 SELL: Date={sell_date}, Price={sell_price:.4f}, Value={trade_value:.3f}, Fees={total_fees:.3f}, PnL={pnl:.3f}\n"
    
    # Handle open trade (last BUY without matching SELL)
    if open_trade_info:
        buy_date = open_trade_info.get('buy_date', 'N/A')
        buy_price = open_trade_info.get('buy_price', 0)
        shares = open_trade_info.get('shares', 0)
        
        # Calculate capital after all completed trades
        total_pnl = sum(t.get('pnl', 0) for t in matched_trades)
        capital = 10000.0 + total_pnl
        
        # Calculate raw shares
        raw_shares = capital / buy_price if buy_price > 0 else shares
        
        # Add open BUY line
        trades_text += f"🔢 BUY: Date={buy_date}, Capital={capital:.2f}, Price={buy_price:.4f}, Raw={raw_shares:.6f}, Shares={shares:.6f}\n"
        trades_text += f"📊 OPEN POSITION: {shares:.6f} shares @ {buy_price:.4f} (Not yet closed)\n"
    
    return trades_text

def get_crypto_data_enhanced(symbol, backtest_years, update_today=True):
    """
    Enhanced crypto data loading with today's data included
    FIXED: Ensures today's candle is always included
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - pd.DateOffset(years=backtest_years)
        
        print(f"📅 Loading data for {symbol} from {start_date.date()} to {end_date.date()}")
        
        # Download with extended period to ensure today is included
        df = yf.download(
            symbol, 
            start=start_date.strftime('%Y-%m-%d'),
            end=(end_date + pd.DateOffset(days=1)).strftime('%Y-%m-%d'),  # +1 day to include today
            interval="1d", 
            auto_adjust=True, 
            progress=False
        )
        
        if df is None or df.empty:
            print(f"❌ No data received for {symbol}")
            return None
        
        # Fix MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ensure standard column names
        df.columns = [str(col).strip().capitalize() for col in df.columns]
        
        # Add today's partial candle if market is open and update_today=True
        if update_today:
            today = datetime.now().date()
            latest_date = df.index.max().date()
            
            if latest_date < today:
                print(f"📈 Latest data: {latest_date}, trying to add today: {today}")
                
                # Try to get today's data
                today_df = yf.download(
                    symbol,
                    start=today.strftime('%Y-%m-%d'),
                    interval="1d",
                    auto_adjust=True,
                    progress=False
                )
                
                if not today_df.empty:
                    if isinstance(today_df.columns, pd.MultiIndex):
                        today_df.columns = today_df.columns.get_level_values(0)
                    today_df.columns = [str(col).strip().capitalize() for col in today_df.columns]
                    
                    # Combine dataframes
                    df = pd.concat([df, today_df])
                    df = df[~df.index.duplicated(keep='last')]  # Remove duplicates
                    print(f"✅ Added today's data! New latest date: {df.index.max().date()}")
                else:
                    print(f"⚠️ No data available for today yet")
            else:
                print(f"✅ Data already includes today: {latest_date}")
        
        # Ensure required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing columns for {symbol}: {missing_cols}")
            return None
        
        print(f"✅ Loaded {len(df)} days of data for {symbol} (from {df.index.min().date()} to {df.index.max().date()})")
        return df
        
    except Exception as e:
        print(f"❌ Error loading data for {symbol}: {e}")
        return None
    """
    Enhanced crypto data loading with today's data included
    FIXED: Ensures today's candle is always included
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - pd.DateOffset(years=backtest_years)
        
        print(f"� Loading data for {symbol} from {start_date.date()} to {end_date.date()}")
        
        # Download with extended period to ensure today is included
        df = yf.download(
            symbol, 
            start=start_date.strftime('%Y-%m-%d'),
            end=(end_date + pd.DateOffset(days=1)).strftime('%Y-%m-%d'),  # +1 day to include today
            interval="1d", 
            auto_adjust=True, 
            progress=False
        )
        
        if df is None or df.empty:
            print(f"❌ No data received for {symbol}")
            return None
        
        # Fix MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ensure standard column names
        df.columns = [str(col).strip().capitalize() for col in df.columns]
        
        # Add today's partial candle if market is open and update_today=True
        if update_today:
            today = datetime.now().date()
            latest_date = df.index.max().date()
            
            if latest_date < today:
                print(f"� Latest data: {latest_date}, trying to add today: {today}")
                
                # Try to get today's data
                today_df = yf.download(
                    symbol,
                    start=today.strftime('%Y-%m-%d'),
                    interval="1d",
                    auto_adjust=True,
                    progress=False
                )
                
                if not today_df.empty:
                    if isinstance(today_df.columns, pd.MultiIndex):
                        today_df.columns = today_df.columns.get_level_values(0)
                    today_df.columns = [str(col).strip().capitalize() for col in today_df.columns]
                    
                    # Combine dataframes
                    df = pd.concat([df, today_df])
                    df = df[~df.index.duplicated(keep='last')]  # Remove duplicates
                    print(f"✅ Added today's data! New latest date: {df.index.max().date()}")
                else:
                    print(f"⚠️ No data available for today yet")
            else:
                print(f"✅ Data already includes today: {latest_date}")
        
        # Ensure required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing columns for {symbol}: {missing_cols}")
            return None
        
        print(f"✅ Loaded {len(df)} days of data for {symbol} (from {df.index.min().date()} to {df.index.max().date()})")
        return df
        
    except Exception as e:
        print(f"❌ Error loading data for {symbol}: {e}")
        return None

def display_matched_trades_table_enhanced():
    raise NotImplementedError

def run_backtest(symbol, config):
    """
    Führt einen vollständigen Backtest für ein Symbol durch
    """
    try:
        # Konfiguration extrahieren
        initial_capital = config.get('initial_capital', 10000)
        trade_on = config.get('trade_on', 'close').lower()
        order_round_factor = config.get('order_round_factor', 0.01)
        commission_rate = config.get('commission_rate', 0.0018)
        
        print(f"\n=== Backtest für {symbol} ===")
        print(f"💰 Initial Capital: {initial_capital}")
        print(f"📊 Trade on: {trade_on.title()} price")
        print(f"🔧 Order Round Factor: {order_round_factor}")
        print(f"💸 Commission Rate: {commission_rate*100}%")
        
        # Daten laden - 1 Jahr
        df = load_crypto_data_yf(symbol, 1)
        if df is None or df.empty:
            print(f"❌ Keine Daten für {symbol}")
            return False
        
        print(f"📊 Dataset: {len(df)} Zeilen ({df.index[0].date()} bis {df.index[-1].date()})")
        
        # 1. HEAD UND TAIL DER DAILY DATA
        print(f"\n📊 1. DAILY DATA - HEAD (5 Zeilen) - {symbol}")
        print("="*80)
        print(df.head().to_string())
        print(f"\n📊 1. DAILY DATA - TAIL (5 Zeilen) - {symbol}")
        print("="*80)
        print(df.tail().to_string())
        
        # Support/Resistance berechnen mit Backtesting für optimale Parameter
        print(f"\n📊 Optimiere Parameter für {symbol}...")
        optimal_results = optimize_parameters(df, symbol)  # ✅ df ist hier definiert
        
        optimal_past_window = optimal_results.get('optimal_past_window', 0)
        optimal_trade_window = optimal_results.get('optimal_trade_window', 2)
        
        supp_full, res_full = calculate_support_resistance(df, optimal_past_window, optimal_trade_window, verbose=False, ticker=symbol)
        
        # 2. BACKTEST RESULTS MIT OPTIMALEN PARAMETERN
        print(f"\n📊 2. BACKTEST RESULTS - {symbol}")
        print("="*80)
        print(f"   📈 Optimal Past Window: {optimal_past_window}")
        print(f"   📈 Optimal Trade Window: {optimal_trade_window}")
        print(f"   📊 Support Levels Found: {len(supp_full)}")
        print(f"   📊 Resistance Levels Found: {len(res_full)}")
        print(f"   📅 Analysis Period: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"   📊 Total Trading Days: {len(df)}")
        
        # Extended Signals generieren
        print(f"\n📊 Generiere Extended Signals für {symbol}...")
        ext_full = assign_long_signals_extended(supp_full, res_full, df, optimal_trade_window, "1d")
        
        if ext_full is None or ext_full.empty:
            print(f"❌ Keine Extended Signals für {symbol}")
            return False
        
        # 3. EXTENDED TRADES - KOMPLETTE TABELLE
        print(f"\n📊 3. EXTENDED TRADES - KOMPLETTE TABELLE ({len(ext_full)} Trades) - {symbol}")
        print("="*120)
        if not ext_full.empty:
            display_df = ext_full.copy()
            if 'Level high/low' in display_df.columns:
                display_df['Level high/low'] = display_df['Level high/low'].round(2)
            if 'Level Close' in display_df.columns:
                display_df['Level Close'] = display_df['Level Close'].round(2)
            print(display_df.to_string(index=True, max_rows=None))
        else:
            print("❌ Keine Extended Trades vorhanden")
        
        # 4. MATCHED TRADES - SIMULATION (mit offenen Trades)
        print(f"\n📊 4. MATCHED TRADES - SIMULATION - {symbol}")
        print("="*120)
        matched_trades = simulate_matched_trades(ext_full, initial_capital, commission_rate, df)
        if not matched_trades.empty:
            print(matched_trades.to_string(index=True, max_rows=None))
        else:
            print("❌ Keine Matched Trades generiert")
        
        # 5. TRADE STATISTICS
        print(f"\n📊 5. TRADE STATISTICS - {symbol}")
        print("="*80)
        trade_stats = calculate_trade_statistics(ext_full, matched_trades, initial_capital)
        for key, value in trade_stats.items():
            print(f"   {key}: {value}")
        
        # Tabelle anzeigen
        display_extended_trades_table(ext_full, symbol)
        
        # Result erstellen BEVOR Weekly Trades
        result = {
            'success': True,
            'symbol': symbol,
            'config': config,
            'df_bt': df,
            'dataset_info': {
                'total_days': len(df),
                'start_date': df.index[0].date(),
                'end_date': df.index[-1].date()
            },
            'signals': {
                'total': len(ext_full) if ext_full is not None else 0,
                'long_signals': len(ext_full[ext_full['Long Signal Extended'] == True]) if ext_full is not None and 'Long Signal Extended' in ext_full.columns else 0,
            },
            'ext_signals': ext_full,
            'matched_trades': matched_trades,
            'trade_statistics': trade_stats,
            'support_levels': len(supp_full),
            'resistance_levels': len(res_full)
        }
        
                # ✅ EXTENDED TRADES LISTE DER LETZTEN 2 WOCHEN
        print(f"\n📅 TRADES DER LETZTEN 2 WOCHEN - {symbol}")
        print("="*80)
        if ext_full is not None and not ext_full.empty:
            print(f"🔍 DEBUG: Extended Trades Spalten: {list(ext_full.columns)}")
            print(f"🔍 DEBUG: Anzahl Extended Trades: {len(ext_full)}")
            print(f"🔍 DEBUG: Letzte 5 Extended Trades Daten:")
            print(ext_full.tail(5)[['Action', 'Long Signal Extended']].to_string())
            print(f"🔍 DEBUG: Index der letzten 5 Trades:")
            print(list(ext_full.tail(5).index))
            print(f"🔍 DEBUG: Original DataFrame index type: {type(df.index[0])}")
            print(f"🔍 DEBUG: Latest dates from original df:")
            print(df.tail(5).index.tolist())
            
            # Da ext_full numerische Indices hat, verwende ich die letzten X Trades
            # anstatt Datum-Filter
            last_14_days_count = min(14, len(ext_full))  # Nimm die letzten 14 Trades oder weniger
            recent_ext_trades = ext_full.tail(last_14_days_count).copy()
            
            if not recent_ext_trades.empty:
                print(f"📈 {len(recent_ext_trades)} Extended Trades in den letzten 2 Wochen:")
                print("-" * 80)
                
                for idx, (row_idx, trade) in enumerate(recent_ext_trades.iterrows()):
                    # Verwende den row_idx um das entsprechende Datum aus df zu holen
                    try:
                        trade_date = df.index[row_idx].strftime('%Y-%m-%d')
                    except (IndexError, KeyError):
                        trade_date = f"Row-{row_idx}"
                    
                    # Extended trades structure
                    action = trade.get('Long Action', 'N/A')
                    if action == 'N/A':
                        action = trade.get('Action', 'N/A')
                    
                    # Filter nur echte Trades (BUY/SELL), keine None
                    if action in [None, 'None', 'N/A', '', 'none']:
                        continue  # Überspringe None-Trades
                    
                    price = trade.get('Close', 0)
                    
                    today = datetime.now().date()
                    try:
                        current_trade_date = df.index[row_idx].date()
                    except (IndexError, KeyError):
                        current_trade_date = datetime(2024, 1, 1).date()  # Default old date
                    
                    if current_trade_date == today:
                        type_desc = "Artificial"
                    else:
                        type_desc = "Limit"
                    
                    if action in ['BUY', 'Buy', 'buy']:
                        action_emoji = "🔓 BUY"
                    elif action in ['SELL', 'Sell', 'sell']:
                        action_emoji = "🔒 SELL"
                    else:
                        action_emoji = f"📊 {action}"
                    
                    print(f"  {idx+1}. {symbol} | {action_emoji} | {trade_date} | Type: {type_desc} | Price: {price:.4f}")
                    
                # Für HTML Report - richtige Tabelle erstellen
                html_content = f"""
                <h3>📅 Extended Trades der letzten 2 Wochen ({len(recent_ext_trades)} Trades)</h3>
                <table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">
                    <thead style="background-color: #f2f2f2;">
                        <tr>
                            <th>Nr.</th>
                            <th>Symbol</th>
                            <th>Action</th>
                            <th>Trade Date</th>
                            <th>Type</th>
                            <th>Price</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                for idx, (date_idx, trade) in enumerate(recent_ext_trades.iterrows()):
                    # Convert date index to proper datetime
                    date_obj = pd.to_datetime(trade['Date']) if 'Date' in trade else pd.to_datetime(date_idx)
                    trade_date = date_obj.strftime('%Y-%m-%d')
                    action = trade.get('Action', 'N/A')
                    price = trade.get('Close', 0)
                    
                    today = datetime.now().date()
                    current_trade_date = date_obj.date()
                    type_desc = "Artificial" if current_trade_date == today else "Limit"
                    
                    if action in ['BUY', 'Buy']:
                        action_display = "🔓 BUY"
                    elif action in ['SELL', 'Sell']:
                        action_display = "🔒 SELL"
                    else:
                        action_display = f"📊 {action}"
                    
                    html_content += f"""
                        <tr>
                            <td>{idx+1}</td>
                            <td>{symbol}</td>
                            <td>{action_display}</td>
                            <td>{trade_date}</td>
                            <td>{type_desc}</td>
                            <td>{price:.4f}</td>
                        </tr>
                    """
                
                html_content += """
                    </tbody>
                </table>
                """
                
                result['weekly_trades_html'] = html_content
                result['weekly_trades_count'] = len(recent_ext_trades)
            else:
                print("📈 Keine Extended Trades in den letzten 2 Wochen")
                result['weekly_trades_html'] = "<h3>Keine Extended Trades in den letzten 2 Wochen</h3>"
                result['weekly_trades_count'] = 0
        else:
            print("⚠️ Keine Extended Trades verfügbar")
            result['weekly_trades_html'] = ""
            result['weekly_trades_count'] = 0

        return result
        
    except Exception as e:
        print(f"❌ Fehler für {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return False

def optimize_parameters(df, symbol):
    """
    Verwendet die existierende berechne_best_p_tw_long Funktion
    """
    try:
        print(f"🔍 Optimiere Parameter für {symbol}...")
        
        # Standard Config für Optimierung
        cfg = {
            'initial_capital': 10000,
            'commission_rate': 0.0018,
            'min_commission': 1.0,
            'order_round_factor': 0.01
        }
        
        # Verwende kompletten Dataset für Optimierung
        start_idx = 0
        end_idx = len(df)
        
        # Nutze deine existierende Optimierungsfunktion
        p, tw = berechne_best_p_tw_long(  # ✅ p, tw statt optimal_past_window, optimal_trade_window
            df, cfg, start_idx, end_idx, verbose=True, ticker=symbol
        )
        
        print(f"✅ Optimal: Past={p}, Trade={tw}")
        
        return {
            'optimal_past_window': p,      # ✅ p -> optimal_past_window
            'optimal_trade_window': tw,    # ✅ tw -> optimal_trade_window
            'method': 'berechne_best_p_tw_long'
        }
        
    except Exception as e:
        print(f"❌ Parameter-Optimierung fehlgeschlagen: {e}")
        # Fallback mit gültigen Werten (nicht 0!)
        return {
            'optimal_past_window': 5,
            'optimal_trade_window': 2,
            'method': 'fallback'
        }

def simulate_matched_trades(ext_full, initial_capital, commission_rate, data_df=None):
    """
    Simuliert Matched Trades basierend auf Extended Signals
    Inkludiert offene Trades mit heutigem artificial price
    """
    try:
        if ext_full is None or ext_full.empty:
            return pd.DataFrame()
        
        matched = []
        position = None
        capital = initial_capital
        today = pd.Timestamp.now().date()
        
        for idx, row in ext_full.iterrows():
            if row['Action'] == 'buy' and position is None:
                # Öffne Long Position
                position = {
                    'entry_date': row['Long Date detected'],
                    'entry_price': row['Level Close'],
                    'entry_idx': idx
                }
            elif row['Action'] == 'sell' and position is not None:
                # Schließe Position
                entry_price = position['entry_price']
                exit_price = row['Level Close']
                quantity = capital / entry_price
                
                pnl = (exit_price - entry_price) * quantity
                commission = (entry_price + exit_price) * quantity * commission_rate
                net_pnl = pnl - commission
                capital += net_pnl
                
                matched.append({
                    'Entry Date': position['entry_date'],
                    'Entry Price': round(entry_price, 2),
                    'Exit Date': row['Long Date detected'],
                    'Exit Price': round(exit_price, 2),
                    'Quantity': round(quantity, 4),
                    'PnL': round(pnl, 2),
                    'Commission': round(commission, 2),
                    'Net PnL': round(net_pnl, 2),
                    'Capital': round(capital, 2),
                    'Status': 'CLOSED'
                })
                position = None
        
        # ✅ OFFENE POSITION MIT HEUTIGEM ARTIFICIAL PRICE HINZUFÜGEN
        if position is not None and data_df is not None:
            entry_price = position['entry_price']
            quantity = capital / entry_price
            
            # Heutigen artificial price finden
            today_timestamp = pd.Timestamp(today)
            artificial_price = entry_price  # Fallback
            
            if today_timestamp in data_df.index:
                artificial_price = data_df.loc[today_timestamp, 'Close']
                print(f"🤖 Offene Position: Heute's artificial price = €{artificial_price:.4f}")
            else:
                # Letzter verfügbarer Preis
                artificial_price = data_df['Close'].iloc[-1]
                print(f"🤖 Offene Position: Letzter verfügbarer Preis = €{artificial_price:.4f}")
            
            # Unrealized PnL berechnen
            unrealized_pnl = (artificial_price - entry_price) * quantity
            
            matched.append({
                'Entry Date': position['entry_date'],
                'Entry Price': round(entry_price, 2),
                'Exit Date': today.strftime('%Y-%m-%d'),
                'Exit Price': round(artificial_price, 2),
                'Quantity': round(quantity, 4),
                'PnL': round(unrealized_pnl, 2),
                'Commission': round(entry_price * quantity * commission_rate, 2),
                'Net PnL': round(unrealized_pnl - (entry_price * quantity * commission_rate), 2),
                'Capital': round(capital + unrealized_pnl, 2),
                'Status': 'OPEN',
                'Type': 'Artificial'
            })
            print(f"🔓 Offener Trade hinzugefügt: Entry={entry_price:.2f}, Current={artificial_price:.2f}, PnL={unrealized_pnl:.2f}")
        
        return pd.DataFrame(matched)
        
    except Exception as e:
        print(f"❌ Fehler in simulate_matched_trades: {e}")
        return pd.DataFrame()

def calculate_trade_statistics(ext_full, matched_trades, initial_capital):
    """
    Berechnet umfassende Trade-Statistiken
    """
    try:
        stats = {}
        
        # Extended Signals Stats
        if ext_full is not None and not ext_full.empty:
            buy_signals = len(ext_full[ext_full['Action'] == 'buy'])
            sell_signals = len(ext_full[ext_full['Action'] == 'sell'])
            stats['📊 Total Extended Signals'] = len(ext_full)
            stats['📈 Buy Signals'] = buy_signals
            stats['📉 Sell Signals'] = sell_signals
        else:
            stats['📊 Total Extended Signals'] = 0
            stats['📈 Buy Signals'] = 0
            stats['📉 Sell Signals'] = 0
        
        # Matched Trades Stats
        if matched_trades is not None and not matched_trades.empty:
            total_trades = len(matched_trades)
            winning_trades = len(matched_trades[matched_trades['Net PnL'] > 0])
            losing_trades = len(matched_trades[matched_trades['Net PnL'] < 0])
            
            stats['🔄 Total Completed Trades'] = total_trades
            stats['✅ Winning Trades'] = winning_trades
            stats['❌ Losing Trades'] = losing_trades
            stats['📊 Win Rate'] = f"{(winning_trades/total_trades*100):.1f}%" if total_trades > 0 else "0%"
            
            if total_trades > 0:
                total_pnl = matched_trades['Net PnL'].sum()
                avg_win = matched_trades[matched_trades['Net PnL'] > 0]['Net PnL'].mean() if winning_trades > 0 else 0
                avg_loss = matched_trades[matched_trades['Net PnL'] < 0]['Net PnL'].mean() if losing_trades > 0 else 0
                final_capital = matched_trades['Capital'].iloc[-1] if len(matched_trades) > 0 else initial_capital
                
                stats['💰 Total PnL'] = f"€{total_pnl:.2f}"
                stats['📈 Average Win'] = f"€{avg_win:.2f}"
                stats['📉 Average Loss'] = f"€{avg_loss:.2f}"
                stats['💼 Final Capital'] = f"€{final_capital:.2f}"
                stats['📊 Total Return'] = f"{((final_capital/initial_capital-1)*100):.2f}%"
        else:
            stats['🔄 Total Completed Trades'] = 0
            stats['✅ Winning Trades'] = 0
            stats['❌ Losing Trades'] = 0
            stats['📊 Win Rate'] = "0%"
            stats['💰 Total PnL'] = "€0.00"
            stats['💼 Final Capital'] = f"€{initial_capital:.2f}"
            stats['📊 Total Return'] = "0.00%"
        
        return stats
        
    except Exception as e:
        print(f"❌ Fehler in calculate_trade_statistics: {e}")
        return {'Error': str(e)}

# REMOVE DUPLICATE FUNCTIONS BELOW THIS POINT
# The corrected functions are already defined above

# ✅ FIX 3: Main-Block korrigieren
if __name__ == "__main__":
    print("🚀 Starting Crypto Backtesting with Enhanced Analysis...")
    
    # Configuration anzeigen
    print(f"📊 Configuration:")
    print(f"   Backtest Period: {backtest_years} Jahr(e)")
    print(f"   Commission Rate: {COMMISSION_RATE*100}%")
    
    # Crypto Tickers anzeigen
    print(f"\n💰 CRYPTO TICKERS CONFIGURED ({len(crypto_tickers)}):")
    for symbol, config in crypto_tickers.items():
        # ✅ Sichere Anzeige der Config
        initial_cap = config.get('initial_capital', 'N/A')
        trade_on = config.get('trade_on', 'N/A')
        commission = config.get('commission_rate', COMMISSION_RATE)
        print(f"   {symbol}: Capital={initial_cap}, Trade on={trade_on.upper()}, Commission={commission*100}%")
    
    print(f"\n🔄 Starting main backtest analysis...")
    
    # ✅ Korrekte Unpacking-Syntax
    try:
        backtest_results, trading_analysis = main_backtest_with_analysis()
        success = backtest_results is not False
    except Exception as e:
        print(f"❌ Error during backtest execution: {e}")
        success = False
        backtest_results = False
        trading_analysis = {}
    
    if success:
        print("\n" + "="*80)
        print("🎯 BACKTEST SESSION COMPLETED")
        print("="*80)
        print(f"   📅 Session Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📊 Configuration: {backtest_years} years")
        print("="*80)
        print("🚀 Thank you for using Crypto Backtesting Suite!")
        print("="*80)
    else:
        print("\n❌ BACKTEST SESSION FAILED")
        print("💡 Check the error messages above for details")

