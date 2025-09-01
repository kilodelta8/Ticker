from __future__ import annotations
import os, csv
from ..db import get_session
from ..models import Committee, MemberCommittee
from ..utils.logging import info

def load_committees() -> int:
    """Load committees and member-committee links from fixtures."""
    base = os.path.join(os.path.dirname(__file__), "..", "fixtures")
    committees_csv = os.path.normpath(os.path.join(base, "committees.csv"))
    members_committees_csv = os.path.normpath(os.path.join(base, "member_committees.csv"))

    # Committees
    n = 0
    with get_session() as s, open(committees_csv, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            c = Committee(
                committee_id=row["committee_id"],
                name=row["name"],
                chamber=row["chamber"],
            )
            ex = s.get(Committee, c.committee_id)
            if ex:
                ex.name, ex.chamber = c.name, c.chamber
            else:
                s.add(c)
            n += 1
        s.commit()

    # Member ↔ Committee links
    m = 0
    with get_session() as s, open(members_committees_csv, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            mc = MemberCommittee(
                member_id=row["member_id"],
                committee_id=row["committee_id"],
                role=row.get("role") or None,
            )
            ex = s.get(MemberCommittee, (mc.member_id, mc.committee_id))
            if ex:
                ex.role = mc.role
            else:
                s.add(mc)
            m += 1
        s.commit()

    info(f"Loaded/updated {n} committees and {m} member-committee links")
    return n + m
