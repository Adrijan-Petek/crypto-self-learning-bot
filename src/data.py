"""data.py
Market data access helpers for sample CSV and CCXT exchange data.
"""

import os

import ccxt
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def fetch_ohlcv(exchange_name, symbol, timeframe="1h", since=None, limit=1000):
    exchange_cls = getattr(ccxt, exchange_name, None)
    if exchange_cls is None:
        raise ValueError(f"Unsupported exchange '{exchange_name}' in ccxt.")

    exchange = exchange_cls({"enableRateLimit": True})
    print(f"Fetching OHLCV from {exchange_name} for {symbol} timeframe {timeframe}")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
    if not ohlcv:
        raise ValueError("No OHLCV rows returned from exchange.")

    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)
    return df


def load_sample_csv(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "reports", "sample-data.csv")

    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    if df.empty:
        raise ValueError(f"Sample CSV at '{path}' is empty.")

    df.sort_index(inplace=True)
    return df
