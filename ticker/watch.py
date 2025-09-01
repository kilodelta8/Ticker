from __future__ import annotations
import asyncio, random, time
from datetime import datetime
from .utils.logging import error, banner
from .hotpath import run_hotpath_once

class WatchState:
    last_poll: datetime | None = None
    last_change: datetime | None = None

STATE = WatchState()

async def run_watch(interval: int = 75, jitter: int = 20, sources: str = "house,senate"):
    """Continuously poll for changes and run the hotpath."""
    banner("Ticker Watcher Started")
    while True:
        start = time.monotonic()
        try:
            changed = await discover_changes()
            if changed:
                STATE.last_change = datetime.utcnow()
                await run_hotpath_once(score=True, alerts=True)
        except Exception as e:
            error(f"watch error: {e}")
        finally:
            STATE.last_poll = datetime.utcnow()
            sleep_for = max(5, interval + random.randint(-jitter, jitter) - (time.monotonic() - start))
            await asyncio.sleep(sleep_for)

async def discover_changes() -> bool:
    """Placeholder — in DEV mode always returns True, in live mode would check House/Senate endpoints."""
    return True

def status() -> dict:
    """Return watcher state as a dict (for CLI status)."""
    return {
        "last_poll": STATE.last_poll.isoformat() if STATE.last_poll else None,
        "last_change": STATE.last_change.isoformat() if STATE.last_change else None,
    }
