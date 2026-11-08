"""Master Pipeline orchestrating all 20 Grand League Capabilities for India vs West Indies."""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from .models import Player, VenueConditions, WeatherReport, TossScenario, MatchupDetail, Lineup
from .config import DEFAULT_SCORING, DEFAULT_CONSTRAINTS

from .capabilities.c01_fixture_research import CricketFixtureResearch
from .capabilities.c02_squad_verification import CricketSquadVerification
from .capabilities.c03_toss_analysis import CricketTossAnalysis
from .capabilities.c04_pitch_intelligence import CricketPitchIntelligence
from .capabilities.c05_weather_analysis import CricketWeatherAnalysis
from .capabilities.c06_player_form import CricketPlayerForm
from .capabilities.c07_batter_matchups import CricketBatterMatchups
from .capabilities.c08_bowler_matchups import CricketBowlerMatchups
from .capabilities.c09_phase_analysis import CricketPhaseAnalysis
from .capabilities.c10_role_analysis import CricketRoleAnalysis
from .capabilities.c11_fantasy_scoring import CricketFantasyScoring
from .capabilities.c12_points_forecast import CricketPointsForecast
from .capabilities.c13_ownership_estimator import CricketOwnershipEstimator
from .capabilities.c14_differential_finder import CricketDifferentialFinder
from .capabilities.c15_captain_engine import CricketCaptainEngine
from .capabilities.c16_grand_league_simulator import CricketGrandLeagueSimulator
from .capabilities.c17_multi_team_optimizer import CricketMultiTeamOptimizer
from .capabilities.c18_opponent_simulator import CricketOpponentSimulator
from .capabilities.c19_backtesting import CricketBacktesting
from .capabilities.c20_ai_analyst import CricketAIAnalyst

class GrandLeaguePipeline:
    def __init__(self, data_path: Optional[str] = None):
        if not data_path:
            data_path = str(Path(__file__).parent / "data" / "ind_wi_match.json")
        
        with open(data_path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)
            
        self.venue = VenueConditions(**self.raw_data["match_info"]["venue"])
        self.weather = WeatherReport(**self.raw_data["match_info"]["weather"])
        self.toss_scenarios = [TossScenario(**ts) for ts in self.raw_data["match_info"]["toss_scenarios"]]
        self.players = [Player(**p) for p in self.raw_data["players"]]
        self.matchups = [MatchupDetail(**m) for m in self.raw_data["matchups"]]

    def run_all_capabilities(self, num_teams: int = 10, sim_iterations: int = 3000) -> Dict[str, Any]:
        """Executes all 20 capabilities sequentially and produces the complete Grand League strategy package."""
        
        # Capability 1: Fixture Research
        c01 = CricketFixtureResearch(self.raw_data).execute()
        
        # Capability 2: Squad Verification
        c02 = CricketSquadVerification(self.players).execute()
        
        # Capability 3: Toss Analysis
        c03 = CricketTossAnalysis(self.venue, self.toss_scenarios).execute(0)
        
        # Capability 4: Pitch Intelligence
        c04 = CricketPitchIntelligence(self.venue).execute()
        
        # Capability 5: Weather Analysis
        c05 = CricketWeatherAnalysis(self.weather).execute()
        
        # Capability 6: Player Form
        c06 = CricketPlayerForm(self.players).execute()
        
        # Capability 7: Batter Matchups
        c07 = CricketBatterMatchups(self.matchups, self.players).execute()
        
        # Capability 8: Bowler Matchups
        c08 = CricketBowlerMatchups(self.players).execute()
        
        # Capability 9: Phase Analysis
        c09 = CricketPhaseAnalysis(self.players).execute()
        
        # Capability 10: Role Analysis
        c10 = CricketRoleAnalysis(self.players).execute()
        
        # Capability 11: Fantasy Scoring Engine
        scoring_engine = CricketFantasyScoring(DEFAULT_SCORING)
        c11 = {"capability": "cricket-fantasy-scoring", "status": "ACTIVE_STANDARD_T20_RULES"}
        
        # Capability 12: Points Forecast (XGBoost ML model projection)
        c12 = CricketPointsForecast(self.players, self.venue, self.weather).execute()
        
        # Capability 13: Ownership Estimator
        c13 = CricketOwnershipEstimator(self.players).execute()
        
        # Capability 14: Differential Finder
        c14 = CricketDifferentialFinder(self.players).execute()
        
        # Capability 15: Captain Engine
        c15 = CricketCaptainEngine(self.players).execute()
        
        # Capability 16: Grand League Simulator (Monte Carlo)
        simulator = CricketGrandLeagueSimulator(
            self.players, self.venue, self.weather, DEFAULT_SCORING, n_simulations=sim_iterations
        )
        c16 = simulator.execute()
        
        # Capability 17: Multi-Team Optimizer (PuLP Integer Programming)
        optimizer = CricketMultiTeamOptimizer(self.players, DEFAULT_CONSTRAINTS)
        lineups = optimizer.generate_grand_league_portfolio(
            num_teams=num_teams,
            min_differentials_per_team=2,
            max_overlap_between_teams=8
        )
        c17 = {
            "capability": "cricket-multi-team-optimizer",
            "teams_generated": len(lineups),
            "lineups": [l.model_dump() for l in lineups]
        }
        
        # Capability 18: Opponent Simulator
        c18 = CricketOpponentSimulator(lineups, pool_size=1000000).execute()
        
        # Capability 19: Backtesting
        c19 = CricketBacktesting().execute()
        
        # Capability 20: AI Analyst
        analyst = CricketAIAnalyst()
        c20 = analyst.explain_portfolio(
            lineups=lineups,
            differentials=c14["top_differential_picks"],
            pitch_info=c04,
            weather_info=c05
        )

        return {
            "match": "India vs West Indies Today Match",
            "capabilities": {
                "c01_fixture_research": c01,
                "c02_squad_verification": c02,
                "c03_toss_analysis": c03,
                "c04_pitch_intelligence": c04,
                "c05_weather_analysis": c05,
                "c06_player_form": c06,
                "c07_batter_matchups": c07,
                "c08_bowler_matchups": c08,
                "c09_phase_analysis": c09,
                "c10_role_analysis": c10,
                "c11_fantasy_scoring": c11,
                "c12_points_forecast": c12,
                "c13_ownership_estimator": c13,
                "c14_differential_finder": c14,
                "c15_captain_engine": c15,
                "c16_grand_league_simulator": c16,
                "c17_multi_team_optimizer": c17,
                "c18_opponent_simulator": c18,
                "c19_backtesting": c19,
                "c20_ai_analyst": c20
            },
            "lineups": lineups
        }
