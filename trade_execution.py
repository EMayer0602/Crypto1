# trade_execution.py
import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from config import COMMISSION_RATE, MIN_COMMISSION

# Simuliertes Portfolio

def get_live_price(symbol: str) -> float:
    """
    Holt den aktuellen Spotpreis von Yahoo Finance für das Symbol.
    """
    df = yf.download(symbol, period="1d", interval="1m", progress=False)
    if df is None or df.empty or "Close" not in df.columns:
        return None
    return float(df["Close"].dropna().iloc[-1])


def calculate_fee(amount: float) -> float:
    """
    Berechnet die Handelsgebühr für gehandelten Betrag.
    """
    return max(MIN_COMMISSION, amount * COMMISSION_RATE)


def execute_trade(symbol: str,
                  action: str,
                  quantity: float,
                  limit_price: float = None,
                  cash_balance: float = 10000.0) -> dict:
    """
    Simuliert einen Trade (buy/sell) mit Preisabfrage & Gebührenberechnung.
    Gibt ein Transaktionsobjekt zurück.
    """

    spot = get_live_price(symbol)
    if spot is None:
        return {"status": "error", "reason": "Price not available."}

    price = spot
    now = pd.Timestamp.now()

    # Limit Order prüfen
    if limit_price is not None:
        if action == "buy" and spot > limit_price:
            return {"status": "rejected", "reason": f"Spotpreis {spot:.2f} > Limit {limit_price:.2f}"}
        if action == "sell" and spot < limit_price:
            return {"status": "rejected", "reason": f"Spotpreis {spot:.2f} < Limit {limit_price:.2f}"}
        price = limit_price

    turnover = quantity * price
    fee = calculate_fee(turnover)

    # Simulation für BUY
    if action == "buy":
        if turnover + fee > cash_balance:
            return {"status": "rejected", "reason": "Nicht genug Kapital für Kauf."}

        portfolio.setdefault(symbol, 0.0)
        portfolio[symbol] += quantity
        cash_balance -= (turnover + fee)

    # Simulation für SELL
    elif action == "sell":
        if portfolio.get(symbol, 0.0) < quantity:
            return {"status": "rejected", "reason": "Nicht genug Bestand zum Verkauf."}
        portfolio[symbol] -= quantity
        cash_balance += (turnover - fee)

    return {
        "status": "filled",
        "symbol": symbol,
        "action": action,
        "quantity": quantity,
        "price": round(price, 2),
        "fee": round(fee, 2),
        "value": round(turnover, 2),
        "timestamp": now,
        "cash_balance": round(cash_balance, 2),
        "remaining_position": round(portfolio.get(symbol, 0.0), 4)
    }

def prepare_orders_from_trades(trade_csv_path, symbol, order_type="sell"):
    """
    Wandelt Zeilen aus trades_long_*.csv in Order-Dictionaries um,
    die für die Ausführung (z. B. via Bitpanda oder Simulation) genutzt werden können.
    """

    trades = pd.read_csv(trade_csv_path)
    trades["sell_date"] = pd.to_datetime(trades["sell_date"], errors="coerce")
    today = pd.Timestamp.now().normalize()

    # Filter: Nur Trades, die heute verkauft werden sollen
    today_trades = trades[trades["sell_date"] == today]

    orders = []
    for _, row in today_trades.iterrows():
        limit_price = float(row["sell_price"]) if "sell_price" in row else None
        qty = float(row["shares"])
        order = {
            "symbol": symbol,
            "action": order_type,
            "quantity": qty,
            "limit": limit_price  # Marktorder, wenn None
        }
        orders.append(order)

    return orders

def prepare_orders_from_trades(trade_csv_path, symbol, mode="sell"):
    """
    Extrahiert Tagesorders aus einer Trade-CSV für das gegebene Symbol.
    Filtert sell_date == heute und erzeugt Order-Dictionaries.
    """
    try:
        trades = pd.read_csv(trade_csv_path)
    except FileNotFoundError:
        print(f"[WARNUNG] Datei nicht gefunden: {trade_csv_path}")
        return []

    trades["sell_date"] = pd.to_datetime(trades["sell_date"], errors="coerce")
    today = pd.Timestamp.now().normalize()

    today_trades = trades[trades["sell_date"] == today]
    if today_trades.empty:
        return []

    orders = []
    for _, row in today_trades.iterrows():
        qty = float(row["shares"])
        limit_price = float(row["sell_price"]) if not pd.isna(row["sell_price"]) else None

        order = {
            "symbol": symbol,
            "action": mode,
            "quantity": qty,
            "limit": limit_price
        }
        orders.append(order)

    return orders

def submit_order_bitpanda(order: dict, api_key: str) -> dict:
    """
    Sendet einen echten Trade-Request an Bitpanda API.
    Erwartet ein Dict mit 'symbol', 'action', 'quantity', 'limit', etc.
    """

    url = "https://api.bitpanda.com/v1/orders"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "instrument_code": order["symbol"],
        "type": order["action"],   # "buy" oder "sell"
        "amount": order["quantity"],
        "price": order.get("limit", None),
        "order_type": "limit" if order.get("limit") else "market"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        return {"status": "error", "reason": str(e)}

    if response.status_code == 201:
        return {"status": "filled", "data": response.json()}
    else:
        return {
            "status": "error",
            "code": response.status_code,
            "msg": response.text
        }

