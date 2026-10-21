"""Dream11 player pool, credits, ownership.

No official public API. Strategy: app endpoint -> web scrape -> calibrated
ownership proxy from projections.
"""
from __future__ import annotations

import re

import pandas as pd
try:
    from selectolax.lexbor import LexborHTMLParser as HTMLParser
except ImportError:
    from selectolax.parser import HTMLParser

from .http import APP_UA, get_json, get_text

APP = "https://api.dream11.com"

_ROLE_MAP = {
    "wk": "WK", "wk-batsman": "WK", "keeper": "WK",
    "batsman": "BAT", "bat": "BAT", "batter": "BAT",
    "all-rounder": "AR", "allrounder": "AR", "ar": "AR",
    "bowler": "BOWL", "bowl": "BOWL",
}


def _role(raw: str) -> str:
    return _ROLE_MAP.get(str(raw).strip().lower(), "BAT")


def pool(match_id: str) -> pd.DataFrame:
    for fn in (_pool_app, _pool_web):
        try:
            df = fn(match_id)
            if df is not None and len(df) > 10:
                return df
        except Exception:
            continue
    return pd.DataFrame()


def _pool_app(match_id: str) -> pd.DataFrame:
    js = get_json(f"{APP}/api/v1/match/{match_id}/players",
                  params={"lang": "en"}, ua=APP_UA)
    data = js.get("data", js)
    rows = []
    for p in data.get("players", []):
        rows.append(dict(
            player_id=str(p.get("id")),
            name=p.get("name", ""),
            short_name=p.get("shortName") or p.get("name", ""),
            team=p.get("teamName", ""),
            role=_role(p.get("role", "")),
            credit=float(p.get("credit", 8.0)),
            overseas=bool(p.get("isOverseas")),
            own_pct=float(p.get("selectedBy") or 0.0),
            is_xi=bool(p.get("isPlaying")),
        ))
    return pd.DataFrame(rows)


def _pool_web(match_id: str) -> pd.DataFrame:
    tree = HTMLParser(get_text(f"https://www.dream11.com/cricket/match/{match_id}"))
    rows = []
    for node in tree.css("div[class*=playerCard], div[class*=player-card]"):
        txt = node.text(" ", strip=True)
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:Cr|credits)", txt, re.I)
        if not m:
            continue
        rows.append(dict(name=txt.split()[0], credit=float(m.group(1)),
                         role="BAT", team="", player_id=txt.split()[0],
                         short_name=txt.split()[0], overseas=False,
                         own_pct=0.0, is_xi=False))
    return pd.DataFrame(rows)


def proxy_ownership(proj: pd.Series, temperature: float = 18.0) -> pd.Series:
    """Calibrated softmax proxy.

    Deliberately over-weights the top of the curve: humans over-own stars
    relative to their true edge, which is the bias we want to model.
    """
    z = (proj - proj.mean()) / max(proj.std(), 1e-6)
    e = (z * temperature / 10.0).apply(lambda v: 2.718281828459045 ** v)
    return (100.0 * e / e.sum()).round(2)
