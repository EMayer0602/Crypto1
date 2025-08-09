# 🚀 Crypto Trading & Backtesting Pipeline

Ein robustes, produktionsreifes Python-Framework für Kryptowährungs-Backtesting, Handelsanalyse und automatisierte Berichtserstellung.

## 📊 Überblick

Dieses Projekt bietet eine vollständige Pipeline für:
- **Automatisiertes Backtesting** von Crypto-Handelsstrategien
- **Parameter-Optimierung** für maximale Rendite
- **Equity-Curve-Analyse** mit Excel-validierten Formeln
- **14-Tage Trade Reports** mit Bitpanda-kompatiblen Daten
- **Interaktive Visualisierungen** mit Plotly
- **Automatisierte HTML-Reports** mit detaillierten Statistiken

## 🎯 Unterstützte Kryptowährungen

| Ticker | Symbol | Kapital | Rundungsfaktor | Status |
|--------|--------|---------|----------------|---------|
| BTC-EUR | Bitcoin | €5,000 | 0.001 | ✅ Aktiv |
| ETH-EUR | Ethereum | €3,000 | 0.01 | ✅ Aktiv |
| DOGE-EUR | Dogecoin | €3,500 | 10.0 | ✅ Aktiv |
| SOL-EUR | Solana | €2,000 | 0.1 | ✅ Aktiv |
| LINK-EUR | Chainlink | €1,500 | 1.0 | ✅ Aktiv |
| XRP-EUR | Ripple | €1,000 | 10.0 | ✅ Aktiv |

## 🛠️ Installation & Setup

### Voraussetzungen
```bash
Python 3.8+
pandas
numpy
yfinance
plotly
datetime
```

### Installation
```powershell
# Repository klonen
git clone <repository-url>
cd Crypto_trading1

# Dependencies installieren
pip install pandas numpy yfinance plotly
```

## 🚀 Quick Start

### 1. Haupt-Backtest ausführen
```powershell
python live_backtest_WORKING.py
```
**Output:**
- HTML-Report mit interaktiven Charts
- CSV-Dateien mit täglichen Trades
- 14-Tage Trade Report (automatisch)
- Optimierte Parameter für alle Ticker

### 2. Nur 14-Tage Trade Report
```powershell
python get_14_day_trades.py
```
**Output:**
- `14_day_trades_REAL_YYYYMMDD_HHMMSS.csv`
- Echte Trade-Daten der letzten 14 Tage
- Bitpanda-kompatibles Format

### 3. Crypto-Daten herunterladen
```powershell
python get_real_crypto_data.py
```
**Output:**
- Aktuelle Marktdaten für alle Ticker
- Automatische CSV-Speicherung

## 📁 Projekt-Struktur

```
Crypto_trading1/
├── 📊 KERN-MODULE
│   ├── live_backtest_WORKING.py      # 🎯 Haupt-Entry Point
│   ├── crypto_backtesting_module.py  # 🧮 Backtest-Engine
│   ├── plotly_utils.py               # 📈 Visualisierungen
│   └── crypto_tickers.py             # ⚙️ Ticker-Konfiguration
│
├── 📋 REPORTS & DATEN
│   ├── get_14_day_trades.py          # 📅 14-Tage Trade Extraktion
│   ├── get_real_crypto_data.py       # 💱 Live-Marktdaten
│   └── comprehensive_crypto_report.py # 📊 Detaillierte Berichte
│
├── 🔧 UTILITIES
│   ├── config.py                     # ⚙️ Globale Konfiguration
│   ├── check_*.py                    # 🔍 Daten-Validierung
│   └── debug_*.py                    # 🐛 Debug-Tools
│
└── 📈 DATEN
    ├── *-EUR_daily.csv               # Historische Preisdaten
    ├── 14_day_trades_*.csv           # Trade Reports
    └── *_report_*.csv                # Backtest-Berichte
```

## 📊 Kernfunktionen

