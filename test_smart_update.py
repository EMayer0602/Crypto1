#!/usr/bin/env python3
"""
Test der intelligenten CSV-Update-Logik
"""

from smart_csv_update import check_csv_needs_update

def test_smart_update_logic():
    """Test der intelligenten Update-Logik für alle Tickers"""
    
    print("🧪 TESTE INTELLIGENTE UPDATE-LOGIK")
    print("="*50)
    
    from crypto_tickers import crypto_tickers
    
    for symbol in crypto_tickers.keys():
        try:
            today_needed, yesterday_needed, gaps_needed = check_csv_needs_update(symbol)
            
            print(f"\n📊 {symbol}:")
            print(f"   Heute Update nötig: {'✅ Ja' if today_needed else '❌ Nein'}")
            print(f"   Gestern Update nötig: {'✅ Ja' if yesterday_needed else '❌ Nein'}")
            print(f"   Gaps zu füllen: {len(gaps_needed) if gaps_needed else 0}")
            
            if gaps_needed:
                print(f"   Gap Dates: {gaps_needed[:5]}{'...' if len(gaps_needed) > 5 else ''}")
                
        except Exception as e:
            print(f"❌ {symbol}: Fehler - {e}")
            
    print(f"\n✅ ANALYSE ABGESCHLOSSEN")
    print("🎯 Nur notwendige Updates werden durchgeführt")

if __name__ == "__main__":
    test_smart_update_logic()
