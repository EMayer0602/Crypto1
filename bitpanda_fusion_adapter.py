#!/usr/bin/env python3
"""
BITPANDA FUSION PAPER TRADING ADAPTER
Verbindet das Crypto Trading Framework mit Bitpanda Fusion Paper Trading
"""

import sys
import os
import json
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import run_backtest

class BitpandaFusionPaperTrader:
    """
    Bitpanda Fusion Paper Trading Integration
    Erweitert um Web Automation Support
    """
    
    def __init__(self, api_key: str = None, sandbox: bool = True, use_web_automation: bool = False):
        """
        Initialize Bitpanda Fusion Paper Trading
        
        Args:
            api_key: Bitpanda API Key (für Paper Trading)
            sandbox: True für Paper Trading, False für Live Trading
            use_web_automation: True für Web Automation, False für lokale Simulation
        """
        self.api_key = api_key or "PAPER_TRADING_KEY"  # Placeholder
        self.sandbox = sandbox
        self.use_web_automation = use_web_automation
        self.web_automation = None
        self.base_url = "https://api.bitpanda.com/v1" if not sandbox else "https://api-sandbox.bitpanda.com/v1"
        
        # Paper Trading Portfolio
        self.paper_portfolio = {
            'EUR': 16000.0,  # Startkapital wie in crypto_tickers
            'positions': {}
        }
        
        # Trade History für Reports
        self.trade_history = []
        
        print(f"🎯 Bitpanda Fusion Paper Trading initialisiert")
        print(f"💰 Startkapital: €{self.paper_portfolio['EUR']:,.2f}")
        print(f"📊 Modus: {'PAPER TRADING' if sandbox else 'LIVE TRADING'}")
        
        if use_web_automation:
            print("🤖 Web Automation aktiviert")
            self.initialize_web_automation()
        else:
            print("🧪 Lokale Simulation aktiviert")
    
    def initialize_web_automation(self):
        """Initialisiere Web Automation für echtes Bitpanda Fusion Trading"""
        
        print("\n🤖 INITIALISIERE WEB AUTOMATION...")
        
        try:
            # Versuche Selenium zu laden
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                
                chrome_options = Options()
                chrome_options.add_argument("--disable-web-security")
                
                self.web_automation = webdriver.Chrome(options=chrome_options)
                print("✅ Selenium WebDriver erfolgreich initialisiert")
                return True
                
            except ImportError:
                print("⚠️ Selenium nicht verfügbar")
            except Exception as e:
                print(f"⚠️ Selenium Fehler: {e}")
            
            # Versuche Playwright als Alternative
            try:
                from playwright.sync_api import sync_playwright
                
                self.playwright = sync_playwright().start()
                self.web_automation = self.playwright.chromium.launch(headless=False)
                print("✅ Playwright WebDriver erfolgreich initialisiert")
                return True
                
            except ImportError:
                print("⚠️ Playwright nicht verfügbar")
            except Exception as e:
                print(f"⚠️ Playwright Fehler: {e}")
            
            print("❌ Keine Web Automation Tools verfügbar")
            print("💡 Installieren Sie: pip install selenium ODER pip install playwright")
            self.use_web_automation = False
            return False
            
        except Exception as e:
            print(f"❌ Web Automation Initialisierung fehlgeschlagen: {e}")
            self.use_web_automation = False
            return False
    
    def login_to_fusion_web(self, email=None, password=None):
        """Login zu Bitpanda Fusion über Web Automation"""
        
        if not self.use_web_automation or not self.web_automation:
            print("⚠️ Web Automation nicht verfügbar")
            return False
        
        print("\n🔐 LOGIN ZU BITPANDA FUSION...")
        
        if not email:
            email = input("📧 Bitpanda Email: ")
        if not password:
            password = input("🔐 Bitpanda Password: ")
        
        try:
            # Selenium WebDriver
            if hasattr(self.web_automation, 'get'):
                self.web_automation.get("https://web.bitpanda.com")
                time.sleep(3)
                
                # Login Felder suchen und ausfüllen
                email_field = self.web_automation.find_element("name", "email")
                password_field = self.web_automation.find_element("name", "password")
                
                email_field.send_keys(email)
                password_field.send_keys(password)
                
                # Login Button klicken
                login_button = self.web_automation.find_element("xpath", "//button[contains(text(), 'Sign in')]")
                login_button.click()
                
                time.sleep(5)
                
                # Erfolgreich wenn Dashboard erreicht
                if "dashboard" in self.web_automation.current_url:
                    print("✅ Web Login erfolgreich!")
                    return True
                else:
                    print("❌ Web Login fehlgeschlagen")
                    return False
            
            # Playwright Alternative
            elif hasattr(self.web_automation, 'new_page'):
                page = self.web_automation.new_page()
                page.goto("https://web.bitpanda.com")
                
                page.fill('input[name="email"]', email)
                page.fill('input[name="password"]', password)
                page.click('button:has-text("Sign in")')
                
                page.wait_for_timeout(5000)
                
                if "dashboard" in page.url:
                    print("✅ Web Login erfolgreich!")
                    return True
                else:
                    print("❌ Web Login fehlgeschlagen")
                    return False
            
        except Exception as e:
            print(f"❌ Web Login Fehler: {e}")
            return False
    
    def place_web_order(self, ticker: str, action: str, amount_eur: float):
        """Platziere Order über Web Automation"""
        
        if not self.use_web_automation or not self.web_automation:
            print(f"⚠️ Web Automation nicht verfügbar - simuliere {ticker} {action}")
            return self.simulate_paper_trade(ticker, action, amount_eur, 0)
        
        print(f"\n🌐 WEB ORDER: {action} {ticker} €{amount_eur}")
        
        try:
            # Diese Implementierung muss an die echte Bitpanda Fusion UI angepasst werden
            # Hier nur Beispiel-Code:
            
            if hasattr(self.web_automation, 'find_element'):
                # Selenium
                # 1. Zu Trading navigieren
                trading_link = self.web_automation.find_element("xpath", "//a[contains(text(), 'Exchange')]")
                trading_link.click()
                time.sleep(2)
                
                # 2. Trading Pair auswählen
                pair_selector = self.web_automation.find_element("xpath", f"//span[contains(text(), '{ticker}')]")
                pair_selector.click()
                time.sleep(1)
                
                # 3. Buy/Sell Tab
                if action.upper() == "BUY":
                    buy_tab = self.web_automation.find_element("xpath", "//button[contains(text(), 'Buy')]")
                    buy_tab.click()
                else:
                    sell_tab = self.web_automation.find_element("xpath", "//button[contains(text(), 'Sell')]")
                    sell_tab.click()
                
                # 4. Amount eingeben
                amount_field = self.web_automation.find_element("name", "amount")
                amount_field.clear()
                amount_field.send_keys(str(amount_eur))
                
                # 5. Order platzieren
                place_order_btn = self.web_automation.find_element("xpath", f"//button[contains(text(), '{action.title()}')]")
                place_order_btn.click()
                
                time.sleep(3)
                
                # 6. Erfolg prüfen
                try:
                    success_msg = self.web_automation.find_element("xpath", "//div[contains(text(), 'Order placed')]")
                    print(f"✅ Web Order erfolgreich: {action} {ticker} €{amount_eur}")
                    
                    # Trade in History aufzeichnen
                    trade_record = {
                        'timestamp': datetime.now(),
                        'ticker': ticker,
                        'action': action,
                        'amount_eur': amount_eur,
                        'method': 'WEB_AUTOMATION',
                        'status': 'EXECUTED'
                    }
                    self.trade_history.append(trade_record)
                    
                    return True
                    
                except:
                    print(f"⚠️ Web Order Status unbekannt für {ticker}")
                    return False
            
            else:
                print(f"❌ Web Automation Methode nicht unterstützt")
                return False
            
        except Exception as e:
            print(f"❌ Web Order Fehler für {ticker}: {e}")
            return False
    
    def get_current_prices(self) -> Dict[str, float]:
        """
        Hole aktuelle Marktpreise von Bitpanda
        Fallback auf Yahoo Finance wenn API nicht verfügbar
        """
        prices = {}
        
        for ticker_name, config in crypto_tickers.items():
            symbol = config['symbol']
            
            try:
                # Versuche Bitpanda API (simuliert für Paper Trading)
                if self.sandbox:
                    # Paper Trading: Verwende Yahoo Finance als Proxy
                    import yfinance as yf
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d", interval="1m")
                    if not hist.empty:
                        prices[ticker_name] = float(hist['Close'].iloc[-1])
                        print(f"   📈 {ticker_name}: €{prices[ticker_name]:.4f}")
                else:
                    # Live API Call würde hier stehen
                    pass
                    
            except Exception as e:
                print(f"   ⚠️ Fehler beim Abrufen von {ticker_name}: {e}")
                prices[ticker_name] = 0.0
        
        return prices
    
    def calculate_position_size(self, ticker_name: str, signal_strength: float = 1.0) -> float:
        """
        Berechne Positionsgröße basierend auf verfügbarem Kapital
        """
        config = crypto_tickers[ticker_name]
        max_capital = config['initialCapitalLong']
        available_capital = min(max_capital, self.paper_portfolio['EUR'])
        
        # Verwende Signal-Stärke für Positionsgröße (0.0 - 1.0)
        position_capital = available_capital * signal_strength
        
        return position_capital
    
    def place_paper_order(self, ticker_name: str, action: str, quantity: float, 
                         price: float, order_type: str = "LIMIT") -> Dict[str, Any]:
        """
        Simuliere Order-Platzierung für Paper Trading
        
        Args:
            ticker_name: Ticker (z.B. "BTC-EUR")
            action: "BUY" oder "SELL"
            quantity: Menge in EUR
            price: Limit-Preis
            order_type: "LIMIT" oder "MARKET"
        """
        order_id = f"PAPER_{int(time.time())}_{ticker_name}_{action}"
        timestamp = datetime.now()
        
        # Berechne tatsächliche Coin-Menge
        config = crypto_tickers[ticker_name]
        round_factor = config['order_round_factor']
        coin_quantity = quantity / price
        coin_quantity = round(coin_quantity / round_factor) * round_factor
        
        order = {
            'order_id': order_id,
            'timestamp': timestamp,
            'ticker': ticker_name,
            'action': action,
            'quantity_eur': quantity,
            'quantity_coins': coin_quantity,
            'price': price,
            'order_type': order_type,
            'status': 'FILLED',  # Paper Trading = sofort ausgeführt
            'fees': quantity * 0.0015  # 0.15% Bitpanda Gebühr
        }
        
        # Aktualisiere Paper Portfolio
        if action == "BUY":
            cost = quantity + order['fees']
            if self.paper_portfolio['EUR'] >= cost:
                self.paper_portfolio['EUR'] -= cost
                if ticker_name not in self.paper_portfolio['positions']:
                    self.paper_portfolio['positions'][ticker_name] = {
                        'quantity': 0.0,
                        'avg_price': 0.0,
                        'total_cost': 0.0
                    }
                
                pos = self.paper_portfolio['positions'][ticker_name]
                new_total_cost = pos['total_cost'] + quantity
                new_quantity = pos['quantity'] + coin_quantity
                pos['avg_price'] = new_total_cost / new_quantity if new_quantity > 0 else price
                pos['quantity'] = new_quantity
                pos['total_cost'] = new_total_cost
                
                print(f"   ✅ BUY Order: {coin_quantity:.6f} {ticker_name} @ €{price:.4f}")
            else:
                order['status'] = 'REJECTED'
                print(f"   ❌ Nicht genug Kapital für BUY Order")
        
        elif action == "SELL":
            if ticker_name in self.paper_portfolio['positions']:
                pos = self.paper_portfolio['positions'][ticker_name]
                if pos['quantity'] >= coin_quantity:
                    proceeds = quantity - order['fees']
                    self.paper_portfolio['EUR'] += proceeds
                    pos['quantity'] -= coin_quantity
                    pos['total_cost'] = pos['total_cost'] * (pos['quantity'] / (pos['quantity'] + coin_quantity))
                    
                    print(f"   ✅ SELL Order: {coin_quantity:.6f} {ticker_name} @ €{price:.4f}")
                else:
                    order['status'] = 'REJECTED'
                    print(f"   ❌ Nicht genug {ticker_name} für SELL Order")
            else:
                order['status'] = 'REJECTED'
                print(f"   ❌ Keine Position in {ticker_name}")
        
        # Speichere in Trade History
        if order['status'] == 'FILLED':
            self.trade_history.append(order)
        
        return order
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """
        Berechne aktuellen Portfoliowert
        """
        portfolio_value = {
            'cash': self.paper_portfolio['EUR'],
            'positions_value': 0.0,
            'total_value': 0.0,
            'positions': {}
        }
        
        for ticker_name, position in self.paper_portfolio['positions'].items():
            if position['quantity'] > 0 and ticker_name in current_prices:
                current_value = position['quantity'] * current_prices[ticker_name]
                portfolio_value['positions'][ticker_name] = {
                    'quantity': position['quantity'],
                    'current_price': current_prices[ticker_name],
                    'current_value': current_value,
                    'avg_price': position['avg_price'],
                    'pnl': current_value - position['total_cost']
                }
                portfolio_value['positions_value'] += current_value
        
        portfolio_value['total_value'] = portfolio_value['cash'] + portfolio_value['positions_value']
        
        return portfolio_value
    
    def execute_backtest_signals(self) -> None:
        """
        Führe Backtests aus und konvertiere Signale in Paper Trading Orders
        """
        print(f"\n🔄 FÜHRE BACKTESTS AUS UND GENERIERE TRADING-SIGNALE")
        print("=" * 60)
        
        current_prices = self.get_current_prices()
        
        for ticker_name, config in crypto_tickers.items():
            print(f"\n📊 Analysiere {ticker_name}...")
            
            try:
                # Führe Backtest aus
                symbol = config['symbol']
                backtest_result = run_backtest(symbol, config)
                
                if not backtest_result or not backtest_result.get('matched_trades'):
                    print(f"   ⚠️ Keine Backtest-Ergebnisse für {ticker_name}")
                    continue
                
                # Analysiere letzte Trades für Signale
                matched_trades = backtest_result['matched_trades']
                recent_trades = matched_trades.tail(5)  # Letzte 5 Trades
                
                # Einfache Signal-Logik (kann erweitert werden)
                signal = self.generate_trading_signal(ticker_name, recent_trades, current_prices)
                
                if signal['action'] != 'HOLD':
                    self.execute_signal(ticker_name, signal, current_prices[ticker_name])
                
            except Exception as e:
                print(f"   ❌ Fehler bei {ticker_name}: {e}")
    
    def generate_trading_signal(self, ticker_name: str, recent_trades: pd.DataFrame, 
                              current_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Generiere Trading-Signal basierend auf Backtest-Ergebnissen
        """
        if ticker_name not in current_prices or recent_trades.empty:
            return {'action': 'HOLD', 'strength': 0.0}
        
        current_price = current_prices[ticker_name]
        
        # Analysiere Performance der letzten Trades
        profitable_trades = len(recent_trades[recent_trades.get('PnL', 0) > 0])
        total_trades = len(recent_trades)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0.0
        
        # Einfache Signal-Logik
        if win_rate > 0.6:  # > 60% Erfolgsrate
            # Prüfe ob wir bereits eine Position haben
            if ticker_name in self.paper_portfolio['positions'] and self.paper_portfolio['positions'][ticker_name]['quantity'] > 0:
                return {'action': 'HOLD', 'strength': 0.0}
            else:
                return {'action': 'BUY', 'strength': min(win_rate, 1.0)}
        elif win_rate < 0.4:  # < 40% Erfolgsrate
            # Verkaufe wenn Position vorhanden
            if ticker_name in self.paper_portfolio['positions'] and self.paper_portfolio['positions'][ticker_name]['quantity'] > 0:
                return {'action': 'SELL', 'strength': 1.0 - win_rate}
        
        return {'action': 'HOLD', 'strength': 0.0}
    
    def execute_signal(self, ticker_name: str, signal: Dict[str, Any], current_price: float) -> None:
        """
        Führe Trading-Signal aus
        """
        action = signal['action']
        strength = signal['strength']
        
        if action == 'BUY':
            position_capital = self.calculate_position_size(ticker_name, strength)
            if position_capital > 100:  # Mindest-Order-Größe
                limit_price = current_price * 0.999  # Leicht unter Marktpreis
                self.place_paper_order(ticker_name, 'BUY', position_capital, limit_price)
        
        elif action == 'SELL':
            if ticker_name in self.paper_portfolio['positions']:
                position = self.paper_portfolio['positions'][ticker_name]
                if position['quantity'] > 0:
                    sell_value = position['quantity'] * current_price
                    limit_price = current_price * 1.001  # Leicht über Marktpreis
                    self.place_paper_order(ticker_name, 'SELL', sell_value, limit_price)
    
    def generate_trading_report(self) -> None:
        """
        Generiere Trading Report
        """
        print(f"\n📊 ===== BITPANDA FUSION PAPER TRADING REPORT =====")
        print(f"📅 Stand: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        current_prices = self.get_current_prices()
        portfolio = self.get_portfolio_value(current_prices)
        
        print(f"\n💰 PORTFOLIO ÜBERSICHT:")
        print(f"   💵 Cash: €{portfolio['cash']:,.2f}")
        print(f"   📈 Positionen: €{portfolio['positions_value']:,.2f}")
        print(f"   🎯 Gesamtwert: €{portfolio['total_value']:,.2f}")
        print(f"   📊 Performance: €{portfolio['total_value'] - 16000:+,.2f} ({((portfolio['total_value']/16000-1)*100):+.2f}%)")
        
        if portfolio['positions']:
            print(f"\n📊 AKTIVE POSITIONEN:")
            for ticker, pos in portfolio['positions'].items():
                pnl_pct = (pos['pnl'] / pos['current_value']) * 100 if pos['current_value'] > 0 else 0
                print(f"   {ticker:10} | {pos['quantity']:>10.6f} | €{pos['current_price']:>8.4f} | €{pos['current_value']:>8.2f} | {pnl_pct:>+6.2f}%")
        
        if self.trade_history:
            print(f"\n📋 LETZTE TRADES ({len(self.trade_history)}):")
            for trade in self.trade_history[-10:]:  # Letzte 10 Trades
                print(f"   {trade['timestamp'].strftime('%H:%M:%S')} | {trade['action']:4} | {trade['ticker']:8} | €{trade['price']:>8.4f} | €{trade['quantity_eur']:>8.2f}")
        
        # Speichere Report als CSV
        self.save_bitpanda_report()
    
    def save_bitpanda_report(self) -> None:
        """
        Speichere Trading Report als CSV
        """
        if not self.trade_history:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"bitpanda_paper_trading_{timestamp}.csv"
        
        # Konvertiere zu DataFrame
        df = pd.DataFrame(self.trade_history)
        df['Date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
        df['Time'] = df['timestamp'].dt.strftime('%H:%M:%S')
        
        # Bitpanda-Format
        export_df = pd.DataFrame({
            'Date': df['Date'],
            'Time': df['Time'],
            'Ticker': df['ticker'],
            'Action': df['action'],
            'Quantity': df['quantity_coins'],
            'Price': df['price'],
            'Value': df['quantity_eur'],
            'Fees': df['fees'],
            'Order_Type': df['order_type'],
            'Status': df['status']
        })
        
        export_df.to_csv(filename, sep=';', index=False)
        print(f"\n💾 Trading Report gespeichert: {filename}")

def run_paper_trading_session():
    """
    Führe eine Paper Trading Session aus
    """
    print("🚀 STARTE BITPANDA FUSION PAPER TRADING SESSION")
    print("=" * 60)
    
    # Initialisiere Paper Trader
    trader = BitpandaFusionPaperTrader(sandbox=True)
    
    # Hole aktuelle Preise
    print(f"\n📈 AKTUELLE MARKTPREISE:")
    current_prices = trader.get_current_prices()
    
    # Zeige Startportfolio
    print(f"\n💰 STARTPORTFOLIO:")
    initial_portfolio = trader.get_portfolio_value(current_prices)
    print(f"   Gesamtwert: €{initial_portfolio['total_value']:,.2f}")
    
    # Führe Backtests aus und generiere Signale
    trader.execute_backtest_signals()
    
    # Zeige finales Portfolio
    print(f"\n📊 FINALES PORTFOLIO:")
    trader.generate_trading_report()
    
    return trader

if __name__ == "__main__":
    # Führe Paper Trading Session aus
    paper_trader = run_paper_trading_session()
    
    print(f"\n✅ PAPER TRADING SESSION ABGESCHLOSSEN!")
    print(f"🎯 Nutze 'python bitpanda_fusion_adapter.py' für weitere Sessions")
