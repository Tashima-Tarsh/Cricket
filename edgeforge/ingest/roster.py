"""
EdgeForge – Clean roster resolution.
ZERO hard-coded players. Returns only verified data or explicit failure.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
from datetime import datetime

from edgeforge.models.schemas import Player, Fixture, DataProvenance, Role


class RosterNotFoundError(Exception):
    """Raised when no verified player pool exists for the fixture."""
    pass


class RosterResolver:
    """
    Resolves the player pool for a fixture.
    Sources (in order):
      1. Admin-confirmed fixture (highest trust)
      2. Live provider confirmed XI
      3. Historical Cricsheet / DuckDB last known squad (lower confidence)
    Never invents players.
    """

    def __init__(self, fixture_store, player_store, provider_hub=None):
        self.fixture_store = fixture_store
        self.player_store = player_store
        self.provider_hub = provider_hub

    def get_roster(self, fixture_id: str) -> Tuple[Fixture, List[Player]]:
        """
        Returns (fixture_meta, list_of_players).
        Raises RosterNotFoundError if no verified data exists.
        """
        fixture = self.fixture_store.get(fixture_id)
        if fixture is None:
            raise RosterNotFoundError(
                f"Fixture '{fixture_id}' not found in store. "
                "EdgeForge never fabricates fixtures."
            )

        players = self.player_store.get_players_for_fixture(fixture_id)

        if not players:
            if self.provider_hub is not None:
                try:
                    live_players = self.provider_hub.fetch_confirmed_xi(fixture_id)
                    if live_players:
                        return fixture, live_players
                except Exception:
                    pass

            raise RosterNotFoundError(
                f"No verified player roster for fixture '{fixture_id}'. "
                "Refusing to return synthetic or default players."
            )

        teams = {p.team for p in players}
        if len(teams) < 2:
            raise RosterNotFoundError(
                f"Roster for '{fixture_id}' contains players from only {teams}. "
                "Incomplete data – refusing to proceed."
            )

        return fixture, players

    def get_confirmed_xi_only(self, fixture_id: str) -> List[Player]:
        """Return only players marked is_confirmed_xi=True."""
        _, players = self.get_roster(fixture_id)
        return [p for p in players if p.is_confirmed_xi]
