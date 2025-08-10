#!/usr/bin/env python3
"""
BITPANDA REAL TRANSACTION PROCESSOR FOR TAX 2024
Process real Bitpanda CSV exports for proper tax reporting
"""

import pandas as pd
import os
from datetime import datetime
import glob

def find_real_bitpanda_files():
    """Find real Bitpanda export files (not paper trading)"""
    print("🔍 SEARCHING FOR REAL BITPANDA EXPORT FILES...")
    
    # Look for files that are likely real Bitpanda exports
    patterns = [
        "*bitpanda*real*.csv",
        "*bitpanda*2024*.csv",
        "*real*2024*.csv",
        "*export*2024*.csv",
        "*transactions*2024*.csv",
        "*history*2024*.csv"
    ]
    
    # Also check for any CSV that's NOT paper trading
    all_csvs = glob.glob("*.csv")
    paper_trading_keywords = ['paper', 'backtest', 'strategy', 'trades_report', 'simulation']
    
    real_files = []
    
    # Add files matching our patterns
    for pattern in patterns:
        files = glob.glob(pattern, recursive=False)
        real_files.extend(files)
    
    # Add any other CSV that doesn't look like paper trading
    for csv_file in all_csvs:
        if not any(keyword in csv_file.lower() for keyword in paper_trading_keywords):
            if csv_file not in real_files and os.path.getsize(csv_file) > 100:  # Non-empty
                real_files.append(csv_file)
    
    # Remove duplicates and sort
    real_files = sorted(list(set(real_files)))
    
    print(f"   📄 Found {len(real_files)} potential REAL transaction files:")
    for i, file in enumerate(real_files, 1):
        size_kb = os.path.getsize(file) / 1024
        mod_time = datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M')
        print(f"   {i}. {file} ({size_kb:.1f} KB, modified: {mod_time})")
    
    return real_files

def analyze_real_bitpanda_csv(csv_file):
    """Analyze and process real Bitpanda CSV with better parsing"""
    print(f"\n💰 PROCESSING REAL BITPANDA DATA: {csv_file}")
    
    try:
        # Try different separators and encodings
        separators = [',', ';', '\t']
        encodings = ['utf-8', 'iso-8859-1', 'cp1252', 'utf-16']
        
        df = None
        used_sep = None
        used_encoding = None
        
        for encoding in encodings:
            for sep in separators:
                try:
                    test_df = pd.read_csv(csv_file, sep=sep, encoding=encoding, nrows=5)
                    if test_df.shape[1] > 1:  # Multiple columns = good separation
                        df = pd.read_csv(csv_file, sep=sep, encoding=encoding)
                        used_sep = sep
                        used_encoding = encoding
                        print(f"   ✅ Successfully parsed with separator '{sep}' and encoding '{encoding}'")
                        break
                except:
                    continue
            if df is not None:
                break
        
        if df is None:
            print(f"   ❌ Could not parse {csv_file}")
            return None
        
        print(f"   📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"   📋 Columns: {list(df.columns)}")
        
        # Clean column names
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
        
        # Look for common Bitpanda column patterns
        bitpanda_indicators = [
            'transaction_id', 'asset', 'amount', 'fee', 'timestamp', 'created_at',
            'cryptocoin', 'fiat', 'type', 'status', 'buy', 'sell', 'deposit', 'withdrawal'
        ]
        
        found_indicators = [col for col in df.columns if any(indicator in col for indicator in bitpanda_indicators)]
        print(f"   🏛️ Bitpanda indicators found: {found_indicators}")
        
        # Look for date columns
        date_columns = [col for col in df.columns if any(word in col for word in ['date', 'time', 'created', 'timestamp'])]
        print(f"   📅 Date columns: {date_columns}")
        
        # Process dates and filter for 2024
        df_2024 = df.copy()
        if date_columns:
            date_col = date_columns[0]
            try:
                # Try different date formats
                date_formats = ['%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']
                
                for fmt in date_formats:
                    try:
                        df[date_col] = pd.to_datetime(df[date_col], format=fmt, errors='raise')
                        print(f"      ✅ Parsed dates with format: {fmt}")
                        break
                    except:
                        continue
                else:
                    # Fallback to auto-detection
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    print(f"      ⚠️ Used auto-detection for dates")
                
                # Filter for 2024
                df_2024 = df[df[date_col].dt.year == 2024]
                
                if len(df_2024) > 0:
                    date_range = f"{df_2024[date_col].min().strftime('%Y-%m-%d')} to {df_2024[date_col].max().strftime('%Y-%m-%d')}"
                    print(f"      📅 2024 date range: {date_range}")
                
            except Exception as e:
                print(f"      ❌ Date processing error: {e}")
        
        print(f"   🎯 2024 transactions found: {len(df_2024)}")
        
        if len(df_2024) == 0:
            print(f"   ⚠️ No 2024 data in this file")
            return None
        
        # Show sample data
        print(f"\n   📋 SAMPLE 2024 DATA (first 3 rows):")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 200)
        print(df_2024.head(3).to_string())
        
        return df_2024, date_col
        
    except Exception as e:
        print(f"   ❌ Error processing {csv_file}: {e}")
        return None

