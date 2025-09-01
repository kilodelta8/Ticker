from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

@dataclass
class Config:
    dev: bool = os.getenv("TICKER_DEV", "1") == "1"
    db_url: str = os.getenv("TICKER_DB_URL", "sqlite:///ticker.db")
    tz: str = os.getenv("TICKER_TZ", "America/New_York")

CFG = Config()
