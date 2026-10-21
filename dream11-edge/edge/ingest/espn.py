"""ESPNcricinfo consumer JSON API.

Undocumented but stable. If a shape changes, adjust here only.
"""
from __future__ import annotations

import pandas as pd

from .http import get_json

BASE = "https://hs-consumer-api.espncricinfo.com/v1/pages"
CDN = "https://site.api.espn.com/apis/site/v2/sports/cricket"

IPL_LEAGUE = "8039"


def fixtures(date: str | None = None, league: str = IPL_LEAGUE) -> pd.DataFrame:
    js = get_json(f"{CDN}/{league}/scoreboard",
                  params={"dates": date} if date else None)
    rows = []
    for e in js.get("events", []):
        comp = (e.get("competitions") or [{}])[0]
        teams = comp.get("competitors", [])
        rows.append(dict(
            match_id=str(e.get("id")),
            series_id=str((comp.get("series") or {}).get("uid", "")),
            fmt="T20",
            venue=(comp.get("venue") or {}).get("fullName", ""),
            team_a=teams[0]["team"]["displayName"] if len(teams) > 0 else "",
            team_b=teams[1]["team"]["displayName"] if len(teams) > 1 else "",
            start_utc=e.get("date"),
            status=((e.get("status") or {}).get("type") or {}).get("description", ""),
        ))
    return pd.DataFrame(rows)


def match_home(series_id: str, match_id: str) -> dict:
    return get_json(f"{BASE}/match/home",
                    params={"lang": "en", "seriesId": series_id, "matchId": match_id})


def playing_xi(series_id: str, match_id: str) -> dict:
    """{team_name: [player_name, ...]}. Empty until the toss."""
    js = match_home(series_id, match_id)
    out = {}
    for team in (js.get("match") or {}).get("teams", []):
        names = []
        for p in team.get("players", []):
            if not p.get("isPlaying"):
                continue
            pl = p.get("player") or {}
            nm = pl.get("longName") or pl.get("name")
            if nm:
                names.append(nm)
        if names:
            out[(team.get("team") or {}).get("longName", "")] = names
    return out


def ball_by_ball(series_id: str, match_id: str, innings: int) -> pd.DataFrame:
    js = get_json(f"{BASE}/match/ball-by-ball",
                  params={"lang": "en", "seriesId": series_id,
                          "matchId": match_id, "inningsNumber": innings})
    rows = []
    for inn in (js.get("content") or {}).get("innings", []):
        for ov in inn.get("overs", []):
            for d in ov.get("balls", []):
                bat = (d.get("batter") or {}).get("player") or {}
                bowl = (d.get("bowler") or {}).get("player") or {}
                rows.append(dict(
                    over=d.get("overNumber"), ball=d.get("ballNumber"),
                    batter_id=str(bat.get("id", "")), bowler_id=str(bowl.get("id", "")),
                    bat_style=bat.get("battingStyle", ""),
                    bowl_style=bowl.get("bowlingStyle", ""),
                    runs=d.get("runs", 0),
                    outcome=d.get("shotType") or d.get("dismissalType") or "0",
                ))
    return pd.DataFrame(rows)
