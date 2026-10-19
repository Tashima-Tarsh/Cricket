"""Capability 11: cricket-fantasy-scoring
Apply configurable scoring rules accurately for Dream11 & T20 fantasy formats.
"""
from typing import Dict, Any
from ..config import FantasyScoringConfig, DEFAULT_SCORING

class CricketFantasyScoring:
    def __init__(self, config: FantasyScoringConfig = DEFAULT_SCORING):
        self.config = config

    def calculate_player_points(
        self,
        runs: int = 0,
        fours: int = 0,
        sixes: int = 0,
        balls_faced: int = 0,
        wickets: int = 0,
        bowled_lbw: int = 0,
        overs_bowled: float = 0.0,
        runs_conceded: int = 0,
        maidens: int = 0,
        catches: int = 0,
        stumpings: int = 0,
        run_outs: int = 0,
        is_playing: bool = True
    ) -> Dict[str, Any]:
        points = 0.0
        breakdown = {}

        if is_playing:
            points += self.config.in_starting_11
            breakdown["starting_11"] = self.config.in_starting_11

        # Batting Points
        bat_pts = runs * self.config.run + fours * self.config.boundary_four + sixes * self.config.boundary_six
        if runs >= 100:
            bat_pts += self.config.runs_100_bonus
        elif runs >= 50:
            bat_pts += self.config.runs_50_bonus
        elif runs >= 30:
            bat_pts += self.config.runs_30_bonus
        
        if runs == 0 and balls_faced > 0:
            bat_pts += self.config.duck

        # Strike rate bonus (min 10 balls)
        if balls_faced >= 10:
            sr = (runs / balls_faced) * 100.0
            if sr > 170.0:
                bat_pts += self.config.strike_rate_bonuses.get("over_170", 6.0)
            elif sr >= 150.0:
                bat_pts += self.config.strike_rate_bonuses.get("150_to_170", 4.0)
            elif sr >= 130.0:
                bat_pts += self.config.strike_rate_bonuses.get("130_to_150", 2.0)
            elif sr < 50.0:
                bat_pts += self.config.strike_rate_bonuses.get("under_50", -6.0)

        points += bat_pts
        breakdown["batting"] = round(bat_pts, 1)

        # Bowling Points
        bowl_pts = wickets * self.config.wicket + bowled_lbw * self.config.bowled_lbw_bonus + maidens * self.config.maiden_over
        if wickets >= 5:
            bowl_pts += self.config.five_wickets_bonus
        elif wickets >= 4:
            bowl_pts += self.config.four_wickets_bonus
        elif wickets >= 3:
            bowl_pts += self.config.three_wickets_bonus

        # Economy rate (min 2 overs)
        if overs_bowled >= 2.0:
            econ = runs_conceded / overs_bowled
            if econ < 5.0:
                bowl_pts += self.config.economy_bonuses.get("under_5", 6.0)
            elif econ <= 6.0:
                bowl_pts += self.config.economy_bonuses.get("5_to_6", 4.0)
            elif econ <= 7.0:
                bowl_pts += self.config.economy_bonuses.get("6_to_7", 2.0)
            elif econ > 12.0:
                bowl_pts += self.config.economy_bonuses.get("over_12", -6.0)

        points += bowl_pts
        breakdown["bowling"] = round(bowl_pts, 1)

        # Fielding Points
        field_pts = catches * self.config.catch + stumpings * self.config.stumping + run_outs * self.config.run_out_direct
        if catches >= 3:
            field_pts += self.config.three_catch_bonus
        
        points += field_pts
        breakdown["fielding"] = round(field_pts, 1)

        return {
            "capability": "cricket-fantasy-scoring",
            "total_points": round(points, 1),
            "breakdown": breakdown
        }
