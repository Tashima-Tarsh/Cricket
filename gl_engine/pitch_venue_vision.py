"""Pitch & Venue Vision Intelligence Engine.
Implements the core analytical capabilities of:
- HawkeyeStats & CricketTracker: Ball trajectory, length (Yorker, Full, Good Length, Short) & line heatmaps.
- Cricket-Vision-AI, sports_cv & SportsVision: Computer vision pitch degradation, bounce profiling & wear tracking.
- cricket-analytics, cricket-performance-intelligence, cricket-analysis & Cricket_Analytics:
  Venue dimensions, boundary geometry, par score curves, and pace vs spin wicket split.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
import numpy as np


class DeliveryTrajectory(BaseModel):
    length: str  # "Yorker", "Full", "Good Length", "Back of Length", "Short"
    line: str    # "Outside Off", "Fourth Stump", "Stumps", "Down Leg"
    release_speed_kmh: float = 135.0
    seam_deviation_degrees: float = 0.0
    swing_deviation_degrees: float = 0.0
    pitch_zone_x: float = 0.0  # lateral displacement (-1.5m to +1.5m from centre)
    pitch_zone_y: float = 6.0  # distance from stumps (0 to 20m)
    wicket_probability: float = 0.05
    dot_probability: float = 0.40
    boundary_probability: float = 0.15


class PitchProfile(BaseModel):
    name: str
    city: str
    soil_type: str = "Red Soil"  # "Red Soil", "Black Soil", "Hybrid Clay"
    hardness_index: float = 8.5  # 1 (soft/sluggish) to 10 (rock hard, fast carry)
    grass_cover_pct: float = 12.0
    expected_turn_degrees: float = 2.4
    expected_seam_movement_mm: float = 4.2
    avg_first_innings: int = 180
    chasing_win_pct: float = 54.0
    pace_wickets_pct: float = 62.0
    spin_wickets_pct: float = 38.0
    dew_susceptibility: float = 0.40  # 0.0 (dry) to 1.0 (heavy dew)


class VenueBoundaryGeometry(BaseModel):
    square_leg_m: float = 65.0
    midwicket_m: float = 68.0
    long_on_m: float = 72.0
    straight_m: float = 74.0
    long_off_m: float = 72.0
    cover_m: float = 68.0
    point_m: float = 64.0
    third_man_m: float = 60.0
    fine_leg_m: float = 60.0
    altitude_m: float = 505.0  # altitude affects air density & ball carry


class PitchVenueVisionEngine:
    def __init__(self, pitch_profile: Optional[PitchProfile] = None, boundary_geo: Optional[VenueBoundaryGeometry] = None):
        self.pitch = pitch_profile or self._default_hyderabad_profile()
        self.geometry = boundary_geo or VenueBoundaryGeometry()

    def _default_hyderabad_profile(self) -> PitchProfile:
        return PitchProfile(
            name="Rajiv Gandhi International Cricket Stadium",
            city="Hyderabad",
            soil_type="Red Soil with Black Soil Base",
            hardness_index=9.0,
            grass_cover_pct=8.0,
            expected_turn_degrees=2.1,
            expected_seam_movement_mm=4.8,
            avg_first_innings=192,
            chasing_win_pct=56.0,
            pace_wickets_pct=64.0,
            spin_wickets_pct=36.0,
            dew_susceptibility=0.38
        )

    def analyze_hawkeye_lengths(self, bowler_type: str = "Pace") -> Dict[str, Any]:
        """Simulates Hawkeye length distribution and dismissal clusters by bowling style."""
        if bowler_type.lower() in ["pace", "fast", "medium"]:
            lengths = {
                "Yorker (0-2m)": {"usage_pct": 14.0, "wicket_rate": 0.095, "economy": 6.8},
                "Full (2-4m)": {"usage_pct": 24.0, "wicket_rate": 0.065, "economy": 9.4},
                "Good Length (4-7m)": {"usage_pct": 42.0, "wicket_rate": 0.080, "economy": 7.2},
                "Back of Length (7-9m)": {"usage_pct": 15.0, "wicket_rate": 0.045, "economy": 8.0},
                "Short / Bouncer (>9m)": {"usage_pct": 5.0, "wicket_rate": 0.075, "economy": 9.8}
            }
        else:  # Spin
            lengths = {
                "Full (2-3.5m)": {"usage_pct": 52.0, "wicket_rate": 0.075, "economy": 7.5},
                "Good Length (3.5-5.5m)": {"usage_pct": 34.0, "wicket_rate": 0.082, "economy": 6.9},
                "Short (>5.5m)": {"usage_pct": 14.0, "wicket_rate": 0.035, "economy": 10.2}
            }

        return {
            "bowler_type": bowler_type,
            "optimal_length": "Good Length (4-7m)" if bowler_type == "Pace" else "Good Length (3.5-5.5m)",
            "highest_wicket_length": "Yorker (0-2m)" if bowler_type == "Pace" else "Good Length (3.5-5.5m)",
            "length_breakdown": lengths
        }

    def compute_boundary_risk_zones(self) -> Dict[str, Any]:
        """Calculates boundary clearing probability by field sector based on stadium dimensions."""
        dimensions = self.geometry.model_dump()
        altitude_boost = 1.0 + (self.geometry.altitude_m / 10000.0)  # thinner air carries further

        boundary_ratings = {}
        for sector, distance in dimensions.items():
            if sector == "altitude_m":
                continue
            # Base clearing index: shorter distance => higher boundary index
            clear_prob = round(min(0.95, (85.0 - distance) / 30.0 * altitude_boost), 2)
            boundary_ratings[sector] = {
                "distance_meters": distance,
                "six_clearing_index": clear_prob,
                "risk_category": "High Vulnerability" if clear_prob >= 0.65 else (
                    "Moderate" if clear_prob >= 0.45 else "Protected / Safe"
                )
            }

        return {
            "venue_name": self.pitch.name,
            "altitude_meters": self.geometry.altitude_m,
            "shortest_boundary": min(dimensions.items(), key=lambda x: x[1] if x[0] != "altitude_m" else 999),
            "longest_boundary": max(dimensions.items(), key=lambda x: x[1] if x[0] != "altitude_m" else 0),
            "sectors": boundary_ratings
        }

    def evaluate_pitch_degradation(self, current_over: float, innings: int = 1) -> Dict[str, Any]:
        """Models pitch wear, seam movement reduction, and dew impact across 40 overs."""
        # Seam movement drops as ball softens (overs 1-6 have max seam)
        seam_wear_factor = max(0.35, 1.0 - (current_over / 20.0) * 0.65)
        # Turn increases in middle overs (overs 7-15) unless dew strikes in 2nd innings
        if innings == 1:
            spin_turn_factor = 1.0 + min(0.35, (current_over / 15.0) * 0.25)
            dew_impact = 0.0
        else:
            # 2nd innings dew reduces grip by up to 40% after over 8
            dew_impact = self.pitch.dew_susceptibility * min(1.0, current_over / 10.0)
            spin_turn_factor = max(0.60, 1.15 - (dew_impact * 0.45))

        # Expected run rate multiplier
        batting_ease_factor = round(1.0 + (dew_impact * 0.18) + ((1.0 - seam_wear_factor) * 0.10), 2)

        return {
            "current_over": current_over,
            "innings": innings,
            "seam_movement_remaining_mm": round(self.pitch.expected_seam_movement_mm * seam_wear_factor, 1),
            "spin_turn_remaining_degrees": round(self.pitch.expected_turn_degrees * spin_turn_factor, 1),
            "dew_active": dew_impact > 0.15,
            "dew_severity_pct": round(dew_impact * 100, 1),
            "batting_ease_multiplier": batting_ease_factor,
            "tactical_guidance": (
                "Pacers get early swing in overs 1-5; target top-order batters."
                if current_over <= 5 else (
                    "Dew severely impairs finger spin grip; favor pacers with cutters and top-order chasing batters."
                    if dew_impact > 0.25 else "Middle overs spin squeeze active; boundary rate drops."
                )
            )
        }

