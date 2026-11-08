"""Capability 16: cricket-grand-league-simulator
Simulate match outcomes and fantasy-score distributions using Monte Carlo simulations.
Calculates Dream Team appearance frequency (% of sims in top 11) and covariance.
"""
from typing import List, Dict, Any
import numpy as np
from ..models import Player, VenueConditions, WeatherReport, TossScenario
from ..config import FantasyScoringConfig, DEFAULT_SCORING
from .c11_fantasy_scoring import CricketFantasyScoring

class CricketGrandLeagueSimulator:
    def __init__(
        self,
        players: List[Player],
        venue: VenueConditions,
        weather: WeatherReport,
        scoring_config: FantasyScoringConfig = DEFAULT_SCORING,
        n_simulations: int = 5000
    ):
        self.players = players
        self.venue = venue
        self.weather = weather
        self.scoring = CricketFantasyScoring(scoring_config)
        self.n_simulations = n_simulations

    def execute(self) -> Dict[str, Any]:
        np.random.seed(42)
        n = self.n_simulations
        player_points_sim = {p.id: np.zeros(n) for p in self.players}

        dew_boost = 1.12 if self.weather.dew_expected else 1.0
        pace_favor = self.venue.pace_wickets_pct / 50.0

        for i in range(n):
            # Team match script variability: high scoring (190+) vs low scoring (145-) vs average
            match_tempo = np.random.normal(1.0, 0.15)
            
            sim_scores_this_match = {}

            for p in self.players:
                # 1. Batting simulation
                # Probability of batting depends on batting order
                order = p.batting_order_projected
                prob_bat = max(0.05, 1.0 - (order - 1) * 0.12)
                did_bat = np.random.rand() < prob_bat
                
                runs = 0
                fours = 0
                sixes = 0
                balls = 0
                
                if did_bat:
                    # Exponential or Gamma distribution for T20 runs
                    expected_runs = p.stats.batting_avg * match_tempo * (0.9 if order > 5 else 1.1)
                    if p.team == "IND":
                        expected_runs *= 1.05  # Slight home edge
                    
                    runs = int(np.random.exponential(scale=expected_runs))
                    # Bound runs realistic for T20
                    runs = min(runs, 125)
                    
                    # Balls faced based on strike rate
                    sr = max(80.0, np.random.normal(p.stats.strike_rate, 25.0))
                    balls = max(1, int((runs / sr) * 100.0))
                    
                    # Boundaries
                    fours = int(runs * 0.12)
                    sixes = int(runs * 0.08)

                # 2. Bowling simulation
                wickets = 0
                overs = p.expected_overs
                runs_conceded = 0
                maidens = 0
                bowled_lbw = 0

                if overs > 0:
                    # Adjust overs bowled slightly by match situation
                    actual_overs = min(4.0, max(1.0, round(np.random.normal(overs, 0.4), 1)))
                    # Wicket probability: Poisson process
                    expected_wkts_per_over = 1.0 / (p.stats.bowling_strike_rate if p.stats.bowling_strike_rate > 0 else 20.0)
                    
                    # Pace vs Spin adjustment
                    if p.bowling_style and ("fast" in p.bowling_style.lower() or "medium" in p.bowling_style.lower()):
                        expected_wkts_per_over *= pace_favor
                    else:
                        expected_wkts_per_over *= (2.0 - pace_favor)
                    
                    # Death overs boost
                    if p.stats.death_overs_rate > 0.3:
                        expected_wkts_per_over *= 1.35

                    wickets = int(np.random.poisson(lam=expected_wkts_per_over * actual_overs * 6))
                    wickets = min(wickets, 5)
                    bowled_lbw = int(wickets * 0.4)
                    
                    # Economy and runs conceded
                    econ = max(4.5, np.random.normal(p.stats.economy, 1.8))
                    runs_conceded = int(econ * actual_overs)
                    if econ < 6.0 and actual_overs >= 3.0 and np.random.rand() < 0.2:
                        maidens = 1

                # 3. Fielding simulation
                catches = int(np.random.poisson(lam=0.45 if p.role == "WK" else 0.25))
                stumpings = 1 if p.role == "WK" and np.random.rand() < 0.18 else 0
                run_outs = 1 if np.random.rand() < 0.06 else 0

                # Compute fantasy points
                res = self.scoring.calculate_player_points(
                    runs=runs,
                    fours=fours,
                    sixes=sixes,
                    balls_faced=balls,
                    wickets=wickets,
                    bowled_lbw=bowled_lbw,
                    overs_bowled=overs,
                    runs_conceded=runs_conceded,
                    maidens=maidens,
                    catches=catches,
                    stumpings=stumpings,
                    run_outs=run_outs,
                    is_playing=True
                )
                pts = res["total_points"]
                player_points_sim[p.id][i] = pts
                sim_scores_this_match[p.id] = pts

        # Aggregate simulation statistics
        sim_summary = []
        dream_team_counts = {p.id: 0 for p in self.players}

        # Calculate Dream Team appearance rate (% of sims in top 11 scores)
        for i in range(n):
            match_scores = [(pid, player_points_sim[pid][i]) for pid in player_points_sim]
            match_scores.sort(key=lambda x: x[1], reverse=True)
            for pid, _ in match_scores[:11]:
                dream_team_counts[pid] += 1

        for p in self.players:
            scores = player_points_sim[p.id]
            mean_score = float(np.mean(scores))
            std_score = float(np.std(scores))
            p50 = float(np.percentile(scores, 50))
            p80 = float(np.percentile(scores, 80))
            p95 = float(np.percentile(scores, 95))  # High ceiling benchmark
            dt_rate = round((dream_team_counts[p.id] / n) * 100.0, 1)

            # Update player object
            p.ceiling_score = round(p95, 1)
            p.floor_score = round(float(np.percentile(scores, 15)), 1)
            p.projected_points = round(mean_score, 1)

            sim_summary.append({
                "id": p.id,
                "name": p.name,
                "team": p.team,
                "role": p.role,
                "credits": p.credits,
                "simulated_mean": round(mean_score, 1),
                "simulated_median": round(p50, 1),
                "p80_ceiling": round(p80, 1),
                "p95_elite_ceiling": round(p95, 1),
                "dream_team_appearance_pct": dt_rate,
                "volatility_score": round(std_score, 1)
            })

        sim_summary.sort(key=lambda x: x["dream_team_appearance_pct"], reverse=True)

        return {
            "capability": "cricket-grand-league-simulator",
            "iterations": n,
            "top_dream_team_probabilities": sim_summary[:11],
            "all_player_simulations": sim_summary
        }
