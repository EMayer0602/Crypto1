#!/usr/bin/env python3
"""
Test the modified live_backtest_WORKING.py
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("🧪 Testing modified live_backtest_WORKING.py...")
    print(f"📅 Today's date: {datetime.now().strftime('%Y-%m-%d')}")
    print("🎯 Expected: Only orders for 2025-08-10")
    print("⛔ Blocked: All 2024 historical orders")
    print("-" * 60)
    
    from live_backtest_WORKING import get_14_day_trades_report
    
    print("\n🚀 Running TODAY-ONLY trade report...")
    trades = get_14_day_trades_report()
    
    print(f"\n📊 RESULT SUMMARY:")
    print(f"🔢 Total trades generated: {len(trades)}")
    
    if trades:
        print(f"📅 Dates in report:")
        dates = set(trade['date'] for trade in trades)
        for date in sorted(dates):
            print(f"   - {date}")
            if '2024' in date:
                print(f"     🚨 ERROR: 2024 date found! This should be blocked!")
            elif date == datetime.now().strftime('%Y-%m-%d'):
                print(f"     ✅ TODAY's date - correct!")
            else:
                print(f"     ⚠️ Non-today date: {date}")
    
    print(f"\n✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
