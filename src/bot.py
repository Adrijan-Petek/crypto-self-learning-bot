"""bot.py
CLI entrypoint for backtesting and reporting.

Example:
  python -m src.bot --mode backtest --symbol BTC/USDT --timeframe 1h
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from src.data import fetch_ohlcv, load_sample_csv
from src.features import add_technical_indicators
from src.model import ModelWrapper

load_dotenv()


def timeframe_periods_per_year(timeframe: str) -> int:
    mapping = {
        "1m": 525600,
        "5m": 105120,
        "15m": 35040,
        "30m": 17520,
        "1h": 8760,
        "4h": 2190,
        "1d": 365,
    }
    return mapping.get(timeframe, 365)


def prepare_dataset(df: pd.DataFrame, predict_horizon: int = 1) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    df = add_technical_indicators(df)
    # Label each row with whether the future return is positive.
    df["future_return"] = df["close"].pct_change(predict_horizon).shift(-predict_horizon)
    df = df.dropna()
    df["label"] = (df["future_return"] > 0).astype(int)

    feature_cols = ["sma_10", "sma_50", "ema_10", "rsi_14", "macd", "return_1"]
    features = df[feature_cols].values
    labels = df["label"].values
    return df, features, labels


def run_strategy(
    df: pd.DataFrame,
    preds: np.ndarray,
    fee_rate: float,
    initial_balance: float,
) -> Dict[str, object]:
    cash = initial_balance
    position_qty = 0.0
    entry_value = 0.0
    equity_curve: List[float] = []
    closed_trade_pnls: List[float] = []
    bars_in_position = 0

    for i in range(len(df)):
        price = float(df["close"].iloc[i])
        signal = int(preds[i]) if i < len(preds) else 0

        if signal == 1 and position_qty == 0.0 and cash > 0.0:
            spendable = cash * (1 - fee_rate)
            position_qty = spendable / price
            entry_value = cash
            cash = 0.0
        elif signal == 0 and position_qty > 0.0:
            proceeds = position_qty * price * (1 - fee_rate)
            pnl = proceeds - entry_value
            closed_trade_pnls.append(pnl)
            cash = proceeds
            position_qty = 0.0
            entry_value = 0.0

        if position_qty > 0.0:
            bars_in_position += 1

        equity_curve.append(cash + position_qty * price)

    if position_qty > 0.0:
        final_price = float(df["close"].iloc[-1])
        proceeds = position_qty * final_price * (1 - fee_rate)
        pnl = proceeds - entry_value
        closed_trade_pnls.append(pnl)
        cash = proceeds
        position_qty = 0.0
        equity_curve[-1] = cash

    wins = sum(1 for pnl in closed_trade_pnls if pnl > 0)
    losses = sum(1 for pnl in closed_trade_pnls if pnl <= 0)

    return {
        "equity_curve": equity_curve,
        "final_equity": cash,
        "closed_trades": len(closed_trade_pnls),
        "wins": wins,
        "losses": losses,
        "bars_in_position": bars_in_position,
    }


def max_drawdown(equity_curve: np.ndarray) -> float:
    if equity_curve.size == 0:
        return 0.0
    running_max = np.maximum.accumulate(equity_curve)
    drawdowns = (equity_curve - running_max) / running_max
    return float(drawdowns.min())


def annualized_sharpe(equity_curve: np.ndarray, periods_per_year: int) -> float:
    if equity_curve.size < 2:
        return 0.0
    returns = np.diff(equity_curve) / np.where(equity_curve[:-1] == 0, 1, equity_curve[:-1])
    std = np.std(returns)
    if std == 0:
        return 0.0
    return float(np.sqrt(periods_per_year) * (np.mean(returns) / std))


def build_report(
    args: argparse.Namespace,
    df: pd.DataFrame,
    model_accuracy: float,
    strategy_result: Dict[str, object],
    data_source: str,
) -> Dict[str, object]:
    equity_curve = np.array(strategy_result["equity_curve"], dtype=float)
    final_equity = float(strategy_result["final_equity"])
    total_return = (final_equity / args.initial_balance) - 1 if args.initial_balance else 0.0
    bh_return = (float(df["close"].iloc[-1]) / float(df["close"].iloc[0])) - 1 if len(df) > 1 else 0.0
    mdd = max_drawdown(equity_curve)
    periods = timeframe_periods_per_year(args.timeframe)
    sharpe = annualized_sharpe(equity_curve, periods)
    calmar = (total_return / abs(mdd)) if mdd < 0 else 0.0

    closed_trades = int(strategy_result["closed_trades"])
    wins = int(strategy_result["wins"])
    win_rate = (wins / closed_trades) if closed_trades else 0.0
    exposure = (int(strategy_result["bars_in_position"]) / len(df)) if len(df) else 0.0

    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ")

    return {
        "run_id": run_id,
        "created_at_utc": now.isoformat(),
        "mode": args.mode,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "data_source": data_source,
        "predict_horizon": args.predict_horizon,
        "fee_rate": args.fee_rate,
        "initial_balance": args.initial_balance,
        "final_equity": round(final_equity, 2),
        "equity_curve_len": len(equity_curve),
        "total_return_pct": round(total_return * 100, 2),
        "buy_hold_return_pct": round(bh_return * 100, 2),
        "max_drawdown_pct": round(mdd * 100, 2),
        "annualized_sharpe": round(sharpe, 3),
        "calmar_ratio": round(calmar, 3),
        "closed_trades": closed_trades,
        "wins": wins,
        "losses": int(strategy_result["losses"]),
        "win_rate_pct": round(win_rate * 100, 2),
        "exposure_pct": round(exposure * 100, 2),
        "model_validation_accuracy": round(model_accuracy, 4),
        "report_path": str(Path(args.report_dir) / "sample-report.json"),
    }


def append_history(report: Dict[str, object], report_dir: str) -> None:
    history_path = Path(report_dir) / "backtest-history.jsonl"
    with open(history_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(report) + "\n")


def write_equity_curve(df: pd.DataFrame, equity_curve: List[float], report_dir: str) -> None:
    curve = pd.DataFrame(
        {
            "timestamp": df.index[: len(equity_curve)],
            "equity": equity_curve,
        }
    )
    curve.to_csv(Path(report_dir) / "latest-equity-curve.csv", index=False)


def run_backtest(args: argparse.Namespace) -> None:
    os.makedirs(args.report_dir, exist_ok=True)

    if args.data_mode == "exchange":
        df = fetch_ohlcv(
            exchange_name=args.exchange_name,
            symbol=args.symbol,
            timeframe=args.timeframe,
            limit=args.limit,
        )
        data_source = f"{args.exchange_name} live OHLCV"
    else:
        df = load_sample_csv(path=args.data_path)
        data_source = f"sample csv ({args.data_path or 'reports/sample-data.csv'})"

    df, X, y = prepare_dataset(df, predict_horizon=args.predict_horizon)

    model = ModelWrapper()
    val_accuracy = model.train(X, y)
    preds, _ = model.predict(X)

    strategy_result = run_strategy(
        df,
        preds=preds,
        fee_rate=args.fee_rate,
        initial_balance=args.initial_balance,
    )

    if args.save_model:
        model.save(path=args.model_path)

    write_equity_curve(df, strategy_result["equity_curve"], args.report_dir)
    report = build_report(
        args=args,
        df=df,
        model_accuracy=val_accuracy,
        strategy_result=strategy_result,
        data_source=data_source,
    )

    report_path = Path(args.report_dir) / "sample-report.json"
    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    append_history(report, args.report_dir)

    print("Backtest complete")
    print(f"- Report: {report_path}")
    print(f"- Final equity: {report['final_equity']}")
    print(f"- Return: {report['total_return_pct']}%")
    print(f"- Max drawdown: {report['max_drawdown_pct']}%")
    print(f"- Sharpe: {report['annualized_sharpe']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crypto self-learning bot CLI")
    parser.add_argument("--mode", type=str, default="backtest")
    parser.add_argument("--symbol", type=str, default=os.getenv("DEFAULT_SYMBOL", "BTC/USDT"))
    parser.add_argument("--timeframe", type=str, default=os.getenv("TIMEFRAME", "1h"))
    parser.add_argument("--predict_horizon", type=int, default=1)
    parser.add_argument("--fee_rate", type=float, default=0.001)
    parser.add_argument("--initial_balance", type=float, default=10000)
    parser.add_argument("--report_dir", type=str, default=os.getenv("REPORT_DIR", "reports"))

    parser.add_argument("--data_mode", type=str, choices=["sample", "exchange"], default="sample")
    parser.add_argument("--data_path", type=str, default=None)
    parser.add_argument("--exchange_name", type=str, default="binance")
    parser.add_argument("--limit", type=int, default=1000)

    parser.add_argument("--save_model", action="store_true")
    parser.add_argument("--model_path", type=str, default=os.getenv("MODEL_PATH", "reports/model.joblib"))
    return parser.parse_args()


if __name__ == "__main__":
    cli_args = parse_args()
    if cli_args.mode == "backtest":
        run_backtest(cli_args)
    else:
        print("Only backtest mode is implemented.")
