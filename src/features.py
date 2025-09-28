"""features.py
Compute indicators and features.
"""
import pandas as pd
import ta

def add_technical_indicators(df):
    df = df.copy()
    df['sma_10'] = df['close'].rolling(10).mean()
    df['sma_50'] = df['close'].rolling(50).mean()
    df['ema_10'] = df['close'].ewm(span=10).mean()
    df['rsi_14'] = ta.momentum.rsi(df['close'], window=14)
    df['macd'] = ta.trend.macd_diff(df['close'])
    df['return_1'] = df['close'].pct_change(1)
    df = df.dropna()
    return df
