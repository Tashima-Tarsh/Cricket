"""Test constrained selections and no-lookahead WBBL partial-point projections."""
from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import os

import duckdb

from gl_engine.wbbl_fantasy import historical_proxy, recommend, _solve_one
from gl_engine.free_intake import BrowserPoolSnapshot, XIObservation, TossObservation, save_snapshot


def create_db(path):
    with duckdb.connect(str(path)) as db:
        db.execute("""CREATE TABLE matches (
            match_id VARCHAR, match_date DATE, team1 VARCHAR, team2 VARCHAR)""")
        db.execute("""CREATE TABLE deliveries (
            match_id VARCHAR, batter VARCHAR, bowler VARCHAR, runs_batter INT,
            runs_total INT, is_wicket BOOLEAN, wicket_type VARCHAR)""")
        for year in (2021, 2022, 2023, 2024, 2025):
            mid = f"match-{year}"
            db.execute("INSERT INTO matches VALUES (?, ?, 'Sydney Sixers', 'Sydney Thunder')",
                       [mid, f"{year}-11-01"])
            for i in range(22):
                player = f"Player {i}"
                db.execute("INSERT INTO deliveries VALUES (?, ?, ?, ?, ?, false, '')",
                           [mid, player, f"Player {(i + 1) % 22}", i % 6, i % 6])


def players():
    return [
        {"player_id": str(i), "name": f"Player {i}",
         "team": "Sydney Sixers" if i < 11 else "Sydney Thunder",
         "role": ("WK" if i % 11 == 0 else "BAT" if i % 11 < 5
                  else "AR" if i % 11 < 7 else "BOWL"),
         "credits": 8.5, "selected_by_pct": float(i + 1)}
        for i in range(22)
    ]


def test_no_date_leakage_and_wbbl_only():
    with TemporaryDirectory() as tmp:
        db = Path(tmp) / "historical.duckdb"
        create_db(db)
        prior = historical_proxy(["Player 1"], date(2024, 1, 1), db)
        assert prior["player 1"]["matches"] == 3
        assert len(prior["player 1"]["last_five"]) == 3
        assert not historical_proxy(["Unknown"], date(2027, 1, 1), db)


def test_legal_xi_captain_and_vice():
    pool = players()
    result = _solve_one(pool, [30.0 + i for i in range(22)], [], 8)
    assert result is not None
    xi = result["players"]
    assert len(xi) == 11
    assert result["credits_used"] <= 100
    assert result["captain"]["player_id"] != result["vice_captain"]["player_id"]
    assert len({p["player_id"] for p in xi}) == 11
    for team in ("Sydney Sixers", "Sydney Thunder"):
        assert sum(p["team"] == team for p in xi) <= 7


def test_source_agreement_gives_provisional_result_not_official():
    with TemporaryDirectory() as tmp, patch.dict(os.environ, {
        "CRICKET_FREE_DATA_DB": tmp + "/intake.sqlite3"}):
        db = Path(tmp) / "historical.duckdb"
        create_db(db)
        ts = datetime.now(timezone.utc)
        raw = players()
        save_snapshot("browser", BrowserPoolSnapshot(
            match_id="wbbl-123", page_url="https://www.dream11.com/cricket/match/wbbl-123",
            observed_at_utc=ts, players=raw))
        base = dict(match_id="wbbl-123", observed_at_utc=ts,
                    team_a="Sydney Sixers", team_b="Sydney Thunder",
                    players_a=[p["name"] for p in raw[:11]],
                    players_b=[p["name"] for p in raw[11:]],
                    announcement_type="ANNOUNCED_PLAYING_XI")
        save_snapshot("xi", XIObservation(**base, source_url="https://www.cricket.com.au/matches/a"))
        save_snapshot("xi", XIObservation(**base, source_url="https://www.espncricinfo.com/matches/a"))
        save_snapshot("toss", TossObservation(
            match_id="wbbl-123", observed_at_utc=ts,
            source_url="https://www.espncricinfo.com/matches/a",
            source_type="ESPN_REFERENCE", toss_winner="Sydney Sixers", toss_decision="bowl"))
        result = recommend("wbbl-123", date(2026, 11, 13), 2, 8, db)
        assert result["status"] == "PROVISIONAL_RECOMMENDATIONS", result
        assert result["official_lineup_verified"] is False
        assert len(result["lineups"]) >= 1
        assert len(result["lineups"][0]["players"]) == 11
        if len(result["lineups"]) > 1:
            a = {p["player_id"] for p in result["lineups"][0]["players"]}
            b = {p["player_id"] for p in result["lineups"][1]["players"]}
            assert len(a & b) <= 8


def test_incomplete_toss_blocks():
    with TemporaryDirectory() as tmp, patch.dict(os.environ, {
        "CRICKET_FREE_DATA_DB": tmp + "/none.sqlite3"}):
        r = recommend("no-source", date(2026, 11, 13))
        assert r["status"] == "BLOCKED" and r["reason"] == "TOSS_NOT_OBSERVED"
