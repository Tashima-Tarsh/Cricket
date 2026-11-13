"""Free-only, evidence-preserving WBBL intake for n8n and an authorized browser.

This is a *research* staging area, not an official playing-XI verifier.
No source claims, fantasy credits, or ownership are fabricated.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from contextlib import closing
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_observed_at(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("Observation timestamp must contain a timezone")
    now = _utc_now()
    if value > now + timedelta(minutes=5):
        raise ValueError("Observation timestamp cannot be in the future")
    if value < now - timedelta(days=2):
        raise ValueError("Observation is too old for a post-toss feed")
    return value


def _url_host(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("An HTTPS source URL without embedded credentials is required")
    return parsed.hostname.lower().removeprefix("www.")


class BrowserPlayer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    player_id: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=2, max_length=150)
    team: str = Field(min_length=2, max_length=120)
    role: Literal["WK", "BAT", "AR", "BOWL"]
    credits: float = Field(gt=0, le=20)
    selected_by_pct: float | None = Field(default=None, ge=0, le=100)

    @field_validator("player_id", "name", "team")
    @classmethod
    def non_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Player fields must not be blank")
        return v.strip()


class BrowserPoolSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    match_id: str = Field(min_length=1, max_length=128)
    page_url: str = Field(max_length=2048)
    observed_at_utc: datetime
    players: list[BrowserPlayer] = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def check_source_and_duplicates(self):
        host = _url_host(self.page_url)
        if host not in {"dream11.com", "www.dream11.com"}:
            raise ValueError("Only visible Dream11 pages can supply browser player data")
        _validate_observed_at(self.observed_at_utc)
        ids = [(p.team.casefold(), p.player_id.casefold()) for p in self.players]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate player IDs in browser snapshot")
        return self


class TossObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    match_id: str = Field(min_length=1, max_length=128)
    source_url: str = Field(max_length=2048)
    source_type: Literal["ESPN_REFERENCE", "AUTHORIZED_BROWSER", "OTHER_PERMITTED_PUBLIC_SOURCE"]
    observed_at_utc: datetime
    toss_winner: str = Field(min_length=2, max_length=120)
    toss_decision: Literal["bat", "bowl"]
    pitch_report_text: str | None = Field(default=None, max_length=3000)

    @model_validator(mode="after")
    def check_evidence(self):
        _url_host(self.source_url)
        _validate_observed_at(self.observed_at_utc)
        if not self.toss_winner.strip():
            raise ValueError("Toss winner is required")
        return self


class XIObservation(BaseModel):
    """A source-reported announced XI; never automatically an official XI."""
    model_config = ConfigDict(extra="forbid")
    match_id: str = Field(min_length=1, max_length=128)
    source_url: str = Field(max_length=2048)
    observed_at_utc: datetime
    team_a: str = Field(min_length=2, max_length=120)
    team_b: str = Field(min_length=2, max_length=120)
    players_a: list[str] = Field(min_length=11, max_length=11)
    players_b: list[str] = Field(min_length=11, max_length=11)
    announcement_type: Literal["ANNOUNCED_PLAYING_XI"]

    @model_validator(mode="after")
    def check_xi(self):
        _url_host(self.source_url)
        _validate_observed_at(self.observed_at_utc)
        if not self.team_a.strip() or not self.team_b.strip():
            raise ValueError("Nonblank team names required")
        if self.team_a.strip().casefold() == self.team_b.strip().casefold():
            raise ValueError("Two distinct teams required")
        names = [n.strip().casefold() for n in self.players_a + self.players_b]
        if any(not n or n == "unknown" for n in names) or len(set(names)) != 22:
            raise ValueError("Exactly 22 distinct, nonblank player names required")
        return self


def _db_path() -> Path:
    return Path(os.getenv("CRICKET_FREE_DATA_DB", "var/free_match_intake.sqlite3"))


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(path), timeout=10)
    db.execute("PRAGMA busy_timeout = 10000")
    db.execute("""CREATE TABLE IF NOT EXISTS free_snapshots (
        kind TEXT NOT NULL,
        match_id TEXT NOT NULL,
        digest TEXT NOT NULL,
        observed_at TEXT NOT NULL,
        source_host TEXT NOT NULL,
        payload TEXT NOT NULL,
        PRIMARY KEY (kind, match_id, digest)
    )""")
    db.execute("""CREATE INDEX IF NOT EXISTS idx_free_snapshots_recent
        ON free_snapshots(kind, match_id, observed_at DESC)""")
    return db


def save_snapshot(kind: Literal["browser", "toss", "xi"],
                  snapshot: BrowserPoolSnapshot | TossObservation | XIObservation) -> dict:
    if kind not in ("browser", "toss", "xi"):
        raise ValueError("Unsupported snapshot kind")
    expected = {"browser": BrowserPoolSnapshot, "toss": TossObservation, "xi": XIObservation}
    if not isinstance(snapshot, expected[kind]):
        raise TypeError("Snapshot does not match kind")
    payload = snapshot.model_dump(mode="json")
    # Different capture times of unchanged facts update the observation, not row count.
    facts = {k: v for k, v in payload.items() if k != "observed_at_utc"}
    packed = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(json.dumps(facts, sort_keys=True).encode("utf-8")).hexdigest()
    host = _url_host(payload.get("page_url") or payload.get("source_url"))
    with closing(_connect()) as db, db:
        db.execute("""INSERT INTO free_snapshots
            (kind, match_id, digest, observed_at, source_host, payload)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(kind, match_id, digest) DO UPDATE SET
            observed_at=excluded.observed_at, payload=excluded.payload""",
            (kind, snapshot.match_id, digest, snapshot.observed_at_utc.isoformat(), host, packed))
    return {"status": "RECORDED_UNVERIFIED", "kind": kind,
            "match_id": snapshot.match_id, "digest": digest}


def _recent(kind: str, match_id: str, minutes: int = 120, limit: int = 120) -> list[dict]:
    if not match_id or len(match_id) > 128:
        raise ValueError("Valid match_id required")
    cutoff = (_utc_now() - timedelta(minutes=minutes)).isoformat()
    with _connect() as db:
        rows = db.execute("""SELECT payload FROM free_snapshots
            WHERE kind=? AND match_id=? AND observed_at>=?
            ORDER BY observed_at DESC LIMIT ?""",
            (kind, match_id, cutoff, limit)).fetchall()
    return [json.loads(row[0]) for row in rows]


def get_match_state(match_id: str) -> dict:
    """Merge recent browser captures while keeping all sporting claims unverified."""
    rows = _recent("browser", match_id)
    players: dict[tuple[str, str], dict] = {}
    for snapshot in rows:
        for player in snapshot["players"]:
            key = (player["team"].casefold(), player["player_id"].casefold())
            if key not in players:
                players[key] = player
    pool = list(players.values())
    teams = {p["team"].casefold() for p in pool}
    # A Dream11 squad can have more than 22 players; this does not mean its XI is confirmed.
    browser_complete_candidate = (
        len(pool) >= 22 and len(teams) == 2
        and all(any(p["role"] == role for p in pool) for role in ("WK", "BAT", "AR", "BOWL"))
    )
    tosses = _recent("toss", match_id)
    xis = _recent("xi", match_id)
    agreement = None
    for a in xis:
        for b in xis:
            if a is b:
                continue
            if _url_host(a["source_url"]) == _url_host(b["source_url"]):
                continue
            a_teams = {a["team_a"].casefold(): set(map(str.casefold, a["players_a"])),
                       a["team_b"].casefold(): set(map(str.casefold, a["players_b"]))}
            b_teams = {b["team_a"].casefold(): set(map(str.casefold, b["players_a"])),
                       b["team_b"].casefold(): set(map(str.casefold, b["players_b"]))}
            if a_teams == b_teams:
                agreement = {"status": "TWO_SOURCES_AGREE_UNATTESTED",
                             "source_urls": [a["source_url"], b["source_url"]],
                             "teams": sorted(a_teams)}
                break
        if agreement:
            break
    return {
        "match_id": match_id,
        "status": "RESEARCH_ONLY",
        "browser_pool": {
            "players": pool,
            "player_count": len(pool),
            "candidate_pool_complete": browser_complete_candidate,
            "observed_at_utc": rows[0]["observed_at_utc"] if rows else None,
            "missing_selection_pct": sum(p.get("selected_by_pct") is None for p in pool),
            "source": "AUTHORIZED_BROWSER_UNVERIFIED" if rows else "UNAVAILABLE",
        },
        "toss": (dict(tosses[0], evidence_status="SOURCE_REPORTED_UNVERIFIED")
                 if tosses else None),
        "xi_evidence": {"source_count": len({_url_host(x["source_url"]) for x in xis}),
                        "agreement": agreement,
                        "official_status": "NOT_INDEPENDENTLY_AUTHENTICATED"},
        "optimization_ready": False,
        "readiness_reason": "A complete browser pool and independently authenticated announced XIs are required; no paid-provider gate was bypassed.",
    }
