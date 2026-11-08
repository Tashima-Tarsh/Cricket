"""Cross-Platform Canonical Player ID and Alias Registry.
Blueprint Section 4 & Skill Module 2 (player-id-resolver).
Maps naming variations across Cricsheet (registry.people), Cricbuzz, ESPN Cricinfo, and Dream11.
"""

from typing import Dict, List, Optional, Tuple, Any
import re

CANONICAL_PLAYER_REGISTRY: Dict[str, Dict[str, Any]] = {
    # INDIA
    "samson_s": {
        "canonical_name": "Sanju Samson",
        "cricsheet_id": "8271",
        "team": "IND",
        "role": "WK",
        "bat_hand": "RHB",
        "bowl_style": None,
        "aliases": ["Sanju Samson", "S Samson", "SV Samson", "samson", "S.V. Samson"]
    },
    "sharma_a": {
        "canonical_name": "Abhishek Sharma",
        "cricsheet_id": "12086",
        "team": "IND",
        "role": "BAT",
        "bat_hand": "LHB",
        "bowl_style": "Slow left-arm orthodox",
        "aliases": ["Abhishek Sharma", "A Sharma", "abhishek-sharma", "A. Sharma"]
    },
    "kishan_i": {
        "canonical_name": "Ishan Kishan",
        "cricsheet_id": "10276",
        "team": "IND",
        "role": "WK",
        "bat_hand": "LHB",
        "bowl_style": None,
        "aliases": ["Ishan Kishan", "I Kishan", "ishan-kishan", "I. Kishan"]
    },
    "iyer_s": {
        "canonical_name": "Shreyas Iyer",
        "cricsheet_id": "9428",
        "team": "IND",
        "role": "BAT",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm legbreak",
        "aliases": ["Shreyas Iyer", "SS Iyer", "S Iyer", "shreyas-iyer", "S.S. Iyer"]
    },
    "varma_t": {
        "canonical_name": "Tilak Varma",
        "cricsheet_id": "14504",
        "team": "IND",
        "role": "BAT",
        "bat_hand": "LHB",
        "bowl_style": "Right-arm offbreak",
        "aliases": ["Tilak Varma", "N Tilak Varma", "T Varma", "tilak-varma"]
    },
    "dhir_n": {
        "canonical_name": "Naman Dhir",
        "cricsheet_id": "36139",
        "team": "IND",
        "role": "BAT",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm offbreak",
        "aliases": ["Naman Dhir", "N Dhir", "naman-dhir"]
    },
    "reddy_nk": {
        "canonical_name": "Nitish Kumar Reddy",
        "cricsheet_id": "14701",
        "team": "IND",
        "role": "AR",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm medium-fast",
        "aliases": ["Nitish Kumar Reddy", "Nitish Reddy", "NK Reddy", "nitish-kumar-reddy"]
    },
    "patel_axar": {
        "canonical_name": "Axar Patel",
        "cricsheet_id": "9429",
        "team": "IND",
        "role": "AR",
        "bat_hand": "LHB",
        "bowl_style": "Slow left-arm orthodox",
        "aliases": ["Axar Patel", "AR Patel", "A Patel", "axar-patel", "Akshar Patel"]
    },
    "bishnoi_r": {
        "canonical_name": "Ravi Bishnoi",
        "cricsheet_id": "14505",
        "team": "IND",
        "role": "BOWL",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm legbreak googly",
        "aliases": ["Ravi Bishnoi", "R Bishnoi", "ravi-bishnoi"]
    },
    "yadav_prince": {
        "canonical_name": "Prince Yadav",
        "cricsheet_id": "42109",
        "team": "IND",
        "role": "BOWL",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm medium-fast",
        "aliases": ["Prince Yadav", "P Yadav", "prince-yadav"]
    },
    "yadav_mayank": {
        "canonical_name": "Mayank Yadav",
        "cricsheet_id": "38920",
        "team": "IND",
        "role": "BOWL",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm fast",
        "aliases": ["Mayank Yadav", "M Yadav", "mayank-yadav"]
    },

    # WEST INDIES
    "hope_s": {
        "canonical_name": "Shai Hope",
        "cricsheet_id": "9248",
        "team": "WI",
        "role": "WK",
        "bat_hand": "RHB",
        "bowl_style": None,
        "aliases": ["Shai Hope", "SD Hope", "S Hope", "shai-hope"]
    },
    "andrew_j": {
        "canonical_name": "Jewel Andrew",
        "cricsheet_id": "51201",
        "team": "WI",
        "role": "BAT",
        "bat_hand": "RHB",
        "bowl_style": None,
        "aliases": ["Jewel Andrew", "J Andrew", "jewel-andrew"]
    },
    "hetmyer_s": {
        "canonical_name": "Shimron Hetmyer",
        "cricsheet_id": "10280",
        "team": "WI",
        "role": "BAT",
        "bat_hand": "LHB",
        "bowl_style": None,
        "aliases": ["Shimron Hetmyer", "SO Hetmyer", "S Hetmyer", "shimron-hetmyer"]
    },
    "powell_r": {
        "canonical_name": "Rovman Powell",
        "cricsheet_id": "10281",
        "team": "WI",
        "role": "BAT",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm medium",
        "aliases": ["Rovman Powell", "R Powell", "rovman-powell"]
    },
    "rutherford_s": {
        "canonical_name": "Sherfane Rutherford",
        "cricsheet_id": "11920",
        "team": "WI",
        "role": "BAT",
        "bat_hand": "LHB",
        "bowl_style": "Right-arm medium",
        "aliases": ["Sherfane Rutherford", "SE Rutherford", "S Rutherford", "sherfane-rutherford"]
    },
    "shepherd_r": {
        "canonical_name": "Romario Shepherd",
        "cricsheet_id": "12904",
        "team": "WI",
        "role": "AR",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm fast-medium",
        "aliases": ["Romario Shepherd", "R Shepherd", "romario-shepherd"]
    },
    "paul_k": {
        "canonical_name": "Keemo Paul",
        "cricsheet_id": "10282",
        "team": "WI",
        "role": "AR",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm fast-medium",
        "aliases": ["Keemo Paul", "K Paul", "keemo-paul"]
    },
    "springer_s": {
        "canonical_name": "Shamar Springer",
        "cricsheet_id": "10283",
        "team": "WI",
        "role": "AR",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm medium-fast",
        "aliases": ["Shamar Springer", "SK Springer", "S Springer", "shamar-springer"]
    },
    "chase_r": {
        "canonical_name": "Roston Chase",
        "cricsheet_id": "8902",
        "team": "WI",
        "role": "AR",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm offbreak",
        "aliases": ["Roston Chase", "RL Chase", "R Chase", "roston-chase"]
    },
    "motie_g": {
        "canonical_name": "Gudakesh Motie",
        "cricsheet_id": "9901",
        "team": "WI",
        "role": "BOWL",
        "bat_hand": "LHB",
        "bowl_style": "Slow left-arm orthodox",
        "aliases": ["Gudakesh Motie", "G Motie", "gudakesh-motie"]
    },
    "joseph_s": {
        "canonical_name": "Shamar Joseph",
        "cricsheet_id": "48901",
        "team": "WI",
        "role": "BOWL",
        "bat_hand": "RHB",
        "bowl_style": "Right-arm fast",
        "aliases": ["Shamar Joseph", "S Joseph", "shamar-joseph"]
    }
}

class CanonicalPlayerResolver:
    """Resolves arbitrary raw strings into verified canonical player IDs."""

    def __init__(self):
        self.alias_map: Dict[str, str] = {}
        for canon_id, profile in CANONICAL_PLAYER_REGISTRY.items():
            self.alias_map[profile["canonical_name"].lower()] = canon_id
            for alias in profile["aliases"]:
                self.alias_map[alias.lower().replace("-", " ").strip()] = canon_id
                self.alias_map[alias.lower().replace(".", "").strip()] = canon_id

    def resolve(self, raw_name: str) -> Optional[Dict[str, Any]]:
        clean = raw_name.lower().replace("-", " ").replace(".", "").strip()
        canon_id = self.alias_map.get(clean)
        if canon_id:
            profile = CANONICAL_PLAYER_REGISTRY[canon_id].copy()
            profile["player_id"] = canon_id
            return profile
        
        # Partial token match fallback
        tokens = set(clean.split())
        for alias_key, cid in self.alias_map.items():
            alias_tokens = set(alias_key.split())
            if len(tokens.intersection(alias_tokens)) >= 2:
                profile = CANONICAL_PLAYER_REGISTRY[cid].copy()
                profile["player_id"] = cid
                return profile

        return None
