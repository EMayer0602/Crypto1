# check_crypto_csvs.py

from crypto_tickers import crypto_tickers
from crypto_backtesting_module import safe_loader

CSV_PATH = "C:\\Users\\Edgar.000\\Documents\\____Trading strategies\\Crypto_trading"

def check_and_update_csvs():
    print("🔍 Starte CSV-Update...\n")
    for ticker in crypto_tickers:
        print(f"🔄 {ticker}")
        df = safe_loader(ticker, csv_path=CSV_PATH, refresh=True)
        if df is None:
            print(f"⚠️ {ticker}: Keine Daten\n")
        else:
            print(f"✅ {ticker}: Zeilen: {len(df)} | Von {df.index.min().date()} bis {df.index.max().date()}\n")

if __name__ == "__main__":
    check_and_update_csvs()
