from __future__ import annotations
import re
import pandas as pd
try:
    from selectolax.lexbor import LexborHTMLParser as HTMLParser
except ImportError:
    from selectolax.parser import HTMLParser
from .http import APP_UA, get_json, get_text

APP = "https://api.dream11.com"
_RM = {"wk":"WK","wk-batsman":"WK","keeper":"WK","batsman":"BAT","bat":"BAT",
       "batter":"BAT","all-rounder":"AR","allrounder":"AR","ar":"AR",
       "bowler":"BOWL","bowl":"BOWL"}


def _role(r):
    return _RM.get(str(r).strip().lower(), "BAT")


def pool(match_id):
    for fn in (_app, _web):
        try:
            d = fn(match_id)
            if d is not None and len(d) > 10:
                return d
        except Exception:
            continue
    return pd.DataFrame()


def _app(match_id):
    js = get_json(f"{APP}/api/v1/match/{match_id}/players",
                  params={"lang": "en"}, ua=APP_UA)
    rows = []
    for p in js.get("data", js).get("players", []):
        rows.append(dict(player_id=str(p.get("id")), name=p.get("name", ""),
                         team=p.get("teamName", ""), role=_role(p.get("role", "")),
                         credit=float(p.get("credit", 8.0)),
                         overseas=bool(p.get("isOverseas")),
                         own_pct=float(p.get("selectedBy") or 0.0),
                         is_xi=bool(p.get("isPlaying")), bat_pos=6, bowl_style=""))
    return pd.DataFrame(rows)


def _web(match_id):
    tree = HTMLParser(get_text(f"https://www.dream11.com/cricket/match/{match_id}"))
    rows = []
    for n in tree.css("div[class*=playerCard], div[class*=player-card]"):
        t = n.text(" ", strip=True)
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:Cr|credits)", t, re.I)
        if not m:
            continue
        nm = t.split()[0]
        rows.append(dict(player_id=nm, name=nm, team="", role="BAT",
                         credit=float(m.group(1)), overseas=False,
                         own_pct=0.0, is_xi=False, bat_pos=6, bowl_style=""))
    return pd.DataFrame(rows)


def proxy_ownership(proj, temperature=18.0):
    """Calibrated softmax. Deliberately over-weights the top of the curve
    because humans over-own stars relative to their true edge."""
    z = (proj - proj.mean()) / max(proj.std(), 1e-6)
    e = (z * temperature / 10.0).apply(lambda v: 2.718281828459045 ** v)
    return (100.0 * e / e.sum()).round(2)
