"""
Tests for THENITISHKR-SPORTS // Wicket Oracle Integration
Verifies DraftKings value bets, fractional Kelly sizing, player props, and team phase endpoints.
"""

from fastapi.testclient import TestClient
import pytest

from gl_engine.web_app import app
from gl_engine.wicket_oracle import compute_fractional_kelly, convert_prob_to_american_odds, WicketOracleEngine


@pytest.fixture
def client():
    return TestClient(app)


def test_kelly_criterion_math():
    """Verify Kelly Criterion calculation adheres to 25% fractional rule."""
    # Edge = 0.09, Implied = 0.55
    kelly = compute_fractional_kelly(edge=0.09, implied_prob=0.55, fraction=0.25)
    # odds_multiplier = (1 / 0.55) - 1 = 0.81818
    # raw_kelly = (0.09 / 0.81818) * 0.25 * 100 = 2.75% -> rounded to 2.8%
    assert 2.5 <= kelly <= 3.0

    # Negative edge should yield 0% stake
    assert compute_fractional_kelly(edge=-0.05, implied_prob=0.50) == 0.0

    # Extreme edge capped at 10% safety ceiling
    assert compute_fractional_kelly(edge=0.40, implied_prob=0.80) == 10.0


def test_american_odds_conversion():
    """Verify probability to American odds converter."""
    assert convert_prob_to_american_odds(0.55).startswith("-")
    assert convert_prob_to_american_odds(0.40).startswith("+")


def test_value_bets_endpoint(client):
    """Verify GET /api/oracle/value-bets returns properly structured opportunities."""
    res = client.get("/api/oracle/value-bets")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["platform"] == "THENITISHKR-SPORTS"
    assert "bets" in data
    assert isinstance(data["bets"], list)

    for bet in data["bets"]:
        assert "match" in bet
        assert "bet" in bet
        assert "edge" in bet
        assert "kelly_stake" in bet
        assert bet["tier"] in ("Elite Pick", "Strong")
        assert "%" in bet["kelly_stake"]


def test_player_props_endpoint(client):
    """Verify GET /api/oracle/player-props returns calibrated batter/bowler lines."""
    res = client.get("/api/oracle/player-props")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["platform"] == "THENITISHKR-SPORTS"
    assert "props" in data
    assert isinstance(data["props"], list)

    for prop in data["props"]:
        assert "player" in prop
        assert "market" in prop
        assert prop["market"] in ("Runs Scored", "Wickets Taken")
        assert prop["recommendation"] in ("OVER", "UNDER")
        assert prop["confidence"] in ("High", "Medium", "Low")
        assert "rivalry_note" in prop


def test_team_phase_deep_dive_endpoint(client):
    """Verify GET /api/oracle/team-phase/{team} returns 3-phase split and death economy."""
    res = client.get("/api/oracle/team-phase/Chennai%20Super%20Kings")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["platform"] == "THENITISHKR-SPORTS"
    assert "deep_dive" in data
    dd = data["deep_dive"]
    assert dd["team"] == "Chennai Super Kings"
    assert "phases" in dd
    assert len(dd["phases"]) == 3
    assert dd["phases"][0]["phase"] == "Powerplay (1-6)"
    assert dd["phases"][1]["phase"] == "Middle (7-15)"
    assert dd["phases"][2]["phase"] == "Death (16-20)"
    assert "death_overs_economy" in dd
    assert dd["death_overs_economy"] > 0
