from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

# Teste XRP-EUR matched_trades direkt
result = run_backtest('XRP-EUR', crypto_tickers['XRP-EUR'])

print("=== EQUITY CURVE TEST ===")
if result:
    equity_curve = result.get('equity_curve', [])
    buyhold_curve = result.get('buyhold_curve', [])
    
    print(f"Equity Curve length: {len(equity_curve)}")
    print(f"BuyHold Curve length: {len(buyhold_curve)}")
    
    if len(equity_curve) > 0:
        print(f"Equity first 3: {equity_curve[:3]}")
        print(f"Equity last 3: {equity_curve[-3:]}")
        print(f"Equity min: {min(equity_curve):.0f}")
        print(f"Equity max: {max(equity_curve):.0f}")
    
    if len(buyhold_curve) > 0:
        print(f"BuyHold first 3: {buyhold_curve[:3]}")
        print(f"BuyHold last 3: {buyhold_curve[-3:]}")
    
else:
    print("❌ NO RESULT FROM BACKTEST!")
