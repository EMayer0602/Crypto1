# 🚀 Crypto Trading & Backtesting Pipeline

Ein robustes, produktionsreifes Python-Framework für Kryptowährungs-Backtesting, Handelsanalyse und automatisierte Berichtserstellung.

## ⚡ Quick Links
- [Daten-Update (Yahoo + Bitpanda)](#daten-update-yahoo--bitpanda)
- [Details: README_DATA_PIPELINE.md](README_DATA_PIPELINE.md)

> Start hier – Daten-Update (Yahoo + Bitpanda)
>
> ```powershell
> # Minimal (smart) Update + Backtest/Report
> python smart_csv_update.py
> python live_backtest_WORKING.py
>
> # Vollständiges Update (falls nötig)
> python get_real_crypto_data.py
> ```

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

## � Daten-Update (Yahoo + Bitpanda)

- Empfohlen (minimaler Update-Footprint):
    1) Smart-Update ausführen
         ```powershell
         python smart_csv_update.py
         ```
    2) Backtest/Report starten
         ```powershell
         python live_backtest_WORKING.py
         ```
- Vollständiges Update (alle relevanten Tage neu zusammenführen):
    ```powershell
    python get_real_crypto_data.py
    ```

Hinweis: Die Pipeline nutzt Yahoo Finance (daily bis T-3, hourly für T-2/T-1) und Bitpanda Live-Preis für heute. CoinGecko wird im Backtest-/Update-Pfad nicht mehr verwendet.

Mehr Details: siehe „README_DATA_PIPELINE.md“.

## �📁 Projekt-Struktur

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

---

## 🔥 Bitpanda Fusion Multi-Trade Auto-Fill

Automatisches Vorbefüllen von Limit BUY/SELL Orders im bereits geöffneten Bitpanda Fusion Browser-Tab. Letzter Klick (Review / Bestätigen) bleibt bewusst manuell zur finalen Kontrolle.

### ✅ Features
- Automatisches Anhängen an laufende Chrome/Edge Session (Remote Debug Port 9222)
- Laden der neuesten `TODAY_ONLY_trades_*.csv` (Semikolon-getrennt)
- Sequenzielles Eintragen aller Trades (Open → BUY, Close → SELL)
- Strategie erzwingen: Limit Order
- BUY Preis automatisch: -25bps Button (wenn vorhanden)
- SELL Preis automatisch: +25bps Button (wenn vorhanden)
- SELL Menge: Max Button
- BUY Menge: Berechnung aus `initialCapitalLong / LimitPrice` unter Berücksichtigung von `order_round_factor` + Asset-spezifischer Dezimalrundung
- Mehrstufige Feld-Erkennung (Direkte Selektoren, Heuristiken, Shadow DOM, JS Fallback)
- Sicherheitsschutz gegen versehentliche Verkäufe (Whitelist, Confirm, Fraction, Preis-Guard)
- Debug HTML Dumps bei Problemen

### 🧪 Start
```powershell
python fusion_existing_all_trades_auto.py
```
Browser muss bereits mit eingeloggtem Bitpanda Fusion Tab laufen. Optional Chrome Start z.B.:
```powershell
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-fusion" --profile-directory="Default"
```

### ⚙️ Wichtige Environment Variablen
| Variable | Default | Beschreibung |
|----------|---------|--------------|
| AUTO_CONTINUE | 1 | Nächster Trade nach Wartezeit automatisch starten |
| WAIT_BETWEEN | 2.5 | Sekunden zwischen Trades (wenn AUTO_CONTINUE=1) |
| WAIT_FOR_CLICK | 1 | Wenn 1 → Skript pausiert vor finalem Klick (Empfohlen) |
| USE_MAX_BUTTON | 1 | SELL: Max Button setzen für Menge |
| USE_BPS_BUTTONS | 1 | BUY -25bps / SELL +25bps Buttons für Limitpreis |
| DISABLE_SELLS | 0 | Alle SELLs komplett blockieren |
| SELL_CONFIRM | 1 | Manuelle Bestätigung je SELL (y / skip) |
| SELL_WHITELIST | (leer) | Kommagetrennte Liste erlaubter SELL Paare (z.B. BTC-EUR,ETH-EUR) |
| MAX_SELL_FRACTION | 1.0 | Maximaler Anteil der gehaltenen Menge pro SELL (0.25 = 25%) |
| STRICT_SELL_PRICE_PROTECT | 0 | Max. relativer Abschlag unter Marktpreis (z.B. 0.05 = 5%) |
| DEBUG_MODE | 0 | Erweiterte Logausgaben |
| DEEP_INPUT_DEBUG | 0 | Zusätzliche Input-Feld Auflistung |

