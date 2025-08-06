import pandas as pd
from signal_utils import assign_long_signals_extended, calculate_support_resistance

# Test Signal-Generation
df = pd.read_csv('BTC-EUR_minute.csv', parse_dates=['DateTime'])
df.set_index('DateTime', inplace=True)

support, resistance = calculate_support_resistance(df, 7, 3, verbose=False)
signal_df = assign_long_signals_extended(support, resistance, df, 3, '1d')

print('Signal DataFrame Spalten:', list(signal_df.columns))
print('Action Werte:', signal_df['Action'].value_counts().to_dict() if 'Action' in signal_df.columns else 'No Action column')
print('Long Action Werte:', signal_df['Long Action'].value_counts().to_dict() if 'Long Action' in signal_df.columns else 'No Long Action column')
print('Erste 3 Zeilen:')
print(signal_df.head(3))
