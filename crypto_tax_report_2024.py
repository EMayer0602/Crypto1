#!/usr/bin/env python3
"""
CRYPTO TAX REPORT 2024
Comprehensive tax reporting for cryptocurrency trading activities
"""

import pandas as pd
import os
import sys
from datetime import datetime, date
import glob

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers

class CryptoTaxReport2024:
    """Generate comprehensive tax report for 2024 crypto trading"""
    
    def __init__(self):
        self.tax_year = 2024
        self.report_date = datetime.now()
        self.trades_data = []
        self.summary_data = {}
        
        print("📊 CRYPTO TAX REPORT 2024")
        print("=" * 60)
        print(f"📅 Tax Year: {self.tax_year}")
        print(f"📋 Report Generated: {self.report_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
    
    def collect_trading_data(self):
        """Collect all trading data from CSV files and reports"""
        print("\n🔍 COLLECTING 2024 TRADING DATA...")
        
        # 1. Look for trade report files
        trade_files = [
            "14_day_trades_*.csv",
            "*paper_trading*.csv", 
            "*trades_report*.csv",
            "*backtest_report*.csv"
        ]
        
        for pattern in trade_files:
            files = glob.glob(pattern)
            for file in files:
                try:
                    if self._is_2024_file(file):
                        print(f"   📄 Processing: {file}")
                        df = pd.read_csv(file)
                        self._process_trade_file(df, file)
                except Exception as e:
                    print(f"   ❌ Error reading {file}: {e}")
        
        # 2. Look for individual ticker CSV files with 2024 data
        for ticker_name in crypto_tickers.keys():
            csv_file = f"{ticker_name}_daily.csv"
            if os.path.exists(csv_file):
                try:
                    print(f"   📈 Processing: {csv_file}")
                    df = pd.read_csv(csv_file)
                    self._extract_2024_data(df, ticker_name)
                except Exception as e:
                    print(f"   ❌ Error reading {csv_file}: {e}")
        
        print(f"\n✅ Collected {len(self.trades_data)} trading records for 2024")
    
    def _is_2024_file(self, filename):
        """Check if file contains 2024 data based on filename or modification date"""
        # Check filename for 2024
        if '2024' in filename:
            return True
        
        # Check file modification date
        try:
            mtime = os.path.getmtime(filename)
            mod_year = datetime.fromtimestamp(mtime).year
            return mod_year == 2024
        except:
            return False
    
    def _process_trade_file(self, df, filename):
        """Process trade files and extract 2024 transactions"""
        if df.empty:
            return
        
        # Look for date columns
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'Date' in col]
        
        if not date_columns:
            print(f"   ⚠️ No date column found in {filename}")
            return
        
        date_col = date_columns[0]
        
        try:
            df[date_col] = pd.to_datetime(df[date_col])
            df_2024 = df[df[date_col].dt.year == 2024]
            
            for _, row in df_2024.iterrows():
                trade_record = {
                    'date': row[date_col].strftime('%Y-%m-%d'),
                    'source_file': filename,
                    'data': dict(row)
                }
                self.trades_data.append(trade_record)
                
        except Exception as e:
            print(f"   ⚠️ Date processing error in {filename}: {e}")
    
    def _extract_2024_data(self, df, ticker_name):
        """Extract 2024 price data from ticker CSV files"""
        if df.empty:
            return
        
        try:
            df['Date'] = pd.to_datetime(df['Date'])
            df_2024 = df[df['Date'].dt.year == 2024]
            
            if not df_2024.empty:
                for _, row in df_2024.iterrows():
                    price_record = {
                        'date': row['Date'].strftime('%Y-%m-%d'),
                        'ticker': ticker_name,
                        'open': row.get('Open', 0),
                        'high': row.get('High', 0),
                        'low': row.get('Low', 0),
                        'close': row.get('Close', 0),
                        'volume': row.get('Volume', 0),
                        'source_file': f"{ticker_name}_daily.csv"
                    }
                    self.trades_data.append(price_record)
                    
        except Exception as e:
            print(f"   ⚠️ Error processing {ticker_name}: {e}")
    
    def calculate_tax_summary(self):
        """Calculate tax-relevant summary statistics"""
        print("\n💰 CALCULATING TAX SUMMARY...")
        
        if not self.trades_data:
            print("   ⚠️ No trading data found for 2024")
            return
        
        # Group data by ticker and month
        tickers = set()
        months = set()
        
        for trade in self.trades_data:
            if 'ticker' in trade:
                tickers.add(trade['ticker'])
            trade_date = datetime.strptime(trade['date'], '%Y-%m-%d')
            months.add(trade_date.strftime('%Y-%m'))
        
        self.summary_data = {
            'total_records': len(self.trades_data),
            'active_tickers': list(tickers),
            'active_months': sorted(list(months)),
            'trading_period': {
                'start': min(trade['date'] for trade in self.trades_data),
                'end': max(trade['date'] for trade in self.trades_data)
            }
        }
        
        print(f"   📊 Total Records: {self.summary_data['total_records']}")
        print(f"   🪙 Active Tickers: {len(self.summary_data['active_tickers'])}")
        print(f"   📅 Active Months: {len(self.summary_data['active_months'])}")
        print(f"   📈 Trading Period: {self.summary_data['trading_period']['start']} to {self.summary_data['trading_period']['end']}")
    
    def generate_tax_report(self):
        """Generate comprehensive tax report"""
        print("\n📋 GENERATING TAX REPORT...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"CRYPTO_TAX_REPORT_2024_{timestamp}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            # Header
            f.write("CRYPTOCURRENCY TAX REPORT 2024\n")
            f.write("=" * 60 + "\n")
            f.write(f"Report Generated: {self.report_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tax Year: {self.tax_year}\n")
            f.write("=" * 60 + "\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Trading Records: {self.summary_data.get('total_records', 0)}\n")
            f.write(f"Active Cryptocurrencies: {len(self.summary_data.get('active_tickers', []))}\n")
            f.write(f"Trading Months: {len(self.summary_data.get('active_months', []))}\n")
            
            if 'trading_period' in self.summary_data:
                f.write(f"Trading Period: {self.summary_data['trading_period']['start']} to {self.summary_data['trading_period']['end']}\n")
            
            f.write("\nACTIVE CRYPTOCURRENCIES:\n")
            for ticker in self.summary_data.get('active_tickers', []):
                f.write(f"  - {ticker}\n")
            
            f.write("\nACTIVE TRADING MONTHS:\n")
            for month in self.summary_data.get('active_months', []):
                f.write(f"  - {month}\n")
            
            # Detailed transactions
            f.write("\n" + "=" * 60 + "\n")
            f.write("DETAILED TRANSACTION RECORDS\n")
            f.write("=" * 60 + "\n")
            
            for i, trade in enumerate(self.trades_data, 1):
                f.write(f"\nRecord #{i}:\n")
                f.write(f"  Date: {trade['date']}\n")
                f.write(f"  Source: {trade['source_file']}\n")
                
                if 'ticker' in trade:
                    f.write(f"  Ticker: {trade['ticker']}\n")
                    f.write(f"  Open: €{trade.get('open', 'N/A')}\n")
                    f.write(f"  High: €{trade.get('high', 'N/A')}\n")
                    f.write(f"  Low: €{trade.get('low', 'N/A')}\n")
                    f.write(f"  Close: €{trade.get('close', 'N/A')}\n")
                    f.write(f"  Volume: {trade.get('volume', 'N/A')}\n")
                
                if 'data' in trade:
                    f.write("  Additional Data:\n")
                    for key, value in trade['data'].items():
                        if key.lower() not in ['date', 'unnamed']:
                            f.write(f"    {key}: {value}\n")
            
            # Tax notes
            f.write("\n" + "=" * 60 + "\n")
            f.write("TAX COMPLIANCE NOTES\n")
            f.write("=" * 60 + "\n")
            f.write("1. This report contains all cryptocurrency trading activity for 2024\n")
            f.write("2. All prices are in EUR (Euro)\n")
            f.write("3. Consult with a tax professional for proper reporting\n")
            f.write("4. Keep this report and all source files for tax records\n")
            f.write("5. Capital gains/losses may apply based on your jurisdiction\n")
            
        print(f"   💾 Tax report saved as: {report_filename}")
        return report_filename
    
    def generate_csv_export(self):
        """Generate CSV export for spreadsheet analysis"""
        print("\n📊 GENERATING CSV EXPORT...")
        
        if not self.trades_data:
            print("   ⚠️ No data to export")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"CRYPTO_TAX_DATA_2024_{timestamp}.csv"
        
        # Flatten data for CSV
        csv_data = []
        for trade in self.trades_data:
            row = {
                'Date': trade['date'],
                'Source_File': trade['source_file'],
                'Ticker': trade.get('ticker', 'N/A'),
                'Open_EUR': trade.get('open', 'N/A'),
                'High_EUR': trade.get('high', 'N/A'),
                'Low_EUR': trade.get('low', 'N/A'),
                'Close_EUR': trade.get('close', 'N/A'),
                'Volume': trade.get('volume', 'N/A')
            }
            
            # Add additional data from trade files
            if 'data' in trade:
                for key, value in trade['data'].items():
                    if key not in row:
                        row[f"Extra_{key}"] = value
            
            csv_data.append(row)
        
        df = pd.DataFrame(csv_data)
        df = df.sort_values('Date')
        df.to_csv(csv_filename, index=False)
        
        print(f"   💾 CSV export saved as: {csv_filename}")
        return csv_filename

def main():
    """Main function to generate tax report"""
    
    print("🏛️ CRYPTO TAX REPORT GENERATOR 2024")
    print("📋 Generating comprehensive tax documentation...")
    
    try:
        # Create tax report instance
        tax_report = CryptoTaxReport2024()
        
        # Collect all trading data
        tax_report.collect_trading_data()
        
        # Calculate summary
        tax_report.calculate_tax_summary()
        
        # Generate reports
        txt_report = tax_report.generate_tax_report()
        csv_report = tax_report.generate_csv_export()
        
        print(f"\n🎉 TAX REPORT GENERATION COMPLETE!")
        print("=" * 60)
        print(f"📄 Text Report: {txt_report}")
        print(f"📊 CSV Export: {csv_report}")
        print("=" * 60)
        
        print("\n💡 NEXT STEPS:")
        print("1. Review both generated files")
        print("2. Consult with a tax professional")
        print("3. Keep all files for tax records")
        print("4. Calculate capital gains/losses as required")
        
    except Exception as e:
        print(f"\n❌ Error generating tax report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
