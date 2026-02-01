import {
  getConfig,
  getEquityCurve,
  getHistory,
  getPriceCloseSeries,
  getReport,
} from "@/lib/repo-data";

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const number = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
});

function pct(value: number): string {
  return `${number.format(value)}%`;
}

function linePath(values: number[], width: number, height: number, padding = 10): string {
  if (values.length < 2) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = (width - padding * 2) / (values.length - 1);

  return values
    .map((value, index) => {
      const x = padding + index * step;
      const y = height - padding - ((value - min) / range) * (height - padding * 2);
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

function positiveClass(value: number): string {
  return value >= 0 ? "text-emerald-600" : "text-rose-600";
}

export default async function Home() {
  const [report, config, history, equityCurve, closes] = await Promise.all([
    getReport(),
    getConfig(),
    getHistory(50),
    getEquityCurve(600),
    getPriceCloseSeries(220),
  ]);

  const recentRuns = history.slice(0, 8);
  const equityValues = equityCurve.map((point) => point.equity);
  const modelEdge = report.total_return_pct - report.buy_hold_return_pct;

  const equityPath = linePath(equityValues, 820, 220);
  const closePath = linePath(closes, 820, 140);

  const latestTimestamp = equityCurve.length
    ? equityCurve[equityCurve.length - 1].timestamp
    : report.created_at_utc;

  return (
    <main className="min-h-screen bg-[var(--paper)] text-[var(--ink)]">
      <section className="relative overflow-hidden border-b border-[var(--ink)]/10 pb-16">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_10%_10%,rgba(16,185,129,0.15),transparent_40%),radial-gradient(circle_at_90%_20%,rgba(245,158,11,0.14),transparent_45%)]" />
        <div className="absolute inset-0 bg-grid" />

        <div className="relative mx-auto flex max-w-7xl flex-col gap-12 px-6 pt-10 lg:px-10">
          <header className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--ink)] text-[var(--paper)] font-[var(--font-display)] text-xl shadow-[0_10px_24px_rgba(15,23,42,0.2)]">
                SL
              </span>
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">alpha control room</p>
                <h1 className="font-[var(--font-display)] text-2xl sm:text-3xl">Crypto Self-Learning Bot</h1>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <span className="rounded-full border border-[var(--ink)]/20 bg-white/80 px-3 py-1">
                {config.symbol}
              </span>
              <span className="rounded-full border border-[var(--ink)]/20 bg-white/80 px-3 py-1">
                {config.timeframe}
              </span>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-emerald-700">backtest ready</span>
            </div>
          </header>

          <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
            <div>
              <p className="inline-flex rounded-full border border-[var(--ink)]/15 bg-white/80 px-3 py-1 text-xs uppercase tracking-[0.22em] text-[var(--muted)]">
                full build dashboard
              </p>
              <h2 className="mt-6 max-w-3xl font-[var(--font-display)] text-4xl leading-tight sm:text-5xl">
                Train, evaluate, and present your strategy performance with an executive-grade interface.
              </h2>
              <p className="mt-4 max-w-2xl text-lg text-[var(--muted)]">
                The app reads your latest report, equity curve, and run history from Python outputs so every card,
                chart, and benchmark syncs to the backtest pipeline.
              </p>
              <div className="mt-7 flex flex-wrap gap-4 text-sm">
                <a
                  href="#performance"
                  className="rounded-full bg-[var(--ink)] px-4 py-2 text-[var(--paper)] transition hover:translate-y-[-1px]"
                >
                  Performance
                </a>
                <a
                  href="#history"
                  className="rounded-full border border-[var(--ink)]/20 bg-white px-4 py-2 transition hover:border-[var(--ink)]"
                >
                  Run History
                </a>
              </div>
            </div>

            <div className="rounded-3xl border border-white/70 bg-white/85 p-6 shadow-[0_20px_60px_rgba(15,23,42,0.14)]">
              <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">Latest snapshot</p>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <div className="rounded-2xl bg-[var(--ink)] p-4 text-[var(--paper)]">
                  <p className="text-xs uppercase tracking-[0.2em] text-white/60">Final Equity</p>
                  <p className="mt-2 font-[var(--font-display)] text-2xl">{currency.format(report.final_equity)}</p>
                </div>
                <div className="rounded-2xl border border-[var(--ink)]/10 bg-white p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">Model Acc</p>
                  <p className="mt-2 font-[var(--font-display)] text-2xl">
                    {pct(report.model_validation_accuracy * 100)}
                  </p>
                </div>
                <div className="rounded-2xl border border-[var(--ink)]/10 bg-white p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">Strategy Return</p>
                  <p className={`mt-2 font-[var(--font-display)] text-2xl ${positiveClass(report.total_return_pct)}`}>
                    {pct(report.total_return_pct)}
                  </p>
                </div>
                <div className="rounded-2xl border border-[var(--ink)]/10 bg-white p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">vs Buy/Hold</p>
                  <p className={`mt-2 font-[var(--font-display)] text-2xl ${positiveClass(modelEdge)}`}>
                    {pct(modelEdge)}
                  </p>
                </div>
              </div>
              <p className="mt-4 text-xs text-[var(--muted)]">Last equity timestamp: {latestTimestamp}</p>
            </div>
          </div>
        </div>
      </section>

      <section id="performance" className="mx-auto grid max-w-7xl gap-8 px-6 py-12 lg:px-10">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Sharpe" value={number.format(report.annualized_sharpe)} />
          <MetricCard label="Max Drawdown" value={pct(report.max_drawdown_pct)} />
          <MetricCard label="Win Rate" value={pct(report.win_rate_pct)} />
          <MetricCard label="Closed Trades" value={number.format(report.closed_trades)} />
        </div>

        <div className="grid gap-8 lg:grid-cols-[1.5fr_1fr]">
          <div className="rounded-3xl border border-[var(--ink)]/10 bg-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">Equity Curve</p>
                <h3 className="mt-1 font-[var(--font-display)] text-2xl">Portfolio growth trace</h3>
              </div>
              <p className="text-xs text-[var(--muted)]">{equityValues.length} points</p>
            </div>

            <div className="mt-5 rounded-2xl bg-[var(--ink)]/5 p-4">
              <svg viewBox="0 0 820 220" className="h-56 w-full">
                <path d={equityPath} fill="none" stroke="url(#equity)" strokeWidth="3.5" strokeLinecap="round" />
                <defs>
                  <linearGradient id="equity" x1="0" x2="1">
                    <stop offset="0%" stopColor="#0f172a" />
                    <stop offset="55%" stopColor="#10b981" />
                    <stop offset="100%" stopColor="#f59e0b" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>

          <aside className="rounded-3xl border border-[var(--ink)]/10 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
            <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">Model + Risk</p>
            <h3 className="mt-1 font-[var(--font-display)] text-2xl">Control panel</h3>
            <dl className="mt-5 space-y-3 text-sm">
              <Row k="Symbol" v={config.symbol} />
              <Row k="Timeframe" v={config.timeframe} />
              <Row k="Model" v={config.model_type} />
              <Row k="Predict horizon" v={String(config.predict_horizon)} />
              <Row k="Fee rate" v={String(config.fee_rate)} />
              <Row k="Initial balance" v={currency.format(config.initial_balance)} />
              <Row k="Exposure" v={pct(report.exposure_pct)} />
              <Row k="Calmar" v={number.format(report.calmar_ratio)} />
            </dl>
          </aside>
        </div>

        <div className="rounded-3xl border border-[var(--ink)]/10 bg-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">Market context</p>
              <h3 className="mt-1 font-[var(--font-display)] text-2xl">Sample close-price snapshot</h3>
            </div>
            <p className="text-xs text-[var(--muted)]">{closes.length} closes</p>
          </div>
          <div className="mt-5 rounded-2xl bg-[var(--ink)]/5 p-4">
            <svg viewBox="0 0 820 140" className="h-40 w-full">
              <path d={closePath} fill="none" stroke="#334155" strokeWidth="2.5" strokeLinecap="round" />
            </svg>
          </div>
        </div>
      </section>

      <section id="history" className="mx-auto max-w-7xl px-6 pb-20 lg:px-10">
        <div className="rounded-3xl border border-[var(--ink)]/10 bg-white p-6 shadow-[0_20px_55px_rgba(15,23,42,0.1)]">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">Run archive</p>
              <h3 className="mt-1 font-[var(--font-display)] text-2xl">Recent backtests</h3>
            </div>
            <div className="rounded-full border border-[var(--ink)]/10 bg-[var(--ink)]/5 px-3 py-1 text-xs text-[var(--muted)]">
              {history.length} stored runs
            </div>
          </div>

          <div className="mt-5 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-[0.16em] text-[var(--muted)]">
                <tr>
                  <th className="px-3 py-2">Run</th>
                  <th className="px-3 py-2">Date (UTC)</th>
                  <th className="px-3 py-2">Return</th>
                  <th className="px-3 py-2">MDD</th>
                  <th className="px-3 py-2">Sharpe</th>
                  <th className="px-3 py-2">Trades</th>
                </tr>
              </thead>
              <tbody>
                {recentRuns.length > 0 ? (
                  recentRuns.map((run) => (
                    <tr key={run.run_id} className="border-t border-[var(--ink)]/8">
                      <td className="px-3 py-3 font-medium">{run.run_id}</td>
                      <td className="px-3 py-3 text-[var(--muted)]">{run.created_at_utc}</td>
                      <td className={`px-3 py-3 font-medium ${positiveClass(run.total_return_pct)}`}>
                        {pct(run.total_return_pct)}
                      </td>
                      <td className="px-3 py-3 text-[var(--muted)]">{pct(run.max_drawdown_pct)}</td>
                      <td className="px-3 py-3 text-[var(--muted)]">{number.format(run.annualized_sharpe)}</td>
                      <td className="px-3 py-3 text-[var(--muted)]">{run.closed_trades}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="px-3 py-3 text-[var(--muted)]" colSpan={6}>
                      No history found yet. Run `./.venv/bin/python -m src.bot --mode backtest --save_model`.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="rounded-2xl border border-[var(--ink)]/10 bg-white px-4 py-4 shadow-[0_12px_30px_rgba(15,23,42,0.07)]">
      <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">{label}</p>
      <p className="mt-2 font-[var(--font-display)] text-2xl">{value}</p>
    </article>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-center justify-between border-b border-[var(--ink)]/10 pb-2">
      <dt className="text-[var(--muted)]">{k}</dt>
      <dd className="font-medium">{v}</dd>
    </div>
  );
}
