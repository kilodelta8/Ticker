from __future__ import annotations
from datetime import date
from typing import List, Dict
import os, json
from ..config import CFG
from ..utils.logging import info

def list_new_filings(since: date) -> List[Dict]:
    """Return new House filings since a given date.
    In DEV mode, loads from fixtures.
    """
    if CFG.dev:
        fx_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "house_filings.json")
        fx_path = os.path.normpath(fx_path)
        with open(fx_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        out: List[Dict] = []
        for row in data:
            if date.fromisoformat(row["filed_date"]) >= since:
                out.append(row)

        info(f"Loaded {len(out)} House fixture filings since {since}")
        return out
    else:
        # TODO: implement live fetch from Clerk of House
        return []
