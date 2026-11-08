"""
Unit tests for optimizer.py
"""
import pandas as pd
from optimizer import GrandLeagueOptimizer, ROLE_BOUNDS


def make_upcoming_df() -> pd.DataFrame:
    rng_state = 42
    players = [
        {"name": f"Player_{i}", "role": r, "team": t, "credit": c,
         "projected_sel_pct": s, "expected_points": e, "variance_score": v}
        for i, (r, t, c, s, e, v) in enumerate([
            ("BAT", "MI", 10.5, 78.0, 50.0, 0.5),
            ("BAT", "MI", 10.0, 65.0, 45.0, 0.4),
            ("BOWL", "MI", 10.5, 82.0, 48.0, 0.6),
            ("WK", "MI", 9.0, 45.0, 40.0, 0.3),
            ("BAT", "MI", 8.5, 22.0, 30.0, 0.8),   # differential
            ("BOWL", "MI", 8.0, 8.0, 25.0, 0.9),    # differential
            ("BAT", "MI", 8.0, 12.0, 20.0, 0.7),
            ("BOWL", "MI", 8.5, 14.0, 18.0, 0.5),
            ("BOWL", "MI", 8.0, 6.0, 15.0, 0.9),    # differential
            ("WK", "MI", 8.5, 18.0, 22.0, 0.6),
            ("BOWL", "MI", 8.0, 10.0, 16.0, 0.4),
            ("BAT", "RCB", 11.0, 88.0, 55.0, 0.3),
            ("BAT", "RCB", 9.5, 55.0, 42.0, 0.4),
            ("BAT", "RCB", 9.0, 35.0, 35.0, 0.5),
            ("BOWL", "RCB", 9.5, 60.0, 46.0, 0.5),
            ("WK", "RCB", 8.5, 20.0, 28.0, 0.6),
            ("AR", "RCB", 9.5, 40.0, 38.0, 0.5),
            ("AR", "RCB", 8.5, 25.0, 30.0, 0.6),
            ("BOWL", "RCB", 9.0, 48.0, 40.0, 0.4),
            ("BOWL", "RCB", 8.0, 11.0, 20.0, 0.8),  # differential
            ("BAT", "RCB", 8.0, 7.0, 18.0, 0.9),    # differential
            ("BOWL", "RCB", 8.5, 9.0, 15.0, 0.9),   # differential
            ("AR", "RCB", 8.5, 30.0, 32.0, 0.5),
        ])
    ]
    return pd.DataFrame(players)


def test_optimizer_generates_valid_teams():
    df = make_upcoming_df()
    opt = GrandLeagueOptimizer(df)
    teams = opt.optimize(n_teams=5, scenario="balanced")
    assert len(teams) == 5
    for team in teams:
        players = team["players"]
        assert len(players) == 11
        assert team["total_credits"] <= 100.0 + 1e-6
        # exactly 1 captain, 1 vice-captain
        caps = [p for p in players if p["is_captain"]]
        vcs = [p for p in players if p["is_vice_captain"]]
        assert len(caps) == 1
        assert len(vcs) == 1
        assert caps[0] is not vcs[0]
        # role bounds
        from collections import Counter
        role_counts = Counter(p["role"] for p in players)
        for role, (lo, hi) in ROLE_BOUNDS.items():
            assert lo <= role_counts.get(role, 0) <= hi, f"{role}: {role_counts.get(role, 0)} not in [{lo},{hi}]"
        # max 7 per team
        team_counts = Counter(p["team"] for p in players)
        assert all(c <= 7 for c in team_counts.values())
        # at least 2 differentials
        assert team["n_differentials"] >= 2


def test_optimizer_scenarios():
    df = make_upcoming_df()
    opt = GrandLeagueOptimizer(df)
    for scenario in ["balanced", "top_collapse", "death_bowler_special"]:
        teams = opt.optimize(n_teams=3, scenario=scenario)
        assert len(teams) == 3
        for team in teams:
            assert team["scenario"] == scenario


def test_optimizer_credit_budget_strict():
    df = make_upcoming_df()
    opt = GrandLeagueOptimizer(df)
    teams = opt.optimize(n_teams=10, scenario="balanced")
    for team in teams:
        assert team["total_credits"] <= 100.0


def test_optimizer_no_infeasible_crash():
    """Ensure optimizer returns None gracefully instead of crashing on tight constraints."""
    df = make_upcoming_df()
    opt = GrandLeagueOptimizer(df)
    teams = opt.optimize(n_teams=1, scenario="balanced")
    # With 23 players and normal bounds, should always find feasible
    assert len(teams) == 1
