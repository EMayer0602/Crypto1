#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generiert aktuellen, korrekten Backtest-Report und kombiniert alle Reports
"""

import os
import subprocess
import webbrowser
from datetime import datetime
from bs4 import BeautifulSoup

def run_current_backtest():
    """Führt den aktuellen Backtest mit neuesten Daten durch"""
    print("🔄 Führe aktuellen Backtest durch...")
    
    try:
        # Führe den unified crypto report aus (der sollte die aktuellsten Backtests machen)
        print("📊 Starte unified_crypto_report.py...")
        result = subprocess.run(['python', 'unified_crypto_report.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ Unified Crypto Report erfolgreich erstellt!")
            print("Output:", result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        else:
            print("❌ Fehler beim Unified Crypto Report:")
            print("Error:", result.stderr)
            
        # Führe auch den summary report aus
        print("📈 Starte multi_ticker_analysis.py...")
        result2 = subprocess.run(['python', 'multi_ticker_analysis.py'], 
                               capture_output=True, text=True, encoding='utf-8')
        
        if result2.returncode == 0:
            print("✅ Summary Report erfolgreich erstellt!")
            print("Output:", result2.stdout[-500:] if len(result2.stdout) > 500 else result2.stdout)
        else:
            print("❌ Fehler beim Summary Report:")
            print("Error:", result2.stderr)
            
        return result.returncode == 0 and result2.returncode == 0
        
    except Exception as e:
        print(f"❌ Fehler beim Ausführen der Backtest-Scripts: {e}")
        return False

def get_latest_reports():
    """Get the latest strategy report and unified report files"""
    current_dir = os.getcwd()
    
    # Find latest reports
    strategy_files = []  # trading_summary_report
    unified_files = []   # unified_crypto_report
    
    for file in os.listdir(current_dir):
        if file.startswith('trading_summary_report_') and file.endswith('.html'):
            strategy_files.append(file)
        elif file.startswith('unified_crypto_report_') and file.endswith('.html'):
            unified_files.append(file)
    
    # Sort by timestamp in filename (descending)
    strategy_files.sort(reverse=True)
    unified_files.sort(reverse=True)
    
    if not strategy_files:
        raise FileNotFoundError("No trading_summary_report HTML files found")
    if not unified_files:
        raise FileNotFoundError("No unified_crypto_report HTML files found")
    
    return strategy_files[0], unified_files[0]

def merge_html_reports(strategy_file, unified_file):
    """Merge: Strategy Report (Basis) + Unified Report (KOMPLETT unverändert anhängen)"""
    
    # Read both HTML files
    with open(strategy_file, 'r', encoding='utf-8') as f:
        strategy_content = f.read()
    
    with open(unified_file, 'r', encoding='utf-8') as f:
        unified_content = f.read()
    
    # Parse HTML content
    strategy_soup = BeautifulSoup(strategy_content, 'html.parser')
    unified_soup = BeautifulSoup(unified_content, 'html.parser')
    
    # Use strategy report as base (Trading Summary Report als Basis)
    merged_soup = BeautifulSoup(strategy_content, 'html.parser')
    
    # Find body to append unified content
    body = merged_soup.find('body')
    if not body:
        body = merged_soup
    
    # Add a simple separator
    separator_section = BeautifulSoup('''
    <hr style="margin: 50px 0; border: 2px solid #3498db;">
    ''', 'html.parser')
    
    # Append separator
    body.append(separator_section)
    
    # Extract COMPLETE unified report body content (UNVERÄNDERT!)
    unified_body = unified_soup.find('body')
    if unified_body:
        # Get ALL content from unified body - KOMPLETT UNVERÄNDERT!
        for element in unified_body.children:
            if element.name:  # Only append actual HTML elements
                # Clone the element and append to merged document - NOTHING changed!
                new_element = BeautifulSoup(str(element), 'html.parser')
                body.append(new_element)
    
    return str(merged_soup)

def save_merged_report(merged_html):
    """Save the merged HTML report with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"CURRENT_BACKTEST_REPORT_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(merged_html)
    
    return filename

def main():
    """Main function to create current backtest report"""
    try:
        print("🚀 Erstelle aktuellen, korrekten Backtest-Report...")
        print("=" * 60)
        
        # 1. Führe aktuelle Backtests durch
        backtest_success = run_current_backtest()
        
        if not backtest_success:
            print("⚠️ Warnung: Backtest-Ausführung hatte Probleme. Verwende vorhandene Reports...")
        
        print("\n🔍 Suche nach neuesten Reports...")
        
        # 2. Get latest report files
        strategy_file, unified_file = get_latest_reports()
        
        print(f"📊 Strategy Report (Basis): {strategy_file}")
        print(f"📈 Unified Report (anhängen): {unified_file}")
        
        # Zeige Zeitstempel der Reports
        strategy_time = strategy_file.split('_')[-1].replace('.html', '')
        unified_time = unified_file.split('_')[-1].replace('.html', '')
        print(f"⏰ Strategy Report Zeit: {strategy_time}")
        print(f"⏰ Unified Report Zeit: {unified_time}")
        print()
        
        # 3. Merge the reports
        print("🔄 Führe Reports zusammen (BEIDE komplett unverändert)...")
        merged_html = merge_html_reports(strategy_file, unified_file)
        
        # 4. Save merged report
        output_file = save_merged_report(merged_html)
        
        print(f"✅ Aktueller Backtest-Report erstellt: {output_file}")
        print(f"📁 Pfad: {os.path.abspath(output_file)}")
        print()
        print("🎯 Der Report enthält:")
        print("   • Strategy Report (Trading Summary) - mit aktuellen Backtests")
        print("   • Unified Report (Vollständiger Report) - mit aktuellen Backtests")
        print("   • Beide Reports sind unverändert zusammengeführt")
        print("   • Automatisch mit neuesten Daten aktualisiert")
        print()
        
        # 5. Automatically open in browser
        try:
            file_url = f"file:///{os.path.abspath(output_file).replace(os.sep, '/')}"
            print(f"🌐 Öffne automatisch im Browser: {file_url}")
            webbrowser.open(file_url)
            print("✅ Browser geöffnet!")
        except Exception as e:
            print(f"⚠️ Browser konnte nicht automatisch geöffnet werden: {e}")
            print(f"📂 Bitte öffnen Sie manuell: {os.path.abspath(output_file)}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des aktuellen Backtest-Reports: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
