"""
Unit tests for chaos_intelligence.py
"""
from chaos_intelligence import ChaosIntelligence


def make_chaos():
    return ChaosIntelligence()


def test_load_all_factors_returns_all_keys():
    ci = make_chaos()
    match_context = {
        "venue": "MCG", "rain_prob": 35, "humidity": 78, "wind_speed": 18,
        "cloud_cover": 60, "temperature": 22, "dew_factor": "HIGH",
        "is_night_match": True, "umpires": [
            {"strictness_index": 0.75, "lbw_given_rate": 0.6, "drs_overturn_rate": 0.45}
        ],
        "pitch_type": "slow", "pace_friendly": False, "spin_friendly": True,
        "wear_rate": 0.65, "cracks": True, "grass_cover": "medium",
        "players": [{"name": "P1", "role": "BAT"}],
        "travel_distance_km": 2500, "days_since_last_match": 2,
        "timezone_changes": 1, "is_knockout": True, "rivalry_factor": 0.8,
    }
    factors = ci.load_all_factors(match_context)
    expected_keys = {
        "weather", "umpire", "pitch", "player_form", "historical_patterns",
        "venue_quirks", "toss_impact", "crowd_pressure", "travel_fatigue",
        "match_importance",
    }
    assert expected_keys.issubset(set(factors.keys()))


def test_weather_chaos_scoring():
    ci = make_chaos()
    # High rain uncertainty (30-70)
    w = ci._calculate_weather_chaos({"rain_probability": 50, "dew_factor": "LOW", "wind_speed": 5, "humidity": 50})
    assert w == 0.3
    # High dew
    w = ci._calculate_weather_chaos({"rain_probability": 10, "dew_factor": "HIGH", "wind_speed": 5, "humidity": 50})
    assert w == 0.2
    # Capped at 1.0
    w = ci._calculate_weather_chaos({"rain_probability": 50, "dew_factor": "HIGH", "wind_speed": 30, "humidity": 90})
    assert w <= 1.0


def test_umpire_chaos():
    ci = make_chaos()
    # High DRS overturn
    u = ci._calculate_umpire_chaos({"strictness_index": 0.5, "driven_to_drs": 0.5})
    assert u == 0.3
    # Extreme strictness
    u = ci._calculate_umpire_chaos({"strictness_index": 0.9, "driven_to_drs": 0.0})
    assert u == 0.2


def test_pitch_chaos():
    ci = make_chaos()
    p = ci._calculate_pitch_chaos({"cracks": True, "wear_rate": 0.8, "pace_friendly": False, "spin_friendly": False})
    assert p == 0.45  # 0.25 cracks + 0.2 wear


def test_player_fragility():
    ci = make_chaos()
    f = ci._calculate_player_fragility(
        {"edge_rate": 0.18, "caught_behind_rate": 0.35, "lbw_dismissal_rate": 0.3}, "BAT"
    )
    assert f == 0.7  # 0.3 + 0.2 + 0.2
    # Capped at 1.0
    f = ci._calculate_player_fragility(
        {"edge_rate": 0.18, "caught_behind_rate": 0.35, "lbw_dismissal_rate": 0.3}, "BAT"
    )
    assert f <= 1.0


def test_player_fragility_bowler():
    ci = make_chaos()
    f = ci._calculate_player_fragility(
        {"false_shot_percentage": 0.25, "balls_per_wicket": 40}, "BOWL"
    )
    assert f == 0.1


def test_chaos_level_classification():
    ci = make_chaos()
    summary = ci.get_match_chaos_summary({
        "weather": {"chaos_score": 0.1},
        "umpire": {"chaos_score": 0.1},
        "pitch": {"chaos_score": 0.1},
        "historical_patterns": {"chaos_score": 0.1},
        "venue_quirks": {"chaos_score": 0.1},
        "toss_impact": {"chaos_score": 0.1},
        "crowd_pressure": {"chaos_score": 0.1},
        "travel_fatigue": {"chaos_score": 0.1},
        "match_importance": {"chaos_score": 0.1},
    })
    assert summary["chaos_level"] == "LOW"
    assert summary["total_chaos_score"] == 0.1


def test_apply_chaos_to_player_spin_dew_penalty():
    ci = make_chaos()
    player = {
        "name": "Spin_Bowler", "role": "BOWL", "bowling_style": "leg_spin",
        "expected_points": 50.0, "variance_score": 0.5,
    }
    factors = {
        "weather": {"spin_penalty": True, "dls_risk": False},
        "umpire": {"strictness_index": 0.5},
        "pitch": {"second_innings_spin_boost": 1.0},
        "player_form": {player["name"]: {"fragility_score": 0.0, "luck_factor": 0.0}},
        "travel_fatigue": {"chaos_score": 0.0},
        "crowd_pressure": {"chaos_score": 0.0},
    }
    adjusted = ci.apply_chaos_to_player(player, factors)
    assert adjusted["expected_points"] == 35.0  # 50 * 0.70
    assert adjusted["variance_score"] == 0.7  # 0.5 + 0.2
    assert adjusted["chaos_adjusted"] is True


def test_apply_chaos_lucky_batter_regression():
    ci = make_chaos()
    player = {
        "name": "Lucky_Batter", "role": "BAT", "bowling_style": "",
        "expected_points": 50.0, "variance_score": 0.5,
        "edge_rate": 0.18,
    }
    factors = {
        "weather": {"spin_penalty": False, "dls_risk": False},
        "umpire": {"strictness_index": 0.5},
        "pitch": {"second_innings_spin_boost": 1.0},
        "player_form": {
            player["name"]: {"fragility_score": 0.1, "luck_factor": 0.6}
        },
        "travel_fatigue": {"chaos_score": 0.0},
        "crowd_pressure": {"chaos_score": 0.0},
    }
    adjusted = ci.apply_chaos_to_player(player, factors)
    assert adjusted["expected_points"] == 42.5  # 50 * 0.85
    assert adjusted["variance_score"] == 0.7  # 0.5 + 0.2
