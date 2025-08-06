#!/usr/bin/env python3

try:
    import yfinance as yf
    print('✅ yfinance verfügbar')
    
    # Teste BTC-EUR Daten
    ticker = yf.Ticker('BTC-EUR')
    hist = ticker.history(period='7d')
    print(f'Yahoo Finance BTC-EUR: {len(hist)} Tage')
    print('Letzte 3 Tage:')
    print(hist.tail(3)[['Close', 'Volume']])
    
except ImportError:
    print('❌ yfinance nicht installiert - installiere...')
    import subprocess
    subprocess.check_call(['pip', 'install', 'yfinance'])
    print('✅ yfinance installiert')
    
except Exception as e:
    print(f'❌ Fehler: {e}')
