<<<<<<< HEAD
# Web (placeholder)

This folder is a placeholder for a front-end dashboard. You can create a Next.js or React app here.
A minimal Next.js index page might fetch `reports/sample-report.json` and render charts.

Example quick-start:
```bash
npx create-next-app web
```
Then add an API route or static fetch to consume `reports/sample-report.json`.
=======
# Web Dashboard

Production-style Next.js dashboard for the Crypto Self-Learning Bot.

It reads generated backend artifacts from the repository root and presents:
- latest run KPIs,
- portfolio equity curve,
- market context series,
- and recent backtest history.

## Stack

- Next.js App Router (`src/app`)
- TypeScript
- Tailwind CSS v4
- Server-side file loading from Python artifacts

## Data files consumed

The UI reads these files from `../` (repo root):
- `reports/sample-report.json`
- `reports/backtest-history.jsonl`
- `reports/latest-equity-curve.csv`
- `reports/sample-data.csv`
- `config/bot.config.json`

## API routes

- `GET /api/report` -> latest report JSON
- `GET /api/config` -> bot config JSON
- `GET /api/history` -> backtest history array
- `GET /api/equity` -> equity curve array

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Build and start

```bash
npm run build
npm run start
```

## Where to edit

- `src/app/page.tsx` main dashboard page
- `src/lib/repo-data.ts` file readers and data shaping
- `src/app/api/*/route.ts` API endpoints
- `src/app/globals.css` global look-and-feel tokens
- `src/app/layout.tsx` metadata and font setup
>>>>>>> fb80fe8 (Full app build: backend, dashboard, and professional docs)
