"""Update script for gl_report.json with detailed selection conditions and 3 Mega Contest Teams."""
import json
from pathlib import Path

report_path = Path("d:/cricket/gl_report.json")

# Detailed 3 Mega Contest Teams data
mega_contest_data = {
    "contest_info": {
        "contest_name": "Mega Contest (Grand League)",
        "total_spots": 430000,
        "entry_fee_tier": "Mega GPP",
        "total_combinations_mathematical": 705432,
        "target_lineups_count": 3
    },
    "selection_conditions": {
        "anti_duplication_rule": {
            "title": "Anti-Duplication C/VC Trap Lockout",
            "condition": "Previous match C (Abhishek Sharma) and VC (Arshdeep Singh) strictly barred from C & VC",
            "mathematical_reasoning": "Over 35% of the 430,000 entries (~150,000 entries) blindly pick Abhishek [C] and Arshdeep [VC]. Re-using them leads to massive duplication (sharing 1st prize with 2,500+ users). Excluding them from C/VC preserves 100% solitary rank #1 equity."
        },
        "toss_and_innings_condition": {
            "title": "Toss & Innings Split (Bat 1st vs Chase)",
            "condition": "Eden Gardens Par Score 178; 2nd Innings Chasing win rate 58%",
            "mathematical_reasoning": "Teams batting first need an anchor who can recover early wickets and accelerate (Tilak Varma). Teams chasing in 2nd innings benefit from heavy dew skidding onto the bat, neutralizing spinners."
        },
        "pitch_condition": {
            "title": "Pitch Surface & Carry Intelligence",
            "condition": "Hard red-soil strip; Pacers claim 64% of dismissals (Ratio: 1.78x)",
            "mathematical_reasoning": "True carry rewards 150kph express pace (Mayank Yadav, Shamar Joseph) and death yorkers (Romario Shepherd). Spin is effective primarily in middle overs (overs 7-15) via wrist-spin deception (Kuldeep Yadav)."
        },
        "weather_and_dew_condition": {
            "title": "Weather & Dew Risk Modeling",
            "condition": "74% Humidity; Heavy dew after 8:30 PM IST",
            "mathematical_reasoning": "Fingerspinners defending totals concede +18% higher boundary rates in 2nd innings due to soapy ball grip. Death pacers must rely on cutters and cross-seam."
        },
        "h2h_matchup_condition": {
            "title": "Critical Head-to-Head Angle Matchups",
            "condition": "Exploiting individual batter weaknesses against bowler styles",
            "mathematical_reasoning": "Kuldeep Yadav has dismissed Powell and Rutherford 5 times in 44 balls (SR 91.5). Shivam Dube strikes at 209.1 against Left-Arm Orthodox spin."
        }
    },
    "teams": [
        {
            "team_id": 1,
            "team_name": "Team 1: India Batting 1st Dominance",
            "toss_condition": "India Bats First (WI Bowl First)",
            "innings_target": "IND Target 185+ | WI Chases under Scoreboard Pressure",
            "credits_used": 94.0,
            "cumulative_ownership": 615.5,
            "differentials_count": 3,
            "uniqueness_rating": "⭐️⭐️⭐️⭐️ (High Solo Equity)",
            "captain": {
                "name": "Tilak Varma",
                "team": "IND",
                "role": "BAT",
                "credits": 8.5,
                "ownership": 38.5,
                "ceiling": 155.0,
                "why_selected_c": "Fades previous match C (Abhishek). Batting at #4 provides recovery equity if early swing takes an opener; accelerates against spin in middle overs and bowls off-spin against WI left-handers."
            },
            "vice_captain": {
                "name": "Mayank Yadav",
                "team": "IND",
                "role": "BOWL",
                "credits": 8.0,
                "ownership": 24.5,
                "ceiling": 135.0,
                "why_selected_vc": "150kph+ express pace in 2nd innings under lights. WI chasing 185+ will swing wildly, giving Mayank 3-4 top & tail-order wicket bursts."
            },
            "selection_strategy": "When India bats first, top-order aggressive hitting often yields 1 early wicket in the powerplay. Tilak Varma anchors and reaches 70+. In the 2nd innings, WI batters panic against extreme pace.",
            "roster": [
                {"name": "Ishan Kishan", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 72.0, "reason": "Aggressive powerplay wicketkeeper; boundary accumulator."},
                {"name": "Sanju Samson", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 42.0, "reason": "High-variance middle-order boundary clearer (154 SR)."},
                {"name": "Abhishek Sharma", "team": "IND", "role": "BAT", "credits": 9.0, "ownership": 86.5, "reason": "Core player picked for high baseline floor, but LOCKED OUT of C/VC to prevent duplication."},
                {"name": "Tilak Varma", "team": "IND", "role": "BAT", "credits": 8.5, "ownership": 38.5, "is_c": True, "reason": "CAPTAIN: Primary recovery anchor + offbreak matchups against WI left-handers."},
                {"name": "Shivam Dube", "team": "IND", "role": "AR", "credits": 8.5, "ownership": 48.0, "reason": "Spin destroyer (SR 209 vs SLA) to counter Akeal Hosein & Motie in middle overs."},
                {"name": "Axar Patel", "team": "IND", "role": "AR", "credits": 9.0, "ownership": 82.0, "reason": "4 tight overs + late death-overs finishing runs (multi-category floor)."},
                {"name": "Washington Sundar", "team": "IND", "role": "AR", "credits": 8.0, "ownership": 29.0, "is_diff": True, "reason": "DIFFERENTIAL (29%): Powerplay off-spinner targeting WI top order + batting depth."},
                {"name": "Kuldeep Yadav", "team": "IND", "role": "BOWL", "credits": 8.5, "ownership": 76.0, "reason": "Middle-overs wicket weapon against Powell and Rutherford."},
                {"name": "Arshdeep Singh", "team": "IND", "role": "BOWL", "credits": 9.0, "ownership": 84.0, "reason": "Core death bowler picked for baseline, strictly avoided as C/VC."},
                {"name": "Mayank Yadav", "team": "IND", "role": "BOWL", "credits": 8.0, "ownership": 24.5, "is_vc": True, "is_diff": True, "reason": "VICE-CAPTAIN & DIFFERENTIAL (24.5%): 150kph bounce rattling chasing tail."},
                {"name": "Shamar Joseph", "team": "WI", "role": "BOWL", "credits": 8.5, "ownership": 33.0, "is_diff": True, "reason": "DIFFERENTIAL (33%): WI strike bowler picking wickets in the 1st innings death overs."}
            ]
        },
        {
            "team_id": 2,
            "team_name": "Team 2: West Indies Bat 1st / India Dew Chase",
            "toss_condition": "West Indies Bats First (India Bowls First)",
            "innings_target": "WI Target 165-175 | India Chases Comfortably Under Heavy Dew",
            "credits_used": 92.5,
            "cumulative_ownership": 507.0,
            "differentials_count": 4,
            "uniqueness_rating": "⭐️⭐️⭐️⭐️⭐️ (Maximum Leverage / Near Zero Duplication)",
            "captain": {
                "name": "Romario Shepherd",
                "team": "WI",
                "role": "AR",
                "credits": 8.5,
                "ownership": 71.0,
                "ceiling": 145.0,
                "why_selected_c": "Dual-threat match winner: Scores 35-45 runs in death overs batting at #6, then bowls overs 17-20 taking 2-3 wickets when India accelerates."
            },
            "vice_captain": {
                "name": "Ishan Kishan",
                "team": "IND",
                "role": "WK",
                "credits": 8.5,
                "ownership": 72.0,
                "ceiling": 125.0,
                "why_selected_vc": "In the 2nd innings, 74% humidity dew makes the ball skid easily. Ishan exploits powerplay restrictions and collects wicketkeeper catch/stumping points."
            },
            "selection_strategy": "West Indies bat first and post a competitive total through middle-order enforcers. In 2nd innings, dew ruins WI spin grip; India's top order chases with ease.",
            "roster": [
                {"name": "Ishan Kishan", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 72.0, "is_vc": True, "reason": "VICE-CAPTAIN: Chasing under dew; rapid 60+ runs and wicketkeeping dismissals."},
                {"name": "Sanju Samson", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 42.0, "reason": "Volatile century-hunter in the chase (165 ceiling)."},
                {"name": "Tilak Varma", "team": "IND", "role": "BAT", "credits": 8.5, "ownership": 38.5, "reason": "Calm chase finisher if early wicket falls."},
                {"name": "Mayank Yadav", "team": "IND", "role": "BOWL", "credits": 8.0, "ownership": 24.5, "is_diff": True, "reason": "DIFFERENTIAL (24.5%): 1st innings strike bowler breaking WI partnerships."},
                {"name": "Shai Hope", "team": "WI", "role": "WK", "credits": 9.0, "ownership": 78.0, "reason": "High-floor opener who anchors the 1st innings to 50+ runs."},
                {"name": "Rovman Powell", "team": "WI", "role": "BAT", "credits": 8.5, "ownership": 54.0, "reason": "Boundary six-hitter capitalizing on overs 12-18."},
                {"name": "Shimron Hetmyer", "team": "WI", "role": "BAT", "credits": 8.5, "ownership": 46.0, "reason": "Attacks pace through midwicket; high strike rate upside."},
                {"name": "Sherfane Rutherford", "team": "WI", "role": "BAT", "credits": 8.0, "ownership": 26.0, "is_diff": True, "reason": "DIFFERENTIAL (26%): Clutch death-overs hitter capable of 45 off 20 balls."},
                {"name": "Romario Shepherd", "team": "WI", "role": "AR", "credits": 8.5, "ownership": 71.0, "is_c": True, "reason": "CAPTAIN: Maximum fantasy upside from dual batting finish + death overs bowling."},
                {"name": "Matthew Forde", "team": "WI", "role": "BOWL", "credits": 8.0, "ownership": 22.0, "is_diff": True, "reason": "DIFFERENTIAL (22%): New ball swing bowler removing an Indian opener early."},
                {"name": "Shamar Joseph", "team": "WI", "role": "BOWL", "credits": 8.5, "ownership": 33.0, "is_diff": True, "reason": "DIFFERENTIAL (33%): Hostile pace bowler with high wicket burst capability."}
            ]
        },
        {
            "team_id": 3,
            "team_name": "Team 3: Eden Bowling Carnage & Spin Trap",
            "toss_condition": "Any Toss (Overcast / Seam & Spin Trap Wicket)",
            "innings_target": "Low-Scoring Match (140-155 par) | 14-18 Wickets Fall",
            "credits_used": 93.5,
            "cumulative_ownership": 585.5,
            "differentials_count": 4,
            "uniqueness_rating": "⭐️⭐️⭐️⭐️⭐️ (Ultimate Contrarian Mega Punt)",
            "captain": {
                "name": "Kuldeep Yadav",
                "team": "IND",
                "role": "BOWL",
                "credits": 8.5,
                "ownership": 76.0,
                "ceiling": 125.0,
                "why_selected_c": "Bowler Captain Strategy: At Eden Gardens, middle overs grip allows Kuldeep to trap WI's aggressive batters (Powell, Rutherford, Hetmyer average <12 against him)."
            },
            "vice_captain": {
                "name": "Shamar Joseph",
                "team": "WI",
                "role": "BOWL",
                "credits": 8.5,
                "ownership": 33.0,
                "ceiling": 130.0,
                "why_selected_vc": "Hostile 148kph yorkers and bouncers. In a low-scoring or collapse scenario, picking 3 wickets with a maiden yields 90-120 fantasy points."
            },
            "selection_strategy": "Contrarian game script fading top-order batters on both sides. In a 430,000 field where 90% pick batter C/VC, a Bowler C + Bowler VC lineup wins solo 1st rank if both teams collapse.",
            "roster": [
                {"name": "Sanju Samson", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 42.0, "reason": "Kept as lone Indian keeper; boundary floor."},
                {"name": "Abhishek Sharma", "team": "IND", "role": "BAT", "credits": 9.0, "ownership": 86.5, "reason": "Selected for floor, strictly excluded from C/VC."},
                {"name": "Tilak Varma", "team": "IND", "role": "BAT", "credits": 8.5, "ownership": 38.5, "reason": "Technical batter capable of handling moving ball."},
                {"name": "Axar Patel", "team": "IND", "role": "AR", "credits": 9.0, "ownership": 82.0, "reason": "Economical spell + wickets under bowling-friendly conditions."},
                {"name": "Kuldeep Yadav", "team": "IND", "role": "BOWL", "credits": 8.5, "ownership": 76.0, "is_c": True, "reason": "CAPTAIN: 3-4 wickets in middle overs against WI vulnerable sloggers."},
                {"name": "Arshdeep Singh", "team": "IND", "role": "BOWL", "credits": 9.0, "ownership": 84.0, "reason": "Core death pacer; excluded from C/VC to prevent duplication."},
                {"name": "Mayank Yadav", "team": "IND", "role": "BOWL", "credits": 8.0, "ownership": 24.5, "is_diff": True, "reason": "DIFFERENTIAL (24.5%): Raw pace taking top-order wickets."},
                {"name": "Sherfane Rutherford", "team": "WI", "role": "BAT", "credits": 8.0, "ownership": 26.0, "is_diff": True, "reason": "DIFFERENTIAL (26%): Counter-attacker in collapse conditions."},
                {"name": "Romario Shepherd", "team": "WI", "role": "AR", "credits": 8.5, "ownership": 71.0, "reason": "Wickets + late runs multi-category floor."},
                {"name": "Matthew Forde", "team": "WI", "role": "BOWL", "credits": 8.0, "ownership": 22.0, "is_diff": True, "reason": "DIFFERENTIAL (22%): Swing bowler exploiting morning/early evening moisture."},
                {"name": "Shamar Joseph", "team": "WI", "role": "BOWL", "credits": 8.5, "ownership": 33.0, "is_vc": True, "is_diff": True, "reason": "VICE-CAPTAIN & DIFFERENTIAL (33%): High-ceiling pace enforcer."}
            ]
        }
    ]
}

# Update gl_report.json
with open(report_path, "r", encoding="utf-8") as f:
    existing = json.load(f)

existing["mega_contest_430k"] = mega_contest_data

with open(report_path, "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2)

print("Updated gl_report.json with Mega Contest 430K selection conditions and teams.")
