"""
nlp_deconstructor.py
LLM Pitch & Toss Intelligence Agent (Real-Time NLP Sprint Deconstructor).

Parses unstructured pitch reports and captain post-toss commentary into
rigorous quantitative mathematical modifiers for the simulation and optimization layers.
"""

from typing import Dict, Any, List
import re

class NLPCommentaryDeconstructor:
    """Deconstructs pre-match text into quantitative parameters."""

    def __init__(self):
        pass

    def deconstruct_pitch_report(self, pitch_text: str) -> Dict[str, Any]:
        """Converts qualitative commentary into exact mathematical modifiers."""
        text = pitch_text.lower()
        
        # Base modifiers
        modifiers = {
            "seam_movement_pct": 0.0,
            "spin_grip_pct": 0.0,
            "bounce_carry_rating": 5.0, # 1 to 10
            "par_score_adjustment": 0,
            "pitch_class": "BALANCED",
            "extracted_keywords": []
        }

        # 1. Pitch Surface Classification
        if any(w in text for w in ["dry", "dusty", "turn", "spin", "cracks", "black soil", "slow"]):
            modifiers["spin_grip_pct"] += 25.0
            modifiers["par_score_adjustment"] -= 15
            modifiers["pitch_class"] = "DRY_TURNER"
            modifiers["extracted_keywords"].append("DRY_TURN")
            
        if any(w in text for w in ["grass", "green", "seam", "swing", "fresh", "overhead"]):
            modifiers["seam_movement_pct"] += 20.0
            modifiers["par_score_adjustment"] -= 10
            modifiers["pitch_class"] = "GREEN_SEAM"
            modifiers["extracted_keywords"].append("GREEN_SEAM")

        if any(w in text for w in ["flat", "belter", "batting paradise", "hard", "pristine", "rolled well"]):
            modifiers["par_score_adjustment"] += 20
            modifiers["bounce_carry_rating"] = 9.0
            modifiers["pitch_class"] = "FLAT_HIGHWAY"
            modifiers["extracted_keywords"].append("FLAT_HIGHWAY")

        # 2. Bounce & Carry Detection
        if any(w in text for w in ["bounce", "shoulder", "tall", "carry", "skid"]):
            modifiers["bounce_carry_rating"] = 8.5
            modifiers["extracted_keywords"].append("HIGH_BOUNCE")

        # 3. 2nd Innings Conditions (Dew / Skid)
        if any(w in text for w in ["dew", "skid", "under lights", "night"]):
            modifiers["extracted_keywords"].append("DEW_SKID_ADVANTAGE")

        return modifiers

    def deconstruct_captain_statement(self, statement: str) -> Dict[str, Any]:
        """Detects dead-rubber tactics, batting demotions, and bowling rest rotations."""
        text = statement.lower()
        
        tactics = {
            "captain_rest_or_demotion": False,
            "middle_order_boost_pct": 0.0,
            "captain_balls_penalty_pct": 0.0,
            "bowler_rest_detected": False,
            "target_total_stated": None,
            "tactical_flags": []
        }

        # Detect captain demoting self or prioritizing middle order
        if any(w in text for w in ["middle order", "game time", "experiment", "testing bench"]):
            tactics["captain_rest_or_demotion"] = True
            tactics["captain_balls_penalty_pct"] = -35.0
            tactics["middle_order_boost_pct"] = +40.0
            tactics["tactical_flags"].append("MIDDLE_ORDER_PROMOTION")

        # Detect rested player
        if any(w in text for w in ["resting", "rests", "rested", "misses out", "niggle"]):
            tactics["bowler_rest_detected"] = True
            tactics["tactical_flags"].append("REST_ROTATION")

        # Stated totals (e.g., 'looking at 180 plus' or 'looking for 200')
        target_m = re.search(r'looking (?:at|for) (\d{3})', text)
        if target_m:
            tactics["target_total_stated"] = int(target_m.group(1))

        return tactics

    def process_pre_match_intel(self, pitch_report: str, toss_quote: str) -> Dict[str, Any]:
        """Unified runner that processes both pitch and toss text."""
        pitch_mods = self.deconstruct_pitch_report(pitch_report)
        toss_mods = self.deconstruct_captain_statement(toss_quote)
        
        return {
            "pitch_modifiers": pitch_mods,
            "tactic_modifiers": toss_mods,
            "derived_archetype": (
                "ROAD_HIGHWAY" if pitch_mods["par_score_adjustment"] > 10 else (
                    "SPIN_CHOKE_MINEFIELD" if pitch_mods["spin_grip_pct"] > 20 else "BALANCED"
                )
            )
        }

_DECONSTRUCTOR_INSTANCE = None

def get_nlp_deconstructor() -> NLPCommentaryDeconstructor:
    global _DECONSTRUCTOR_INSTANCE
    if _DECONSTRUCTOR_INSTANCE is None:
        _DECONSTRUCTOR_INSTANCE = NLPCommentaryDeconstructor()
    return _DECONSTRUCTOR_INSTANCE

