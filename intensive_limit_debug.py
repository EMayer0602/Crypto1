#!/usr/bin/env python3
"""
INTENSIVE Limit-Strategy Debug Session
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
        print('\n🔍 INTENSIVE LIMIT-STRATEGY DEBUGGING...')
        
        # SCHRITT 1: Aktueller Status
        print('\n📊 SCHRITT 1: Aktueller UI Status')
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        if 'Strategie auswählen' in body_text:
            print('❌ "Strategie auswählen" ist noch sichtbar')
        else:
            print('✅ "Strategie auswählen" ist nicht sichtbar')
            
        if 'Limit' in body_text:
            print('✅ "Limit" ist irgendwo im UI')
        else:
            print('❌ "Limit" ist nicht im UI')
        
        # SCHRITT 2: Alle Elemente mit "Strategie" finden
        print('\n📋 SCHRITT 2: Alle Strategie-Elemente')
        strategy_elements = driver.find_elements(By.XPATH, "//*[contains(text(),'Strategie')]")
        
        for i, elem in enumerate(strategy_elements):
            try:
                tag = elem.tag_name
                text = elem.text.strip()[:50]
                visible = elem.is_displayed()
                enabled = elem.is_enabled()
                classes = elem.get_attribute('class') or ''
                
                print(f'   [{i}] {tag}: "{text}" | visible={visible} | enabled={enabled}')
                if 'auswählen' in text and visible and enabled:
                    print(f'       🎯 DIESER IST UNSER DROPDOWN TRIGGER!')
                    
                    # Versuche direkten Klick
                    print(f'       🔄 Teste direkten Klick...')
                    try:
                        driver.execute_script("arguments[0].click();", elem)
                        time.sleep(1)
                        print(f'       ✅ Klick ausgeführt')
                        
                        # Prüfe was passiert ist
                        new_text = driver.find_element(By.TAG_NAME, 'body').text
                        if 'Market' in new_text or 'Stop' in new_text:
                            print(f'       ✅ DROPDOWN GEÖFFNET! Market/Stop sichtbar')
                            break
                        else:
                            print(f'       ❌ Dropdown nicht geöffnet')
                            
                    except Exception as e:
                        print(f'       ❌ Klick fehlgeschlagen: {e}')
                        
            except Exception as e:
                print(f'   [{i}] Fehler: {e}')
        
        # SCHRITT 3: Warte und suche Limit
        print('\n🎯 SCHRITT 3: Suche Limit-Optionen')
        time.sleep(1)
        
        limit_elements = driver.find_elements(By.XPATH, "//*[contains(text(),'Limit')]")
        print(f'Gefundene Limit-Elemente: {len(limit_elements)}')
        
        for i, elem in enumerate(limit_elements):
            try:
                tag = elem.tag_name
                text = elem.text.strip()
                visible = elem.is_displayed()
                enabled = elem.is_enabled()
                
                print(f'   [{i}] {tag}: "{text}" | visible={visible} | enabled={enabled}')
                
                if visible and enabled and text == 'Limit':
                    print(f'       🎯 PERFEKTER LIMIT KANDIDAT!')
                    try:
                        driver.execute_script("arguments[0].click();", elem)
                        time.sleep(1)
                        print(f'       ✅ Limit geklickt')
                        
                        # Prüfe Erfolg
                        final_text = driver.find_element(By.TAG_NAME, 'body').text
                        if 'Strategie auswählen' not in final_text:
                            print(f'       🎉 ERFOLG! Strategie auswählen ist weg!')
                            break
                        else:
                            print(f'       ❌ Strategie auswählen noch da')
                            
                    except Exception as e:
                        print(f'       ❌ Limit-Klick Fehler: {e}')
                        
            except Exception as e:
                print(f'   [{i}] Fehler: {e}')
        
        # SCHRITT 4: Final Status
        print('\n📊 SCHRITT 4: Final Status Check')
        final_body = driver.find_element(By.TAG_NAME, 'body').text
        if 'Strategie auswählen' in final_body:
            print('❌ LIMIT NICHT AKTIVIERT - Strategie auswählen noch da')
        else:
            print('✅ LIMIT AKTIVIERT - Strategie auswählen ist weg!')
            
        if 'Limitpreis' in final_body:
            print('✅ Limitpreis-Feld ist sichtbar!')
        else:
            print('❌ Limitpreis-Feld nicht sichtbar')
        
        print('\n🎯 Debug Session abgeschlossen.')
        
    except Exception as e:
        print(f'❌ Debug Fehler: {e}')
        import traceback
        traceback.print_exc()
    
    input('ENTER zum Beenden...')

if __name__ == '__main__':
    main()
