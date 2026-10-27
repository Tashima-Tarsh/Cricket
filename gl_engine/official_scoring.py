"""Dated published Dream11 fantasy-cricket points profile.

Source (manually reviewed 2026-10-27):
https://www.dream11.com/fantasy-cricket/point-system
Do NOT rewrite past archived leagues with these rules. Select exact format.
Bowling overs use scorecard X.Y notation (e.g. 4.2 = 26 legal balls).
Supplied runs, fours, sixes, dismissed and playing status are inputs; the
scorer does not infer observed fielding or valid replacement eligibility.
"""
from decimal import Decimal, InvalidOperation
from math import isfinite
from typing import Dict, Any

RULE_VERSION = "dream11_published_2026_10_27"
SOURCE_URL = "https://www.dream11.com/fantasy-cricket/point-system"
MILESTONES = {
    "T20": [(25, 4), (50, 8), (75, 12), (100, 16)],
    "ODI": [(25, 4), (50, 8), (75, 12), (100, 16), (125, 20), (150, 24)],
    "T10": [(25, 8), (50, 12), (75, 16), (100, 20)],
}
WICKET_HAUL = {
    "T20": [(3, 4), (4, 8), (5, 12)],
    "ODI": [(4, 4), (5, 8), (6, 12)],
    "T10": [(2, 4), (3, 8), (4, 12), (5, 16)],
}


def _threshold_bonus(value: int, bands) -> int:
    return next((pts for threshold, pts in reversed(bands) if value >= threshold), 0)


def _strike_rate(fmt: str, runs: int, balls: int) -> float:
    if balls < {"T20": 10, "ODI": 20, "T10": 5}[fmt]:
        return 0.0
    sr = 100 * runs / balls
    if fmt == "T20":
        return 6 if sr > 170 else 4 if sr > 150 else 2 if sr >= 130 else (
            -6 if sr < 50 else -4 if sr < 60 else -2 if sr <= 70 else 0
        )
    if fmt == "ODI":
        return 6 if sr > 140 else 4 if sr > 120 else 2 if sr >= 100 else (
            -6 if sr < 30 else -4 if sr < 40 else -2 if sr <= 50 else 0
        )
    return 6 if sr > 190 else 4 if sr > 170 else 2 if sr >= 150 else (
        -6 if sr < 60 else -4 if sr < 70 else -2 if sr <= 80 else 0
    )


def _overs_as_balls(overs: float) -> int:
    """Convert cricket scorecard notation X.Y to legitimate balls bowled.

    4.2 is 4 completed overs + 2 balls (26 legal deliveries), NOT 4.2
    decimal overs. Inputs such as 4.6 and 4.25 are not cricket notation.
    """
    if isinstance(overs, bool) or not isinstance(overs, (int, float)) or not isfinite(overs) or overs < 0:
        raise ValueError("Overs must be a nonnegative finite number in cricket X.Y notation")
    try:
        value = Decimal(str(overs))
    except InvalidOperation as exc:
        raise ValueError("Invalid cricket-notation overs") from exc
    completed = int(value)
    partial = (value - Decimal(completed)) * 10
    if partial != partial.to_integral_value() or not 0 <= partial <= 5:
        raise ValueError("Cricket overs must have 0-5 balls after the decimal point")
    return completed * 6 + int(partial)


def _economy(fmt: str, runs: int, overs: float) -> float:
    balls = _overs_as_balls(overs)
    minimum_balls = {"T20": 12, "ODI": 30, "T10": 6}[fmt]
    if balls < minimum_balls:
        return 0.0
    er = runs * 6.0 / balls
    if fmt == "T20":
        return 6 if er < 5 else 4 if er < 6 else 2 if er <= 7 else (
            -6 if er > 12 else -4 if er > 11 else -2 if er >= 10 else 0
        )
    if fmt == "ODI":
        return 6 if er < 2.5 else 4 if er < 3.5 else 2 if er <= 4.5 else (
            -6 if er > 9 else -4 if er > 8 else -2 if er >= 7 else 0
        )
    return 6 if er < 7 else 4 if er < 8 else 2 if er <= 9 else (
        -6 if er > 16 else -4 if er > 15 else -2 if er >= 14 else 0
    )


