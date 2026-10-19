"""Cricsheet Historical Match Database Ingestion, Parsing, and Feature Engineering.
Fetches, unzips, and parses ball-by-ball T20 and IPL match data from https://cricsheet.org/downloads/.
Computes official Dream11 fantasy points and compiles historical training datasets for XGBoost.
"""

import os
import json
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import requests
import pandas as pd
import numpy as np


CRICSHEET_URLS = {
    "ipl_json": "https://cricsheet.org/downloads/ipl_json.zip",
    "t20s_json": "https://cricsheet.org/downloads/t20s_json.zip",
    "it20s_json": "https://cricsheet.org/downloads/it20s_json.zip",
}


class CricsheetDatabase:
    def __init__(self, data_dir: Optional[str] = None):
        if not data_dir:
            data_dir = str(Path(__file__).parent.parent / "data" / "cricsheet")
        self.data_dir = Path(data_dir)
        self.matches_dir = self.data_dir / "matches"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.matches_dir.mkdir(parents=True, exist_ok=True)

    def download_dataset(self, dataset_key: str = "ipl_json", limit_matches: int = 50) -> int:
        """Downloads and extracts a Cricsheet dataset. Returns number of matches available."""
        url = CRICSHEET_URLS.get(dataset_key, CRICSHEET_URLS["ipl_json"])
        zip_path = self.data_dir / f"{dataset_key}.zip"

        if not zip_path.exists() or zip_path.stat().st_size == 0:
            print(f"Downloading Cricsheet dataset '{dataset_key}' from {url}...")
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded {zip_path.stat().st_size / (1024*1024):.2f} MB.")

        print(f"Extracting up to {limit_matches} matches from {zip_path.name}...")
        extracted_count = 0
        with zipfile.ZipFile(zip_path, "r") as z:
            json_files = [f for f in z.namelist() if f.endswith(".json")]
            for filename in json_files[:limit_matches]:
                dest_file = self.matches_dir / Path(filename).name
                if not dest_file.exists():
                    z.extract(filename, str(self.matches_dir.parent))
                    # If extracted in subfolder or flat
                    extracted_path = self.matches_dir.parent / filename
                    if extracted_path.exists() and extracted_path != dest_file:
                        dest_file.write_bytes(extracted_path.read_bytes())
                extracted_count += 1

        total_extracted = len(list(self.matches_dir.glob("*.json")))
        print(f"Extraction complete. Total match files in {self.matches_dir}: {total_extracted}")
        return total_extracted

    def list_matches(self) -> List[Dict[str, Any]]:
        """Returns metadata for all extracted matches."""
        matches = []
        for file_path in self.matches_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                info = data.get("info", {})
                matches.append({
                    "match_id": file_path.stem,
                    "date": info.get("dates", ["Unknown"])[0],
                    "teams": info.get("teams", []),
                    "venue": info.get("venue", "Unknown"),
                    "city": info.get("city", "Unknown"),
                    "match_type": info.get("match_type", "T20"),
                    "winner": info.get("outcome", {}).get("winner", "No Result"),
                    "file_path": str(file_path)
                })
            except Exception:
                continue
        matches.sort(key=lambda x: str(x["date"]), reverse=True)
        return matches

    def parse_match(self, match_id_or_path: str) -> Dict[str, Any]:
        """Parses ball-by-ball Cricsheet match JSON into innings summaries and player box scores."""
        path = Path(match_id_or_path)
        if not path.exists():
            path = self.matches_dir / f"{match_id_or_path}.json"
        if not path.exists():
            raise FileNotFoundError(f"Match file not found: {match_id_or_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        info = data.get("info", {})
        innings_list = data.get("innings", [])

        player_stats: Dict[str, Dict[str, Any]] = {}

        # Initialize players registered in match info
        registry = info.get("players", {})
        for team, players in registry.items():
            for p in players:
                player_stats[p] = {
                    "player": p,
                    "team": team,
                    # Batting
                    "runs": 0,
                    "balls_faced": 0,
                    "fours": 0,
                    "sixes": 0,
                    "is_out": False,
                    "dismissal_kind": None,
                    "batting_position": None,
                    # Bowling
                    "balls_bowled": 0,
                    "runs_conceded": 0,
                    "wickets": 0,
                    "maidens": 0,
                    "bowled_or_lbw": 0,
                    "dot_balls": 0,
                    # Fielding
                    "catches": 0,
                    "stumpings": 0,
                    "run_outs": 0,
                }

        batting_order_tracker = {team: 1 for team in registry.keys()}

        for inn_idx, inn in enumerate(innings_list):
            team_batting = inn.get("team")
            overs = inn.get("overs", [])

            for over_data in overs:
                over_num = over_data.get("over", 0)
                deliveries = over_data.get("deliveries", [])
                over_runs = 0
                legal_balls = 0

                for delivery in deliveries:
                    batter = delivery.get("batter")
                    bowler = delivery.get("bowler")
                    runs_dict = delivery.get("runs", {})
                    batter_runs = runs_dict.get("batter", 0)
                    extras = runs_dict.get("extras", 0)
                    total_delivery_runs = runs_dict.get("total", 0)
                    is_wicket = "wickets" in delivery

                    # Ensure batter in stats
                    if batter not in player_stats:
                        player_stats[batter] = self._empty_player_dict(batter, team_batting)
                    b_entry = player_stats[batter]
                    if b_entry["batting_position"] is None:
                        curr_pos = batting_order_tracker.get(team_batting, 1)
                        b_entry["batting_position"] = curr_pos
                        batting_order_tracker[team_batting] = curr_pos + 1

                    b_entry["runs"] += batter_runs
                    b_entry["balls_faced"] += 1
                    if batter_runs == 4:
                        b_entry["fours"] += 1
                    elif batter_runs == 6:
                        b_entry["sixes"] += 1

                    # Ensure bowler in stats
                    if bowler not in player_stats:
                        bowler_team = [t for t in registry.keys() if t != team_batting]
                        player_stats[bowler] = self._empty_player_dict(bowler, bowler_team[0] if bowler_team else "Opposition")
                    bowl_entry = player_stats[bowler]

                    # Legal ball check (no wide / no ball extras charged as balls faced)
                    extras_detail = delivery.get("extras", {})
                    is_wide = "wides" in extras_detail
                    is_noball = "noballs" in extras_detail

                    if not is_wide:
                        legal_balls += 1
                        bowl_entry["balls_bowled"] += 1

                    # Bowling runs: total minus legbyes/byes
                    byes = extras_detail.get("byes", 0) + extras_detail.get("legbyes", 0)
                    bowler_conceded = total_delivery_runs - byes
                    bowl_entry["runs_conceded"] += bowler_conceded
                    over_runs += bowler_conceded

                    if bowler_conceded == 0 and not is_wide and not is_noball:
                        bowl_entry["dot_balls"] += 1

                    # Wickets
                    if is_wicket:
                        for w in delivery["wickets"]:
                            kind = w.get("kind", "")
                            player_out = w.get("player_out")
                            if player_out and player_out in player_stats:
                                player_stats[player_out]["is_out"] = True
                                player_stats[player_out]["dismissal_kind"] = kind

                            # Bowler gets wicket unless run out, retired, obstructing
                            if kind not in ["run out", "retired hurt", "retired out", "obstructing the field"]:
                                bowl_entry["wickets"] += 1
                                if kind in ["bowled", "lbw"]:
                                    bowl_entry["bowled_or_lbw"] += 1

                            # Fielding credit
                            for fielder in w.get("fielders", []):
                                f_name = fielder.get("name")
                                if f_name:
                                    if f_name not in player_stats:
                                        player_stats[f_name] = self._empty_player_dict(f_name, "Fielding")
                                    if kind == "caught":
                                        player_stats[f_name]["catches"] += 1
                                    elif kind == "stumped":
                                        player_stats[f_name]["stumpings"] += 1
                                    elif kind == "run out":
                                        player_stats[f_name]["run_outs"] += 1

                # Check maiden over
                if legal_balls >= 6 and over_runs == 0:
                    bowl_entry["maidens"] += 1

        # Calculate Dream11 fantasy points for each player
        match_summary = {
            "match_id": path.stem,
            "info": info,
            "players": []
        }

        for player_name, stats in player_stats.items():
            pts = self.calculate_dream11_points(stats)
            stats["fantasy_points"] = pts
            stats["overs_bowled"] = round(stats["balls_bowled"] / 6, 1)
            stats["economy"] = round(stats["runs_conceded"] / (stats["overs_bowled"] or 1), 2)
            stats["strike_rate"] = round((stats["runs"] / (stats["balls_faced"] or 1)) * 100, 2)
            match_summary["players"].append(stats)

        return match_summary

    def _empty_player_dict(self, name: str, team: str) -> Dict[str, Any]:
        return {
            "player": name, "team": team,
            "runs": 0, "balls_faced": 0, "fours": 0, "sixes": 0,
            "is_out": False, "dismissal_kind": None, "batting_position": None,
            "balls_bowled": 0, "runs_conceded": 0, "wickets": 0,
            "maidens": 0, "bowled_or_lbw": 0, "dot_balls": 0,
            "catches": 0, "stumpings": 0, "run_outs": 0,
        }

    @staticmethod
    def calculate_dream11_points(s: Dict[str, Any]) -> float:
        """Calculates official Dream11 T20 Fantasy points from player match statistics."""
        pts = 4.0  # Starting XI points

        # --- Batting Points ---
        runs = s.get("runs", 0)
        fours = s.get("fours", 0)
        sixes = s.get("sixes", 0)
        balls_faced = s.get("balls_faced", 0)
        is_out = s.get("is_out", False)
        pos = s.get("batting_position", 11) or 11

        pts += runs * 1.0
        pts += fours * 1.0
        pts += sixes * 2.0

        # Milestone bonuses (non-cumulative in standard rules)
        if runs >= 100:
            pts += 16.0
        elif runs >= 50:
            pts += 8.0
        elif runs >= 30:
            pts += 4.0

        # Duck penalty: top 7 batters dismissed for 0
        if is_out and runs == 0 and pos <= 7 and balls_faced > 0:
            pts -= 2.0

        # Strike Rate bonus / penalty (minimum 10 balls faced)
        if balls_faced >= 10:
            sr = (runs / balls_faced) * 100.0
            if sr > 170.0:
                pts += 6.0
            elif sr >= 150.0:
                pts += 4.0
            elif sr >= 130.0:
                pts += 2.0
            elif 60.0 <= sr <= 70.0:
                pts -= 2.0
            elif 50.0 <= sr < 60.0:
                pts -= 4.0
            elif sr < 50.0:
                pts -= 6.0

        # --- Bowling Points ---
        wickets = s.get("wickets", 0)
        bowled_or_lbw = s.get("bowled_or_lbw", 0)
        maidens = s.get("maidens", 0)
        balls_bowled = s.get("balls_bowled", 0)
        runs_conceded = s.get("runs_conceded", 0)
        overs = balls_bowled / 6.0

        pts += wickets * 25.0
        pts += bowled_or_lbw * 8.0
        pts += maidens * 12.0

        # Wicket haul bonus
        if wickets >= 5:
            pts += 16.0
        elif wickets == 4:
            pts += 8.0
        elif wickets == 3:
            pts += 4.0

        # Economy Rate bonus / penalty (minimum 2 overs bowled)
        if overs >= 2.0:
            er = runs_conceded / overs
            if er < 5.0:
                pts += 6.0
            elif er < 6.0:
                pts += 4.0
            elif er <= 7.0:
                pts += 2.0
            elif 10.0 <= er <= 11.0:
                pts -= 2.0
            elif 11.0 < er <= 12.0:
                pts -= 4.0
            elif er > 12.0:
                pts -= 6.0

        # --- Fielding Points ---
        catches = s.get("catches", 0)
        stumpings = s.get("stumpings", 0)
        run_outs = s.get("run_outs", 0)

        pts += catches * 8.0
        if catches >= 3:
            pts += 4.0  # 3-catch bonus
        pts += stumpings * 12.0
        pts += run_outs * 12.0

        return round(pts, 1)

    def generate_training_dataset(self, max_matches: int = 100) -> pd.DataFrame:
        """Parses available matches and builds a feature dataset for ML model training."""
        match_files = list(self.matches_dir.glob("*.json"))[:max_matches]
        if not match_files:
            # If no matches extracted yet, extract sample
            self.download_dataset("ipl_json", limit_matches=25)
            match_files = list(self.matches_dir.glob("*.json"))[:max_matches]

        all_player_match_rows = []

        for f in match_files:
            try:
                parsed = self.parse_match(str(f))
                match_id = parsed["match_id"]
                venue = parsed["info"].get("venue", "Unknown Venue")
                city = parsed["info"].get("city", "Unknown City")

                for p in parsed["players"]:
                    row = {
                        "match_id": match_id,
                        "player": p["player"],
                        "team": p["team"],
                        "venue": venue,
                        "city": city,
                        "runs": p["runs"],
                        "balls_faced": p["balls_faced"],
                        "fours": p["fours"],
                        "sixes": p["sixes"],
                        "batting_position": p["batting_position"] or 9,
                        "balls_bowled": p["balls_bowled"],
                        "overs_bowled": p["overs_bowled"],
                        "wickets": p["wickets"],
                        "runs_conceded": p["runs_conceded"],
                        "economy": p["economy"],
                        "maidens": p["maidens"],
                        "catches": p["catches"],
                        "fantasy_points": p["fantasy_points"]
                    }
                    all_player_match_rows.append(row)
            except Exception as e:
                continue

        df = pd.DataFrame(all_player_match_rows)
        print(f"Generated training dataset with {len(df)} player-match observations across {len(match_files)} matches.")
        return df

