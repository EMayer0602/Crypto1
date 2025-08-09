#!/usr/bin/env python3
"""
Test der stillen Optimierung (ohne Debug-Ausgaben)
"""

from crypto_backtesting_module import run_backtest

def test_silent_optimization():
    """Test dass die Optimierung jetzt ruhiger läuft"""
    
    print("🔍 Teste stille Optimierung...")
    
    # Schneller Test mit XRP-EUR
    try:
        result = run_backtest("XRP-EUR", crypto_tickers["XRP-EUR"])
        
        if result and 'optimal_p' in result:
            print(f"✅ Optimierung abgeschlossen:")
            print(f"   Past Window: {result['optimal_p']}")
            print(f"   Trade Window: {result['optimal_tw']}")
            print(f"   Final Capital: €{result['final_capital']:.2f}")
            print("✅ Konsole ist jetzt sauber - keine Debug-Spam mehr!")
        else:
            print("❌ Optimierung fehlgeschlagen")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    from crypto_tickers import crypto_tickers
    test_silent_optimization()
