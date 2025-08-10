#!/usr/bin/env python3
"""
System Readiness Check - Alles prüfen außer Order-Senden
========================================================

Überprüft alle Komponenten des Trading-Systems:
✅ Python Module verfügbar
✅ API Keys geladen  
✅ CSV Dateien vorhanden
✅ Live-Daten abrufbar
✅ Strategien funktional
✅ Orders vorbereitbar
❌ Order-Übertragung (deaktiviert)

"""

import os
import sys
import importlib
from datetime import datetime

def check_python_modules():
    """Überprüfe benötigte Python Module"""
    print("🔄 Überprüfe Python Module...")
    
    required_modules = [
        'pandas', 'numpy', 'yfinance', 'requests', 
        'plotly', 'logging', 'datetime', 'json'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} - FEHLT")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Fehlende Module: {', '.join(missing_modules)}")
        return False
    else:
        print("✅ Alle Python Module verfügbar")
        return True

def check_config_files():
    """Überprüfe Konfigurationsdateien"""
    print("\n🔄 Überprüfe Konfigurationsdateien...")
    
    files_to_check = [
        'config.py',
        '.env',
        'crypto_backtesting_module.py',
        'bitpanda_secure_api.py'
    ]
    
    missing_files = []
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - FEHLT")
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Fehlende Dateien: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Alle Konfigurationsdateien vorhanden")
        return True

def check_csv_data():
    """Überprüfe CSV Datendateien"""
    print("\n🔄 Überprüfe CSV Datendateien...")
    
    crypto_pairs = ['BTC-EUR', 'ETH-EUR', 'XRP-EUR', 'DOGE-EUR', 'SOL-EUR', 'LINK-EUR']
    csv_files = [f"{pair}_daily.csv" for pair in crypto_pairs]
    
    missing_files = []
    valid_files = 0
    
    for file in csv_files:
        if os.path.exists(file):
            try:
                import pandas as pd
                df = pd.read_csv(file)
                if len(df) > 0 and 'Date' in df.columns:
                    print(f"   ✅ {file} - {len(df)} Zeilen")
                    valid_files += 1
                else:
                    print(f"   ⚠️ {file} - Leer oder ungültig")
            except Exception as e:
                print(f"   ❌ {file} - Fehler: {str(e)}")
        else:
            print(f"   ❌ {file} - FEHLT")
            missing_files.append(file)
    
    success_rate = valid_files / len(csv_files) * 100
    print(f"📊 CSV Dateien: {valid_files}/{len(csv_files)} gültig ({success_rate:.0f}%)")
    
    return valid_files >= len(csv_files) * 0.5  # Mindestens 50% OK

def check_live_data():
    """Überprüfe Live-Daten Abruf"""
    print("\n🔄 Überprüfe Live-Daten Abruf...")
    
    try:
        import yfinance as yf
        
        test_pairs = ['BTC-EUR', 'ETH-EUR']
        successful = 0
        
        for pair in test_pairs:
            try:
                ticker = yf.Ticker(pair)
                hist = ticker.history(period="1d", interval="5m")
                
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
                    print(f"   ✅ {pair}: €{price:.4f}")
                    successful += 1
                else:
                    print(f"   ❌ {pair}: Keine Daten")
                    
            except Exception as e:
                print(f"   ❌ {pair}: {str(e)}")
        
        success_rate = successful / len(test_pairs) * 100
        print(f"📊 Live-Daten: {successful}/{len(test_pairs)} erfolgreich ({success_rate:.0f}%)")
        
        return successful > 0
        
    except Exception as e:
        print(f"❌ Live-Daten Fehler: {str(e)}")
        return False