def save_all_orders_html_report(all_orders: dict, output_dir="reports"):
    """
    Speichert alle Tagesorders in einem HTML-Bericht, gruppiert nach Symbol.
    `all_orders`: Dict mit Schlüssel = Symbol, Wert = Liste von Order-Dicts
    """
    os.makedirs(output_dir, exist_ok=True)
    today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
    html_parts = [f"<h1>📋 Trading-Dashboard ({today_str})</h1>"]

    total_trades = 0
    total_value = 0
    total_fee = 0

    for symbol, orders in all_orders.items():
        if not orders:
            continue

        df = pd.DataFrame(orders)
        if "quantity" in df.columns and "limit" in df.columns:
            df["Trade Value"] = df["quantity"] * df["limit"]
        if "fee" in df.columns:
            df["Fee"] = df["fee"]
        else:
            df["Fee"] = 0.0

        symbol_value = df["Trade Value"].sum()
        symbol_fee = df["Fee"].sum()

        total_trades += len(df)
        total_value += symbol_value
        total_fee += symbol_fee

        html_parts.append(f"<h2>{symbol}</h2>")
        html_parts.append(f"<p><b>{len(df)} Trades</b>, Gesamtwert: {symbol_value:,.2f} €, Gebühren: {symbol_fee:,.2f} €</p>")
        html_parts.append(df.to_html(index=False))

    # Gesamtübersicht oben
    html_parts.insert(1, f"""
        <p>
        <b>🔢 Alle Ticker:</b> {total_trades} Trades<br>
        <b>💰 Gesamter Handelswert:</b> {total_value:,.2f} €<br>
        <b>🧾 Gesamtgebühr:</b> {total_fee:,.2f} €
        </p>
    """)

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Trading-Dashboard (Alle Ticker)</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 40px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f5f5f5; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
        </style>
    </head>
    <body>
        {''.join(html_parts)}
        <p style="color:#999; font-size:0.9em;">Erstellt am {today_str}</p>
    </body>
    </html>
    """

    filepath = os.path.join(output_dir, f"orders_ALL_{today_str}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[REPORT] ✅ Gesamtbericht gespeichert: {filepath}")

def save_all_orders_html_report(all_orders: dict, output_dir="reports"):
    import os
    import pandas as pd

    os.makedirs(output_dir, exist_ok=True)
    today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
    html_parts = [f"<h1>📋 Tages-Dashboard ({today_str})</h1>"]

    total_trades = 0
    total_value = 0
    total_fee = 0

    for symbol, orders in all_orders.items():
        if not orders:
            continue

        df = pd.DataFrame(orders)
        df["Trade Value"] = df["quantity"] * df["limit"]
        df["Fee"] = df.get("fee", 0)
        symbol_value = df["Trade Value"].sum()
        symbol_fee = df["Fee"].sum()

        total_trades += len(df)
        total_value += symbol_value
        total_fee += symbol_fee

        html_parts.append(f"<h2>{symbol}</h2>")
        html_parts.append(f"<p><b>{len(df)} Trades</b>, Gesamtwert: {symbol_value:,.2f} €, Gebühren: {symbol_fee:,.2f} €</p>")
        html_parts.append(df.to_html(index=False))

    # Gesamtübersicht
    html_parts.insert(1, f"<p><b>Alle Ticker:</b> {total_trades} Trades<br><b>Gesamter Wert:</b> {total_value:,.2f} €<br><b>Gesamtgebühr:</b> {total_fee:,.2f} €</p>")

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Trading-Dashboard (Alle Ticker)</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 40px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f5f5f5; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
        </style>
    </head>
    <body>
        {''.join(html_parts)}
        <p style="color:#999; font-size:0.9em;">Erstellt am {today_str}</p>
    </body>
    </html>
    """

    path = os.path.join(output_dir, f"orders_ALL_{today_str}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[REPORT] ✅ Gesamtbericht gespeichert: {path}")


def execute_trade(symbol, action, quantity, limit_price, portfolio):
    """
    Simuliert einen Trade mit Portfolio-Update.
    """
    import pandas as pd

    price = limit_price or 0.0
    fee = price * quantity * 0.002  # Beispiel: 0.2 % Gebühr
    value = price * quantity

    timestamp = pd.Timestamp.now()

    if action == "buy":
        portfolio[symbol] = portfolio.get(symbol, 0.0) + quantity
    elif action == "sell":
        if portfolio.get(symbol, 0.0) < quantity:
            return {"status": "error", "msg": "Nicht genügend Bestand"}
        portfolio[symbol] -= quantity

    return {
        "status": "filled",
        "symbol": symbol,
        "action": action,
        "quantity": quantity,
        "price": price,
        "fee": fee,
        "value": value,
        "timestamp": timestamp,
        "remaining_position": portfolio[symbol]
    }
