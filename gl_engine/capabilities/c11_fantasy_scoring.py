"""Capability 11: cricket-fantasy-scoring
Apply configurable scoring rules accurately for Dream11 & T20/ODI fantasy formats.
"""
from typing import Dict, Any, Optional
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
        dots: int = 0,
        catches: int = 0,
        stumpings: int = 0,
        run_outs: int = 0,
        is_playing: bool = True,
        match_format: str = "T20"
    ) -> Dict[str, Any]:
        points = 0.0
        breakdown = {}
        fmt = (match_format or "T20").upper()

        if is_playing:
            points += self.config.in_starting_11
            breakdown["starting_11"] = self.config.in_starting_11

        # Batting Points
        bat_pts = runs * self.config.run + fours * self.config.boundary_four + sixes * self.config.boundary_six
        
        if fmt == "ODI":
            if runs >= 150:
                bat_pts += 16.0
            elif runs >= 100:
                bat_pts += 8.0
            elif runs >= 50:
                bat_pts += 4.0
        else: # T20 default
            if runs >= 100:
                bat_pts += self.config.runs_100_bonus
            elif runs >= 50:
                bat_pts += self.config.runs_50_bonus
            elif runs >= 30:
                bat_pts += self.config.runs_30_bonus
        
        if runs == 0 and balls_faced > 0:
            bat_pts += self.config.duck

        # Strike rate bonus
        min_balls = 20 if fmt == "ODI" else 10
        if balls_faced >= min_balls:
            sr = (runs / balls_faced) * 100.0
            if fmt == "ODI":
                if sr > 140.0:
                    bat_pts += 6.0
                elif sr >= 120.0:
                    bat_pts += 4.0
                elif sr >= 100.0:
                    bat_pts += 2.0
                elif sr < 30.0:
                    bat_pts -= 6.0
                elif sr <= 39.99:
                    bat_pts -= 4.0
                elif sr <= 49.99:
                    bat_pts -= 2.0
            else:
                if sr > 170.0:
                    bat_pts += self.config.strike_rate_bonuses.get("over_170", 6.0)
                elif sr >= 150.0:
                    bat_pts += self.config.strike_rate_bonuses.get("150_to_170", 4.0)
                elif sr >= 130.0:
                    bat_pts += self.config.strike_rate_bonuses.get("130_to_150", 2.0)
                elif sr < 50.0:
                    bat_pts += self.config.strike_rate_bonuses.get("under_50", -6.0)
                elif sr < 60.0:
                    bat_pts += self.config.strike_rate_bonuses.get("50_to_59", -4.0)
                elif sr < 70.0:
                    bat_pts += self.config.strike_rate_bonuses.get("60_to_70", -2.0)

        points += bat_pts
        breakdown["batting"] = round(bat_pts, 1)

        # Bowling Points
        w_val = 25.0 if fmt == "ODI" else self.config.wicket
        m_val = 4.0 if fmt == "ODI" else self.config.maiden_over
        bowl_pts = (
            wickets * w_val
            + bowled_lbw * self.config.bowled_lbw_bonus
            + maidens * m_val
            + dots * self.config.dot_ball
        )
        if wickets >= 5:
            bowl_pts += self.config.five_wickets_bonus
        elif wickets >= 4:
            bowl_pts += self.config.four_wickets_bonus
        elif wickets >= 3:
            bowl_pts += self.config.three_wickets_bonus

        # Economy rate
        min_overs = 5.0 if fmt == "ODI" else 2.0
        if overs_bowled >= min_overs:
            econ = runs_conceded / overs_bowled
            if fmt == "ODI":
                if econ < 3.5:
                    bowl_pts += 6.0
                elif econ <= 4.5:
                    bowl_pts += 4.0
                elif econ <= 5.5:
                    bowl_pts += 2.0
                elif econ > 9.0:
                    bowl_pts -= 6.0
                elif econ >= 8.01:
                    bowl_pts -= 4.0
                elif econ >= 7.0:
                    bowl_pts -= 2.0
            else:
                if econ < 5.0:
                    bowl_pts += self.config.economy_bonuses.get("under_5", 6.0)
                elif econ <= 6.0:
                    bowl_pts += self.config.economy_bonuses.get("5_to_6", 4.0)
                elif econ <= 7.0:
                    bowl_pts += self.config.economy_bonuses.get("6_to_7", 2.0)
                elif econ > 12.0:
                    bowl_pts += self.config.economy_bonuses.get("over_12", -6.0)
                elif econ >= 11.0:
                    bowl_pts += self.config.economy_bonuses.get("11_to_12", -4.0)
                elif econ >= 10.0:
                    bowl_pts += self.config.economy_bonuses.get("10_to_11", -2.0)

        points += bowl_pts
        breakdown["bowling"] = round(bowl_pts, 1)
        breakdown["dot_balls"] = round(dots * self.config.dot_ball, 1)

        # Fielding Points
        field_pts = catches * self.config.catch + stumpings * self.config.stumping + run_outs * self.config.run_out_direct
        if catches >= 3:
            field_pts += self.config.three_catch_bonus
        
        points += field_pts
        breakdown["fielding"] = round(field_pts, 1)

        return {
            "capability": "cricket-fantasy-scoring",
            "format": fmt,
            "total_points": round(points, 1),
            "breakdown": breakdown
        }
