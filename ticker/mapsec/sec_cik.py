from __future__ import annotations
import os, json
from typing import Dict, Any

def load_company_tickers() -> Dict[str, Any]:
    """
    Load a sample set of SEC company tickers from fixtures.
    Keys are normalized company names -> {ticker, cik}.
    """
    path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "company_tickers_sample.json")
    path = os.path.normpath(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    out: Dict[str, Any] = {}
    for row in data:
        name = row["title"].lower()
        out[name] = {"ticker": row["ticker"], "cik": row["cik"]}
    return out
