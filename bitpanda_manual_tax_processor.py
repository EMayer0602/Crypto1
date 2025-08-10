#!/usr/bin/env python3
"""
BITPANDA MANUAL TAX EXPORT PROCESSOR
Process manually exported CSV files from Bitpanda for tax purposes
"""

import pandas as pd
import os
from datetime import datetime
import glob

def find_bitpanda_csv_files():
    """Find potential Bitpanda CSV exports in the directory"""
    print("🔍 SEARCHING FOR BITPANDA CSV FILES...")
    
    # Common Bitpanda export file patterns
    patterns = [
        "*bitpanda*.csv",
        "*transaction*.csv", 
        "*trade*.csv",
        "*export*.csv",
        "*history*.csv"
    ]
    
    found_files = []
    
    for pattern in patterns:
        files = glob.glob(pattern, recursive=False)
        for file in files:
            if os.path.getsize(file) > 0:  # Only non-empty files
                found_files.append(file)
    
    # Remove duplicates
    found_files = list(set(found_files))
    
    print(f"   📄 Found {len(found_files)} potential CSV files:")
    for i, file in enumerate(found_files, 1):
        size_kb = os.path.getsize(file) / 1024
        print(f"   {i}. {file} ({size_kb:.1f} KB)")
    
    return found_files

def analyze_csv_structure(csv_file):
    """Analyze the structure of a CSV file to understand its format"""
    print(f"\n🔍 ANALYZING: {csv_file}")
    
    try:
        # Try to read with different encodings
        encodings = ['utf-8', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_file, encoding=encoding)
                print(f"   ✅ Successfully read with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print(f"   ❌ Could not read {csv_file} with any encoding")
            return None
        
        print(f"   📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"   📋 Columns: {list(df.columns)}")
        
        # Look for date columns
        date_columns = [col for col in df.columns if any(word in col.lower() for word in ['date', 'time', 'created', 'timestamp'])]
        if date_columns:
            print(f"   📅 Date columns: {date_columns}")
            
            # Check date range
            for date_col in date_columns:
                try:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    min_date = df[date_col].min()
                    max_date = df[date_col].max()
                    print(f"      {date_col}: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
                    
                    # Count 2024 entries
                    df_2024 = df[df[date_col].dt.year == 2024]
                    print(f"      2024 entries: {len(df_2024)}")
                except:
                    print(f"      {date_col}: Could not parse dates")
        
        # Show sample data
        print(f"   📋 Sample data (first 3 rows):")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"   ❌ Error analyzing {csv_file}: {e}")
        return None

def process_bitpanda_export(csv_file, output_name=None):
    """Process a Bitpanda CSV export into tax-compliant format"""
    print(f"\n💼 PROCESSING FOR TAX: {csv_file}")
    
    df = analyze_csv_structure(csv_file)
    if df is None:
        return None
    
    # Filter for 2024 only
    date_columns = [col for col in df.columns if any(word in col.lower() for word in ['date', 'time', 'created', 'timestamp'])]
    
    df_2024 = df.copy()
    if date_columns:
        date_col = date_columns[0]  # Use first date column
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df_2024 = df[df[date_col].dt.year == 2024]
        except:
            print("   ⚠️ Could not filter by date, using all data")
    
    print(f"   📅 2024 transactions: {len(df_2024)}")
    
    if len(df_2024) == 0:
        print("   ⚠️ No 2024 data found")
        return None
    
    # Create standardized output
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_name:
        output_csv = f"{output_name}_{timestamp}.csv"
        output_txt = f"{output_name}_{timestamp}.txt"
    else:
        base_name = os.path.splitext(csv_file)[0]
        output_csv = f"{base_name}_TAX_2024_{timestamp}.csv"
        output_txt = f"{base_name}_TAX_2024_{timestamp}.txt"
    
    # Save CSV
    df_2024.to_csv(output_csv, index=False)
    print(f"   💾 Tax CSV saved: {output_csv}")
    
    # Create readable tax report
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write("BITPANDA TAX REPORT 2024 (FROM MANUAL EXPORT)\n")
        f.write("=" * 70 + "\n")
        f.write(f"Source File: {csv_file}\n")
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tax Year: 2024\n")
        f.write(f"Total 2024 Transactions: {len(df_2024)}\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("COLUMN MAPPING\n")
        f.write("-" * 30 + "\n")
        for i, col in enumerate(df_2024.columns):
            f.write(f"{i+1:2d}. {col}\n")
        
        f.write(f"\nDATA SUMMARY\n")
        f.write("-" * 30 + "\n")
        f.write(f"Rows: {len(df_2024)}\n")
        f.write(f"Columns: {len(df_2024.columns)}\n")
        
        # Look for amount/value columns
        value_columns = [col for col in df_2024.columns if any(word in col.lower() for word in ['amount', 'value', 'price', 'total', 'fee'])]
        if value_columns:
            f.write(f"\nVALUE COLUMNS FOUND:\n")
            for col in value_columns:
                try:
                    numeric_data = pd.to_numeric(df_2024[col], errors='coerce')
                    total = numeric_data.sum()
                    count = numeric_data.count()
                    f.write(f"• {col}: {count} entries, sum = {total:.2f}\n")
                except:
                    f.write(f"• {col}: Non-numeric\n")
        
        f.write(f"\nFULL DATA EXPORT\n")
        f.write("=" * 70 + "\n")
        f.write(df_2024.to_string())
    
    print(f"   📄 Tax report saved: {output_txt}")
    
    return output_csv, output_txt

def process_all_found_files():
    """Process all found CSV files"""
    csv_files = find_bitpanda_csv_files()
    
    if not csv_files:
        print("\n❌ No CSV files found!")
        print("\n📋 MANUAL EXPORT INSTRUCTIONS:")
        print("=" * 50)
        print("1. Log into your Bitpanda account")
        print("2. Go to 'History' or 'Transactions'")
        print("3. Export/Download your transaction history as CSV")
        print("4. Save the CSV file in this directory")
        print("5. Run this script again")
        print("=" * 50)
        return
    
    processed_files = []
    
    for csv_file in csv_files:
        try:
            result = process_bitpanda_export(csv_file)
            if result:
                processed_files.extend(result)
        except Exception as e:
            print(f"   ❌ Error processing {csv_file}: {e}")
    
    print(f"\n🎉 PROCESSING COMPLETE!")
    print("=" * 50)
    print(f"📊 Files processed: {len(csv_files)}")
    print(f"📄 Output files: {len(processed_files)}")
    
    if processed_files:
        print("\n📋 CREATED FILES:")
        for file in processed_files:
            if file and os.path.exists(file):
                print(f"   • {file}")

def main():
    """Main function"""
    print("🏛️ BITPANDA MANUAL TAX EXPORT PROCESSOR")
    print("=" * 60)
    print("📋 This tool processes manually exported Bitpanda CSV files")
    print("🎯 Purpose: Create tax-compliant reports for 2024")
    print("=" * 60)
    
    try:
        process_all_found_files()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
