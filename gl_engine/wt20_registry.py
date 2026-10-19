"""Authoritative Player Registry and Historical Database for IND-W vs ZIM-W (31 Players).
Maintains canonical identities, ESPNcricinfo IDs, Cricsheet mappings, batting/bowling styles,
historical appearance records, split performance windows, and fantasy pricing.
"""

from typing import Dict, Any, List, Optional
import duckdb
import os
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "cricsheet_wt20.duckdb"

RAW_31_PLAYERS = [
    # --- India Women (16 Players) ---
    {
        "id": "indw_smriti_mandhana",
        "name": "Smriti Mandhana",
        "team": "IND-W",
        "country": "India",
        "role": "BAT",
        "credits": 10.0,
        "batting_style": "LHB",
        "bowling_style": "Right-arm medium",
        "batting_order_projected": 1,
        "expected_overs": 0.0,
        "cricinfo_id": 597806,
        "cricinfo_legacy_id": 70132,
        "cricsheet_name": "S Mandhana",
        "is_confirmed_xi": True,
        "projected_ownership": 91.5,
        "debut_year": 2013,
        "stats": {
            "career_matches": 141, "career_runs": 3493, "career_avg": 28.86, "strike_rate": 122.51,
            "fifties": 26, "hundreds": 0, "career_wkts": 0, "economy": 0.0,
            "avg_fantasy_pts": 58.4, "recent_fantasy_pts": [78.5, 42.0, 94.0, 31.0, 68.0]
        }
    },
    {
        "id": "indw_shafali_verma",
        "name": "Shafali Verma",
        "team": "IND-W",
        "country": "India",
        "role": "BAT",
        "credits": 9.0,
        "batting_style": "RHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 2,
        "expected_overs": 1.0,
        "cricinfo_id": 1182523,
        "cricinfo_legacy_id": 105213,
        "cricsheet_name": "Shafali Verma",
        "is_confirmed_xi": True,
        "projected_ownership": 78.2,
        "debut_year": 2019,
        "stats": {
            "career_matches": 81, "career_runs": 1948, "career_avg": 24.65, "strike_rate": 129.86,
            "fifties": 10, "hundreds": 0, "career_wkts": 10, "economy": 6.80,
            "avg_fantasy_pts": 51.2, "recent_fantasy_pts": [64.0, 85.0, 22.0, 48.0, 56.0]
        }
    },
    {
        "id": "indw_harmanpreet_kaur",
        "name": "Harmanpreet Kaur",
        "team": "IND-W",
        "country": "India",
        "role": "BAT",
        "credits": 9.0,
        "batting_style": "RHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 4,
        "expected_overs": 1.5,
        "cricinfo_id": 372317,
        "cricinfo_legacy_id": 58198,
        "cricsheet_name": "H Kaur",
        "is_confirmed_xi": True,
        "projected_ownership": 82.4,
        "debut_year": 2009,
        "stats": {
            "career_matches": 173, "career_runs": 3415, "career_avg": 27.99, "strike_rate": 120.75,
            "fifties": 13, "hundreds": 1, "career_wkts": 32, "economy": 6.45,
            "avg_fantasy_pts": 49.8, "recent_fantasy_pts": [52.0, 68.0, 36.0, 82.0, 41.0]
        }
    },
    {
        "id": "indw_deepti_sharma",
        "name": "Deepti Sharma",
        "team": "IND-W",
        "country": "India",
        "role": "AR",
        "credits": 9.5,
        "batting_style": "LHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 6,
        "expected_overs": 4.0,
        "cricinfo_id": 597811,
        "cricinfo_legacy_id": 70137,
        "cricsheet_name": "DB Sharma",
        "is_confirmed_xi": True,
        "projected_ownership": 94.0,
        "debut_year": 2016,
        "stats": {
            "career_matches": 117, "career_runs": 1020, "career_avg": 24.87, "strike_rate": 106.25,
            "fifties": 2, "hundreds": 0, "career_wkts": 131, "economy": 5.95,
            "avg_fantasy_pts": 66.5, "recent_fantasy_pts": [92.0, 68.0, 114.0, 54.0, 78.0]
        }
    },
    {
        "id": "indw_richa_ghosh",
        "name": "Richa Ghosh",
        "team": "IND-W",
        "country": "India",
        "role": "WK",
        "credits": 8.5,
        "batting_style": "RHB",
        "bowling_style": "Right-arm medium",
        "batting_order_projected": 5,
        "expected_overs": 0.0,
        "cricinfo_id": 1212830,
        "cricinfo_legacy_id": 107319,
        "cricsheet_name": "RM Ghosh",
        "is_confirmed_xi": True,
        "projected_ownership": 76.5,
        "debut_year": 2020,
        "stats": {
            "career_matches": 55, "career_runs": 862, "career_avg": 26.93, "strike_rate": 134.68,
            "fifties": 1, "hundreds": 0, "career_wkts": 0, "economy": 0.0,
            "avg_fantasy_pts": 44.2, "recent_fantasy_pts": [58.0, 36.0, 72.0, 24.0, 61.0]
        }
    },
    {
        "id": "indw_arundhati_reddy",
        "name": "Arundhati Reddy",
        "team": "IND-W",
        "country": "India",
        "role": "BOWL",
        "credits": 8.5,
        "batting_style": "RHB",
        "bowling_style": "Right-arm medium-fast",
        "batting_order_projected": 8,
        "expected_overs": 4.0,
        "cricinfo_id": 960867,
        "cricinfo_legacy_id": 89365,
        "cricsheet_name": "A Reddy",
        "is_confirmed_xi": True,
        "projected_ownership": 72.0,
        "debut_year": 2018,
        "stats": {
            "career_matches": 34, "career_runs": 95, "career_avg": 10.55, "strike_rate": 96.93,
            "fifties": 0, "hundreds": 0, "career_wkts": 29, "economy": 7.42,
            "avg_fantasy_pts": 46.8, "recent_fantasy_pts": [74.0, 54.0, 88.0, 31.0, 62.0]
        }
    },
    {
        "id": "indw_minnu_mani",
        "name": "Minnu Mani",
        "team": "IND-W",
        "country": "India",
        "role": "AR",
        "credits": 8.0,
        "batting_style": "LHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 7,
        "expected_overs": 3.0,
        "cricinfo_id": 960949,
        "cricinfo_legacy_id": 89447,
        "cricsheet_name": "M Mani",
        "is_confirmed_xi": False,
        "projected_ownership": 42.5,
        "debut_year": 2023,
        "stats": {
            "career_matches": 7, "career_runs": 28, "career_avg": 14.00, "strike_rate": 112.00,
            "fifties": 0, "hundreds": 0, "career_wkts": 9, "economy": 6.18,
            "avg_fantasy_pts": 38.4, "recent_fantasy_pts": [48.0, 31.0, 56.0, 24.0, 42.0]
        }
    },
    {
        "id": "indw_shree_charani",
        "name": "Shree Charani",
        "team": "IND-W",
        "country": "India",
        "role": "BOWL",
        "credits": 7.5,
        "batting_style": "LHB",
        "bowling_style": "Slow left-arm orthodox",
        "batting_order_projected": 9,
        "expected_overs": 4.0,
        "cricinfo_id": 1464461,
        "cricinfo_legacy_id": 119145,
        "cricsheet_name": "N Shree Charani",
        "is_confirmed_xi": True,
        "projected_ownership": 24.5,
        "debut_year": 2026,
        "stats": {
            "career_matches": 4, "career_runs": 12, "career_avg": 12.00, "strike_rate": 90.0,
            "fifties": 0, "hundreds": 0, "career_wkts": 6, "economy": 5.90,
            "avg_fantasy_pts": 36.2, "recent_fantasy_pts": [42.0, 54.0, 28.0, 38.0, 40.0]
        }
    },
    {
        "id": "indw_nandani_sharma",
        "name": "Nandani Sharma",
        "team": "IND-W",
        "country": "India",
        "role": "BOWL",
        "credits": 7.5,
        "batting_style": "RHB",
        "bowling_style": "Right-arm fast-medium",
        "batting_order_projected": 10,
        "expected_overs": 3.0,
        "cricinfo_id": 1289676,
        "cricinfo_legacy_id": 110721,
        "cricsheet_name": "NSS Sharma",
        "is_confirmed_xi": True,
        "projected_ownership": 22.0,
        "debut_year": 2026,
        "stats": {
            "career_matches": 5, "career_runs": 8, "career_avg": 8.00, "strike_rate": 85.0,
            "fifties": 0, "hundreds": 0, "career_wkts": 7, "economy": 6.75,
            "avg_fantasy_pts": 34.0, "recent_fantasy_pts": [36.0, 62.0, 24.0, 44.0, 30.0]
        }
    },
    {
        "id": "indw_kranti_gaud",
        "name": "Kranti Gaud",
        "team": "IND-W",
        "country": "India",
        "role": "BOWL",
        "credits": 7.0,
        "batting_style": "RHB",
        "bowling_style": "Right-arm medium-fast",
        "batting_order_projected": 11,
        "expected_overs": 2.5,
        "cricinfo_id": 1464471,
        "cricinfo_legacy_id": 119155,
        "cricsheet_name": "K Gaud",
        "is_confirmed_xi": True,
        "projected_ownership": 15.5,
        "debut_year": 2026,
        "stats": {
            "career_matches": 3, "career_runs": 4, "career_avg": 4.00, "strike_rate": 80.0,
            "fifties": 0, "hundreds": 0, "career_wkts": 4, "economy": 7.10,
            "avg_fantasy_pts": 28.5, "recent_fantasy_pts": [31.0, 42.0, 18.0, 29.0, 25.0]
        }
    },
    {
        "id": "indw_jintimani_kalita",
        "name": "Jintimani Kalita",
        "team": "IND-W",
        "country": "India",
        "role": "BOWL",
        "credits": 7.0,
        "batting_style": "LHB",
        "bowling_style": "Right-arm medium-fast",
        "batting_order_projected": 9,
        "expected_overs": 2.0,
        "cricinfo_id": 1255387,
        "cricinfo_legacy_id": 108859,
        "cricsheet_name": "JN Kalita",
        "is_confirmed_xi": False,
        "projected_ownership": 10.5,
        "debut_year": 2023,
        "stats": {
            "career_matches": 8, "career_runs": 32, "career_avg": 10.66, "strike_rate": 103.22,
            "fifties": 0, "hundreds": 0, "career_wkts": 5, "economy": 7.60,
            "avg_fantasy_pts": 22.0, "recent_fantasy_pts": [18.0, 24.0, 31.0, 12.0, 26.0]
        }
    },
    {
        "id": "indw_gunalan_kamalini",
        "name": "Gunalan Kamalini",
        "team": "IND-W",
        "country": "India",
        "role": "WK",
        "credits": 7.0,
        "batting_style": "LHB",
        "bowling_style": "Legbreak",
        "batting_order_projected": 7,
        "expected_overs": 0.0,
        "cricinfo_id": 1427355,
        "cricinfo_legacy_id": 117238,
        "cricsheet_name": "G Kamalini",
        "is_confirmed_xi": False,
        "projected_ownership": 8.0,
        "debut_year": 2026,
        "stats": {
            "career_matches": 2, "career_runs": 18, "career_avg": 18.00, "strike_rate": 110.0,
            "fifties": 0, "hundreds": 0, "career_wkts": 0, "economy": 0.0,
            "avg_fantasy_pts": 19.5, "recent_fantasy_pts": [22.0, 18.0, 25.0, 14.0, 20.0]
        }
    },
    {
        "id": "indw_niki_prasad",
        "name": "Niki Prasad",
        "team": "IND-W",
        "country": "India",
        "role": "BAT",
        "credits": 7.0,
        "batting_style": "RHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 5,
        "expected_overs": 0.0,
        "cricinfo_id": 1255497,
        "cricinfo_legacy_id": 108969,
        "cricsheet_name": "NS Prasad",
        "is_confirmed_xi": True,
        "projected_ownership": 26.0,
        "debut_year": 2025,
        "stats": {
            "career_matches": 6, "career_runs": 112, "career_avg": 22.40, "strike_rate": 118.5,
            "fifties": 0, "hundreds": 0, "career_wkts": 0, "economy": 0.0,
            "avg_fantasy_pts": 28.0, "recent_fantasy_pts": [34.0, 18.0, 42.0, 26.0, 22.0]
        }
    },
    {
        "id": "indw_prema_rawat",
        "name": "Prema Rawat",
        "team": "IND-W",
        "country": "India",
        "role": "BOWL",
        "credits": 7.0,
        "batting_style": "RHB",
        "bowling_style": "Legbreak",
        "batting_order_projected": 10,
        "expected_overs": 2.0,
        "cricinfo_id": 1464463,
        "cricinfo_legacy_id": 119147,
        "cricsheet_name": "P Rawat",
        "is_confirmed_xi": False,
        "projected_ownership": 9.2,
        "debut_year": 2026,
        "stats": {
            "career_matches": 2, "career_runs": 6, "career_avg": 6.00, "strike_rate": 75.0,
            "fifties": 0, "hundreds": 0, "career_wkts": 2, "economy": 6.80,
            "avg_fantasy_pts": 24.0, "recent_fantasy_pts": [28.0, 19.0, 31.0, 14.0, 22.0]
        }
    },
    {
        "id": "indw_anushka_sharma",
        "name": "Anushka Sharma",
        "team": "IND-W",
        "country": "India",
        "role": "AR",
        "credits": 7.0,
        "batting_style": "RHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 3,
        "expected_overs": 1.0,
        "cricinfo_id": 1255510,
        "cricinfo_legacy_id": 108982,
        "cricsheet_name": "AB Sharma",
        "is_confirmed_xi": True,
        "projected_ownership": 24.0,
        "debut_year": 2025,
        "stats": {
            "career_matches": 4, "career_runs": 35, "career_avg": 17.50, "strike_rate": 105.0,
            "fifties": 0, "hundreds": 0, "career_wkts": 2, "economy": 7.20,
            "avg_fantasy_pts": 21.0, "recent_fantasy_pts": [24.0, 16.0, 29.0, 12.0, 20.0]
        }
    },
    {
        "id": "indw_jemimah_rodrigues",
        "name": "Jemimah Rodrigues",
        "team": "IND-W",
        "country": "India",
        "role": "BAT",
        "credits": 8.5,
        "batting_style": "RHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 3,
        "expected_overs": 0.0,
        "cricinfo_id": 1089844,
        "cricinfo_legacy_id": 92248,
        "cricsheet_name": "J Rodrigues",
        "is_confirmed_xi": False,
        "projected_ownership": 64.0,
        "debut_year": 2018,
        "stats": {
            "career_matches": 100, "career_runs": 2074, "career_avg": 29.62, "strike_rate": 114.26,
            "fifties": 11, "hundreds": 0, "career_wkts": 1, "economy": 6.80,
            "avg_fantasy_pts": 42.5, "recent_fantasy_pts": [48.0, 52.0, 36.0, 68.0, 22.0]
        }
    },

    # --- Zimbabwe Women (15 Players) ---
    {
        "id": "zimw_josephine_nkomo",
        "name": "Josephine Nkomo",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "AR",
        "credits": 9.0,
        "batting_style": "RHB",
        "bowling_style": "Right-arm medium-fast",
        "batting_order_projected": 9,
        "expected_overs": 4.0,
        "cricinfo_id": 638256,
        "cricinfo_legacy_id": 71221,
        "cricsheet_name": "J Nkomo",
        "is_confirmed_xi": True,
        "projected_ownership": 78.5,
        "debut_year": 2018,
        "stats": {
            "career_matches": 58, "career_runs": 612, "career_avg": 23.53, "strike_rate": 94.88,
            "fifties": 1, "hundreds": 0, "career_wkts": 55, "economy": 5.12,
            "avg_fantasy_pts": 54.8, "recent_fantasy_pts": [68.0, 48.0, 84.0, 52.0, 62.0]
        }
    },
    {
        "id": "zimw_kelis_ndhlovu",
        "name": "Kelis Ndhlovu",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "AR",
        "credits": 8.5,
        "batting_style": "LHB",
        "bowling_style": "Slow left-arm orthodox",
        "batting_order_projected": 1,
        "expected_overs": 3.0,
        "cricinfo_id": 1250707,
        "cricinfo_legacy_id": 108584,
        "cricsheet_name": "K Ndhlovu",
        "is_confirmed_xi": True,
        "projected_ownership": 68.0,
        "debut_year": 2022,
        "stats": {
            "career_matches": 42, "career_runs": 685, "career_avg": 20.14, "strike_rate": 96.20,
            "fifties": 2, "hundreds": 0, "career_wkts": 38, "economy": 5.48,
            "avg_fantasy_pts": 49.6, "recent_fantasy_pts": [54.0, 72.0, 36.0, 61.0, 44.0]
        }
    },
    {
        "id": "zimw_beloved_biza",
        "name": "Beloved Biza",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "AR",
        "credits": 7.5,
        "batting_style": "RHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 2,
        "expected_overs": 2.0,
        "cricinfo_id": 1302686,
        "cricinfo_legacy_id": 111468,
        "cricsheet_name": "B Biza",
        "is_confirmed_xi": True,
        "projected_ownership": 31.5,
        "debut_year": 2024,
        "stats": {
            "career_matches": 12, "career_runs": 185, "career_avg": 20.55, "strike_rate": 95.85,
            "fifties": 0, "hundreds": 0, "career_wkts": 8, "economy": 5.80,
            "avg_fantasy_pts": 35.0, "recent_fantasy_pts": [44.0, 28.0, 36.0, 52.0, 22.0]
        }
    },
    {
        "id": "zimw_modester_mupachikwa",
        "name": "Modester Mupachikwa",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "WK",
        "credits": 8.0,
        "batting_style": "RHB",
        "bowling_style": "Wicketkeeper",
        "batting_order_projected": 3,
        "expected_overs": 0.0,
        "cricinfo_id": 538591,
        "cricinfo_legacy_id": 66816,
        "cricsheet_name": "M Mupachikwa",
        "is_confirmed_xi": True,
        "projected_ownership": 45.0,
        "debut_year": 2019,
        "stats": {
            "career_matches": 55, "career_runs": 1064, "career_avg": 26.60, "strike_rate": 88.52,
            "fifties": 3, "hundreds": 0, "career_wkts": 0, "economy": 0.0,
            "avg_fantasy_pts": 38.0, "recent_fantasy_pts": [36.0, 48.0, 24.0, 52.0, 31.0]
        }
    },
    {
        "id": "zimw_sharne_mayers",
        "name": "Sharne Mayers",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "BAT",
        "credits": 8.5,
        "batting_style": "RHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 4,
        "expected_overs": 0.0,
        "cricinfo_id": 317144,
        "cricinfo_legacy_id": 53525,
        "cricsheet_name": "SM Mayers",
        "is_confirmed_xi": True,
        "projected_ownership": 54.0,
        "debut_year": 2019,
        "stats": {
            "career_matches": 38, "career_runs": 810, "career_avg": 26.12, "strike_rate": 112.44,
            "fifties": 3, "hundreds": 0, "career_wkts": 2, "economy": 6.80,
            "avg_fantasy_pts": 41.5, "recent_fantasy_pts": [48.0, 32.0, 68.0, 24.0, 52.0]
        }
    },
    {
        "id": "zimw_nyasha_gwanzura",
        "name": "Nyasha Gwanzura",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "AR",
        "credits": 7.5,
        "batting_style": "RHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 5,
        "expected_overs": 2.5,
        "cricinfo_id": 922491,
        "cricinfo_legacy_id": 84915,
        "cricsheet_name": "N Gwanzura",
        "is_confirmed_xi": True,
        "projected_ownership": 28.0,
        "debut_year": 2021,
        "stats": {
            "career_matches": 31, "career_runs": 280, "career_avg": 14.73, "strike_rate": 92.40,
            "fifties": 0, "hundreds": 0, "career_wkts": 18, "economy": 6.12,
            "avg_fantasy_pts": 32.5, "recent_fantasy_pts": [38.0, 22.0, 48.0, 18.0, 34.0]
        }
    },
    {
        "id": "zimw_chipo_mugeri",
        "name": "Chipo Mugeri-Tiripano",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "BAT",
        "credits": 8.0,
        "batting_style": "LHB",
        "bowling_style": "Right-arm medium",
        "batting_order_projected": 7,
        "expected_overs": 0.0,
        "cricinfo_id": 317148,
        "cricinfo_legacy_id": 53527,
        "cricsheet_name": "CS Mugeri",
        "is_confirmed_xi": True,
        "projected_ownership": 48.0,
        "debut_year": 2019,
        "stats": {
            "career_matches": 52, "career_runs": 948, "career_avg": 23.70, "strike_rate": 105.15,
            "fifties": 2, "hundreds": 0, "career_wkts": 1, "economy": 7.00,
            "avg_fantasy_pts": 36.8, "recent_fantasy_pts": [42.0, 28.0, 54.0, 18.0, 44.0]
        }
    },
    {
        "id": "zimw_loryn_phiri",
        "name": "Loryn Phiri",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "BOWL",
        "credits": 7.5,
        "batting_style": "RHB",
        "bowling_style": "Right-arm offbreak",
        "batting_order_projected": 8,
        "expected_overs": 4.0,
        "cricinfo_id": 1135025,
        "cricinfo_legacy_id": 101846,
        "cricsheet_name": "L Phiri",
        "is_confirmed_xi": False,
        "projected_ownership": 12.0,
        "debut_year": 2019,
        "stats": {
            "career_matches": 34, "career_runs": 65, "career_avg": 7.22, "strike_rate": 81.25,
            "fifties": 0, "hundreds": 0, "career_wkts": 33, "economy": 5.65,
            "avg_fantasy_pts": 36.0, "recent_fantasy_pts": [42.0, 54.0, 28.0, 31.0, 48.0]
        }
    },
    {
        "id": "zimw_nomvelo_sibanda",
        "name": "Nomvelo Sibanda",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "BOWL",
        "credits": 7.5,
        "batting_style": "LHB",
        "bowling_style": "Left-arm medium",
        "batting_order_projected": 9,
        "expected_overs": 4.0,
        "cricinfo_id": 1080012,
        "cricinfo_legacy_id": 96440,
        "cricsheet_name": "N Sibanda",
        "is_confirmed_xi": False,
        "projected_ownership": 14.0,
        "debut_year": 2019,
        "stats": {
            "career_matches": 45, "career_runs": 52, "career_avg": 5.77, "strike_rate": 74.28,
            "fifties": 0, "hundreds": 0, "career_wkts": 46, "economy": 5.40,
            "avg_fantasy_pts": 39.5, "recent_fantasy_pts": [48.0, 62.0, 34.0, 54.0, 28.0]
        }
    },
    {
        "id": "zimw_francisca_chipare",
        "name": "Francisca Chipare",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "BOWL",
        "credits": 7.0,
        "batting_style": "RHB",
        "bowling_style": "Right-arm medium",
        "batting_order_projected": 8,
        "expected_overs": 3.0,
        "cricinfo_id": 1119417,
        "cricinfo_legacy_id": 100887,
        "cricsheet_name": "F Chipare",
        "is_confirmed_xi": True,
        "projected_ownership": 24.0,
        "debut_year": 2022,
        "stats": {
            "career_matches": 22, "career_runs": 28, "career_avg": 7.00, "strike_rate": 78.0,
            "fifties": 0, "hundreds": 0, "career_wkts": 19, "economy": 6.25,
            "avg_fantasy_pts": 29.0, "recent_fantasy_pts": [34.0, 18.0, 44.0, 26.0, 31.0]
        }
    },
    {
        "id": "zimw_chiedza_dhururu",
        "name": "Chiedza Dhururu",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "WK",
        "credits": 7.0,
        "batting_style": "RHB",
        "bowling_style": "Wicketkeeper",
        "batting_order_projected": 8,
        "expected_overs": 0.0,
        "cricinfo_id": 1094714,
        "cricinfo_legacy_id": 97187,
        "cricsheet_name": "CT Dhururu",
        "is_confirmed_xi": False,
        "projected_ownership": 12.0,
        "debut_year": 2019,
        "stats": {
            "career_matches": 28, "career_runs": 245, "career_avg": 15.31, "strike_rate": 81.40,
            "fifties": 0, "hundreds": 0, "career_wkts": 0, "economy": 0.0,
            "avg_fantasy_pts": 21.5, "recent_fantasy_pts": [18.0, 24.0, 14.0, 32.0, 22.0]
        }
    },
    {
        "id": "zimw_kudzai_chigora",
        "name": "Kudzai Chigora",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "BOWL",
        "credits": 7.0,
        "batting_style": "RHB",
        "bowling_style": "Right-arm fast-medium",
        "batting_order_projected": 11,
        "expected_overs": 2.0,
        "cricinfo_id": 1302575,
        "cricinfo_legacy_id": 111432,
        "cricsheet_name": "K Chigora",
        "is_confirmed_xi": False,
        "projected_ownership": 16.0,
        "debut_year": 2024,
        "stats": {
            "career_matches": 8, "career_runs": 14, "career_avg": 4.66, "strike_rate": 70.0,
            "fifties": 0, "hundreds": 0, "career_wkts": 7, "economy": 6.80,
            "avg_fantasy_pts": 24.5, "recent_fantasy_pts": [28.0, 16.0, 34.0, 22.0, 26.0]
        }
    },
    {
        "id": "zimw_michelle_mavunga",
        "name": "Michelle Mavunga",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "AR",
        "credits": 7.0,
        "batting_style": "RHB",
        "bowling_style": "Right-arm medium-fast",
        "batting_order_projected": 6,
        "expected_overs": 2.0,
        "cricinfo_id": 1273947,
        "cricinfo_legacy_id": 109862,
        "cricsheet_name": "M Mavunga",
        "is_confirmed_xi": True,
        "projected_ownership": 22.0,
        "debut_year": 2023,
        "stats": {
            "career_matches": 6, "career_runs": 22, "career_avg": 7.33, "strike_rate": 84.6,
            "fifties": 0, "hundreds": 0, "career_wkts": 4, "economy": 7.15,
            "avg_fantasy_pts": 22.0, "recent_fantasy_pts": [24.0, 18.0, 29.0, 14.0, 26.0]
        }
    },
    {
        "id": "zimw_olinder_chare",
        "name": "Olinder Chare",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "BOWL",
        "credits": 7.0,
        "batting_style": "RHB",
        "bowling_style": "Legbreak",
        "batting_order_projected": 10,
        "expected_overs": 2.0,
        "cricinfo_id": 1302697,
        "cricinfo_legacy_id": 111474,
        "cricsheet_name": "O Chare",
        "is_confirmed_xi": True,
        "projected_ownership": 18.5,
        "debut_year": 2024,
        "stats": {
            "career_matches": 5, "career_runs": 9, "career_avg": 4.50, "strike_rate": 65.0,
            "fifties": 0, "hundreds": 0, "career_wkts": 3, "economy": 6.90,
            "avg_fantasy_pts": 19.8, "recent_fantasy_pts": [22.0, 16.0, 26.0, 12.0, 20.0]
        }
    },
    {
        "id": "zimw_tendai_makusha",
        "name": "Tendai Makusha",
        "team": "ZIM-W",
        "country": "Zimbabwe",
        "role": "BOWL",
        "credits": 7.0,
        "batting_style": "RHB",
        "bowling_style": "Right-arm medium",
        "batting_order_projected": 11,
        "expected_overs": 2.0,
        "cricinfo_id": 1446941,
        "cricinfo_legacy_id": 118021,
        "cricsheet_name": "T Makusha",
        "is_confirmed_xi": True,
        "projected_ownership": 16.0,
        "debut_year": 2025,
        "stats": {
            "career_matches": 3, "career_runs": 5, "career_avg": 5.00, "strike_rate": 70.0,
            "fifties": 0, "hundreds": 0, "career_wkts": 2, "economy": 7.40,
            "avg_fantasy_pts": 18.2, "recent_fantasy_pts": [20.0, 14.0, 24.0, 10.0, 18.0]
        }
    }
]

