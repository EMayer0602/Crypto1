#!/usr/bin/env python3
"""
Analysiere die Strategie-Auswahl UI Structure
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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
        print('\n🔍 Analysiere Strategie-Auswahl UI...')
        
        # Suche alle Elemente mit "Strategie"
        strategy_elements = driver.find_elements(By.XPATH, "//*[contains(text(),'Strategie')]")
        
        print(f'\n📋 Gefundene Strategie-Elemente: {len(strategy_elements)}')
        for i, elem in enumerate(strategy_elements[:5]):
            try:
                tag = elem.tag_name
                text = elem.text
                classes = elem.get_attribute('class') or ''
                role = elem.get_attribute('role') or ''
                clickable = elem.is_enabled() and elem.is_displayed()
                
                print(f'   [{i}] {tag}: "{text}" | class="{classes}" | role="{role}" | clickable={clickable}')
                
                if clickable and 'auswählen' in text:
                    print(f'       🎯 DIES IST DER DROPDOWN TRIGGER!')
                    
            except Exception as e:
                print(f'   [{i}] Fehler: {e}')
        
        # Teste den direkten Klick auf das erste "Strategie auswählen" Element
        try:
            auswahl_elem = driver.find_element(By.XPATH, "//*[contains(text(),'Strategie auswählen')]")
            if auswahl_elem.is_displayed() and auswahl_elem.is_enabled():
                print(f'\n🎯 Teste direkten Klick auf Strategie auswählen...')
                print(f'   Element: {auswahl_elem.tag_name} | Text: "{auswahl_elem.text}"')
                
                # JavaScript Click
                driver.execute_script("arguments[0].click();", auswahl_elem)
                time.sleep(1)
                
                print(f'   ✅ Klick ausgeführt, warte auf UI Update...')
                
                # Prüfe ob sich was geändert hat
                new_body_text = driver.find_element(By.TAG_NAME, 'body').text
                if 'Limit' in new_body_text and 'Market' in new_body_text:
                    print(f'   ✅ Dropdown geöffnet! Limit und Market sichtbar')
                else:
                    print(f'   ❌ Dropdown nicht geöffnet')
                    
        except Exception as e:
            print(f'❌ Dropdown Test Fehler: {e}')
        
        print('\n🎯 Analyse abgeschlossen.')
        
    except Exception as e:
        print(f'❌ Analyse Fehler: {e}')
        import traceback
        traceback.print_exc()
    
    input('ENTER zum Beenden...')

if __name__ == '__main__':
    main()
