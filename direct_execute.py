#!/usr/bin/env python3

print("STARTE BITPANDA PAPER TRADING...")

try:
    # Direct execution
    import subprocess
    import sys
    
    result = subprocess.run([sys.executable, "signal_transmitter.py"], 
                          capture_output=True, text=True, timeout=60)
    
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("RETURN CODE:", result.returncode)
    
    if result.returncode == 0:
        print("✅ ERFOLGREICH AUSGEFÜHRT")
    else:
        print("❌ FEHLER BEI AUSFÜHRUNG")
        
except Exception as e:
    print("FEHLER:", str(e))

print("ABGESCHLOSSEN")
