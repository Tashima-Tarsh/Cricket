from __future__ import annotations

import argparse
import webbrowser
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table

from . import db
from .config import settings
from .ingest import espn
from .ingest.dream11 import proxy_ownership
from .model import projections as P
from .optimize import field as F
from .optimize import portfolio as PF
from .optimize.constraints import Ctx
from .report import payload, write

con = Console()

DEMO_SPEC = [
    # (name, team, role, credit, bat_pos, overseas)
    ("A. Rahane",   "MUM", "BAT",  9.0, 1, 0),
    ("S. Iyer",     "MUM", "BAT",  9.5, 2, 0),
    ("D. Brevis",   "MUM", "BAT",  8.5, 3, 1),
    ("T. Varma",    "MUM", "BAT",  9.0, 4, 0),
    ("H. Pandya",   "MUM", "AR",   9.5, 5, 0),
    ("N. Wadhera",  "MUM", "BAT",  8.0, 6, 0),
    ("T. David",    "MUM", "AR",   9.0, 7, 1),
    ("I. Kishan",   "MUM", "WK",   9.0, 8, 0),
    ("P. Chawla",   "MUM", "BOWL", 8.5, 9, 0),
    ("J. Bumrah",   "MUM", "BOWL", 9.5, 10, 0),
    ("G. Coetzee",  "MUM", "BOWL", 8.5, 11, 1),
    ("R. Gaikwad",  "CHE", "BAT",  9.5, 1, 0),
    ("D. Conway",   "CHE", "WK",   9.0, 2, 1),
    ("S. Dube",     "CHE", "AR",   9.0, 3, 0),
    ("A. Rayudu",   "CHE", "BAT",  8.5, 4, 0),
    ("J. Jadeja",   "CHE", "AR",   9.5, 5, 0),
    ("S. Curran",   "CHE", "AR",   9.0, 6, 1),
    ("M. Dhoni",    "CHE", "WK",   8.5, 7, 0),
    ("M. Theekshana", "CHE", "BOWL", 8.5, 9, 1),
    ("R. Jadeja",   "CHE", "BOWL", 8.5, 10, 0),
    ("T. Deshpande", "CHE", "BOWL", 8.0, 11, 0),
    ("M. Pathirana", "CHE", "BOWL", 9.0, 10, 1),
]

DEMO_PROJ = [34, 39, 31, 36, 33, 27, 31, 30, 26, 40, 29,
             38, 35, 32, 29, 34, 30, 30, 28, 27, 26, 37]
DEMO_SD = [22, 24, 20, 23, 21, 19, 22, 20, 18, 25, 20,
           24, 22, 21, 20, 22, 21, 20, 19, 18, 18, 24]
DEMO_PDNB = [.16, .14, .22, .18, .20, .24, .26, .20, .30, .14, .26,
             .14, .16, .22, .24, .16, .22, .22, .28, .28, .30, .18]


def demo_roster() -> pd.DataFrame:
    rows = []
    for k, (name, team, role, cr, pos, ovs) in enumerate(DEMO_SPEC):
        rows.append(dict(
            player_id=f"p{k:02d}", name=name, short_name=name.split()[-1],
            team=team, role=role, credit=cr, bat_pos=pos, overseas=bool(ovs),
            is_xi=True, proj=float(DEMO_PROJ[k]), sd=float(DEMO_SD[k]),
            p_dnb=float(DEMO_PDNB[k]),
        ))
    df = pd.DataFrame(rows)
    df["own_pct"] = proxy_ownership(df.proj)
    return df


def cmd_init(_args):
    con.print(f"[green]database ready at {db.init()}[/]")


def cmd_sync(_args):
    db.init()
    con.print("[dim]fetching fixtures[/]")
    try:
        fx = espn.fixtures()
        con.print(f"[green]{len(fx)} matches[/]")
        if len(fx):
            print(fx.to_string(index=False))
    except Exception as exc:  # network is optional
        con.print(f"[yellow]espn unreachable: {exc}[/]")


def cmd_matches(_args):
    con_ = db.connect()
    print(con_.execute(
        "SELECT match_id, team_a, team_b, start_utc FROM matches"
    ).df().to_string(index=False))


