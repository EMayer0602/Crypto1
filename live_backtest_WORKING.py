#!/usr/bin/env python3
"""
LIVE BACKTEST WORKING - Aufruf der integrierten Funktion
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the integrated live backtest function
from crypto_backtesting_module import run_live_backtest_analysis

if __name__ == "__main__":
    """
    Hauptfunktion - ruft die integrierte Live-Backtest Analyse auf
    """
    print("🚀 Starting LIVE Crypto Backtest...")
    
    # Run the integrated live backtest analysis
    result = run_live_backtest_analysis()
    
    if result:
        print(f"✅ Live backtest completed successfully!")
        print(f"📊 Report: {result}")
    else:
        print("❌ Live backtest failed!")
        sys.exit(1)
