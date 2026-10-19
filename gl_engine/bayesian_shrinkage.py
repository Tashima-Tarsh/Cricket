"""Hierarchical Bayesian Shrinkage and Player Form Model.
Blueprint Section 5.2 & Skill Module 3 (player-form-model).
Implements:
1. Beta-Binomial / Gamma-Poisson shrinkage for low sample sizes (<40 balls).
2. Exponential recency decay weighting.
3. League-strength adjustment scaling.
"""

from typing import Dict, List, Any, Optional
import math
import numpy as np

class HierarchicalPlayerModel:
    """Computes calibrated, shrunk player metrics to eliminate small-sample noise."""

    LEAGUE_STRENGTH_MULTIPLIER = {
        "IPL": 1.00,
        "T20I_TIER1": 0.98,
        "BBL": 0.92,
        "THE_HUNDRED": 0.90,
        "PSL": 0.90,
        "CPL": 0.88,
        "SA20": 0.89,
        "MLC": 0.86,
        "T20I_TIER2": 0.82,
        "DOMESTIC_OTHER": 0.80
    }

    ROLE_PRIORS = {
        "OPENER": {"boundary_rate": 0.185, "dot_rate": 0.360, "wicket_rate": 0.045, "prior_strength": 45.0},
        "TOP_ORDER": {"boundary_rate": 0.170, "dot_rate": 0.350, "wicket_rate": 0.042, "prior_strength": 40.0},
        "MIDDLE_ACCELERATOR": {"boundary_rate": 0.160, "dot_rate": 0.330, "wicket_rate": 0.052, "prior_strength": 35.0},
        "DEATH_FINISHER": {"boundary_rate": 0.220, "dot_rate": 0.310, "wicket_rate": 0.080, "prior_strength": 30.0},
        "SPIN_BOWLER": {"dot_rate": 0.370, "boundary_rate": 0.135, "wicket_rate": 0.052, "prior_strength": 50.0},
        "PACE_BOWLER": {"dot_rate": 0.410, "boundary_rate": 0.155, "wicket_rate": 0.058, "prior_strength": 50.0},
    }

    @staticmethod
    def apply_shrinkage(
        observed_events: int,
        observed_balls: int,
        prior_rate: float,
        prior_strength: float
    ) -> Dict[str, float]:
        """Beta-Binomial shrinkage:
        posterior_rate = (prior_strength * prior_rate + observed_events) / (prior_strength + observed_balls)
        Calculates 90% credible interval [q05, q95].
        """
        if observed_balls == 0:
            return {
                "posterior_rate": round(prior_rate, 4),
                "lower_ci_90": round(max(0.0, prior_rate - 0.04), 4),
                "upper_ci_90": round(prior_rate + 0.04, 4),
                "shrinkage_weight": 1.0,
                "confidence_label": "PRIOR_ONLY (Thin Data)"
            }

        shrunk_rate = (prior_strength * prior_rate + observed_events) / (prior_strength + observed_balls)
        
        # Approximate Beta variance
        alpha_post = prior_strength * prior_rate + observed_events
        beta_post = prior_strength * (1.0 - prior_rate) + (observed_balls - observed_events)
        var = (alpha_post * beta_post) / ((alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1.0))
        std_err = math.sqrt(max(1e-6, var))
        
        lower_ci = max(0.0, shrunk_rate - 1.645 * std_err)
        upper_ci = min(1.0, shrunk_rate + 1.645 * std_err)

        shrinkage_weight = prior_strength / (prior_strength + observed_balls)
        
        confidence = "HIGH" if observed_balls >= 120 else ("MODERATE" if observed_balls >= 40 else "SHRUNK_TOWARD_PRIOR")

        return {
            "posterior_rate": round(shrunk_rate, 4),
            "lower_ci_90": round(lower_ci, 4),
            "upper_ci_90": round(upper_ci, 4),
            "shrinkage_weight": round(shrinkage_weight, 3),
            "confidence_label": confidence
        }

    @classmethod
    def shrink_rate(
        cls,
        sample_size: int = 25,
        observed_success_rate: float = 0.45,
        role: str = "TOP_ORDER",
        league: str = "IPL"
    ) -> Dict[str, Any]:
        """Convenience method shrinking an observed rate over a sample size."""
        role_key = role.upper() if role.upper() in cls.ROLE_PRIORS else "TOP_ORDER"
        prior = cls.ROLE_PRIORS[role_key]
        mult = cls.LEAGUE_STRENGTH_MULTIPLIER.get(league.upper(), 1.0)
        adj_balls = int(round(sample_size * mult))
        adj_events = int(round(sample_size * observed_success_rate * mult))
        res = cls.apply_shrinkage(
            observed_events=adj_events,
            observed_balls=adj_balls,
            prior_rate=prior["boundary_rate"],
            prior_strength=prior["prior_strength"]
        )
        res["role_prior_baseline"] = prior["boundary_rate"]
        res["league_strength_multiplier"] = mult
        res["input_sample_size"] = sample_size
        res["input_observed_rate"] = observed_success_rate
        return res

    @classmethod
    def evaluate_player_form(
        cls,
        player_name: str,
        role: str,
        recent_matches: List[Dict[str, Any]],
        decay_factor: float = 0.85
    ) -> Dict[str, Any]:
        """Calculates exponentially recency-weighted metrics with Bayesian shrinkage."""
        role_key = role.upper() if role.upper() in cls.ROLE_PRIORS else "TOP_ORDER"
        prior = cls.ROLE_PRIORS[role_key]

        weighted_balls = 0.0
        weighted_boundaries = 0.0
        weighted_dots = 0.0

        for i, match in enumerate(recent_matches):
            weight = decay_factor ** i
            league = match.get("league", "IPL")
            multiplier = cls.LEAGUE_STRENGTH_MULTIPLIER.get(league, 0.85)

            balls = match.get("balls", 0) * multiplier
            boundaries = match.get("boundaries", 0) * multiplier
            dots = match.get("dots", 0) * multiplier

            weighted_balls += balls * weight
            weighted_boundaries += boundaries * weight
            weighted_dots += dots * weight

        boundary_shrunk = cls.apply_shrinkage(
            observed_events=int(round(weighted_boundaries)),
            observed_balls=int(round(weighted_balls)),
            prior_rate=prior["boundary_rate"],
            prior_strength=prior["prior_strength"]
        )

        return {
            "player_name": player_name,
            "role": role,
            "weighted_balls_sample": round(weighted_balls, 1),
            "boundary_rate_calibrated": boundary_shrunk["posterior_rate"],
            "credible_interval_90": [boundary_shrunk["lower_ci_90"], boundary_shrunk["upper_ci_90"]],
            "confidence": boundary_shrunk["confidence_label"],
            "shrinkage_impact": f"{round(boundary_shrunk['shrinkage_weight'] * 100, 1)}% regressed to {role_key} prior"
        }

HierarchicalBayesianShrinkage = HierarchicalPlayerModel
