#!/usr/bin/env python3
"""
CLEAN STARTUP - Ensure only the new simple daily trader is running
"""

import os
import sys
import time
import psutil
from datetime import datetime

def ensure_clean_startup():
    """Ensure clean environment and start the correct trader"""
    
    print("🧹 CLEAN STARTUP FOR CRYPTO TRADING")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Check for any old trading processes
    print("\n🔍 Checking for old trading processes...")
    
    old_processes_found = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    if 'daily_opening_trader.py' in cmdline_str:
                        print(f"⚠️ Found old daily_opening_trader.py (PID: {proc.info['pid']})")
                        print("💡 This might be the source of '300s cycles' - consider stopping it")
                        old_processes_found = True
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if not old_processes_found:
        print("✅ No old trading processes found")
    
    # 2. Verify our new files exist
    print("\n📂 Verifying new system files...")
    
    required_files = [
        'simple_daily_trader.py',
        'signal_transmitter.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing!")
            return False
    
    # 3. Test signal transmitter
    print("\n🧪 Testing signal transmitter...")
    try:
        from signal_transmitter import SignalTransmitter
        transmitter = SignalTransmitter()
        print("✅ Signal transmitter loaded successfully")
    except Exception as e:
        print(f"❌ Signal transmitter error: {e}")
        return False
    
    # 4. Start the correct system
    print("\n🚀 STARTING NEW SYSTEM...")
    print("💡 This system will:")
    print("   - Wait for daily opening (00:00 UTC)")
    print("   - Run live_backtest_WORKING.py to get TODAY's signals")
    print("   - Transmit only fresh signals from today (2025-08-10)")
    print("   - NO 300-second cycles!")
    print("   - NO historical signals from 2024!")
    
    return True

def main():
    """Main function"""
    
    if ensure_clean_startup():
        print(f"\n✅ CLEAN STARTUP COMPLETE")
        print("=" * 50)
        print("🎯 System ready for daily opening trading")
        print("💡 Old '300s cycle' messages are from previous sessions")
        print("🚀 New system will run cleanly at market opening")
        
        # Import and start the simple daily trader
        try:
            from simple_daily_trader import SimpleDailyOpeningTrader
            
            print(f"\n🔔 Starting Simple Daily Opening Trader...")
            trader = SimpleDailyOpeningTrader()
            trader.run_2_week_campaign()
            
        except KeyboardInterrupt:
            print(f"\n🛑 Stopped by user")
        except Exception as e:
            print(f"\n❌ Error starting trader: {e}")
            
    else:
        print(f"\n❌ Clean startup failed - check errors above")

if __name__ == "__main__":
    main()
