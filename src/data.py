"""data.py
<<<<<<< HEAD
Fetch historical OHLCV using CCXT (stubbed to allow offline backtesting with CSV)
=======
Market data access helpers for sample CSV and CCXT exchange data.
>>>>>>> fb80fe8 (Full app build: backend, dashboard, and professional docs)
"""
import os
import pandas as pd
import ccxt
from dotenv import load_dotenv

load_dotenv()

def fetch_ohlcv(exchange_name, symbol, timeframe='1h', since=None, limit=1000):
<<<<<<< HEAD
    exchange_cls = getattr(ccxt, exchange_name)
    exchange = exchange_cls()
    print(f"Fetching OHLCV from {exchange_name} for {symbol} timeframe {timeframe}")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
=======
    exchange_cls = getattr(ccxt, exchange_name, None)
    if exchange_cls is None:
        raise ValueError(f"Unsupported exchange '{exchange_name}' in ccxt.")
    exchange = exchange_cls({"enableRateLimit": True})
    print(f"Fetching OHLCV from {exchange_name} for {symbol} timeframe {timeframe}")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
    if not ohlcv:
        raise ValueError("No OHLCV rows returned from exchange.")
    df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
>>>>>>> fb80fe8 (Full app build: backend, dashboard, and professional docs)
    return df

def load_sample_csv(path=None):
    # loads a small bundled CSV (sample)
    if path is None:
        path = os.path.join(os.path.dirname(__file__), '..', 'reports', 'sample-data.csv')
<<<<<<< HEAD
    return pd.read_csv(path, parse_dates=['timestamp'], index_col='timestamp')
=======
    df = pd.read_csv(path, parse_dates=['timestamp'], index_col='timestamp')
    if df.empty:
        raise ValueError(f"Sample CSV at '{path}' is empty.")
    df.sort_index(inplace=True)
    return df
>>>>>>> fb80fe8 (Full app build: backend, dashboard, and professional docs)
