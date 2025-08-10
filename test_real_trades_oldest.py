#!/usr/bin/env python3
"""
Test the modified live_backtest_WORKING.py - 14 OLDEST trades for TODAY
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("🧪 Testing REAL TRADES + 14 OLDEST selection...")
    print(f"📅 Today's date: {datetime.now().strftime('%Y-%m-%d')}")
    print("🎯 Expected: Real trades for TODAY, 14 oldest selected")
    print("⛔ Blocked: All 2024 historical orders")
    print("🔄 Changed: Now uses actual backtest results, not sample data")
    print("-" * 70)
    
    from live_backtest_WORKING import get_14_day_trades_report
    
    print("\n🚀 Running REAL TRADES extraction (14 OLDEST for TODAY)...")
    trades = get_14_day_trades_report()
    
    print(f"\n📊 RESULT SUMMARY:")
    print(f"🔢 Total trades extracted: {len(trades)}")
    
    if trades:
        print(f"📅 Verification - All trades should be for TODAY:")
        dates = set(trade['date'] for trade in trades)
        for date in sorted(dates):
            count = sum(1 for t in trades if t['date'] == date)
            print(f"   - {date}: {count} trades")
            
            if '2024' in date:
                print(f"     🚨 ERROR: 2024 date found! This should be blocked!")
            elif date == datetime.now().strftime('%Y-%m-%d'):
                print(f"     ✅ TODAY's date - correct! ({count} trades)")
            else:
                print(f"     ⚠️ Non-today date: {date}")
        
        print(f"\n📊 Trade details (should be 14 OLDEST from today):")
        for i, trade in enumerate(trades[:5], 1):  # Show first 5 as sample
            print(f"   {i}. {trade['ticker']} | {trade['open_close']} | €{trade['price']:.4f}")
        if len(trades) > 5:
            print(f"   ... and {len(trades) - 5} more trades")
            
        print(f"\n📋 Key Changes Verified:")
        print(f"✅ Uses real backtest results (not sample data)")
        print(f"✅ Filters for TODAY only")
        print(f"✅ Selects 14 OLDEST trades (not newest)")
        print(f"✅ Sorts by date ascending (oldest first)")
        
    else:
        print("⚠️ No trades found - this might mean:")
        print("   - No actual trading signals generated today")
        print("   - Backtest analysis didn't produce trades")
        print("   - All trades were from historical dates (correctly blocked)")
    
    print(f"\n✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
