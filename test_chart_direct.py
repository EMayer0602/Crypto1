from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers
from plotly_utils import plotly_combined_chart_and_equity
import pandas as pd

# 1. Backtest für XRP-EUR
print("=== RUNNING XRP-EUR BACKTEST ===")
result = run_backtest('XRP-EUR', crypto_tickers['XRP-EUR'])

if result:
    print(f"✅ Backtest successful")
    
    # 2. Extrahiere Daten 
    df = result['df_bt'].copy()
    ext_signals = result.get('ext_signals', pd.DataFrame())
    equity_curve = result.get('equity_curve', [])
    buyhold_curve = result.get('buyhold_curve', [])  # ✅ ECHTE BUYHOLD AUS RESULT!
    initial_capital = crypto_tickers['XRP-EUR'].get('initialCapitalLong', 1000)
    
    print(f"Initial Capital: {initial_capital}")
    print(f"Equity Curve: {len(equity_curve)} values")
    print(f"Buy&Hold Curve: {len(buyhold_curve)} values")
    print(f"Equity First 3: {equity_curve[:3]}")
    print(f"Equity Last 3: {equity_curve[-3:]}")
    print(f"BuyHold First 3: {buyhold_curve[:3] if len(buyhold_curve) > 0 else 'EMPTY'}")
    print(f"BuyHold Last 3: {buyhold_curve[-3:] if len(buyhold_curve) > 0 else 'EMPTY'}")
    
    # 3. Erstelle Chart direkt
    print("\n=== CREATING CHART ===")
    chart_success = plotly_combined_chart_and_equity(
        df=df,
        standard_signals=ext_signals,
        support=pd.Series(dtype=float),
        resistance=pd.Series(dtype=float),
        equity_curve=equity_curve,
        buyhold_curve=buyhold_curve,  # ✅ ECHTE BUYHOLD CURVE!
        ticker='XRP-EUR',
        backtest_years=None,
        initial_capital=initial_capital
    )
    
    if chart_success:
        print("✅ Chart created successfully!")
        print("📊 Check chart_XRP_EUR.html")
    else:
        print("❌ Chart failed")
else:
    print("❌ Backtest failed")
