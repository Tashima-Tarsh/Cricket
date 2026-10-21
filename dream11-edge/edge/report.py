from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .config import settings


def payload(match: dict, roster, portfolio, corr, field_n: int, corr_err: float) -> dict:
    return dict(
        match=match,
        players=[
            dict(
                id=r.player_id, name=r.name, t=r.team, r=r.role,
                cr=float(r.credit), pos=int(getattr(r, "bat_pos", 5)),
                own=float(r.own_pct), proj=float(r.proj), sd=float(r.sd),
                boom=float(r.boom), lev=float(r.leverage), expo=float(getattr(r, "expo", 0.0)),
            )
            for r in roster.itertuples()
        ],
        portfolio=[
            dict(squad=e["squad"], cap=e["cap"], vic=e["vic"], p1=e["p_rank1"],
                 p10=e["p_top10"], p100=e["p_top100"], avg=e["avg_rank"])
            for e in portfolio
        ],
        corr=corr.tolist(),
        meta=dict(
            field=field_n,
            corr_err=round(float(corr_err), 4),
            sims=settings().sim.n_sims,
            generated=datetime.now().isoformat(timespec="seconds"),
        ),
    )


def write(p: dict) -> Path:
    settings().ensure_dirs()
    out = settings().web_dir / "players.json"
    out.write_text(json.dumps(p, indent=1))
    return out