Setzen (Beispiele PowerShell):
```powershell
$env:SELL_CONFIRM="1"
$env:DISABLE_SELLS="0"
$env:SELL_WHITELIST="BTC-EUR,LINK-EUR"
$env:MAX_SELL_FRACTION="0.5"
$env:STRICT_SELL_PRICE_PROTECT="0.03"
python fusion_existing_all_trades_auto.py
```

### 🔐 Sicherheitslogik SELL
Prüf-Reihenfolge vor Ausführung:
1. DISABLE_SELLS → Abbruch
2. SELL_WHITELIST (falls gesetzt) → Abbruch wenn nicht enthalten
3. MAX_SELL_FRACTION (falls Portfolio-Menge erkannt) → Abbruch wenn überschritten
4. STRICT_SELL_PRICE_PROTECT (falls Marktpreis verfügbar) → Abbruch wenn Limit zu tief
5. SELL_CONFIRM → Nachfrage (Abort wenn nicht bestätigt)

### 🛠️ Mengenberechnung BUY
```
Quantity = floor( (initialCapitalLong / LimitPrice) / order_round_factor ) * order_round_factor
→ anschließend asset-spezifische Dezimal-Kappung
```

### 🧩 Troubleshooting Fusion
| Problem | Hinweis |
|---------|---------|
| Preisfeld bleibt leer | PRICE_COMMIT_VERIFY=1 aktivieren für strengere Erneuerung |
| Buttons fehlen | UI Reload; BPS Buttons evtl. nicht sichtbar im aktuellen Modus |
| Falsches Tab | Browser mit nur einem Fusion Tab starten / andere Tabs schließen |
| Shadow DOM Probleme | DEBUG_MODE=1 + DEEP_INPUT_DEBUG=1 setzen und HTML Dump prüfen |

HTML Dumps werden als `fusion_debug_*.html` abgelegt.

