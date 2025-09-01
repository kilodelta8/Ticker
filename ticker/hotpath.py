from __future__ import annotations
from datetime import date
from sqlmodel import select
from .db import get_session
from .models import Filing, Trade
from .utils.logging import info, banner
from .fetch import house as fetch_house
from .fetch import senate as fetch_senate
from .parse.ptr import parse_pdf_file
from .enrich.members import load_members
from .enrich.committees import load_committees
from .mapsec.issuers import map_issuer_to_ticker
from .score.signals import score_all_new_trades, compute_follow_scores
from .notify.alerts import send_alerts

def _today_minus(days: int) -> date:
    from datetime import timedelta
    return date.today() - timedelta(days=days)

def ingest_since(days: int = 30) -> int:
    """Ingest filings since a given number of days ago."""
    since = _today_minus(days)
    load_members()
    load_committees()
    new = 0
    with get_session() as s:
        for row in fetch_house.list_new_filings(since):
            f = s.get(Filing, row["filing_id"])
            if not f:
                f = Filing(
                    filing_id=row["filing_id"],
                    source="house",
                    filer_member_id=row.get("filer_member_id"),
                    filer_name_raw=row["filer_name_raw"],
                    filed_date=date.fromisoformat(row["filed_date"]),
                    url=row.get("url"),
                    file_local_path=row.get("file_local_path"),
                    doc_type=row.get("doc_type", "PTR"),
                    status="fetched",
                )
                s.add(f)
                new += 1
        for row in fetch_senate.list_new_filings(since):
            f = s.get(Filing, row["filing_id"])
            if not f:
                f = Filing(
                    filing_id=row["filing_id"],
                    source="senate",
                    filer_member_id=row.get("filer_member_id"),
                    filer_name_raw=row["filer_name_raw"],
                    filed_date=date.fromisoformat(row["filed_date"]),
                    url=row.get("url"),
                    file_local_path=row.get("file_local_path"),
                    doc_type=row.get("doc_type", "PTR"),
                    status="fetched",
                )
                s.add(f)
                new += 1
        s.commit()
    info(f"Ingested {new} new filings")
    return new

def parse_all() -> int:
    """Parse all filings into trades."""
    n = 0
    with get_session() as s:
        filings = s.exec(select(Filing)).all()
        for f in filings:
            trades, _ = parse_pdf_file(f.file_local_path or "", f)
            old = s.exec(select(Trade).where(Trade.filing_id == f.filing_id)).all()
            for o in old:
                s.delete(o)
            for tr in trades:
                s.add(tr)
                n += 1
            f.status = "parsed"
        s.commit()
    info(f"Parsed {n} trades")
    return n

def map_all(fuzzy: bool = True) -> int:
    """Map issuers to tickers."""
    m = 0
    with get_session() as s:
        trades = s.exec(select(Trade)).all()
        for t in trades:
            if not t.ticker:
                tk, conf, meth = map_issuer_to_ticker(t.issuer_raw, fuzzy=fuzzy)
                if tk:
                    t.ticker = tk
                    t.confidence = conf
                    t.map_method = meth
                    m += 1
        s.commit()
    info(f"Mapped {m} issuers to tickers")
    return m

def run_hotpath_once(score: bool = True, alerts: bool = False) -> None:
    """Run one full ingestion → parsing → mapping → scoring pipeline."""
    banner("Hotpath")
    ingest_since(60)
    parse_all()
    map_all(True)
    if score:
        score_all_new_trades()
        compute_follow_scores()
    if alerts:
        send_alerts(["New filings processed and scored"])