def create_tax_report_from_real_data(df_2024, source_file, date_col):
    """Create comprehensive tax report from real Bitpanda data"""
    print(f"\n📄 CREATING TAX REPORT FROM REAL DATA...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Save cleaned CSV
    csv_filename = f"REAL_BITPANDA_TAX_2024_{timestamp}.csv"
    df_2024_sorted = df_2024.sort_values(date_col)
    df_2024_sorted.to_csv(csv_filename, index=False)
    print(f"   💾 Tax CSV saved: {csv_filename}")
    
    # 2. Create comprehensive tax report
    txt_filename = f"REAL_BITPANDA_TAX_REPORT_2024_{timestamp}.txt"
    
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write("REAL BITPANDA CRYPTOCURRENCY TAX REPORT 2024\n")
        f.write("=" * 70 + "\n")
        f.write(f"Source File: {source_file}\n")
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tax Year: 2024\n")
        f.write(f"Total Real Transactions: {len(df_2024)}\n")
        f.write("⚠️  IMPORTANT: This is for REAL transactions, not paper trading\n")
        f.write("=" * 70 + "\n\n")
        
        # Column analysis
        f.write("DATA STRUCTURE ANALYSIS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Columns ({len(df_2024.columns)}): {', '.join(df_2024.columns)}\n\n")
        
        # Look for transaction types
        type_columns = [col for col in df_2024.columns if 'type' in col]
        if type_columns:
            f.write("TRANSACTION TYPES:\n")
            for col in type_columns:
                type_counts = df_2024[col].value_counts()
                f.write(f"  {col}:\n")
                for tx_type, count in type_counts.items():
                    f.write(f"    • {tx_type}: {count} transactions\n")
            f.write("\n")
        
        # Look for amounts and values
        amount_columns = [col for col in df_2024.columns if any(word in col for word in ['amount', 'value', 'price', 'total'])]
        if amount_columns:
            f.write("FINANCIAL SUMMARY:\n")
            for col in amount_columns:
                try:
                    numeric_data = pd.to_numeric(df_2024[col], errors='coerce').dropna()
                    if len(numeric_data) > 0:
                        total = numeric_data.sum()
                        avg = numeric_data.mean()
                        f.write(f"  {col}:\n")
                        f.write(f"    • Total: {total:,.2f}\n")
                        f.write(f"    • Average: {avg:,.2f}\n")
                        f.write(f"    • Count: {len(numeric_data)}\n")
                except:
                    f.write(f"  {col}: Non-numeric data\n")
            f.write("\n")
        
        # Timeline analysis
        if date_col in df_2024.columns:
            f.write("TIMELINE ANALYSIS:\n")
            monthly_counts = df_2024.groupby(df_2024[date_col].dt.to_period('M')).size()
            f.write("Monthly transaction counts:\n")
            for month, count in monthly_counts.items():
                f.write(f"  {month}: {count} transactions\n")
            f.write("\n")
        
        # Full data export
        f.write("COMPLETE TRANSACTION DETAILS\n")
        f.write("=" * 70 + "\n")
        f.write(df_2024_sorted.to_string())
        
    print(f"   📄 Tax report saved: {txt_filename}")
    
    # 3. Create summary
    print(f"\n🎉 TAX REPORT SUMMARY:")
    print(f"   📊 Total 2024 transactions: {len(df_2024)}")
    print(f"   📅 Date range: {df_2024[date_col].min().strftime('%Y-%m-%d')} to {df_2024[date_col].max().strftime('%Y-%m-%d')}")
    print(f"   💾 Files created:")
    print(f"      • {csv_filename} (for tax software)")
    print(f"      • {txt_filename} (human readable)")
    
    return csv_filename, txt_filename

def process_real_bitpanda_exports():
    """Process all real Bitpanda exports found"""
    
    print("🏛️ REAL BITPANDA TAX PROCESSOR 2024")
    print("=" * 60)
    print("🎯 Processing REAL transaction data for tax purposes")
    print("❌ Excludes paper trading and backtesting data")
    print("=" * 60)
    
    # Find real files
    real_files = find_real_bitpanda_files()
    
    if not real_files:
        print("\n❌ NO REAL BITPANDA FILES FOUND!")
        print("\n📋 TO GET YOUR REAL 2024 TRANSACTION DATA:")
        print("=" * 50)
        print("1. Go to https://www.bitpanda.com")
        print("2. Log in to your account")
        print("3. Navigate to Portfolio → History")
        print("4. Set date range: Jan 1, 2024 - Dec 31, 2024")
        print("5. Export/Download as CSV")
        print("6. Save the file in this directory")
        print("7. Run this script again")
        print("=" * 50)
        return
    
    processed_count = 0
    
    for csv_file in real_files:
        print(f"\n{'='*60}")
        print(f"PROCESSING: {csv_file}")
        print(f"{'='*60}")
        
        result = analyze_real_bitpanda_csv(csv_file)
        if result:
            df_2024, date_col = result
            create_tax_report_from_real_data(df_2024, csv_file, date_col)
            processed_count += 1
        else:
            print(f"   ⚠️ Skipped {csv_file} - no 2024 data or processing error")
    
    print(f"\n🎉 PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"📊 Files processed successfully: {processed_count}")
    print(f"📄 Real files found: {len(real_files)}")
    
    if processed_count == 0:
        print("\n⚠️  NO 2024 DATA PROCESSED!")
        print("This could mean:")
        print("• You need to export your data from Bitpanda first")
        print("• The exported files are in a different format")
        print("• The date filtering isn't working correctly")
        print("\nTry manually exporting from Bitpanda web interface.")

def main():
    """Main function"""
    try:
        process_real_bitpanda_exports()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
