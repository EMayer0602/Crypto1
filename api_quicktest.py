#!/usr/bin/env python3
"""
SCHNELLER API TEST
Prüft sofort, ob Ihr API Key funktioniert
"""

from bitpanda_secure_api import get_api_key_safely
import requests

print("BITPANDA API SCHNELLTEST")
print("=" * 40)

api_key = get_api_key_safely()
print(f"API Key gefunden: {'JA' if api_key else 'NEIN'}")

if api_key:
    print(f"API Key (gekürzt): {api_key[:8]}...{api_key[-4:]}")
    
    headers = {"X-API-KEY": api_key}
    
    try:
        response = requests.get("https://api.bitpanda.com/v1/account", 
                              headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API FUNKTIONIERT!")
            data = response.json()
            print(f"Account: {data.get('data', {}).get('email', 'Unknown')}")
        elif response.status_code == 401:
            print("❌ API KEY UNGÜLTIG")
        elif response.status_code == 403:
            print("🔒 PREMIUM ACCOUNT ERFORDERLICH")
        else:
            print(f"⚠️ UNBEKANNT: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ FEHLER: {e}")
else:
    print("❌ KEIN API KEY GEFUNDEN")

print("\nFAZIT:")
if api_key:
    print("1. API Key ist vorhanden")
    print("2. Testen Sie Ihren Bitpanda Account Typ")
    print("3. Eventuell Premium/Pro Account erforderlich")
else:
    print("1. Erstellen Sie einen API Key in Bitpanda")
    print("2. Fügen Sie ihn zur .env Datei hinzu")

print("ABGESCHLOSSEN")
