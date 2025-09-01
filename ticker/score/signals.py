from __future__ import annotations
from typing import List, Tuple
from datetime import date, datetime
from sqlmodel import select
from ..db import get_session
from ..models import Trade, Filing, Member, Signal, MemberSnapshot

def compute_trade_signal(trade: Trade, member: Member | None) -> Tuple[float, str, List[str]]:
    """Compute a score for a single trade."""
    score = 0.0
    tags: List[str] = []
    reason = []

    # Amount bands
    if trade.amount_band:
        if "$100k" in trade.amount_band or "$250k" in trade.amount_band:
            score += 0.35
            tags.append("size_large")
        elif "$50k" in trade.amount_band:
            score += 0.25
            tags.append("size_med")
        else:
            score += 0.10
            tags.append("size_small")

    # Recency
    days = (date.today() - trade.txn_date).days
    if days <= 30:
        score += 0.25
        tags.append("recent")
    elif days <= 90:
        score += 0.15
        tags.append("recent90")

    # Options
    if (trade.security_type or "").lower() == "option":
        score += 0.15
        tags.append("options")

    # Committee/political influence (simple proxy)
    if member and member.party in ("D", "R"):
        score += 0.05
        tags.append("influence")

    score = min(score, 1.0)
    reason.append(f"size/recency/options/influence -> {score:.2f}")

    # Return as 0–5 scale (to match later aggregation)
    return score * 5.0, "; ".join(reason), tags

def score_all_new_trades() -> int:
    """Score all trades and store Signal rows."""
    n = 0
    with get_session() as s:
        trades = s.exec(select(Trade)).all()
        for t in trades:
            sig = Signal(signal_id=f"S-{t.trade_id}", trade_id=t.trade_id, score=0.0)
            m = None
            if t.filing_id:
                f = s.get(Filing, t.filing_id)
                if f and f.filer_member_id:
                    m = s.get(Member, f.filer_member_id)

            sc, reason, tags = compute_trade_signal(t, m)
            sig.score = sc
            sig.reason = reason
            sig.tags = ",".join(tags)

            old = s.get(Signal, sig.signal_id)
            if old:
                s.delete(old)
                s.commit()
            s.add(sig)
            n += 1
        s.commit()
    return n

def compute_follow_scores() -> int:
    """Compute 'Follow Likelihood %' for each member and save snapshots."""
    with get_session() as s:
        members = s.exec(select(Member)).all()
        cnt = 0
        for m in members:
            q = s.exec(
                select(Trade).join(Filing, Filing.filing_id == Trade.filing_id)
                .where(Filing.filer_member_id == m.member_id)
            )
            trades = q.all()
            if not trades:
                m.follow_score = 0.0
                m.follow_score_updated_at = datetime.utcnow()
                cnt += 1
                continue

            total, n = 0.0, 0
            for t in trades:
                sig = s.get(Signal, f"S-{t.trade_id}")
                if sig:
                    total += sig.score
                    n += 1

            base = (total / max(1, n)) / 5.0  # normalize 0–1
            recent = sum(1 for t in trades if (date.today() - t.txn_date).days <= 90)
            rec_boost = min(0.2, 0.05 * (recent // 3))

            m.follow_score = round(min(1.0, base + rec_boost) * 100.0, 1)
            m.follow_score_updated_at = datetime.utcnow()

            # Snapshot (idempotent per day)
            from datetime import date as _date
            snap = MemberSnapshot(
                member_id=m.member_id,
                as_of_date=_date.today(),
                follow_score=m.follow_score,
                metrics_json=None,
            )
            old = s.get(MemberSnapshot, (m.member_id, _date.today()))
            if old:
                s.delete(old)
            s.add(snap)
            cnt += 1

        s.commit()
    return cnt
