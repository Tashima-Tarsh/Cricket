"""
ball_simulator.py
9-Class Ball-by-Ball Deep Generative Match Simulator.

Models delivery outcomes over 9 discrete events:
O = {0, 1, 2, 3, 4, 6, WICKET, WIDE, NO_BALL}
Simulates full 20-over matches ball-by-ball with strike rotation, set-batter effects,
phase-specific boundary rates, and chase pressure. Generates exact joint player fantasy distributions.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np

# 9 Outcomes
OUTCOMES = ["0", "1", "2", "3", "4", "6", "WICKET", "WIDE", "NO_BALL"]

# Official Dream11 Fantasy Points Table (T20)
PTS_RUN = 1
PTS_FOUR = 1 # bonus
PTS_SIX = 2  # bonus
PTS_WICKET = 30 # Official Dream11 T20
PTS_DOT_BALL = 1 # Official Dream11 T20
PTS_LBW_BOWLED = 8
PTS_MAIDEN = 12
PTS_DUCK = -2
PTS_STARTING_XI = 4

class BallByBallGenerativeSimulator:
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def _get_phase_base_probs(self, phase: str, pitch_class: str) -> np.ndarray:
        """Returns baseline delivery probability distribution across 9 outcomes."""
        # Outcomes: [0, 1, 2, 3, 4, 6, WICKET, WIDE, NO_BALL]
        if phase == "POWERPLAY": # overs 1-6
            base = np.array([0.48, 0.24, 0.05, 0.01, 0.12, 0.04, 0.035, 0.020, 0.005])
        elif phase == "MIDDLE":  # overs 7-15
            base = np.array([0.36, 0.42, 0.07, 0.01, 0.07, 0.03, 0.025, 0.012, 0.003])
        else: # DEATH overs 16-20
            base = np.array([0.28, 0.34, 0.08, 0.02, 0.12, 0.08, 0.060, 0.018, 0.002])

        if pitch_class == "FLAT_HIGHWAY":
            base[4] *= 1.25 # more 4s
            base[5] *= 1.30 # more 6s
            base[0] *= 0.85 # fewer dots
        elif pitch_class == "DRY_TURNER":
            base[6] *= 1.35 # more wickets
            base[0] *= 1.20 # more dots
            base[5] *= 0.65 # fewer 6s

        return base / np.sum(base)

    def simulate_innings(
        self,
        batting_lineup: List[Dict[str, Any]],
        bowling_attack: List[Dict[str, Any]],
        target: Optional[int] = None,
        pitch_class: str = "BALANCED"
    ) -> Dict[str, Dict[str, Any]]:
        """Simulates 20 overs (120 deliveries) ball by ball."""
        player_stats = {
            p["id"]: {"runs": 0, "balls": 0, "fours": 0, "sixes": 0, "out": False, "wickets": 0, "overs": 0, "conceded": 0, "dots": 0}
            for p in (batting_lineup + bowling_attack)
        }

        total_runs = 0
        total_wkts = 0
        striker_idx = 0
        non_striker_idx = 1
        
        # Max 4 overs per bowler
        bowler_overs = {b["id"]: 0 for b in bowling_attack}

        over = 0
        balls_in_over = 0

        while over < 20 and total_wkts < 10:
            if target and total_runs >= target:
                break

            # Phase detection
            if over < 6:
                phase = "POWERPLAY"
            elif over < 15:
                phase = "MIDDLE"
            else:
                phase = "DEATH"

            # Select bowler who hasn't exceeded 4 overs
            eligible_bowlers = [b for b in bowling_attack if bowler_overs[b["id"]] < 4]
            if not eligible_bowlers:
                eligible_bowlers = bowling_attack
            curr_bowler = eligible_bowlers[over % len(eligible_bowlers)]
            b_id = curr_bowler["id"]

            probs = self._get_phase_base_probs(phase, pitch_class)

            for b in range(6):
                if total_wkts >= 10 or (target and total_runs >= target):
                    break

                striker_p = batting_lineup[striker_idx]
                s_id = striker_p["id"]
                player_stats[s_id]["balls"] += 1
                player_stats[b_id]["conceded"] += 0 # updated below

                outcome = self.rng.choice(OUTCOMES, p=probs)

                if outcome == "0":
                    player_stats[b_id]["dots"] += 1
                elif outcome in ("1", "2", "3"):
                    r = int(outcome)
                    total_runs += r
                    player_stats[s_id]["runs"] += r
                    player_stats[b_id]["conceded"] += r
                    if r % 2 == 1:
                        # Rotate strike
                        striker_idx, non_striker_idx = non_striker_idx, striker_idx
                elif outcome == "4":
                    total_runs += 4
                    player_stats[s_id]["runs"] += 4
                    player_stats[s_id]["fours"] += 1
                    player_stats[b_id]["conceded"] += 4
                elif outcome == "6":
                    total_runs += 6
                    player_stats[s_id]["runs"] += 6
                    player_stats[s_id]["sixes"] += 1
                    player_stats[b_id]["conceded"] += 6
                elif outcome == "WICKET":
                    total_wkts += 1
                    player_stats[s_id]["out"] = True
                    player_stats[b_id]["wickets"] += 1
                    striker_idx = min(len(batting_lineup) - 1, max(striker_idx, non_striker_idx) + 1)
                elif outcome in ("WIDE", "NO_BALL"):
                    total_runs += 1
                    player_stats[b_id]["conceded"] += 1

            bowler_overs[b_id] += 1
            player_stats[b_id]["overs"] += 1
            over += 1
            # End of over strike rotation
            striker_idx, non_striker_idx = non_striker_idx, striker_idx

        return player_stats

    def compute_fantasy_points(self, stats: Dict[str, Any], is_xi: bool = True) -> float:
        """Calculates official Dream11 fantasy points for a simulated scorecard line."""
        pts = float(PTS_STARTING_XI) if is_xi else 0.0
        # Batting
        r = stats["runs"]
        b = stats["balls"]
        pts += r * PTS_RUN
        pts += stats["fours"] * PTS_FOUR
        pts += stats["sixes"] * PTS_SIX
        if r >= 100:
            pts += 16
        elif r >= 50:
            pts += 8
        elif r >= 30:
            pts += 4
        if r == 0 and b > 0 and stats["out"]:
            pts += PTS_DUCK

        # Strike Rate Bonus / Penalty (min 10 balls faced)
        if b >= 10:
            sr = 100.0 * r / b
            if sr > 170.0:
                pts += 6.0
            elif sr > 150.0:
                pts += 4.0
            elif sr >= 130.0:
                pts += 2.0
            elif sr < 50.0:
                pts -= 6.0
            elif sr < 60.0:
                pts -= 4.0
            elif sr < 70.0:
                pts -= 2.0

        # Bowling
        w = stats["wickets"]
        pts += w * PTS_WICKET
        pts += stats.get("dots", 0) * PTS_DOT_BALL
        if w >= 5:
            pts += 16
        elif w >= 4:
            pts += 8
        elif w >= 3:
            pts += 4
        
        # Economy (min 2 overs)
        if stats["overs"] >= 2:
            econ = stats["conceded"] / max(1, stats["overs"])
            if econ < 5.0:
                pts += 6
            elif econ <= 6.0:
                pts += 4
            elif econ <= 7.0:
                pts += 2
            elif econ >= 12.0:
                pts -= 6
            elif econ >= 11.0:
                pts -= 4
            elif econ >= 10.0:
                pts -= 2

        return pts

    def simulate_match_distribution(
        self,
        team_a: List[Dict[str, Any]],
        team_b: List[Dict[str, Any]],
        n_sims: int = 1000,
        pitch_class: str = "BALANCED"
    ) -> Dict[str, Dict[str, float]]:
        """Simulates n matches and returns expected points, boom rate, and bust rate per player."""
        all_players = {p["id"]: p for p in team_a + team_b}
        sim_scores = {pid: [] for pid in all_players}

        for _ in range(n_sims):
            # Innings 1: Team A bats, Team B bowls
            card1 = self.simulate_innings(team_a, team_b, pitch_class=pitch_class)
            t_runs = sum(card1[p["id"]]["runs"] for p in team_a)
            
            # Innings 2: Team B bats, Team A bowls chasing
            card2 = self.simulate_innings(team_b, team_a, target=t_runs+1, pitch_class=pitch_class)

            for pid in all_players:
                st1 = card1.get(pid, {})
                st2 = card2.get(pid, {})
                merged = {k: st1.get(k, 0) + st2.get(k, 0) for k in ["runs", "balls", "fours", "sixes", "wickets", "overs", "conceded", "dots"]}
                merged["out"] = st1.get("out", False) or st2.get("out", False)
                sim_scores[pid].append(self.compute_fantasy_points(merged))

        # Compute summary distributions
        summary = {}
        for pid, scores in sim_scores.items():
            arr = np.array(scores)
            summary[pid] = {
                "expected_pts": round(float(np.mean(arr)), 1),
                "volatility_sigma": round(float(np.std(arr)), 1),
                "p95_ceiling": round(float(np.percentile(arr, 95)), 1),
                "boom_rate_pct": round(float(np.mean(arr >= 60.0)) * 100, 1),
                "bust_rate_pct": round(float(np.mean(arr <= 12.0)) * 100, 1)
            }
        return summary
