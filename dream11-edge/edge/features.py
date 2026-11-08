"""Leakage-safe feature construction."""
from __future__ import annotations
import numpy as np
import pandas as pd

PHASES = ("pp", "mid", "death")


def bowl_type(style):
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


def decay_weights(dates, halflife, ref):
    age = (ref - pd.to_datetime(dates)).dt.days.clip(lower=0)
    return np.power(0.5, age / max(halflife, 1))


def form_table(balls, halflife, ref):
    b = balls.copy()
    b["w"] = decay_weights(b["match_date"], halflife, ref)
    b["bnd"] = b["runs"].isin([4, 6]).astype(float)
    b["ib"] = (~b["outcome"].isin(["wd", "nb"])).astype(float)
    b["iw"] = (b["outcome"] == "W").astype(float)
    rows = []
    for (pid, ph), d in b.groupby(["batter_id", "phase"]):
        wb = d["w"].sum()
        rows.append(dict(batter_id=pid, phase=ph, wballs=wb,
                         sr=100 * (d["w"] * d["runs"]).sum() / max(wb, 1e-6),
                         bnd=(d["w"] * d["bnd"]).sum() / max(wb, 1e-6),
                         p_out=(d["w"] * d["iw"]).sum() / max(wb, 1e-6)))
    return pd.DataFrame(rows)


def matchup_table(balls, min_balls):
    b = balls.copy()
    b["bt"] = b["bowl_style"].map(bowl_type)
    b["ib"] = (~b["outcome"].isin(["wd", "nb"])).astype(float)
    b["iw"] = (b["outcome"] == "W").astype(float)
    cell = b.groupby(["batter_id", "bt"]).agg(balls=("ib","sum"), runs=("runs","sum"),
                                              outs=("iw","sum")).reset_index()
    base = b.groupby("batter_id").agg(bb=("ib","sum"), br=("runs","sum"),
                                      bo=("iw","sum")).reset_index()
    d = cell.merge(base, on="batter_id")
    k = max(min_balls, 1)
    d["sr"] = 100 * (d["runs"] + k * d["br"] / d["bb"].clip(lower=1)) / (d["balls"] + k)
    return d[["batter_id", "bt", "sr"]]


def build(match, roster, balls, ref):
    """Attach features. Missing history falls back to priors."""
    from .config import settings
    mcfg = settings().model
    venue = match.get("venue", "")
    vcfg = settings().venues["venues"].get(venue, settings().venues["default"])
    out = roster.copy()
    out["venue_adj"] = vcfg["par"] / settings().venues["default"]["par"]

    if balls is None or not len(balls):
        for ph in PHASES:
            out[f"sr_{ph}"] = 128.0
            out[f"pout_{ph}"] = 0.06
        out["form_sr"] = 130.0
        out["matchup_edge"] = 0.0
        out["team_strength_adj"] = 1.0
        out["bowl_share"] = 1.0
        out["bowl_quality"] = 1.0
        return out

    form = form_table(balls, mcfg.form_halflife_days, ref)
    mu = matchup_table(balls, mcfg.matchup_min_balls)
    for ph in PHASES:
        sub = form[form.phase == ph].set_index("batter_id")
        out[f"sr_{ph}"] = out.player_id.map(sub["sr"]).fillna(128.0)
        out[f"pout_{ph}"] = out.player_id.map(sub["p_out"]).fillna(0.06)
    agg = form.assign(x=form.sr * form.wballs).groupby("batter_id").agg(
        x=("x","sum"), w=("wballs","sum"))
    out["form_sr"] = out.player_id.map(agg["x"] / agg["w"].clip(lower=1e-6)).fillna(130.0)
    team_a = out.team.iloc[0] if len(out) else ""
    opp = set(roster[roster.team != team_a]["bowl_style"].map(bowl_type))
    mi = mu[mu.bt.isin(opp)].groupby("batter_id")["sr"].mean()
    out["matchup_sr"] = out.player_id.map(mi).fillna(out["sr_mid"])
    out["matchup_edge"] = out["matchup_sr"] - out["sr_mid"]
    out["team_strength_adj"] = 1.0
    out["bowl_share"] = 1.0
    out["bowl_quality"] = out.player_id.map(
        mu.groupby("batter_id")["sr"].mean()).fillna(130.0).rdiv(130.0)
    return out
