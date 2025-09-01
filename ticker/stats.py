from __future__ import annotations
from datetime import datetime, timedelta, date
from typing import List
from rich.table import Table
from rich.console import Console
from sqlmodel import select
from .db import get_session
from .models import Filing, Trade, Signal, Member

console = Console()

def _last_24h_range():
    now = datetime.now()
    return now - timedelta(days=1), now

def table_daily_report() -> Table:
    since, now = _last_24h_range()
    t = Table(title=f"Ticker • Daily Report (last 24h) • as of {now.strftime('%Y-%m-%d %H:%M')}")
    t.add_column("#", justify="right")
    t.add_column("Member")
    t.add_column("Issuer / Ticker")
    t.add_column("Txn Date")
    t.add_column("Band")
    t.add_column("Score")

    with get_session() as s:
        # For fixtures: show trades in last 30 days and rank by signal score
        trades = s.exec(select(Trade)).all()
        trades = [tr for tr in trades if (date.today() - tr.txn_date).days <= 30]

        ranked: List[tuple] = []
        for tr in trades:
            sig = s.get(Signal, f"S-{tr.trade_id}")
            f = s.exec(select(Filing).where(Filing.filing_id == tr.filing_id)).first()
            mem = s.get(Member, f.filer_member_id) if f and f.filer_member_id else None
            ranked.append((sig.score if sig else 0.0, tr, mem))

        ranked.sort(key=lambda x: x[0], reverse=True)

        for i, (_, tr, mem) in enumerate(ranked[:10], start=1):
            name = f"{mem.first} {mem.last}" if mem else (f.filer_name_raw if f else "?")
            t.add_row(
                str(i),
                name,
                f"{tr.issuer_raw} / {tr.ticker or '-'}",
                tr.txn_date.isoformat(),
                tr.amount_band or "-",
                f"{(s.get(Signal, 'S-'+tr.trade_id).score if s.get(Signal, 'S-'+tr.trade_id) else 0):.2f}",
            )
    return t

def print_last_24h_report():
    table = table_daily_report()
    console.print(table)
