# 🏦 Bitpanda Fusion Paper Trading Integration

## 📋 Überblick

Diese Integration verbindet dein Crypto Trading Framework mit Bitpanda Fusion Paper Trading. Du kannst deine Backtest-Strategien in einer realistischen Umgebung testen, ohne echtes Geld zu riskieren.

## 🚀 Quick Start

### 1. Paper Trading Test starten
```powershell
python test_bitpanda_integration.py
```

### 2. Einzelne Paper Trading Session
```powershell
python bitpanda_fusion_adapter.py
```

### 3. Nur Konfiguration prüfen
```powershell
python bitpanda_config.py
```

## 🔧 Setup & Konfiguration

### API-Konfiguration

1. **Paper Trading (Simulation):**
   - Keine API-Keys erforderlich
   - Verwendet Yahoo Finance für Preisdaten
   - Vollständig simulierte Order-Ausführung

2. **Live Paper Trading (mit echten Bitpanda APIs):**
   ```python
   # In bitpanda_config.py
   BITPANDA_API_KEYS = {
       'paper_trading_key': 'DEIN_BITPANDA_API_KEY',
       'live_trading_key': 'NIEMALS_HIER_EINTRAGEN'
   }
   ```

### Portfolio-Konfiguration

```python
# Startkapital anpassen
PAPER_TRADING_CONFIG = {
    'initial_capital_eur': 16000.0,  # Dein Startkapital
    'min_order_size_eur': 50.0,     # Min Order-Größe
    'max_position_size_pct': 0.25,  # Max 25% pro Position
}
```

## 📊 Features

### ✅ **Was funktioniert:**
- **Paper Trading Simulation** mit realistischen Gebühren
- **Backtest-Signal Integration** - deine Strategien werden automatisch ausgeführt
- **Portfolio Management** - automatisches Rebalancing
- **Order-Simulation** - Buy/Sell Orders mit Limit-Preisen
- **Performance-Tracking** - detaillierte Reports
- **CSV-Export** - Bitpanda-kompatible Formate
- **Risk Management** - Stop-Loss, Position-Limits
- **Multi-Ticker Support** - alle deine 6 Cryptos

### 🔄 **Workflow:**
1. System führt Backtests für alle Ticker aus
2. Analysiert Performance und generiert Trading-Signale
3. Konvertiert Signale in Paper Trading Orders
4. Führt Orders im simulierten Portfolio aus
5. Trackt Performance und generiert Reports

## 📈 Trading-Strategien

### Momentum Strategy (Standard)
```python
# Kaufe wenn Backtest-Gewinnrate > 60%
if win_rate > 0.6:
    signal = 'BUY'
    
# Verkaufe wenn Backtest-Gewinnrate < 40%
if win_rate < 0.4:
    signal = 'SELL'
```

### Erweiterte Strategien
Du kannst eigene Strategien hinzufügen in `generate_trading_signal()`:

```python
def generate_trading_signal(self, ticker_name, recent_trades, current_prices):
    # Deine eigene Logik hier
    # Analysiere recent_trades DataFrame
    # Generiere BUY/SELL/HOLD Signal
    return {'action': 'BUY', 'strength': 0.8}
```

## 📋 Output-Formate

### Console Output
```
🚀 BITPANDA FUSION PAPER TRADING SESSION
📈 BTC-EUR: €41,234.56
✅ BUY Order: 0.024305 BTC-EUR @ €41,193.32
📊 Portfolio: €16,847.23 (+5.3%)
```

### CSV Reports
```csv
Date;Time;Ticker;Action;Quantity;Price;Value;Fees;Order_Type;Status
2025-08-10;14:30:15;BTC-EUR;BUY;0.024305;41193.32;1000.00;1.50;LIMIT;FILLED
2025-08-10;14:45:22;ETH-EUR;BUY;0.341242;2345.67;800.00;1.20;LIMIT;FILLED
```

### Portfolio Report
```
💰 PORTFOLIO ÜBERSICHT:
   💵 Cash: €13,200.00
   📈 Positionen: €3,647.23
   🎯 Gesamtwert: €16,847.23
   📊 Performance: €+847.23 (+5.30%)
```

