"""
Cricsheet BBL/WBBL data loader.
Attempts to download real ball-by-ball CSV data from Cricsheet.org,
caches it locally, and falls back to synthetic data when offline
or when the Cricsheet download path is unavailable.
"""
import glob
import logging
import os
import time
import zipfile
from pathlib import Path
from typing import List, Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# Cricsheet Big Bash download endpoints (candidates; cricsheet.org changes paths)
CRICSHEET_URLS = [
    "https://cricsheet.org/downloads/bbl_csv.zip",
    "https://cricsheet.org/downloads/bbl.zip",
    "https://cricsheet.org/downloads/icsv_bbl.zip",
    "https://cricsheet.org/downloads/wbbl_csv.zip",
    "https://cricsheet.org/downloads/wbbl.zip",
]

DEFAULT_CACHE_DIR = Path.home() / ".bbl_wbbl_engine" / "cricsheet_cache"
REQUEST_TIMEOUT = 60
DOWNLOAD_RETRIES = 3
DOWNLOAD_BACKOFF = 2


class CricsheetLoader:
    def __init__(self, cache_dir: Optional[str | Path] = None):
        self.cache_dir = Path(cache_dir or DEFAULT_CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "BBLWBBLFantasyEngine/1.0 (educational)"}
        )

    def _download(self, url: str, dest: Path) -> bool:
        for attempt in range(1, DOWNLOAD_RETRIES + 1):
            try:
                logger.info("Downloading %s (attempt %d/%d)", url, attempt, DOWNLOAD_RETRIES)
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT, stream=True)
                resp.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.info("Saved %s (%d bytes)", dest, dest.stat().st_size)
                return True
            except Exception as exc:  # noqa: BLE001
                logger.warning("Download attempt %d failed: %s", attempt, exc)
                if attempt < DOWNLOAD_RETRIES:
                    time.sleep(DOWNLOAD_BACKOFF ** attempt)
        logger.error("Failed to download %s after %d attempts", url, DOWNLOAD_RETRIES)
        return False

    def fetch_zip(self, force_refresh: bool = False) -> Optional[Path]:
        zip_path = self.cache_dir / "bbl_wbbl.zip"
        if zip_path.exists() and not force_refresh:
            logger.info("Using cached Cricsheet data: %s", zip_path)
            return zip_path

        for url in CRICSHEET_URLS:
            if self._download(url, zip_path):
                return zip_path
            if zip_path.exists():
                zip_path.unlink(missing_ok=True)

        logger.error("All Cricsheet URLs failed; will use synthetic fallback")
        return None

    def extract_and_parse(self, zip_path: Path, max_matches: Optional[int] = None) -> pd.DataFrame:
        records: List[dict] = []
        extract_dir = self.cache_dir / "bbl_extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        csv_files = sorted(glob.glob(str(extract_dir / "*.csv")))
        if max_matches:
            csv_files = csv_files[:max_matches]

        for csv_path in csv_files:
            try:
                match_records = self._parse_match_csv(csv_path)
                records.extend(match_records)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Skipping %s: %s", csv_path, exc)

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        logger.info("Parsed %d ball-by-ball records from %d matches", len(df), len(csv_files))
        return df

    def _parse_match_csv(self, csv_path: str) -> List[dict]:
        """Parse a Cricsheet iCSV match file (version 1.9.0 format)."""
        records: List[dict] = []
        match_id = None
        date = None
        teams: List[str] = []
        with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                tag = parts[0]

                if tag == "info":
                    if len(parts) >= 3:
                        key, val = parts[1], parts[2]
                        if key == "match_id":
                            match_id = val
                        elif key == "date":
                            date = val
                        elif key == "team" and val not in teams:
                            teams.append(val)
                    continue

                if tag != "ball" or len(parts) < 9:
                    continue

                # Determine bowling team (the team not batting)
                batting_team = parts[3] if len(parts) > 3 else ""
                bowling_team = ""
                if len(teams) == 2:
                    bowling_team = teams[1] if batting_team == teams[0] else teams[0]

                over_ball = parts[2]
                try:
                    over_str, ball_str = over_ball.split(".")
                    over_val = float(over_str)
                    ball_val = float(ball_str)
                except (ValueError, AttributeError):
                    over_val = 0.0
                    ball_val = 0.0

                runs_batter = self._safe_int(parts[7]) if len(parts) > 7 else 0
                runs_extra = self._safe_int(parts[8]) if len(parts) > 8 else 0
                wicket_type = parts[14].strip('"') if len(parts) > 14 else ""
                is_wicket = 1 if wicket_type else 0

                records.append({
                    "match_id": match_id or os.path.basename(csv_path).replace(".csv", ""),
                    "date": date or "",
                    "innings": parts[1] if len(parts) > 1 else "1",
                    "over": over_val,
                    "ball": ball_val,
                    "batter": parts[4] if len(parts) > 4 else "",
                    "non_striker": parts[5] if len(parts) > 5 else "",
                    "bowler": parts[6] if len(parts) > 6 else "",
                    "fielder": parts[15].strip('"') if len(parts) > 15 else "",
                    "runs_batter": runs_batter,
                    "runs_extra": runs_extra,
                    "runs_total": runs_batter + runs_extra,
                    "is_wicket": is_wicket,
                    "wicket_type": wicket_type,
                    "batting_team": batting_team,
                    "bowling_team": bowling_team,
                })
        return records

    @staticmethod
    def _safe_int(val: str) -> int:
        try:
            return int(float(val))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _safe_float(val: str) -> float:
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    def load_bbl_data(
        self,
        max_matches: Optional[int] = None,
        use_synthetic_fallback: bool = True,
    ) -> pd.DataFrame:
        zip_path = self.fetch_zip()
        if zip_path:
            df = self.extract_and_parse(zip_path, max_matches=max_matches)
            if not df.empty:
                # compute runs_total
                df["runs_total"] = df["runs_batter"] + df["runs_extra"]
                return df

        if use_synthetic_fallback:
            logger.warning("Cricsheet data unavailable; using synthetic BBL fallback")
            return generate_sample_bbl_data(max_matches or 100)

        return pd.DataFrame()


