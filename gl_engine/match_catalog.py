"""Canonical Match Catalog for the 5-Match India vs West Indies 2026 Bilateral Series.
Provides complete venue parameters, pitch nature, playing conditions, and player pools for all 5 fixtures.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

MATCH_FILE_5TH = Path(__file__).parent / "data" / "ind_wi_match.json"


class UnknownMatchError(KeyError):
    """Requested fixture has no connected metadata and player pool."""

SERIES_FIXTURES = {
    "ind_wi_2026_01": {
        "id": "ind_wi_2026_01",
        "name": "India vs West Indies, 1st T20I (Kolkata)",
        "format": "T20 International",
        "status": "COMPLETED (IND won by 28 runs)",
        "venue": {
            "id": "eden_gardens",
            "name": "Eden Gardens, Kolkata",
            "city": "Kolkata",
            "soil_type": "Clay-dominant black soil with true bounce",
            "avg_first_innings": 194,
            "avg_second_innings": 166,
            "chasing_win_pct": 52.0,
            "pace_wicket_pct": 50.0,
            "spin_wicket_pct": 50.0,
            "dew_factor": 0.45,
            "pitch_nature": "High-scoring true deck. Evening dew assists second innings batting.",
            "boundaries": {"square_leg": 64, "midwicket": 68, "long_on": 74, "straight": 75, "long_off": 74, "cover": 68, "point": 62}
        },
        "teams": {
            "home": {"name": "India", "code": "IND", "score": "194/4", "overs": "20.0"},
            "away": {"name": "West Indies", "code": "WI", "score": "166/8", "overs": "20.0"}
        },
        "toss": {"winner": "West Indies", "choice": "bowl", "statement": "West Indies won toss and elected to field first"},
        "current_crr": 9.70,
        "projected_total": 194,
        "chasing_win_prob": 48.0
    },
    "ind_wi_2026_02": {
        "id": "ind_wi_2026_02",
        "name": "India vs West Indies, 2nd T20I (Ahmedabad)",
        "format": "T20 International",
        "status": "COMPLETED (WI won by 4 wickets)",
        "venue": {
            "id": "motera",
            "name": "Narendra Modi Stadium, Ahmedabad",
            "city": "Ahmedabad",
            "soil_type": "Red soil with heavy carry and steep bounce",
            "avg_first_innings": 182,
            "avg_second_innings": 183,
            "chasing_win_pct": 58.0,
            "pace_wicket_pct": 69.2,
            "spin_wicket_pct": 30.8,
            "dew_factor": 0.28,
            "pitch_nature": "Bouncy red soil wicket favoring express pace. Long straight boundaries.",
            "boundaries": {"square_leg": 68, "midwicket": 72, "long_on": 78, "straight": 80, "long_off": 78, "cover": 72, "point": 66}
        },
        "teams": {
            "home": {"name": "India", "code": "IND", "score": "182/7", "overs": "20.0"},
            "away": {"name": "West Indies", "code": "WI", "score": "183/6", "overs": "19.2"}
        },
        "toss": {"winner": "India", "choice": "bat", "statement": "India won toss and elected to bat first"},
        "current_crr": 9.10,
        "projected_total": 182,
        "chasing_win_prob": 58.0
    },
    "ind_wi_2026_03": {
        "id": "ind_wi_2026_03",
        "name": "India vs West Indies, 3rd T20I (Cuttack)",
        "format": "T20 International",
        "status": "COMPLETED (IND won by 7 wickets)",
        "venue": {
            "id": "barabati",
            "name": "Barabati Stadium, Cuttack",
            "city": "Cuttack",
            "soil_type": "Mixed alluvial soil with variable low bounce",
            "avg_first_innings": 142,
            "avg_second_innings": 145,
            "chasing_win_pct": 62.0,
            "pace_wicket_pct": 76.9,
            "spin_wicket_pct": 23.1,
            "dew_factor": 0.52,
            "pitch_nature": "Two-paced wicket with seam movement under lights. Mayank Yadav 4/18 express spell.",
            "boundaries": {"square_leg": 62, "midwicket": 66, "long_on": 71, "straight": 72, "long_off": 71, "cover": 66, "point": 60}
        },
        "teams": {
            "home": {"name": "India", "code": "IND", "score": "145/3", "overs": "15.2"},
            "away": {"name": "West Indies", "code": "WI", "score": "142 all out", "overs": "18.4"}
        },
        "toss": {"winner": "India", "choice": "bowl", "statement": "India won toss and elected to bowl first"},
        "current_crr": 7.10,
        "projected_total": 142,
        "chasing_win_prob": 62.0
    },
    "ind_wi_2026_04": {
        "id": "ind_wi_2026_04",
        "name": "India vs West Indies, 4th T20I (Visakhapatnam)",
        "format": "T20 International",
        "status": "COMPLETED (WI won by 18 runs)",
        "venue": {
            "id": "vizag",
            "name": "ACA-VDCA Stadium, Visakhapatnam",
            "city": "Visakhapatnam",
            "soil_type": "Dry black clay surface with grip and turn",
            "avg_first_innings": 178,
            "avg_second_innings": 160,
            "chasing_win_pct": 44.0,
            "pace_wicket_pct": 43.8,
            "spin_wicket_pct": 56.2,
            "dew_factor": 0.22,
            "pitch_nature": "Gripping, abrasive surface. Spinners Motie & Akeal dominated middle overs.",
            "boundaries": {"square_leg": 63, "midwicket": 67, "long_on": 73, "straight": 74, "long_off": 73, "cover": 67, "point": 61}
        },
        "teams": {
            "home": {"name": "India", "code": "IND", "score": "160 all out", "overs": "19.1"},
            "away": {"name": "West Indies", "code": "WI", "score": "178/6", "overs": "20.0"}
        },
        "toss": {"winner": "West Indies", "choice": "bat", "statement": "West Indies won toss and elected to bat first"},
        "current_crr": 8.90,
        "projected_total": 178,
        "chasing_win_prob": 44.0
    },
    "ind_vs_wi_5th_t20_2026": {
        "id": "ind_vs_wi_5th_t20_2026",
        "name": "India vs West Indies, 5th T20I (Series Decider)",
        "format": "T20 International",
        "status": "TOSS DELAYED DUE TO RAIN | Overcast Skies (84% Humidity)",
        "venue": {
            "id": "chinnaswamy",
            "name": "M. Chinnaswamy Stadium, Bengaluru",
            "city": "Bengaluru",
            "soil_type": "Sub-surface air-injected red clay with sand base (Rapid Drainage)",
            "avg_first_innings": 188,
            "avg_second_innings": 192,
            "chasing_win_pct": 70.0,
            "pace_wicket_pct": 59.6,
            "spin_wicket_pct": 40.4,
            "dew_factor": 0.38,
            "pitch_nature": "High altitude carry, true bounce, short boundaries (60m). Overcast skies & rain delay offer heavy early swing.",
            "boundaries": {"square_leg": 60, "midwicket": 64, "long_on": 70, "straight": 70, "long_off": 70, "cover": 64, "point": 58}
        },
        "teams": {
            "home": {"name": "India", "code": "IND", "score": "Series 2-2", "overs": "Decider"},
            "away": {"name": "West Indies", "code": "WI", "score": "Series 2-2", "overs": "Decider"}
        },
        "toss": {
            "winner": "West Indies",
            "choice": "bowl",
            "statement": "West Indies won the toss and elected to field first (9 overs per side, 2.4-over powerplay)."
        },
        "current_crr": 10.10,
        "projected_total": 204,
        "chasing_win_prob": 70.0
    },
    "ind_w_vs_zim_w_2026_02": {
        "id": "ind_w_vs_zim_w_2026_02",
        "name": "India Women vs Zimbabwe Women, 2nd T20I (Raipur)",
        "format": "Women's T20 International",
        "status": "TOSS CONCLUDED | Zimbabwe Opt to Bat | Both Teams Unchanged",
        "venue": {
            "id": "raipur_svns_stadium",
            "name": "Shaheed Veer Narayan Singh International Stadium, Raipur",
            "city": "Raipur",
            "soil_type": "Black soil surface (Pitch No. 4) with grass-bound cracks",
            "avg_first_innings": 142.0,
            "avg_second_innings": 136.0,
            "chasing_win_pct": 60.0,
            "pace_wicket_pct": 52.0,
            "spin_wicket_pct": 48.0,
            "dew_factor": 0.28,
            "pitch_nature": "Black soil Pitch No. 4 rolled well with grass growing in cracks, nicely bound. WV Raman pitch report: Pace-off deliveries and back-of-the-hand cutters (Arundhati Reddy, Nandani Sharma) grip exceptionally well. Straight down the ground boundary routes for Mandhana & Deepti; back-foot punch for Niki Prasad.",
            "boundaries": {"square_leg": 63, "midwicket": 67, "long_on": 73, "straight": 74, "long_off": 73, "cover": 66, "point": 61}
        },
        "teams": {
            "home": {"name": "India Women", "code": "IND-W", "score": "Bowling First", "overs": "20.0"},
            "away": {"name": "Zimbabwe Women", "code": "ZIM-W", "score": "Batting First", "overs": "20.0"}
        },
        "toss": {
            "winner": "Zimbabwe Women",
            "choice": "bat",
            "statement": "Zimbabwe Women won the toss and opted to bat first. Both teams playing an unchanged playing XI."
        },
        "current_crr": 6.85,
        "projected_total": 135,
        "chasing_win_prob": 76.0
    }
}

# Aliases
SERIES_FIXTURES["ind_wi_2026_05"] = SERIES_FIXTURES["ind_vs_wi_5th_t20_2026"]
SERIES_FIXTURES["indw_zimw"] = SERIES_FIXTURES["ind_w_vs_zim_w_2026_02"]
SERIES_FIXTURES["ind_w_vs_zim_w"] = SERIES_FIXTURES["ind_w_vs_zim_w_2026_02"]

def get_match_data(match_id: Optional[str] = None) -> Dict[str, Any]:
    """Returns canonical match info and player pool for the requested fixture."""
    canonical_id = match_id or "ind_w_vs_zim_w_2026_02"
    
    # Check if IND-W vs ZIM-W requested
    if canonical_id in ("ind_w_vs_zim_w_2026_02", "indw_zimw", "ind_w_vs_zim_w", "indw_zimw_2026_02"):
        from .wt20_registry import get_wt20_registry
        reg = get_wt20_registry()
        return {
            "match_info": SERIES_FIXTURES["ind_w_vs_zim_w_2026_02"],
            "players": reg.get_all_players()
        }
    
    # Check if this is a live match from ESPNcricinfo cricdata feed
    if canonical_id.startswith("cricdata_"):
        from .live_feed import load_cricdata_match_detail
        live_data = load_cricdata_match_detail(canonical_id)
        if live_data and live_data.get("players"):
            return live_data

    if canonical_id not in SERIES_FIXTURES:
        raise UnknownMatchError(f"Unknown or disconnected match: {canonical_id}")

    # Load base players from bundled 5th match file
    base_players = []
    if MATCH_FILE_5TH.exists():
        with open(MATCH_FILE_5TH, "r", encoding="utf-8") as f:
            full_json = json.load(f)
            base_players = full_json.get("players", [])

    # If canonical fixture is in catalog, use its specific venue and match metadata
    fixture_meta = dict(SERIES_FIXTURES[canonical_id], data_provenance="UNVERIFIED_BUNDLED_FIXTURE", status="BUNDLED FIXTURE | [VERIFY REQUIRED]")

    
    # Custom adjustments per fixture (ownership / stats tailored to match context)
    players_copy = []
    for p in base_players:
        p_copy = dict(p)
        # Adapt ownership & recent form if earlier match
        if canonical_id == "ind_wi_2026_01":
            # 1st match: Abhishek Sharma had higher novelty ownership, Arshdeep prime chalk
            if p_copy["id"] == "ind_abhishek":
                p_copy["projected_ownership"] = 82.5
            elif p_copy["id"] == "ind_mayank":
                p_copy["projected_ownership"] = 18.0  # Debut fixture
        elif canonical_id == "ind_wi_2026_04":
            # 4th match: Spinners Motie & Hosein were heavily owned on slow track
            if p_copy["id"] == "wi_motie":
                p_copy["projected_ownership"] = 52.0
            elif p_copy["id"] == "wi_rutherford":
                p_copy["projected_ownership"] = 48.0
        players_copy.append(p_copy)

    return {
        "match_info": fixture_meta,
        "players": players_copy
    }

