#!/usr/bin/env python3
"""Test script to generate enhanced charts for ALL tickers"""

from crypto_backtesting_module import run_backtest
from crypto_tickers import crypto_tickers
import os
import time

def test_all_enhanced_charts():
    print('🚀 TESTING ENHANCED CHARTS FOR ALL TICKERS 🚀')
    print('=' * 60)
    
    # Stelle sicher, dass reports Ordner existiert
    os.makedirs("reports", exist_ok=True)
    
    success_count = 0
    total_count = 0
    
    for ticker in crypto_tickers.keys():
        total_count += 1
        print(f'\n📊 Testing Enhanced Chart for {ticker} ({total_count}/{len(crypto_tickers)})...')
        print('-' * 40)
        
        try:
            # Hole ticker-spezifische Config
            ticker_config = crypto_tickers.get(ticker, {})
            
            # Erstelle vollständige Config
            config = {
                'timeframe': 'daily',
                'csv_path': './',
                'initial_capital': ticker_config.get('initialCapitalLong', 10000),
                'commission_rate': 0.0018,
                'trade_on': ticker_config.get('trade_on', 'close'),
                'order_round_factor': ticker_config.get('order_round_factor', 0.01)
            }
            
            # Führe Backtest aus
            result = run_backtest(ticker, config)
            
            if result and 'success' in result and result['success']:
                success_count += 1
                print(f'✅ {ticker}: Chart created successfully!')
                
                # Extract final capital from trade_statistics
                trade_stats = result.get('trade_statistics', {})
                final_capital = trade_stats.get('💼 Final Capital', 'N/A')
                print(f'   📈 Final Capital: {final_capital}')
                
                if 'optimal_past_window' in result:
                    print(f'   🎯 Optimal Parameters: Past={result["optimal_past_window"]}, Trade={result["optimal_trade_window"]}')
            else:
                print(f'❌ {ticker}: Chart creation failed - backtest unsuccessful')
                if result:
                    print(f'   Result keys: {list(result.keys())}')
                
        except Exception as e:
            print(f'❌ {ticker}: Error - {e}')
        
        # Kurze Pause zwischen Charts um Browser nicht zu überlasten
        time.sleep(2)
    
    print('\n' + '=' * 60)
    print(f'🎉 SUMMARY: {success_count}/{total_count} enhanced charts created successfully!')
    
    if success_count > 0:
        print(f'📁 All charts saved in: reports\\')
        print('🌐 Charts opened in browser for visual inspection')
    
    return success_count == total_count

if __name__ == "__main__":
    test_all_enhanced_charts()
