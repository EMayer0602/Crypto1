#!/usr/bin/env python3
"""
PROCESS CHECKER - Find and manage crypto trading processes
"""

import psutil
import sys
import os
from datetime import datetime

def find_crypto_trading_processes():
    """Find all Python processes related to crypto trading"""
    
    print("🔍 SCANNING FOR CRYPTO TRADING PROCESSES")
    print("=" * 50)
    
    crypto_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    
                    # Look for crypto trading related scripts
                    crypto_keywords = [
                        'daily_opening_trader',
                        'simple_daily_trader', 
                        'signal_transmitter',
                        'crypto_backtest',
                        'live_backtest',
                        'bitpanda',
                        'trading'
                    ]
                    
                    for keyword in crypto_keywords:
                        if keyword in cmdline_str.lower():
                            create_time = datetime.fromtimestamp(proc.info['create_time'])
                            crypto_processes.append({
                                'pid': proc.info['pid'],
                                'cmdline': cmdline_str,
                                'created': create_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'keyword': keyword
                            })
                            break
                            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if crypto_processes:
        print(f"📊 Found {len(crypto_processes)} crypto trading processes:")
        for i, proc in enumerate(crypto_processes, 1):
            print(f"\n{i}. PID: {proc['pid']}")
            print(f"   Command: {proc['cmdline']}")
            print(f"   Created: {proc['created']}")
            print(f"   Keyword: {proc['keyword']}")
            
        return crypto_processes
    else:
        print("✅ No crypto trading processes found")
        return []

def stop_process_by_pid(pid):
    """Safely stop a specific process by PID"""
    
    try:
        proc = psutil.Process(pid)
        proc.terminate()  # Send SIGTERM first
        
        # Wait up to 3 seconds for graceful termination
        proc.wait(timeout=3)
        print(f"✅ Process {pid} terminated gracefully")
        return True
        
    except psutil.TimeoutExpired:
        # Force kill if didn't terminate gracefully
        try:
            proc.kill()
            print(f"🔥 Process {pid} force killed")
            return True
        except:
            print(f"❌ Failed to kill process {pid}")
            return False
            
    except psutil.NoSuchProcess:
        print(f"⚠️ Process {pid} already terminated")
        return True
        
    except Exception as e:
        print(f"❌ Error stopping process {pid}: {e}")
        return False

def main():
    """Main function"""
    
    print("🔧 CRYPTO TRADING PROCESS MANAGER")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Find processes
    processes = find_crypto_trading_processes()
    
    if not processes:
        print("\n💡 No crypto trading processes to manage")
        return
    
    print(f"\n⚠️ Found processes that might be running the 300-second cycles")
    print("💡 You can manually stop specific processes if needed")
    
    # Show how to stop processes
    print(f"\n📝 TO STOP A SPECIFIC PROCESS:")
    print("   1. Note the PID of the unwanted process")
    print("   2. Run: python -c \"import psutil; psutil.Process(PID).terminate()\"")
    print("   3. Replace PID with the actual process ID")
    
    print(f"\n🚀 TO START FRESH:")
    print("   Run: python simple_daily_trader.py")

if __name__ == "__main__":
    main()
