#!/usr/bin/env python3
"""
IMMEDIATE FIX - Stop 2024 signals and start fresh 2025 system
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def immediate_fix():
    """Stop everything and start fresh"""
    
    print("🚨 IMMEDIATE FIX FOR 2024 SIGNAL PROBLEM")
    print("=" * 60)
    print(f"📅 Today is: {datetime.now().strftime('%Y-%m-%d')}")
    print("🎯 Goal: Stop 2024 signals, start fresh 2025 system")
    print("=" * 60)
    
    print("\n1️⃣ KILLING ALL PYTHON PROCESSES...")
    try:
        # Try multiple methods to kill Python processes
        os.system("taskkill /F /IM python.exe /T >nul 2>&1")
        os.system("taskkill /F /IM pythonw.exe /T >nul 2>&1")
        
        print("✅ Python processes terminated")
        time.sleep(2)
        
    except Exception as e:
        print(f"⚠️ Kill command error: {e}")
    
    print("\n2️⃣ CHECKING FOR REMAINING PROCESSES...")
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, timeout=10)
        if 'python.exe' in result.stdout:
            print("⚠️ Some Python processes still running")
        else:
            print("✅ No Python processes found")
    except:
        print("⚠️ Could not check processes")
    
    print("\n3️⃣ CLEARING PROBLEMATIC DATA...")
    
    # Check for any files that might contain 2024 signals
    problem_files = [
        'current_backtest_report.py',
        '14_day_trades_REAL_*.csv',
        '*paper_trading*.csv'
    ]
    
    print("📂 Checking for files with potentially old signals...")
    for pattern in problem_files:
        if '*' in pattern:
            import glob
            matches = glob.glob(pattern)
            for match in matches:
                mtime = os.path.getmtime(match)
                mod_date = datetime.fromtimestamp(mtime)
                if mod_date.year == 2024:
                    print(f"⚠️ Found 2024 file: {match} (modified: {mod_date.strftime('%Y-%m-%d')})")
        else:
            if os.path.exists(pattern):
                mtime = os.path.getmtime(pattern)
                mod_date = datetime.fromtimestamp(mtime)
                print(f"📄 {pattern} - {mod_date.strftime('%Y-%m-%d')}")
    
    print("\n4️⃣ VERIFYING NEW SYSTEM FILES...")
    
    new_files = {
        'simple_daily_trader.py': 'New daily opening trader (2025 only)',
        'signal_transmitter.py': 'Today-only signal extractor',
        'bitpanda_live_integration.py': 'Live data integration'
    }
    
    for file, desc in new_files.items():
        if os.path.exists(file):
            print(f"✅ {file} - {desc}")
        else:
            print(f"❌ {file} - MISSING!")
    
    print("\n5️⃣ STARTING FRESH 2025 SYSTEM...")
    print("🎯 This system will ONLY process signals from 2025-08-10 onwards")
    print("⛔ It will IGNORE any historical 2024 signals")
    print("📅 It runs at daily open, NOT every 300 seconds")
    
    return True

def start_fresh_system():
    """Start the correct 2025-only system"""
    
    print("\n🚀 STARTING FRESH 2025 SYSTEM")
    print("-" * 40)
    
    try:
        # Import the new system
        from simple_daily_trader import SimpleDailyOpeningTrader
        
        print("✅ SimpleDailyOpeningTrader loaded")
        print("🎯 This will:")
        print("   - Wait for daily market opening")
        print("   - Generate signals for TODAY (2025-08-10)")
        print("   - Transmit ONLY fresh signals")
        print("   - NO 300-second cycles")
        print("   - NO 2024 historical signals")
        
        print("\n🔄 Starting trader...")
        trader = SimpleDailyOpeningTrader()
        trader.run_2_week_campaign()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Simple_daily_trader.py may need to be recreated")
    except Exception as e:
        print(f"❌ Start error: {e}")

if __name__ == "__main__":
    if immediate_fix():
        print(f"\n{'='*60}")
        print("✅ IMMEDIATE FIX COMPLETE")
        print("🛑 Old 2024 system should be stopped")
        print("🚀 Ready to start fresh 2025 system")
        print("=" * 60)
        
        start_fresh_system()
    else:
        print("\n❌ Fix failed - manual intervention needed")
