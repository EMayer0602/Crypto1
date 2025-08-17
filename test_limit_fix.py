#!/usr/bin/env python3
"""
Direkter Test der Limit-Strategie Fix
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
        print('\n🔍 Teste Limit-Strategie Fix direkt...')
        
        from fusion_ui_fixes import fix_limit_strategy
        
        print('\n🎯 Teste Limit Strategy mit max Debug...')
        result = fix_limit_strategy(driver, debug=True)
        
        if result:
            print('✅ Limit Strategie erfolgreich!')
        else:
            print('❌ Limit Strategie fehlgeschlagen!')
            
        print('\n📊 Aktueller UI Status:')
        try:
            body_text = driver.find_element('tag name', 'body').text
            if 'Strategie auswählen' in body_text:
                print('❌ "Strategie auswählen" immer noch sichtbar')
            else:
                print('✅ "Strategie auswählen" nicht mehr sichtbar')
                
            if 'Limit' in body_text:
                print('✅ "Limit" ist im UI sichtbar')
            else:
                print('❌ "Limit" ist nicht sichtbar')
        except Exception as e:
            print(f'⚠️ UI Check Fehler: {e}')
        
        print('\n🎯 Test abgeschlossen. Prüfen Sie die UI...')
        
    except Exception as e:
        print(f'❌ Test Fehler: {e}')
        import traceback
        traceback.print_exc()
    
    input('ENTER zum Beenden...')

if __name__ == '__main__':
    main()
