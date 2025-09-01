from __future__ import annotations
import asyncio
import typer
from rich import print
from .db import init_db
from .hotpath import run_hotpath_once, ingest_since, parse_all, map_all
from .score.signals import score_all_new_trades, compute_follow_scores
from .enrich.members import load_members
from .enrich.committees import load_committees
from .stats import print_last_24h_report
from .watch import run_watch, status as watch_status
from .tui.app import run_menu

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Ticker CLI")

@app.command(name="init-db")
def init_db_cmd():
    """Initialize the database."""
    init_db()
    load_members()
    load_committees()
    print('[green]DB initialized and fixtures loaded.[/]')

@app.command()
def hotpath(action: str = typer.Argument("run"), score: bool = typer.Option(True), alerts: bool = typer.Option(False)):
    """Fetch → parse → map → (score) in one go."""
    if action != "run":
        raise typer.BadParameter("Only 'run' is supported")
    run_hotpath_once(score=score, alerts=alerts)

@app.command()
def ingest(source: str = typer.Argument(...), since: str = typer.Option(None)):
    """Ingest filings since a given date (YYYY-MM-DD)."""
    from datetime import date
    d = date.fromisoformat(since) if since else None
    ingest_since(60 if d is None else (date.today() - d).days)

@app.command()
def parse(source: str = typer.Option(None)):
    """Parse all filings (source arg is ignored in DEV mode)."""
    parse_all()

@app.command()
def enrich(what: str = typer.Argument(...)):
    """Enrich database with members or committees."""
    if what == "members":
        load_members()
    elif what == "committees":
        load_committees()
    else:
        raise typer.BadParameter("Unknown enrich target") 

@app.command()
def map(what: str = typer.Argument("issuers"), fuzzy: bool = typer.Option(True)):
    """Map issuers to tickers (using SEC reference data)."""
    if what != "issuers":
        raise typer.BadParameter("Only 'issuers' supported")
    map_all(fuzzy)

@app.command()
def score(what: str = typer.Argument("signals")):
    """Score trades and update follow likelihoods."""
    if what != "signals":
        raise typer.BadParameter("Only 'signals' supported")
    score_all_new_trades()
    compute_follow_scores()

@app.command()
def stats(period: str = typer.Argument("last-24h"), format: str = typer.Option("table")):
    """Show stats for the last 24h."""
    if period != "last-24h":
        raise typer.BadParameter("Only last-24h supported in MVP")
    print_last_24h_report()

@app.command()
def watch(action: str = typer.Argument(...), interval: int = typer.Option(75), jitter: int = typer.Option(20), sources: str = typer.Option("house,senate")):
    """Run or check the background watcher."""
    if action == "start":
        asyncio.run(run_watch(interval=interval, jitter=jitter, sources=sources))
    elif action == "status":
        from rich.pretty import pprint
        pprint(watch_status())
    else:
        raise typer.BadParameter("Use start|status") 

@app.command()
def menu():
    """Launch interactive TUI menu."""
    run_menu()
    print_last_24h_report()
