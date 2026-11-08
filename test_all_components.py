"""Automated Unit and Integration Test Suite verifying all 5 Core Pillars:
1. Cricsheet Historical Match Database
2. CricketData Live Cricket API
3. Predict-11 Fantasy Foundation (Dream11 Rules Engine)
4. XGBoost Player Performance & Ceiling Predictor
5. Google OR-Tools Multi-Lineup CP-SAT Optimizer
"""

import sys
import os
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from gl_engine.cricsheet import CricsheetDatabase
from gl_engine.cricketdata_api import CricketDataClient
from gl_engine.predict11 import Predict11Foundation, Dream11Rules
from gl_engine.xgboost_model import XGBoostFantasyPredictor
from gl_engine.ortools_optimizer import ORToolsCricketOptimizer
from gl_engine.models import Player, VenueConditions, WeatherReport


def test_01_cricsheet_database():
    """Verify Cricsheet match files download/load, parse ball-by-ball, and calculate fantasy points."""
    db = CricsheetDatabase()
    matches = db.list_matches()
    assert len(matches) > 0, "No Cricsheet match files found"

    sample = matches[0]
    parsed = db.parse_match(sample["file_path"])
    assert "players" in parsed
    assert len(parsed["players"]) >= 20

    top_performer = max(parsed["players"], key=lambda p: p["fantasy_points"])
    assert top_performer["fantasy_points"] > 0
    assert "runs" in top_performer
    assert "wickets" in top_performer
    print(f"✔ Cricsheet Test Passed: Parsed {len(parsed['players'])} players, top score {top_performer['fantasy_points']} pts.")


def test_02_cricketdata_live_api():
    """Verify CricketData API client retrieves current matches, match info, squads, and scorecards."""
    client = CricketDataClient()
    matches = client.get_current_matches()
    assert len(matches) > 0, "Current matches list is empty"

    match_id = matches[0]["id"]
    info = client.get_match_info(match_id)
    assert info is not None

    squad = client.get_match_squad(match_id)
    assert "teams" in squad
    assert len(squad["teams"]["IND"]["playing_xi"]) == 11
    assert len(squad["teams"]["WI"]["playing_xi"]) == 11

    scorecard = client.get_match_scorecard(match_id)
    assert "innings" in scorecard
    print(f"✔ CricketData API Test Passed: Retrieved match '{match_id}' with confirmed Playing 11s.")


def test_03_predict11_foundation():
    """Verify Predict-11 Dream11 constraints validator, scoring, and CSV export."""
    app = Predict11Foundation()
    
    # Valid 11 mock players
    mock_players = [
        {"id": f"p{i}", "name": f"Player {i}", "role": role, "credits": 8.5, "team": "IND" if i < 7 else "WI", "projected_points": 45.0}
        for i, role in enumerate(["WK", "WK", "BAT", "BAT", "BAT", "AR", "AR", "BOWL", "BOWL", "BOWL", "BOWL"])
    ]
    
    # Test valid lineup
    res = app.validate_lineup(mock_players, captain_id="p0", vice_captain_id="p1")
    assert res.is_valid, f"Validation failed: {res.errors}"
    assert res.credits_used == 93.5

    # Test illegal lineup (exceed credits)
    mock_illegal = list(mock_players)
    mock_illegal[0] = dict(mock_illegal[0], credits=30.0)
    res_illegal = app.validate_lineup(mock_illegal, captain_id="p0", vice_captain_id="p1")
    assert not res_illegal.is_valid
    assert any("exceeds salary budget" in e for e in res_illegal.errors)

    # Test scoring with C (2x) and VC (1.5x)
    score = app.calculate_lineup_fantasy_score(mock_players, "p0", "p1")
    # Base: 11 * 45 = 495. Extra for C: +45, Extra for VC: +22.5 => 562.5
    assert score == 562.5
    print("✔ Predict-11 Foundation Test Passed: Dream11 rules & multipliers strictly enforced.")


def test_04_xgboost_predictor():
    """Verify XGBoost player model feature extraction, training, and ceiling prediction."""
    predictor = XGBoostFantasyPredictor()
    assert predictor.is_trained, "XGBoost model should be trained"

    player = Player(
        id="test_p",
        name="Test Batter",
        team="IND",
        role="BAT",
        credits=9.0,
        batting_style="RHB",
        batting_order_projected=2,
        expected_overs=0.0
    )
    venue = VenueConditions(name="Test Ground", city="Kolkata", avg_first_innings_score=185)
    weather = WeatherReport()

    pred = predictor.predict_player(player, venue, weather)
    assert "mean_points" in pred
    assert "ceiling_90th" in pred
    assert "floor_10th" in pred
    assert pred["ceiling_90th"] >= pred["mean_points"]
    assert pred["mean_points"] >= pred["floor_10th"]
    print(f"✔ XGBoost Predictor Test Passed: Mean={pred['mean_points']}, Ceiling={pred['ceiling_90th']}, Floor={pred['floor_10th']}.")


