"""Capability 5: cricket-weather-analysis
Rain, dew-risk proxies, humidity and interruptions modeling.
"""
from typing import Dict, Any
from ..models import WeatherReport

class CricketWeatherAnalysis:
    def __init__(self, weather: WeatherReport):
        self.weather = weather

    def execute(self) -> Dict[str, Any]:
        dew_risk_level = "High" if self.weather.humidity_pct > 70.0 and self.weather.dew_expected else "Moderate"
        interruption = "Low / Full 20 overs expected" if self.weather.rain_probability_pct < 20.0 else "DLS Threat Present"
        
        return {
            "capability": "cricket-weather-analysis",
            "temperature_c": self.weather.temperature_c,
            "humidity_pct": self.weather.humidity_pct,
            "rain_probability_pct": self.weather.rain_probability_pct,
            "dew_risk_level": dew_risk_level,
            "interruption_status": interruption,
            "impact_on_fantasy": {
                "overs_expected": 20,
                "ball_grip_reduction_2nd_innings": "Significant in 2nd innings under high humidity / evening dew" if self.weather.dew_expected else "Negligible ball grip reduction expected",
                "bowler_risk": "Fingerspinners defending total will suffer higher economy rate; pacers relying on cross-seam grip slightly hindered" if self.weather.dew_expected else "Standard bowling grip conditions",
                "batter_boost": "2nd innings batters gain +12% boundary conversion due to wet outfield skid" if self.weather.dew_expected else "Normal surface pace and bounce for batters"
            }
        }
