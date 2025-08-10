#!/usr/bin/env python3
"""
SICHERE BITPANDA API KONFIGURATION
NIEMALS API-KEYS IN CODE SPEICHERN!
"""

import os
from pathlib import Path

def get_api_key_safely():
    """
    Sichere Methode um API-Key zu laden
    
    Priorität:
    1. Umgebungsvariable
    2. Sichere .env Datei (nicht in Git)
    3. Benutzer-Input (für Tests)
    """
    
    # Methode 1: Umgebungsvariable (EMPFOHLEN)
    api_key = os.getenv('BITPANDA_API_KEY')
    if api_key:
        print("✅ API-Key aus Umgebungsvariable geladen")
        return api_key
    
    # Methode 2: .env Datei (lokal, nicht in Git)
    env_file = Path('.env')
    if env_file.exists():
        try:
            # Windows-sicheres Encoding verwenden
            with open(env_file, 'r', encoding='utf-8-sig') as f:  # Handles BOM
                for line in f:
                    line = line.strip()
                    if line.startswith('BITPANDA_API_KEY=') and not line.startswith('#'):
                        api_key = line.split('=', 1)[1].strip()
                        if api_key and api_key != 'YOUR_FOURTH_NEW_API_KEY_HERE':
                            print("✅ API-Key aus .env Datei geladen")
                            return api_key
        except UnicodeDecodeError:
            # Fallback für Windows-Encoding-Probleme
            try:
                with open(env_file, 'r', encoding='cp1252') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('BITPANDA_API_KEY=') and not line.startswith('#'):
                            api_key = line.split('=', 1)[1].strip()
                            if api_key and api_key != 'YOUR_FOURTH_NEW_API_KEY_HERE':
                                print("✅ API-Key aus .env Datei geladen (Windows-Encoding)")
                                return api_key
            except Exception as inner_e:
                print(f"⚠️ Encoding-Fehler bei .env Datei: {inner_e}")
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der .env Datei: {e}")
    
    # Methode 3: Benutzer-Input (nur für Tests)
    print("⚠️ Kein API-Key in Umgebungsvariable oder .env gefunden")
    print("📝 Für Produktion: Umgebungsvariable BITPANDA_API_KEY setzen")
    
    return None  # Für Paper Trading ohne echte API

# SICHERE API KONFIGURATION
BITPANDA_SECURE_CONFIG = {
    'base_url': 'https://api.bitpanda.com/v1',
    'ticker_endpoint': 'ticker',
    'orders_endpoint': 'orders',
    'portfolio_endpoint': 'account/balances',
    
    # Sicherheitseinstellungen
    'timeout': 30,
    'max_retries': 3,
    'rate_limit_per_minute': 60,
    
    # Headers
    'headers': {
        'Content-Type': 'application/json',
        'User-Agent': 'CryptoTradingBot/1.0'
    }
}

def create_secure_api_url(endpoint: str, api_key: str = None) -> str:
    """
    Erstelle sichere API-URL
    
    Args:
        endpoint: API-Endpoint (z.B. 'ticker')
        api_key: API-Key (optional)
    
    Returns:
        Vollständige URL
    """
    base_url = BITPANDA_SECURE_CONFIG['base_url']
    url = f"{base_url}/{endpoint}"
    
    if api_key:
        url += f"?apikey={api_key}"
    
    return url

def setup_environment_variable():
    """
    Anleitung zum sicheren Setup der Umgebungsvariable
    """
    print("\n🔒 SICHERE API-KEY KONFIGURATION")
    print("=" * 50)
    
    print("\n1️⃣ WINDOWS (PowerShell):")
    print("   $env:BITPANDA_API_KEY = 'DEIN_NEUER_API_KEY'")
    print("   # Für permanent:")
    print("   [System.Environment]::SetEnvironmentVariable('BITPANDA_API_KEY', 'DEIN_NEUER_API_KEY', 'User')")
    
    print("\n2️⃣ .ENV DATEI (empfohlen für Entwicklung):")
    print("   Erstelle Datei '.env' im Projektordner:")
    print("   BITPANDA_API_KEY=DEIN_NEUER_API_KEY")
    print("   # .env wird automatisch von .gitignore ignoriert")
    
    print("\n3️⃣ NIEMALS:")
    print("   ❌ API-Key in Code hardcoden")
    print("   ❌ API-Key in Git committen") 
    print("   ❌ API-Key öffentlich posten")
    print("   ❌ API-Key in Screenshots zeigen")

def test_secure_api_connection():
    """
    Teste sichere API-Verbindung
    """
    print("\n🔍 TESTE SICHERE API-VERBINDUNG")
    print("-" * 40)
    
    api_key = get_api_key_safely()
    
    if not api_key:
        print("⚠️ Paper Trading Modus - keine echte API")
        return False
    
    try:
        import requests
        
        url = create_secure_api_url('ticker', api_key)
        
        # Sichere API-Anfrage mit Timeout
        response = requests.get(
            url, 
            headers=BITPANDA_SECURE_CONFIG['headers'],
            timeout=BITPANDA_SECURE_CONFIG['timeout']
        )
        
        if response.status_code == 200:
            print("✅ API-Verbindung erfolgreich")
            data = response.json()
            print(f"📊 {len(data)} Ticker-Daten erhalten")
            return True
        else:
            print(f"❌ API-Fehler: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Verbindungsfehler: {e}")
        return False

if __name__ == "__main__":
    print("🔒 BITPANDA SICHERE API KONFIGURATION")
    print("=" * 45)
    
    # Setup-Anleitung anzeigen
    setup_environment_variable()
    
    # API-Verbindung testen
    test_secure_api_connection()
    
    print(f"\n⚠️ WICHTIG:")
    print(f"   1. Alten API-Key SOFORT widerrufen")
    print(f"   2. Neuen API-Key erstellen") 
    print(f"   3. Als Umgebungsvariable setzen")
    print(f"   4. Niemals wieder in Code posten!")
