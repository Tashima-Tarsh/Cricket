"""Fixture resolver without shipped or implicit fixture IDs.

An archived scorecard is not a confirmed playing XI. Only fixtures
explicitly ingested through the validated store are usable for optimization.
"""
from pathlib import Path
from typing import Any

from .roster_safety import validate_roster

# Backward-compatibility names for imports; no preloaded production catalog.
SERIES_FIXTURES: dict[str, dict[str, Any]] = {}
MATCH_FILE_5TH = Path(__file__).parent / "data" / "ind_wi_match.json"


class UnknownMatchError(KeyError):
    """Requested match has not been connected with a validated playing XI."""


def get_match_data(match_id: str | None = None) -> dict[str, Any]:
    if not match_id or not match_id.strip():
        raise UnknownMatchError("An explicit connected match_id is required")
    from .universal_engine import get_universal_engine
    engine = get_universal_engine()
    match_id = match_id.removeprefix("display_")
    if match_id not in engine._matches:
        raise UnknownMatchError(f"Unknown or disconnected match: {match_id}")
    match_meta = engine._matches[match_id]
    players = engine._profile_match_players(match_meta)
    validate_roster(players)
    return {"match_info": match_meta, "players": players}
