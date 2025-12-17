# Crypto Self-Learning Bot (Template)


A starter template for a self-learning crypto trading bot.  
Includes Python backend scripts for data ingestion, feature engineering, a simple ML model (Random Forest), a self-learning loop, backtesting utilities, sample reports, and a minimal web placeholder.

**This is a template** — you'll need to add your own API keys and tweak strategies before using with real money.

## Features
- Fetch OHLCV via CCXT (script stub)
- Compute common technical indicators (RSI, SMA, EMA)
- Train a simple supervised ML model (RandomForest) to predict short-term movement
- Simple self-learning loop that simulates trades and updates the model
- Backtesting metrics and sample JSON report
- GitHub Actions workflow for scheduled runs

## Quickstart (local)
1. Create a Python virtualenv:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Edit `.env` (create from `.env.example`) with your keys and config.

3. Run a backtest (sample):
```bash
python -m src.bot --symbol BTC/USDT --timeframe 1h --mode backtest
```

4. Run live (VERY RISKY — only after testing):
```bash
python -m src.bot --symbol BTC/USDT --timeframe 1h --mode paper
```

## Structure
```
crypto-self-learning-bot/
├─ src/
│  ├─ data.py
│  ├─ features.py
│  ├─ model.py
│  ├─ bot.py
├─ config/
│  └─ bot.config.json
├─ reports/
│  └─ sample-report.json
├─ web/
│  └─ README.md
├─ .github/workflows/daily-bot.yml
├─ .env.example
├─ requirements.txt
└─ README.md
```

## Notes & Warnings
- This template is educational. Do not use with real funds until thoroughly tested.
- Trading cryptocurrencies involves substantial risk.

