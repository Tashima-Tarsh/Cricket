"""Reject unusable rosters before projection, battle generation or optimization."""
from fastapi import HTTPException


def validate_roster(players):
    if not players or len(players) < 11:
        raise HTTPException(503, 'Fixture player pool is unavailable or incomplete')
    ids = set()
    teams = set()
    for player in players:
        row = player if isinstance(player, dict) else player.model_dump()
        identity, name, team = row.get('id'), row.get('name'), row.get('team')
        if not identity or identity in ids or not isinstance(name, str) or not name.strip() or not team:
            raise HTTPException(503, 'Fixture player pool has missing or duplicate identities')
        # Role placeholders are not player identities.
        words = name.casefold().split()
        if words[:2] in (['top', 'batter'], ['star', 'opener'], ['strike', 'pacer'], ['key', 'batter'], ['lead', 'spinner']) or words == ['tailender']:
            raise HTTPException(503, 'Fixture player pool contains placeholder identities')
        ids.add(identity)
        teams.add(team)
    if len(teams) != 2:
        raise HTTPException(503, 'Fixture player pool must contain two teams')
    return players


def validate_confirmed_xi(players):
    """Validate an explicitly confirmed 11+11 roster without inferring players."""
    from collections import Counter
    if not isinstance(players, (list, tuple)) or len(players) != 22:
        raise HTTPException(503, 'A confirmed XI requires exactly 22 named players')
    validate_roster(players)
    rows = [p if isinstance(p, dict) else p.model_dump() for p in players]
    teams = Counter(p["team"] for p in rows)
    if sorted(teams.values()) != [11, 11]:
        raise HTTPException(503, 'Confirmed XI must contain exactly 11 players per team')
    if any(p.get("is_confirmed_xi") is not True for p in rows):
        raise HTTPException(503, 'Unconfirmed squad players cannot be treated as a playing XI')
    for p in rows:
        if p.get("role") not in ("WK", "BAT", "AR", "BOWL"):
            raise HTTPException(503, 'Confirmed XI contains missing or invalid fantasy roles')
        credits = p.get("credits")
        if isinstance(credits, bool) or not isinstance(credits, (int, float)) or not 0 < credits <= 20:
            raise HTTPException(503, 'Confirmed XI contains missing or invalid credits')
    return players
