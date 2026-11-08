"""EdgeForge – Live-capable persistent store (SQLite)."""
from __future__ import annotations
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional

from edgeforge.models.schemas import Player, Fixture, DataProvenance, Role, Archetype


def _default_db_path() -> str:
    return os.environ.get("EDGEFORGE_DB", str(Path.cwd() / "edgeforge_live.db"))


class LiveStore:
    def __init__(self, db_path: Optional[str] = None, provider_hub=None):
        self.db_path = db_path or _default_db_path()
        self.provider_hub = provider_hub
        self._init_schema()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS fixtures (
                id TEXT PRIMARY KEY, title TEXT, series TEXT, match_date TEXT,
                venue TEXT, format TEXT, team_a TEXT, team_b TEXT, status TEXT,
                archetype TEXT, par_score INTEGER, toss_winner TEXT, toss_decision TEXT,
                source TEXT, confidence REAL, last_updated TEXT, payload_json TEXT
            );
            CREATE TABLE IF NOT EXISTS fixture_players (
                fixture_id TEXT, player_id TEXT, name TEXT, team TEXT, role TEXT,
                credits REAL, batting_hand TEXT, bowling_style TEXT, is_confirmed_xi INTEGER,
                batting_order INTEGER, expected_overs REAL, projected_ownership REAL,
                ownership_available INTEGER, projected_points REAL, ceiling REAL, floor REAL,
                source TEXT, confidence REAL, last_updated TEXT,
                PRIMARY KEY (fixture_id, player_id)
            );
            CREATE INDEX IF NOT EXISTS idx_fp_fixture ON fixture_players(fixture_id);
            """)

    def put_fixture(self, fixture: Fixture) -> None:
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO fixtures
                (id, title, series, match_date, venue, format, team_a, team_b, status,
                 archetype, par_score, toss_winner, toss_decision, source, confidence,
                 last_updated, payload_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (fixture.id, fixture.title, fixture.series, fixture.match_date.isoformat(),
                 fixture.venue, fixture.format, fixture.team_a, fixture.team_b, fixture.status,
                 fixture.archetype.value if fixture.archetype else None, fixture.par_score,
                 fixture.toss_winner, fixture.toss_decision, fixture.provenance.source,
                 fixture.provenance.confidence, fixture.provenance.last_updated.isoformat(),
                 fixture.model_dump_json()),
            )

    def put_players(self, fixture_id: str, players: List[Player]) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM fixture_players WHERE fixture_id = ?", (fixture_id,))
            for p in players:
                conn.execute(
                    """INSERT INTO fixture_players
                    (fixture_id, player_id, name, team, role, credits, batting_hand,
                     bowling_style, is_confirmed_xi, batting_order, expected_overs,
                     projected_ownership, ownership_available, projected_points,
                     ceiling, floor, source, confidence, last_updated)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (fixture_id, p.id, p.name, p.team, p.role.value, p.credits, p.batting_hand,
                     p.bowling_style, int(p.is_confirmed_xi), p.batting_order, p.expected_overs,
                     p.projected_ownership, int(p.ownership_available), p.projected_points,
                     p.ceiling, p.floor, p.provenance.source, p.provenance.confidence,
                     p.provenance.last_updated.isoformat()),
                )

    def get_fixture(self, fixture_id: str) -> Optional[Fixture]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM fixtures WHERE id = ?", (fixture_id,)).fetchone()
        if not row:
            return None
        prov = DataProvenance(
            source=row["source"] or "admin_fixture",
            confidence=row["confidence"] or 0.0,
            last_updated=datetime.fromisoformat(row["last_updated"]) if row["last_updated"] else datetime.utcnow(),
        )
        arch = None
        if row["archetype"]:
            try:
                arch = Archetype(row["archetype"])
            except ValueError:
                pass
        return Fixture(
            id=row["id"], title=row["title"], series=row["series"],
            match_date=date.fromisoformat(row["match_date"]), venue=row["venue"],
            format=row["format"] or "T20", team_a=row["team_a"], team_b=row["team_b"],
            status=row["status"] or "SCHEDULED", archetype=arch, par_score=row["par_score"],
            toss_winner=row["toss_winner"], toss_decision=row["toss_decision"], provenance=prov,
        )

    def get_players(self, fixture_id: str) -> List[Player]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM fixture_players WHERE fixture_id = ?", (fixture_id,)).fetchall()
        players = []
        for r in rows:
            try:
                role = Role(r["role"])
            except ValueError:
                role = Role.BAT
            prov = DataProvenance(
                source=r["source"] or "admin_fixture",
                confidence=r["confidence"] or 0.0,
                last_updated=datetime.fromisoformat(r["last_updated"]) if r["last_updated"] else datetime.utcnow(),
            )
            players.append(Player(
                id=r["player_id"], name=r["name"], team=r["team"], role=role, credits=r["credits"],
                batting_hand=r["batting_hand"] or "RHB", bowling_style=r["bowling_style"],
                is_confirmed_xi=bool(r["is_confirmed_xi"]), batting_order=r["batting_order"],
                expected_overs=r["expected_overs"] or 0.0, projected_ownership=r["projected_ownership"],
                ownership_available=bool(r["ownership_available"]), projected_points=r["projected_points"],
                ceiling=r["ceiling"], floor=r["floor"], provenance=prov,
            ))
        return players

    def list_fixture_ids(self) -> List[str]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id FROM fixtures ORDER BY last_updated DESC").fetchall()
        return [r["id"] for r in rows]


class LiveFixtureStoreAdapter:
    def __init__(self, live: LiveStore):
        self.live = live
    def get(self, fixture_id: str):
        return self.live.get_fixture(fixture_id)
    def put(self, fixture: Fixture):
        self.live.put_fixture(fixture)
    def list_ids(self):
        return self.live.list_fixture_ids()


class LivePlayerStoreAdapter:
    def __init__(self, live: LiveStore):
        self.live = live
    def get_players_for_fixture(self, fixture_id: str):
        return self.live.get_players(fixture_id)
    def put_players(self, fixture_id: str, players: List[Player]):
        self.live.put_players(fixture_id, players)
