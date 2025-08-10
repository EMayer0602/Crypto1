#!/usr/bin/env python3
"""
QUICK STATUS CHECK - See what's actually running
"""

import psutil
import os
from datetime import datetime

print("🔍 CRYPTO TRADING STATUS CHECK")
print("=" * 50)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Check all Python processes
print("\n🐍 All Python processes:")
python_processes = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
    try:
        if proc.info['name'] and 'python' in proc.info['name'].lower():
            cmdline = proc.info['cmdline']
            if cmdline and len(cmdline) > 1:
                script = cmdline[-1] if cmdline[-1].endswith('.py') else 'N/A'
                create_time = datetime.fromtimestamp(proc.info['create_time'])
                
                python_processes.append({
                    'pid': proc.info['pid'],
                    'script': script,
                    'age': create_time,
                    'cmdline': ' '.join(cmdline)
                })
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

if python_processes:
    for i, proc in enumerate(python_processes, 1):
        print(f"{i}. PID: {proc['pid']} | Script: {proc['script']}")
        print(f"   Started: {proc['age'].strftime('%Y-%m-%d %H:%M:%S')}")
        if 'daily_opening_trader' in proc['script'] or 'crypto' in proc['cmdline'].lower():
            print("   🚨 POTENTIAL OLD CRYPTO TRADER!")
        print(f"   Command: {proc['cmdline'][:80]}...")
        print()
else:
    print("✅ No Python processes found")

# Check current directory files
print("\n📂 Current trading files:")
trading_files = [
    'daily_opening_trader.py',
    'simple_daily_trader.py', 
    'signal_transmitter.py',
    'live_backtest_WORKING.py'
]

for file in trading_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        mtime = datetime.fromtimestamp(os.path.getmtime(file))
        status = "🟢 NEW" if file in ['simple_daily_trader.py', 'signal_transmitter.py'] else "🔴 OLD"
        print(f"{status} {file} ({size} bytes, modified {mtime.strftime('%H:%M:%S')})")
    else:
        print(f"❌ {file} - Not found")

print(f"\n💡 If you see 'Cycle 10' messages, they're likely from:")
print("   - Old terminal output still displayed")
print("   - Previous session logs")
print("   - Not from current running processes")
