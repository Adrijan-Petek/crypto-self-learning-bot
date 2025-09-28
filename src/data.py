"""data.py
Fetch historical OHLCV using CCXT (stubbed to allow offline backtesting with CSV)
"""
import os
import pandas as pd
import ccxt
from dotenv import load_dotenv

load_dotenv()

def fetch_ohlcv(exchange_name, symbol, timeframe='1h', since=None, limit=1000):
    exchange_cls = getattr(ccxt, exchange_name)
    exchange = exchange_cls()
    print(f"Fetching OHLCV from {exchange_name} for {symbol} timeframe {timeframe}")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def load_sample_csv(path=None):
    # loads a small bundled CSV (sample)
    if path is None:
        path = os.path.join(os.path.dirname(__file__), '..', 'reports', 'sample-data.csv')
    return pd.read_csv(path, parse_dates=['timestamp'], index_col='timestamp')
