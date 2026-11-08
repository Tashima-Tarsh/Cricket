"""Capability 12: cricket-points-forecast
Predict fantasy-point distributions (mean, std dev, 10th percentile floor, 90th percentile ceiling)
powered by the trained XGBoost machine learning model.
"""
from typing import List, Dict, Any, Optional
import numpy as np
from ..models import Player, VenueConditions, WeatherReport
from ..xgboost_model import XGBoostFantasyPredictor


class CricketPointsForecast:
    def __init__(
        self,
        players: List[Player],
        venue: Optional[VenueConditions] = None,
        weather: Optional[WeatherReport] = None,
        predictor: Optional[XGBoostFantasyPredictor] = None
    ):
        self.players = players
        self.venue = venue
        self.weather = weather
        self.predictor = predictor or XGBoostFantasyPredictor()

    def execute(self) -> Dict[str, Any]:
        forecasts = []
        for p in self.players:
            pred = self.predictor.predict_player(p, self.venue, self.weather)

            mean_pts = pred["mean_points"]
            ceiling = pred["ceiling_90th"]
            floor = pred["floor_10th"]
            std_dev = pred["std_dev"]

            p.projected_points = mean_pts
            p.ceiling_score = ceiling
            p.floor_score = floor

            forecasts.append({
                "id": p.id,
                "name": p.name,
                "team": p.team,
                "role": p.role,
                "credits": p.credits,
                "mean_points": mean_pts,
                "floor_10th": floor,
                "ceiling_90th": ceiling,
                "std_dev": std_dev,
                "upside_ratio": round(ceiling / max(1.0, mean_pts), 2),
                "model": "XGBoost Regressor"
            })

        forecasts.sort(key=lambda x: x["ceiling_90th"], reverse=True)

        return {
            "capability": "cricket-points-forecast",
            "model_engine": "XGBoost",
            "top_ceiling_players": forecasts[:8],
            "all_forecasts": forecasts
        }
