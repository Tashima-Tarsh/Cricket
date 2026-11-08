"""Analytic projection model.

Turns features into (mean, sd, p_dnb) with NO training required, using T20
base-rate priors. Recalibrate the priors from real scorecards when available.

Every constant carries its cricket rationale.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

# --- batting priors ------------------------------------------------------
# mean legal balls faced by batting position in a T20 innings
BALLS_BY_POS = {1: 24.0, 2: 23.0, 3: 20.0, 4: 18.0, 5: 15.0, 6: 12.0,
                7: 9.0, 8: 6.0, 9: 4.0, 10: 3.0, 11: 2.0}
# baseline strike rate by position; openers face the new ball, finishers attack
SR_BY_POS = {1: 132.0, 2: 130.0, 3: 136.0, 4: 138.0, 5: 145.0, 6: 148.0,
             7: 140.0, 8: 125.0, 9: 115.0, 10: 108.0, 11: 100.0}
# P(batter does not bat, or faces <3 balls) by position
PDNB_BY_POS = {1: 0.02, 2: 0.02, 3: 0.04, 4: 0.06, 5: 0.10, 6: 0.16,
               7: 0.24, 8: 0.34, 9: 0.46, 10: 0.54, 11: 0.60}

# points coefficient of variation by role - how volatile a role's scoring is
CV_BY_ROLE = {"BAT": 1.15, "WK": 1.15, "AR": 1.30, "BOWL": 1.40}

# --- bowling priors ------------------------------------------------------
OVERS_BY_ROLE = {"BOWL": 3.2, "AR": 2.2, "BAT": 0.3, "WK": 0.0}  # ~3.2 overs avg per innings
WKT_PER_BALL = 0.048          # ~1.15 wickets per 24 balls
ECON_PRIOR = 8.4              # runs per over at a neutral venue
MAIDEN_RATE = 0.035           # maidens per over
LBW_BOWLED_SHARE = 0.55       # share of wickets that are bowled/lbw

# --- fielding priors -----------------------------------------------------
CATCHES_BY_ROLE = {"WK": 0.50, "BAT": 0.30, "AR": 0.25, "BOWL": 0.12}
STUMPINGS_BY_ROLE = {"WK": 0.18, "BAT": 0.0, "AR": 0.0, "BOWL": 0.0}

MIN_MEAN, MAX_MEAN = 1.0, 95.0


def _gamma_milestone(mu_runs: float, cv: float) -> float:
    """E[bonus] for 30/50/100 from a gamma fitted to (mu_runs, cv)."""
    if mu_runs <= 0:
        return 0.0
    shape = 1.0 / (cv * cv)
    g = stats.gamma(shape, scale=mu_runs / shape)
    return 4.0 * (1 - g.cdf(30)) + 8.0 * (1 - g.cdf(50)) + 16.0 * (1 - g.cdf(100))


def _expected_sr_bonus(sr: float, balls: float) -> float:
    """E[strike-rate bonus] given expected SR and balls."""
    if balls < 10:
        return 0.0
    if sr > 170:
        return 6.0
    if sr > 150:
        return 4.0
    if sr >= 130:
        return 2.0
    if sr >= 60:
        return -2.0
    if sr >= 50:
        return -4.0
    return -6.0


def _expected_eco_bonus(econ: float, balls: float) -> float:
    if balls < 12:
        return 0.0
    if econ <= 5:
        return 6.0
    if econ < 6:
        return 4.0
    if econ < 7:
        return 2.0
    if econ <= 10:
        return 0.0
    if econ <= 11:
        return -2.0
    if econ <= 12:
        return -4.0
    return -6.0


def project_batter(f) -> tuple[float, float, float]:
    pos = int(getattr(f, "bat_pos", 6) or 6)
    pos = min(max(pos, 1), 11)
    venue_adj = float(getattr(f, "venue_adj", 1.0) or 1.0)
    team_adj = float(getattr(f, "team_strength_adj", 1.0) or 1.0)
    form_sr = float(getattr(f, "form_sr", 130.0) or 130.0)
    matchup_edge = float(getattr(f, "matchup_edge", 0.0) or 0.0)

    mu_balls = BALLS_BY_POS[pos] * venue_adj * team_adj
    sr = SR_BY_POS[pos] * (form_sr / 130.0) * (1.0 + matchup_edge / 300.0) * venue_adj
    sr = float(np.clip(sr, 70.0, 220.0))
    mu_runs = max(mu_balls * sr / 100.0, 0.0)

    cv = CV_BY_ROLE.get(getattr(f, "role", "BAT"), 1.15)
    boundary = 0.11 * mu_runs * 1.0 + 0.035 * mu_runs * 2.0
    milestone = _gamma_milestone(mu_runs, cv)
    sr_b = _expected_sr_bonus(sr, mu_balls)
    duck = 2.0 * float(getattr(f, "pout_mid", 0.06) or 0.06) * 4.0

    proj = mu_runs + boundary + milestone + sr_b - duck
    sd = cv * max(proj, 1.0)
    p_dnb = PDNB_BY_POS[pos]
    return float(np.clip(proj, MIN_MEAN, MAX_MEAN)), float(sd), float(p_dnb)


def project_bowler(f) -> tuple[float, float, float]:
    role = getattr(f, "role", "BOWL")
    venue_adj = float(getattr(f, "venue_adj", 1.0) or 1.0)
    share = float(getattr(f, "bowl_share", 1.0) or 1.0)
    quality = float(getattr(f, "bowl_quality", 1.0) or 1.0)

    overs = OVERS_BY_ROLE.get(role, 0.0) * share
    if overs <= 0.05:
        return 0.0, 0.0, 1.0
    balls = 6.0 * overs
    wkts = balls * WKT_PER_BALL * quality
    econ = ECON_PRIOR / max(venue_adj, 0.5) / max(quality, 0.5)

    proj = (30.0 * wkts + 8.0 * LBW_BOWLED_SHARE * wkts
            + 12.0 * MAIDEN_RATE * overs
            + _expected_eco_bonus(econ, balls))
    proj += 8.0 * CATCHES_BY_ROLE.get(role, 0.12)

    cv = CV_BY_ROLE.get(role, 1.4)
    sd = cv * max(proj, 1.0)
    return float(np.clip(proj, MIN_MEAN, MAX_MEAN)), float(sd), 0.0


def project_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Vectorised entrypoint. Returns player_id, proj, sd, p_dnb."""
    rows = []
    for f in df.itertuples():
        role = getattr(f, "role", "BAT")
        if role == "BOWL" or (role == "AR" and float(getattr(f, "bowl_share", 0.0) or 0) > 0.5):
            m, s, d = project_bowler(f)
            bm, bs, bd = project_batter(f)
            # all-rounder blends both disciplines
            if role == "AR":
                m, s = 0.65 * m + 0.35 * bm, 0.65 * s + 0.35 * bs
                d = min(d, bd)
        else:
            m, s, d = project_batter(f)
            if role == "AR":
                bw, sw, _ = project_bowler(f)
                m, s = 0.7 * m + 0.3 * bw, 0.7 * s + 0.3 * sw
        rows.append(dict(player_id=f.player_id, proj=m, sd=s, p_dnb=d))
    return pd.DataFrame(rows)


def calibrate(scorecards: pd.DataFrame) -> dict:
    """Re-estimate priors from real scorecards. Returns a patch dict."""
    if scorecards is None or len(scorecards) < 200:
        return {}
    pts = scorecards.groupby("role")["points"]
    return {"cv_by_role": {r: float(g.std() / max(g.mean(), 1e-6))
                           for r, g in pts if g.mean() > 0}}
