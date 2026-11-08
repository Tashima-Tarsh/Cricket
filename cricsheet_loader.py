"""
Cricsheet data loader.
Downloads and parses real ball-by-ball CSV data from https://cricsheet.org/
Caches downloads locally and falls back to synthetic data when offline.
"""
import os
import io
import csv
import zipfile
import glob
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import requests

logger = logging.getLogger(__name__)

# Cricsheet download endpoints (men's international ball-by-ball CSV)
# Multiple candidate URLs since cricsheet.org occasionally changes paths.
CRICSHEET_URLS = {
    "international_men": [
        "https://cricsheet.org/downloads/icsv.zip",
        "https://cricsheet.org/downloads/cricsheet_icsv.zip",
        "https://cricsheet.org/downloads/icsv_mens.zip",
    ],
    "international_women": [
        "https://cricsheet.org/downloads/icsv_women.zip",
        "https://cricsheet.org/downloads/cricsheet_icsv_women.zip",
    ],
    "ipl": [
        "https://cricsheet.org/downloads/ipl_csv.zip",
        "https://cricsheet.org/downloads/ipl.zip",
    ],
}

DEFAULT_CACHE_DIR = Path.home() / ".fantasy_cricket_engine" / "cricsheet_cache"
REQUEST_TIMEOUT = 60
DOWNLOAD_RETRIES = 3
DOWNLOAD_BACKOFF = 2


class CricsheetLoader:
    """Downloads and parses Cricsheet ball-by-ball CSV data."""

    def __init__(self, cache_dir: Optional[str | Path] = None):
        self.cache_dir = Path(cache_dir or DEFAULT_CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "FantasyCricketEngine/1.0 (educational)"}
        )

    def _download(self, url: str, dest: Path) -> bool:
        """Download a URL with retries and exponential backoff."""
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

    def fetch_batter_data(
        self, source: str = "international_men", force_refresh: bool = False
    ) -> Optional[Path]:
        """Fetch a Cricsheet ZIP archive and return the local ZIP path."""
        candidates = CRICSHEET_URLS.get(source)
        if not candidates:
            raise ValueError(f"Unknown source '{source}'. Options: {list(CRICSHEET_URLS)}")
        if isinstance(candidates, str):
            candidates = [candidates]

        zip_path = self.cache_dir / f"{source}.zip"
        if zip_path.exists() and not force_refresh:
            age = datetime.now() - datetime.fromtimestamp(zip_path.stat().st_mtime)
            if age < timedelta(days=1):
                logger.info("Using cached Cricsheet data: %s", zip_path)
                return zip_path

        for url in candidates:
            ok = self._download(url, zip_path)
            if ok:
                return zip_path
            # Remove failed partial download before trying next URL
            if zip_path.exists():
                zip_path.unlink(missing_ok=True)

        logger.error("All Cricsheet URLs failed for source '%s'", source)
        return None

    def extract_and_parse(
        self, zip_path: Path, max_matches: Optional[int] = None
    ) -> pd.DataFrame:
        """Extract a Cricsheet ZIP and parse all match CSVs into a flat DataFrame."""
        records: List[Dict] = []
        extract_dir = self.cache_dir / f"{zip_path.stem}_extracted"
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

    def _parse_match_csv(self, csv_path: str) -> List[Dict]:
        """Parse a single Cricsheet match CSV into per-ball records."""
        records: List[Dict] = []
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(self._normalize_ball_row(row))
        return records

    def _normalize_ball_row(self, row: Dict[str, str]) -> Dict:
        """Map Cricsheet CSV columns to a common schema."""
        def col(*names: str) -> str:
            for n in names:
                if n in row and row[n] not in (None, ""):
                    return row[n]
            return ""

        batter = col("batter", "batsman")
        bowler = col("bowler")
        non_striker = col("non_striker")
        runs_batter = self._safe_int(col("batter_runs", "runs_batter", "runs_off_bat"))
        runs_extra = self._safe_int(col("extras_runs", "extras"))
        runs_total = runs_batter + runs_extra
        wicket = col("wicket", "wicket_type", "dismissal")
        is_wicket = 1 if wicket else 0
        fielder = col("fielder", "catcher", "fielder_involved")
        over = self._safe_float(col("over", "ball_over"))
        ball = self._safe_float(col("ball", "ball_in_over"))
        innings = col("innings", "inning")
        match_id = col("match_id", "matchid", "id")
        date = col("date", "match_date")
        team_batting = col("batting_team", "bat_team")
        team_bowling = col("bowling_team", "bowl_team")

        return {
            "match_id": match_id,
            "date": date,
            "innings": innings,
            "over": over,
            "ball": ball,
            "batter": batter,
            "non_striker": non_striker,
            "bowler": bowler,
            "fielder": fielder,
            "runs_batter": runs_batter,
            "runs_extra": runs_extra,
            "runs_total": runs_total,
            "is_wicket": is_wicket,
            "wicket_type": wicket,
            "batting_team": team_batting,
            "bowling_team": team_bowling,
        }

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

    def load_historical(
        self,
        source: str = "international_men",
        max_matches: Optional[int] = None,
        use_synthetic_fallback: bool = True,
    ) -> pd.DataFrame:
        """Load historical ball-by-ball data, downloading from Cricsheet if needed."""
        zip_path = self.fetch_batter_data(source=source)
        if zip_path:
            df = self.extract_and_parse(zip_path, max_matches=max_matches)
            if not df.empty:
                return df

        if use_synthetic_fallback:
            logger.warning("Cricsheet data unavailable; using synthetic fallback")
            from data_loader import generate_sample_historical_data

            return generate_sample_historical_data(n_matches=50)

        return pd.DataFrame()


def load_historical_cricsheet(
    source: str = "international_men",
    max_matches: Optional[int] = None,
    cache_dir: Optional[str | Path] = None,
) -> pd.DataFrame:
    """Convenience function to load Cricsheet historical data."""
    loader = CricsheetLoader(cache_dir=cache_dir)
    return loader.load_historical(source=source, max_matches=max_matches)