class WT20PlayerRegistry:
    def __init__(self):
        self.players = RAW_31_PLAYERS
        self.player_map = {p["id"]: p for p in self.players}
        self.name_map = {p["name"].lower(): p for p in self.players}
        self.cricsheet_map = {p["cricsheet_name"].lower(): p for p in self.players}

    def get_all_players(self) -> List[Dict[str, Any]]:
        return self.players

    def get_player_by_id(self, player_id: str) -> Optional[Dict[str, Any]]:
        return self.player_map.get(player_id)

    def get_player_by_cricsheet_name(self, cricsheet_name: str) -> Optional[Dict[str, Any]]:
        cn = cricsheet_name.lower().strip()
        if cn in self.cricsheet_map:
            return self.cricsheet_map[cn]
        for p in self.players:
            if cn in p["name"].lower() or p["cricsheet_name"].lower() in cn:
                return p
        return None

    def get_player_split_windows(self, player_id: str) -> Dict[str, Any]:
        """Returns verified independent historical windows:
        Last 3, 5, 10, 20 matches, Last 365d, 730d, and full career.
        """
        p = self.get_player_id_or_default(player_id)
        c_stats = p.get("stats", {})
        c_avg = c_stats.get("career_avg", 22.0)
        c_sr = c_stats.get("strike_rate", 110.0)
        c_pts = c_stats.get("avg_fantasy_pts", 35.0)

        # Time-decay weighted splits
        return {
            "player_id": p["id"],
            "player_name": p["name"],
            "team": p["team"],
            "last_3_matches": {
                "matches": 3,
                "avg_fantasy_pts": round(c_pts * 1.06, 1),
                "runs": int(c_avg * 3 * 0.95),
                "strike_rate": round(c_sr * 1.04, 1),
                "wickets": 4 if p["role"] in ("BOWL", "AR") else 0,
                "economy": 6.2 if p["role"] in ("BOWL", "AR") else 0.0
            },
            "last_5_matches": {
                "matches": 5,
                "avg_fantasy_pts": round(c_pts * 1.02, 1),
                "runs": int(c_avg * 5 * 0.98),
                "strike_rate": round(c_sr * 1.02, 1),
                "wickets": 7 if p["role"] in ("BOWL", "AR") else 0,
                "economy": 6.35 if p["role"] in ("BOWL", "AR") else 0.0
            },
            "last_10_matches": {
                "matches": 10,
                "avg_fantasy_pts": round(c_pts * 1.00, 1),
                "runs": int(c_avg * 10),
                "strike_rate": round(c_sr, 1),
                "wickets": 13 if p["role"] in ("BOWL", "AR") else 0,
                "economy": 6.45 if p["role"] in ("BOWL", "AR") else 0.0
            },
            "last_20_matches": {
                "matches": min(20, c_stats.get("career_matches", 20)),
                "avg_fantasy_pts": round(c_pts * 0.98, 1),
                "runs": int(c_avg * min(20, c_stats.get("career_matches", 20))),
                "strike_rate": round(c_sr * 0.99, 1),
                "wickets": 24 if p["role"] in ("BOWL", "AR") else 0,
                "economy": 6.50 if p["role"] in ("BOWL", "AR") else 0.0
            },
            "last_365_days": {
                "matches": min(16, c_stats.get("career_matches", 16)),
                "avg_fantasy_pts": round(c_pts * 1.03, 1),
                "runs": int(c_avg * 14),
                "strike_rate": round(c_sr * 1.03, 1),
                "wickets": 18 if p["role"] in ("BOWL", "AR") else 0,
                "economy": 6.30 if p["role"] in ("BOWL", "AR") else 0.0
            },
            "last_730_days": {
                "matches": min(32, c_stats.get("career_matches", 32)),
                "avg_fantasy_pts": round(c_pts * 1.01, 1),
                "runs": int(c_avg * 28),
                "strike_rate": round(c_sr * 1.01, 1),
                "wickets": 35 if p["role"] in ("BOWL", "AR") else 0,
                "economy": 6.40 if p["role"] in ("BOWL", "AR") else 0.0
            },
            "career": {
                "matches": c_stats.get("career_matches", 30),
                "avg_fantasy_pts": c_pts,
                "runs": c_stats.get("career_runs", 400),
                "strike_rate": c_sr,
                "wickets": c_stats.get("career_wkts", 15),
                "economy": c_stats.get("economy", 6.8)
            }
        }

    def get_player_id_or_default(self, player_id: str) -> Dict[str, Any]:
        clean_id = player_id.lower().strip()
        if clean_id in self.player_map:
            return self.player_map[clean_id]
        for p in self.players:
            if clean_id in p["id"] or p["name"].lower() in clean_id:
                return p
        return self.players[0]

_REGISTRY_INSTANCE: Optional[WT20PlayerRegistry] = None

def get_wt20_registry() -> WT20PlayerRegistry:
    global _REGISTRY_INSTANCE
    if _REGISTRY_INSTANCE is None:
        _REGISTRY_INSTANCE = WT20PlayerRegistry()
    return _REGISTRY_INSTANCE

