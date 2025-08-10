#!/usr/bin/env python3
"""
BITPANDA FUSION CONFIGURATION
API-Konfiguration für Paper Trading und Live Trading
"""

# ===============================================
# BITPANDA FUSION API KONFIGURATION
# ===============================================

# API URLs
BITPANDA_API_CONFIG = {
    'sandbox_url': 'https://api-sandbox.bitpanda.com/v1',
    'live_url': 'https://api.bitpanda.com/v1',
    'websocket_sandbox': 'wss://streams-sandbox.bitpanda.com',
    'websocket_live': 'wss://streams.bitpanda.com'
}

# API KEYS (für echte Nutzung hier eintragen)
BITPANDA_API_KEYS = {
    'paper_trading_key': 'YOUR_PAPER_TRADING_API_KEY_HERE',
    'live_trading_key': 'YOUR_LIVE_TRADING_API_KEY_HERE'  # NIEMALS IN PRODUCTION HARDCODEN!
}

# ===============================================
# PAPER TRADING KONFIGURATION
# ===============================================

PAPER_TRADING_CONFIG = {
    # Startkapital
    'initial_capital_eur': 16000.0,
    
    # Trading-Parameter
    'min_order_size_eur': 50.0,
    'max_position_size_pct': 0.25,  # Max 25% des Portfolios pro Position
    'stop_loss_pct': 0.05,          # 5% Stop-Loss
    'take_profit_pct': 0.15,        # 15% Take-Profit
    
    # Gebührenstruktur (Bitpanda Fusion)
    'trading_fee_pct': 0.0015,      # 0.15% Trading Fee
    'spread_buffer_pct': 0.001,     # 0.1% Spread-Puffer für Limit Orders
    
    # Signal-Parameter
    'min_win_rate_buy': 0.60,       # Mindest-Gewinnrate für BUY-Signal
    'max_win_rate_sell': 0.40,      # Max-Gewinnrate für SELL-Signal
    'signal_strength_multiplier': 1.0,
    
    # Risk Management
    'max_daily_trades': 50,
    'max_trades_per_ticker': 10,
    'portfolio_rebalance_threshold': 0.05,
    
    # Logging
    'enable_trade_logging': True,
    'log_level': 'INFO',
    'save_reports': True
}

# ===============================================
# BITPANDA TICKER MAPPING
# ===============================================

# Mapping von unseren Ticker-Namen zu Bitpanda Instrument IDs
BITPANDA_TICKER_MAPPING = {
    'BTC-EUR': {
        'bitpanda_symbol': 'BTC_EUR',
        'instrument_id': 'BTC_EUR',
        'min_order_size': 0.0001,
        'price_precision': 2,
        'quantity_precision': 8
    },
    'ETH-EUR': {
        'bitpanda_symbol': 'ETH_EUR', 
        'instrument_id': 'ETH_EUR',
        'min_order_size': 0.001,
        'price_precision': 2,
        'quantity_precision': 6
    },
    'DOGE-EUR': {
        'bitpanda_symbol': 'DOGE_EUR',
        'instrument_id': 'DOGE_EUR', 
        'min_order_size': 1.0,
        'price_precision': 6,
        'quantity_precision': 2
    },
    'SOL-EUR': {
        'bitpanda_symbol': 'SOL_EUR',
        'instrument_id': 'SOL_EUR',
        'min_order_size': 0.01,
        'price_precision': 3,
        'quantity_precision': 4
    },
    'LINK-EUR': {
        'bitpanda_symbol': 'LINK_EUR',
        'instrument_id': 'LINK_EUR',
        'min_order_size': 0.1,
        'price_precision': 4,
        'quantity_precision': 3
    },
    'XRP-EUR': {
        'bitpanda_symbol': 'XRP_EUR',
        'instrument_id': 'XRP_EUR',
        'min_order_size': 1.0,
        'price_precision': 6,
        'quantity_precision': 2
    }
}

# ===============================================
# TRADING STRATEGIEN
# ===============================================

TRADING_STRATEGIES = {
    'momentum_strategy': {
        'enabled': True,
        'lookback_days': 14,
        'win_rate_threshold': 0.65,
        'position_size_pct': 0.20,
        'rebalance_frequency': 'daily'
    },
    
    'mean_reversion_strategy': {
        'enabled': False,
        'lookback_days': 30,
        'oversold_threshold': 0.3,
        'overbought_threshold': 0.7,
        'position_size_pct': 0.15
    },
    
    'breakout_strategy': {
        'enabled': False,
        'breakout_periods': [20, 50],
        'volume_confirmation': True,
        'position_size_pct': 0.25
    }
}

