"""bot.py
Simple self-learning loop and backtester.
Usage examples:
  python -m src.bot --mode backtest --symbol BTC/USDT
"""
import argparse, os, json
import pandas as pd
import numpy as np
from src.data import load_sample_csv, fetch_ohlcv
from src.features import add_technical_indicators
from src.model import ModelWrapper
from dotenv import load_dotenv

load_dotenv()

def prepare_dataset(df, predict_horizon=1):
    df = add_technical_indicators(df)
    # label: 1 if future return positive, else 0
    df['future_return'] = df['close'].pct_change(predict_horizon).shift(-predict_horizon)
    df = df.dropna()
    df['label'] = (df['future_return'] > 0).astype(int)
    features = df[['sma_10','sma_50','ema_10','rsi_14','macd','return_1']].values
    labels = df['label'].values
    return df, features, labels

def backtest(df, preds, fee_rate=0.001, initial_balance=10000):
    balance = initial_balance
    position = 0
    equity_curve = []
    for i in range(len(df)-1):
        price = df['close'].iloc[i]
        action = preds[i]  # 1 -> buy/hold, 0 -> sell/short(not implemented)
        if action == 1 and position == 0:
            # buy full balance (simplified)
            position = balance / price
            balance = 0
        elif action == 0 and position > 0:
            balance = position * price * (1 - fee_rate)
            position = 0
        equity = balance + position * price
        equity_curve.append(equity)
    return equity_curve

def run_backtest(args):
    df = load_sample_csv()
    df, X, y = prepare_dataset(df, predict_horizon=args.predict_horizon)
    model = ModelWrapper()
    model.train(X, y)
    preds, _ = model.predict(X)
    equity = backtest(df, preds, fee_rate=args.fee_rate, initial_balance=args.initial_balance)
    report = {
        'final_equity': equity[-1] if equity else args.initial_balance,
        'initial_balance': args.initial_balance,
        'equity_curve_len': len(equity)
    }
    os.makedirs(args.report_dir, exist_ok=True)
    with open(os.path.join(args.report_dir, 'sample-report.json'), 'w') as f:
        json.dump(report, f, indent=2)
    print('Backtest complete. Report saved to', args.report_dir)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--mode', type=str, default='backtest')
    p.add_argument('--symbol', type=str, default=os.getenv('DEFAULT_SYMBOL','BTC/USDT'))
    p.add_argument('--timeframe', type=str, default=os.getenv('TIMEFRAME','1h'))
    p.add_argument('--predict_horizon', type=int, default=1)
    p.add_argument('--fee_rate', type=float, default=0.001)
    p.add_argument('--initial_balance', type=float, default=10000)
    p.add_argument('--report_dir', type=str, default=os.getenv('REPORT_DIR','reports'))
    args = p.parse_args()
    if args.mode == 'backtest':
        run_backtest(args)
    else:
        print('Only backtest mode implemented in this template.')
