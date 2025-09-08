from websockets import Close


crypto_tickers = {
    "BTC-EUR":  {"symbol": "BTC-EUR",  "conID": None, "long": True, "short": False, "initialCapitalLong": 5000, "initialCapitalShort": 0, "order_round_factor": 0.001, "trade_on": "Close"},
    "ETH-EUR":  {"symbol": "ETH-EUR",  "conID": None, "long": True, "short": False, "initialCapitalLong": 3000, "initialCapitalShort": 0, "order_round_factor": 0.01, "trade_on": "Close"},
    "DOGE-EUR": {"symbol": "DOGE-EUR", "conID": None, "long": True, "short": False, "initialCapitalLong": 3500, "initialCapitalShort": 0, "order_round_factor": 10.0, "trade_on": "Close"},
    "SOL-EUR":  {"symbol": "SOL-EUR",  "conID": None, "long": True, "short": False, "initialCapitalLong": 2000, "initialCapitalShort": 0, "order_round_factor": 0.1, "trade_on": "Close"},
    "LINK-EUR": {"symbol": "LINK-EUR", "conID": None, "long": True, "short": False, "initialCapitalLong": 1500, "initialCapitalShort": 0, "order_round_factor": 1.0, "trade_on": "Close"},
    "XRP-EUR":  {"symbol": "XRP-EUR",  "conID": None, "long": True, "short": False, "initialCapitalLong": 1000, "initialCapitalShort": 0, "order_round_factor": 10.0, "trade_on": "Close"},
    "XLM-EUR":  {"symbol": "XLM-EUR",  "conID": None, "long": True, "short": False, "initialCapitalLong": 1000, "initialCapitalShort": 0, "order_round_factor": 100.0, "trade_on": "Close"}
}