def test_05_ortools_optimizer():
    """Verify Google OR-Tools CP-SAT multi-lineup optimizer satisfies all constraints."""
    data_path = Path(__file__).parent / "gl_engine" / "data" / "ind_wi_match.json"
    with open(data_path, "r", encoding="utf-8") as f:
        match_json = json.load(f)

    players = [Player(**p) for p in match_json["players"]]
    opt = ORToolsCricketOptimizer(players)

    num_teams = 5
    max_overlap = 8
    lineups = opt.generate_grand_league_portfolio(
        num_teams=num_teams,
        min_differentials_per_team=2,
        max_overlap_between_teams=max_overlap
    )

    assert len(lineups) == num_teams, f"Expected {num_teams} lineups, got {len(lineups)}"

    app = Predict11Foundation()
    for idx, l in enumerate(lineups):
        # 11 players check
        assert len(l.players) == 11
        # Credits check <= 100
        assert l.total_credits <= 100.0
        # Captain & Vice Captain
        assert l.captain is not None
        assert l.vice_captain is not None
        assert l.captain.id != l.vice_captain.id
        # Differential requirement (at least 2 sub-35% picks)
        assert l.differential_count >= 2

        # Predict-11 validator
        res = app.validate_lineup([p.model_dump() for p in l.players], l.captain.id, l.vice_captain.id)
        assert res.is_valid, f"Lineup {idx+1} failed validation: {res.errors}"

    # Verify overlap constraint between every pair
    for i in range(len(lineups)):
        set_i = set(p.id for p in lineups[i].players)
        for j in range(i + 1, len(lineups)):
            set_j = set(p.id for p in lineups[j].players)
            overlap = len(set_i.intersection(set_j))
            assert overlap <= max_overlap, f"Teams {i+1} and {j+1} overlap ({overlap}) exceeded limit of {max_overlap}!"

    print(f"✔ Google OR-Tools Optimizer Test Passed: Generated {len(lineups)} lineups with strictly enforced overlap <= {max_overlap}.")


def test_06_sportmonks_api():
    """Verify Sportmonks Cricket API client retrieves livescores, lineups, and detailed scorecards."""
    from gl_engine.providers.sportmonks_api import SportmonksCricketClient
    client = SportmonksCricketClient()
    lives = client.get_livescores()
    assert len(lives) > 0, "Sportmonks livescores empty"
    fixture = client.get_fixture_details(lives[0]["id"])
    assert "lineup" in fixture or "status" in fixture
    lineup = client.get_lineup(lives[0]["id"])
    assert len(lineup["playing_xi"]["home"]) > 0
    print("✔ Sportmonks Cricket API Test Passed: Retrieved live fixtures, scorecards, and lineups.")


def test_07_roanuz_match_api():
    """Verify Roanuz Match API client retrieves live intelligence and ball-by-ball micro data."""
    from gl_engine.providers.roanuz_match_api import RoanuzCricketClient
    client = RoanuzCricketClient()
    matches = client.get_matches()
    assert len(matches) > 0, "Roanuz matches empty"
    intel = client.get_match_intelligence(matches[0]["key"])
    assert "toss" in intel
    assert "venue" in intel
    b_by_b = client.get_ball_by_ball(matches[0]["key"])
    assert "recent_balls" in b_by_b
    print("✔ Roanuz Match API Test Passed: Live match intelligence & ball-by-ball telemetry verified.")


def test_08_roanuz_fantasy_api():
    """Verify Roanuz Fantasy API client computes real-time fantasy points and player credits."""
    from gl_engine.providers.roanuz_fantasy_api import RoanuzFantasyClient
    client = RoanuzFantasyClient()
    pts = client.get_fantasy_match_points("ind_wi_t20_2026_m4")
    assert "points" in pts
    assert len(pts["points"]) > 0
    credits = client.get_fantasy_match_credits("ind_wi_t20_2026_m4")
    assert "credits" in credits
    assert len(credits["credits"]) > 0
    print("✔ Roanuz Fantasy API Test Passed: Real-time fantasy scoring & player credits verified.")


