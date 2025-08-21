from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def diagnose_chrome_debug():
    print("🔍 Starte Diagnose...")

    # Schritt 1: Verbindung zur Debugging-Instanz
    options = Options()
    options.debugger_address = "127.0.0.1:57814"

    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Verbindung zu Chrome Debugging erfolgreich.")
    except Exception as e:
        print("❌ Verbindung zu Chrome Debugging fehlgeschlagen.")
        print("Fehler:", e)
        return

    # Schritt 2: Testseite öffnen
    try:
        driver.get("https://www.google.com")
        time.sleep(2)
        print("✅ Testseite erfolgreich geöffnet.")
    except Exception as e:
        print("❌ Fehler beim Öffnen der Testseite.")
        print("Fehler:", e)
        driver.quit()
        return

    # Schritt 3: Bitpanda-Seite prüfen
    try:
        driver.get("https://web.bitpanda.com/fusion/trade/BTC-EUR")
        time.sleep(5)
        print("✅ Bitpanda Fusion Seite geöffnet.")
    except Exception as e:
        print("❌ Fehler beim Öffnen der Bitpanda-Seite.")
        print("Fehler:", e)

    input("Drücke Enter zum Beenden...")
    driver.quit()

diagnose_chrome_debug()
