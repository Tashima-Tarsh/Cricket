"""Odds Ingestion and Mathematical De-vigging Engine.
Blueprint Section 5.6 & Skill Module 13.
Implements:
1. Multiplicative (Normalized) De-vig
2. Power (Logarithmic Margin) Method
3. Shin (Insider-Trading & Favorite-Longshot Bias) Method
4. Calibration Scoring: Brier Score, Log Loss, and Closing Line Value (CLV)
"""

import math
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

class OddsDeVigEngine:
    """Calculates true fair probabilities from bookmaker decimal odds."""

    @staticmethod
    def multiplicative(decimal_odds: List[float]) -> List[float]:
        """Multiplicative normalization: p_i* = p_i / sum(p_i)."""
        raw_probs = [1.0 / o for o in decimal_odds]
        overround = sum(raw_probs)
        return [p / overround for p in raw_probs]

    @staticmethod
    def power_method(decimal_odds: List[float], max_iter: int = 100, tol: float = 1e-6) -> List[float]:
        """Finds exponent k such that sum((1/o_i)^k) = 1.0."""
        raw_probs = [1.0 / o for o in decimal_odds]
        
        # Binary search for k
        low, high = 1.0, 3.0
        k = 1.0
        for _ in range(max_iter):
            mid = (low + high) / 2.0
            total = sum(math.pow(p, mid) for p in raw_probs)
            if abs(total - 1.0) < tol:
                k = mid
                break
            elif total > 1.0:
                low = mid
            else:
                high = mid
            k = mid

        fair_probs = [math.pow(p, k) for p in raw_probs]
        # Normalize to ensure exactly 1.0
        s = sum(fair_probs)
        return [p / s for p in fair_probs]

    @staticmethod
    def shin_method(decimal_odds: List[float], max_iter: int = 100, tol: float = 1e-6) -> Dict[str, Any]:
        """Shin's model assumes a proportion z of bettors possess insider knowledge.
        Solves for z and returns true fair probabilities.
        """
        raw_probs = [1.0 / o for o in decimal_odds]
        n = len(raw_probs)
        s = sum(raw_probs)
        
        if n != 2:
            # Fallback to power method for multi-way
            probs = OddsDeVigEngine.power_method(decimal_odds)
            return {"fair_probabilities": probs, "z_insider_factor": 0.0, "method": "power_fallback"}

        # Binary search for z in [0, s - 1]
        low = 0.0
        high = s - 1.0
        z = 0.0
        
        for _ in range(max_iter):
            mid = (low + high) / 2.0
            # Under Shin, p_i = (sqrt(z^2 + 4 * (1 - z) * (raw_i^2 / s)) - z) / (2 * (1 - z))
            p_est = []
            for r in raw_probs:
                denom = 2 * (1 - mid)
                num = math.sqrt(mid**2 + 4 * (1 - mid) * (r**2 / s)) - mid
                p_est.append(num / max(1e-9, denom))
            
            sum_p = sum(p_est)
            if abs(sum_p - 1.0) < tol:
                z = mid
                break
            elif sum_p > 1.0:
                low = mid
            else:
                high = mid
            z = mid

        fair_probs = []
        for r in raw_probs:
            denom = 2 * (1 - z)
            num = math.sqrt(z**2 + 4 * (1 - z) * (r**2 / s)) - z
            fair_probs.append(num / max(1e-9, denom))

        tot = sum(fair_probs)
        normalized_shin = [p / tot for p in fair_probs]
        return {
            "fair_probabilities": normalized_shin,
            "z_insider_factor": round(z, 5),
            "method": "shin"
        }

    @staticmethod
    def evaluate_model_vs_closing(
        model_prob: float,
        devigged_closing_prob: float,
        actual_outcome: int  # 1 if won, 0 if lost
    ) -> Dict[str, float]:
        """Calculates Brier score, Log Loss, and Closing Line Value (CLV).
        Blueprint Gate: Model must beat naive baseline and stay calibrated to sharp close.
        """
        brier_model = (model_prob - actual_outcome) ** 2
        brier_market = (devigged_closing_prob - actual_outcome) ** 2
        
        eps = 1e-12
        log_loss_model = -(actual_outcome * math.log(max(eps, model_prob)) + (1 - actual_outcome) * math.log(max(eps, 1.0 - model_prob)))
        log_loss_market = -(actual_outcome * math.log(max(eps, devigged_closing_prob)) + (1 - actual_outcome) * math.log(max(eps, 1.0 - devigged_closing_prob)))
        
        clv_advantage = model_prob - devigged_closing_prob

        return {
            "brier_score_model": round(brier_model, 4),
            "brier_score_market": round(brier_market, 4),
            "log_loss_model": round(log_loss_model, 4),
            "log_loss_market": round(log_loss_market, 4),
            "clv_advantage": round(clv_advantage, 4),
            "beats_market_calibration": brier_model <= brier_market
        }

    @classmethod
    def analyze_market(cls, decimal_a: float, decimal_b: float, team_a: str = "Team A", team_b: str = "Team B") -> Dict[str, Any]:
        """Provides side-by-side Multiplicative, Power, and Shin fair probabilities with overround analysis."""
        odds = [decimal_a, decimal_b]
        raw_prob_a = 1.0 / decimal_a
        raw_prob_b = 1.0 / decimal_b
        overround = (raw_prob_a + raw_prob_b) - 1.0
        margin_pct = round(overround * 100, 2)

        mult = cls.multiplicative(odds)
        power = cls.power_method(odds)
        shin = cls.shin_method(odds)

        return {
            "teams": {team_a: decimal_a, team_b: decimal_b},
            "overround_percent": margin_pct,
            "raw_implied_probabilities": {
                team_a: round(raw_prob_a * 100, 2),
                team_b: round(raw_prob_b * 100, 2)
            },
            "multiplicative_devig": {
                team_a: round(mult[0] * 100, 2),
                team_b: round(mult[1] * 100, 2)
            },
            "power_devig": {
                team_a: round(power[0] * 100, 2),
                team_b: round(power[1] * 100, 2)
            },
            "shin_devig": {
                team_a: round(shin["fair_probabilities"][0] * 100, 2),
                team_b: round(shin["fair_probabilities"][1] * 100, 2),
                "insider_factor_z": shin.get("z_insider_factor", 0.0)
            },
            "recommended_fair_prob": {
                team_a: round(shin["fair_probabilities"][0] * 100, 2),
                team_b: round(shin["fair_probabilities"][1] * 100, 2),
                "methodology": "Shin Model (Accounts for Favorite-Longshot Bias & Insider Leakage)"
            }
        }
