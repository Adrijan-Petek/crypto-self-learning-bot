import fs from "node:fs/promises";
import path from "node:path";

export type Report = {
  run_id: string;
  created_at_utc: string;
  mode: string;
  symbol: string;
  timeframe: string;
  data_source: string;
  predict_horizon: number;
  fee_rate: number;
  initial_balance: number;
  final_equity: number;
  equity_curve_len: number;
  total_return_pct: number;
  buy_hold_return_pct: number;
  max_drawdown_pct: number;
  annualized_sharpe: number;
  calmar_ratio: number;
  closed_trades: number;
  wins: number;
  losses: number;
  win_rate_pct: number;
  exposure_pct: number;
  model_validation_accuracy: number;
  report_path: string;
};

export type BotConfig = {
  symbol: string;
  timeframe: string;
  initial_balance: number;
  fee_rate: number;
  train_window: number;
  predict_horizon: number;
  model_type: string;
  data_mode?: string;
  exchange_name?: string;
  limit?: number;
  report_dir?: string;
  save_model?: boolean;
  model_path?: string;
};

export type EquityPoint = {
  timestamp: string;
  equity: number;
};

const defaults: { report: Report; config: BotConfig } = {
  report: {
    run_id: "sample",
    created_at_utc: new Date(0).toISOString(),
    mode: "backtest",
    symbol: "BTC/USDT",
    timeframe: "1h",
    data_source: "sample csv",
    predict_horizon: 1,
    fee_rate: 0.001,
    initial_balance: 10000,
    final_equity: 10000,
    equity_curve_len: 0,
    total_return_pct: 0,
    buy_hold_return_pct: 0,
    max_drawdown_pct: 0,
    annualized_sharpe: 0,
    calmar_ratio: 0,
    closed_trades: 0,
    wins: 0,
    losses: 0,
    win_rate_pct: 0,
    exposure_pct: 0,
    model_validation_accuracy: 0,
    report_path: "reports/sample-report.json",
  },
  config: {
    symbol: "BTC/USDT",
    timeframe: "1h",
    initial_balance: 10000,
    fee_rate: 0.001,
    train_window: 500,
    predict_horizon: 1,
    model_type: "random_forest",
  },
};

function repoPath(...parts: string[]): string {
  return path.resolve(process.cwd(), "..", ...parts);
}

async function readJson<T>(filePath: string): Promise<T | null> {
  try {
    const data = await fs.readFile(filePath, "utf-8");
    return JSON.parse(data) as T;
  } catch {
    return null;
  }
}

export async function getReport(): Promise<Report> {
  const report = await readJson<Report>(repoPath("reports", "sample-report.json"));
  return report ?? defaults.report;
}

export async function getConfig(): Promise<BotConfig> {
  const config = await readJson<BotConfig>(repoPath("config", "bot.config.json"));
  return config ?? defaults.config;
}

export async function getHistory(limit = 200): Promise<Report[]> {
  try {
    const data = await fs.readFile(repoPath("reports", "backtest-history.jsonl"), "utf-8");
    const lines = data
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean)
      .slice(-limit);
    return lines
      .map((line) => {
        try {
          return JSON.parse(line) as Report;
        } catch {
          return null;
        }
      })
      .filter((row): row is Report => row !== null)
      .reverse();
  } catch {
    return [];
  }
}

export async function getEquityCurve(limit = 1200): Promise<EquityPoint[]> {
  try {
    const data = await fs.readFile(repoPath("reports", "latest-equity-curve.csv"), "utf-8");
    const rows = data
      .trim()
      .split("\n")
      .slice(1)
      .map((line) => {
        const [timestamp, equity] = line.split(",");
        return {
          timestamp,
          equity: Number(equity),
        };
      })
      .filter((row) => row.timestamp && Number.isFinite(row.equity));
    return rows.slice(-limit);
  } catch {
    return [];
  }
}

export async function getPriceCloseSeries(limit = 300): Promise<number[]> {
  try {
    const data = await fs.readFile(repoPath("reports", "sample-data.csv"), "utf-8");
    const lines = data.trim().split("\n").slice(1);
    const values = lines
      .map((line) => Number(line.split(",")[4]))
      .filter((value) => Number.isFinite(value));
    return values.slice(-limit);
  } catch {
    return [];
  }
}
