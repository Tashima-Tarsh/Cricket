"""Dynamic GL scenario templates — no hardcoded player IDs."""
from typing import List, Dict, Any, Optional, Sequence

def build_default_scenarios(players: Optional[Sequence[Any]] = None) -> List[Dict[str, Any]]:
    """Build scenario templates from the active roster. Never hardcodes player IDs."""
    players = list(players or [])
    teams = list(dict.fromkeys(getattr(p, "team", None) for p in players if getattr(p, "team", None)))
    team_a = teams[0] if teams else "TEAM_A"
    team_b = teams[1] if len(teams) > 1 else team_a

    def _pick(roles_c, roles_vc, order_max=4, prefer_pace=False, team=None):
        pool = [p for p in players if team is None or p.team == team] or players
        if not pool:
            return None, None

        def score(p, roles, pace):
            s = float(getattr(p, "ceiling_score", 0) or getattr(p, "projected_points", 0) or 0)
            if getattr(p, "role", None) in roles:
                s += 25.0
            if (getattr(p, "batting_order_projected", 99) or 99) <= order_max:
                s += 15.0
            if pace:
                style = (getattr(p, "bowling_style", None) or "").lower()
                if any(w in style for w in ("fast", "pace", "medium")):
                    s += 20.0
            own = getattr(p, "projected_ownership", 50.0) or 50.0
            if own < 40.0:
                s += 8.0
            return s

        ranked = sorted(pool, key=lambda p: score(p, roles_c, prefer_pace), reverse=True)
        c = ranked[0] if ranked else None
        rest = [p for p in ranked if c is None or p.id != c.id]
        ranked_vc = sorted(rest, key=lambda p: score(p, roles_vc, prefer_pace), reverse=True)
        vc = ranked_vc[0] if ranked_vc else None
        return (c.id if c else None), (vc.id if vc else None)

    templates = [
        ("EXPRESS_PACE_CARNAGE", "Express Pace & Seam Emphasis", 1.05, 1.05, "High-Ceiling Leverage",
         "Overcast or damp conditions amplify early seam/swing. Prioritise frontline pace and top-order anchors.",
         (["BOWL", "AR"], ["BAT", "WK", "AR"], 3, True, None)),
        ("TEAM_B_COUNTER", f"{team_b} Counter-Punch", 0.85, 1.30, "High Volatility",
         f"Leverage underdog volume from {team_b}: two-way all-rounders and top-order batters who retain overs.",
         (["BAT", "WK", "AR"], ["BOWL", "AR"], 4, False, team_b)),
        ("MIDDLE_ORDER_REBUILD", "Middle-Overs Recovery", 1.15, 0.95, "Elite Floor + Ceiling",
         "Early wickets favour middle-order anchors and bowling all-rounders who bat 4-6.",
         (["BAT", "AR"], ["AR", "BOWL"], 5, False, None)),
        ("DEATH_OVERS_BLITZ", "Death Overs Boundary Emphasis", 0.95, 1.20, "Contrarian Multiplier",
         "Finishers and death bowlers drive the ceiling in high-scoring or slog-phase scripts.",
         (["BAT", "AR"], ["BOWL"], 6, True, None)),
        ("TOP_ORDER_STACK", "Top-Order Concentration", 1.10, 1.10, "High Aggregate Ceiling",
         "Concentrate volume on top-3 batters who face the majority of deliveries.",
         (["BAT", "WK"], ["BAT", "AR"], 3, False, None)),
        ("SPIN_CHOKE", "Spin / Grip Surface", 1.05, 1.05, "Dot-Ball Accumulator",
         "Gripping surfaces elevate spinner and cutter value; fade pure boundary openers.",
         (["BOWL", "AR"], ["BOWL", "AR"], 11, False, None)),
        ("PACE_STRANGLE", "Dual Pace Strangle", 1.08, 1.08, "Wicket Multiplier",
         "Two frontline pacers who keep full quotas remove top orders early under lights.",
         (["BOWL"], ["BOWL", "AR"], 11, True, None)),
        ("ANTI_CHALK_LEVERAGE", "Anti-Chalk Leverage Portfolio", 1.00, 1.10, "Low-Duplication Portfolio",
         "Prefer lower-ownership ceiling plays; leave credits unspent for uniqueness. Not a Rank guarantee.",
         (["BAT", "AR", "BOWL"], ["BOWL", "AR"], 5, False, None)),
    ]

    scenarios = []
    for tag, name, a_bias, b_bias, potential, rationale, pick_args in templates:
        roles_c, roles_vc, order_max, pace, team = pick_args
        pref_c, pref_vc = _pick(roles_c, roles_vc, order_max, pace, team)
        scenarios.append({
            "tag": tag,
            "name": name,
            "team_a_bias": a_bias,
            "team_b_bias": b_bias,
            "ind_bias": a_bias,
            "wi_bias": b_bias,
            "preferred_c": pref_c,
            "preferred_vc": pref_vc,
            "gl_potential": potential,
            "rationale": rationale,
            "data_provenance": "DYNAMIC_FROM_ACTIVE_ROSTER" if players else "TEMPLATE_NO_ROSTER",
            "verification": "Constrained mathematical scenario — not a Rank-1 or calibrated claim.",
        })
    return scenarios
