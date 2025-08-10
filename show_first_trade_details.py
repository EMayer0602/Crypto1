#!/usr/bin/env python3
"""
Erster Trade - Details für Fusion Eingabe
========================================

Zeigt Details des ersten Trades für manuelle Eingabe in Bitpanda Fusion.
Keine Automatisierung - nur die genauen Werte zum Abtippen.

"""

import os
import pandas as pd
from datetime import datetime

def main():
    print("🎯 ERSTER TRADE - FUSION EINGABE DETAILS")
    print("="*50)
    print("📋 Details für manuelle Eingabe in Bitpanda Fusion")
    print("❌ Trade wird NICHT automatisch gesendet!")
    print()
    
    # Lade ersten Trade
    trades_file = "TODAY_ONLY_trades_20250810_093857.csv"
    
    if not os.path.exists(trades_file):
        print(f"❌ Trades-Datei nicht gefunden: {trades_file}")
        return
    
    try:
        df = pd.read_csv(trades_file, delimiter=';')
        
        if len(df) == 0:
            print("❌ Keine Trades in Datei")
            return
        
        # Erster Trade (BTC Buy)
        first_trade = df.iloc[0]
        
        print("🔍 ERSTER TRADE DETAILS:")
        print("="*50)
        print(f"📊 Action: BUY (weil 'Open')")
        print(f"🪙 Crypto Pair: {first_trade['Ticker']}")
        print(f"📈 Quantity: {first_trade['Quantity']:.6f}")
        print(f"💰 Limit Price: €{first_trade['Limit Price']:.4f}")
        print(f"📍 Current Market Price: €{first_trade['Realtime Price Bitpanda']:.4f}")
        
        quantity = float(first_trade['Quantity'])
        limit_price = float(first_trade['Limit Price'])
        order_value = quantity * limit_price
        
        print(f"💵 Order Value: €{order_value:.2f}")
        print(f"📅 Date: {first_trade['Date']}")
        
        print("\n🌐 BITPANDA FUSION - MANUELLE EINGABE:")
        print("="*50)
        print("1. 🔗 Gehen Sie zu: https://fusion.bitpanda.com/")
        print("2. 🔐 Loggen Sie sich ein")
        print("3. 📈 Gehen Sie zum Trading-Bereich")
        print(f"4. 🪙 Wählen Sie Paar: {first_trade['Ticker']}")
        print("5. 🟢 Klicken Sie auf 'BUY'")
        print("6. ⚡ Wählen Sie 'Limit Order'")
        print(f"7. 📈 Geben Sie Quantity ein: {first_trade['Quantity']}")
        print(f"8. 💰 Geben Sie Limit Price ein: {first_trade['Limit Price']}")
        print("9. 🔍 PRÜFEN Sie alle Eingaben!")
        print("10. ❌ NICHT SENDEN - nur prüfen!")
        
        print(f"\n📋 ZUM KOPIEREN:")
        print("="*30)
        print(f"Pair: {first_trade['Ticker']}")
        print(f"Action: BUY")
        print(f"Type: Limit Order")
        print(f"Quantity: {first_trade['Quantity']}")
        print(f"Limit Price: {first_trade['Limit Price']}")
        print("="*30)
        
        print(f"\n💡 WICHTIGE HINWEISE:")
        print(f"   🎯 Dies ist der erste von {len(df)} heutigen Trades")
        print(f"   📊 Order Value: €{order_value:.2f}")
        print(f"   ⚠️ Limit Price ist {((limit_price / float(first_trade['Realtime Price Bitpanda']) - 1) * 100):+.2f}% vom Marktpreis")
        print(f"   🔍 Prüfen Sie den Preis bevor Sie senden!")
        print(f"   ❌ Script sendet NICHT automatisch!")
        
        # Zeige auch die nächsten paar Trades
        if len(df) > 1:
            print(f"\n📋 NÄCHSTE TRADES (zur Info):")
            print("-"*30)
            for i in range(1, min(4, len(df))):
                trade = df.iloc[i]
                action = "BUY" if i % 2 == 0 else "SELL"  # Vereinfacht
                print(f"{i+1}. {action} {trade['Quantity']:.6f} {trade['Ticker']} @ €{trade['Limit Price']:.4f}")
        
        print(f"\n🎉 BEREIT FÜR MANUELLE EINGABE!")
        print(f"🔗 Öffnen Sie jetzt Bitpanda Fusion und geben Sie die Werte ein")
        
    except Exception as e:
        print(f"❌ Fehler: {str(e)}")

if __name__ == "__main__":
    main()
