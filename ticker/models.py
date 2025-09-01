from __future__ import annotations
from typing import Optional
from datetime import date, datetime
from sqlmodel import SQLModel, Field

class Member(SQLModel, table=True):
    member_id: str = Field(primary_key=True)
    first: str
    last: str
    chamber: str  # house|senate
    state: str
    district: Optional[str] = None
    party: Optional[str] = None
    active: bool = True
    follow_score: float = 0.0
    follow_score_updated_at: Optional[datetime] = None

class Committee(SQLModel, table=True):
    committee_id: str = Field(primary_key=True)
    name: str
    chamber: str

class MemberCommittee(SQLModel, table=True):
    member_id: str = Field(foreign_key="member.member_id", primary_key=True)
    committee_id: str = Field(foreign_key="committee.committee_id", primary_key=True)
    role: Optional[str] = None

class Filing(SQLModel, table=True):
    filing_id: str = Field(primary_key=True)
    source: str
    filer_member_id: Optional[str] = Field(default=None, foreign_key="member.member_id")
    filer_name_raw: str
    filed_date: date
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    url: Optional[str] = None
    file_local_path: Optional[str] = None
    doc_type: str = "PTR"
    status: str = "fetched"
    checksum: Optional[str] = None

class Trade(SQLModel, table=True):
    trade_id: str = Field(primary_key=True)
    filing_id: str = Field(foreign_key="filing.filing_id")
    txn_date: date
    issuer_raw: str
    ticker: Optional[str] = None
    security_type: Optional[str] = "stock"
    txn_type: Optional[str] = None
    amount_band: Optional[str] = None
    comments_raw: Optional[str] = None
    confidence: float = 1.0
    map_method: Optional[str] = None

class Signal(SQLModel, table=True):
    signal_id: str = Field(primary_key=True)
    trade_id: str = Field(foreign_key="trade.trade_id")
    score: float
    tags: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PriceCache(SQLModel, table=True):
    ticker: str = Field(primary_key=True)
    as_of: date = Field(primary_key=True)
    close: float


class RunMetric(SQLModel, table=True):
    run_id: str = Field(primary_key=True)
    started_at: datetime
    finished_at: datetime
    stage: str
    success: bool
    details: Optional[str] = None

class MemberSnapshot(SQLModel, table=True):
    member_id: str = Field(foreign_key="member.member_id", primary_key=True)
    as_of_date: date = Field(primary_key=True)
    follow_score: float
    metrics_json: Optional[str] = None
