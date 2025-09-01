from __future__ import annotations
import re
from rapidfuzz import fuzz

def normalize_issuer(name: str) -> str:
    # Strip common suffixes and punctuation, collapse whitespace
    s = re.sub(r'\b(Inc|Incorporated|Corp|Corporation|LLC|LP|Ltd|S\.A\.|AG|PLC)\.?\b', '', name, flags=re.I)
    s = re.sub(r'[^A-Za-z0-9 &\-]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def fuzzy_ratio(a: str, b: str) -> int:
    return fuzz.token_set_ratio(a, b)
