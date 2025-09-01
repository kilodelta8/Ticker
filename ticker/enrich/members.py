from __future__ import annotations
import os, csv
from ..db import get_session
from ..models import Member
from ..utils.logging import info

def load_members() -> int:
    """Load/update members from fixture CSV."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "members.csv")
    csv_path = os.path.normpath(csv_path)

    n = 0
    with get_session() as s, open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            member = Member(
                member_id=row["member_id"],
                first=row["first"],
                last=row["last"],
                chamber=row["chamber"],
                state=row["state"],
                district=row.get("district") or None,
                party=row.get("party") or None,
                active=True,
            )
            existing = s.get(Member, member.member_id)
            if existing:
                # Update fields if already present
                for k in ["first", "last", "chamber", "state", "district", "party", "active"]:
                    setattr(existing, k, getattr(member, k))
            else:
                s.add(member)
            n += 1
        s.commit()

    info(f"Loaded/updated {n} members from fixtures")
    return n
