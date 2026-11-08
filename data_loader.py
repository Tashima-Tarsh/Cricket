"""
Data loader for cricket fantasy engine.
Handles Cricsheet CSV parsing + provides synthetic sample data for immediate testing.
"""
import pandas as pd
import numpy as np
from typing import List, Dict
import os

# ---------- SAMPLE DATA (for immediate testing) ----------
# In production, replace this with real Cricsheet.org ball-by-ball CSVs
def generate_sample_historical_data(n_matches: int = 50) -> pd.DataFrame:
    """Generate realistic synthetic cricket fantasy data for model training."""
    np.random.seed(42)
    records = []
    players = [
        {"name": "Rohit_Sharma", "role": "BAT", "team": "MI", "skill": 85},
        {"name": "Virat_Kohli", "role": "BAT", "team": "RCB", "skill": 90},
        {"name": "Jasprit_Bumrah", "role": "BOWL", "team": "MI", "skill": 92},
        {"name": "Rashid_Khan", "role": "BOWL", "team": "GT", "skill": 88},
        {"name": "Hardik_Pandya", "role": "AR", "team": "GT", "skill": 82},
        {"name": "Ravindra_Jadeja", "role": "AR", "team": "CSK", "skill": 84},
        {"name": "KL_Rahul", "role": "WK", "team": "LSG", "skill": 80},
        {"name": "Rishabh_Pant", "role": "WK", "team": "DC", "skill": 83},
        {"name": "Yuzvendra_Chahal", "role": "BOWL", "team": "RR", "skill": 81},
        {"name": "Suryakumar_Yadav", "role": "BAT", "team": "MI", "skill": 87},
        {"name": "Shubman_Gill", "role": "BAT", "team": "GT", "skill": 86},
        {"name": "Faf_du_Plessis", "role": "BAT", "team": "RCB", "skill": 79},
        {"name": "Mohammed_Siraj", "role": "BOWL", "team": "RCB", "skill": 80},
        {"name": "Trent_Boult", "role": "BOWL", "team": "GT", "skill": 85},
        {"name": "MS_Dhoni", "role": "WK", "team": "CSK", "skill": 75},
    ]
    venues = ["Wankhede", "Chinnaswamy", "Chepauk", "Eden_Gardens", "Kotla"]

    for match_id in range(n_matches):
        venue = np.random.choice(venues)
        for p in players:
            # Fantasy points = f(skill, venue, recent form, randomness)
            base = p["skill"] * 0.6
            venue_bonus = np.random.uniform(-5, 10)
            noise = np.random.normal(0, 15)
            fantasy_points = max(0, base + venue_bonus + noise)

            records.append({
                "match_id": match_id,
                "player": p["name"],
                "role": p["role"],
                "team": p["team"],
                "venue": venue,
                "skill_rating": p["skill"],
                "recent_form_last_5": np.random.uniform(40, 100),
                "opposition_strength": np.random.uniform(50, 90),
                "phase_strike_rate": np.random.uniform(110, 180),  # death overs SR
                "economy_rate": np.random.uniform(6.0, 10.5),
                "fantasy_points": round(fantasy_points, 2)
            })
    return pd.DataFrame(records)


