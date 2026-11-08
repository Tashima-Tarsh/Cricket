"""
Chaos Intelligence Engine.
Looks at ALL chaos factors (weather, umpire, pitch, player tendencies, historical patterns,
venue quirks, toss impact, crowd pressure, travel fatigue, match importance) and applies
intelligent adjustments to player projections for Grand League optimization.
"""
from typing import Dict, List

import numpy as np
import pandas as pd


class ChaosIntelligence:
    def __init__(self):
        self.weather_data = {}
        self.umpire_data = {}
        self.pitch_conditions = {}
        self.player_tendencies = {}
        self.historical_chaos_events = []

    def load_all_factors(self, match_context: Dict) -> Dict:
        """Load ALL chaos factors for a specific match."""
        factors = {
            "weather": self._analyze_weather(match_context),
            "umpire": self._analyze_umpires(match_context),
            "pitch": self._analyze_pitch(match_context),
            "player_form": self._analyze_player_form(match_context),
            "historical_patterns": self._analyze_historical_patterns(match_context),
            "venue_quirks": self._analyze_venue_quirks(match_context),
            "toss_impact": self._analyze_toss_impact(match_context),
            "crowd_pressure": self._analyze_crowd_pressure(match_context),
            "travel_fatigue": self._analyze_travel_fatigue(match_context),
            "match_importance": self._analyze_match_importance(match_context),
        }
        return factors

    def _analyze_weather(self, match_context: Dict) -> Dict:
        weather = {
            "rain_probability": match_context.get("rain_prob", 0),
            "humidity": match_context.get("humidity", 50),
            "wind_speed": match_context.get("wind_speed", 0),
            "cloud_cover": match_context.get("cloud_cover", 0),
            "temperature": match_context.get("temperature", 25),
            "dew_factor": match_context.get("dew_factor", "LOW"),
            "is_night_match": match_context.get("is_night_match", False),
        }
        weather["chaos_score"] = self._calculate_weather_chaos(weather)
        weather["dls_risk"] = weather["rain_probability"] > 40
        weather["spin_penalty"] = weather["dew_factor"] == "HIGH" and weather["is_night_match"]
        return weather

    def _calculate_weather_chaos(self, weather: Dict) -> float:
        chaos = 0.0
        if 30 < weather["rain_probability"] < 70:
            chaos += 0.3
        elif weather["rain_probability"] > 70:
            chaos += 0.1
        if weather["dew_factor"] == "HIGH":
            chaos += 0.2
        if weather["wind_speed"] > 20:
            chaos += 0.15
        if weather["humidity"] > 75:
            chaos += 0.1
        return min(1.0, chaos)

    def _analyze_umpires(self, match_context: Dict) -> Dict:
        umpires = match_context.get("umpires", [])
        umpire_analysis = {
            "strictness_index": 0.5,
            "lbw_rate": 0.5,
            "driven_to_drs": 0.0,
            "player_specific_bias": {},
        }
        if umpires:
            strictness_scores = [u.get("strictness_index", 0.5) for u in umpires]
            umpire_analysis["strictness_index"] = float(np.mean(strictness_scores))
            lbw_rates = [u.get("lbw_given_rate", 0.5) for u in umpires]
            umpire_analysis["lbw_rate"] = float(np.mean(lbw_rates))
            drs_rates = [u.get("drs_overturn_rate", 0.3) for u in umpires]
            umpire_analysis["driven_to_drs"] = float(np.mean(drs_rates))
        umpire_analysis["chaos_score"] = self._calculate_umpire_chaos(umpire_analysis)
        return umpire_analysis

    def _calculate_umpire_chaos(self, umpire: Dict) -> float:
        chaos = 0.0
        if umpire["driven_to_drs"] > 0.4:
            chaos += 0.3
        if umpire["strictness_index"] > 0.8 or umpire["strictness_index"] < 0.2:
            chaos += 0.2
        return min(1.0, chaos)

    def _analyze_pitch(self, match_context: Dict) -> Dict:
        pitch = {
            "type": match_context.get("pitch_type", "neutral"),
            "pace_friendly": match_context.get("pace_friendly", False),
            "spin_friendly": match_context.get("spin_friendly", False),
            "bounce": match_context.get("bounce", "medium"),
            "wear_rate": match_context.get("wear_rate", 0.5),
            "cracks": match_context.get("cracks", False),
            "grass_cover": match_context.get("grass_cover", "medium"),
        }
        pitch["second_innings_spin_boost"] = 1.0
        if pitch["spin_friendly"] and pitch["wear_rate"] > 0.6:
            pitch["second_innings_spin_boost"] = 1.3
        pitch["chaos_score"] = self._calculate_pitch_chaos(pitch)
        return pitch

    def _calculate_pitch_chaos(self, pitch: Dict) -> float:
        chaos = 0.0
        if pitch["cracks"]:
            chaos += 0.25
        if pitch["wear_rate"] > 0.7:
            chaos += 0.2
        if pitch["pace_friendly"] and pitch["spin_friendly"]:
            chaos += 0.15
        return min(1.0, chaos)

    def _analyze_player_form(self, match_context: Dict) -> Dict:
        players = match_context.get("players", [])
        player_chaos = {}
        for player in players:
            chaos_factors = {
                "edge_rate": player.get("edge_rate", 0.10),
                "false_shot_percentage": player.get("false_shot_percentage", 0.15),
                "balls_per_wicket": player.get("balls_per_wicket", 30),
                "lbw_dismissal_rate": player.get("lbw_dismissal_rate", 0.20),
                "caught_behind_rate": player.get("caught_behind_rate", 0.25),
                "recent_form_variance": player.get("recent_form_variance", 0.3),
            }
            chaos_factors["fragility_score"] = self._calculate_player_fragility(
                chaos_factors, player["role"]
            )
            chaos_factors["luck_factor"] = self._calculate_luck_factor(chaos_factors)
            player_chaos[player["name"]] = chaos_factors
        return player_chaos

    def _calculate_player_fragility(self, factors: Dict, role: str) -> float:
        fragility = 0.0
        if role == "BAT":
            if factors["edge_rate"] > 0.15:
                fragility += 0.3
            if factors["caught_behind_rate"] > 0.30:
                fragility += 0.2
            if factors["lbw_dismissal_rate"] > 0.25:
                fragility += 0.2
        elif role == "BOWL":
            if factors["false_shot_percentage"] > 0.20 and factors["balls_per_wicket"] > 35:
                fragility = 0.1
        return min(1.0, fragility)

    def _calculate_luck_factor(self, factors: Dict) -> float:
        luck = 0.0
        if factors["recent_form_variance"] > 0.5:
            luck += 0.3
        if factors["edge_rate"] > 0.15:
            luck += 0.2
        return min(1.0, luck)

    def _analyze_historical_patterns(self, match_context: Dict) -> Dict:
        patterns = {
            "venue_upset_rate": match_context.get("venue_upset_rate", 0.3),
            "head_to_head_chaos": match_context.get("head_to_head_chaos", 0.4),
            "recent_upsets": match_context.get("recent_upsets", 0),
            "average_margin": match_context.get("average_margin", 20),
            "margin_variance": match_context.get("margin_variance", 15),
        }
        patterns["chaos_score"] = self._calculate_historical_chaos(patterns)
        return patterns

    def _calculate_historical_chaos(self, patterns: Dict) -> float:
        chaos = 0.0
        if patterns["venue_upset_rate"] > 0.4:
            chaos += 0.2
        if patterns["margin_variance"] > 20:
            chaos += 0.25
        if patterns["recent_upsets"] > 2:
            chaos += 0.15
        return min(1.0, chaos)

    def _analyze_venue_quirks(self, match_context: Dict) -> Dict:
        quirks = {
            "boundary_size": match_context.get("boundary_size", "medium"),
            "crowd_noise_level": match_context.get("crowd_noise", "medium"),
            "home_advantage": match_context.get("home_advantage", 0.5),
            "night_match_factor": match_context.get("is_night_match", False),
        }
        quirks["chaos_score"] = self._calculate_venue_chaos(quirks)
        return quirks

    def _calculate_venue_chaos(self, quirks: Dict) -> float:
        chaos = 0.0
        if quirks["boundary_size"] == "huge":
            chaos += 0.15
        if quirks["crowd_noise_level"] == "high":
            chaos += 0.1
        return min(1.0, chaos)

    def _analyze_toss_impact(self, match_context: Dict) -> Dict:
        dew_factor = match_context.get("dew_factor", "LOW")
        toss_impact = {
            "dew_advantage": dew_factor == "HIGH"
            and match_context.get("toss_decision", "") == "bowl",
            "pitch_deterioration": match_context.get("pitch_wear_rate", 0.5) > 0.6,
            "chasing_advantage": match_context.get("chasing_win_rate", 0.5),
        }
        toss_impact["chaos_score"] = 0.2 if toss_impact["dew_advantage"] else 0.0
        return toss_impact

    def _analyze_crowd_pressure(self, match_context: Dict) -> Dict:
        crowd = {
            "home_crowd_percentage": match_context.get("home_crowd_pct", 50),
            "match_importance": match_context.get("match_importance", "regular"),
            "rivalry_factor": match_context.get("rivalry_factor", 0.5),
        }
        crowd["chaos_score"] = self._calculate_crowd_chaos(crowd)
        return crowd

    def _calculate_crowd_chaos(self, crowd: Dict) -> float:
        chaos = 0.0
        if crowd["rivalry_factor"] > 0.7:
            chaos += 0.2
        if crowd["match_importance"] in ("playoff", "final"):
            chaos += 0.25
        if crowd["home_crowd_percentage"] > 80 or crowd["home_crowd_percentage"] < 20:
            chaos += 0.15
        return min(1.0, chaos)

    def _analyze_travel_fatigue(self, match_context: Dict) -> Dict:
        travel = {
            "distance_km": match_context.get("travel_distance_km", 0),
            "days_since_last_match": match_context.get("days_since_last_match", 3),
            "timezone_changes": match_context.get("timezone_changes", 0),
        }
        travel["chaos_score"] = self._calculate_travel_chaos(travel)
        return travel

    def _calculate_travel_chaos(self, travel: Dict) -> float:
        chaos = 0.0
        if travel["distance_km"] > 2000:
            chaos += 0.2
        if travel["days_since_last_match"] < 2:
            chaos += 0.25
        if travel["timezone_changes"] > 1:
            chaos += 0.15
        return min(1.0, chaos)

    def _analyze_match_importance(self, match_context: Dict) -> Dict:
        importance = {
            "is_knockout": match_context.get("is_knockout", False),
            "qualification_impact": match_context.get("qualification_impact", 0.0),
            "relegation_risk": match_context.get("relegation_risk", False),
        }
        importance["chaos_score"] = 0.3 if importance["is_knockout"] else 0.0
        return importance

    def apply_chaos_to_player(self, player: Dict, all_factors: Dict) -> Dict:
        """Apply ALL chaos factors to a single player. Master intelligence function."""
        player = player.copy()
        expected_points_multiplier = 1.0
        variance_boost = 0.0

        # 1. WEATHER IMPACT
        weather = all_factors["weather"]
        bowling_style = str(player.get("bowling_style", ""))
        if weather["spin_penalty"] and player["role"] == "BOWL" and "spin" in bowling_style:
            expected_points_multiplier *= 0.70
            variance_boost += 0.2
        if weather["dls_risk"]:
            if player["role"] == "BAT" and player.get("batting_order", 5) <= 3:
                expected_points_multiplier *= 1.3
            elif player["role"] == "BOWL" and player.get("bowling_phase", "middle") == "death":
                expected_points_multiplier *= 1.2

        # 2. UMPIRE IMPACT
        umpire = all_factors["umpire"]
        if umpire["strictness_index"] > 0.7:
            if player["role"] == "BOWL" and bowling_style == "pace":
                expected_points_multiplier *= 1.05
            elif player["role"] == "BAT" and player.get("lbw_dismissal_rate", 0.2) > 0.3:
                expected_points_multiplier *= 0.90

        # 3. PITCH IMPACT
        pitch = all_factors["pitch"]
        if pitch["second_innings_spin_boost"] > 1.0:
            if player["role"] == "BOWL" and "spin" in bowling_style:
                if player.get("bowling_innings", 1) == 2:
                    expected_points_multiplier *= pitch["second_innings_spin_boost"]

        # 4. PLAYER FRAGILITY
        player_chaos = all_factors["player_form"].get(player["name"], {})
        if player_chaos.get("fragility_score", 0) > 0.5:
            variance_boost += 0.3
        if player_chaos.get("luck_factor", 0) > 0.5:
            if player["role"] == "BAT":
                expected_points_multiplier *= 0.85
                variance_boost += 0.2
            elif player["role"] == "BOWL":
                expected_points_multiplier *= 1.15

        # 5. TRAVEL FATIGUE
        travel = all_factors["travel_fatigue"]
        if travel["chaos_score"] > 0.4:
            if player["role"] == "BOWL" and player.get("bowling_style", "pace") == "pace":
                expected_points_multiplier *= 0.85

        # 6. CROWD PRESSURE
        crowd = all_factors["crowd_pressure"]
        if crowd["chaos_score"] > 0.4:
            if player.get("experience_years", 5) < 3:
                expected_points_multiplier *= 0.90
                variance_boost += 0.15

        player["expected_points"] = player.get("expected_points", 50) * expected_points_multiplier
        player["variance_score"] = min(1.0, player.get("variance_score", 0.5) + variance_boost)
        player["chaos_adjusted"] = True
        return player

    def get_match_chaos_summary(self, all_factors: Dict) -> Dict:
        total_chaos = float(np.mean([
            all_factors["weather"]["chaos_score"],
            all_factors["umpire"]["chaos_score"],
            all_factors["pitch"]["chaos_score"],
            all_factors["historical_patterns"]["chaos_score"],
            all_factors["venue_quirks"]["chaos_score"],
            all_factors["toss_impact"]["chaos_score"],
            all_factors["crowd_pressure"]["chaos_score"],
            all_factors["travel_fatigue"]["chaos_score"],
            all_factors["match_importance"]["chaos_score"],
        ]))
        return {
            "total_chaos_score": round(total_chaos, 2),
            "chaos_level": (
                "LOW" if total_chaos < 0.3 else "MEDIUM" if total_chaos < 0.6 else "HIGH"
            ),
            "key_factors": self._identify_key_chaos_factors(all_factors),
            "recommended_strategy": self._recommend_strategy(total_chaos, all_factors),
        }

    def _identify_key_chaos_factors(self, all_factors: Dict) -> List[str]:
        factors = [
            ("Weather", all_factors["weather"]["chaos_score"]),
            ("Umpire", all_factors["umpire"]["chaos_score"]),
            ("Pitch", all_factors["pitch"]["chaos_score"]),
            ("Historical", all_factors["historical_patterns"]["chaos_score"]),
            ("Venue", all_factors["venue_quirks"]["chaos_score"]),
            ("Travel", all_factors["travel_fatigue"]["chaos_score"]),
        ]
        factors.sort(key=lambda x: x[1], reverse=True)
        return [f"{name} ({score:.2f})" for name, score in factors[:3]]

    def _recommend_strategy(self, total_chaos: float, all_factors: Dict) -> str:
        if total_chaos > 0.6:
            return (
                "HIGH CHAOS: Maximize variance picks. Target low-owned players with high upside. Expect upsets."
            )
        elif total_chaos > 0.3:
            return (
                "MEDIUM CHAOS: Balanced approach. Mix safe picks with 2-3 differentials. Monitor weather closely."
            )
        return (
            "LOW CHAOS: Predictable match. Stick to form players. Lower ownership differentials still valuable."
        )