# ===============================================
# REPORTING & MONITORING
# ===============================================

REPORTING_CONFIG = {
    'daily_report': True,
    'trade_notifications': True,
    'performance_alerts': True,
    'telegram_bot_token': None,  # Optional: Telegram Benachrichtigungen
    'telegram_chat_id': None,
    
    # Report-Formate
    'csv_reports': True,
    'html_reports': True,
    'json_reports': False,
    
    # Report-Inhalte
    'include_charts': True,
    'include_performance_metrics': True,
    'include_trade_details': True,
    'include_risk_metrics': True
}

# ===============================================
# ENTWICKLUNG & DEBUG
# ===============================================

DEBUG_CONFIG = {
    'simulation_mode': True,        # True = Kein echter API-Call
    'mock_api_responses': True,     # True = Verwende Mock-Daten
    'verbose_logging': True,        # Detaillierte Logs
    'save_api_calls': True,         # API-Calls für Debug speichern
    'dry_run_mode': False,          # True = Keine Orders platzieren
    
    # Test-Daten
    'use_historical_data': True,
    'backtest_start_date': '2024-01-01',
    'backtest_end_date': '2025-08-10'
}

# ===============================================
# SICHERHEIT
# ===============================================

SECURITY_CONFIG = {
    'api_rate_limit': 100,          # Max API-Calls pro Minute
    'max_daily_loss_pct': 0.05,     # Max 5% Verlust pro Tag
    'emergency_stop_loss_pct': 0.10, # 10% Portfolio-Stop-Loss
    'whitelisted_ips': [],           # Nur für Live Trading
    'enable_2fa': True,              # Aktiviere 2FA wenn verfügbar
    
    # Order-Validierung
    'max_order_size_eur': 5000,     # Max Order-Größe
    'min_order_interval_seconds': 5, # Min Zeit zwischen Orders
    'validate_orders_before_send': True
}

# ===============================================
# PERFORMANCE BENCHMARKS
# ===============================================

BENCHMARK_CONFIG = {
    'benchmark_symbols': ['BTC-EUR', 'ETH-EUR'],
    'performance_targets': {
        'daily_return': 0.005,       # 0.5% täglich
        'monthly_return': 0.10,      # 10% monatlich  
        'max_drawdown': 0.15,        # Max 15% Drawdown
        'sharpe_ratio': 1.5          # Min Sharpe Ratio
    },
    
    'risk_metrics': {
        'var_confidence': 0.05,      # 5% VaR
        'max_correlation': 0.8,      # Max Korrelation zwischen Positionen
        'concentration_limit': 0.4   # Max 40% in einem Asset
    }
}

def get_config(config_type: str = 'paper_trading'):
    """
    Hole Konfiguration für bestimmten Typ
    
    Args:
        config_type: 'paper_trading', 'live_trading', 'debug', etc.
    
    Returns:
        Dict mit Konfiguration
    """
    configs = {
        'paper_trading': PAPER_TRADING_CONFIG,
        'api': BITPANDA_API_CONFIG,
        'tickers': BITPANDA_TICKER_MAPPING,
        'strategies': TRADING_STRATEGIES,
        'reporting': REPORTING_CONFIG,
        'debug': DEBUG_CONFIG,
        'security': SECURITY_CONFIG,
        'benchmark': BENCHMARK_CONFIG
    }
    
    return configs.get(config_type, {})

def validate_config():
    """
    Validiere Konfiguration
    """
    print("🔧 VALIDIERE BITPANDA FUSION KONFIGURATION...")
    
    # Prüfe API Keys
    if BITPANDA_API_KEYS['paper_trading_key'] == 'YOUR_PAPER_TRADING_API_KEY_HERE':
        print("   ⚠️ Paper Trading API Key nicht gesetzt (verwende Simulation)")
    
    # Prüfe Ticker Mapping
    from crypto_tickers import crypto_tickers
    for ticker in crypto_tickers.keys():
        if ticker not in BITPANDA_TICKER_MAPPING:
            print(f"   ⚠️ Ticker {ticker} nicht in Bitpanda Mapping gefunden")
    
    # Prüfe Trading-Parameter
    if PAPER_TRADING_CONFIG['initial_capital_eur'] <= 0:
        print("   ❌ Initial Capital muss > 0 sein")
    
    print("   ✅ Konfiguration validiert")

if __name__ == "__main__":
    validate_config()
    print("\n📋 VERFÜGBARE KONFIGURATIONEN:")
    for config_name in ['paper_trading', 'api', 'tickers', 'strategies']:
        config = get_config(config_name)
        print(f"   {config_name}: {len(config)} Einstellungen")
