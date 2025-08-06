import pandas as pd
from datetime import datetime, timedelta

# BTC CSV prüfen
df_btc = pd.read_csv('BTC-EUR_daily.csv', index_col=0, parse_dates=True)
print('=== BTC-EUR CSV ANALYSIS ===')
print(f'Total rows: {len(df_btc)}')
print(f'Date range: {df_btc.index.min()} to {df_btc.index.max()}')

# Artificial values
artificial = df_btc[df_btc['Volume'] == -1000]
print(f'Artificial values: {len(artificial)}')
if len(artificial) > 0:
    print('Artificial rows:')
    for idx, row in artificial.iterrows():
        print(f'  {idx}: Close={row.Close:.4f}, Volume={row.Volume}')

print()
print('Last 3 days:')
print(df_btc.tail(3)[['Close', 'Volume']])

# Check for gaps
yesterday = datetime.now() - timedelta(days=1)
today = datetime.now()
print(f'\nYesterday: {yesterday.strftime("%Y-%m-%d")}')
print(f'Today: {today.strftime("%Y-%m-%d")}')

# Check if yesterday and today exist
yesterday_str = yesterday.strftime('%Y-%m-%d')
today_str = today.strftime('%Y-%m-%d')

if yesterday_str in df_btc.index.strftime('%Y-%m-%d'):
    y_row = df_btc[df_btc.index.strftime('%Y-%m-%d') == yesterday_str]
    print(f'Yesterday data: Close={y_row.iloc[0].Close:.4f}, Volume={y_row.iloc[0].Volume}')
else:
    print('❌ Yesterday data missing')

if today_str in df_btc.index.strftime('%Y-%m-%d'):
    t_row = df_btc[df_btc.index.strftime('%Y-%m-%d') == today_str]
    print(f'Today data: Close={t_row.iloc[0].Close:.4f}, Volume={t_row.iloc[0].Volume}')
else:
    print('❌ Today data missing')
