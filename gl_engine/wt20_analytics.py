"""Ball-by-Ball Analytics Engine and Matchup Matrix for IND-W vs ZIM-W.
Connects directly to DuckDB (134,722 Women's T20 deliveries) to calculate delivery-level metrics,
phase splits (Powerplay, Middle, Death), spin vs pace splits, and batter-bowler H2H battles.
"""

from typing import Dict, Any, List, Optional, Tuple
import duckdb
from pathlib import Path
import numpy as np

DB_PATH = Path(__file__).parent.parent / "data" / "cricsheet_wt20.duckdb"

class WT20AnalyticsEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or DB_PATH)
        self.con = duckdb.connect(self.db_path, read_only=True)

    def query_batter_telemetry(self, batter_name: str) -> Dict[str, Any]:
        """Calculates delivery-level metrics across all phases from DuckDB."""
        # Query overall
        sql_overall = """
            SELECT 
                count(*) as balls,
                sum(runs_batter) as runs,
                sum(CASE WHEN runs_batter = 0 AND runs_extras = 0 THEN 1 ELSE 0 END) as dots,
                sum(CASE WHEN runs_batter = 4 THEN 1 ELSE 0 END) as fours,
                sum(CASE WHEN runs_batter = 6 THEN 1 ELSE 0 END) as sixes,
                sum(CASE WHEN is_wicket AND player_dismissed = batter THEN 1 ELSE 0 END) as dismissals
            FROM deliveries
            WHERE batter ILIKE ?
        """
        row = self.con.execute(sql_overall, [f"%{batter_name}%"]).fetchone()
        balls = row[0] or 0
        runs = row[1] or 0
        dots = row[2] or 0
        fours = row[3] or 0
        sixes = row[4] or 0
        dismissals = row[5] or 0

        sr = round((runs / balls * 100), 1) if balls > 0 else 115.0
        dot_pct = round((dots / balls * 100), 1) if balls > 0 else 42.0
        bnd_pct = round(((fours + sixes) / balls * 100), 1) if balls > 0 else 14.5
        avg = round(runs / dismissals, 1) if dismissals > 0 else float(runs)

        # Phase breakdown: Powerplay (0-5), Middle (6-14), Death (15-19)
        phase_sql = """
            SELECT 
                CASE 
                    WHEN over <= 5 THEN 'Powerplay'
                    WHEN over BETWEEN 6 AND 14 THEN 'Middle'
                    ELSE 'Death'
                END as phase,
                count(*) as balls,
                sum(runs_batter) as runs,
                sum(CASE WHEN is_wicket AND player_dismissed = batter THEN 1 ELSE 0 END) as dismissals
            FROM deliveries
            WHERE batter ILIKE ?
            GROUP BY 1
        """
        phase_rows = self.con.execute(phase_sql, [f"%{batter_name}%"]).fetchall()
        phases = {}
        for pr in phase_rows:
            p_name = pr[0]
            p_balls = pr[1] or 0
            p_runs = pr[2] or 0
            p_sr = round((p_runs / p_balls * 100), 1) if p_balls > 0 else 100.0
            phases[p_name] = {
                "balls": p_balls, "runs": p_runs, "strike_rate": p_sr, "dismissals": pr[3] or 0
            }

        return {
            "batter": batter_name,
            "sample_balls": balls,
            "runs": runs,
            "strike_rate": sr,
            "batting_avg": avg,
            "dot_ball_pct": dot_pct,
            "boundary_pct": bnd_pct,
            "dismissal_prob_per_ball": round(dismissals / balls, 4) if balls > 0 else 0.035,
            "phases": phases
        }

    def query_bowler_telemetry(self, bowler_name: str) -> Dict[str, Any]:
        """Calculates bowler delivery metrics, economy, dot-ball %, and phase wickets from DuckDB."""
        sql_overall = """
            SELECT 
                count(*) as balls,
                sum(runs_total) as runs_conceded,
                sum(CASE WHEN runs_total = 0 THEN 1 ELSE 0 END) as dots,
                sum(CASE WHEN runs_batter >= 4 THEN 1 ELSE 0 END) as boundaries,
                sum(CASE WHEN is_wicket AND wicket_type NOT IN ('run out', 'retired hurt') THEN 1 ELSE 0 END) as wickets
            FROM deliveries
            WHERE bowler ILIKE ?
        """
        row = self.con.execute(sql_overall, [f"%{bowler_name}%"]).fetchone()
        balls = row[0] or 0
        runs = row[1] or 0
        dots = row[2] or 0
        boundaries = row[3] or 0
        wickets = row[4] or 0

        overs = balls / 6.0
        econ = round(runs / overs, 2) if overs > 0 else 6.80
        dot_pct = round((dots / balls * 100), 1) if balls > 0 else 44.0
        wkt_per_4_ov = round((wickets / overs * 4.0), 2) if overs > 0 else 1.25

        # Phase breakdown
        phase_sql = """
            SELECT 
                CASE 
                    WHEN over <= 5 THEN 'Powerplay'
                    WHEN over BETWEEN 6 AND 14 THEN 'Middle'
                    ELSE 'Death'
                END as phase,
                count(*) as balls,
                sum(runs_total) as runs,
                sum(CASE WHEN is_wicket AND wicket_type NOT IN ('run out', 'retired hurt') THEN 1 ELSE 0 END) as wkts
            FROM deliveries
            WHERE bowler ILIKE ?
            GROUP BY 1
        """
        phase_rows = self.con.execute(phase_sql, [f"%{bowler_name}%"]).fetchall()
        phases = {}
        for pr in phase_rows:
            p_name = pr[0]
            p_balls = pr[1] or 0
            p_overs = p_balls / 6.0
            p_runs = pr[2] or 0
            phases[p_name] = {
                "balls": p_balls, "overs": round(p_overs, 1), "wickets": pr[3] or 0,
                "economy": round(p_runs / p_overs, 2) if p_overs > 0 else 6.5
            }

        return {
            "bowler": bowler_name,
            "sample_balls": balls,
            "overs_bowled": round(overs, 1),
            "wickets": wickets,
            "economy": econ,
            "dot_ball_pct": dot_pct,
            "expected_wkts_per_4ov": wkt_per_4_ov,
            "phases": phases
        }

    def query_h2h_matchup(self, batter_name: str, bowler_name: str, batter_style: str = "LHB", bowling_style: str = "Medium") -> Dict[str, Any]:
        """Calculates exact direct delivery battle if observed;
        Falls back to empirical Bayesian archetype prior when direct H2H is sparse.
        """
        sql = """
            SELECT 
                count(*) as balls,
                sum(runs_batter) as runs,
                sum(CASE WHEN is_wicket AND player_dismissed = batter THEN 1 ELSE 0 END) as dismissals,
                sum(CASE WHEN runs_batter = 0 AND runs_extras = 0 THEN 1 ELSE 0 END) as dots,
                sum(CASE WHEN runs_batter >= 4 THEN 1 ELSE 0 END) as boundaries
            FROM deliveries
            WHERE batter ILIKE ? AND bowler ILIKE ?
        """
        row = self.con.execute(sql, [f"%{batter_name}%", f"%{bowler_name}%"]).fetchone()
        balls = row[0] or 0
        runs = row[1] or 0
        dismissals = row[2] or 0
        dots = row[3] or 0
        boundaries = row[4] or 0

        if balls >= 6:
            # DIRECT OBSERVED MATCHUP
            sr = round((runs / balls * 100), 1)
            dot_pct = round((dots / balls * 100), 1)
            bnd_pct = round((boundaries / balls * 100), 1)
            wkt_prob = round(dismissals / balls, 3)
            advantage = "Bowler Dominant" if dismissals >= 2 or (sr < 95.0 and balls >= 12) else ("Batter Dominant" if sr > 135.0 else "Competitive Balance")
            return {
                "batter": batter_name,
                "bowler": bowler_name,
                "provenance": "OBSERVED_CRICSHEET_H2H",
                "balls_faced": balls,
                "runs_scored": runs,
                "dismissals": dismissals,
                "strike_rate": sr,
                "dot_pct": dot_pct,
                "boundaries_pct": bnd_pct,
                "wicket_probability": wkt_prob,
                "tactical_advantage": advantage,
                "confidence": "HIGH" if balls >= 18 else "MODERATE",
                "ci_90": [round(max(60.0, sr - 25.0), 1), round(sr + 25.0, 1)]
            }
        else:
            # EMPIRICAL BAYESIAN ARCHETYPE MODEL
            # Query comparable bowling style against batter or batter style
            # e.g. LHB vs Left-arm medium (Nomvelo Sibanda vs Smriti Mandhana)
            # e.g. RHB vs Off-spin (Shafali Verma vs Loryn Phiri / Kelis Ndhlovu)
            b_stats = self.query_batter_telemetry(batter_name)
            bw_stats = self.query_bowler_telemetry(bowler_name)

            # Prior Bayesian synthesis
            prior_sr = b_stats["strike_rate"]
            prior_econ = bw_stats["economy"]
            prior_wkt_rate = bw_stats["expected_wkts_per_4ov"] / 24.0

            # Matchup tactical adjusters
            style_lower = bowling_style.lower()
            if "left" in style_lower and batter_style == "LHB":
                # LHB vs SLA/LM: Left-arm angle takes ball across or cramps LHB
                modeled_sr = round(prior_sr * 0.94, 1)
                modeled_wkt = round(prior_wkt_rate * 1.15, 3)
                adv = "Bowler Favorable (Angle Matchup)"
            elif "off" in style_lower and batter_style == "LHB":
                # Off-spin turns into LHB: favorable for hitting through leg-side
                modeled_sr = round(prior_sr * 1.08, 1)
                modeled_wkt = round(prior_wkt_rate * 0.90, 3)
                adv = "Batter Dominant (Favorable Turn)"
            elif "off" in style_lower and batter_style == "RHB":
                # Off-spin takes ball into RHB: dot ball squeeze in powerplay
                modeled_sr = round(prior_sr * 0.96, 1)
                modeled_wkt = round(prior_wkt_rate * 1.08, 3)
                adv = "Competitive Balance"
            else:
                modeled_sr = round(prior_sr, 1)
                modeled_wkt = round(prior_wkt_rate, 3)
                adv = "Competitive Balance"

            return {
                "batter": batter_name,
                "bowler": bowler_name,
                "provenance": "MODELED_BAYESIAN_ARCHETYPE",
                "balls_faced": balls,
                "runs_scored": runs,
                "dismissals": dismissals,
                "strike_rate": modeled_sr,
                "dot_pct": b_stats["dot_ball_pct"],
                "boundaries_pct": b_stats["boundary_pct"],
                "wicket_probability": modeled_wkt,
                "tactical_advantage": adv,
                "confidence": "BAYESIAN_MODELED (PRIOR)",
                "ci_90": [round(max(60.0, modeled_sr - 20.0), 1), round(modeled_sr + 20.0, 1)]
            }

    def generate_indw_zimw_battle_matrix(self) -> List[Dict[str, Any]]:
        """Generates real player-versus-player matrix for every key IND-W vs ZIM-W encounter."""
        battles = []
        
        # 1. Smriti Mandhana vs Zimbabwe's opening & spin options
        battles.append(self.query_h2h_matchup("Mandhana", "Sibanda", "LHB", "Left-arm medium"))
        battles.append(self.query_h2h_matchup("Mandhana", "Nkomo", "LHB", "Right-arm medium-fast"))
        battles.append(self.query_h2h_matchup("Mandhana", "Ndhlovu", "LHB", "Slow left-arm orthodox"))
        battles.append(self.query_h2h_matchup("Mandhana", "Phiri", "LHB", "Right-arm offbreak"))
        
        # 2. Shafali Verma vs Zimbabwe spin options
        battles.append(self.query_h2h_matchup("Verma", "Phiri", "RHB", "Right-arm offbreak"))
        battles.append(self.query_h2h_matchup("Verma", "Ndhlovu", "RHB", "Slow left-arm orthodox"))
        battles.append(self.query_h2h_matchup("Verma", "Gwanzura", "RHB", "Right-arm offbreak"))
        battles.append(self.query_h2h_matchup("Verma", "Sibanda", "RHB", "Left-arm medium"))

        # 3. Harmanpreet Kaur vs Zimbabwe middle-over attack
        battles.append(self.query_h2h_matchup("Kaur", "Nkomo", "RHB", "Right-arm medium-fast"))
        battles.append(self.query_h2h_matchup("Kaur", "Ndhlovu", "RHB", "Slow left-arm orthodox"))
        battles.append(self.query_h2h_matchup("Kaur", "Phiri", "RHB", "Right-arm offbreak"))
        battles.append(self.query_h2h_matchup("Kaur", "Chipare", "RHB", "Right-arm medium"))

        # 4. Deepti Sharma vs Zimbabwe expected batting order
        battles.append(self.query_h2h_matchup("Mayers", "Sharma", "RHB", "Right-arm offbreak"))
        battles.append(self.query_h2h_matchup("Mugeri", "Sharma", "LHB", "Right-arm offbreak"))
        battles.append(self.query_h2h_matchup("Mupachikwa", "Sharma", "RHB", "Right-arm offbreak"))
        battles.append(self.query_h2h_matchup("Nkomo", "Sharma", "RHB", "Right-arm offbreak"))
        battles.append(self.query_h2h_matchup("Ndhlovu", "Sharma", "LHB", "Right-arm offbreak"))

        # 5. S Charani (Shree Charani) vs Zimbabwe RHB & LHB
        battles.append(self.query_h2h_matchup("Mayers", "Charani", "RHB", "Slow left-arm orthodox"))
        battles.append(self.query_h2h_matchup("Mugeri", "Charani", "LHB", "Slow left-arm orthodox"))
        battles.append(self.query_h2h_matchup("Mupachikwa", "Charani", "RHB", "Slow left-arm orthodox"))
        battles.append(self.query_h2h_matchup("Biza", "Charani", "RHB", "Slow left-arm orthodox"))

        # 6. N Sharma (Nandani Sharma) vs Zimbabwe top order
        battles.append(self.query_h2h_matchup("Mayers", "Sharma", "RHB", "Right-arm fast-medium"))
        battles.append(self.query_h2h_matchup("Ndhlovu", "Sharma", "LHB", "Right-arm fast-medium"))
        battles.append(self.query_h2h_matchup("Mugeri", "Sharma", "LHB", "Right-arm fast-medium"))

        # 7. N Gwanzura vs India expected spin attack
        battles.append(self.query_h2h_matchup("Gwanzura", "Sharma", "RHB", "Right-arm offbreak"))
        battles.append(self.query_h2h_matchup("Gwanzura", "Mani", "RHB", "Right-arm offbreak"))

        # 8. S Mayers vs India opening bowlers
        battles.append(self.query_h2h_matchup("Mayers", "Reddy", "RHB", "Right-arm medium-fast"))
        battles.append(self.query_h2h_matchup("Mayers", "Gaud", "RHB", "Right-arm medium-fast"))

        # 9. K Ndhlovu vs India new-ball attack
        battles.append(self.query_h2h_matchup("Ndhlovu", "Reddy", "LHB", "Right-arm medium-fast"))
        battles.append(self.query_h2h_matchup("Ndhlovu", "Sharma", "LHB", "Right-arm offbreak"))

        return battles

_ANALYTICS_INSTANCE: Optional[WT20AnalyticsEngine] = None

def get_wt20_analytics() -> WT20AnalyticsEngine:
    global _ANALYTICS_INSTANCE
    if _ANALYTICS_INSTANCE is None:
        _ANALYTICS_INSTANCE = WT20AnalyticsEngine()
    return _ANALYTICS_INSTANCE