def test_09_unified_data_hub():
    """Verify Unified Multi-Provider Cricket Data Hub harmonizes all 5 providers."""
    from gl_engine.providers.data_hub import UnifiedCricketDataHub
    hub = UnifiedCricketDataHub()
    status = hub.get_providers_status()
    assert len(status) >= 5
    assert all(p in status for p in ["cricsheet", "cricketdata", "sportmonks", "roanuz_match", "roanuz_fantasy"])
    unified = hub.fetch_unified_live_match("ind-vs-wi-t20i-2026")
    assert "lineup" in unified
    assert "toss" in unified
    assert "scorecard" in unified
    assert "live_fantasy_points" in unified
    print("✔ Unified Cricket Data Hub Test Passed: Successfully harmonized all 5 providers.")


def test_10_pitch_venue_vision():
    """Verify Hawkeye delivery length simulation, boundary geometry, and pitch degradation."""
    from gl_engine.pitch_venue_vision import PitchVenueVisionEngine
    engine = PitchVenueVisionEngine()
    hawkeye_pace = engine.analyze_hawkeye_lengths("Pace")
    assert "optimal_length" in hawkeye_pace
    assert "Yorker (0-2m)" in hawkeye_pace["length_breakdown"]
    
    boundaries = engine.compute_boundary_risk_zones()
    assert "shortest_boundary" in boundaries
    
    deg = engine.evaluate_pitch_degradation(current_over=14.0, innings=2)
    assert deg["dew_active"] is True
    print("✔ Pitch & Venue Vision Test Passed: Hawkeye lengths, boundary risk, and dew wear verified.")


def test_11_player_battles_and_mcp():
    """Verify Batter vs Bowler H2H matchup engine, DLS calculator, and MCP protocol tool definitions."""
    from gl_engine.player_battles_mcp import PlayerBattlesMCPEngine
    engine = PlayerBattlesMCPEngine()
    
    h2h = engine.query_h2h_battle("Pooran", "Kuldeep")
    assert h2h is not None
    assert h2h.balls_faced >= 1
    
    dls = engine.compute_dls_target(first_innings_runs=190, first_innings_overs=20, second_innings_overs=14, interruption_wickets=1)
    assert dls["dls_revised_target"] > 0
    assert dls["dls_revised_target"] < 190
    
    mcp_defs = engine.get_mcp_tool_definitions()
    assert len(mcp_defs) >= 2
    mcp_call = engine.dispatch_mcp_tool("cricket_h2h_matchup", {"batter": "Samson", "bowler": "Joseph"})
    assert "batter_name" in mcp_call or "status" in mcp_call
    print("✔ Player Battles & MCP Test Passed: H2H battles, DLS targets, and MCP tool protocols verified.")


def test_12_datasets_2026_and_cricoracle():
    """Verify 2026 match schedule, CricOracle live win probability, and player impact ratings."""
    from gl_engine.datasets_2026 import Datasets2026Pipeline, CricOracle2026, CricIQAnalytics
    pipeline = Datasets2026Pipeline()
    fixtures = pipeline.get_season_2026_fixtures()
    assert len(fixtures) >= 3
    
    wpa = CricOracle2026.calculate_win_probability(target_runs=185, current_runs=125, balls_remaining=42, wickets_in_hand=7)
    assert 0.0 <= wpa["chasing_win_prob"] <= 1.0
    
    proj = CricOracle2026.forecast_final_innings_score(current_runs=118, overs_bowled=11.4, wickets_lost=2)
    assert proj["projected"] > 118
    
    pir = CricIQAnalytics.compute_player_impact_rating(runs=58, balls=29, wickets=1, overs=2.0, economy=7.0, catches=1)
    assert pir > 0
    print("✔ 2026 Datasets & CricOracle Test Passed: 2026 fixtures, WPA model, and player impact ratings verified.")


if __name__ == "__main__":
    print("\n--- Running Complete Production Suite: All 12 Engines & Providers ---")
    test_01_cricsheet_database()
    test_02_cricketdata_live_api()
    test_03_predict11_foundation()
    test_04_xgboost_predictor()
    test_05_ortools_optimizer()
    test_06_sportmonks_api()
    test_07_roanuz_match_api()
    test_08_roanuz_fantasy_api()
    test_09_unified_data_hub()
    test_10_pitch_venue_vision()
    test_11_player_battles_and_mcp()
    test_12_datasets_2026_and_cricoracle()
    print("\n🎉 ALL 12 INTEGRATION TESTS PASSED 100%! COMPLETE PRODUCTION READY! 🎉\n")