def load_bbl_data(
    max_matches: Optional[int] = None,
    cache_dir: Optional[str | Path] = None,
    use_synthetic_fallback: bool = True,
) -> pd.DataFrame:
    loader = CricsheetLoader(cache_dir=cache_dir)
    return loader.load_bbl_data(
        max_matches=max_matches, use_synthetic_fallback=use_synthetic_fallback
    )


# ---------------------------------------------------------------------------
# Synthetic fallback data (BBL/WBBL style)
# ---------------------------------------------------------------------------

BBL_PLAYERS = [
    {"name": "Steve_Smith", "role": "BAT", "team": "Sydney Sixers", "skill": 92},
    {"name": "David_Warner", "role": "BAT", "team": "Sydney Thunder", "skill": 88},
    {"name": "Glenn_Maxwell", "role": "AR", "team": "Melbourne Stars", "skill": 85},
    {"name": "Marcus_Stoinis", "role": "AR", "team": "Melbourne Stars", "skill": 82},
    {"name": "Rashid_Khan", "role": "BOWL", "team": "Adelaide Strikers", "skill": 90},
    {"name": "Pat_Cummins", "role": "BOWL", "team": "Sydney Thunder", "skill": 89},
    {"name": "Josh_Hazlewood", "role": "BOWL", "team": "Sydney Sixers", "skill": 87},
    {"name": "Adam_Zampa", "role": "BOWL", "team": "Sydney Sixers", "skill": 86},
    {"name": "Matthew_Wade", "role": "WK", "team": "Hobart Hurricanes", "skill": 80},
    {"name": "Alex_Carey", "role": "WK", "team": "Adelaide Strikers", "skill": 78},
    {"name": "Nick_Madron", "role": "WK", "team": "Perth Scorchers", "skill": 79},
    {"name": "Tim_David", "role": "BAT", "team": "Perth Scorchers", "skill": 81},
    {"name": "Colin_Munro", "role": "BAT", "team": "Perth Scorchers", "skill": 83},
    {"name": "Chris_Lynn", "role": "BAT", "team": "Brisbane Heat", "skill": 79},
    {"name": "Ben_McDermott", "role": "BAT", "team": "Hobart Hurricanes", "skill": 80},
    {"name": "D'Arcy_Short", "role": "AR", "team": "Hobart Hurricanes", "skill": 77},
    {"name": "Ashton_Turner", "role": "AR", "team": "Perth Scorchers", "skill": 76},
    {"name": "Nathan_Coulter_Nile", "role": "BOWL", "team": "Melbourne Stars", "skill": 83},
    {"name": "Jason_Behrendorff", "role": "BOWL", "team": "Perth Scorchers", "skill": 81},
    {"name": "Kane_Richardson", "role": "BOWL", "team": "Melbourne Renegades", "skill": 80},
]

VENUES = ["MCG", "Perth_Stadium", "Adelaide_Oval", "SCG", "Gabba", "Marvel_Stadium"]


def generate_sample_bbl_data(n_matches: int = 100) -> pd.DataFrame:
    import numpy as np

    np.random.seed(42)
    records: List[dict] = []
    venues = VENUES

    for match_id in range(n_matches):
        venue = np.random.choice(venues)
        # Two teams per match
        team_a = "Sydney Sixers"
        team_b = "Perth Scorchers"
        players = [
            p for p in BBL_PLAYERS if p["team"] in (team_a, team_b)
        ]
        for p in players:
            # Simulate a few balls per player per match
            for _ in range(np.random.randint(1, 6)):
                base = p["skill"] * 0.5
                venue_bonus = np.random.uniform(-5, 10)
                noise = np.random.normal(0, 12)
                fantasy_points = max(0, base + venue_bonus + noise)
                runs_batter = int(np.random.poisson(2))
                is_wicket = 1 if np.random.random() < 0.08 else 0
                records.append({
                    "match_id": match_id,
                    "date": "2026-01-01",
                    "innings": 1,
                    "over": float(np.random.randint(1, 21)),
                    "ball": 1.0,
                    "batter": p["name"],
                    "non_striker": "",
                    "bowler": p["name"],
                    "fielder": "",
                    "runs_batter": runs_batter,
                    "runs_extra": 0,
                    "runs_total": runs_batter,
                    "is_wicket": is_wicket,
                    "wicket_type": "caught" if is_wicket else "",
                    "batting_team": p["team"],
                    "bowling_team": team_b if p["team"] == team_a else team_a,
                    "player": p["name"],
                    "role": p["role"],
                    "skill_rating": p["skill"],
                    "venue": venue,
                    "fantasy_points": round(fantasy_points, 2),
                })

    return pd.DataFrame(records)
