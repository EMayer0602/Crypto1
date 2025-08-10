print("TEST - Python funktioniert!")
import datetime
print(f"Zeit: {datetime.datetime.now()}")

try:
    import pandas
    print("✅ Pandas verfügbar")
except ImportError:
    print("❌ Pandas nicht verfügbar")

try:
    import requests
    print("✅ Requests verfügbar")  
except ImportError:
    print("❌ Requests nicht verfügbar")

print("TEST ABGESCHLOSSEN")
