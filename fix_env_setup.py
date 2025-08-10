#!/usr/bin/env python3
"""
SICHERER .ENV SETUP HELPER
Behebt Windows-Encoding-Probleme und erstellt sichere .env
"""

import os
import sys
from pathlib import Path

def fix_env_encoding():
    """
    Repariert .env Encoding-Probleme
    """
    print("🔧 ENV ENCODING REPARATUR")
    print("-" * 40)
    
    env_file = Path('.env')
    backup_file = Path('.env.backup')
    
    if env_file.exists():
        print("📁 Bestehende .env gefunden")
        
        # Backup erstellen
        if backup_file.exists():
            backup_file.unlink()
        env_file.rename(backup_file)
        print("💾 Backup erstellt: .env.backup")
    
    # Sichere neue .env erstellen
    safe_content = '''# SICHERE .ENV DATEI - Windows ASCII kompatibel
# Keine Unicode-Zeichen, kein BOM

# TRAGE HIER DEINEN VIERTEN NEUEN API-KEY EIN:
BITPANDA_API_KEY=YOUR_NEW_API_KEY_HERE

# Konfiguration
BITPANDA_SANDBOX=true
TRADING_MODE=paper
DEBUG_MODE=true

# Optional
MAX_DAILY_TRADES=50
PORTFOLIO_LIMIT=16000
'''
    
    with open('.env', 'w', encoding='ascii') as f:
        f.write(safe_content)
    
    print("✅ Neue sichere .env erstellt (ASCII-Encoding)")
    print("")
    print("📝 NÄCHSTE SCHRITTE:")
    print("1. Öffne .env in Notepad")
    print("2. Ersetze YOUR_NEW_API_KEY_HERE mit deinem VIERTEN API-Key")
    print("3. Speichere als normaler Text (nicht UTF-8)")
    print("4. Teste mit: python test_env_setup.py")

def test_env_loading():
    """
    Teste .env Laden
    """
    print("\n🧪 TESTE .ENV LADEN")
    print("-" * 40)
    
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env Datei nicht gefunden")
        return False
    
    # Test verschiedene Encodings
    encodings = ['ascii', 'utf-8', 'utf-8-sig', 'cp1252', 'latin1']
    
    for encoding in encodings:
        try:
            with open('.env', 'r', encoding=encoding) as f:
                content = f.read()
                print(f"✅ {encoding}: OK ({len(content)} Zeichen)")
                
                # Suche API-Key
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('BITPANDA_API_KEY=') and not line.startswith('#'):
                        api_key = line.split('=', 1)[1].strip()
                        if api_key and api_key != 'YOUR_NEW_API_KEY_HERE':
                            print(f"🔑 API-Key gefunden: {api_key[:10]}...{api_key[-10:]}")
                            return True
                        else:
                            print("⚠️ API-Key ist Platzhalter - trage echten Key ein")
                            return False
                break
                
        except Exception as e:
            print(f"❌ {encoding}: {e}")
    
    return False

def create_env_safely():
    """
    Erstelle .env sicher mit Benutzer-Input
    """
    print("\n🔒 SICHERE .ENV ERSTELLUNG")
    print("-" * 40)
    
    print("⚠️ WICHTIG: Gib NIEMALS deinen API-Key im Terminal ein!")
    print("📝 Stattdessen:")
    print("")
    print("1. Erstelle neuen API-Key bei Bitpanda Pro")
    print("2. Kopiere ihn in die Zwischenablage")  
    print("3. Öffne .env in Notepad")
    print("4. Ersetze YOUR_NEW_API_KEY_HERE")
    print("5. Speichere als normalen Text")
    print("")
    
    choice = input("Möchtest du die sichere .env Vorlage erstellen? (j/n): ")
    
    if choice.lower() in ['j', 'ja', 'y', 'yes']:
        fix_env_encoding()
        return True
    else:
        print("❌ Setup abgebrochen")
        return False

def main():
    """
    Haupt-Setup-Funktion
    """
    print("🔒 SICHERER BITPANDA API-KEY SETUP")
    print("=" * 50)
    
    print("\n🚨 SICHERHEITSKRITISCH:")
    print("   Du hast bereits 3 API-Keys kompromittiert!")
    print("   1. 5b295003... (hoffentlich widerrufen)")
    print("   2. da0ec951... (hoffentlich widerrufen)")
    print("   3. 608e9843... (SOFORT WIDERRUFEN!)")
    print("")
    
    # Schritt 1: Encoding reparieren
    if not test_env_loading():
        print("\n❌ .env Problem erkannt - repariere...")
        create_env_safely()
    else:
        print("\n✅ .env lädt korrekt")
    
    # Schritt 2: API-Test
    print("\n🧪 TESTE SICHERE API-INTEGRATION")
    try:
        from bitpanda_secure_api import get_api_key_safely
        api_key = get_api_key_safely()
        
        if api_key:
            print("✅ API-Key erfolgreich geladen!")
            print(f"🔑 Key: {api_key[:10]}...{api_key[-10:]}")
        else:
            print("⚠️ Kein API-Key - Paper Trading Modus")
    except Exception as e:
        print(f"❌ Import-Fehler: {e}")
    
    print("\n🎯 NÄCHSTE SCHRITTE:")
    print("1. ✅ Alle alten API-Keys widerrufen")
    print("2. ✅ Neuen API-Key erstellen") 
    print("3. ✅ In .env eintragen (ASCII-Format)")
    print("4. ✅ Testen mit: python bitpanda_live_integration.py")

if __name__ == "__main__":
    main()