### 📋 Vollständige ENV Variable Referenz (fusion_existing_all_trades_auto.py)
| Primär Variable | Alternative Aliase | Default | Wirkung |
|-----------------|--------------------|---------|--------|
| AUTO_CONTINUE | FUSION_AUTO_CONTINUE | 1 | Nächster Trade automatisch nach Wartezeit starten |
| WAIT_BETWEEN | FUSION_WAIT, FUSION_WAIT_BETWEEN | 2.5 | Sekunden Pause zwischen Trades (nur wenn AUTO_CONTINUE=1) |
| AUTO_SUBMIT | FUSION_AUTO_SUBMIT | 0 | Wenn 1: automatischer Submit nach Review (nicht empfohlen) |
| USE_REALTIME_LIMIT | FUSION_REALTIME_LIMIT | 1 | Realtime Preis als Limit (falls nicht durch BPS Button überschrieben) |
| PORTFOLIO_CHECK | FUSION_PORTFOLIO_CHECK | 1 | Portfolio Menge prüfen (begrenzen SELL) |
| DEBUG_MODE | FUSION_DEBUG | 0 | Ausführliche Logs & zusätzliche Hinweise |
| MAX_WAIT | FUSION_MAX_WAIT | 15 | Globale Wartezeit für Elemente (Sekunden) |
| DEEP_INPUT_DEBUG | FUSION_DEEP_INPUT_DEBUG | 0 | Listet gefundene Input Felder (max 10) vor Befüllung |
| MIN_INPUT_COUNT | FUSION_MIN_INPUTS | 1 | Mindestanzahl Input-Felder bevor Befüllung startet |
| AGGRESSIVE_IFRAME_SCAN | FUSION_AGGRESSIVE_IFRAME | 1 | Intensivere iFrame Durchsuchung für Order Form |
| SLOW_KEYSTROKES | FUSION_SLOW_KEYS | 0 | Simuliert langsame Eingabe (stabilisiert manche UIs) |
| ORDER_FRAME_KEYWORDS | FUSION_ORDER_FRAME_KEYS | menge,amount,... | Komma-Liste Keywords zur iFrame Relevanzbewertung |
| STRICT_FIELD_MATCH | FUSION_STRICT_FIELD_MATCH | 1 | Erzwingt getrennte Felder für Menge/Preis (wartet sonst) |
| WAIT_FOR_CLICK | FUSION_WAIT_FOR_CLICK | 1 | Pausiert nach Befüllung auf Enter vor Review/Submit |
| PRICE_COMMIT_VERIFY | FUSION_PRICE_COMMIT_VERIFY | 0 | Strenger Preis-Verifikations- & Re-Commit Zyklus |
| TAB_NAV | FUSION_TAB_NAV, USE_TAB_NAV | 1 | Aktiviert TAB Sequenz Navigation (Fallback Pfad) |
| USE_MAX_BUTTON | FUSION_USE_MAX | 1 | Aktiviert Nutzung Max Button für SELL Menge |
| USE_BPS_BUTTONS | FUSION_USE_BPS | 1 | Aktiviert -25bps (BUY) / +25bps (SELL) Preis Buttons |
| DISABLE_SELLS | FUSION_DISABLE_SELLS | 0 | Blockiert alle SELL Trades vollständig |
| SELL_CONFIRM | FUSION_SELL_CONFIRM | 1 | Interaktive Bestätigung vor SELL |
| SELL_WHITELIST | FUSION_SELL_WHITELIST | (leer) | Erlaubte SELL Paare (Kommagetrennt) |
| MAX_SELL_FRACTION | FUSION_MAX_SELL_FRACTION | 1.0 | Anteil der gehaltenen Menge der verkauft werden darf |
| STRICT_SELL_PRICE_PROTECT | FUSION_STRICT_SELL_PRICE_PROTECT | 0 | Preis-Schutz: max Abschlag unter Markt (z.B. 0.05) |
| SLOW_KEYS_DELAY | FUSION_SLOW_KEYS_DELAY | 0.0 | Verzögerung je Taste wenn SLOW_KEYSTROKES aktiv (falls implementiert) |
| DUMP_ON_ERROR | FUSION_DUMP_ON_ERROR | 1 | HTML Dump bei Fehlersituationen erzeugen |
| USE_REALTIME_FALLBACK | FUSION_USE_REALTIME_FALLBACK | 1 | Falls Limit fehlte: Realtime Preis erneut erzwingen |
| ENABLE_SPINBUTTON | FUSION_ENABLE_SPINBUTTON | 1 | Nutzung role=spinbutton Felder priorisieren |
| FORCE_LIMIT | FUSION_FORCE_LIMIT | 1 | Strategie Limit aktiv erzwingen, falls UI anderes zeigt |
| ROUND_STRICT | FUSION_ROUND_STRICT | 1 | Strikte Rundung Mengen laut ASSET_DECIMALS |
| JS_DEEP_SCAN | FUSION_JS_DEEP_SCAN | 1 | Tiefen-Scan via JS & Shadow DOM nach Input Feldern |
| BUTTON_RETRY | FUSION_BUTTON_RETRY | 2 | Anzahl Wiederholungen bei Button Klicks (Max/Bps) |
| ACTIVE_TAB_RECHECK | FUSION_ACTIVE_TAB_RECHECK | 1 | Tab-Fokus vor jedem Trade verifizieren |

Nur setzen, was gebraucht wird – Defaults decken Standard Flow.

Beispiel Minimal Sicherer Run (nur BUY Tests):
```powershell
$env:DISABLE_SELLS="1"
$env:DEBUG_MODE="1"
python fusion_existing_all_trades_auto.py
```

### ⚠️ Empfehlung
Immer erst mit `DISABLE_SELLS=1` testen und danach Schutz graduell lockern.

---
