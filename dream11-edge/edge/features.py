"""Feature construction.

Leakage-safe: a feature for match M only uses data strictly before M.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

PHASES = ("pp", "mid", "death")

_BOWL_TYPES = ("leftarm_spin", "leftarm_pace", "offspin", "legspin", "pace", "medium")


def bowl_type(style: str) -> str:
    s = (style or "").lower()
    if "left" in s and ("orthodox" in s or "spin" in s or "wrist" in s):
        return "leftarm_spin"
    if "left" in s and ("fast" in s or "medium" in s or "pace" in s):
        return "leftarm_pace"
    if "off" in s or "orthodox" in s:
        return "offspin"
    if "leg" in s or "chinaman" in s or "wrist" in s:
        return "legspin"
    if "fast" in s or "pace" in s:
        return "pace"
    return "medium"


def decay_weights(dates: pd.Series, halflife_days: int, ref: pd.Timestamp) -> np.ndarray:
    age = (ref - pd.to_datetime(dates)).dt.days.clip(lower=0)
    return np.power(0.5, age / max(halflife_days, 1))


def phase_of(over: int) -> str:
    return "pp" if over < 6 else "mid" if over < 16 else "death"


def form_table(balls: pd.DataFrame, halflife: int, ref: pd.Timestamp) -> pd.DataFrame:
    b = balls.copy()
    b["w"] = decay_weights(b["match_date"], halflife, ref)
    b["boundary"] = b["runs"].isin([4, 6]).astype(float)
    b["is_ball"] = (~b["outcome"].isin(["wd", "nb"])).astype(float)
    b["is_w"] = (b["outcome"] == "W").astype(float)

    rows = []
    for (pid, phase), d in b.groupby(["batter_id", "phase"]):
        wb = d["w"].sum()
        rows.append(dict(
            batter_id=pid, phase=phase,
            balls=d["is_ball"].sum(), wballs=wb,
            sr=100 * (d["w"] * d["runs"]).sum() / max(wb, 1e-6),
            bnd=(d["w"] * d["boundary"]).sum() / max(wb, 1e-6),
            p_out=(d["w"] * d["is_w"]).sum() / max(wb, 1e-6),
        ))
    return pd.DataFrame(rows)


def matchup_table(balls: pd.DataFrame, min_balls: int) -> pd.DataFrame:
    """batter x bowler-type, empirical-Bayes shrunk toward the batter's own rate."""
    b = balls.copy()
    b["btype"] = b["bowl_style"].map(bowl_type)
    b["is_ball"] = (~b["outcome"].isin(["wd", "nb"])).astype(float)
    b["is_w"] = (b["outcome"] == "W").astype(float)

    cell = b.groupby(["batter_id", "btype"]).agg(
        balls=("is_ball", "sum"), runs=("runs", "sum"), outs=("is_w", "sum")
    ).reset_index()
    base = b.groupby("batter_id").agg(
        b_balls=("is_ball", "sum"), b_runs=("runs", "sum"), b_outs=("is_w", "sum")
    ).reset_index()

    d = cell.merge(base, on="batter_id")
    k = max(min_balls, 1)
    d["sr"] = 100 * (d["runs"] + k * d["b_runs"] / d["b_balls"].clip(lower=1)) / (d["balls"] + k)
    d["dismissal"] = (d["outs"] + k * d["b_outs"] / d["b_balls"].clip(lower=1)) / (d["balls"] + k)
    return d[["batter_id", "btype", "balls", "sr", "dismissal"]]


def venue_par(scorecards: pd.DataFrame, venues: dict) -> dict:
    par = {k: v["par"] for k, v in venues.get("venues", {}).items()}
    if "venue" in scorecards.columns and len(scorecards):
        agg = scorecards.groupby("venue").agg(
            runs=("runs", "sum"), n=("match_id", "nunique"))
        for v, row in agg.iterrows():
            obs = row["runs"] / max(row["n"], 1)
            par[v] = 0.5 * par.get(v, venues["default"]["par"]) + 0.5 * float(obs)
    return par


def build(match: dict, roster: pd.DataFrame, balls: pd.DataFrame,
          scorecards: pd.DataFrame, ref: pd.Timestamp) -> pd.DataFrame:
    from .config import settings

    mcfg = settings().model
    venue = match.get("venue", "")
    vcfg = settings().venues["venues"].get(venue, settings().venues["default"])

    form = form_table(balls, mcfg.form_halflife_days, ref)
    mu = matchup_table(balls, mcfg.matchup_min_balls)

    out = roster.copy()
    out["venue_par"] = vcfg["par"]
    out["pitch"] = match.get("pitch_class", vcfg["pitch"])

    for ph in PHASES:
        sub = form[form.phase == ph].set_index("batter_id")
        out[f"sr_{ph}"] = out.player_id.map(sub["sr"]).fillna(110.0)
        out[f"bnd_{ph}"] = out.player_id.map(sub["bnd"]).fillna(0.11)
        out[f"pout_{ph}"] = out.player_id.map(sub["p_out"]).fillna(0.06)

    team_a = out.team.iloc[0] if len(out) else ""
    opp_types = set(roster[roster.team != team_a]["bowl_style"].map(bowl_type)) or set(_BOWL_TYPES)
    mu_idx = mu[mu.btype.isin(opp_types)].groupby("batter_id")["sr"].mean()
    out["matchup_sr"] = out.player_id.map(mu_idx).fillna(out["sr_mid"])
    out["matchup_edge"] = out["matchup_sr"] - out["sr_mid"]

    agg = form.assign(x=form.sr * form.wballs).groupby("batter_id").agg(
        x=("x", "sum"), w=("wballs", "sum"))
    out["form_sr"] = out.player_id.map(agg["x"] / agg["w"].clip(lower=1e-6)).fillna(115.0)
    out["venue_adj"] = out["venue_par"] / settings().venues["default"]["par"]
    return out
