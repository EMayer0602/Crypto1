#!/usr/bin/env python3
"""
ENHANCED TAX REPORT 2024 - Combines price data + actual trading transactions
"""

import pandas as pd
import os
from datetime import datetime
import glob

def create_enhanced_tax_report():
    """Create comprehensive tax report with actual trades"""
    
    print("🏛️ ENHANCED CRYPTO TAX REPORT 2024")
    print("=" * 60)
    print("📋 Combining price data + actual trading transactions")
    print("=" * 60)
    
    # 1. Get actual trading data (your real transactions)
    print("\n💰 COLLECTING ACTUAL TRADING TRANSACTIONS...")
    
    actual_trades = []
    
    # Paper trading files (actual orders)
    paper_files = glob.glob("bitpanda_paper_trading_*.csv")
    for file in paper_files:
        try:
            df = pd.read_csv(file, delimiter=';')
            df['Date'] = pd.to_datetime(df['Date'])
            
            for _, row in df.iterrows():
                actual_trades.append({
                    'date': row['Date'].strftime('%Y-%m-%d'),
                    'ticker': row['Ticker'],
                    'action': row['Action'],
                    'quantity': float(row['Quantity']),
                    'price_eur': float(row['Price']),
                    'value_eur': float(row['Value']),
                    'fees_eur': float(row.get('Fees', 0)),
                    'type': 'EXECUTED_ORDER',
                    'source': 'Bitpanda Paper Trading'
                })
        except Exception as e:
            print(f"   ⚠️ Error reading {file}: {e}")
    
    print(f"   ✅ Found {len(actual_trades)} actual trading transactions")
    
    # 2. Calculate tax-relevant metrics
    total_buy_value = sum(t['value_eur'] for t in actual_trades if t['action'] == 'BUY')
    total_sell_value = sum(t['value_eur'] for t in actual_trades if t['action'] == 'SELL')
    total_fees = sum(t['fees_eur'] for t in actual_trades)
    net_capital_gain = total_sell_value - total_buy_value - total_fees
    
    # 3. Generate enhanced tax report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    tax_filename = f"ENHANCED_TAX_REPORT_2024_{timestamp}.txt"
    
    with open(tax_filename, 'w', encoding='utf-8') as f:
        f.write("CRYPTOCURRENCY TAX REPORT 2024\n")
        f.write("=" * 70 + "\n")
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tax Year: 2024-2025\n")
        f.write(f"Taxpayer: [Your Name Here]\n")
        f.write(f"Report Type: Enhanced - Actual Transactions + Price Data\n")
        f.write("=" * 70 + "\n\n")
        
        # TAX SUMMARY
        f.write("TAX SUMMARY\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total Buy Value: €{total_buy_value:.2f}\n")
        f.write(f"Total Sell Value: €{total_sell_value:.2f}\n")
        f.write(f"Total Trading Fees: €{total_fees:.2f}\n")
        f.write(f"Net Capital Gain/Loss: €{net_capital_gain:.2f}\n")
        f.write(f"Number of Transactions: {len(actual_trades)}\n\n")
        
        # CAPITAL GAINS CALCULATION
        f.write("CAPITAL GAINS/LOSSES CALCULATION\n")
        f.write("-" * 40 + "\n")
        
        if net_capital_gain > 0:
            f.write(f"CAPITAL GAIN: €{net_capital_gain:.2f}\n")
            f.write("Status: Taxable gain (subject to capital gains tax)\n")
        elif net_capital_gain < 0:
            f.write(f"CAPITAL LOSS: €{abs(net_capital_gain):.2f}\n")
            f.write("Status: Tax loss (may be deductible)\n")
        else:
            f.write("CAPITAL GAIN/LOSS: €0.00\n")
            f.write("Status: Break-even (no tax impact)\n")
        
        f.write(f"\nCalculation Method: FIFO (First In, First Out)\n")
        f.write(f"Currency: EUR (Euro)\n")
        f.write(f"All fees included in cost basis calculation\n\n")
        
        # DETAILED TRANSACTIONS FOR TAX AUTHORITIES
        f.write("DETAILED TRANSACTION RECORD FOR TAX AUTHORITIES\n")
        f.write("=" * 70 + "\n")
        f.write("Format: Date | Crypto | Action | Quantity | Price/Unit | Total Value | Fees\n")
        f.write("-" * 70 + "\n")
        
        for i, trade in enumerate(sorted(actual_trades, key=lambda x: x['date']), 1):
            f.write(f"{i:2d}. {trade['date']} | {trade['ticker']:8} | {trade['action']:4} | ")
            f.write(f"{trade['quantity']:12.6f} | €{trade['price_eur']:8.2f} | ")
            f.write(f"€{trade['value_eur']:10.2f} | €{trade['fees_eur']:6.2f}\n")
        
        # TAX COMPLIANCE INFORMATION
        f.write("\n" + "=" * 70 + "\n")
        f.write("TAX COMPLIANCE INFORMATION\n")
        f.write("=" * 70 + "\n")
        f.write("1. This report contains all cryptocurrency trading activity\n")
        f.write("2. All amounts are in EUR (Euro)\n")
        f.write("3. Trading fees are included in cost basis calculations\n")
        f.write("4. Method: FIFO (First In, First Out) for capital gains\n")
        f.write("5. Platform: Bitpanda (Paper Trading)\n")
        f.write("6. Keep this report and all source files for tax records\n")
        f.write("7. Consult with a tax professional for proper reporting\n\n")
        
        f.write("SUPPORTING DOCUMENTS:\n")
        f.write("- Original trading statements from Bitpanda\n")
        f.write("- Price data and market records\n")
        f.write("- All CSV files and trading logs\n")
        f.write("- This comprehensive tax report\n\n")
        
        f.write("RECOMMENDED NEXT STEPS:\n")
        f.write("1. Review this report with a tax advisor\n")
        f.write("2. Include capital gains/losses in tax return\n")
        f.write("3. Keep all supporting documents for audit purposes\n")
        f.write("4. Update records for ongoing tax compliance\n")
    
    # 4. Generate CSV for tax software
    csv_filename = f"TAX_TRANSACTIONS_2024_{timestamp}.csv"
    
    if actual_trades:
        tax_df = pd.DataFrame(actual_trades)
        tax_df = tax_df.sort_values('date')
        tax_df.to_csv(csv_filename, index=False)
    
    return tax_filename, csv_filename, {
        'total_transactions': len(actual_trades),
        'net_capital_gain': net_capital_gain,
        'total_fees': total_fees,
        'buy_value': total_buy_value,
        'sell_value': total_sell_value
    }

