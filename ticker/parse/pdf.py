from __future__ import annotations
import os
from typing import Optional

try:
    import pdfplumber  # type: ignore
except Exception:
    pdfplumber = None

def extract_text(path: str) -> Optional[str]:
    """Extract text from a PDF or text file."""
    if not os.path.exists(path):
        return None

    if pdfplumber is None:
        # Fallback: try to read as plain text
        try:
            with open(path, "rb") as f:
                data = f.read().decode("utf-8", errors="ignore")
                return data
        except Exception:
            return None

    try:
        with pdfplumber.open(path) as pdf:
            text = []
            for page in pdf.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    except Exception:
        return None
