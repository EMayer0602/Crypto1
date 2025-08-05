# 📊 Handelsparameter
COMMISSION_RATE = 0.0018   # 0,18 % Gebühren pro Trade
MIN_COMMISSION = 1.0       # Mindestprovision in EUR
ORDER_SIZE = 100           # Standardgröße (nicht direkt genutzt)
ORDER_ROUND_FACTOR = 0.01     # Globale Rundungseinheit (wird meist im Ticker überschrieben)

# Zeitraum für Backtest in Jren (z.B. [1/12, 5] für 1 Monat bis 5 Jahre)
# config.py oder am Anfang deines Moduls
backtest_years = 1      # 1 Jahr
# backtest_years = 0.5    # 6 Monate  
# backtest_years = 0.25   # 3 Monate
# backtest_years = 1/12   # 1 Monat
#     # 2 Jahre
# backtest_years = 5      # 5 Jahre

# 🧪 Backtest-Bereich (in Prozent der Daten)
backtesting_begin = 25     # Beginne bei z. B. 25 % der Daten
backtesting_end = 95       # Ende bei z. B. 98 % der Daten