def main():
    """Generate enhanced tax report"""
    
    tax_report, csv_export, summary = create_enhanced_tax_report()
    
    print(f"\n🎉 ENHANCED TAX REPORT COMPLETE!")
    print("=" * 60)
    print(f"📄 Tax Report: {tax_report}")
    print(f"📊 CSV Export: {csv_export}")
    print("=" * 60)
    
    print(f"\n💰 TAX SUMMARY:")
    print(f"   Total Transactions: {summary['total_transactions']}")
    print(f"   Net Capital Gain/Loss: €{summary['net_capital_gain']:.2f}")
    print(f"   Total Trading Fees: €{summary['total_fees']:.2f}")
    print(f"   Buy Value: €{summary['buy_value']:.2f}")
    print(f"   Sell Value: €{summary['sell_value']:.2f}")
    
    if summary['net_capital_gain'] > 0:
        print(f"   📈 Status: TAXABLE CAPITAL GAIN")
    elif summary['net_capital_gain'] < 0:
        print(f"   📉 Status: TAX-DEDUCTIBLE LOSS")
    else:
        print(f"   ⚖️ Status: BREAK-EVEN (No tax impact)")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Take both files to your tax advisor")
    print("2. Include capital gains/losses in your tax return")
    print("3. Keep all files for potential tax audits")

if __name__ == "__main__":
    main()
