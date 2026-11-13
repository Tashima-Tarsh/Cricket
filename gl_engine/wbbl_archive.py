"""Reproducible, licensed WBBL-only Cricsheet archive synchronizer.

Downloads a public, attribution-licensed JSON archive with no paid key.
Never scrapes live scores, mislabels historical facts as today's conditions,
or replaces the last usable database after a failed synchronization.
"""
from __future__ import annotations

import io
import json
import os
import re
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import duckdb

CRICSHEET_WBBL_JSON = "https://cricsheet.org/downloads/wbb_json.zip"
LICENSE_URL = "https://cricsheet.org/licensing/"
_MAX_ARCHIVE = 25_000_000
_MAX_ENTRY = 3_000_000
_MAX_ENTRIES = 1800
_TEAMS = {
    "sydney sixers", "sydney thunder", "melbourne stars",
    "melbourne renegades", "brisbane heat", "perth scorchers",
    "adelaide strikers", "hobart hurricanes",
}


def _normal_team(value: str) -> str:
    return re.sub(r"(?i)\s+women(?:'s)?$", "", value).strip().casefold()


def download_wbbl_zip() -> bytes:
    req = Request(CRICSHEET_WBBL_JSON, headers={
        "User-Agent": "Cricket-WBBL-research-sync/1.0 (Cricsheet ODC-BY attribution)"
    })
    with urlopen(req, timeout=40) as res:
        if res.headers.get("Content-Length") and int(res.headers["Content-Length"]) > _MAX_ARCHIVE:
            raise ValueError("WBBL archive exceeds the maximum permitted size")
        payload = res.read(_MAX_ARCHIVE + 1)
    if len(payload) > _MAX_ARCHIVE:
        raise ValueError("WBBL archive exceeds the maximum permitted size")
    return payload


def build_wbbl_archive(payload: bytes, db_path: Path, minimum_matches: int = 100) -> dict:
    """Validate archive before atomically replacing target DuckDB file."""
    path = Path(db_path)
    if len(payload) > _MAX_ARCHIVE:
        raise ValueError("Archive exceeds size limit")
    matches = []
    balls = []
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        entries = [info for info in archive.infolist() if info.filename.lower().endswith(".json")]
        if len(entries) > _MAX_ENTRIES:
            raise ValueError("Archive has an implausible number of match files")
        if sum(x.file_size for x in entries) > _MAX_ENTRIES * _MAX_ENTRY:
            raise ValueError("Archive expands to an implausible size")
        for entry in entries:
            if entry.file_size > _MAX_ENTRY:
                raise ValueError("Oversized Cricsheet match file")
            match_id = Path(entry.filename).stem
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", match_id):
                continue
            raw = json.loads(archive.read(entry))
            info = raw.get("info") or {}
            genders = str(info.get("gender") or "").casefold()
            if genders and genders not in ("female", "women"):
                continue
            sides = info.get("teams") or []
            if len(sides) != 2 or any(_normal_team(t) not in _TEAMS for t in sides):
                continue
            dates = info.get("dates") or []
            if not dates:
                continue
            try:
                match_day = date.fromisoformat(str(dates[0]))
            except ValueError:
                continue
            rows = []
            for inning_index, inning in enumerate(raw.get("innings") or [], start=1):
                for over in inning.get("overs") or []:
                    for ball_index, event in enumerate(over.get("deliveries") or [], start=1):
                        batter = event.get("batter")
                        bowler = event.get("bowler")
                        if not batter or not bowler:
                            continue
                        wickets = event.get("wickets") or []
                        wicket = wickets[0] if wickets else {}
                        run = event.get("runs") or {}
                        extras = event.get("extras") or {}
                        rows.append((
                            match_id, batter, bowler, int(run.get("batter",0)),
                            int(run.get("total",0)), bool(wickets),
                            wicket.get("kind"), wicket.get("player_out"),
                            int(over.get("over",0)), ball_index,
                            not (extras.get("wides") or extras.get("noballs")),
                            inning_index,
                        ))
            if not rows:
                continue
            matches.append((
                match_id, match_day.isoformat(), sides[0], sides[1],
                "Women's Big Bash League", info.get("venue"),
            ))
            balls.extend(rows)
    if len(matches) < minimum_matches:
        raise ValueError(
            f"Archive contains only {len(matches)} WBBL matches; "
            f"minimum required is {minimum_matches}"
        )
    if len({m[0] for m in matches}) != len(matches):
        raise ValueError("Duplicate Cricsheet match ID in downloaded archive")
    if not balls:
        raise ValueError("Archive contains no deliveries")

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".building")
    if temporary.exists():
        temporary.unlink()
    try:
        with duckdb.connect(str(temporary)) as db:
            db.execute("""CREATE TABLE matches (
                 match_id VARCHAR PRIMARY KEY, match_date DATE, team1 VARCHAR,
                 team2 VARCHAR, competition VARCHAR, venue VARCHAR)""")
            db.execute("""CREATE TABLE deliveries (
                 match_id VARCHAR, batter VARCHAR, bowler VARCHAR, runs_batter INTEGER,
                 runs_total INTEGER, is_wicket BOOLEAN, wicket_type VARCHAR,
                 player_dismissed VARCHAR, over INTEGER, ball INTEGER,
                 is_legal_ball BOOLEAN, innings INTEGER)""")
            db.executemany("INSERT INTO matches VALUES (?,?,?,?,?,?)", matches)
            for i in range(0, len(balls), 10000):
                db.executemany("INSERT INTO deliveries VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                               balls[i:i+10000])
            db.execute("CREATE INDEX match_ball_index ON deliveries(match_id)")
            db.execute("CREATE INDEX batter_ball_index ON deliveries(batter)")
            db.execute("CREATE INDEX bowler_ball_index ON deliveries(bowler)")
            db.execute("""CREATE TABLE archive_metadata(
               source_url VARCHAR, license_url VARCHAR, synced_at_utc TIMESTAMP,
               match_count INTEGER, delivery_count INTEGER)""")
            db.execute("INSERT INTO archive_metadata VALUES (?,?,?,?,?)", (
                CRICSHEET_WBBL_JSON, LICENSE_URL, datetime.now(timezone.utc).isoformat(),
                len(matches), len(balls)))
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"status": "ARCHIVE_SYNCED", "match_count": len(matches),
            "recorded_deliveries": len(balls), "path": str(path),
            "source": CRICSHEET_WBBL_JSON, "license": LICENSE_URL,
            "historical_only": True}


def sync_wbbl_archive(db_path: Path | None = None) -> dict:
    output = db_path or Path(os.getenv("CRICKET_WBBL_DB", "/app/var/wbbl.duckdb"))
    return build_wbbl_archive(download_wbbl_zip(), Path(output))
