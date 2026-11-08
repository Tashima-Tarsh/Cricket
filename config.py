"""
Configuration for BBL vs WBBL fantasy cricket engine.
Adjusts scoring, boundary weights, venue metadata, and meta based on league type.
"""

LEAGUE = "BBL"  # Change to "WBBL" for Women's Big Bash League

# Scoring rules (Dream11 standard)
SCORING = {
    "run": 1,
    "wicket": 25,
    "catch": 8,
    "stumping": 12,
    "run_out": 12,
    "century_bonus": 20,
    "half_century_bonus": 8,
    "five_wicket_bonus": 12,
    "four_wicket_bonus": 8,
    "three_wicket_bonus": 4,
    "strike_rate_170_plus": 6,
    "strike_rate_150_to_169": 4,
    "economy_under_5_bonus": 6,
    "economy_5_to_6_bonus": 4,
    "duck_penalty": -2,
}

# League-specific adjustments
if LEAGUE == "BBL":
    VENUE_ADJUSTMENTS = {
        "MCG": {"boundary_size": "huge", "pace_boost": 1.0, "spin_boost": 0.85, "avg_first_innings": 165},
        "Perth_Stadium": {"boundary_size": "large", "pace_boost": 1.2, "spin_boost": 0.9, "avg_first_innings": 170},
        "Adelaide_Oval": {"boundary_size": "medium", "pace_boost": 0.95, "spin_boost": 1.15, "avg_first_innings": 160},
        "SCG": {"boundary_size": "medium", "pace_boost": 1.0, "spin_boost": 1.1, "avg_first_innings": 175},
        "Gabba": {"boundary_size": "large", "pace_boost": 1.15, "spin_boost": 0.95, "avg_first_innings": 168},
        "Marvel_Stadium": {"boundary_size": "small", "pace_boost": 0.9, "spin_boost": 1.0, "avg_first_innings": 180},
    }
    TRAVEL_FATIGUE_PENALTY = 0.15
    
elif LEAGUE == "WBBL":
    VENUE_ADJUSTMENTS = {
        "MCG": {"boundary_size": "large", "pace_boost": 0.95, "spin_boost": 1.2, "avg_first_innings": 145},
        "Perth_Stadium": {"boundary_size": "medium", "pace_boost": 1.1, "spin_boost": 1.15, "avg_first_innings": 150},
        "Adelaide_Oval": {"boundary_size": "medium", "pace_boost": 0.9, "spin_boost": 1.25, "avg_first_innings": 140},
        "SCG": {"boundary_size": "small", "pace_boost": 0.95, "spin_boost": 1.2, "avg_first_innings": 155},
        "Gabba": {"boundary_size": "medium", "pace_boost": 1.05, "spin_boost": 1.1, "avg_first_innings": 148},
        "North_Sydney_Oval": {"boundary_size": "small", "pace_boost": 0.85, "spin_boost": 1.3, "avg_first_innings": 152},
    }
    TRAVEL_FATIGUE_PENALTY = 0.10

# Role bounds (Dream11 standard)
ROLE_BOUNDS = {
    "WK": (1, 4),
    "BAT": (1, 6),
    "AR": (1, 4),
    "BOWL": (3, 6)
}

# Grand League constraints
MIN_DIFFERENTIALS = 2
MAX_TEAM_PLAYERS = 7
TOTAL_CREDITS = 100.0

# Fantasy points feature columns used by the predictor
FEATURE_COLS = [
    "skill_rating", "recent_form_last_5", "opposition_strength",
    "phase_strike_rate", "economy_rate", "venue_factor", "travel_fatigue"
]

# BBL/WBBL teams
BBL_TEAMS = [
    "Sydney Sixers", "Sydney Thunder", "Melbourne Stars", "Melbourne Renegades",
    "Brisbane Heat", "Perth Scorchers", "Adelaide Strikers", "Hobart Hurricanes"
]

WBBL_TEAMS = [
    "Sydney Sixers", "Sydney Thunder", "Melbourne Stars", "Melbourne Renegades",
    "Brisbane Heat", "Perth Scorchers", "Adelaide Strikers", "Hobart Hurricanes"
]

# Scenarios for Grand League diversification
SCENARIOS = [
    "balanced", "death_bowler_special", "top_collapse",
    "high_scoring_chase", "spin_dominance", "pace_dominance"
]
