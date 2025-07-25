crypto_tickers = {
    "BTC-EUR": {
        "symbol": "BTC-EUR",
        "long": True,
        "short": False,
        "initialCapitalLong": 2000,
        "initialCapitalShort": 1500,
        "order_round_factor": 0.001,
        "short_proxy_1": "BTC-1SHORT-EUR",  # optional, falls vorhanden
        "short_proxy_2": "BTC-2SHORT-EUR"
    },
    "ETH-EUR": {
        "symbol": "ETH-EUR",
        "long": True,
        "short": False,
        "initialCapitalLong": 1500,
        "initialCapitalShort": 1000,
        "order_round_factor": 0.01,
        "short_proxy_1": "ETH-1SHORT-EUR",
        "short_proxy_2": None
    },
    "DOGE-EUR": {
        "symbol": "DOGE-EUR",
        "long": True,
        "short": False,
        "initialCapitalLong": 500,
        "initialCapitalShort": 300,
        "order_round_factor": 1,
        "short_proxy_1": None,
        "short_proxy_2": None
    },
    "SOL-EUR": {
        "symbol": "SOL-EUR",
        "long": True,
        "short": False,
        "initialCapitalLong": 800,
        "initialCapitalShort": 600,
        "order_round_factor": 0.1,
        "short_proxy_1": "SOL-1SHORT-EUR",
        "short_proxy_2": None
    },
    "LINK-EUR": {
        "symbol": "LINK-EUR",
        "long": True,
        "short": False,
        "initialCapitalLong": 600,
        "initialCapitalShort": 500,
        "order_round_factor": 0.1,
        "short_proxy_1": None,
        "short_proxy_2": None
    },
    "XRP-EUR": {
        "symbol": "XRP-EUR",
        "long": True,
        "short": False,
        "initialCapitalLong": 700,
        "initialCapitalShort": 500,
        "order_round_factor": 1,
        "short_proxy_1": "XRP-1SHORT-EUR",
        "short_proxy_2": "XRP-2SHORT-EUR"
    }
}
