#!/usr/bin/env python3

import sys
import os
from datetime import datetime

# Redirect output to file
log_file = open("bitpanda_execution.log", "w", encoding='utf-8')
sys.stdout = log_file
sys.stderr = log_file

try:
    print(f"BITPANDA PAPER TRADING START: {datetime.now()}")
    
    # Add current directory to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from signal_transmitter import transmit_backtest_signals
    
    print("Signal transmitter imported successfully")
    
    orders = transmit_backtest_signals()
    
    print(f"RESULT: {orders} orders transmitted to Bitpanda Paper Trading")
    print(f"COMPLETED: {datetime.now()}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    log_file.close()
    
    # Also create a simple result file
    with open("result.txt", "w") as f:
        f.write(f"Execution completed at {datetime.now()}\n")
