#!/usr/bin/env python3
"""
Direkter Test der UI-Fixes
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def attach_to_debug_chrome():
    options = Options()
    options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    try:
        driver = webdriver.Chrome(options=options)
        print('✅ Mit Debug Chrome verbunden')
        return driver
    except Exception as e:
        print(f'❌ Verbindung fehlgeschlagen: {e}')
        return None

def main():
    driver = attach_to_debug_chrome()
    if not driver:
        return
    
    try:
        print('\n🔍 Teste UI-Fixes direkt...')
        
        # Import unserer UI-Fixes
        from fusion_ui_fixes import fix_pair_selection_soleur, fix_limit_strategy, fix_max_button, fix_bps_plus25
        
        print('\n1️⃣ Teste SOL-EUR Selection...')
        if fix_pair_selection_soleur(driver, debug=True):
            print('✅ SOL-EUR erfolgreich')
        else:
            print('❌ SOL-EUR fehlgeschlagen')
        
        time.sleep(2)
        
        print('\n2️⃣ Teste Limit Strategy...')
        if fix_limit_strategy(driver, debug=True):
            print('✅ Limit Strategie erfolgreich')
        else:
            print('❌ Limit Strategie fehlgeschlagen')
        
        time.sleep(2)
        
        print('\n3️⃣ Teste MAX Button...')
        if fix_max_button(driver, debug=True):
            print('✅ MAX Button erfolgreich')
        else:
            print('❌ MAX Button fehlgeschlagen')
        
        time.sleep(2)
        
        print('\n4️⃣ Teste +25bps...')
        if fix_bps_plus25(driver, debug=True):
            print('✅ +25bps erfolgreich')
        else:
            print('❌ +25bps fehlgeschlagen')
        
        print('\n🎯 Test abgeschlossen. Prüfen Sie die UI...')
        
    except Exception as e:
        print(f'❌ Test Fehler: {e}')
        import traceback
        traceback.print_exc()
    
    # Driver offen lassen für Inspektion
    input('ENTER zum Beenden...')

if __name__ == '__main__':
    main()
