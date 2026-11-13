"""Immutable, idempotent local research reports. Never imply official XI verified."""
from __future__ import annotations

import hashlib
import json
from contextlib import closing
from datetime import datetime, timezone
from .free_intake import _connect


def _table(db):
    db.execute("""CREATE TABLE IF NOT EXISTS free_recommendations (
        match_id TEXT NOT NULL,
        digest TEXT NOT NULL,
        status TEXT NOT NULL,
        generated_at_utc TEXT NOT NULL,
        payload TEXT NOT NULL,
        PRIMARY KEY(match_id,digest)
    )""")
    db.execute("""CREATE INDEX IF NOT EXISTS idx_free_reports
          ON free_recommendations(match_id,generated_at_utc DESC)""")


def save_report(match_id: str, report: dict) -> dict:
    """Persist blocked and provisional research status; no timestamp-based duplicate."""
    if report.get("match_id") != match_id:
        raise ValueError("Report and path match identifiers differ")
    report_data = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    digest = hashlib.sha256(report_data.encode("utf-8")).hexdigest()
    with closing(_connect()) as db, db:
        _table(db)
        db.execute("""INSERT INTO free_recommendations
          (match_id,digest,status,generated_at_utc,payload)
          VALUES(?,?,?,?,?)
          ON CONFLICT(match_id,digest) DO NOTHING""",
          (match_id, digest, report.get("status","BLOCKED"),
           datetime.now(timezone.utc).isoformat(), report_data))
    return {"status":"SAVED_IDEMPOTENT","match_id":match_id,"report_digest":digest}


def latest_report(match_id: str) -> dict:
    if not match_id or len(match_id) > 128:
        raise ValueError("Valid match identifier required")
    with closing(_connect()) as db:
        _table(db)
        row = db.execute("""SELECT payload,digest,generated_at_utc
            FROM free_recommendations WHERE match_id=?
            ORDER BY generated_at_utc DESC LIMIT 1""", (match_id,)).fetchone()
    if not row:
        return {"status":"NO_REPORT","match_id":match_id,"report":None}
    return {"status":"AVAILABLE","match_id":match_id,"report":json.loads(row[0]),
            "digest":row[1], "generated_at_utc":row[2]}
