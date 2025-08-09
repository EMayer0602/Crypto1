# signal_utils.py

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from config import COMMISSION_RATE, MIN_COMMISSION, ORDER_ROUND_FACTOR, backtesting_begin, backtesting_end, backtest_years
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import traceback
from datetime import date, timedelta
def remove_all_headers_and_set_columns(df, new_columns=None):
    """
    Entfernt alle Header und setzt neue Spalten
    """
    try:
        # Prüfe aktuelle Spaltenanzahl
        current_cols = len(df.columns)
        
        if new_columns is None:
            new_columns = ["Open", "High", "Low", "Close", "Volume"]
        
        # Passe neue Spalten an aktuelle Anzahl an
        if current_cols > len(new_columns):
            # Füge zusätzliche Spalten hinzu
            extra_cols = [f"Extra_{i}" for i in range(len(new_columns), current_cols)]
            new_columns.extend(extra_cols)
        elif current_cols < len(new_columns):
            # Kürze neue Spalten
            new_columns = new_columns[:current_cols]
        
        df.columns = new_columns
        return df
        
    except Exception as e:
        print(f"❌ Fehler beim Setzen der Spalten: {e}")
        return df

def calculate_support_resistance(df, p, tw, verbose=False, ticker=None):
    """
    Calculates support and resistance levels using local extrema.
    Only calculates levels at actual peaks and valleys, not every day.
    
    Parameters:
    - df: DataFrame with OHLCV data
    - p: optimized past_window parameter
    - tw: optimized trade window parameter
    - verbose: print debug info
    - ticker: ticker symbol for debug output
    """
    df = df.copy()
    #df = remove_all_headers_and_set_columns(df, new_columns=["Open", "High", "Low", "Close", "Volume"])
    
    if "Close" not in df.columns:
        raise KeyError(f"'Close' column missing! Available columns: {list(df.columns)}")

    total_window = int(p + tw)  # Both optimized parameters
    prices = df["Close"].values

    # Find local minima (support levels)
    local_min_idx = argrelextrema(prices, np.less, order=total_window)[0]
    support = pd.Series(prices[local_min_idx], index=df.index[local_min_idx])

    # Find local maxima (resistance levels)
    local_max_idx = argrelextrema(prices, np.greater, order=total_window)[0]
    resistance = pd.Series(prices[local_max_idx], index=df.index[local_max_idx])

    # Add global extrema if not already included
    absolute_low_date = df["Close"].idxmin()
    absolute_low = df["Close"].min()
    if absolute_low_date not in support.index:
        support = pd.concat([support, pd.Series([absolute_low], index=[absolute_low_date])])

    absolute_high_date = df["Close"].idxmax()
    absolute_high = df["Close"].max()
    if absolute_high_date not in resistance.index:
        resistance = pd.concat([resistance, pd.Series([absolute_high], index=[absolute_high_date])])

    support.sort_index(inplace=True)
    resistance.sort_index(inplace=True)

    if verbose:
        print(f"[{ticker}] Support levels found: {len(support)} (dates: {support.index.date.tolist()[:5]}...)")
        print(f"[{ticker}] Resistance levels found: {len(resistance)} (dates: {resistance.index.date.tolist()[:5]}...)")

    return support, resistance

def compute_trend(df, window=20):
    return df["Close"].rolling(window=window).mean()

