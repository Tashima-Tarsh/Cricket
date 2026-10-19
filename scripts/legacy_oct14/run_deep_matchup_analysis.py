"""Deep Bowling Matchups, Wicket Fall Predictions, Innings Scenarios & Mega Contest Teams."""
import json
from pathlib import Path

# Matchup & Game Script Engine
matchup_analysis = {
    "pitch_behavior_red_soil": {
        "composition": "80% Red Soil + 20% Black Soil (Relaid 45 days ago)",
        "pace_effect": "Hard surface generates steep, unpredictable bounce for bowlers delivering at 145-152 kph (Mayank Yadav & Shamar Joseph).",
        "spin_effect": "Cracks packed with straw offer sharp bite in 1st innings; however, 2nd innings dew neutralizes spin grip.",
        "boundary_bias": "64m & 67m square boundaries encourage sixes (avg 24 sixes); 75m straight boundary causes mistimed aerial catches against short balls."
    },
    "west_indies_batting_first_breakdown": {
        "projected_score": "181/7 in 20.0 Overs (Range: 176 - 188)",
        "powerplay_phase": {
            "overs": "1 to 6",
            "score_prediction": "48/2",
            "fast_wickets_falling": [
                {
                    "wicket_num": 1,
                    "over": "2.4",
                    "batter_out": "Shai Hope",
                    "bowler": "Arshdeep Singh",
                    "dismissal_mode": "Caught behind (wkt Sanju Samson)",
                    "tactical_matchup": "Arshdeep angles the left-arm swing across Shai Hope outside off. Hope's tentative poke away from the body finds the outside edge."
                },
                {
                    "wicket_num": 2,
                    "over": "4.3",
                    "batter_out": "Jewel Andrew",
                    "bowler": "Mayank Yadav",
                    "dismissal_mode": "Top edge pull caught at midwicket (fielder Tilak Varma)",
                    "tactical_matchup": "Mayank clocks 151.4 kph on the 80% red-soil pitch. The steep bounce hurries the 19yo Andrew into a mistimed pull shot."
                }
            ]
        },
        "middle_overs_phase": {
            "overs": "7 to 15",
            "score_prediction": "119/4",
            "fast_wickets_falling": [
                {
                    "wicket_num": 3,
                    "over": "9.5",
                    "batter_out": "Rovman Powell",
                    "bowler": "Axar Patel",
                    "dismissal_mode": "Bowled (arm ball skidding through cracks)",
                    "tactical_matchup": "Powell has a major documented weakness against spin in 2026 (striking at only 105.42 vs spin compared to 168.15 vs pace). Axar darts an arm-ball that skids low off the cracks."
                },
                {
                    "wicket_num": 4,
                    "over": "13.2",
                    "batter_out": "Shimron Hetmyer",
                    "bowler": "Nitish Kumar Reddy",
                    "dismissal_mode": "Caught long-on attempting to clear 75m straight boundary",
                    "tactical_matchup": "Hetmyer strikes well against short square boundaries, but Nitish Reddy drags the length back outside off, forcing Hetmyer down the longer 75m ground."
                }
            ]
        },
        "death_overs_phase": {
            "overs": "16 to 20",
            "score_prediction": "181/7 (62 runs scored in last 5 overs)",
            "key_performers": "Romario Shepherd (44 off 21 balls, 4 sixes) & Sherfane Rutherford (34 off 18 balls) exploit 64m boundaries.",
            "fast_wickets_falling": [
                {
                    "wicket_num": 5,
                    "over": "17.4",
                    "batter_out": "Sherfane Rutherford",
                    "bowler": "Mayank Yadav",
                    "dismissal_mode": "Clean bowled by 150 kph yorker",
                    "tactical_matchup": "Mayank changes pace and nails a 150kph toe-crusher as Rutherford clears his front leg."
                },
                {
                    "wicket_num": 6,
                    "over": "19.3",
                    "batter_out": "Keemo Paul",
                    "bowler": "Arshdeep Singh",
                    "dismissal_mode": "Caught deep backward square leg",
                    "tactical_matchup": "Arshdeep wide slower bouncer miscued."
                }
            ]
        }
    },
    "india_chasing_breakdown": {
        "target": "182 Runs to Win from 120 Balls",
        "projected_finish": "India 184/3 in 18.4 Overs (Wins by 7 Wickets)",
        "dew_effect": "Dew begins heavily around 8:15 PM IST. Outfield accelerates dramatically, and West Indies spinners Motie and Chase struggle to grip the wet seam.",
        "powerplay_phase": {
            "overs": "1 to 6",
            "score_prediction": "56/1",
            "fast_wickets_falling": [
                {
                    "wicket_num": 1,
                    "over": "4.1",
                    "batter_out": "Abhishek Sharma",
                    "runs_scored": "32 (15 balls, 3 sixes, 2 fours)",
                    "bowler": "Shamar Joseph",
                    "dismissal_mode": "Caught deep square leg (fielder Powell)",
                    "tactical_matchup": "Abhishek attacks aggressively in the powerplay. Shamar Joseph bends his back at 148 kph and generates fierce red-soil bounce. A top edge lands in Powell's hands."
                }
            ]
        },
        "middle_overs_phase": {
            "overs": "7 to 15",
            "score_prediction": "142/3 (Partnership Samson & Ishan, then Samson & Tilak)",
            "fast_wickets_falling": [
                {
                    "wicket_num": 2,
                    "over": "9.4",
                    "batter_out": "Ishan Kishan",
                    "runs_scored": "34 (22 balls)",
                    "bowler": "Romario Shepherd",
                    "dismissal_mode": "LBW by slower off-cutter",
                    "tactical_matchup": "Shepherd deceives Ishan with a knuckle-ball dipping on middle stump."
                },
                {
                    "wicket_num": 3,
                    "over": "14.2",
                    "batter_out": "Shreyas Iyer",
                    "runs_scored": "18 (14 balls)",
                    "bowler": "Gudakesh Motie",
                    "dismissal_mode": "Stumped / caught behind",
                    "tactical_matchup": "Motie tosses one slightly wider outside off."
                }
            ]
        },
        "chase_finish": {
            "overs": "16 to 18.4",
            "finishers": "Sanju Samson (62* off 39 balls, 2 T20 tons at Hyderabad) and Tilak Varma (48* off 28 balls, native home ground hero).",
            "target_achieved": "184/3 in 18.4 Overs. India loses only 3 wickets to complete the chase."
        }
    },
    "differential_player_analysis": {
        "india_differentials": [
            {
                "name": "Mayank Yadav",
                "ownership": "28.5%",
                "role": "Bowler",
                "ceiling": 140,
                "why_wild_card_essential": "Extreme 150kph+ pace on an 80% red-soil bouncy pitch. Dismantles top-order youth (Jewel Andrew) and clean bowls death hitters (Rutherford). 2-3 wickets guaranteed."
            },
            {
                "name": "Nitish Kumar Reddy",
                "ownership": "32.0%",
                "role": "All-Rounder",
                "ceiling": 135,
                "why_wild_card_essential": "Playing at his Sunrisers Hyderabad home IPL venue. Familiar with pitch dynamics; bowls 2-3 middle overs picking Hetmyer/Powell, plus power-hitting if required."
            },
            {
                "name": "Tilak Varma",
                "ownership": "44.0%",
                "role": "Batter (Captaincy Differential)",
                "ceiling": 150,
                "why_wild_card_essential": "Sub-50% ownership for Captaincy. Native Hyderabad boy playing on his childhood wicket. Perfect scenario anchoring and finishing the 2nd innings chase."
            }
        ],
        "west_indies_differentials": [
            {
                "name": "Shamar Joseph",
                "ownership": "36.0%",
                "role": "Bowler",
                "ceiling": 135,
                "why_wild_card_essential": "148 kph express speed counter-weapon. Extracts steep bounce from the red soil to dismiss Abhishek Sharma in the powerplay."
            },
            {
                "name": "Sherfane Rutherford",
                "ownership": "29.0%",
                "role": "Batter",
                "ceiling": 125,
                "why_wild_card_essential": "Death-overs basher who effortlessly clears the short 64m boundaries. Crucial 35+ run cameo when WI loses middle-order wickets."
            },
            {
                "name": "Keemo Paul",
                "ownership": "24.0%",
                "role": "All-Rounder",
                "ceiling": 115,
                "why_wild_card_essential": "Cutter variations that grip in the cracks + late lower-order six hitting."
            },
            {
                "name": "Jewel Andrew",
                "ownership": "15.5%",
                "role": "Wicketkeeper / Batter",
                "ceiling": 110,
                "why_wild_card_essential": "Direct replacement for Pooran/Sampson; ultra-low ownership keeper playing with freedom."
            }
        ]
    }
}

# Load existing gl_report.json
report_path = Path("d:/cricket/gl_report.json")
with open(report_path, "r", encoding="utf-8") as f:
    rep = json.load(f)

rep["mega_contest_430k"]["deep_matchup_analysis"] = matchup_analysis

with open(report_path, "w", encoding="utf-8") as f:
    json.dump(rep, f, indent=2)

print("Updated gl_report.json with deep bowling matchups & wicket falling predictions!")