## 🎯 Testszenarien

### 1. Basis-Test
```powershell
# Einfacher Test mit manuellen Orders
python test_bitpanda_integration.py
```

### 2. Multi-Tage Simulation
```powershell
# 7-Tage Simulation mit täglichem Rebalancing
python -c "
from test_bitpanda_integration import run_extended_simulation
run_extended_simulation(7)
"
```

### 3. Einzelne Komponenten
```powershell
# Teste nur Preisdaten-Abruf
python -c "
from bitpanda_fusion_adapter import BitpandaFusionPaperTrader
trader = BitpandaFusionPaperTrader()
prices = trader.get_current_prices()
print(prices)
"
```

## ⚠️ Risk Management

### Automatische Limits
- **Max Position:** 25% des Portfolios
- **Stop-Loss:** 5% pro Position
- **Take-Profit:** 15% Gewinnmitnahme
- **Max Daily Loss:** 5% des Gesamtportfolios
- **Min Order Size:** €50

### Portfolio-Schutz
```python
# Notfall-Stop bei 10% Portfolio-Verlust
if portfolio_loss > 0.10:
    liquidate_all_positions()
    
# Max 10 Trades pro Ticker pro Tag
if daily_trades[ticker] >= 10:
    skip_trading(ticker)
```

## 🔧 Troubleshooting

### Häufige Probleme

**1. Keine Preisdaten**
```
⚠️ Fehler beim Abrufen von BTC-EUR: HTTP 401
```
**Lösung:** Internet-Verbindung prüfen, ggf. VPN verwenden

**2. Kein Trading-Signal**
```
⚠️ Keine Backtest-Ergebnisse für ETH-EUR
```
**Lösung:** Datenqualität prüfen mit `check_crypto_csvs.py`

**3. Order Rejected**
```
❌ Nicht genug Kapital für BUY Order
```
**Lösung:** Portfolio-Balance prüfen, Order-Größe reduzieren

**4. API Rate Limit**
```
⚠️ API Rate Limit erreicht
```
**Lösung:** Warten oder `api_rate_limit` in Config reduzieren

### Debug-Modus
```python
# In bitpanda_config.py
DEBUG_CONFIG = {
    'verbose_logging': True,
    'save_api_calls': True,
    'dry_run_mode': True  # Keine Orders ausführen
}
```

## 🚀 Erweiterungen

### Echte Bitpanda API Integration

1. **API-Key registrieren** bei Bitpanda Pro
2. **Paper Trading aktivieren** in deinem Account
3. **API-Key eintragen** in `bitpanda_config.py`
4. **Sandbox-Modus deaktivieren:**
   ```python
   trader = BitpandaFusionPaperTrader(sandbox=False)
   ```

### Telegram Benachrichtigungen

```python
# In bitpanda_config.py
REPORTING_CONFIG = {
    'telegram_bot_token': 'DEIN_BOT_TOKEN',
    'telegram_chat_id': 'DEINE_CHAT_ID'
}
```

### Erweiterte Strategien

```python
# Neue Strategie hinzufügen
def rsi_strategy(self, ticker_data):
    rsi = calculate_rsi(ticker_data)
    if rsi < 30:  # Überverkauft
        return {'action': 'BUY', 'strength': 0.8}
    elif rsi > 70:  # Überkauft
        return {'action': 'SELL', 'strength': 0.8}
    return {'action': 'HOLD', 'strength': 0.0}
```

## 📞 Support

- **GitHub Issues:** Für Bug Reports
- **Dokumentation:** Siehe README.md
- **Konfiguration:** bitpanda_config.py anpassen
- **Logs:** Automatisch in CSV-Files gespeichert

---

**⚠️ Disclaimer:** Paper Trading dient nur zu Testzwecken. Echtes Trading birgt hohe Risiken.

**🎯 Ready to go:** Dein Framework ist jetzt bereit für Bitpanda Fusion Paper Trading! 🚀
