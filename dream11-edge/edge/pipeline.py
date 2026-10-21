"""Full orchestration. CLI and dashboard both call this."""
from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from .config import settings
from .features import build as build_features
from .model import projection_model as PM
from .model import projections as PR
from .optimize import field as F
from .optimize import portfolio as PF
from .optimize.constraints import Ctx


def build_match(roster: pd.DataFrame, match: dict, *, n_sims=None, n_field=None,
                n_entries=None, risk=0.0, locked=(), banned=(), seed=11,
                progress=None):
    st = settings()
    n_sims = n_sims or st.sim.n_sims
    n_field = n_field or st.sim.n_field
    n_entries = n_entries or st.sim.n_entries

    ref = datetime.now(ZoneInfo(st.tz))
    feats = build_features(match, roster, None, ref)
    proj = PM.project_frame(feats)
    roster = roster.drop(columns=["proj", "sd", "p_dnb"], errors="ignore").merge(
        proj, on="player_id", how="left")

    if progress:
        progress("simulating")
    marginals = PR.fit_marginals(roster, roster.proj, roster.sd, roster.p_dnb)
    sims, ids, corr, err = PR.run(roster, marginals, match.get("pitch_class", "flat"),
                                  n_sims, seed=seed)

    own = dict(zip(roster.player_id, roster.own_pct))
    summary = PR.summarise(sims, ids, own)
    roster = roster.drop(columns=["proj", "sd", "boom", "own_pct", "leverage"], errors="ignore").merge(
        summary[["player_id", "proj", "sd", "boom", "own_pct", "leverage"]],
        on="player_id", how="left")

    ctx = Ctx.from_frame(roster)
    idx = {p: i for i, p in enumerate(ids)}
    rng = np.random.default_rng(seed)

    if progress:
        progress("building field")
    field = F.build_field(ctx, n_field, rng)
    fsc = F.field_scores(field, sims, idx)

    if progress:
        progress("optimising portfolio")
    port = PF.build(ctx, sims, idx, fsc, n_entries, rng, risk=risk,
                    locked=locked, banned=banned)

    expo = dict(PF.exposure_report(port, ctx))
    roster["expo"] = roster.player_id.map(expo).fillna(0.0)
    return dict(roster=roster, portfolio=port, corr=corr, err=err,
                field_n=len(field), sims=n_sims, ids=ids)


def demo_roster() -> pd.DataFrame:
    from .ingest.dream11 import proxy_ownership
    spec = [("A. Rahane","MUM","BAT",9.0,1,0,0),("S. Iyer","MUM","BAT",9.5,2,0,0),
            ("D. Brevis","MUM","BAT",8.5,3,1,0),("T. Varma","MUM","BAT",9.0,4,0,0),
            ("H. Pandya","MUM","AR",9.5,5,0,1),("N. Wadhera","MUM","BAT",8.0,6,0,0),
            ("T. David","MUM","AR",9.0,7,1,1),("I. Kishan","MUM","WK",9.0,8,0,0),
            ("P. Chawla","MUM","BOWL",8.5,9,0,1),("J. Bumrah","MUM","BOWL",9.5,10,0,1),
            ("G. Coetzee","MUM","BOWL",8.5,11,1,1),
            ("R. Gaikwad","CHE","BAT",9.5,1,0,0),("D. Conway","CHE","WK",9.0,2,1,0),
            ("S. Dube","CHE","AR",9.0,3,0,1),("A. Rayudu","CHE","BAT",8.5,4,0,0),
            ("J. Jadeja","CHE","AR",9.5,5,0,1),("S. Curran","CHE","AR",9.0,6,1,1),
            ("M. Dhoni","CHE","WK",8.5,7,0,0),("M. Theekshana","CHE","BOWL",8.5,9,1,1),
            ("R. Jadeja","CHE","BOWL",8.5,10,0,1),("T. Deshpande","CHE","BOWL",8.0,11,0,1),
            ("M. Pathirana","CHE","BOWL",9.0,10,1,1)]
    styles = {"BOWL": ["right-arm fast","off-break","left-arm orthodox","leg-break",
                       "right-arm medium","left-arm fast"],
              "AR": ["right-arm medium","off-break","left-arm orthodox"],
              "BAT": ["right-arm medium"], "WK": []}
    rows = []
    for k, (nm, tm, rl, cr, pos, ovs, is_bowl) in enumerate(spec):
        st = styles[rl]
        rows.append(dict(player_id=f"p{k:02d}", name=nm, team=tm, role=rl, credit=cr,
                         bat_pos=pos, overseas=bool(ovs), is_xi=True,
                         bowl_style=(st[k % len(st)] if st else "")))
    df = pd.DataFrame(rows)
    df["own_pct"] = proxy_ownership(df.bat_pos.rsub(12) * 4.0)
    return df

