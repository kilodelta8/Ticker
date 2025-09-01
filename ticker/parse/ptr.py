from __future__ import annotations
import re, uuid
from datetime import date
from typing import List, Tuple, Optional
from ..models import Filing, Trade
from ..utils.text import normalize_issuer

# Matches lines like:
# 2025-08-20 | NVIDIA Corporation | NVDA | BUY | $50k-$100k
TRADE_LINE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+\|\s+(?P<issuer>[^|]+)\|\s*(?P<ticker>[A-Z.\-]{1,10})?\s*\|\s*(?P<type>BUY|SELL|Other)\s*\|\s*(?P<band>\$[\dk\-\$]+)",
    re.I,
)

def parse_text_to_trades(text: str, filing: Filing) -> List[Trade]:
    """Parse plain text into Trade objects."""
    trades: List[Trade] = []
    for m in TRADE_LINE.finditer(text):
        d = date.fromisoformat(m.group("date"))
        issuer = m.group("issuer").strip()
        ticker = (m.group("ticker") or "").strip() or None
        ttype = m.group("type").upper()
        band = m.group("band").replace(" ", "")

        trades.append(
            Trade(
                trade_id=str(uuid.uuid4()),
                filing_id=filing.filing_id,
                txn_date=d,
                issuer_raw=normalize_issuer(issuer),
                ticker=ticker,
                security_type="stock",
                txn_type=ttype.lower(),
                amount_band=band,
                comments_raw=None,
                confidence=0.95 if ticker else 0.75,
                map_method="extracted" if ticker else None,
            )
        )
    return trades

def parse_pdf_file(path: str, filing: Filing) -> Tuple[List[Trade], Optional[str]]:
    """Parse a filing file into trades + return raw text."""
    from .pdf import extract_text
    text = None

    # Allow direct .txt fixture files
    if path and path.lower().endswith(".txt"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            text = None

    if text is None:
        text = extract_text(path or "") or ""

    trades = parse_text_to_trades(text or "", filing)
    return trades, text
