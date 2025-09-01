from __future__ import annotations
from typing import Optional
from ..utils.text import normalize_issuer, fuzzy_ratio
from .sec_cik import load_company_tickers

def map_issuer_to_ticker(name: str, fuzzy: bool = True) -> tuple[Optional[str], float, str]:
    """
    Map a raw issuer name to a stock ticker.
    
    Returns (ticker, confidence, method).
    - ticker: str or None
    - confidence: float between 0.0 and 1.0
    - method: "exact" | "fuzzy" | "none"
    """
    ref = load_company_tickers()
    norm = normalize_issuer(name).lower()

    # Exact match
    if norm in ref:
        return ref[norm]["ticker"], 0.99, "exact"

    # Fuzzy match
    if fuzzy:
        best_t, best_score = None, 0
        for k, v in ref.items():
            sc = fuzzy_ratio(norm, k)
            if sc > best_score:
                best_score, best_t = sc, v["ticker"]
        if best_score >= 85:
            return best_t, best_score / 100.0, "fuzzy"

    return None, 0.0, "none"
