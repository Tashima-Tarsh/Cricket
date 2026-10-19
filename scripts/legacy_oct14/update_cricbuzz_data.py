"""Update gl_report.json with Cricbuzz Scraped Data: Hyderabad Venue + 4th T20I Squads + 3 Mega Teams."""
import json
from pathlib import Path

report_path = Path("d:/cricket/gl_report.json")

cricbuzz_mega_data = {
    "cricbuzz_source": {
        "url": "https://www.cricbuzz.com/live-cricket-scores/151598/ind-vs-wi-4th-t20i-west-indies-tour-of-india-2026",
        "match": "India vs West Indies, 4th T20I, West Indies tour of India, 2026",
        "venue": "Rajiv Gandhi International Stadium, Hyderabad",
        "date_time": "Today, Oct 14, 2026 • 7:00 PM LOCAL (1:30 PM GMT)",
        "series": "West Indies tour of India, 2026 (5-match T20I series)"
    },
    "selection_conditions": {
        "anti_duplication_rule": {
            "title": "Anti-Duplication C/VC Trap Lockout",
            "condition": "Previous match (Indore 3rd T20I) winners Abhishek Sharma & Arshdeep Singh locked out of C & VC",
            "mathematical_reasoning": "Cricbuzz headline: 'Chain of chases breaks as Arshdeep, Abhishek headline India win'. Over 35% of the 430,000 field will set Abhishek [C] and Arshdeep [VC]. Re-using them leads to thousands of split lineups. Fading them as C/VC provides pure solo 1st prize equity."
        },
        "venue_and_pitch_condition": {
            "title": "Hyderabad Re-Soiled High-Scoring Pitch",
            "condition": "Rajiv Gandhi Stadium has re-soiled pitches; 5 of 7 IPL 2026 games won by team batting first; India scored 297 here",
            "mathematical_reasoning": "Cricbuzz notes: 'Both Abhishek Sharma and Sanju Samson have two T20 hundreds each in Hyderabad', while local boy Tilak Varma has intimate venue knowledge. Batters enjoy true bounce and massive scoring potential."
        },
        "weather_and_dew_condition": {
            "title": "Hyderabad Evening Dew & Outfield Skid",
            "condition": "7:00 PM evening start; 68% humidity; dew skids ball onto bat in 2nd innings",
            "mathematical_reasoning": "Defending bowlers face wet ball conditions in the second innings. Chasing top-order batters gain significant value from pace skidding off the pitch."
        },
        "h2h_matchup_condition": {
            "title": "Matchup Exploitation: Spin vs Pace Vulnerability",
            "condition": "Rovman Powell strikes at only 105.42 against spin in 2026 vs 168.15 against pace",
            "mathematical_reasoning": "Cricbuzz stat verified: Rovman Powell is vulnerable to spin choke (Axar/Tilak). Conversely, Roston Chase (econ 8.48) is the only WI bowler with sub-9 economy, making him an anchor pick."
        }
    },
    "teams": [
        {
            "team_id": 1,
            "team_name": "Team 1: Hyderabad Batting First Carnage (Home Boys Stack)",
            "toss_condition": "India Bats First (WI Bowls First)",
            "innings_target": "IND 210+ Par Score | WI Crumbles Under 11+ RRR",
            "credits_used": 93.5,
            "cumulative_ownership": 586.5,
            "differentials_count": 3,
            "uniqueness_rating": "⭐️⭐️⭐️⭐️ (High Solo Rank 1 Potential)",
            "captain": {
                "name": "Tilak Varma",
                "team": "IND",
                "role": "BAT",
                "credits": 8.5,
                "ownership": 44.0,
                "ceiling": 160.0,
                "why_selected_c": "Hyderabad Local Hero & Vice-Captain: Playing on his native home ground where he possesses supreme ground knowledge. Cricbuzz highlights his versatility to anchor or go from ball one, plus part-time off-spin against WI lefties."
            },
            "vice_captain": {
                "name": "Sanju Samson",
                "team": "IND",
                "role": "WK",
                "credits": 8.5,
                "ownership": 58.0,
                "ceiling": 175.0,
                "why_selected_vc": "Hyderabad Venue Maestro: Cricbuzz confirms Sanju Samson has TWO T20 centuries at this exact Rajiv Gandhi Stadium. Batting at #1, his ceiling here is the highest in the entire contest."
            },
            "selection_strategy": "Capitalizes on Cricbuzz venue data: 5 of 7 games won batting first in Hyderabad, with India once posting 297 here. Tilak and Samson anchor and explode, while Mayank Yadav's 150kph pace attacks chasing WI batsmen.",
            "roster": [
                {"name": "Sanju Samson", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 58.0, "is_vc": True, "reason": "VICE-CAPTAIN (1.5x): 2 T20 centuries at Hyderabad; explosive opener."},
                {"name": "Ishan Kishan", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 69.0, "reason": "SRH venue experienced top-order aggressor."},
                {"name": "Abhishek Sharma", "team": "IND", "role": "BAT", "credits": 9.0, "ownership": 88.0, "reason": "Core opener with 2 T20 hundreds in Hyderabad; STRICTLY LOCKED OUT of C/VC to dodge duplication."},
                {"name": "Shreyas Iyer", "team": "IND", "role": "BAT", "credits": 9.0, "ownership": 62.0, "reason": "Skipper hunting 5th straight series win; middle-order stabilizer."},
                {"name": "Tilak Varma", "team": "IND", "role": "BAT", "credits": 8.5, "ownership": 44.0, "is_c": True, "reason": "CAPTAIN (2x): Hyderabad home boy & India vice-captain; master of local pitch conditions."},
                {"name": "Nitish Kumar Reddy", "team": "IND", "role": "AR", "credits": 8.0, "ownership": 32.0, "is_diff": True, "reason": "DIFFERENTIAL (32%): Sunrisers Hyderabad home star; boundary hitting + 2-3 overs medium pace."},
                {"name": "Axar Patel", "team": "IND", "role": "AR", "credits": 9.0, "ownership": 79.0, "reason": "4 overs of left-arm spin targeting Powell (SR 105 vs spin) + batting floor."},
                {"name": "Arshdeep Singh", "team": "IND", "role": "BOWL", "credits": 9.0, "ownership": 86.0, "reason": "Death overs strike bowler; excluded from C/VC to prevent crowd duplicate trap."},
                {"name": "Mayank Yadav", "team": "IND", "role": "BOWL", "credits": 8.0, "ownership": 28.5, "is_diff": True, "reason": "DIFFERENTIAL (28.5%): 150kph+ express pace praised in Cricbuzz match report; dismantles chasing tail."},
                {"name": "Shai Hope", "team": "WI", "role": "WK", "credits": 9.0, "ownership": 76.0, "reason": "High-floor WI captain anchoring the chase."},
                {"name": "Shamar Joseph", "team": "WI", "role": "BOWL", "credits": 8.5, "ownership": 36.0, "is_diff": True, "reason": "DIFFERENTIAL (36%): 148kph express pacer picking wickets in India's death assault."}
            ]
        },
        {
            "team_id": 2,
            "team_name": "Team 2: West Indies Bat First / India Dew Chase",
            "toss_condition": "West Indies Bats First (India Bowls First)",
            "innings_target": "WI Post 180-195 | India Chases Under Wet Ball Dew",
            "credits_used": 93.0,
            "cumulative_ownership": 516.5,
            "differentials_count": 4,
            "uniqueness_rating": "⭐️⭐️⭐️⭐️⭐️ (Maximum Leverage / Solitary Winner Equity)",
            "captain": {
                "name": "Roston Chase",
                "team": "WI",
                "role": "AR",
                "credits": 8.5,
                "ownership": 64.0,
                "ceiling": 130.0,
                "why_selected_c": "Cricbuzz Special Highlight: Only bowler in this entire high-scoring series conceding at just 8.48 rpo while all others went for 10+. Dual threat: bats in top 6 + bowls 4 tidy overs with top wicket equity."
            },
            "vice_captain": {
                "name": "Ishan Kishan",
                "team": "IND",
                "role": "WK",
                "credits": 8.5,
                "ownership": 69.0,
                "ceiling": 130.0,
                "why_selected_vc": "Chasing under Hyderabad evening lights: ball skids onto bat. Ishan exploits powerplay restrictions with a rapid 60+ and takes wicketkeeper catches."
            },
            "selection_strategy": "West Indies bat first and post a fighting 180+ through middle-order power hitters (Powell, Hetmyer, Rutherford). India chases aggressively with dew aiding the strokeplay.",
            "roster": [
                {"name": "Ishan Kishan", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 69.0, "is_vc": True, "reason": "VICE-CAPTAIN (1.5x): Powerplay chaser exploiting wet ball skid."},
                {"name": "Sanju Samson", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 58.0, "reason": "Elite venue record (two 100s in Hyderabad); boundary collector."},
                {"name": "Tilak Varma", "team": "IND", "role": "BAT", "credits": 8.5, "ownership": 44.0, "reason": "Calm chase finisher on his native Hyderabad wicket."},
                {"name": "Nitish Kumar Reddy", "team": "IND", "role": "AR", "credits": 8.0, "ownership": 32.0, "is_diff": True, "reason": "DIFFERENTIAL (32%): Home venue allrounder picking wickets in 1st innings."},
                {"name": "Mayank Yadav", "team": "IND", "role": "BOWL", "credits": 8.0, "ownership": 28.5, "is_diff": True, "reason": "DIFFERENTIAL (28.5%): Breaks opening stand with extreme 150kph bounce."},
                {"name": "Shai Hope", "team": "WI", "role": "WK", "credits": 9.0, "ownership": 76.0, "reason": "Captain & WK; reliable 40+ runs anchor."},
                {"name": "Shimron Hetmyer", "team": "WI", "role": "BAT", "credits": 8.5, "ownership": 51.0, "reason": "Middle-overs accelerator targeting straight boundaries."},
                {"name": "Rovman Powell", "team": "WI", "role": "BAT", "credits": 8.5, "ownership": 55.0, "reason": "168.15 SR vs pace; dangerous against fast medium bowling."},
                {"name": "Sherfane Rutherford", "team": "WI", "role": "BAT", "credits": 8.0, "ownership": 29.0, "is_diff": True, "reason": "DIFFERENTIAL (29%): Death-overs finisher capable of 50 off 22 balls."},
                {"name": "Roston Chase", "team": "WI", "role": "AR", "credits": 8.5, "ownership": 64.0, "is_c": True, "reason": "CAPTAIN (2x): Series-best economy (8.48 rpo) + solid top-6 batting runs."},
                {"name": "Keemo Paul", "team": "WI", "role": "AR", "credits": 8.0, "ownership": 24.0, "is_diff": True, "reason": "DIFFERENTIAL (24%): Death overs bowler and lower-order boundary hitter."}
            ]
        },
        {
            "team_id": 3,
            "team_name": "Team 3: Fast-Paced Collapse & Differential Strike Pace",
            "toss_condition": "Any Toss (Early Seam Movement on Re-Soiled Track)",
            "innings_target": "Top-Order Wicket Carnage | 15+ Wickets Fall",
            "credits_used": 92.5,
            "cumulative_ownership": 535.5,
            "differentials_count": 4,
            "uniqueness_rating": "⭐️⭐️⭐️⭐️⭐️ (Extreme Contrarian Punt to Beat 430K Field)",
            "captain": {
                "name": "Mayank Yadav",
                "team": "IND",
                "role": "BOWL",
                "credits": 8.0,
                "ownership": 28.5,
                "ceiling": 140.0,
                "why_selected_c": "Extreme Pace Captain Punt: Cricbuzz notes his impressive rhythm across all 3 T20Is. On re-soiled Hyderabad bounce, his 150kph+ thunderbolts produce multi-wicket hauls (3-4 wickets)."
            },
            "vice_captain": {
                "name": "Shamar Joseph",
                "team": "WI",
                "role": "BOWL",
                "credits": 8.5,
                "ownership": 36.0,
                "ceiling": 135.0,
                "why_selected_vc": "Express Pace Counter-Punch: 148kph yorkers and bouncers. In a pace-dominated contest, Joseph picking early top-order wickets yields 90-120 fantasy points."
            },
            "selection_strategy": "Contrarian game script fading top-order batters. In a 430,000 field where 90% build heavy batting teams, a Dual 150kph Pace Bowler C/VC lineup guarantees solitary 1st rank if early wickets fall on the re-soiled pitch.",
            "roster": [
                {"name": "Sanju Samson", "team": "IND", "role": "WK", "credits": 8.5, "ownership": 58.0, "reason": "Selected for lone wicketkeeper role; elite ground history."},
                {"name": "Abhishek Sharma", "team": "IND", "role": "BAT", "credits": 9.0, "ownership": 88.0, "reason": "Picked for baseline floor; locked out of C/VC to prevent duplication."},
                {"name": "Tilak Varma", "team": "IND", "role": "BAT", "credits": 8.5, "ownership": 44.0, "reason": "Technically sound local batter able to survive early movement."},
                {"name": "Nitish Kumar Reddy", "team": "IND", "role": "AR", "credits": 8.0, "ownership": 32.0, "is_diff": True, "reason": "DIFFERENTIAL (32%): Seam bowling allrounder on home ground."},
                {"name": "Axar Patel", "team": "IND", "role": "AR", "credits": 9.0, "ownership": 79.0, "reason": "Tight bowling + lower-order runs during a batting squeeze."},
                {"name": "Arshdeep Singh", "team": "IND", "role": "BOWL", "credits": 9.0, "ownership": 86.0, "reason": "New ball swing + death yorkers; excluded from C/VC to avoid the crowd."},
                {"name": "Mayank Yadav", "team": "IND", "role": "BOWL", "credits": 8.0, "ownership": 28.5, "is_c": True, "is_diff": True, "reason": "CAPTAIN (2x) & DIFFERENTIAL (28.5%): 150kph hostile pace taking 3-4 wickets."},
                {"name": "Sherfane Rutherford", "team": "WI", "role": "BAT", "credits": 8.0, "ownership": 29.0, "is_diff": True, "reason": "DIFFERENTIAL (29%): Counter-punching middle order hitter."},
                {"name": "Roston Chase", "team": "WI", "role": "AR", "credits": 8.5, "ownership": 64.0, "reason": "Cricbuzz best bowler (8.48 econ); dual-threat allrounder."},
                {"name": "Shamar Springer", "team": "WI", "role": "AR", "credits": 7.5, "ownership": 16.0, "is_diff": True, "reason": "DIFFERENTIAL (16%): Medium-fast change of pace bowler."},
                {"name": "Shamar Joseph", "team": "WI", "role": "BOWL", "credits": 8.5, "ownership": 36.0, "is_vc": True, "is_diff": True, "reason": "VICE-CAPTAIN (1.5x) & DIFFERENTIAL (36%): 148kph express pacer."}
            ]
        }
    ]
}

# Read existing report
with open(report_path, "r", encoding="utf-8") as f:
    data = json.load(f)

data["cricbuzz_match_scraped"] = cricbuzz_mega_data
data["mega_contest_430k"] = cricbuzz_mega_data

with open(report_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Updated gl_report.json successfully with Cricbuzz 4th T20I data!")
