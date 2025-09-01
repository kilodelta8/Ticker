2️⃣ README.md
# Ticker (CLI/TUI)

A command-line and terminal-UI app that ingests U.S. Congressional trade disclosures, parses and normalizes them, maps issuers to tickers/CIKs, computes "Follow Likelihood %" scores for members, and lets you search portfolios and view daily stats. It also supports a watcher that targets a ≤5-minute freshness objective after new filings appear.

> **Note:** Live endpoints sometimes change or throttle; this repo ships **DEV mode** with fixtures so you can run the app end-to-end immediately. Switch off DEV when you're ready to hit real sources and add your credentials/robots-friendly settings.

## Quick start (DEV mode)

```bash
# 1) Install (suggest using Poetry, but pip works too)
pip install -e .
# or
poetry install

# 2) Initialize the DB
ticker init-db

# 3) Ingest + parse + score using fixtures
export TICKER_DEV=1   # or set in .env
ticker hotpath run --score --alerts

# 4) Launch the interactive menu
ticker menu
# When you exit the menu, a Daily Report table is printed automatically.

Live mode

Create a .env (copy .env.example) and set TICKER_DEV=0.

(Optional) Install Tesseract: sudo apt-get install tesseract-ocr (for scanned PDFs).

Start the watcher:

ticker watch start --interval 75 --jitter 20 --sources house,senate
ticker watch status


Manually run the hot path any time:

ticker hotpath run --score --alerts

Core commands

ticker init-db

ticker ingest house --since 2025-06-01

ticker ingest senate --since 2025-06-01

ticker parse --source house

ticker enrich members

ticker enrich committees

ticker map issuers --fuzzy

ticker score signals

ticker stats last-24h

ticker hotpath run --score --alerts

ticker watch start|status

ticker menu (TUI; shows Daily Report after exit)

Follow Likelihood %

A transparent heuristic intended for discovery (not advice). Inputs: recency, size bands, repeated buys, options activity, committee relevance, and a simple disclosure-anchored lookahead return proxy. See ticker/score/signals.py for details.

DEV fixtures

Members + committees (small sample)

Fixture filings & parsed trades

SEC ticker mapping sample

Price cache sample for backtests

Legal

This app processes public disclosures (e.g., STOCK Act). Check source terms and any commercial use restrictions. This is not investment advice.