"""Cricsheet: free ball-by-ball corpus. The training set."""
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import httpx
import pandas as pd

from ..config import settings

URLS = {
    "ipl": "https://cricsheet.org/downloads/ipl_json.zip",
    "t20i": "https://cricsheet.org/downloads/t20s_male_json.zip",
    "odis": "https://cricsheet.org/downloads/odis_male_json.zip",
}


def download(which: str = "ipl", force: bool = False) -> Path:
    dest = settings().data_dir / f"cricsheet_{which}"
    if dest.exists() and any(dest.glob("*.json")) and not force:
        return dest
    dest.mkdir(parents=True, exist_ok=True)
    r = httpx.get(URLS[which], timeout=300, follow_redirects=True)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(dest)
    return dest


def parse(which: str = "ipl") -> pd.DataFrame:
    root = download(which)
    rows = []
    for f in sorted(root.glob("*.json")):
        if f.name.startswith("_"):
            continue
        try:
            m = json.loads(f.read_text())
        except Exception:
            continue
        mid = f.stem
        date = (m.get("info") or {}).get("dates", [None])[0]
        venue = (m.get("info") or {}).get("venue", "")
        for inn in m.get("innings", []):
            for ov in inn.get("overs", []):
                for i, d in enumerate(ov.get("deliveries", []), start=1):
                    runs = d["runs"]["batter"]
                    rows.append(dict(
                        match_id=mid, innings=inn.get("team", ""),
                        over=ov["over"], ball=i,
                        batter_id=d["batter"], bowler_id=d["bowler"],
                        bat_style="", bowl_style="", runs=runs,
                        outcome=_outcome(d, runs),
                        phase="pp" if ov["over"] < 6 else "mid" if ov["over"] < 16 else "death",
                        venue=venue, fmt=which, match_date=date,
                    ))
    return pd.DataFrame(rows)


def _outcome(d: dict, runs: int) -> str:
    if d.get("wickets"):
        return "W"
    ex = d.get("extras", {})
    if "wides" in ex:
        return "wd"
    if "noballs" in ex:
        return "nb"
    return str(runs)
