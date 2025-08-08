from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers

# Test buyhold_curve direkt
result = run_backtest('XRP-EUR', crypto_tickers['XRP-EUR'])

print("\n=== BUYHOLD CURVE TEST ===")
if result:
    buyhold = result.get('buyhold_curve', [])
    print(f"BuyHold length: {len(buyhold)}")
    if len(buyhold) > 0:
        print(f"BuyHold first 3: {buyhold[:3]}")
        print(f"BuyHold last 3: {buyhold[-3:]}")
        print(f"BuyHold min: {min(buyhold):.0f}")
        print(f"BuyHold max: {max(buyhold):.0f}")
    else:
        print("❌ BUYHOLD CURVE IS EMPTY!")
else:
    print("❌ NO RESULT FROM BACKTEST!")
