#!/usr/bin/env python3
"""
BITPANDA API DIAGNOSE TOOL
Prüft API-Zugang, Kontotyp und verfügbare Endpunkte
"""

import requests
import json
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bitpanda_secure_api import get_api_key_safely

class BitpandaAPIDiagnose:
    """Diagnose Bitpanda API Zugang und Berechtigungen"""
    
    def __init__(self):
        self.api_key = get_api_key_safely()
        self.base_url = "https://api.bitpanda.com/v1"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        } if self.api_key else {}
        
        print("🔍 BITPANDA API DIAGNOSE TOOL")
        print("=" * 70)
        print(f"🔑 API Key Status: {'✅ Geladen' if self.api_key else '❌ Nicht gefunden'}")
        if self.api_key:
            print(f"🔑 API Key (gekürzt): {self.api_key[:8]}...{self.api_key[-4:]}")
        print("=" * 70)
    
    def test_basic_connection(self):
        """Test grundlegende Verbindung"""
        print("\n🌐 TEST 1: GRUNDLEGENDE VERBINDUNG")
        print("-" * 50)
        
        if not self.api_key:
            print("❌ Kein API Key - Verbindung nicht möglich")
            return False
        
        try:
            # Test einfachste Endpunkt
            response = requests.get(f"{self.base_url}/account", 
                                  headers=self.headers, 
                                  timeout=10)
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ Grundlegende Verbindung erfolgreich")
                return True
            elif response.status_code == 401:
                print("❌ Authentifizierung fehlgeschlagen")
                print("💡 Mögliche Ursachen:")
                print("   • API Key ungültig oder abgelaufen")
                print("   • API Key hat keine Berechtigung")
                print("   • Falscher API Key Typ")
                return False
            elif response.status_code == 403:
                print("❌ Zugriff verweigert")
                print("💡 Mögliche Ursachen:")
                print("   • Premium Account erforderlich")
                print("   • API Trading nicht aktiviert")
                print("   • Insufficient permissions")
                return False
            else:
                print(f"⚠️ Unerwarteter Status Code: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
        except Exception as e:
            print(f"❌ Verbindungsfehler: {e}")
            return False
    
    def check_account_type(self):
        """Prüfe Kontotyp und Berechtigungen"""
        print("\n👤 TEST 2: KONTOTYP UND BERECHTIGUNGEN")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/account", 
                                  headers=self.headers, 
                                  timeout=10)
            
            if response.status_code == 200:
                account_data = response.json()
                data = account_data.get('data', {})
                
                print("✅ Account Information:")
                print(f"   📧 Email: {data.get('email', 'N/A')}")
                print(f"   🆔 ID: {data.get('id', 'N/A')}")
                print(f"   🏛️ Company: {data.get('company_name', 'N/A')}")
                print(f"   ✅ Verified: {data.get('is_verified', 'N/A')}")
                
                # Prüfe spezielle Flags
                flags = data.get('flags', {})
                if flags:
                    print("🚩 Account Flags:")
                    for flag, value in flags.items():
                        print(f"   • {flag}: {value}")
                
                return data
            else:
                print(f"❌ Kann Account Info nicht abrufen: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Fehler bei Account Info: {e}")
            return None
    
    def test_trading_endpoints(self):
        """Teste verfügbare Trading Endpunkte"""
        print("\n📈 TEST 3: TRADING ENDPUNKTE")
        print("-" * 50)
        
        endpoints_to_test = [
            ("GET", "wallets", "Wallet Information"),
            ("GET", "orders", "Order History"),
            ("GET", "trades", "Trade History"), 
            ("POST", "orders", "Order Creation (TEST)"),
            ("GET", "assets", "Available Assets"),
            ("GET", "time", "Server Time"),
        ]
        
        available_endpoints = []
        
        for method, endpoint, description in endpoints_to_test:
            try:
                url = f"{self.base_url}/{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, headers=self.headers, timeout=5)
                elif method == "POST" and endpoint == "orders":
                    # Nicht wirklich ausführen, nur testen ob Endpunkt existiert
                    response = requests.post(url, headers=self.headers, 
                                           json={"test": "true"}, timeout=5)
                
                print(f"📡 {method} {endpoint}: ", end="")
                
                if response.status_code == 200:
                    print(f"✅ Verfügbar ({description})")
                    available_endpoints.append(endpoint)
                elif response.status_code == 401:
                    print(f"❌ Nicht autorisiert")
                elif response.status_code == 403:
                    print(f"🔒 Premium erforderlich")
                elif response.status_code == 404:
                    print(f"❌ Nicht gefunden")
                elif response.status_code == 400:
                    if endpoint == "orders" and method == "POST":
                        print(f"✅ Endpunkt existiert (Bad Request = normal für Test)")
                        available_endpoints.append(endpoint)
                    else:
                        print(f"⚠️ Bad Request")
                else:
                    print(f"⚠️ Status {response.status_code}")
                    
            except Exception as e:
                print(f"📡 {method} {endpoint}: ❌ Fehler - {e}")
        
        print(f"\n📊 Verfügbare Endpunkte: {len(available_endpoints)}")
        return available_endpoints
    
    def check_bitpanda_pro_vs_standard(self):
        """Prüfe ob Bitpanda Pro oder Standard"""
        print("\n🏛️ TEST 4: BITPANDA STANDARD vs PRO/FUSION")
        print("-" * 50)
        
        # Test auf Bitpanda Pro API
        pro_headers = self.headers.copy() if self.headers else {}
        
        try:
            # Bitpanda Pro verwendet andere URLs
            pro_url = "https://api.exchange.bitpanda.com/public/v1/time"
            
            pro_response = requests.get(pro_url, timeout=5)
            
            if pro_response.status_code == 200:
                print("✅ Bitpanda Pro API erreichbar")
                print("💡 Für Trading könnte Bitpanda Pro besser geeignet sein")
            else:
                print("⚠️ Bitpanda Pro API nicht verfügbar")
            
            # Test Standard API
            standard_url = "https://api.bitpanda.com/v1/time"
            standard_response = requests.get(standard_url, headers=self.headers, timeout=5)
            
            if standard_response.status_code == 200:
                print("✅ Bitpanda Standard API erreichbar")
            else:
                print("❌ Bitpanda Standard API nicht verfügbar")
            
        except Exception as e:
            print(f"❌ Fehler bei API Vergleich: {e}")
    
    def get_api_requirements_info(self):
        """Zeige API Anforderungen und Lösungen"""
        print("\n💡 BITPANDA API ANFORDERUNGEN & LÖSUNGEN")
        print("=" * 70)
        
        print("🔑 API KEY TYPEN:")
        print("   1️⃣ Read-Only API Key:")
        print("      • Kann nur Daten lesen (Wallets, History)")
        print("      • Kann KEINE Trades ausführen")
        print("      • Meist kostenlos verfügbar")
        print()
        print("   2️⃣ Trading API Key:")
        print("      • Kann Trades ausführen")
        print("      • Erfordert meist Premium/Pro Account")
        print("      • Höhere Sicherheitsanforderungen")
        print()
        
        print("🏛️ BITPANDA KONTOTYPEN:")
        print("   📱 Bitpanda Standard (Consumer):")
        print("      • Begrenzte API Funktionen")
        print("      • Meist nur Read-Only")
        print("      • Paper Trading möglicherweise nicht verfügbar")
        print()
        print("   💼 Bitpanda Pro/Exchange:")
        print("      • Vollständige Trading API")
        print("      • Lower fees")
        print("      • Bessere API Limits")
        print()
        print("   🔄 Bitpanda Fusion:")
        print("      • Neues Produkt für institutionelle Kunden")
        print("      • Erweiterte API Features")
        print("      • Möglicherweise Paper Trading Support")
        print()
        
        print("🎯 EMPFOHLENE LÖSUNGEN:")
        print("   1️⃣ Prüfen Sie Ihren Bitpanda Account Typ")
        print("   2️⃣ Upgrade zu Bitpanda Pro erwägen")
        print("   3️⃣ Trading API Key mit Write-Berechtigung erstellen")
        print("   4️⃣ Paper Trading in Account Settings aktivieren")
        print("   5️⃣ Alternative: Andere Exchanges mit besserer API")
    
    def run_full_diagnosis(self):
        """Führe komplette Diagnose aus"""
        
        # Test 1: Grundverbindung
        connection_ok = self.test_basic_connection()
        
        # Test 2: Account Info
        account_info = self.check_account_type()
        
        # Test 3: Trading Endpunkte
        available_endpoints = self.test_trading_endpoints()
        
        # Test 4: Pro vs Standard
        self.check_bitpanda_pro_vs_standard()
        
        # Zeige Anforderungen
        self.get_api_requirements_info()
        
        # Fazit
        print("\n🎯 DIAGNOSE ZUSAMMENFASSUNG")
        print("=" * 70)
        
        if connection_ok:
            print("✅ API Verbindung funktioniert grundsätzlich")
        else:
            print("❌ API Verbindung fehlgeschlagen")
            print("💡 Problem: API Key oder Berechtigung")
        
        if len(available_endpoints) > 0:
            print(f"✅ {len(available_endpoints)} Endpunkte verfügbar")
        else:
            print("❌ Keine Trading Endpunkte verfügbar")
            print("💡 Problem: Premium Account oder Trading API erforderlich")
        
        # Spezifische Empfehlung
        print("\n🎯 SPEZIFISCHE EMPFEHLUNG FÜR SIE:")
        if not connection_ok:
            print("1. Prüfen Sie Ihren API Key in der .env Datei")
            print("2. Erstellen Sie einen neuen API Key in Bitpanda")
            print("3. Stellen Sie sicher, dass Trading-Berechtigung aktiviert ist")
        elif len(available_endpoints) == 0:
            print("1. Upgrade zu Bitpanda Pro erwägen")
            print("2. Trading API Key mit Write-Berechtigung erstellen")
            print("3. Paper Trading in Account aktivieren")
        else:
            print("1. System sollte funktionieren")
            print("2. Möglicherweise anderes Problem im Code")

def main():
    """Hauptfunktion"""
    
    try:
        diagnose = BitpandaAPIDiagnose()
        diagnose.run_full_diagnosis()
        
    except Exception as e:
        print(f"\n❌ Fehler in Diagnose: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
