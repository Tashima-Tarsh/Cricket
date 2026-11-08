from __future__ import annotations
import argparse, sys, webbrowser
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from rich.console import Console
from rich.table import Table
from . import db
from .config import settings
from .pipeline import build_match, demo_roster
from .report import payload, write, portfolio_csv

con = Console()


def cmd_init(_):
    con.print(f"[green]db at {db.init()}[/]")


def cmd_sync(_):
    db.init()
    from .ingest import espn
    try:
        fx = espn.fixtures()
        con.print(f"[green]{len(fx)} fixtures[/]")
        if len(fx):
            print(fx.to_string(index=False))
    except Exception as e:
        con.print(f"[yellow]offline: {e}[/]")


def cmd_build(args):
    settings().ensure_dirs()
    db.init()
    demo = args.demo or args.match_id == "demo"
    roster = demo_roster()
    match = dict(match_id="demo", venue="Wankhede Stadium, Mumbai", team_a="MUM",
                 team_b="CHE", pitch_class=args.pitch, fmt="T20")

    n_field = args.field or (20000 if demo else None)
    res = build_match(roster, match, n_sims=args.sims, n_field=n_field,
                      n_entries=args.entries, risk=args.risk,
                      progress=lambda s: con.print(f"[dim]{s}…[/]"))
    port, ros = res["portfolio"], res["roster"]

    t = Table(title="top leverage")
    for c in ("player","role","proj","sd","own%","lev","expo"):
        t.add_column(c, justify="right" if c != "player" else "left")
    for r in ros.sort_values("leverage", ascending=False).head(12).itertuples():
        t.add_row(r.name, r.role, f"{r.proj:.1f}", f"{r.sd:.1f}", f"{r.own_pct:.1f}",
                  f"{r.leverage:+.2f}", f"{r.expo*100:.0f}%")
    con.print(t)

    out = write(payload(match, ros, port, res["corr"], res["field_n"], res["err"]))
    (settings().web_dir / "portfolio.csv").write_text(portfolio_csv(port, ros))
    best = max((e["p_rank1"] for e in port), default=0.0)
    con.print(f"[green]{len(port)} lineups · best P(rank 1) {best*100:.2f}% · "
              f"corr err {res['err']:.4f}[/]")
    con.print(f"[green]wrote {out}[/]")
    if args.open:
        webbrowser.open(f"file://{out.parent / 'dashboard.html'}")


def cmd_watch(args):
    from .live.watcher import wait_for_xi
    con.print("[dim]waiting for toss + XI…[/]")
    m = dict(match_id=args.match_id, series_id=args.series or "", slug=args.slug or "")
    info = wait_for_xi(m)
    if not info:
        con.print("[yellow]no toss within window[/]")
        return
    con.print(f"[green]toss: {info['toss']['winner']} chose to "
              f"{info['toss']['decision']} · pitch {info['pitch_class']}[/]")
    args.pitch = info["pitch_class"]
    args.demo = True
    cmd_build(args)


def cmd_backtest(args):
    from .backtest import run_backtest
    run_backtest(args.start, args.end, demo=args.demo)


def cmd_serve(_):
    p = settings().web_dir / "dashboard.html"
    webbrowser.open(f"file://{p}")
    con.print(f"[green]{p}[/]")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="edge")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("init", "sync", "serve"):
        sub.add_parser(n).set_defaults(fn={"init": cmd_init, "sync": cmd_sync,
                                          "serve": cmd_serve}[n])

    def common(p):
        p.add_argument("--pitch", default="flat",
                       choices=["flat","green_seam","dry_turner","slow_low"])
        p.add_argument("--entries", type=int)
        p.add_argument("--sims", type=int)
        p.add_argument("--field", type=int)
        p.add_argument("--risk", type=float, default=0.0)
        p.add_argument("--open", action="store_true")

    b = sub.add_parser("build")
    b.add_argument("match_id", nargs="?", default="demo")
    b.add_argument("--demo", action="store_true")
    common(b)
    b.set_defaults(fn=cmd_build)

    w = sub.add_parser("watch")
    w.add_argument("match_id")
    w.add_argument("--series")
    w.add_argument("--slug")
    common(w)
    w.set_defaults(fn=cmd_watch)

    t = sub.add_parser("backtest")
    t.add_argument("start", nargs="?", default=None)
    t.add_argument("end", nargs="?", default=None)
    t.add_argument("--demo", action="store_true")
    t.set_defaults(fn=cmd_backtest)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    main()
