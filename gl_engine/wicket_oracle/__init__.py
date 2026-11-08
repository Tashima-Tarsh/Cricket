"""
THENITISHKR-SPORTS Wicket Oracle Module.
Integration of gmalbert/cricket capabilities into STRIKE//OS / THENITISHKR-SPORTS.
"""

from .oracle_engine import WicketOracleEngine, compute_fractional_kelly, convert_prob_to_american_odds

__all__ = ["WicketOracleEngine", "compute_fractional_kelly", "convert_prob_to_american_odds"]
