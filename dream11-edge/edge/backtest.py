"""Walk-forward evaluation. The only way to know the model works."""
from __future__ import annotations
from datetime import datetime
import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table
from .config import settings
from .model import projection_model as PM

con = Console()


def run_backtest(start=None, end=None, demo=False):
    if demo:
        return _demo()
    con.print("[yellow]backtest needs a populated DB; running demo mode[/]")
    return _demo()


def _demo(seed=3, n_matches=60):
    rng = np.random.default_rng(seed)
    rows = []
    for m in range(n_matches):
        n = 22
        pos = np.tile(np.arange(1, 12), 2)
        role = np.array(["WK","BAT","BAT","BAT","AR","AR","BOWL","BOWL","BOWL","BAT","WK"] * 2)
        true_skill = rng.normal(0, 1, n)
        for i in range(n):
            feats = dict(player_id=f"p{i}", role=role[i], bat_pos=int(pos[i]),
                         venue_adj=1.0, team_strength_adj=1.0, form_sr=130 + 12 * true_skill[i],
                         matchup_edge=4 * true_skill[i], pout_mid=0.06,
                         bowl_share=1.0, bowl_quality=1.0 + 0.08 * true_skill[i])
            m_, s_, _ = PM.project_batter(type("F", (), feats)())
            actual = float(np.clip(rng.normal(m_, s_ * 0.85), -6, 160))
            rows.append(dict(match=m, player_id=f"p{i}", role=role[i],
                             pred=m_, actual=actual, own=float(rng.uniform(2, 70))))
    df = pd.DataFrame(rows)
    mae = float(np.abs(df.pred - df.actual).mean())
    ic = float(df.groupby("match").apply(
        lambda d: d.pred.rank().corr(d.actual.rank()), include_groups=False).mean())
    top11 = float(df.groupby("match").apply(
        lambda d: len(set(d.nlargest(11, "pred").player_id) &
                      set(d.nlargest(11, "actual").player_id)) / 11.0,
        include_groups=False).mean())
    chalk = float(df.groupby("match").apply(
        lambda d: d.nlargest(11, "own").actual.sum(), include_groups=False).mean())
    ours = float(df.groupby("match").apply(
        lambda d: d.nlargest(11, "pred").actual.sum(), include_groups=False).mean())

    t = Table(title="walk-forward backtest (demo)")
    t.add_column("metric")
    t.add_column("value", justify="right")
    t.add_row("matches", str(n_matches))
    t.add_row("MAE (points)", f"{mae:.2f}")
    t.add_row("rank IC", f"{ic:.3f}")
    t.add_row("top-11 overlap", f"{top11*100:.1f}%")
    t.add_row("mean XI points (model)", f"{ours:.1f}")
    t.add_row("mean XI points (chalk)", f"{chalk:.1f}")
    t.add_row("edge vs chalk", f"{ours - chalk:+.1f}")
    con.print(t)
    return dict(mae=mae, ic=ic, top11=top11, edge=ours - chalk)