def load_upcoming_match_players() -> List[Dict]:
    """
    Returns the players for the upcoming match with credits and projected selection %.
    In production, scrape this from Dream11/My11Circle 30 min before deadline.
    """
    np.random.seed(42)
    role_features = {
        "BAT":  {"skill_rating": 85, "recent_form_last_5": 70.0, "opposition_strength": 70.0, "phase_strike_rate": 140.0, "economy_rate": 9.5},
        "BOWL": {"skill_rating": 85, "recent_form_last_5": 70.0, "opposition_strength": 70.0, "phase_strike_rate": 110.0, "economy_rate": 8.0},
        "AR":   {"skill_rating": 82, "recent_form_last_5": 70.0, "opposition_strength": 70.0, "phase_strike_rate": 130.0, "economy_rate": 8.5},
        "WK":   {"skill_rating": 80, "recent_form_last_5": 70.0, "opposition_strength": 70.0, "phase_strike_rate": 135.0, "economy_rate": 9.5},
    }
    players = [
        # Team A (MI)
        {"name": "Rohit_Sharma", "role": "BAT", "team": "MI", "credit": 10.5, "projected_sel_pct": 78.0},
        {"name": "Suryakumar_Yadav", "role": "BAT", "team": "MI", "credit": 10.0, "projected_sel_pct": 65.0},
        {"name": "Jasprit_Bumrah", "role": "BOWL", "team": "MI", "credit": 10.5, "projected_sel_pct": 82.0},
        {"name": "Ishan_Kishan", "role": "WK", "team": "MI", "credit": 9.0, "projected_sel_pct": 45.0},
        {"name": "Tilak_Varma", "role": "BAT", "team": "MI", "credit": 8.5, "projected_sel_pct": 22.0},  # differential
        {"name": "Piyush_Chawla", "role": "BOWL", "team": "MI", "credit": 8.0, "projected_sel_pct": 8.0},   # differential
        {"name": "Nehal_Wadhera", "role": "BAT", "team": "MI", "credit": 8.0, "projected_sel_pct": 12.0},
        {"name": "Kumar_Kartikeya", "role": "BOWL", "team": "MI", "credit": 8.5, "projected_sel_pct": 14.0},
        {"name": "Dumesh_Mathesha", "role": "BOWL", "team": "MI", "credit": 8.0, "projected_sel_pct": 6.0},   # differential
        {"name": "Ryan_Rickelton", "role": "WK", "team": "MI", "credit": 8.5, "projected_sel_pct": 18.0},
        {"name": "Ashwani_Kumar", "role": "BOWL", "team": "MI", "credit": 8.0, "projected_sel_pct": 10.0},
        # Team B (RCB)
        {"name": "Virat_Kohli", "role": "BAT", "team": "RCB", "credit": 11.0, "projected_sel_pct": 88.0},
        {"name": "Faf_du_Plessis", "role": "BAT", "team": "RCB", "credit": 9.5, "projected_sel_pct": 55.0},
        {"name": "Rajat_Patidar", "role": "BAT", "team": "RCB", "credit": 9.0, "projected_sel_pct": 35.0},
        {"name": "Mohammed_Siraj", "role": "BOWL", "team": "RCB", "credit": 9.5, "projected_sel_pct": 60.0},
        {"name": "Jitesh_Sharma", "role": "WK", "team": "RCB", "credit": 8.5, "projected_sel_pct": 20.0},
        {"name": "Liam_Livingstone", "role": "AR", "team": "RCB", "credit": 9.5, "projected_sel_pct": 40.0},
        {"name": "Krunal_Pandya", "role": "AR", "team": "RCB", "credit": 8.5, "projected_sel_pct": 25.0},
        {"name": "Josh_Hazlewood", "role": "BOWL", "team": "RCB", "credit": 9.0, "projected_sel_pct": 48.0},
        {"name": "Yash_Dayal", "role": "BOWL", "team": "RCB", "credit": 8.0, "projected_sel_pct": 11.0},    # differential
        {"name": "Swaabh_Pandey", "role": "BAT", "team": "RCB", "credit": 8.0, "projected_sel_pct": 7.0},    # differential
        {"name": "Nuwan_Thushara", "role": "BOWL", "team": "RCB", "credit": 8.5, "projected_sel_pct": 9.0},  # differential
        {"name": "Tim_David", "role": "AR", "team": "RCB", "credit": 8.5, "projected_sel_pct": 30.0},
    ]
    for pl in players:
        rf = role_features[pl["role"]]
        pl["skill_rating"] = rf["skill_rating"] + np.random.uniform(-5, 5)
        pl["recent_form_last_5"] = round(np.random.uniform(40, 100), 1)
        pl["opposition_strength"] = round(np.random.uniform(50, 90), 1)
        pl["phase_strike_rate"] = round(np.random.uniform(110, 180), 1)
        pl["economy_rate"] = round(np.random.uniform(6.0, 10.5), 2)
    return players
