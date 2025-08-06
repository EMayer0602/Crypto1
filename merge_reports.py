#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Merge both Crypto Trading Reports (Strategy + Summary) into one unified HTML report
"""

import os
import re
import webbrowser
from datetime import datetime
from bs4 import BeautifulSoup

def get_latest_reports():
    """Get the latest strategy report and unified report files"""
    current_dir = os.getcwd()
    
    # Find latest trading summary report (Strategy Report - Basis)
    # Find latest unified crypto report (wird angehängt)
    strategy_files = []  # trading_summary_report = Strategy Report (Basis)
    unified_files = []   # unified_crypto_report = wird angehängt
    
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
    
    # Find body or container to append unified content
    body = merged_soup.find('body')
    if not body:
        body = merged_soup
    
    # Add a separator section before unified report
    separator_section = BeautifulSoup('''
    <hr style="margin: 50px 0; border: 2px solid #3498db;">
    <div style="text-align: center; margin: 30px 0; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h2 style="color: #3498db; margin: 0;">� Unified Crypto Trading Report</h2>
        <p style="margin: 10px 0; color: #7f8c8d;">Unverändert angehängt</p>
    </div>
    ''', 'html.parser')
    
    # Append separator
    body.append(separator_section)
    
    # Extract content from unified report (everything inside body, excluding head)
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
    filename = f"COMBINED_crypto_reports_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(merged_html)
    
    return filename

def main():
    """Main function to merge reports"""
    try:
        print("🔍 Suche nach neuesten Reports...")
        
        # Get latest report files
        strategy_file, unified_file = get_latest_reports()
        
        print(f"📊 Strategy Report (Basis): {strategy_file}")
        print(f"📈 Unified Report (anhängen): {unified_file}")
        print()
        
        print("🔄 Führe Reports zusammen (Strategy Report als Basis + Unified Report UNVERÄNDERT anhängen)...")
        
        # Merge the reports
        merged_html = merge_html_reports(strategy_file, unified_file)
        
        # Save merged report
        output_file = save_merged_report(merged_html)
        
        print(f"✅ Kombinierter Report erstellt: {output_file}")
        print(f"📁 Pfad: {os.path.abspath(output_file)}")
        print()
        print("🎯 Der kombinierte Report enthält:")
        print("   • Strategy Report (Trading Summary Report) - KOMPLETT UNVERÄNDERT")
        print("   • Unified Report (Unified Crypto Trading Report) - KOMPLETT UNVERÄNDERT angehängt")
        print("   • Beide Reports sind 100% unverändert - nur zusammengefügt")
        print()
        
        # Automatically open in browser
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
        print(f"❌ Fehler beim Zusammenführen der Reports: {e}")
        return None

if __name__ == "__main__":
    main()
