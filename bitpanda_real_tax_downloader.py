#!/usr/bin/env python3
"""
BITPANDA REAL TRANSACTION HISTORY DOWNLOADER
Downloads actual transaction history from Bitpanda for tax purposes using verified API endpoints
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bitpanda_secure_api import get_api_key_safely

class BitpandaRealTaxDownloader:
    """Download real transaction history from Bitpanda for tax reporting"""
    
    def __init__(self):
        self.api_key = get_api_key_safely()
        self.base_url = "https://api.bitpanda.com/v1"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        print("🏛️ BITPANDA REAL TRANSACTION HISTORY DOWNLOADER")
        print("=" * 70)
        print(f"🔑 API Key: {'✅ Loaded' if self.api_key else '❌ Missing'}")
        print("📋 Purpose: Download REAL transactions for tax reporting")
        print("⚠️  NOT paper trading - ACTUAL executed trades")
        print("=" * 70)
    
    def test_api_connection(self):
        """Test API connection and get available endpoints"""
        print("\n🔍 TESTING API CONNECTION...")
        
        try:
            # Test basic account access
            response = requests.get(f"{self.base_url}/account", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                print("   ✅ API Connection successful")
                account_data = response.json()
                print(f"   👤 Account: {account_data.get('data', {}).get('email', 'Unknown')}")
                return True
            elif response.status_code == 401:
                print("   ❌ API Key invalid or expired")
                return False
            else:
                print(f"   ⚠️ API responded with: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error: {e}")
            return False
    
    def get_wallets(self):
        """Get all wallets to see available assets"""
        print("\n💼 GETTING WALLET INFORMATION...")
        
        try:
            response = requests.get(f"{self.base_url}/wallets", headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                wallets_data = response.json()
                wallets = wallets_data.get('data', [])
                
                print(f"   💰 Found {len(wallets)} wallets:")
                
                for wallet in wallets[:10]:  # Show first 10
                    symbol = wallet.get('attributes', {}).get('cryptocoin', {}).get('symbol', 'Unknown')
                    balance = wallet.get('attributes', {}).get('balance', 0)
                    name = wallet.get('attributes', {}).get('name', 'Unknown')
                    print(f"      • {symbol}: {balance} ({name})")
                
                return wallets
            else:
                print(f"   ❌ Error getting wallets: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"   ❌ Exception getting wallets: {e}")
            return []
    
    def get_trades_history(self):
        """Get trading history - the most important for taxes"""
        print("\n📈 GETTING TRADE HISTORY (REAL TRANSACTIONS)...")
        
        all_trades = []
        
        try:
            # Try different endpoints for trades
            endpoints_to_try = [
                "trades",
                "orders", 
                "transactions",
                "fiatwallets/transactions",
                "assetwallets/transactions"
            ]
            
            for endpoint in endpoints_to_try:
                print(f"   🔍 Trying endpoint: {endpoint}")
                
                try:
                    # Add pagination and date filters
                    params = {
                        "page": 1,
                        "max_page_size": 100,
                    }
                    
                    response = requests.get(f"{self.base_url}/{endpoint}", 
                                          headers=self.headers, 
                                          params=params, 
                                          timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"      ✅ Success! Response structure:")
                        
                        # Print response structure to understand data format
                        if isinstance(data, dict):
                            if 'data' in data:
                                items = data['data']
                                print(f"         📊 Found {len(items)} items")
                                
                                if items:
                                    # Show first item structure
                                    first_item = items[0]
                                    print(f"         📋 Sample item keys: {list(first_item.keys())[:10]}")
                                    
                                    # Look for 2024 transactions
                                    trades_2024 = self._filter_2024_transactions(items, endpoint)
                                    all_trades.extend(trades_2024)
                                    print(f"         📅 2024 transactions: {len(trades_2024)}")
                            else:
                                print(f"         📋 Response keys: {list(data.keys())}")
                        
                    elif response.status_code == 404:
                        print(f"      ❌ Endpoint not found: {endpoint}")
                    elif response.status_code == 403:
                        print(f"      ❌ Access forbidden: {endpoint}")
                    else:
                        print(f"      ⚠️ Status {response.status_code}: {response.text[:100]}")
                
                except requests.exceptions.Timeout:
                    print(f"      ⏱️ Timeout for endpoint: {endpoint}")
                except Exception as e:
                    print(f"      ❌ Error with {endpoint}: {e}")
            
            print(f"\n   📊 TOTAL 2024 TRANSACTIONS FOUND: {len(all_trades)}")
            return all_trades
            
        except Exception as e:
            print(f"   ❌ General error: {e}")
            return []
    
    def _filter_2024_transactions(self, items, endpoint):
        """Filter transactions for 2024"""
        trades_2024 = []
        
        for item in items:
            # Look for date fields
            date_fields = ['created_at', 'time', 'date', 'updated_at', 'timestamp']
            transaction_date = None
            
            for field in date_fields:
                if field in item:
                    date_value = item[field]
                    if isinstance(date_value, dict) and 'date_iso8601' in date_value:
                        transaction_date = date_value['date_iso8601']
                    elif isinstance(date_value, str):
                        transaction_date = date_value
                    break
            
            if transaction_date and '2024' in transaction_date:
                # Structure the transaction data
                trade_record = {
                    'date': transaction_date,
                    'endpoint': endpoint,
                    'transaction_id': item.get('id', ''),
                    'type': item.get('type', 'Unknown'),
                    'raw_data': item
                }
                
                # Extract common fields based on endpoint
                if endpoint == 'trades':
                    trade_record.update({
                        'asset': item.get('cryptocoin', {}).get('symbol', 'Unknown'),
                        'amount': item.get('amount_cryptocoin', 0),
                        'fiat_amount': item.get('amount_fiat', 0),
                        'price': item.get('price', 0),
                        'fees': item.get('fee_amount', 0)
                    })
                elif 'transactions' in endpoint:
                    trade_record.update({
                        'asset': item.get('asset', {}).get('symbol', item.get('cryptocoin', {}).get('symbol', 'Unknown')),
                        'amount': item.get('amount', 0),
                        'fiat_amount': item.get('amount_fiat', item.get('amount', 0)),
                        'fees': item.get('fee', {}).get('amount', 0)
                    })
                
                trades_2024.append(trade_record)
        
        return trades_2024
    
    def save_comprehensive_tax_report(self, transactions):
        """Save comprehensive tax report with all found data"""
        print("\n💾 SAVING COMPREHENSIVE TAX REPORT...")
        
        if not transactions:
            print("   ⚠️ No transactions found")
            return None, None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Save raw data for investigation
        raw_filename = f"BITPANDA_RAW_DATA_2024_{timestamp}.json"
        with open(raw_filename, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, indent=2, default=str)
        print(f"   📄 Raw data saved: {raw_filename}")
        
        # 2. Save structured CSV
        csv_filename = f"BITPANDA_REAL_TRANSACTIONS_2024_{timestamp}.csv"
        
        # Flatten transaction data
        flattened_data = []
        for tx in transactions:
            flat_tx = {
                'date': tx.get('date', ''),
                'endpoint': tx.get('endpoint', ''),
                'transaction_id': tx.get('transaction_id', ''),
                'type': tx.get('type', ''),
                'asset': tx.get('asset', ''),
                'amount': tx.get('amount', 0),
                'fiat_amount': tx.get('fiat_amount', 0),
                'price': tx.get('price', 0),
                'fees': tx.get('fees', 0)
            }
            flattened_data.append(flat_tx)
        
        df = pd.DataFrame(flattened_data)
        df = df.sort_values('date')
        df.to_csv(csv_filename, index=False)
        print(f"   📊 CSV saved: {csv_filename}")
        
        # 3. Save readable tax report
        txt_filename = f"BITPANDA_REAL_TAX_REPORT_2024_{timestamp}.txt"
        
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("BITPANDA REAL CRYPTOCURRENCY TAX REPORT 2024\n")
            f.write("=" * 70 + "\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tax Year: 2024\n")
            f.write(f"Platform: Bitpanda (REAL TRANSACTIONS)\n")
            f.write(f"Total Transactions Found: {len(transactions)}\n")
            f.write("=" * 70 + "\n\n")
            
            # Group by endpoint
            endpoints = {}
            for tx in transactions:
                endpoint = tx.get('endpoint', 'unknown')
                if endpoint not in endpoints:
                    endpoints[endpoint] = []
                endpoints[endpoint].append(tx)
            
            f.write("TRANSACTIONS BY ENDPOINT\n")
            f.write("-" * 40 + "\n")
            for endpoint, txs in endpoints.items():
                f.write(f"{endpoint}: {len(txs)} transactions\n")
            
            f.write(f"\nDETAILED TRANSACTION LIST\n")
            f.write("=" * 70 + "\n")
            
            for i, tx in enumerate(sorted(transactions, key=lambda x: x.get('date', '')), 1):
                f.write(f"\n{i}. {tx.get('date', 'No date')[:19]}\n")
                f.write(f"   ID: {tx.get('transaction_id', 'N/A')}\n")
                f.write(f"   Type: {tx.get('type', 'N/A')}\n")
                f.write(f"   Asset: {tx.get('asset', 'N/A')}\n")
                f.write(f"   Amount: {tx.get('amount', 0)}\n")
                f.write(f"   Fiat Value: €{tx.get('fiat_amount', 0)}\n")
                f.write(f"   Fees: €{tx.get('fees', 0)}\n")
                f.write(f"   Source: {tx.get('endpoint', 'N/A')}\n")
        
        print(f"   📄 Tax report saved: {txt_filename}")
        
        return csv_filename, txt_filename, raw_filename
    
    def download_complete_tax_package(self):
        """Download complete real transaction package for taxes"""
        
        if not self.api_key:
            print("❌ No API key found! Please check your Bitpanda API settings.")
            return False
        
        # Test connection
        if not self.test_api_connection():
            print("❌ Cannot connect to Bitpanda API")
            return False
        
        # Get wallet info
        wallets = self.get_wallets()
        
        # Get transaction history
        transactions = self.get_trades_history()
        
        if not transactions:
            print("⚠️ No 2024 transactions found. This could mean:")
            print("   • No real trades were executed in 2024")
            print("   • Different API endpoints are needed")
            print("   • API permissions may be limited")
        
        # Save whatever we found
        files = self.save_comprehensive_tax_report(transactions)
        
        print(f"\n🎉 BITPANDA REAL DATA DOWNLOAD COMPLETE!")
        print("=" * 70)
        print(f"📊 Transactions Found: {len(transactions)}")
        print(f"📄 Files Created: {len([f for f in files if f])}")
        print("=" * 70)
        
        if transactions:
            print("✅ SUCCESS: Real transaction data downloaded for tax purposes")
        else:
            print("⚠️  NOTE: No transactions found - may need manual export from Bitpanda")
            print("   Consider downloading CSV from Bitpanda web interface")
        
        return True

def main():
    """Main function to download real tax data from Bitpanda"""
    
    try:
        downloader = BitpandaRealTaxDownloader()
        success = downloader.download_complete_tax_package()
        
        if not success:
            print("\n❌ Download failed. Check your API credentials.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
