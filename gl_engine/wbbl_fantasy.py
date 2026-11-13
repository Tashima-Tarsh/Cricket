"""Conservative WBBL-only, post-toss research optimizer.

No paid API, no fabricated playing XI, no claimed contest-winning odds.
Uses historical pre-match Cricsheet *partial scoring proxy*, NOT official Dream11
fantasy points or calibrated predictions. Output is provisional source-reported.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import duckdb
from ortools.sat.python import cp_model

from .free_intake import get_match_state
from .wbbl_historical import DB_DEFAULT, TEAMS, _TEAM_FILTER

ROLES = {"WK": (1, 4), "BAT": (3, 6), "AR": (1, 4), "BOWL": (3, 6)}
MAX_CREDITS_TENTHS = 1000
HISTORY_MIN_MATCHES = 3


def canonical_name(raw: str) -> str:
    """Punctuation-insensitive but deliberately not fuzzy: ambiguity must block."""
    return " ".join("".join(c if c.isalnum() else " " for c in raw.casefold()).split())


def historical_proxy(names: list[str], before: date, database: str | Path = DB_DEFAULT) -> dict:
    """Compute pre-date, WBBL-only score proxies, combining batting and bowling.

    Score proxy: batter runs + boundary event bonuses + bowler dismissals
    and recorded all-zero deliveries. Excludes fielding, SR/economy,
    actual Dream11 rule versions and batting/bowling replacement eligibility.
    """
    path = Path(database)
    if not path.is_file():
        return {}
    keys = sorted({canonical_name(n) for n in names})
    if not keys:
        return {}
    sql = f"""
      WITH bats AS (
        SELECT lower(trim(d.batter)) AS player, d.match_id, CAST(m.match_date AS DATE) AS match_date,
               SUM(COALESCE(d.runs_batter,0)
                   + CASE WHEN d.runs_batter=4 THEN 1 ELSE 0 END
                   + CASE WHEN d.runs_batter=6 THEN 2 ELSE 0 END) AS points
        FROM deliveries d JOIN matches m ON m.match_id=d.match_id
        WHERE {_TEAM_FILTER}
          AND lower(trim(d.batter)) IN (SELECT unnest(?::VARCHAR[]))
          AND CAST(m.match_date AS DATE) < ?::DATE
        GROUP BY 1,2,3
      ),
      bowls AS (
        SELECT lower(trim(d.bowler)) AS player, d.match_id, CAST(m.match_date AS DATE) AS match_date,
               SUM(CASE WHEN d.is_wicket AND
                        lower(COALESCE(d.wicket_type,'')) NOT IN
                            ('run out', 'retired hurt', 'obstructing the field')
                        THEN 30 ELSE 0 END
                   + CASE WHEN d.runs_total=0 THEN 1 ELSE 0 END) AS points
        FROM deliveries d JOIN matches m ON m.match_id=d.match_id
        WHERE {_TEAM_FILTER}
          AND lower(trim(d.bowler)) IN (SELECT unnest(?::VARCHAR[]))
          AND CAST(m.match_date AS DATE) < ?::DATE
        GROUP BY 1,2,3
      )
      SELECT player, match_id, match_date, SUM(points) AS proxy_points
      FROM (SELECT * FROM bats UNION ALL SELECT * FROM bowls)
      GROUP BY 1,2,3 ORDER BY player, match_date DESC, match_id DESC
    """
    args = [list(TEAMS), list(TEAMS), keys, str(before),
            list(TEAMS), list(TEAMS), keys, str(before)]
    with duckdb.connect(str(path), read_only=True) as db:
        rows = db.execute(sql, args).fetchall()
    observed = defaultdict(list)
    for name, _match_id, _day, score in rows:
        observed[canonical_name(name)].append(float(score))
    result = {}
    for name, scores in observed.items():
        if len(scores) < HISTORY_MIN_MATCHES:
            continue
        recent = scores[:5]
        longer = scores[:12]
        estimate = 0.65 * sum(recent) / len(recent) + 0.35 * sum(longer) / len(longer)
        result[name] = {"estimated_partial_points": round(estimate, 3),
                        "matches": len(scores), "last_five": [round(x, 2) for x in recent],
                        "method": "RECENCY_BLENDED_WBBL_PARTIAL_SCORE_PROXY"}
    return result


def _valid_evidence(state: dict) -> tuple[bool, str]:
    if not state["toss"]:
        return False, "TOSS_NOT_OBSERVED"
    if not state["xi_evidence"]["agreement"]:
        return False, "TWO_AGREEING_XI_REPORTS_NOT_AVAILABLE"
    if not state["browser_pool"]["candidate_pool_complete"]:
        return False, "BROWSER_PLAYER_POOL_INCOMPLETE"
    return True, "SOURCE_REPORTED_ONLY_NOT_OFFICIALLY_AUTHENTICATED"


def _solve_one(players: list[dict], scores: list[float], prior: list[list[int]],
               max_overlap: int, *, time_limit_sec: float = 5.0) -> dict | None:
    model = cp_model.CpModel()
    count = len(players)
    chosen = [model.new_bool_var(f"x{i}") for i in range(count)]
    cap = [model.new_bool_var(f"c{i}") for i in range(count)]
    vice = [model.new_bool_var(f"v{i}") for i in range(count)]
    model.add(sum(chosen) == 11)
    model.add(sum(cap) == 1)
    model.add(sum(vice) == 1)
    for i in range(count):
        model.add(cap[i] <= chosen[i])
        model.add(vice[i] <= chosen[i])
        model.add(cap[i] + vice[i] <= 1)
    model.add(sum(int(round(p["credits"] * 10)) * chosen[i]
                  for i, p in enumerate(players)) <= MAX_CREDITS_TENTHS)
    for role, (lo, hi) in ROLES.items():
        subset = [chosen[i] for i, p in enumerate(players) if p["role"] == role]
        model.add(sum(subset) >= lo)
        model.add(sum(subset) <= hi)
    for team in {p["team"] for p in players}:
        model.add(sum(chosen[i] for i, p in enumerate(players)
                      if p["team"] == team) <= 7)
    for previously_selected in prior:
        model.add(sum(chosen[i] for i in previously_selected) <= max_overlap)
    # Highest uncalibrated expected partial points. Captain 2x, vice 1.5x.
    # Deterministic slight tie-break by stable pool order.
    scaled = [int(round(max(0., score) * 100)) for score in scores]
    model.maximize(sum(scaled[i] * chosen[i] + scaled[i] * cap[i]
                       + scaled[i] // 2 * vice[i] for i in range(count)))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_sec
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 11
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    indices = [i for i in range(count) if solver.value(chosen[i])]
    c = next(i for i in range(count) if solver.value(cap[i]))
    v = next(i for i in range(count) if solver.value(vice[i]))
    credit = round(sum(players[i]["credits"] for i in indices), 1)
    points = sum(scores[i] for i in indices) + scores[c] + scores[v] / 2
    return {"indices": indices, "players": [players[i] for i in indices],
            "captain": players[c], "vice_captain": players[v],
            "credits_used": credit, "credits_left": round(100 - credit, 1),
            "expected_partial_proxy": round(points, 2),
            "solver_status": "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"}


def recommend(match_id: str, before: date, teams: int = 3,
              max_overlap: int = 8, database: str | Path = DB_DEFAULT) -> dict:
    """Return an explicitly provisional report or a precise blocking reason."""
    if teams < 1 or teams > 5 or max_overlap < 0 or max_overlap > 10:
        raise ValueError("teams must be 1..5 and max_overlap 0..10")
    state = get_match_state(match_id)
    result = {"match_id": match_id, "before": before.isoformat(),
              "status": "BLOCKED", "official_lineup_verified": False,
              "contest_win_probability": None, "lineups": [],
              "prediction_type": "UNCALIBRATED_WBBL_PARTIAL_PROXY",
              "source": "CRICSHEET_PRE_DATE_AND_BROWSER_SOURCE_REPORTED_XI"}
    valid, reason = _valid_evidence(state)
    if not valid:
        return {**result, "reason": reason}
    # Never promote self-declared URL content to official provider verification.
    agreement = state["xi_evidence"]["agreement"]
    reports = state["xi_evidence"]["reports"] if "reports" in state["xi_evidence"] else []
    if not reports:
        return {**result, "reason": "CONFIRMED_SOURCE_PLAYER_NAMES_NOT_AVAILABLE"}
    report = reports[0]
    required = {canonical_name(name): team.casefold().strip()
                for team, names in ((report["team_a"], report["players_a"]),
                                    (report["team_b"], report["players_b"]))
                for name in names}
    pool = state["browser_pool"]["players"]
    by_name = defaultdict(list)
    for p in pool:
        by_name[canonical_name(p["name"])].append(p)
    selected = []
    problems = []
    for name, team in required.items():
        possibilities = [p for p in by_name.get(name, []) if p["team"].casefold().strip() == team]
        if len(possibilities) != 1:
            problems.append({"player": name, "reason": "MISSING_OR_AMBIGUOUS_DREAM11_PLAYER"})
        elif possibilities[0]["selected_by_pct"] is None:
            problems.append({"player": name, "reason": "SELECTION_PERCENTAGE_NOT_OBSERVED"})
        else:
            selected.append(possibilities[0])
    if problems:
        return {**result, "reason": "XI_TO_BROWSER_RECONCILIATION_FAILED",
                "unresolved_players": problems}
    if len(selected) != 22 or len({p["player_id"] for p in selected}) != 22:
        return {**result, "reason": "XI_IDENTITY_COLLISION"}
    # Evidence must be for the same two teams as the source-reported toss.
    if canonical_name(state["toss"]["toss_winner"]) not in {
        canonical_name(report["team_a"]), canonical_name(report["team_b"])
    }:
        return {**result, "reason": "TOSS_TEAM_MISMATCH"}
    projections = historical_proxy([p["name"] for p in selected], before, database)
    no_history = [p["name"] for p in selected
                  if canonical_name(p["name"]) not in projections]
    elig = [p for p in selected if canonical_name(p["name"]) in projections]
    if len(elig) < 11:
        return {**result, "reason": "INSUFFICIENT_WBBL_HISTORICAL_COVERAGE",
                "players_with_history": len(elig), "missing_history": no_history}
    elig = sorted(elig, key=lambda p: (p["team"], p["player_id"]))
    scores = [projections[canonical_name(p["name"])]["estimated_partial_points"]
              for p in elig]
    previous = []
    lineups = []
    for _ in range(teams):
        solved = _solve_one(elig, scores, previous, max_overlap)
        if solved is None:
            break
        previous.append(solved.pop("indices"))
        solved["players"] = [
            {**p, "historical_projection": projections[canonical_name(p["name"])]}
            for p in solved["players"]
        ]
        solved["model_status"] = "RESEARCH_ONLY_UNCALIBRATED"
        lineups.append(solved)
    if not lineups:
        return {**result, "reason": "NO_LEGAL_FANTASY_TEAM",
                "missing_history": no_history}
    return {**result,
            "status": "PROVISIONAL_RECOMMENDATIONS",
            "reason": reason,
            "lineups": lineups,
            "missing_history": no_history,
            "xi_sources": agreement["source_urls"],
            "toss": state["toss"],
            "warning": "Do not treat partial-point estimates as official fantasy points, verified playing XIs, or rank-one probabilities."}
