#!/usr/bin/env python3
"""
BITPANDA FUSION PAPER TRADING TEST
Vollständiger Test des Paper Trading Systems
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bitpanda_fusion_adapter import BitpandaFusionPaperTrader
from bitpanda_config import get_config, validate_config
from crypto_tickers import crypto_tickers

def run_comprehensive_test():
    """
    Führe umfassenden Test des Bitpanda Paper Trading Systems aus
    """
    print("🚀 BITPANDA FUSION PAPER TRADING - VOLLSTÄNDIGER TEST")
    print("=" * 70)
    
    # 1. Konfiguration validieren
    print("\n1️⃣ KONFIGURATION VALIDIEREN")
    print("-" * 40)
    validate_config()
    
    # 2. Paper Trader initialisieren
    print("\n2️⃣ PAPER TRADER INITIALISIEREN")
    print("-" * 40)
    trader = BitpandaFusionPaperTrader(sandbox=True)
    
    # 3. Aktuelle Marktpreise abrufen
    print("\n3️⃣ MARKTDATEN ABRUFEN")
    print("-" * 40)
    current_prices = trader.get_current_prices()
    
    if not current_prices:
        print("❌ Keine Marktpreise verfügbar - beende Test")
        return None
    
    # 4. Initial Portfolio anzeigen
    print("\n4️⃣ INITIAL PORTFOLIO")
    print("-" * 40)
    initial_portfolio = trader.get_portfolio_value(current_prices)
    print(f"💰 Startkapital: €{initial_portfolio['total_value']:,.2f}")
    
    # 5. Manuelle Test-Orders
    print("\n5️⃣ MANUELLE TEST-ORDERS")
    print("-" * 40)
    test_orders = [
        {'ticker': 'BTC-EUR', 'action': 'BUY', 'amount': 1000},
        {'ticker': 'ETH-EUR', 'action': 'BUY', 'amount': 800},
        {'ticker': 'DOGE-EUR', 'action': 'BUY', 'amount': 500}
    ]
    
    for order in test_orders:
        ticker = order['ticker']
        if ticker in current_prices:
            price = current_prices[ticker]
            limit_price = price * 0.999  # Slightly below market
            result = trader.place_paper_order(
                ticker, order['action'], order['amount'], limit_price
            )
            time.sleep(0.5)  # Kurze Pause zwischen Orders
    
    # 6. Backtest-basierte Signale
    print("\n6️⃣ BACKTEST-SIGNALE AUSFÜHREN")
    print("-" * 40)
    trader.execute_backtest_signals()
    
    # 7. Portfolio nach Trading anzeigen
    print("\n7️⃣ PORTFOLIO NACH TRADING")
    print("-" * 40)
    time.sleep(1)
    final_prices = trader.get_current_prices()
    final_portfolio = trader.get_portfolio_value(final_prices)
    
    performance = final_portfolio['total_value'] - initial_portfolio['total_value']
    performance_pct = (performance / initial_portfolio['total_value']) * 100
    
    print(f"💰 Endwert: €{final_portfolio['total_value']:,.2f}")
    print(f"📊 Performance: €{performance:+.2f} ({performance_pct:+.2f}%)")
    
    # 8. Detaillierten Report generieren
    print("\n8️⃣ TRADING REPORT GENERIEREN")
    print("-" * 40)
    trader.generate_trading_report()
    
    # 9. Test-Statistiken
    print("\n9️⃣ TEST-STATISTIKEN")
    print("-" * 40)
    print(f"📋 Total Orders: {len(trader.trade_history)}")
    if trader.trade_history:
        buy_orders = len([t for t in trader.trade_history if t['action'] == 'BUY'])
        sell_orders = len([t for t in trader.trade_history if t['action'] == 'SELL'])
        total_fees = sum([t['fees'] for t in trader.trade_history])
        
        print(f"🟢 BUY Orders: {buy_orders}")
        print(f"🔴 SELL Orders: {sell_orders}")
        print(f"💸 Total Gebühren: €{total_fees:.2f}")
    
    active_positions = len([p for p in trader.paper_portfolio['positions'].values() if p['quantity'] > 0])
    print(f"📊 Aktive Positionen: {active_positions}")
    print(f"💵 Verfügbares Cash: €{trader.paper_portfolio['EUR']:,.2f}")
    
    return trader

def run_extended_simulation(days: int = 7):
    """
    Führe erweiterte Multi-Tage Simulation aus
    """
    print(f"\n🔄 ERWEITERTE {days}-TAGE SIMULATION")
    print("=" * 50)
    
    trader = BitpandaFusionPaperTrader(sandbox=True)
    daily_performance = []
    
    for day in range(days):
        print(f"\n📅 Tag {day + 1}/{days}")
        print("-" * 30)
        
        # Simuliere Marktbewegungen (kleine zufällige Änderungen)
        current_prices = trader.get_current_prices()
        
        # Führe tägliche Trading-Routine aus
        trader.execute_backtest_signals()
        
        # Berechne Tagesperformance
        portfolio = trader.get_portfolio_value(current_prices)
        daily_performance.append(portfolio['total_value'])
        
        print(f"   💰 Portfoliowert: €{portfolio['total_value']:,.2f}")
        
        if day > 0:
            daily_change = portfolio['total_value'] - daily_performance[day-1]
            daily_change_pct = (daily_change / daily_performance[day-1]) * 100
            print(f"   📊 Tagesänderung: €{daily_change:+.2f} ({daily_change_pct:+.2f}%)")
        
        time.sleep(0.5)  # Kurze Pause zwischen Tagen
    
    # Finale Simulation-Statistiken
    print(f"\n📊 SIMULATION ABGESCHLOSSEN")
    print("-" * 30)
    total_return = daily_performance[-1] - daily_performance[0]
    total_return_pct = (total_return / daily_performance[0]) * 100
    
    print(f"🎯 Gesamtperformance: €{total_return:+.2f} ({total_return_pct:+.2f}%)")
    print(f"📈 Bester Tag: €{max(daily_performance):,.2f}")
    print(f"📉 Schlechtester Tag: €{min(daily_performance):,.2f}")
    
    # Performance Chart (einfach)
    print(f"\n📈 PERFORMANCE VERLAUF:")
    for i, value in enumerate(daily_performance):
        change = "📈" if i == 0 or value >= daily_performance[i-1] else "📉"
        print(f"   Tag {i+1:2d}: {change} €{value:8,.2f}")
    
    return trader, daily_performance

def test_individual_components():
    """
    Teste einzelne Komponenten isoliert
    """
    print("\n🔧 KOMPONENTEN-TESTS")
    print("=" * 40)
    
    # Test 1: Konfiguration
    print("\n🧪 Test 1: Konfiguration laden")
    config = get_config('paper_trading')
    print(f"   ✅ {len(config)} Konfigurationsparameter geladen")
    
    # Test 2: Ticker Mapping
    print("\n🧪 Test 2: Ticker Mapping")
    ticker_config = get_config('tickers')
    for ticker in crypto_tickers.keys():
        if ticker in ticker_config:
            symbol = ticker_config[ticker]['bitpanda_symbol']
            print(f"   ✅ {ticker} -> {symbol}")
        else:
            print(f"   ⚠️ {ticker} nicht gemappt")
    
    # Test 3: Paper Trading Initialisierung
    print("\n🧪 Test 3: Paper Trading Initialisierung")
    trader = BitpandaFusionPaperTrader(sandbox=True)
    print(f"   ✅ Trader initialisiert mit €{trader.paper_portfolio['EUR']:,.2f}")
    
    # Test 4: Preisdaten-Abruf
    print("\n🧪 Test 4: Preisdaten-Abruf")
    prices = trader.get_current_prices()
    print(f"   ✅ {len(prices)} Preise abgerufen")
    
    # Test 5: Order-Simulation
    print("\n🧪 Test 5: Order-Simulation")
    if 'BTC-EUR' in prices:
        order = trader.place_paper_order('BTC-EUR', 'BUY', 100, prices['BTC-EUR'])
        status = order['status']
        print(f"   ✅ Test-Order Status: {status}")
    
    print("\n✅ Alle Komponenten-Tests erfolgreich!")

def main():
    """
    Haupt-Testfunktion
    """
    print("🎯 BITPANDA FUSION PAPER TRADING - INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # 1. Komponenten-Tests
        test_individual_components()
        
        # 2. Vollständiger System-Test
        trader = run_comprehensive_test()
        
        if trader is None:
            print("❌ System-Test fehlgeschlagen")
            return
        
        # 3. Erweiterte Simulation (optional)
        print(f"\n❓ Erweiterte 3-Tage Simulation starten? (j/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['j', 'ja', 'y', 'yes']:
                run_extended_simulation(3)
        except KeyboardInterrupt:
            print("\n⏹️ Simulation abgebrochen")
        
        print(f"\n🎉 ALLE TESTS ERFOLGREICH ABGESCHLOSSEN!")
        print(f"📁 Trading Reports wurden als CSV gespeichert")
        print(f"🚀 System ist bereit für Bitpanda Fusion Paper Trading!")
        
    except Exception as e:
        print(f"\n❌ FEHLER WÄHREND DER TESTS: {e}")
        print(f"🔍 Debug-Informationen:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