def score_official(*, match_format: str, runs: int = 0, fours: int = 0,
                   sixes: int = 0, balls_faced: int = 0, wickets: int = 0,
                   bowled_lbw: int = 0, overs_bowled: float = 0.0,
                   runs_conceded: int = 0, maidens: int = 0, dots: int = 0,
                   catches: int = 0, stumpings: int = 0,
                   run_outs_direct: int = 0, run_outs_indirect: int = 0,
                   is_playing: bool = True, is_womens: bool = False,
                   is_captain: bool = False, is_vice_captain: bool = False,
                   was_dismissed: bool = False, **unsupported) -> Dict[str, Any]:
    fmt = match_format.upper()
    if fmt not in MILESTONES:
        raise ValueError("Unsupported scoring format: explicit T20, ODI or T10 required")
    if unsupported:
        raise ValueError(f"Unsupported scoring statistics: {sorted(unsupported)}")
    quantities = (runs, fours, sixes, balls_faced, wickets, bowled_lbw,
                  overs_bowled, runs_conceded, maidens, dots, catches,
                  stumpings, run_outs_direct, run_outs_indirect)
    if any(isinstance(x, bool) or x < 0 for x in quantities):
        raise ValueError("Negative or nonnumeric scorecard statistics are not allowed")
    legal_balls_bowled = _overs_as_balls(overs_bowled)
    if fours * 4 + sixes * 6 > runs or fours + sixes > balls_faced:
        raise ValueError("Boundary counts exceed observed runs or balls")
    if bowled_lbw > wickets:
        raise ValueError("Bowled/LBW dismissals cannot exceed bowler wickets")
    if is_captain and is_vice_captain:
        raise ValueError("Captain and vice-captain cannot be the same player")
    # Duck must mean an actual dismissal, not simply 0 runs faced.
    milestones = _threshold_bonus(runs, MILESTONES[fmt])
    bat = runs + fours * 4 + sixes * 6 + milestones
    if was_dismissed and runs == 0 and balls_faced:
        bat -= 3 if fmt == "ODI" else 2
    bat += _strike_rate(fmt, runs, balls_faced)

    wicket_bonus = _threshold_bonus(wickets, WICKET_HAUL[fmt])
    dot_pts = (dots // 3) if fmt == "ODI" else dots
    bowl = (30 * wickets + 8 * bowled_lbw + dot_pts +
            (4 if fmt == "ODI" else 16 if fmt == "T10" else 12) * maidens +
            wicket_bonus + _economy(fmt, runs_conceded, overs_bowled))
    field = catches * 8 + (4 if catches >= 3 else 0) + (
        12 * stumpings + 12 * run_outs_direct + 6 * run_outs_indirect
    )
    xi = 4 if is_playing else 0
    # No undocumented artificial -6 ceiling/floor.
    base = round(float(bat + bowl + field + xi), 2)
    multiplier = 2.0 if is_captain else 1.5 if is_vice_captain else 1.0
    return {
        "rule_version": RULE_VERSION, "format": fmt,
        "total_points": round(base * multiplier, 2),
        "base_points": base, "multiplier": multiplier,
        "breakdown": {"batting": bat, "bowling": bowl, "fielding": field,
                      "starting_xi": xi, "dot_balls": dot_pts,
                      "wicket_haul_bonus": wicket_bonus,
                      "batting_milestone_bonus": milestones,
                      "legal_balls_bowled": legal_balls_bowled},
        "provenance": {
            "source": SOURCE_URL,
            "verification_status": "VERIFIED",
            "reviewed_on": "2026-10-27",
            "caveat": "Contest rules may change; confirm exact format/rule snapshot before playing.",
        },
    }
