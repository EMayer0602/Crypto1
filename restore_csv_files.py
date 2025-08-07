#!/usr/bin/env python3
"""
Script zum Wiederherstellen aller benötigten CSV-Dateien
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Ticker-Liste basierend auf crypto_tickers.py
tickers = ["BTC-EUR", "ETH-EUR", "DOGE-EUR", "SOL-EUR", "LINK-EUR", "XRP-EUR"]

def download_and_save_csv(ticker):
    """Lädt Daten herunter und speichert als CSV"""
    try:
        print(f"📥 Lade {ticker} Daten...")
        
        # 1 Jahr Daten holen
        end_date = datetime.now()
        start_date = end_date - timedelta(days=400)  # Mehr als 1 Jahr für Sicherheit
        
        # Yahoo Finance Daten holen
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date, interval='1d')
        
        if df.empty:
            print(f"❌ Keine Daten für {ticker} von Yahoo Finance")
            return False
            
        # Index als Date column, nur OHLCV behalten
        df.index.name = 'Date'
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # CSV speichern
        filename = f"{ticker}_daily.csv"
        df.to_csv(filename)
        
        print(f"✅ {filename} erstellt mit {len(df)} Zeilen")
        print(f"   Zeitraum: {df.index.min().date()} bis {df.index.max().date()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei {ticker}: {e}")
        return False

def main():
    print("🚀 RESTORE CSV FILES")
    print("=" * 50)
    
    success_count = 0
    
    for ticker in tickers:
        if download_and_save_csv(ticker):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"✅ {success_count}/{len(tickers)} CSV-Dateien erstellt")
    
    if success_count == len(tickers):
        print("🎉 Alle CSV-Dateien erfolgreich wiederhergestellt!")
    else:
        print("⚠️ Einige CSV-Dateien konnten nicht erstellt werden")

if __name__ == "__main__":
    main()