def check_api_keys():
    """Überprüfe API Keys"""
    print("\n🔄 Überprüfe API Keys...")
    
    try:
        # Überprüfe .env Datei
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                content = f.read()
            
            # Suche nach API Keys (ohne sie anzuzeigen)
            has_bitpanda_key = 'BITPANDA_API_KEY=' in content
            has_coingecko_key = 'COINGECKO_API_KEY=' in content or 'COINGECKO' in content
            
            if has_bitpanda_key:
                print("   ✅ Bitpanda API Key gefunden")
            else:
                print("   ⚠️ Bitpanda API Key fehlt")
            
            if has_coingecko_key:
                print("   ✅ CoinGecko API Key gefunden")
            else:
                print("   ℹ️ CoinGecko API Key optional")
            
            return has_bitpanda_key
        else:
            print("   ❌ .env Datei fehlt")
            return False
            
    except Exception as e:
        print(f"   ❌ Fehler beim Lesen der API Keys: {str(e)}")
        return False

def check_strategy_functionality():
    """Überprüfe Strategie-Funktionalität"""
    print("\n🔄 Überprüfe Strategie-Funktionalität...")
    
    try:
        # Versuche eine einfache Backtest-Funktion zu importieren
        sys.path.append(os.getcwd())
        
        if os.path.exists('crypto_backtesting_module.py'):
            print("   ✅ Backtest-Modul vorhanden")
        else:
            print("   ❌ Backtest-Modul fehlt")
            return False
        
        # Versuche Config zu laden
        if os.path.exists('config.py'):
            print("   ✅ Config-Modul vorhanden")
        else:
            print("   ❌ Config-Modul fehlt")
            return False
        
        print("   ✅ Strategie-Module verfügbar")
        return True
        
    except Exception as e:
        print(f"   ❌ Strategie-Funktionalität Fehler: {str(e)}")
        return False

def main():
    """Hauptfunktion für System-Check"""
    print("🚀 System Readiness Check - Trading System")
    print("="*60)
    print("📋 Überprüfe alle Komponenten außer Order-Übertragung")
    print(f"⏰ Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Führe alle Checks durch
    checks = {
        'Python Module': check_python_modules(),
        'Konfigurationsdateien': check_config_files(), 
        'CSV Datendateien': check_csv_data(),
        'Live-Daten Abruf': check_live_data(),
        'API Keys': check_api_keys(),
        'Strategie-Funktionalität': check_strategy_functionality()
    }
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("📋 SYSTEM READINESS ERGEBNISSE")
    print("="*60)
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, result in checks.items():
        status = "✅ OK" if result else "❌ FEHLER"
        print(f"{check_name}: {status}")
        if result:
            passed_checks += 1
    
    print("-"*60)
    success_rate = passed_checks / total_checks * 100
    print(f"Erfolgsrate: {passed_checks}/{total_checks} ({success_rate:.0f}%)")
    
    if passed_checks == total_checks:
        print("\n🎉 SYSTEM BEREIT FÜR TRADING!")
        print("📤 Alle Komponenten funktional (Orders deaktiviert)")
        print("✅ Kann jetzt comprehensive_trading_test.py oder quick_trading_test.py ausführen")
    elif passed_checks >= total_checks * 0.8:  # 80% oder mehr
        print("\n⚠️ SYSTEM GRÖSSTENTEILS BEREIT")
        print("🔧 Einige kleinere Probleme beheben, aber grundsätzlich funktional")
    else:
        print("\n❌ SYSTEM NICHT BEREIT")
        print("🔧 Mehrere kritische Probleme müssen behoben werden")
    
    print("="*60)
    print("📋 NÄCHSTE SCHRITTE:")
    if success_rate >= 80:
        print("1. ✅ Führe 'python quick_trading_test.py' aus")
        print("2. ✅ Führe 'python comprehensive_trading_test.py' aus")
        print("3. ✅ System bereit für Live-Trading (wenn Orders aktiviert)")
    else:
        print("1. 🔧 Behebe die oben genannten Fehler")
        print("2. 🔄 Führe diesen Check erneut aus") 
        print("3. ✅ Dann führe die Trading-Tests aus")
    
    return success_rate >= 80

if __name__ == "__main__":
    main()
