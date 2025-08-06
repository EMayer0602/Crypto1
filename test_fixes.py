#!/usr/bin/env python3
"""Test der fixes für shares und matched trades"""

from unified_crypto_report import generate_unified_crypto_report

print("🧪 Testing Unified Crypto Report fixes...")
print("=" * 60)

# Test nur ein kurzer Lauf
result = generate_unified_crypto_report()

if result:
    print("\n✅ TEST ERFOLGREICH!")
    print(f"Trades: {len(result['all_weekly_trades'])}")
    print(f"Matched Trades: {len(result['all_matched_trades'])}")
    
    # Zeige ein Sample Trade
    if result['all_weekly_trades']:
        sample_trade = result['all_weekly_trades'][0]
        print(f"Sample Trade: {sample_trade}")
        
    # Zeige ein Sample Matched Trade
    if result['all_matched_trades']:
        sample_matched = result['all_matched_trades'][0]
        print(f"Sample Matched Trade: {sample_matched}")
else:
    print("❌ TEST FEHLGESCHLAGEN!")