def cmd_build(args):
    settings().ensure_dirs()
    db.init()

    if args.demo or args.match_id == "demo":
        roster = demo_roster()
        match = dict(match_id="demo", venue="Wankhede Stadium, Mumbai",
                     team_a="MUM", team_b="CHE", pitch_class=args.pitch, fmt="T20")
    else:
        roster, match = _load_match(args.match_id)

    n_entries = args.entries or settings().sim.n_entries
    n_sims = settings().sim.n_sims
    n_field = min(settings().sim.n_field, 20000)  # keep demo interactive

    ref = datetime.now(ZoneInfo(settings().tz))
    marginals = P.fit_marginals(roster, {}, roster.proj, roster.sd, roster.p_dnb)
    sims, ids, corr, err = P.run(roster, marginals, match["pitch_class"], n_sims)
    con.print(f"[dim]sims {n_sims} · corr err {err:.4f}[/]")

    own = dict(zip(roster.player_id, roster.own_pct))
    summary = P.summarise(sims, ids, own)
    roster = roster.drop(columns=['proj', 'sd', 'boom', 'own_pct'], errors='ignore').merge(
        summary[["player_id", "proj", "sd", "boom", "own_pct", "leverage"]],
        on="player_id", how="left")

    ctx = Ctx.from_frame(roster)
    idx = {p: i for i, p in enumerate(ids)}
    rng = np.random.default_rng(11)
    field = F.build_field(ctx, n_field, rng)
    fsc = F.field_scores(field, sims, idx)
    con.print(f"[dim]field {len(field)} entries[/]")

    port = PF.build(ctx, sims, idx, fsc, n_entries, rng)
    if not port:
        con.print("[red]no legal lineups produced[/]")
        raise SystemExit(1)

    expo = dict(PF.exposure_report(port, ctx))
    roster["expo"] = roster.player_id.map(expo).fillna(0.0)

    out = write(payload(match, roster, port, corr, len(field), err))

    t = Table(title="top leverage")
    for c in ("player", "role", "proj", "own%", "lev", "expo"):
        t.add_column(c, justify="right" if c != "player" else "left")
    for r in roster.sort_values("leverage", ascending=False).head(12).itertuples():
        t.add_row(r.name, r.role, f"{r.proj:.1f}", f"{r.own_pct:.1f}",
                  f"{r.leverage:+.2f}", f"{r.expo * 100:.0f}%")
    con.print(t)

    best = max(e["p_rank1"] for e in port)
    con.print(f"[green]{len(port)} lineups · best P(rank 1) {best * 100:.2f}%[/]")
    con.print(f"[green]wrote {out}[/]")

    if args.open:
        webbrowser.open(f"file://{out.parent / 'dashboard.html'}")


def _load_match(match_id: str):
    con_ = db.connect()
    row = con_.execute("SELECT * FROM matches WHERE match_id = ?", [match_id]).df()
    if not len(row):
        raise SystemExit(f"unknown match {match_id}; run `edge sync` first")
    match = row.iloc[0].to_dict()
    roster = con_.execute(
        "SELECT * FROM players WHERE is_xi = TRUE").df()
    if not len(roster):
        raise SystemExit("no confirmed XI; run `edge watch` or `edge sync`")
    roster["own_pct"] = roster["player_id"].map(
        dict(zip(*con_.execute(
            "SELECT player_id, own_pct FROM ownership WHERE match_id = ?",
            [match_id]).df().values.T))).fillna(0.0)
    return roster, match


def cmd_backtest(args):
    from .backtest import run_backtest
    run_backtest(args.start, args.end)


def cmd_serve(_args):
    out = settings().web_dir / "dashboard.html"
    webbrowser.open(f"file://{out}")
    con.print(f"[green]{out}[/]")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="edge")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(fn=cmd_init)
    sub.add_parser("sync").set_defaults(fn=cmd_sync)
    sub.add_parser("matches").set_defaults(fn=cmd_matches)
    sub.add_parser("serve").set_defaults(fn=cmd_serve)

    b = sub.add_parser("build")
    b.add_argument("match_id", nargs="?", default="demo")
    b.add_argument("--demo", action="store_true")
    b.add_argument("--pitch", default="flat",
                   choices=["flat", "green_seam", "dry_turner", "slow_low"])
    b.add_argument("--entries", type=int)
    b.add_argument("--open", action="store_true")
    b.set_defaults(fn=cmd_build)

    w = sub.add_parser("watch")
    w.add_argument("match_id")
    w.add_argument("--entries", type=int)
    w.add_argument("--open", action="store_true")
    w.set_defaults(fn=cmd_build)

    t = sub.add_parser("backtest")
    t.add_argument("start")
    t.add_argument("end")
    t.set_defaults(fn=cmd_backtest)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    main()
