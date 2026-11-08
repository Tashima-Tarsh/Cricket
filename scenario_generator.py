"""
Scenario generator for BBL/WBBL Grand League diversification.
Produces 6 distinct match-script scenarios that drive diverse portfolio
construction via the OR-Tools optimizer.
"""
from typing import Dict, List

SCENARIOS: List[str] = [
    "balanced",
    "death_bowler_special",
    "top_collapse",
    "high_scoring_chase",
    "spin_dominance",
    "pace_dominance",
]

SCENARIO_DESCRIPTIONS: Dict[str, str] = {
    "balanced": "Mix of safe picks + differentials; no scenario forcing.",
    "death_bowler_special": "Force 2+ death-overs specialists; targets high-impact final overs.",
    "top_collapse": "Force 2+ opening bowlers + 1 opposing batter; targets early-wicket scripts.",
    "high_scoring_chase": "Force 4+ batters; targets run-chase batting dominance.",
    "spin_dominance": "Force 2+ spinners; targets spin-friendly venues (MCG, SCG, Adelaide).",
    "pace_dominance": "Force 2+ pacers; targets bounce-friendly venues (Perth, Gabba).",
}

DEFAULT_TEAMS_PER_SCENARIO = {
    "balanced": 7,
    "death_bowler_special": 4,
    "top_collapse": 4,
    "high_scoring_chase": 2,
    "spin_dominance": 2,
    "pace_dominance": 1,
}


def get_scenarios() -> List[str]:
    return list(SCENARIOS)


def describe(scenario: str) -> str:
    return SCENARIO_DESCRIPTIONS.get(scenario, "Unknown scenario")


def teams_for_scenario(scenario: str) -> int:
    return DEFAULT_TEAMS_PER_SCENARIO.get(scenario, 3)
