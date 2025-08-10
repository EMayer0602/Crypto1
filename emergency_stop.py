#!/usr/bin/env python3
"""
EMERGENCY STOP - Kill the old trader that's sending 2024 signals
"""

import os
import sys
import psutil
import time
from datetime import datetime

def emergency_stop():
    """Stop any process sending old 2024 signals"""
    
    print("🚨 EMERGENCY STOP - KILLING OLD TRADER")
    print("="*50)
    print(f"🎯 Target: Process sending 2024 signals with 300s cycles")
    print(f"📅 Current date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    killed_processes = []
    
    # Find and kill Python processes related to trading
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    
                    # Check for trading-related scripts
                    trading_keywords = [
                        'daily_opening_trader.py',
                        'crypto_trading',
                        'bitpanda_live',
                        'live_backtest'
                    ]
                    
                    for keyword in trading_keywords:
                        if keyword in cmdline_str:
                            print(f"🎯 Found trading process: PID {proc.info['pid']}")
                            print(f"   Script: {cmdline_str}")
                            print(f"   Started: {datetime.fromtimestamp(proc.info['create_time'])}")
                            
                            try:
                                proc.terminate()
                                print(f"   ⚠️ Terminated (SIGTERM)")
                                killed_processes.append(proc.info['pid'])
                                
                                # Wait a bit, then force kill if still running
                                time.sleep(2)
                                if proc.is_running():
                                    proc.kill()
                                    print(f"   💀 Force killed (SIGKILL)")
                                    
                            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                                print(f"   ❌ Could not kill: {e}")
                            
                            break
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if killed_processes:
        print(f"\n✅ Killed {len(killed_processes)} trading processes:")
        for pid in killed_processes:
            print(f"   - PID {pid}")
    else:
        print(f"\n⚠️ No obvious trading processes found")
        print("The 'Cycle 11' might be from:")
        print("  - A hidden background process")
        print("  - VS Code integrated terminal")
        print("  - System service or scheduled task")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Check if 'Cycle X' messages stop appearing")
    print("2. Close all VS Code terminals and open fresh ones")
    print("3. Start clean with: python simple_daily_trader.py")
    print("4. Monitor that only TODAY (2025-08-10) signals are sent")

def nuclear_option():
    """Last resort: Kill ALL Python processes"""
    print(f"\n🚨 NUCLEAR OPTION: Kill ALL Python processes")
    response = input("This will kill ALL Python processes. Type 'YES' to confirm: ")
    
    if response == 'YES':
        os.system("taskkill /F /IM python.exe /T")
        print("💥 All Python processes terminated")
    else:
        print("❌ Nuclear option cancelled")

if __name__ == "__main__":
    emergency_stop()
    
    print(f"\n❓ Are you still seeing 'Cycle X' messages?")
    print("If YES, we may need the nuclear option to kill ALL Python processes.")
    
    # Uncomment the next line only if needed:
    # nuclear_option()