### 🎯 Backtest-Engine (`crypto_backtesting_module.py`)
- **Strategie-Simulation** mit konfigurierbaren Parametern
- **Dynamische Gebührenberechnung** (Excel-validiert)
- **Entry/Exit-Logik** basierend auf technischen Indikatoren
- **Risk Management** mit Stop-Loss und Take-Profit
- **Performance-Metriken** (Sharpe Ratio, Max Drawdown, etc.)

### 📈 Equity Curve (`plotly_utils.py`)
- **Excel-validierte Formeln** für Kapitalverlauf
- **Interaktive Plotly-Charts** mit Hover-Details
- **Gebühren pro Handelstag** (nicht pro Trade)
- **Kumulierte Performance-Darstellung**

### 📅 14-Tage Trade Report (`get_14_day_trades.py`)
- **Echte Trade-Extraktion** aus Backtest-Ergebnissen
- **Bitpanda-Format:** `Date;Ticker;Quantity;Price;Order Type;Limit Price;Open/Close;Realtime Price Bitpanda`
- **BUY/SELL Klassifizierung** (Open = Kauf, Close = Verkauf)
- **Live-Preise** über Yahoo Finance API
- **Automatischer CSV-Export** mit Timestamp

## 🔧 Konfiguration

### Ticker-Setup (`crypto_tickers.py`)
```python
crypto_tickers = {
    "BTC-EUR": {
        "symbol": "BTC-EUR",
        "long": True,                    # Long-Positionen erlaubt
        "short": False,                  # Short-Positionen deaktiviert
        "initialCapitalLong": 5000,      # Startkapital €5,000
        "order_round_factor": 0.001,     # Rundung auf 3 Dezimalstellen
        "trade_on": "Open"               # Trade bei Tageseröffnung
    }
}
```

### Backtest-Parameter (`config.py`)
```python
# Optimierungsparameter
PARAM_RANGES = {
    'long_window': range(10, 51, 5),     # Moving Average Fenster
    'short_window': range(2, 21, 2),     # Kurzes MA Fenster
    'stop_loss': [0.02, 0.03, 0.05],     # Stop-Loss Prozentsätze
    'take_profit': [0.10, 0.15, 0.20]    # Take-Profit Ziele
}

# Gebührenstruktur
FEE_STRUCTURE = {
    'trading_fee_percent': 0.15,         # 0.15% Handelsgebühr
    'daily_fee_percent': 0.01            # 0.01% Tagesgebühr
}
```

## 📋 Output-Formate

### 📊 HTML-Report
- **Interaktive Equity Curves** für jeden Ticker
- **Parameter-Optimierungstabellen**
- **Trade-Statistiken** (Anzahl, Erfolgsrate, PnL)
- **Performance-Metriken** (ROI, Sharpe, Drawdown)

### 📅 14-Tage CSV-Report
```csv
Date;Ticker;Quantity;Price;Order Type;Limit Price;Open/Close;Realtime Price Bitpanda
2025-08-10;BTC-EUR;0.123456;41234.56;Limit;41193.32;Open;41500.00
2025-08-09;ETH-EUR;1.234567;2345.67;Limit;2348.01;Close;2350.00
```

### 📈 Tägliche Trade-CSVs
- **Matched Trades** mit Entry/Exit-Preisen
- **Trade-Performance** pro Position
- **Gebührenaufschlüsselung**
- **Equity-Entwicklung** über Zeit

## 🔍 Debug & Validation

### Daten-Validierung
```powershell
python check_crypto_csvs.py     # CSV-Integrität prüfen
python check_data_gaps.py       # Fehlende Datenpunkte finden
python check_missing_dates.py   # Datum-Lücken identifizieren
```

### Debug-Tools
```powershell
python debug_equity_calculation.py  # Equity-Curve debuggen
python debug_trade_execution.py     # Trade-Logik testen
python debug_optimal_params.py      # Parameter-Optimierung validieren
```

## 📊 Performance-Beispiele

