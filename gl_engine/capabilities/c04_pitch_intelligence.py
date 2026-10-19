"""Capability 4: cricket-pitch-intelligence
Analyse historical venue conditions, pitch reports, Hawkeye delivery lengths, boundary geometry, and phase splits.
"""
from typing import Dict, Any
from ..models import VenueConditions
from ..pitch_venue_vision import PitchVenueVisionEngine, PitchProfile


class CricketPitchIntelligence:
    def __init__(self, venue: VenueConditions):
        self.venue = venue
        self.vision_engine = PitchVenueVisionEngine(
            PitchProfile(
                name=venue.name,
                city=venue.city,
                avg_first_innings=venue.avg_first_innings_score,
                pace_wickets_pct=venue.pace_wickets_pct,
                spin_wickets_pct=venue.spin_wickets_pct,
                dew_susceptibility=venue.dew_factor
            )
        )

    def execute(self) -> Dict[str, Any]:
        hawkeye_pace = self.vision_engine.analyze_hawkeye_lengths("Pace")
        hawkeye_spin = self.vision_engine.analyze_hawkeye_lengths("Spin")
        boundary_risk = self.vision_engine.compute_boundary_risk_zones()
        degradation = self.vision_engine.evaluate_pitch_degradation(current_over=10.0, innings=2)

        return {
            "capability": "cricket-pitch-intelligence",
            "venue": self.venue.name,
            "city": self.venue.city,
            "avg_first_innings_score": self.venue.avg_first_innings_score,
            "surface_profile": self.venue.pitch_nature,
            "pace_vs_spin_wickets": {
                "pace_pct": self.venue.pace_wickets_pct,
                "spin_pct": self.venue.spin_wickets_pct,
                "ratio": round(self.venue.pace_wickets_pct / max(1.0, self.venue.spin_wickets_pct), 2)
            },
            "hawkeye_analytics": {
                "pace": hawkeye_pace,
                "spin": hawkeye_spin
            },
            "boundary_geometry": boundary_risk,
            "in_play_degradation": degradation,
            "key_fantasy_takeaway": (
                f"Pacers account for {self.venue.pace_wickets_pct}% of dismissals at {self.venue.name}. "
                "Death pacers with hard yorkers and express bounce have highest wicket ceiling."
            )
        }