def assign_long_signals(support, resistance, data, tw, interval="1d"):
    """
    ✅ NEUE UNIFIED FUNKTION - Ersetzt beide alte Funktionen
    Generiert VOLLSTÄNDIGE Signale in einem Schritt
    """
    try:
        print(f"📊 Generiere vollständige Long-Signale...")
        print(f"   Support: {type(support)} mit {len(support)} Levels")
        print(f"   Resistance: {type(resistance)} mit {len(resistance)} Levels")
        
        signals = []
        
        # ✅ SUPPORT PROCESSING:
        support_items = support.items() if isinstance(support, pd.Series) else support.iterrows()
        
        for date_idx, level in support_items:
            try:
                # Level Value extrahieren
                level_value = level.iloc[0] if hasattr(level, 'iloc') else float(level)
                
                # Trade Day berechnen
                trade_day = get_trade_day_offset(date_idx, tw, data)
                
                if pd.notna(trade_day) and trade_day in data.index:
                    close_price = data.at[trade_day, 'Close']
                    # Support = Buy wenn Preis über Support
                    action = "buy" if close_price > level_value else "None"
                else:
                    close_price = 0.0
                    action = "None"
                    trade_day = pd.NaT
                
                signals.append({
                    'Date high/low': date_idx,
                    'Level high/low': level_value,
                    'Supp/Resist': 'Support',
                    'Action': action,
                    'Long Date detected': trade_day,
                    'Long Trade Day': trade_day,
                    'Level Close': close_price,
                    'Level trade': close_price,
                    'signal_long': 1 if action == "buy" else 0
                })
                
            except Exception as e:
                print(f"⚠️ Support-Fehler für {date_idx}: {e}")
                continue
        
        # ✅ RESISTANCE PROCESSING:
        resistance_items = resistance.items() if isinstance(resistance, pd.Series) else resistance.iterrows()
        
        for date_idx, level in resistance_items:
            try:
                # Level Value extrahieren
                level_value = level.iloc[0] if hasattr(level, 'iloc') else float(level)
                
                # Trade Day berechnen
                trade_day = get_trade_day_offset(date_idx, tw, data)
                
                if pd.notna(trade_day) and trade_day in data.index:
                    close_price = data.at[trade_day, 'Close']
                    # Resistance = Sell wenn Preis unter Resistance
                    action = "sell" if close_price < level_value else "None"
                else:
                    close_price = 0.0
                    action = "None"
                    trade_day = pd.NaT
                
                signals.append({
                    'Date high/low': date_idx,
                    'Level high/low': level_value,
                    'Supp/Resist': 'Resistance',
                    'Action': action,
                    'Long Date detected': trade_day,
                    'Long Trade Day': trade_day,
                    'Level Close': close_price,
                    'Level trade': close_price,
                    'signal_long': -1 if action == "sell" else 0
                })
                
            except Exception as e:
                print(f"⚠️ Resistance-Fehler für {date_idx}: {e}")
                continue
        
        # DataFrame erstellen
        result_df = pd.DataFrame(signals)
        
        if len(result_df) > 0:
            result_df = result_df.sort_values('Date high/low').reset_index(drop=True)
            
            # Statistics
            buy_count = len(result_df[result_df['Action'] == 'buy'])
            sell_count = len(result_df[result_df['Action'] == 'sell'])
            none_count = len(result_df[result_df['Action'] == 'None'])
            
            print(f"✅ VOLLSTÄNDIGE Signale generiert:")
            print(f"   📊 Total: {len(result_df)}")
            print(f"   📈 Buy: {buy_count}")
            print(f"   📉 Sell: {sell_count}")
            print(f"   ⭕ None: {none_count}")
            
        return result_df
        
    except Exception as e:
        print(f"❌ FEHLER in assign_long_signals: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return pd.DataFrame()

def assign_long_signals_base(support, resistance, data, tw):
    """
    ✅ KORRIGIERTE assign_long_signals_base für Series UND DataFrame Input
    """
    try:
        signals = []
        
        # ✅ SUPPORT PROCESSING - Handle Series AND DataFrame:
        if isinstance(support, pd.Series):
            print("🔄 Support ist Series - konvertiere zu DataFrame-ähnlicher Iteration")
            support_items = [(idx, val) for idx, val in support.items()]
        elif isinstance(support, pd.DataFrame):
            print("🔄 Support ist DataFrame - verwende iterrows()")
            support_items = [(idx, row.iloc[0] if len(row) > 0 else row) for idx, row in support.iterrows()]
        else:
            print(f"⚠️ Unbekannter Support-Typ: {type(support)}")
            support_items = []
        
        # Support-Signale verarbeiten
        for date_idx, level in support_items:
            try:
                # Finde nächsten verfügbaren Trade-Tag
                trade_day = get_trade_day_offset(date_idx, tw, data)
                
                if pd.notna(trade_day) and trade_day in data.index:
                    # Support = Buy Signal (wenn Preis über Support Level)
                    current_price = data.at[trade_day, 'Close']
                    
                    if isinstance(level, (pd.Series, pd.DataFrame)):
                        level = level.iloc[0] if hasattr(level, 'iloc') else float(level)
                    
                    signal = "buy" if current_price > float(level) else "None"
                else:
                    signal = "None"
                
                signals.append({
                    'Date': date_idx,
                    'Level': float(level) if pd.notna(level) else 0.0,
                    'Type': 'Support',
                    'Long': signal
                })
                
            except Exception as e:
                print(f"⚠️ Fehler bei Support-Signal für {date_idx}: {e}")
                signals.append({
                    'Date': date_idx,
                    'Level': 0.0,
                    'Type': 'Support', 
                    'Long': 'None'
                })
        
        # ✅ RESISTANCE PROCESSING - Handle Series AND DataFrame:
        if isinstance(resistance, pd.Series):
            print("🔄 Resistance ist Series - konvertiere zu DataFrame-ähnlicher Iteration")
            resistance_items = [(idx, val) for idx, val in resistance.items()]
        elif isinstance(resistance, pd.DataFrame):
            print("🔄 Resistance ist DataFrame - verwende iterrows()")
            resistance_items = [(idx, row.iloc[0] if len(row) > 0 else row) for idx, row in resistance.iterrows()]
        else:
            print(f"⚠️ Unbekannter Resistance-Typ: {type(resistance)}")
            resistance_items = []
        
        # Resistance-Signale verarbeiten
        for date_idx, level in resistance_items:
            try:
                # Finde nächsten verfügbaren Trade-Tag
                trade_day = get_trade_day_offset(date_idx, tw, data)
                
                if pd.notna(trade_day) and trade_day in data.index:
                    # Resistance = Sell Signal (wenn Preis unter Resistance Level)
                    current_price = data.at[trade_day, 'Close']
                    
                    if isinstance(level, (pd.Series, pd.DataFrame)):
                        level = level.iloc[0] if hasattr(level, 'iloc') else float(level)
                    
                    signal = "sell" if current_price < float(level) else "None"
                else:
                    signal = "None"
                
                signals.append({
                    'Date': date_idx,
                    'Level': float(level) if pd.notna(level) else 0.0,
                    'Type': 'Resistance',
                    'Long': signal
                })
                
            except Exception as e:
                print(f"⚠️ Fehler bei Resistance-Signal für {date_idx}: {e}")
                signals.append({
                    'Date': date_idx,
                    'Level': 0.0,
                    'Type': 'Resistance',
                    'Long': 'None'
                })
        
        # DataFrame erstellen und sortieren
        result_df = pd.DataFrame(signals)
        
        if len(result_df) > 0:
            result_df = result_df.sort_values('Date').reset_index(drop=True)
            print(f"✅ Base Signals generiert: {len(result_df)} total")
            print(f"   📈 Buy: {len(result_df[result_df['Long'] == 'buy'])}")
            print(f"   📉 Sell: {len(result_df[result_df['Long'] == 'sell'])}")
            print(f"   ⭕ None: {len(result_df[result_df['Long'] == 'None'])}")
        else:
            print("⚠️ Keine Base Signals generiert!")
            
        return result_df
        print(result_df.head(3))  # Debug-Ausgabe
    except Exception as e:
        print(f"❌ KRITISCHER FEHLER in assign_long_signals_base: {e}")
        print(f"❌ Support-Typ: {type(support)}")
        print(f"❌ Resistance-Typ: {type(resistance)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return pd.DataFrame(columns=['Date', 'Level', 'Type', 'Long'])
    """
    FINALE LOGIK: Support=BUY, Resistance=SELL mit Consecutiveness-Filter
    """
    # Kombiniere Support und Resistance
    all_levels = []
    
    # Support Levels hinzufügen
    for date_idx, level in support.iterrows():
        all_levels.append({
            'Date': date_idx,
            'Level': level.iloc[0] if hasattr(level, 'iloc') else level,
            'Type': 'Support'
        })
    
    # Resistance Levels hinzufügen  
    for date_idx, level in resistance.iterrows():
        all_levels.append({
            'Date': date_idx,
            'Level': level.iloc[0] if hasattr(level, 'iloc') else level,
            'Type': 'Resistance'
        })
    
    # Nach Datum sortieren
    df = pd.DataFrame(all_levels)
    df = df.sort_values('Date').reset_index(drop=True)
    
    # **SIGNAL-LOGIK ANWENDEN:**
    signals = []
    prev_type = None
    
    for i, row in df.iterrows():
        current_type = row['Type']
        
        if current_type == 'Support':
            if prev_type != 'Support':  # Erster Support in Serie
                signals.append('buy')
            else:  # Aufeinanderfolgender Support
                signals.append('None')
                
        elif current_type == 'Resistance':
            if prev_type != 'Resistance':  # Erste Resistance in Serie
                signals.append('sell')
            else:  # Aufeinanderfolgende Resistance
                signals.append('None')
        
        prev_type = current_type
    
    df['Long'] = signals
    
    # Statistik
    buy_count = signals.count('buy')
    sell_count = signals.count('sell') 
    none_count = signals.count('None')
    
    print(f"🔍 Signal-Statistik: {buy_count} BUY, {sell_count} SELL, {none_count} None")
    print(df.head(3))  # Debug-Ausgabe
    return df

def get_trade_day_offset(date_hl, tw, data):
    """
    ✅ KORRIGIERTE get_trade_day_offset Funktion
    """
    try:
        if pd.isna(date_hl):
            return pd.NaT
            
        # Datum normalisieren
        if isinstance(date_hl, str):
            date_hl = pd.to_datetime(date_hl).date()
        elif isinstance(date_hl, pd.Timestamp):
            date_hl = date_hl.date()
        elif not isinstance(date_hl, date):
            date_hl = pd.to_datetime(str(date_hl)).date()
        
        # Target Datum = Level Datum + Trade Window
        target_date = date_hl + timedelta(days=tw)
        
        # Verfügbare Daten als Dates
        data_dates = [d.date() if hasattr(d, 'date') else pd.to_datetime(d).date() for d in data.index]
        
        # Nächsten verfügbaren Handelstag finden
        for i, d in enumerate(data_dates):
            if d >= target_date:
                return data.index[i]
        
        # Falls nichts gefunden, letztes Datum zurückgeben
        return data.index[-1] if len(data.index) > 0 else pd.NaT
        
    except Exception as e:
        print(f"⚠️ Fehler in get_trade_day_offset für {date_hl}: {e}")
        return pd.NaT
    """
    Helper function to get the trade date offset from base date
    """
    future_dates = df.index[df.index > base_date]
    if len(future_dates) < tw:
        return pd.NaT
    return future_dates[tw - 1]

def assign_long_signals_extended(supp_full, res_full, df, tw, timeframe, trade_on="Close"):
    """
    CONSECUTIVE LOGIC: Nur erste Support/Resistance in Serie = Action
    """
    try:
        signals = []
        
        # Kombiniere und sortiere alle Levels chronologisch
        all_levels = []
        
        # Support Levels
        for date, level in supp_full.items():
            all_levels.append({
                'date': date,
                'level': level,
                'type': 'support',
                'base_action': 'buy'
            })
        
        # Resistance Levels
        for date, level in res_full.items():
            all_levels.append({
                'date': date,
                'level': level,
                'type': 'resistance',
                'base_action': 'sell'
            })
        
        # WICHTIG: Chronologisch sortieren
        all_levels.sort(key=lambda x: x['date'])
        
        # CONSECUTIVE LOGIC: Nur erste Support/Resistance in Serie = Action
        last_type = None
        
        for level_info in all_levels:
            current_type = level_info['type']
            
            # NUR der erste in einer Serie bekommt Action
            if current_type != last_type:
                # Typ-Wechsel oder allererster -> Action
                action = level_info['base_action']
                long_signal = (action == 'buy')
            else:
                # Consecutive (gleicher Typ wie vorher) -> None
                action = 'None'
                long_signal = False
            
            # Update für nächste Iteration
            last_type = current_type
            
            # ✅ HANDELSDATUM MIT TW BERECHNEN
            trade_day = get_trade_day_offset(level_info['date'], tw, df)
            
            # Price based on trade_on setting
            price_column = "Open" if trade_on.upper() == "OPEN" else "Close"
            if trade_day in df.index:
                close_price = df.loc[trade_day, price_column]
            elif level_info['date'] in df.index:
                close_price = df.loc[level_info['date'], price_column]
            else:
                continue
            
            signals.append({
                'Date high/low': level_info['date'].strftime('%Y-%m-%d'),
                'Level high/low': level_info['level'],
                'Supp/Resist': current_type,
                'Action': action,  # buy/sell/None
                'Long Signal Extended': long_signal,
                'Long Date detected': trade_day.strftime('%Y-%m-%d'),
                'Level Close': close_price,
                'Long Trade Day': trade_day,
                'Level trade': None
            })
        
        # DataFrame erstellen
        ext_df = pd.DataFrame(signals)
        
        if not ext_df.empty:
            ext_df = ext_df.sort_values('Long Trade Day').reset_index(drop=True)
            
            # Statistiken für Debug (nur wenn DataFrame nicht leer)
            buy_count = len(ext_df[ext_df['Action'] == 'buy'])
            sell_count = len(ext_df[ext_df['Action'] == 'sell'])
            none_count = len(ext_df[ext_df['Action'] == 'None'])
            
            print(f"✅ CONSECUTIVE LOGIC Applied:")
            print(f"   📊 Total Signals: {len(ext_df)}")
            print(f"   📈 Buy Actions: {buy_count}")
            print(f"   📉 Sell Actions: {sell_count}")
            print(f"   ⏸️  None Actions: {none_count}")
        else:
            print(f"⚠️  No signals generated")
        
        return ext_df
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def get_trade_day_offset(date_hl, tw, data):
    """
    ✅ VERBESSERTE get_trade_day_offset Funktion
    """
    try:
        if pd.isna(date_hl):
            return pd.NaT
            
        # Stelle sicher dass date_hl ein datetime ist
        if isinstance(date_hl, str):
            date_hl = pd.to_datetime(date_hl).date()
        elif isinstance(date_hl, pd.Timestamp):
            date_hl = date_hl.date()
        elif not isinstance(date_hl, date):
            date_hl = pd.to_datetime(str(date_hl)).date()
        
        # Finde den nächsten verfügbaren Handelstag nach date_hl + tw Tage
        target_date = date_hl + timedelta(days=tw)
        
        # Konvertiere data.index zu date objects für Vergleich
        data_dates = [d.date() if hasattr(d, 'date') else pd.to_datetime(d).date() for d in data.index]
        
        # Finde den nächsten verfügbaren Tag >= target_date
        for i, d in enumerate(data_dates):
            if d >= target_date:
                return data.index[i]
        
        # Falls kein späteres Datum gefunden, return letztes verfügbares Datum
        return data.index[-1] if len(data.index) > 0 else pd.NaT
        
    except Exception as e:
        print(f"⚠️ Fehler in get_trade_day_offset: {e}")
        return pd.NaT

def simulate_trades_compound_extended(signals_df, initial_capital, commission_rate, min_commission, 
                                    order_round_factor, data, trade_on_price='Close'):
    """
    ✅ ERWEITERTE TRADE SIMULATION
    """
    try:
        if signals_df is None or len(signals_df) == 0:
            print("❌ Keine Signale für Trade Simulation!")
            return None
            
        print(f"📊 Simuliere Trades mit {len(signals_df)} Signalen...")
        
        # Basis Trade-Simulation hier implementieren
        # (Komplex - würde separaten Code benötigen)
        
        result = {
            'initial_capital': initial_capital,
            'final_capital': initial_capital * 1.1,  # Placeholder
            'total_trades': len(signals_df[signals_df['Action'].isin(['buy', 'sell'])]),
            'win_rate': 0.6  # Placeholder
        }
        
        return result
        
    except Exception as e:
        print(f"❌ FEHLER in simulate_trades_compound_extended: {e}")
        return None

def calculate_shares(capital, price, round_factor=1):
    """
    Berechnet die Anzahl kaufbarer Einheiten für das gegebene Kapital und Rundung.
    """
    if price <= 0 or capital <= 0:
        return 0
    raw = capital / price
    return round(raw / round_factor) * round_factor

def update_level_close_long(ext, df, trade_on="Close"):
    """
    Update Level Close column based on trade_on parameter.
    trade_on: "Open" or "Close"
    """
    closes = []
    price_column = "Open" if trade_on.upper() == "OPEN" else "Close"
    
    for _, row in ext.iterrows():
        dt = row.get("Long Date detected")  # Changed from "Detect Date" to "Long Date detected"
        if pd.isna(dt):
            closes.append(np.nan)
        else:
            try:
                # Handle both string and datetime objects
                if isinstance(dt, str):
                    dt0 = pd.to_datetime(dt).normalize()
                else:
                    dt0 = dt.normalize()
                val = df.at[dt0, price_column]  # Use Open or Close based on trade_on
                closes.append(float(val))
            except:
                closes.append(np.nan)
    ext["Level Close"] = closes
    return ext

def berechne_best_p_tw_long(df, cfg, start_idx, end_idx, verbose=False, ticker=None):
    optimierungsergebnisse = []

    for past_window in range(2, 15):  # Erweitert von 3-10 auf 2-15
        for tw in range(1, 8):  # Erweitert von 1-6 auf 1-8
            try:
                df_opt = df.iloc[start_idx:end_idx].copy()
                # Both past_window and tw are optimized here
                support, resistance = calculate_support_resistance(df_opt, past_window, tw, verbose=False)
                signal_df = assign_long_signals_extended(support, resistance, df_opt, tw, "1d")
                # KORRIGIERT: Nicht update_level_close_long verwenden - das überschreibt mit NaN!
                # signal_df = update_level_close_long(signal_df, df_opt)  # DEAKTIVIERT!

                final_capital, _ = simulate_trades_compound_extended(
                    signal_df, 
                    cfg.get("initial_capital", 10000),
                    cfg.get("commission_rate", 0.001),
                    cfg.get("min_commission", 1.0),
                    cfg.get("order_round_factor", 1),
                    df_opt
                )

                optimierungsergebnisse.append({
                    "past_window": past_window,
                    "trade_window": tw,  # Store tw as trade_window for compatibility
                    "final_cap": final_capital
                })
            except Exception as e:
                continue

    if optimierungsergebnisse:
        df_result = pd.DataFrame(optimierungsergebnisse).sort_values("final_cap", ascending=False)
        best_row = df_result.iloc[0]
        p = int(best_row["past_window"])
        tw = int(best_row["trade_window"])
        if verbose:
            label = ticker or "Unbekannter Ticker"
            print(f"\n📊 Optimierung Long für {label}")
            print(df_result.to_string(index=False))
            print(f"→ Beste Kombination: {df_result.iloc[0].to_dict()}")
    else:
        p = 5
        tw = 2
        if verbose:
            print("⚠️ Keine Optimierungsergebnisse, nutze Default-Werte.")

    return p, tw

def plot_combined_chart_and_equity(df, standard, _dummy, supp, res, trend,
                                   equity_long, _empty, buyhold, ticker):
    offset = 0.02 * (df["Close"].max() - df["Close"].min())
    buy_off = 2 * offset
    sell_off = -2 * offset

    # Marker vorbereiten
    buy_m = pd.Series(np.nan, index=df.index)
    sell_m = pd.Series(np.nan, index=df.index)

    for _, row in standard.iterrows():
        dt = row.get("Long Date")
        if row.get("Long") == "buy" and pd.notna(dt):
            try:
                px = df.at[dt.normalize(), "Close"]
                buy_m.at[dt.normalize()] = float(px) + buy_off
            except:
                pass
        elif row.get("Long") == "sell" and pd.notna(dt):
            try:
                px = df.at[dt.normalize(), "Close"]
                sell_m.at[dt.normalize()] = float(px) + sell_off
            except:
                pass

    # Equity- & Buy&Hold als Arrays
    eq = np.array([float(v) for v in equity_long], dtype=float)
    bh = np.array([float(v) for v in buyhold], dtype=float)
    dates = df.index
    opens = df["Open"].to_numpy(dtype=float)
    highs = df["High"].to_numpy(dtype=float)
    lows = df["Low"].to_numpy(dtype=float)
    closes = df["Close"].to_numpy(dtype=float)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                   sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})

    # Chart 1: Candlestick + Trend + Zonen
    for i, dt in enumerate(dates):
        color = "green" if closes[i] >= opens[i] else "red"
        ax1.plot([dt, dt], [lows[i], highs[i]], color="black", lw=0.5)
        ax1.bar(dt, closes[i] - opens[i], bottom=opens[i],
                color=color, width=0.6, alpha=0.7)

    ax1.plot(trend.index, trend.values, label="Trend", color="blue", lw=2)
    ax1.scatter(supp.index, supp.values, label="Support",
                color="limegreen", marker="o", s=60)
    ax1.scatter(res.index, res.values, label="Resistance",
                color="red", marker="x", s=60)
    ax1.scatter(buy_m.index, buy_m.values, label="Buy",
                color="blue", marker="^", s=80)
    ax1.scatter(sell_m.index, sell_m.values, label="Sell",
                color="orange", marker="v", s=80)

    ax1.set_title(f"{ticker} – Candlestick mit Signalen & Zonen")
    ax1.legend()
    ax1.grid(True)

    # Chart 2: Equity vs Buy&Hold
    ax2.plot(dates, eq, label="Strategie", color="blue")
    ax2.plot(dates, bh, label="Buy & Hold", color="gray", linestyle="--")
    ax2.set_title("Kapitalentwicklung")
    ax2.set_ylabel("Kapital (€)")
    ax2.legend()
    ax2.grid(True)

    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def simulate_trades_compound_extended(signals_df, initial_capital, commission_rate, min_commission, 
                                    order_round_factor, data, trade_on_price='Close'):
    """
    ✅ ERWEITERTE TRADE SIMULATION
    Simuliert Trades basierend auf Signalen und gibt detaillierte Ergebnisse zurück.
    """
    try:
        if signals_df is None or len(signals_df) == 0:
            print("❌ Keine Signale für Trade Simulation!")
            return initial_capital, pd.DataFrame()
            
        print(f"📊 Simuliere Trades mit {len(signals_df)} Signalen...")
        
        # Grundlegende Trade-Simulation
        trades = []
        capital = initial_capital
        position = 0
        
        for idx, row in signals_df.iterrows():
            action = row.get('Action', '').lower()
            # KORRIGIERT: Level Close statt Close für extended signals
            price = row.get('Level Close', row.get('Close', 0))
            
            if action == 'buy' and position == 0:
                # Kaufen - Nutze das GANZE Capital, aber berücksichtige Fees
                # Berechne verfügbares Capital nach Abzug geschätzter Fees
                estimated_commission_rate = commission_rate
                # Iterative Berechnung: shares so dass (shares * price + commission) <= capital
                
                # Erste Näherung: rohes Capital durch Preis
                raw_shares = capital / price
                
                # Anwendung des order_round_factor (z.B. 1000 für DOGE)
                if order_round_factor >= 1:
                    # Runde auf Vielfache des Rundungsfaktors (z.B. 1000, 100, 10)
                    shares = round(raw_shares / order_round_factor) * order_round_factor
                else:
                    # Runde auf Dezimalstellen (z.B. 0.001 für BTC)
                    decimal_places = len(str(order_round_factor).split('.')[-1])
                    shares = round(raw_shares, decimal_places)
                
                # Überprüfe, ob genug Capital nach Rundung vorhanden ist
                if shares > 0:
                    cost = shares * price
                    commission = max(cost * commission_rate, min_commission)
                    total_required = cost + commission
                    
                    # Falls nach Rundung nicht genug Capital: reduziere shares
                    if total_required > capital:
                        # Berechne maximal mögliche shares unter Berücksichtigung von fees
                        max_cost = capital - min_commission  # Reserve für Mindest-Commission
                        if max_cost > 0:
                            max_shares_unrounded = max_cost / (price * (1 + commission_rate))
                            
                            # Wende Rundung auf reduzierte shares an
                            if order_round_factor >= 1:
                                shares = round(max_shares_unrounded / order_round_factor) * order_round_factor
                            else:
                                decimal_places = len(str(order_round_factor).split('.')[-1])
                                shares = round(max_shares_unrounded, decimal_places)
                            
                            # Neuberechnung der Kosten
                            cost = shares * price
                            commission = max(cost * commission_rate, min_commission)
                            total_required = cost + commission
                    
                    # Final validation
                    if shares > 0 and total_required <= capital:
                        capital -= total_required
                        position = shares
                        
                        trades.append({
                            'Date': idx,
                            'Action': 'BUY',
                            'Price': price,
                            'Shares': shares,
                            'Cost': total_required,
                            'Capital': capital
                        })
                    
            elif action == 'sell' and position > 0:
                # Verkaufen
                revenue = position * price
                commission = max(revenue * commission_rate, min_commission)
                capital += (revenue - commission)
                
                trades.append({
                    'Date': idx,
                    'Action': 'SELL',
                    'Price': price,
                    'Shares': position,
                    'Revenue': revenue - commission,
                    'Capital': capital
                })
                
                position = 0
        
        # Offene Position schließen (falls vorhanden)
        if position > 0 and len(signals_df) > 0:
            # KORRIGIERT: Level Close für extended signals
            last_price = signals_df['Level Close'].iloc[-1] if 'Level Close' in signals_df.columns else signals_df['Close'].iloc[-1]
            revenue = position * last_price
            commission = max(revenue * commission_rate, min_commission)
            capital += (revenue - commission)
        
        trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
        
        return capital, trades_df
        
    except Exception as e:
        print(f"❌ FEHLER in simulate_trades_compound_extended: {e}")
        return initial_capital, pd.DataFrame()