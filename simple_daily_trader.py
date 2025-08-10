#!/usr/bin/env python3
"""
SIMPLE DAILY OPENING TRADER
Uses signals from live_backtest_WORKING.py and transmits them immediately at daily open
"""

import time
from datetime import datetime, timedelta
import signal
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from signal_transmitter import transmit_backtest_signals

class SimpleDailyOpeningTrader:
    """Simple trader that uses backtest signals at daily opening"""
    
    def __init__(self):
        self.running = False
        print("🚀 SIMPLE DAILY OPENING TRADER")
        print("=" * 50)
        print("💡 Uses signals from live_backtest_WORKING.py")
        print("📡 Transmits orders immediately at daily open")
        print("⏰ Runs at 00:00 UTC for 2 weeks")
        print("=" * 50)
    
    def wait_for_next_opening(self):
        """Wait until next daily opening (00:00 UTC)"""
        
        now = datetime.now()
        next_open = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # If we've passed today's opening, move to tomorrow
        if now.hour > 0 or (now.hour == 0 and now.minute > 5):
            next_open += timedelta(days=1)
        
        time_until = (next_open - now).total_seconds()
        
        print(f"\n⏳ WAITING FOR NEXT OPENING")
        print(f"   Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Next Opening: {next_open.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Time Until: {time_until/3600:.1f} hours")
        
        # Sleep until opening time
        if time_until > 0:
            time.sleep(time_until)
    
    def execute_opening_session(self, day_number: int):
        """Execute one opening session using backtest signals"""
        
        print(f"\n🔔 MARKET OPEN - DAY {day_number}")
        print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        try:
            # Get signals from backtest and transmit immediately
            orders_transmitted = transmit_backtest_signals()
            
            print(f"\n📊 SESSION {day_number} COMPLETE")
            print(f"📈 Orders Transmitted: {orders_transmitted}")
            print("⏳ Waiting for next day...")
            
            return orders_transmitted
            
        except Exception as e:
            print(f"❌ Error in session {day_number}: {e}")
            return 0
    
    def run_2_week_campaign(self):
        """Run the 2-week daily opening campaign"""
        
        print(f"\n🎯 STARTING 2-WEEK CAMPAIGN")
        print(f"📅 Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🔄 Simple cycle: Wait for opening → Get backtest signals → Transmit → Repeat")
        print("="*60)
        
        self.running = True
        start_date = datetime.now()
        end_date = start_date + timedelta(days=14)
        
        day_count = 0
        total_orders = 0
        
        try:
            while self.running and datetime.now() < end_date and day_count < 14:
                
                # Wait for next opening
                self.wait_for_next_opening()
                
                # Execute opening session
                if self.running and datetime.now() < end_date:
                    day_count += 1
                    orders = self.execute_opening_session(day_count)
                    total_orders += orders
                
        except KeyboardInterrupt:
            print("\n🛑 STOPPED BY USER")
        
        finally:
            self.running = False
            
            print(f"\n🏁 2-WEEK CAMPAIGN COMPLETED!")
            print("="*50)
            print(f"📅 Duration: {datetime.now() - start_date}")
            print(f"📊 Days Traded: {day_count}")
            print(f"📈 Total Orders: {total_orders}")
            print("="*50)

def main():
    """Main function"""
    
    print("🚀 SIMPLE DAILY OPENING TRADER")
    print("💡 Gets signals from live_backtest_WORKING.py at daily open")
    print("📡 Transmits orders to paper trading immediately")
    print("⏰ Runs for 2 weeks at 00:00 UTC daily")
    print("⚠️ Press Ctrl+C to stop")
    print()
    
    trader = SimpleDailyOpeningTrader()
    
    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print("\n🛑 Shutdown signal received...")
        trader.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start campaign
    trader.run_2_week_campaign()

if __name__ == "__main__":
    main()
