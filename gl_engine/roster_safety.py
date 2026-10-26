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
