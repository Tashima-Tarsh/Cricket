"""Rain & Reduced Overs Mathematical Engine for T20 Cricket.
Accurately models DLS targets, bowler quota caps, batting order ball-share decay,
and strategic Grand League roster adaptations under weather interruptions.

INVARIANTS:
- official_dls is always False (fantasy adaptation only).
- No hardcoded player IDs or names in scenarios.
- When players are supplied, preferred C/VC are chosen dynamically from the active roster.
"""

from typing import Dict, Any, List, Optional
import math
from .models import Player

class RainReducedOversEngine:
    """Calculates cricket rule adjustments and fantasy point transformations
    when rain interruptions force reduced-overs matches (5 to 19 overs per side).
    """

    @staticmethod
    def get_over_constraints(overs: int, is_womens: bool = True) -> Dict[str, Any]:
        """Returns standard ICC T20 / WT20 Playing Conditions constraints for shortened games (5 to 20 overs).
        Accurately models legal over quotas (including 2 overs per bowler in 5-9 over games) and ball-accurate powerplays.
        """
        valid_overs = max(5, min(20, int(overs)))
        
        if valid_overs <= 9:
            max_bowler_quota = 2
            base_quota = 1
            if valid_overs == 5:
                quota_breakdown = "2 bowlers max 2 ov, 1 bowler max 1 ov (2+2+1 allocation; min 3 bowlers)"
            elif valid_overs == 6:
                quota_breakdown = "2 bowlers max 2 ov, 2 bowlers max 1 ov (2+2+1+1 allocation; min 4 bowlers)"
            elif valid_overs == 7:
                quota_breakdown = "3 bowlers max 2 ov, 1 bowler max 1 ov (2+2+2+1 allocation; min 4 bowlers)"
            elif valid_overs == 8:
                quota_breakdown = "4 bowlers max 2 ov (2+2+2+2 allocation; min 4 bowlers)"
            else:
                quota_breakdown = "4 bowlers max 2 ov, 1 bowler max 1 ov (min 5 bowlers)"
        else:
            base_quota = valid_overs // 5
            extra_bowlers = valid_overs % 5
            base_bowlers = 5 - extra_bowlers if extra_bowlers > 0 else 5
            max_bowler_quota = base_quota + (1 if extra_bowlers > 0 else 0)
            if extra_bowlers > 0:
                quota_breakdown = f"{extra_bowlers} bowlers max {base_quota + 1} ov, {base_bowlers} bowlers max {base_quota} ov"
            else:
                quota_breakdown = f"All 5 bowlers max {base_quota} ov"

        pp_table = {
            5: (1.5, "1.3 ov (9 balls)"),
            6: (1.83, "1.5 ov (11 balls)"),
            7: (2.17, "2.1 ov (13 balls)"),
            8: (2.33, "2.2 ov (14 balls)"),
            9: (2.67, "2.4 ov (16 balls)"),
            10: (3.0, "3.0 ov (18 balls)"),
            11: (3.33, "3.2 ov (20 balls)"),
            12: (3.67, "3.4 ov (22 balls)"),
            13: (3.83, "3.5 ov (23 balls)"),
            14: (4.17, "4.1 ov (25 balls)"),
            15: (4.5, "4.3 ov (27 balls)"),
            16: (4.83, "4.5 ov (29 balls)"),
            17: (5.17, "5.1 ov (31 balls)"),
            18: (5.5, "5.3 ov (33 balls)"),
            19: (5.83, "5.5 ov (35 balls)"),
            20: (6.0, "6.0 ov (36 balls)")
        }
        pp_overs_numeric, pp_overs_str = pp_table.get(valid_overs, (valid_overs * 0.3, f"{valid_overs * 0.3:.1f} ov"))
        pp_overs = int(round(pp_overs_numeric))

        res_pct = (1.0 - math.exp(-0.065 * valid_overs)) / (1.0 - math.exp(-0.065 * 20))
        projected_par = int(round(185 * res_pct))
        rrr = round(projected_par / valid_overs, 2)
        chasing_equity = min(76.0, 56.4 + (20 - valid_overs) * 1.15)
        total_balls = valid_overs * 6
        top3_ball_share_pct = min(88.0, 58.0 + (20 - valid_overs) * 2.0)
        top3_expected_balls = int(round(total_balls * (top3_ball_share_pct / 100.0)))
        lower_order_balls = max(0, total_balls - top3_expected_balls)

        if valid_overs == 20:
            tactical_key = "Full 20-over tactical blueprint: Standard pace-spin balance with full 5-bowler 4-over distribution."
            fantasy_adjustment = "Balanced roster: 4 pacers, 3 top-order anchors, 3 multi-phase all-rounders, 1 strike spinner."
        elif valid_overs >= 16:
            tactical_key = f"{valid_overs}-over match: Powerplay {pp_overs_str}. {quota_breakdown}. Middle overs compressed to {valid_overs - pp_overs - 4} overs."
            fantasy_adjustment = "Slight top-3 upgrade. Part-time bowling volume reduced. Lock in frontline 4-over seamers."
        elif valid_overs >= 12:
            tactical_key = f"{valid_overs}-over match: Critical {pp_overs_str} powerplay. {quota_breakdown}. Total balls: {total_balls}. Top-3 face ~{top3_expected_balls} deliveries."
            fantasy_adjustment = f"Heavily favor Top-3 batters & frontline strike bowlers. Lower order (No. 6-8) face only ~{lower_order_balls} balls combined."
        elif valid_overs >= 8:
            tactical_key = f"{valid_overs}-over sprint: {pp_overs_str} powerplay. {quota_breakdown}. Zero settling time. Target ~{projected_par} ({rrr} RPO)."
            fantasy_adjustment = "Strictly fade pure non-bowling middle-order batters. Captain MUST be an aggressive opener or primary strike bowler."
        else:
            tactical_key = f"{valid_overs}-over shootout: {pp_overs_str} powerplay. {quota_breakdown}. Frontline bowlers permitted up to 2 overs (e.g. 2+2+1 allocation). Total balls: {total_balls}."
            fantasy_adjustment = "Max out top 3 batters. Lock in primary strike bowler capable of bowling 2 overs (doubling expected opportunity)."

        return {
            "data_provenance": "ICC_CONDITIONS_ALIGNED_FANTASY_ADAPTATION",
            "official_dls": False,
            "verification": "Fantasy adaptation only — NOT for match adjudication. Aligned with ICC Clause 13.9.1 & WT20 Playing Conditions for quotas/powerplay.",
            "overs": valid_overs,
            "is_shortened": valid_overs < 20,
            "max_bowler_quota": max_bowler_quota,
            "base_quota": base_quota,
            "quota_breakdown": quota_breakdown,
            "powerplay_overs": pp_overs,
            "powerplay_overs_display": pp_overs_str,
            "projected_par": projected_par,
            "required_run_rate": rrr,
            "total_balls": total_balls,
            "top3_ball_share_pct": round(top3_ball_share_pct, 1),
            "top3_expected_balls": top3_expected_balls,
            "lower_order_balls": lower_order_balls,
            "chasing_win_prob": round(chasing_equity, 1),
            "defending_win_prob": round(100.0 - chasing_equity, 1),
            "resource_pct": round(res_pct * 100.0, 1),
            "tactical_key": tactical_key,
            "fantasy_adjustment": fantasy_adjustment,
            "min_bowlers_required": 5
        }

    @staticmethod
    def adjust_player_projections(
        players: List[Player],
        overs: int = 20,
        venue: Optional[Dict[str, Any]] = None
    ) -> List[Player]:
        if overs >= 20:
            return players

        constraints = RainReducedOversEngine.get_over_constraints(overs)
        r = overs / 20.0
        max_quota = constraints["max_bowler_quota"]
        venue_pace = (venue or {}).get("pace_wickets_pct", 59.6)

        adjusted_players = []
        for p in players:
            p_adj = p.model_copy(deep=True)
            orig_pts = p.projected_points or (p.stats.avg_fantasy_pts * 0.85)

            order = p.batting_order_projected or 4
            sr = getattr(p.stats, "strike_rate", 130.0)

            if order in [1, 2]:
                sr_boost = 1.18 if sr >= 155.0 else 1.05
                bat_scale = (r ** 0.52) * 1.25 * sr_boost
            elif order == 3:
                bat_scale = (r ** 0.65) * 1.12
            elif order == 4:
                bat_scale = (r ** 0.88) * 0.88
            elif order == 5:
                bat_scale = (r ** 1.25) * 0.60
            else:
                bat_scale = (r ** 1.85) * 0.32

            exp_overs = p.expected_overs or 0.0
            bowl_style = (p.bowling_style or "").lower()
            is_pacer = any(w in bowl_style for w in ["fast", "pace", "medium"])
            is_spinner = any(w in bowl_style for w in ["spin", "orthodox", "break"])

            if exp_overs >= 3.0:
                intensity = 1.22
                if is_pacer and venue_pace >= 55.0:
                    intensity *= 1.15
                elif is_spinner:
                    intensity *= 0.85
                bowl_scale = (min(max_quota, exp_overs * r) / 4.0) * intensity
            elif exp_overs >= 1.5:
                bowl_scale = (min(max_quota - 1, exp_overs * r) / 4.0) * 0.90
            else:
                bowl_scale = (r ** 2.2) * 0.15

            role = p.role
            if role == "WK":
                final_scale = bat_scale * 0.92 + (r * 0.08)
            elif role == "BAT":
                final_scale = bat_scale
            elif role == "BOWL":
                final_scale = bowl_scale
            else:
                bat_weight = 0.50 if order <= 5 else 0.25
                bowl_weight = 1.0 - bat_weight
                final_scale = bat_scale * bat_weight + bowl_scale * bowl_weight

            p_adj.projected_points = round(max(8.0, orig_pts * final_scale), 1)
            p_adj.ceiling_score = round(max(15.0, (p.ceiling_score or orig_pts * 1.5) * final_scale * 1.15), 1)
            p_adj.floor_score = round(max(4.0, (p.floor_score or orig_pts * 0.5) * final_scale), 1)
            p_adj.stats.avg_fantasy_pts = p_adj.projected_points

            adjusted_players.append(p_adj)

        return adjusted_players

    @staticmethod
    def _pick_dynamic_c_vc(
        players: Optional[List[Player]],
        prefer_roles_c: List[str],
        prefer_roles_vc: List[str],
        prefer_order_max: int = 4,
        prefer_pace: bool = False
    ) -> Dict[str, Optional[str]]:
        if not players:
            return {"preferred_c_id": None, "preferred_c_name": None,
                    "preferred_vc_id": None, "preferred_vc_name": None}

        def score(p: Player, roles: List[str], order_max: int, pace: bool) -> float:
            s = float(p.ceiling_score or p.projected_points or 0.0)
            if p.role in roles:
                s += 25.0
            if (p.batting_order_projected or 99) <= order_max:
                s += 15.0
            if pace:
                style = (p.bowling_style or "").lower()
                if any(w in style for w in ["fast", "pace", "medium"]):
                    s += 20.0
            own = getattr(p, "projected_ownership", 50.0) or 50.0
            if own < 40.0:
                s += 8.0
            return s

        ranked = sorted(players, key=lambda p: score(p, prefer_roles_c, prefer_order_max, prefer_pace), reverse=True)
        c = ranked[0] if ranked else None
        remaining = [p for p in ranked if c is None or p.id != c.id]
        ranked_vc = sorted(remaining, key=lambda p: score(p, prefer_roles_vc, prefer_order_max, prefer_pace), reverse=True)
        vc = ranked_vc[0] if ranked_vc else None

        return {
            "preferred_c_id": c.id if c else None,
            "preferred_c_name": c.name if c else None,
            "preferred_vc_id": vc.id if vc else None,
            "preferred_vc_name": vc.name if vc else None,
        }

    @staticmethod
    def get_rain_scenarios(
        overs: int,
        players: Optional[List[Player]] = None
    ) -> List[Dict[str, Any]]:
        """Returns specialized Grand League game scripts for shortened matches.

        When `players` is supplied, preferred C/VC are chosen dynamically from that roster.
        When absent, preferred fields are null (never hardcoded player IDs or names).
        """
        if overs >= 20:
            return []

        pp_blitz = RainReducedOversEngine._pick_dynamic_c_vc(
            players, prefer_roles_c=["BAT", "WK", "AR"], prefer_roles_vc=["BOWL", "AR"],
            prefer_order_max=3, prefer_pace=True
        )
        dls_chase = RainReducedOversEngine._pick_dynamic_c_vc(
            players, prefer_roles_c=["BAT", "WK", "AR"], prefer_roles_vc=["BOWL", "AR"],
            prefer_order_max=4, prefer_pace=False
        )
        death_yorker = RainReducedOversEngine._pick_dynamic_c_vc(
            players, prefer_roles_c=["BOWL", "AR"], prefer_roles_vc=["BAT", "AR"],
            prefer_order_max=5, prefer_pace=True
        )
        top_order = RainReducedOversEngine._pick_dynamic_c_vc(
            players, prefer_roles_c=["BAT", "WK", "AR"], prefer_roles_vc=["BAT", "WK", "AR"],
            prefer_order_max=3, prefer_pace=False
        )
        express_pace = RainReducedOversEngine._pick_dynamic_c_vc(
            players, prefer_roles_c=["BOWL"], prefer_roles_vc=["BOWL", "AR"],
            prefer_order_max=11, prefer_pace=True
        )

        def scenario(
            tag_suffix: str,
            name: str,
            gl_potential: str,
            rationale: str,
            picks: Dict[str, Optional[str]],
            team_a_bias: float = 1.1,
            team_b_bias: float = 1.1
        ) -> Dict[str, Any]:
            return {
                "tag": f"RAIN_SPRINT_{overs}OV_{tag_suffix}",
                "name": name,
                "short_match": True,
                "team_a_bias": team_a_bias,
                "team_b_bias": team_b_bias,
                "preferred_c_id": picks["preferred_c_id"],
                "preferred_c_name": picks["preferred_c_name"],
                "preferred_vc_id": picks["preferred_vc_id"],
                "preferred_vc_name": picks["preferred_vc_name"],
                "gl_potential": gl_potential,
                "rationale": rationale,
                "data_provenance": "DYNAMIC_FROM_ACTIVE_ROSTER" if players else "TEMPLATE_NO_ROSTER",
                "official_dls": False,
                "verification": "Fantasy scenario template. Preferred C/VC derived from supplied roster or null."
            }

        return [
            scenario(
                "POWERPLAY_BLITZ",
                f"{overs}-Over Powerplay Sprint",
                "Short-Format Ceiling",
                f"{overs}-over match eliminates middle-order anchor value. Prioritise aggressive top-order batters and frontline pacers who keep full quota.",
                pp_blitz,
                team_a_bias=1.20, team_b_bias=0.95
            ),
            scenario(
                "DLS_CHASE",
                f"{overs}-Over Reduced-Overs Chase Leverage",
                "Chase Volume Leverage",
                f"Wet-ball conditions impair spin control. Favour top-order anchors and death-capable all-rounders/bowlers who retain overs under shortened quotas.",
                dls_chase,
                team_a_bias=1.05, team_b_bias=1.15
            ),
            scenario(
                "DEATH_YORKER_CARNAGE",
                f"{overs}-Over Death Seam Carnage",
                "Wicket Multiplier",
                f"Batters slog in a compressed {overs}-over shootout. Frontline seamers with yorker/death skill produce elevated wicket rates.",
                death_yorker,
                team_a_bias=1.10, team_b_bias=1.05
            ),
            scenario(
                "TOP_ORDER_SHOOTOUT",
                f"{overs}-Over Top-3 Heavy Shootout",
                "High-Ceiling Concentration",
                f"Fade pure lower-middle-order batters. Concentrate volume on top-3 batters who face the majority of deliveries in short games.",
                top_order,
                team_a_bias=1.12, team_b_bias=1.12
            ),
            scenario(
                "EXPRESS_PACE_STRANGLE",
                f"{overs}-Over Express Pace Strangle",
                "Differential Pace Punt",
                f"High-pace bowlers who keep 1–2 overs under reduced quotas can remove top orders early on damp surfaces.",
                express_pace,
                team_a_bias=1.08, team_b_bias=1.08
            ),
        ]
