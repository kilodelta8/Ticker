from __future__ import annotations
from typing import List
from ..utils.logging import info

def send_alerts(messages: List[str]) -> None:
    """Send alerts (currently logs to console)."""
    for m in messages:
        info(f"[ALERT] {m}")