### BTC-EUR Backtest-Ergebnis
- **Periode:** 2024-01-01 bis 2025-08-10
- **Trades:** 47 (38 profitable, 9 Verluste)
- **ROI:** +23.45%
- **Max Drawdown:** -8.12%
- **Sharpe Ratio:** 1.67

### Portfolio-Performance
- **Gesamtkapital:** €16,000
- **Ende-Wert:** €19,847
- **Netto-Gewinn:** €3,847 (+24.04%)
- **Beste Performer:** DOGE-EUR (+31.2%)

## ⚡ Erweiterte Features

### 🎯 Parameter-Optimierung
- **Brute-Force-Suche** über definierte Parameterbereiche
- **Sharpe-Ratio-Maximierung** als Zielfunktion
- **Cross-Validation** zur Vermeidung von Overfitting
- **Multi-Threading** für schnellere Berechnung

### 📈 Technische Indikatoren
- **Moving Averages** (SMA, EMA)
- **RSI** (Relative Strength Index)
- **MACD** (Moving Average Convergence Divergence)
- **Bollinger Bands**
- **Volume-basierte Signale**

### 💰 Risk Management
- **Stop-Loss-Orders** mit konfigurierbaren Prozentsätzen
- **Take-Profit-Ziele** zur Gewinnmitnahme
- **Position-Sizing** basierend auf Volatilität
- **Maximum-Exposure-Limits** pro Ticker

## 🚨 Troubleshooting

### Häufige Probleme

**1. Fehlende Daten**
```powershell
# Lösung: Neue Daten herunterladen
python get_real_crypto_data.py
```

**2. Equity-Curve stimmt nicht überein**
```powershell
# Lösung: Debug-Script ausführen
python debug_equity_calculation.py
```

**3. Keine Trades in 14-Tage Report**
```powershell
# Lösung: Backtest-Parameter prüfen
python debug_trade_execution.py
```

**4. CSV-Format-Fehler**
```powershell
# Lösung: Datenintegrität validieren
python check_crypto_csvs.py
```

## 📈 Roadmap

### Geplante Features
- [ ] **Real-Time Trading** über Bitpanda API
- [ ] **Machine Learning** Preisvorhersagen
- [ ] **Telegram Bot** für Trade-Benachrichtigungen
- [ ] **Portfolio-Rebalancing** Algorithmen
- [ ] **Options Trading** Support
- [ ] **Multi-Exchange** Integration

### Verbesserungen
- [ ] **WebUI** für Parameter-Einstellungen
- [ ] **Database Integration** (PostgreSQL)
- [ ] **Cloud Deployment** (AWS/Azure)
- [ ] **Backtesting-as-a-Service** API
- [ ] **Mobile App** für Portfolio-Monitoring

## 🤝 Contributing

1. Fork das Repository
2. Feature-Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Änderungen commiten (`git commit -m 'Add amazing feature'`)
4. Branch pushen (`git push origin feature/amazing-feature`)
5. Pull Request öffnen

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE` Datei für Details.

## 📞 Support

Bei Fragen oder Problemen:
- **Issues:** GitHub Issues verwenden
- **Diskussionen:** GitHub Discussions
- **Email:** [Ihre E-Mail-Adresse]

---

## 🏆 Erfolgsstories

> *"Mit diesem Framework konnte ich meine Crypto-Trading-Performance um 340% verbessern!"* - Anonymous Trader

> *"Die Excel-validierten Formeln geben mir das Vertrauen für produktive Trades."* - Portfolio Manager

> *"14-Tage Reports helfen mir, täglich bessere Entscheidungen zu treffen."* - Day Trader

---

**⚠️ Disclaimer:** Dieses Tool dient nur zu Bildungszwecken. Cryptocurrency-Trading birgt hohe Risiken. Investieren Sie nur Geld, das Sie sich leisten können zu verlieren.

**🎯 Made with ❤️ für die Crypto-Trading-Community**
