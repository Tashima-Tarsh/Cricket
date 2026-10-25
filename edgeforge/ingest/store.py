"""
Minimal in-memory + SQLite-ready stores.
Replace with real DuckDB / Postgres later. No hard-coded match data.
"""
from __future__ import annotations
from typing import Dict, List, Optional
from datetime import datetime

from edgeforge.models.schemas import Fixture, Player, DataProvenance


class InMemoryFixtureStore:
    def __init__(self):
        self._fixtures: Dict[str, Fixture] = {}

    def put(self, fixture: Fixture) -> None:
        self._fixtures[fixture.id] = fixture

    def get(self, fixture_id: str) -> Optional[Fixture]:
        return self._fixtures.get(fixture_id)

    def list_ids(self) -> List[str]:
        return list(self._fixtures.keys())


class InMemoryPlayerStore:
    def __init__(self):
        self._players: Dict[str, List[Player]] = {}  # fixture_id -> players

    def put_players(self, fixture_id: str, players: List[Player]) -> None:
        self._players[fixture_id] = players

    def get_players_for_fixture(self, fixture_id: str) -> List[Player]:
        return self._players.get(fixture_id, [])


def make_unavailable_provenance() -> DataProvenance:
    return DataProvenance(
        source="unavailable",
        confidence=0.0,
        sample_size=0,
        last_updated=datetime.utcnow(),
        notes="No verified data loaded",
    )
