"""Use authorized local Dream11 browser observations; no undocumented API calls.

The returned pool is research-only and does not independently confirm a playing XI.
Missing credit/role/team/selection are never substituted with invented values.
"""
from __future__ import annotations

import pandas as pd

COLUMNS = ["player_id", "name", "team", "role", "credit", "own_pct",
           "overseas", "is_xi", "bat_pos", "bowl_style"]


def pool(match_id: str) -> pd.DataFrame:
    """Load only locally captured, validated browser-visible fantasy data."""
    from gl_engine.free_intake import get_match_state
    state = get_match_state(match_id)
    source = state["browser_pool"]
    # Partial tab captures and unknown ownership cannot feed field simulations.
    if not source["candidate_pool_complete"] or source["missing_selection_pct"]:
        return pd.DataFrame(columns=COLUMNS)
    rows = []
    for p in source["players"]:
        if p.get("selected_by_pct") is None:
            return pd.DataFrame(columns=COLUMNS)
        rows.append({
            "player_id": p["player_id"], "name": p["name"],
            "team": p["team"], "role": p["role"],
            "credit": p["credits"], "own_pct": p["selected_by_pct"],
            "overseas": False,  # Not asserted: legacy field is non-evidentiary.
            "is_xi": False,     # Browser pool is NOT a confirmed playing XI.
            "bat_pos": None, "bowl_style": None,
        })
    return pd.DataFrame(rows, columns=COLUMNS)


def proxy_ownership(proj, temperature=18.0):
    """DEMO-ONLY, simulated ownership; never pass off as selected-by percentages."""
    z = (proj - proj.mean()) / max(proj.std(), 1e-6)
    e = (z * temperature / 10.0).apply(lambda v: 2.718281828459045 ** v)
    return (100.0 * e / e.sum()).round(2)
