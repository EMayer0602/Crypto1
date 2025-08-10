#!/usr/bin/env python3
"""
SOFORTIGER PAPER TRADING MIT LOG
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def log_and_print(message):
    """Print und Log gleichzeitig"""
    print(message)
    with open("paper_trading_log.txt", "a", encoding='utf-8') as f:
        f.write(f"{datetime.now()}: {message}\n")

try:
    log_and_print("🚀 STARTING IMMEDIATE PAPER TRADING")
    
    from signal_transmitter import transmit_backtest_signals
    
    log_and_print("📡 Importing signal transmitter successful")
    
    # Führe die Signalübertragung aus
    orders_transmitted = transmit_backtest_signals()
    
    log_and_print(f"✅ SUCCESS: {orders_transmitted} orders transmitted to Paper Trading")
    
except Exception as e:
    log_and_print(f"❌ ERROR: {e}")
    import traceback
    error_details = traceback.format_exc()
    log_and_print(f"ERROR DETAILS: {error_details}")

log_and_print("🏁 SCRIPT COMPLETED")
