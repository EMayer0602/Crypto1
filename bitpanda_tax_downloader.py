#!/usr/bin/env python3
"""
BITPANDA TRANSACTION HISTORY DOWNLOADER
Downloads real transaction history from Bitpanda for tax purposes
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

class BitpandaTaxDownloader:
    """Download transaction history from Bitpanda for tax reporting"""
    
    def __init__(self):
        self.api_key = get_api_key_safely()
        self.base_url = "https://api.bitpanda.com/v1"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        print("🏛️ BITPANDA TAX TRANSACTION DOWNLOADER")
        print("=" * 60)
        print(f"🔑 API Key: {'✅ Loaded' if self.api_key else '❌ Missing'}")
        print("📋 Purpose: Download real transactions for tax reporting")
        print("=" * 60)
    
    def get_account_info(self):
        """Get account information"""
        print("\n👤 GETTING ACCOUNT INFORMATION...")
        
        try:
            response = requests.get(f"{self.base_url}/account", headers=self.headers)
            
            if response.status_code == 200:
                account_data = response.json()
                print(f"   ✅ Account ID: {account_data.get('data', {}).get('id', 'Unknown')}")
                print(f"   📧 Email: {account_data.get('data', {}).get('email', 'Unknown')}")
                return account_data
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return None
    
    def get_transactions_2024(self):
        """Download all transactions from 2024 for tax purposes"""
        print("\n💰 DOWNLOADING 2024 TRANSACTIONS...")
        
        all_transactions = []
        
        # Define 2024 date range
        start_date = "2024-01-01T00:00:00Z"
        end_date = "2024-12-31T23:59:59Z"
        
        try:
            # Get trades/orders
            print("   📈 Fetching trades...")
            trades = self._get_trades(start_date, end_date)
            if trades:
                all_transactions.extend(trades)
            
            # Get deposits/withdrawals
            print("   💳 Fetching deposits/withdrawals...")
            deposits = self._get_deposits_withdrawals(start_date, end_date)
            if deposits:
                all_transactions.extend(deposits)
            
            # Get fees
            print("   💸 Fetching fees...")
            fees = self._get_fees(start_date, end_date)
            if fees:
                all_transactions.extend(fees)
            
            print(f"   ✅ Total transactions downloaded: {len(all_transactions)}")
            return all_transactions
            
        except Exception as e:
            print(f"   ❌ Error downloading transactions: {e}")
            return []
    
    def _get_trades(self, start_date, end_date):
        """Get trading transactions"""
        trades = []
        
        try:
            params = {
                "from": start_date,
                "to": end_date,
                "max_page_size": 100
            }
            
            response = requests.get(f"{self.base_url}/trades", headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                trades_data = data.get('data', [])
                
                for trade in trades_data:
                    trade_record = {
                        'date': trade.get('time', {}).get('date_iso8601', ''),
                        'type': 'TRADE',
                        'asset': trade.get('cryptocoin', {}).get('symbol', 'Unknown'),
                        'amount': float(trade.get('amount_cryptocoin', 0)),
                        'price': float(trade.get('price', 0)),
                        'fiat_amount': float(trade.get('amount_fiat', 0)),
                        'fiat_currency': trade.get('fiat', {}).get('symbol', 'EUR'),
                        'side': trade.get('type', 'Unknown'),  # buy/sell
                        'fees': float(trade.get('fee_amount', 0)),
                        'trade_id': trade.get('id', ''),
                        'raw_data': trade
                    }
                    trades.append(trade_record)
                
                print(f"      📊 Found {len(trades)} trades")
                
            else:
                print(f"      ⚠️ Trades API error: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Trades error: {e}")
        
        return trades
    
    def _get_deposits_withdrawals(self, start_date, end_date):
        """Get deposits and withdrawals"""
        transactions = []
        
        try:
            # Get deposits
            params = {
                "from": start_date,
                "to": end_date,
                "max_page_size": 100
            }
            
            response = requests.get(f"{self.base_url}/fiatwallets/transactions", headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                tx_data = data.get('data', [])
                
                for tx in tx_data:
                    tx_record = {
                        'date': tx.get('time', {}).get('date_iso8601', ''),
                        'type': tx.get('type', 'Unknown').upper(),
                        'asset': tx.get('fiat', {}).get('symbol', 'EUR'),
                        'amount': float(tx.get('amount', 0)),
                        'price': 1.0,  # Fiat to fiat
                        'fiat_amount': float(tx.get('amount', 0)),
                        'fiat_currency': tx.get('fiat', {}).get('symbol', 'EUR'),
                        'side': tx.get('type', 'Unknown'),
                        'fees': 0.0,
                        'transaction_id': tx.get('id', ''),
                        'raw_data': tx
                    }
                    transactions.append(tx_record)
                
                print(f"      💳 Found {len(transactions)} deposits/withdrawals")
                
            else:
                print(f"      ⚠️ Fiat transactions API error: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Deposits/withdrawals error: {e}")
        
        return transactions
    
    def _get_fees(self, start_date, end_date):
        """Get fee transactions"""
        fees = []
        
        try:
            # Note: Fees are often included in trades, but we try to get separate fee records
            params = {
                "from": start_date,
                "to": end_date
            }
            
            # This endpoint might not exist, but let's try
            response = requests.get(f"{self.base_url}/fees", headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                fee_data = data.get('data', [])
                
                for fee in fee_data:
                    fee_record = {
                        'date': fee.get('time', {}).get('date_iso8601', ''),
                        'type': 'FEE',
                        'asset': fee.get('asset', {}).get('symbol', 'Unknown'),
                        'amount': float(fee.get('amount', 0)),
                        'price': 0.0,
                        'fiat_amount': float(fee.get('fiat_amount', 0)),
                        'fiat_currency': 'EUR',
                        'side': 'FEE',
                        'fees': float(fee.get('amount', 0)),
                        'fee_id': fee.get('id', ''),
                        'raw_data': fee
                    }
                    fees.append(fee_record)
                
                print(f"      💸 Found {len(fees)} separate fee records")
            else:
                print(f"      ℹ️ No separate fee endpoint (fees included in trades)")
                
        except Exception as e:
            print(f"      ℹ️ Fees endpoint not available or error: {e}")
        
        return fees
    
    def save_tax_report(self, transactions):
        """Save transactions in tax-compliant format"""
        print("\n📄 SAVING TAX REPORT...")
        
        if not transactions:
            print("   ⚠️ No transactions to save")
            return None, None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Save detailed CSV
        csv_filename = f"BITPANDA_TAX_TRANSACTIONS_2024_{timestamp}.csv"
        
        df = pd.DataFrame(transactions)
        df = df.sort_values('date')
        
        # Clean up for tax purposes
        tax_df = df[[
            'date', 'type', 'asset', 'amount', 'price', 
            'fiat_amount', 'fiat_currency', 'side', 'fees'
        ]].copy()
        
        tax_df.to_csv(csv_filename, index=False)
        print(f"   💾 CSV saved: {csv_filename}")
        
        # 2. Save detailed text report
        txt_filename = f"BITPANDA_TAX_REPORT_2024_{timestamp}.txt"
        
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("BITPANDA CRYPTOCURRENCY TAX REPORT 2024\n")
            f.write("=" * 60 + "\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tax Year: 2024\n")
            f.write(f"Platform: Bitpanda\n")
            f.write(f"Total Transactions: {len(transactions)}\n")
            f.write("=" * 60 + "\n\n")
            
            # Calculate totals
            total_buys = sum(t['fiat_amount'] for t in transactions if t['side'] == 'buy')
            total_sells = sum(t['fiat_amount'] for t in transactions if t['side'] == 'sell')
            total_fees = sum(t['fees'] for t in transactions)
            
            f.write("TAX SUMMARY\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Buy Value: €{total_buys:.2f}\n")
            f.write(f"Total Sell Value: €{total_sells:.2f}\n")
            f.write(f"Total Fees: €{total_fees:.2f}\n")
            f.write(f"Net Capital Gain/Loss: €{total_sells - total_buys - total_fees:.2f}\n\n")
            
            f.write("DETAILED TRANSACTIONS\n")
            f.write("=" * 60 + "\n")
            
            for i, tx in enumerate(sorted(transactions, key=lambda x: x['date']), 1):
                f.write(f"\n{i}. {tx['date'][:10]} | {tx['type']} | {tx['asset']}\n")
                f.write(f"   Amount: {tx['amount']:.8f} {tx['asset']}\n")
                f.write(f"   Price: €{tx['price']:.2f}\n")
                f.write(f"   Total Value: €{tx['fiat_amount']:.2f}\n")
                f.write(f"   Fees: €{tx['fees']:.2f}\n")
                f.write(f"   Side: {tx['side']}\n")
        
        print(f"   📄 Tax report saved: {txt_filename}")
        
        return csv_filename, txt_filename
    
    def download_full_tax_package(self):
        """Download complete tax package"""
        
        if not self.api_key:
            print("❌ No API key found! Please check your .env file.")
            return
        
        # Get account info
        account_info = self.get_account_info()
        
        if not account_info:
            print("❌ Could not access Bitpanda account")
            return
        
        # Download transactions
        transactions = self.get_transactions_2024()
        
        if not transactions:
            print("⚠️ No transactions found for 2024")
            return
        
        # Save tax report
        csv_file, txt_file = self.save_tax_report(transactions)
        
        print(f"\n🎉 TAX DOWNLOAD COMPLETE!")
        print("=" * 60)
        print(f"📄 Tax Report: {txt_file}")
        print(f"📊 CSV Export: {csv_file}")
        print(f"💰 Total Transactions: {len(transactions)}")
        print("=" * 60)
        
        return csv_file, txt_file

def main():
    """Main function to download tax data"""
    
    try:
        downloader = BitpandaTaxDownloader()
        downloader.download_full_tax_package()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
