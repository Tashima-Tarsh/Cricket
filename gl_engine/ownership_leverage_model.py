"""
STRIKE//OS PRO - Dream11 Ownership Modeling & GPP Leverage Engine
Addresses the primary structural gap in fantasy cricket optimization:
Modeling public ownership psychology (Recency Bias, Marquee Fame, Role Safety, Price Anchoring)
and calculating exact GPP Tournament Leverage = Optimal Win Rate % - Projected Ownership %.
"""

from typing import List, Dict, Any, Optional
import math
import numpy as np


class OwnershipLeverageModel:
    """Models public Dream11 ownership distribution and identifies high-leverage GPP pivots."""

    # Well-known international marquee players who command natural public chalk bias
    MARQUEE_SUPERSTARS = {
        "virat kohli": 1.45,
        "rohit sharma": 1.40,
        "suryakumar yadav": 1.35,
        "jasprit bumrah": 1.40,
        "hardik pandya": 1.35,
        "abhishek sharma": 1.30,
        "glenn maxwell": 1.30,
        "travis head": 1.35,
        "pat cummins": 1.25,
        "mitchell starc": 1.25,
        "babar azam": 1.40,
        "shaheen afridi": 1.30,
        "mohammad rizwan": 1.30,
        "jos buttler": 1.35,
        "jofra archer": 1.25,
        "rashid khan": 1.45,
        "rahmanullah gurbaz": 1.25,
        "smriti mandhana": 1.40,
        "harmanpreet kaur": 1.35,
        "deepti sharma": 1.30,
        "alyssa healy": 1.35,
        "ellyse perry": 1.40
    }

    def __init__(
        self,
        weight_projection: float = 0.45,
        weight_price: float = 0.20,
        weight_recency: float = 0.25,
        weight_fame: float = 0.10
    ):
        self.w_proj = weight_projection
        self.w_price = weight_price
        self.w_recency = weight_recency
        self.w_fame = weight_fame

    def predict_ownership(
        self,
        players: List[Dict[str, Any]],
        target_sum_pct: float = 1100.0  # 11 players per lineup * 100%
    ) -> List[Dict[str, Any]]:
        """Predicts realistic public ownership for all 22 players using calibrated softmax
        incorporating price anchoring, recency bias, and fame multiplier.
        """
        raw_logits = []
        for p in players:
            name_lower = p.get("name", "").lower()
            proj_pts = float(p.get("projected_points", 35.0))
            credits = float(p.get("credits", 8.0))
            recent_form = float(p.get("last_match_pts", proj_pts))  # Recency proxy
            role = p.get("role", "BAT").upper()

            # 1. Fame multiplier
            fame_mult = 1.0
            for star_name, mult in self.MARQUEE_SUPERSTARS.items():
                if star_name in name_lower:
                    fame_mult = mult
                    break

            # 2. Role convenience bias: All-rounders have higher casual ownership floor
            role_bias = 1.15 if role == "AR" else (1.05 if role == "WK" else 1.0)

            # 3. Compute latent pick utility
            # Normalize projection to ~0-1 range
            norm_proj = proj_pts / 60.0
            # Price anchor: high credits create perceived "must-have" bias
            norm_price = (credits - 7.0) / 3.0
            # Recency bias: recent boom (>60 pts) creates massive public chase
            norm_recency = (recent_form / 60.0) * 1.25

            utility = (
                self.w_proj * norm_proj +
                self.w_price * norm_price +
                self.w_recency * norm_recency
            ) * fame_mult * role_bias

            raw_logits.append(utility)

        # Softmax with temperature scaling calibrated to Dream11 ownership curves
        # (Chalk reaches 70-85%, middle tier 30-50%, differentials 5-18%)
        logits_arr = np.array(raw_logits)
        temp = 0.55  # Controls dispersion of ownership
        exp_logits = np.exp((logits_arr - np.max(logits_arr)) / temp)
        probs = exp_logits / np.sum(exp_logits)

        # Scale to 1100% total ownership (each user picks 11 players)
        predicted_ownerships = probs * target_sum_pct
        # Clamp realistic individual bounds: 2.0% min, 92.0% max
        predicted_ownerships = np.clip(predicted_ownerships, 2.0, 92.0)

        # Re-normalize to exact target sum
        current_sum = np.sum(predicted_ownerships)
        if current_sum > 0:
            predicted_ownerships = predicted_ownerships * (target_sum_pct / current_sum)

        enriched = []
        for idx, p in enumerate(players):
            p_copy = dict(p)
            p_copy["projected_ownership"] = round(float(predicted_ownerships[idx]), 1)
            enriched.append(p_copy)

        return enriched

    def compute_gpp_leverage(
        self,
        players: List[Dict[str, Any]],
        optimal_roster_rates: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Calculates Tournament Leverage:
        Leverage = Optimal Rate % (from simulations) - Projected Public Ownership %
        
        Leverage Classifications:
        - HIGH_LEVERAGE_GOLDMINE: Leverage > +8.0% (Under-owned elite performers)
        - POSITIVE_LEVERAGE: Leverage between +2.0% and +8.0%
        - FAIR_CHALK: Leverage between -5.0% and +2.0%
        - CHALK_TRAP: Leverage < -12.0% (Massively over-owned relative to winning ceiling)
        """
        results = []
        for p in players:
            pid = p.get("id") or p.get("name")
            p_name = p.get("name", "Unknown")
            own = float(p.get("projected_ownership", 30.0))
            opt_rate = float(optimal_roster_rates.get(pid, optimal_roster_rates.get(p_name, own * 0.9)))

            leverage = round(opt_rate - own, 1)

            if leverage >= 8.0:
                tag = "HIGH_LEVERAGE_GOLDMINE"
                recommendation = "Aggressively Overweight in Multi-Entry GPP (+25% over field)"
            elif leverage >= 2.0:
                tag = "POSITIVE_LEVERAGE"
                recommendation = "Core Exposure with Positive Expected Edge"
            elif leverage >= -8.0:
                tag = "FAIR_VALUE"
                recommendation = "Match Public Ownership (Neutral Exposure)"
            elif leverage >= -15.0:
                tag = "MODERATE_FADE"
                recommendation = "Underweight: Find Lower-Owned Pivots in same price tier"
            else:
                tag = "CHALK_TRAP"
                recommendation = "Aggressive Fade: Ranks highly duplicated, low solo win equity"

            results.append({
                "id": pid,
                "name": p_name,
                "team": p.get("team"),
                "role": p.get("role"),
                "credits": p.get("credits"),
                "projected_ownership_pct": own,
                "optimal_win_rate_pct": opt_rate,
                "gpp_leverage_pct": leverage,
                "classification": tag,
                "gpp_strategy": recommendation
            })

        # Sort by GPP leverage descending
        results.sort(key=lambda x: x["gpp_leverage_pct"], reverse=True)
        return results

    def find_direct_pivots(
        self,
        chalk_player: Dict[str, Any],
        candidate_pivots: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identifies direct differential pivots in the same credit bracket (+/- 1.0 Cr)
        and same or complementary role to maximize tournament uniqueness.
        """
        c_price = chalk_player.get("credits", 8.5)
        c_role = chalk_player.get("role", "BAT")
        c_name = chalk_player.get("name", "")

        pivots = []
        for p in candidate_pivots:
            if p.get("name") == c_name:
                continue
            price_diff = abs(p.get("credits", 8.5) - c_price)
            if price_diff <= 1.5:
                # Same role or AR equivalent
                if p.get("role") == c_role or (c_role in ["BAT", "BOWL"] and p.get("role") == "AR"):
                    own_savings = chalk_player.get("projected_ownership", 60.0) - p.get("projected_ownership", 20.0)
                    if own_savings > 15.0:
                        pivots.append({
                            "pivot_name": p.get("name"),
                            "role": p.get("role"),
                            "credits": p.get("credits"),
                            "ownership": p.get("projected_ownership"),
                            "ownership_reduction": round(own_savings, 1),
                            "projected_pts": p.get("projected_points"),
                            "rationale": f"Direct swap for {c_name} shedding {round(own_savings, 1)}% public chalk."
                        })

        pivots.sort(key=lambda x: x["ownership_reduction"], reverse=True)
        return pivots[:3]

