"""
STRIKE//OS PRO - Master Fixture Intelligence
"""

MASTER_FIXTURES = {
    "afg_vs_zim_sharjah_odi": {
        "id": "afg_vs_zim_sharjah_odi",
        "aliases": [
            "afg_vs_zim",
            "afg_zim",
            "afg_v_zim",
            "zim_vs_afg",
            "sharjah_odi",
            "today",
            "live"
        ],
        "title": "Afghanistan vs Zimbabwe, 1st ODI",
        "series": "Afghanistan vs Zimbabwe ODI Series 2026",
        "date": "Today, Oct 24, 2026",
        "time": "In-Play • Toss: Zimbabwe Opted to Bat",
        "venue": "Sharjah Cricket Stadium, Sharjah, UAE",
        "countdown": "Match Underway • Lock Passed / Live Tracking Active",
        "format": "ODI",
        "status": "LIVE IN-PLAY • ZIM BATTING 1ST",
        "category": "INTERNATIONAL",
        "archetype": "MINEFIELD_SPIN_CHOKE",
        "par_score": 225,
        "soil": "Dry Red Clay with Tacky Grass Binder (2,086 Pacer Wkts vs 1,215 Spin)",
        "seamMm": "3.8 mm",
        "turnDeg": "2.6°",
        "pacePct": 63,
        "spinPct": 37,
        "spin_pct": "37% Wkts (2.6° Turn • 2,086 Historical Pacer Wickets)",
        "toss_statement": "Toss Update: Zimbabwe won the toss and opted to bat first! Sharjah pitch report: In 255 historical ODIs, 1st innings average is 225 and 2nd innings average is 192. Pacers dominate with 2,086 wickets (63.2%). Afghanistan powerplay pacers (Farooqi, Omarzai, Sami) attack early; Rashid Khan and AM Ghazanfar strangle middle overs.",
        "unspent_shield": "14.0 - 16.5 Cr Unspent",
        "narrative_shield": "100% Sharjah Post-Toss Game Script Aligned",
        "boundaries": {
            "straight": "65m",
            "sqLeg": "58m",
            "midWkt": "62m",
            "thirdMan": "56m",
            "cover": "60m"
        },
        "lineups": [
            {
                "name": "Team 1 • Afghan Seam & Spin Strangle (ZIM <185)",
                "scenario_tag": "AFG_SEAM_SPIN_STRANGLE",
                "captain": "Fazalhaq Farooqi",
                "vice_captain": "Azmatullah Omarzai",
                "unspent_credits": 14.0,
                "uniqueness": 99.98,
                "strategy": "Farooqi (2.99% sel) attacks with new ball swing in the daytime heat. Omarzai, Rashid, and Ghazanfar dismantle Zimbabwe middle order. AFG chases target under 185 with minimal loss.",
                "players": [
                    {"name": "Brendan Taylor", "role": "WK", "credits": 8.0, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "Ibrahim Zadran", "role": "BAT", "credits": 7.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Sediqullah Atal", "role": "BAT", "credits": 7.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Azmatullah Omarzai", "role": "AR", "credits": 8.5, "team": "AFG", "is_c": False, "is_vc": True},
                    {"name": "Sikandar Raza", "role": "AR", "credits": 9.0, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "Wessly Madhevere", "role": "AR", "credits": 6.5, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "Brad Evans", "role": "AR", "credits": 7.5, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "Rashid Khan", "role": "BOWL", "credits": 9.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "AM Ghazanfar", "role": "BOWL", "credits": 7.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Fazalhaq Farooqi", "role": "BOWL", "credits": 8.0, "team": "AFG", "is_c": True, "is_vc": False},
                    {"name": "Blessing Muzarabani", "role": "BOWL", "credits": 8.5, "team": "ZIM", "is_c": False, "is_vc": False}
                ]
            },
            {
                "name": "Team 2 • Raza-Taylor Fightback & Muzarabani 2nd Inns Bounce",
                "scenario_tag": "RAZA_TAYLOR_RESISTANCE",
                "captain": "Sikandar Raza",
                "vice_captain": "Blessing Muzarabani",
                "unspent_credits": 14.0,
                "uniqueness": 99.96,
                "strategy": "Zimbabwe recovers to 220+ behind Raza (c) & Taylor. In 2nd innings under wearing Sharjah pitch, 6ft 8in Muzarabani strikes early against AFG openers. Shahidi and Rahmat Shah anchor AFG response.",
                "players": [
                    {"name": "Brendan Taylor", "role": "WK", "credits": 8.0, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "Ibrahim Zadran", "role": "BAT", "credits": 7.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Sediqullah Atal", "role": "BAT", "credits": 7.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Hashmatullah Shahidi", "role": "BAT", "credits": 9.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Rahmat Shah", "role": "AR", "credits": 8.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Brian Bennett", "role": "AR", "credits": 7.5, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "Sikandar Raza", "role": "AR", "credits": 9.0, "team": "ZIM", "is_c": True, "is_vc": False},
                    {"name": "Brad Evans", "role": "AR", "credits": 7.5, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "AM Ghazanfar", "role": "BOWL", "credits": 7.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Wellington Masakadza", "role": "BOWL", "credits": 7.5, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "Blessing Muzarabani", "role": "BOWL", "credits": 8.5, "team": "ZIM", "is_c": False, "is_vc": True}
                ]
            },
            {
                "name": "Team 3 • Sharjah Pacer Carnage (16.0 Cr Unspent Shield)",
                "scenario_tag": "SHARJAH_PACER_CARNAGE",
                "captain": "Blessing Muzarabani",
                "vice_captain": "Fazalhaq Farooqi",
                "unspent_credits": 16.0,
                "uniqueness": 99.99,
                "strategy": "Direct exploitation of Sharjah 2,086 pacer wickets stat. Stacks frontline pacers from both innings (Muzarabani, Farooqi, Evans, Sami, Omarzai). Budget keeper Tsiga unlocks 16.0 Cr unspent shield for total zero collision.",
                "players": [
                    {"name": "Tafadzwa Tsiga", "role": "WK", "credits": 6.5, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "Ibrahim Zadran", "role": "BAT", "credits": 7.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Sediqullah Atal", "role": "BAT", "credits": 7.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Azmatullah Omarzai", "role": "AR", "credits": 8.5, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Brian Bennett", "role": "AR", "credits": 7.5, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "Brad Evans", "role": "AR", "credits": 7.5, "team": "ZIM", "is_c": False, "is_vc": False},
                    {"name": "Rashid Khan", "role": "BOWL", "credits": 9.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "AM Ghazanfar", "role": "BOWL", "credits": 7.0, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Bilal Sami", "role": "BOWL", "credits": 7.5, "team": "AFG", "is_c": False, "is_vc": False},
                    {"name": "Fazalhaq Farooqi", "role": "BOWL", "credits": 8.0, "team": "AFG", "is_c": False, "is_vc": True},
                    {"name": "Blessing Muzarabani", "role": "BOWL", "credits": 8.5, "team": "ZIM", "is_c": True, "is_vc": False}
                ]
            }
        ],
        "battles": [
            {"batter": "R Gurbaz", "bowler": "B Muzarabani", "runs": 32, "balls": 28, "dism": 2, "sr": 114.3, "adv": "Bowler Strike (Steep Bounce)"},
            {"batter": "I Zadran", "bowler": "B Evans", "runs": 45, "balls": 40, "dism": 1, "sr": 112.5, "adv": "Batter Dominant (Backfoot Punch)"},
            {"batter": "H Shahidi", "bowler": "W Masakadza", "runs": 38, "balls": 44, "dism": 0, "sr": 86.4, "adv": "Batter Advantage (Controls SLA)"},
            {"batter": "S Raza", "bowler": "Rashid Khan", "runs": 28, "balls": 34, "dism": 2, "sr": 82.4, "adv": "Bowler Strike (Googly LBW Threat)"},
            {"batter": "B Taylor", "bowler": "F Farooqi", "runs": 18, "balls": 22, "dism": 1, "sr": 81.8, "adv": "Bowler Strike (Powerplay In-Swinger)"},
            {"batter": "B Bennett", "bowler": "A Omarzai", "runs": 21, "balls": 24, "dism": 1, "sr": 87.5, "adv": "Bowler Strike (Seam Movement)"}
        ],
        "matchups": [
            {
                "batter": "R Gurbaz", "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "B Muzarabani", "bowler_arm": "Right-Arm Fast (RAF 6ft 8in)",
                "speed": "142.5 km/h", "runs": 32, "balls": 28, "dism": 2, "sr": 114.3, "dots": 42.8, "fours": 4, "sixes": 1,
                "venue_factor": "Sharjah pitch bounce tests Gurbaz outside off stump in 2nd innings",
                "adv": "Bowler Advantage (Steep Bounce from Hard Length)"
            },
            {
                "batter": "I Zadran", "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "B Evans", "bowler_arm": "Right-Arm Fast-Medium (RAFM)",
                "speed": "133.0 km/h", "runs": 45, "balls": 40, "dism": 1, "sr": 112.5, "dots": 35.0, "fours": 5, "sixes": 1,
                "venue_factor": "True bounce allows Zadran backfoot punch through covers",
                "adv": "Batter Dominant (ODI Anchor Stability)"
            },
            {
                "batter": "S Raza", "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Rashid Khan", "bowler_arm": "Right-Arm Leg-Spin (LB / Googly)",
                "speed": "94.0 km/h", "runs": 28, "balls": 34, "dism": 2, "sr": 82.4, "dots": 47.0, "fours": 2, "sixes": 1,
                "venue_factor": "Sharjah daytime grip maximizes Rashid quick googly in middle overs",
                "adv": "Bowler Strike (Rashid Leg-Spin Strangle)"
            },
            {
                "batter": "B Taylor", "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "F Farooqi", "bowler_arm": "Left-Arm Fast-Medium (LAFM)",
                "speed": "138.0 km/h", "runs": 18, "balls": 22, "dism": 1, "sr": 81.8, "dots": 50.0, "fours": 2, "sixes": 0,
                "venue_factor": "Powerplay swing with fresh white Kookaburra ball",
                "adv": "Bowler Strike (In-dipper vs RHB)"
            }
        ],
        "handedness_matrix": {
            "afg_rhb": 8, "afg_lhb": 3,
            "zim_rhb": 8, "zim_lhb": 3,
            "analysis": "Balanced left-right pairings. Afghanistan off-spinner M Nabi and mystery spinner Ghazanfar get favorable angles against Zimbabwe left-handers Tafadzwa Tsiga, Ryan Burl, and Wellington Masakadza."
        },
        "venue_player_records": [
            {"player": "Rashid Khan", "team": "AFG", "matches": 16, "wickets": 34, "economy": 4.12, "avg": 14.8},
            {"player": "AM Ghazanfar", "team": "AFG", "matches": 3, "wickets": 9, "economy": 3.80, "avg": 9.2},
            {"player": "Fazalhaq Farooqi", "team": "AFG", "matches": 9, "wickets": 19, "economy": 4.65, "avg": 19.3},
            {"player": "Rahmanullah Gurbaz", "team": "AFG", "matches": 12, "runs": 485, "avg": 44.1, "sr": 92.4},
            {"player": "Ibrahim Zadran", "team": "AFG", "matches": 10, "runs": 420, "avg": 46.7, "sr": 84.1},
            {"player": "Sikandar Raza", "team": "ZIM", "matches": 6, "runs": 210, "wickets": 8, "avg": 35.0, "economy": 4.75}
        ]
    },
    "161190": {
        "id": "161190",
        "aliases": [
            "nz_vs_ind_t20_auckland",
            "nz_vs_ind"
        ],
        "title": "New Zealand vs India, 1st T20I",
        "series": "India Tour of New Zealand 2026",
        "date": "Today, Oct 24, 2026",
        "time": "12:30 PM IST (7:00 PM Local NZDT)",
        "venue": "Eden Park, Auckland, New Zealand",
        "countdown": "Starts in 17h 15m \u2022 Lock Deadline 12:30 PM IST",
        "format": "T20I",
        "status": "UPCOMING",
        "category": "INTERNATIONAL",
        "archetype": "ROAD_HIGHWAY",
        "par_score": 204,
        "soil": "Drop-in Rye Grass & Clay (Short 55m Straight Boundaries)",
        "seamMm": "2.1 mm",
        "turnDeg": "1.4\u00b0",
        "pacePct": 65,
        "spinPct": 35,
        "spin_pct": "35% Wkts (1.4\u00b0 Turn)",
        "toss_statement": "Eden Park drop-in wicket #3: Lightning fast outfield with 55m straight boundaries. Average 1st innings total is 198. Batting second has won 62% of recent T20Is due to short boundaries.",
        "unspent_shield": "13.0 - 17.5 Cr Unspent",
        "narrative_shield": "100% High-Scoring Boundary Aligned",
        "boundaries": {
            "straight": "55m (Short)",
            "sqLeg": "66m",
            "midWkt": "64m",
            "thirdMan": "54m",
            "cover": "62m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 Eden Park Boundary Blitz",
                "scenario_tag": "ROAD_HIGHWAY_SURGE",
                "captain": "Abhishek Sharma",
                "vice_captain": "Glenn Phillips",
                "unspent_credits": 15.5,
                "uniqueness": 99.9,
                "strategy": "Exploits short 55m Eden Park straight boundaries. Stacks boundary clearing openers and death overs hitters.",
                "players": [
                    {
                        "name": "Abhishek Sharma",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Finn Allen",
                        "role": "WK",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Suryakumar Yadav",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Glenn Phillips",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Hardik Pandya",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Rinku Singh",
                        "role": "BAT",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mitchell Santner",
                        "role": "AR",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Arshdeep Singh",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Lockie Ferguson",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Varun Chakravarthy",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Jacob Duffy",
                        "role": "BOWL",
                        "credits": 6.0,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            },
            {
                "name": "Team 2 \u2022 Powerplay Seam Carnage",
                "scenario_tag": "POWERPLAY_SEAM_CRUSH",
                "captain": "Arshdeep Singh",
                "vice_captain": "Lockie Ferguson",
                "unspent_credits": 16.0,
                "uniqueness": 99.8,
                "strategy": "Contrarian hedge anticipating early swing with white kookaburra under Auckland twilight sea breeze.",
                "players": [
                    {
                        "name": "Devon Conway",
                        "role": "WK",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Sanju Samson",
                        "role": "WK",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Daryl Mitchell",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Hardik Pandya",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Shivam Dube",
                        "role": "AR",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Glenn Phillips",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Arshdeep Singh",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Lockie Ferguson",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Harshit Rana",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Ish Sodhi",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Rinku Singh",
                        "role": "BAT",
                        "credits": 6.5,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            },
            {
                "name": "Team 3 \u2022 Middle Overs Spin Strangle",
                "scenario_tag": "SPIN_TURNING_TRAP",
                "captain": "Varun Chakravarthy",
                "vice_captain": "Suryakumar Yadav",
                "unspent_credits": 14.0,
                "uniqueness": 99.7,
                "strategy": "Capitalizes on mystery spin variation forcing mis-timed slogs towards deep square leg boundaries.",
                "players": [
                    {
                        "name": "Suryakumar Yadav",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Abhishek Sharma",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Glenn Phillips",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mitchell Santner",
                        "role": "AR",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Axar Patel",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Varun Chakravarthy",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Ish Sodhi",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Jasprit Bumrah",
                        "role": "BOWL",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Sanju Samson",
                        "role": "WK",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mark Chapman",
                        "role": "BAT",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Jacob Duffy",
                        "role": "BOWL",
                        "credits": 6.0,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            },
            {
                "name": "Team 4 \u2022 220+ Chase Engine",
                "scenario_tag": "SECOND_INNS_CHASE_DOMINANCE",
                "captain": "Hardik Pandya",
                "vice_captain": "Abhishek Sharma",
                "unspent_credits": 15.0,
                "uniqueness": 99.9,
                "strategy": "Simulates 2nd innings dew and batting paradise where chasing team hits 14+ sixes.",
                "players": [
                    {
                        "name": "Abhishek Sharma",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Finn Allen",
                        "role": "WK",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Suryakumar Yadav",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Hardik Pandya",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Glenn Phillips",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Rinku Singh",
                        "role": "BAT",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Tim Seifert",
                        "role": "WK",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Arshdeep Singh",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Lockie Ferguson",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Ravi Bishnoi",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Ben Sears",
                        "role": "BOWL",
                        "credits": 6.0,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Abhishek Sharma",
                "bowler": "Lockie Ferguson",
                "runs": 38,
                "balls": 21,
                "dism": 1,
                "sr": 180.9,
                "adv": "Batter Dominant"
            },
            {
                "batter": "Suryakumar Yadav",
                "bowler": "Mitchell Santner",
                "runs": 52,
                "balls": 34,
                "dism": 0,
                "sr": 152.9,
                "adv": "Batter Advantage"
            },
            {
                "batter": "Finn Allen",
                "bowler": "Arshdeep Singh",
                "runs": 22,
                "balls": 17,
                "dism": 2,
                "sr": 129.4,
                "adv": "Bowler Strike"
            },
            {
                "batter": "Glenn Phillips",
                "bowler": "Varun Chakravarthy",
                "runs": 19,
                "balls": 18,
                "dism": 2,
                "sr": 105.5,
                "adv": "Bowler Advantage"
            },
            {
                "batter": "Hardik Pandya",
                "bowler": "Jacob Duffy",
                "runs": 44,
                "balls": 22,
                "dism": 0,
                "sr": 200.0,
                "adv": "Batter Dominant"
            }
        ],
        "matchups": [
            {
                "batter": "Abhishek Sharma",
                "batter_hand": "Left-Hand Bat (LHB)",
                "bowler": "Lockie Ferguson",
                "bowler_arm": "Right-Arm Fast (RAF)",
                "speed": "145.8 km/h",
                "runs": 38,
                "balls": 21,
                "dism": 1,
                "sr": 180.9,
                "dots": 33.3,
                "fours": 4,
                "sixes": 3,
                "venue_factor": "Eden Park 55m straight boundary increases boundary % by +35%",
                "adv": "Batter Dominant (+180 SR vs Express Pace)"
            },
            {
                "batter": "Abhishek Sharma",
                "batter_hand": "Left-Hand Bat (LHB)",
                "bowler": "Mitchell Santner",
                "bowler_arm": "Slow Left-Arm Orthodox (SLA)",
                "speed": "91.2 km/h",
                "runs": 29,
                "balls": 18,
                "dism": 0,
                "sr": 161.1,
                "dots": 27.8,
                "fours": 3,
                "sixes": 2,
                "venue_factor": "Ball turns into LHB hitting arc over midwicket (64m)",
                "adv": "Batter Dominant (Favorable SLA Angle)"
            },
            {
                "batter": "Suryakumar Yadav",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Lockie Ferguson",
                "bowler_arm": "Right-Arm Fast (RAF)",
                "speed": "146.2 km/h",
                "runs": 44,
                "balls": 26,
                "dism": 1,
                "sr": 169.2,
                "dots": 30.8,
                "fours": 5,
                "sixes": 2,
                "venue_factor": "SKY uses express pace for fine-leg scoops over 54m boundary",
                "adv": "Batter Advantage (360\u00b0 Ramp vs Pace)"
            },
            {
                "batter": "Suryakumar Yadav",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Mitchell Santner",
                "bowler_arm": "Slow Left-Arm Orthodox (SLA)",
                "speed": "90.5 km/h",
                "runs": 52,
                "balls": 34,
                "dism": 0,
                "sr": 152.9,
                "dots": 26.5,
                "fours": 6,
                "sixes": 2,
                "venue_factor": "Inside-out lofted drives over extra cover (62m)",
                "adv": "Batter Advantage (Zero Dismissals)"
            },
            {
                "batter": "Finn Allen",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Arshdeep Singh",
                "bowler_arm": "Left-Arm Fast-Medium (LAP)",
                "speed": "137.5 km/h",
                "runs": 22,
                "balls": 17,
                "dism": 2,
                "sr": 129.4,
                "dots": 47.1,
                "fours": 2,
                "sixes": 1,
                "venue_factor": "Left-arm swing back into RHB front pad causes early LBW risk",
                "adv": "Bowler Strike Hazard (2 Dismissals in PP)"
            },
            {
                "batter": "Devon Conway",
                "batter_hand": "Left-Hand Bat (LHB)",
                "bowler": "Varun Chakravarthy",
                "bowler_arm": "Right-Arm Mystery Spin (OB/LWS)",
                "speed": "94.8 km/h",
                "runs": 18,
                "balls": 19,
                "dism": 2,
                "sr": 94.7,
                "dots": 52.6,
                "fours": 1,
                "sixes": 0,
                "venue_factor": "Mystery carrom ball spinning away from LHB",
                "adv": "Bowler Trap (Sub-100 SR & 2 Dismissals)"
            },
            {
                "batter": "Glenn Phillips",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Varun Chakravarthy",
                "bowler_arm": "Right-Arm Mystery Spin (OB/LWS)",
                "speed": "93.4 km/h",
                "runs": 19,
                "balls": 18,
                "dism": 2,
                "sr": 105.5,
                "dots": 44.4,
                "fours": 2,
                "sixes": 0,
                "venue_factor": "Googly induces false stroke toward deep square leg",
                "adv": "Bowler Advantage (Spin Strangle)"
            },
            {
                "batter": "Hardik Pandya",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Jacob Duffy",
                "bowler_arm": "Right-Arm Fast-Medium (RAF)",
                "speed": "134.2 km/h",
                "runs": 44,
                "balls": 22,
                "dism": 0,
                "sr": 200.0,
                "dots": 22.7,
                "fours": 3,
                "sixes": 4,
                "venue_factor": "Clears straight 55m boundary with ease in death overs",
                "adv": "Batter Dominant (Death Overs Carnage 200 SR)"
            }
        ],
        "handedness_matrix": [
            {
                "batter": "Abhishek Sharma",
                "hand": "LHB",
                "vs_rap": "Avg 34.2 | SR 168.4",
                "vs_lap": "Avg 26.5 | SR 142.1",
                "vs_ob": "Avg 41.0 | SR 174.5",
                "vs_lb": "Avg 31.8 | SR 155.0",
                "vs_sla": "Avg 46.2 | SR 182.0",
                "weakness_speed": "Short-pitched bouncer > 142 km/h from LAP",
                "venue_fit": "Elite (Short straight boundary favors pull/loft)"
            },
            {
                "batter": "Suryakumar Yadav",
                "hand": "RHB",
                "vs_rap": "Avg 42.8 | SR 176.2",
                "vs_lap": "Avg 38.5 | SR 165.0",
                "vs_ob": "Avg 35.0 | SR 148.0",
                "vs_lb": "Avg 44.2 | SR 162.5",
                "vs_sla": "Avg 48.0 | SR 158.4",
                "weakness_speed": "Hard length outside off > 144 km/h",
                "venue_fit": "10/10 (Square boundaries & fine ramps at Eden Park)"
            },
            {
                "batter": "Finn Allen",
                "hand": "RHB",
                "vs_rap": "Avg 28.4 | SR 162.0",
                "vs_lap": "Avg 19.2 | SR 131.5",
                "vs_ob": "Avg 32.0 | SR 154.0",
                "vs_lb": "Avg 22.5 | SR 128.0",
                "vs_sla": "Avg 36.5 | SR 166.0",
                "weakness_speed": "In-swinging fuller ball 135-138 km/h (Arshdeep angle)",
                "venue_fit": "High Ceiling / High Variance"
            },
            {
                "batter": "Devon Conway",
                "hand": "LHB",
                "vs_rap": "Avg 39.5 | SR 138.0",
                "vs_lap": "Avg 44.0 | SR 142.5",
                "vs_ob": "Avg 31.2 | SR 124.0",
                "vs_lb": "Avg 36.0 | SR 135.0",
                "vs_sla": "Avg 42.0 | SR 130.0",
                "weakness_speed": "Mystery carrom/googly spinning away from LHB",
                "venue_fit": "Anchor (High floor at Eden Park)"
            },
            {
                "batter": "Glenn Phillips",
                "hand": "RHB",
                "vs_rap": "Avg 35.0 | SR 156.0",
                "vs_lap": "Avg 32.5 | SR 148.0",
                "vs_ob": "Avg 38.0 | SR 162.0",
                "vs_lb": "Avg 28.5 | SR 134.0",
                "vs_sla": "Avg 41.5 | SR 170.0",
                "weakness_speed": "Quick slider/flipper onto stumps 98 km/h",
                "venue_fit": "Strong boundary clearer over midwicket"
            },
            {
                "batter": "Hardik Pandya",
                "hand": "RHB",
                "vs_rap": "Avg 33.5 | SR 162.4",
                "vs_lap": "Avg 29.0 | SR 145.0",
                "vs_ob": "Avg 40.5 | SR 168.0",
                "vs_lb": "Avg 36.2 | SR 152.0",
                "vs_sla": "Avg 45.0 | SR 175.0",
                "weakness_speed": "Wide yorkers outside off > 140 km/h",
                "venue_fit": "Death overs powerhouse (Straight ground hit)"
            }
        ],
        "venue_player_records": [
            {
                "player": "Suryakumar Yadav",
                "team": "IND",
                "role": "BAT",
                "hand": "RHB",
                "matches": 4,
                "runs_wkts": "184 runs",
                "avg": "61.3",
                "sr_econ": "182.2 SR",
                "fantasy_avg": "78.5 pts",
                "badge": "Venue Master"
            },
            {
                "player": "Abhishek Sharma",
                "team": "IND",
                "role": "BAT",
                "hand": "LHB",
                "matches": 2,
                "runs_wkts": "92 runs",
                "avg": "46.0",
                "sr_econ": "191.7 SR",
                "fantasy_avg": "68.0 pts",
                "badge": "Boundary Surge"
            },
            {
                "player": "Glenn Phillips",
                "team": "NZ",
                "role": "AR",
                "hand": "RHB / OB",
                "matches": 9,
                "runs_wkts": "298 runs, 4 wkts",
                "avg": "37.2",
                "sr_econ": "154.4 SR",
                "fantasy_avg": "64.2 pts",
                "badge": "Home Dominance"
            },
            {
                "player": "Finn Allen",
                "team": "NZ",
                "role": "WK",
                "hand": "RHB",
                "matches": 6,
                "runs_wkts": "212 runs",
                "avg": "35.3",
                "sr_econ": "172.4 SR",
                "fantasy_avg": "56.0 pts",
                "badge": "Powerplay Risk"
            },
            {
                "player": "Arshdeep Singh",
                "team": "IND",
                "role": "BOWL",
                "hand": "LAP (138 km/h)",
                "matches": 3,
                "runs_wkts": "7 wickets",
                "avg": "14.2",
                "sr_econ": "7.40 Econ",
                "fantasy_avg": "62.0 pts",
                "badge": "Powerplay Swing"
            },
            {
                "player": "Lockie Ferguson",
                "team": "NZ",
                "role": "BOWL",
                "hand": "RAF (148 km/h)",
                "matches": 8,
                "runs_wkts": "14 wickets",
                "avg": "17.8",
                "sr_econ": "7.85 Econ",
                "fantasy_avg": "58.5 pts",
                "badge": "Express Pace"
            },
            {
                "player": "Varun Chakravarthy",
                "team": "IND",
                "role": "BOWL",
                "hand": "Mystery Spin (95 km/h)",
                "matches": 2,
                "runs_wkts": "5 wickets",
                "avg": "11.4",
                "sr_econ": "6.20 Econ",
                "fantasy_avg": "65.0 pts",
                "badge": "Spin Strangle"
            },
            {
                "player": "Hardik Pandya",
                "team": "IND",
                "role": "AR",
                "hand": "RHB / RAF (138 km/h)",
                "matches": 4,
                "runs_wkts": "115 runs, 3 wkts",
                "avg": "38.3",
                "sr_econ": "164.3 SR",
                "fantasy_avg": "72.0 pts",
                "badge": "Dual Equity"
            }
        ]
    },
    "afg_vs_ban_odi_sharjah": {
        "id": "afg_vs_ban_odi_sharjah",
        "aliases": [
            "172681",
            "afg_ban"
        ],
        "title": "Afghanistan vs Bangladesh, 3rd ODI",
        "series": "Tri-Nation Series in UAE 2026",
        "date": "Today, Oct 24, 2026",
        "time": "1:30 PM IST (8:00 AM GMT)",
        "venue": "Sharjah Cricket Stadium, Sharjah, UAE",
        "countdown": "Toss in 25 mins \u2022 Lock Deadline 1:30 PM IST",
        "format": "ODI",
        "status": "LIVE & SCHEDULED",
        "category": "INTERNATIONAL",
        "archetype": "SPIN_CHOKE_MINEFIELD",
        "par_score": 242,
        "soil": "Cracked Dry Clay (High Dust & Abrasive Surface)",
        "seamMm": "2.8 mm",
        "turnDeg": "3.8\u00b0",
        "pacePct": 42,
        "spinPct": 58,
        "spin_pct": "58% Wkts (3.8\u00b0 Turn)",
        "toss_statement": "Sharjah dry pitch report: Surface is black soil with prominent crust cracks. Spin grip measured at 3.8 degrees. Hashmatullah: 'Dry wicket, 240 is winning total here. Rashid and Ghazanfar will dominate 2nd innings.'",
        "unspent_shield": "12.5 - 16.5 Cr Unspent",
        "narrative_shield": "100% Spin Grip Aligned",
        "boundaries": {
            "straight": "62m",
            "sqLeg": "58m",
            "midWkt": "62m",
            "thirdMan": "56m",
            "cover": "60m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 Spin Choke & Top-3 Fade",
                "scenario_tag": "SPIN_CHOKE_MINEFIELD",
                "captain": "Rashid Khan",
                "vice_captain": "Rahmanullah Gurbaz",
                "unspent_credits": 15.5,
                "uniqueness": 99.8,
                "strategy": "Fades Bangladesh top 3 against Rashid Khan and AM Ghazanfar. Banks on Gurbaz powerplay assault and AFG middle order.",
                "players": [
                    {
                        "name": "Rahmanullah Gurbaz",
                        "role": "WK",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Sediqullah Atal",
                        "role": "BAT",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Towhid Hridoy",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Najmul Hossain Shanto",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Azmatullah Omarzai",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mehidy Hasan Miraz",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Rashid Khan",
                        "role": "BOWL",
                        "credits": 9.0,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "AM Ghazanfar",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Fazalhaq Farooqi",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mustafizur Rahman",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Nahid Rana",
                        "role": "BOWL",
                        "credits": 6.5,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            },
            {
                "name": "Team 2 \u2022 Bangladesh Reversal & Miraz Anchor",
                "scenario_tag": "BAN_REVERSAL_SURGE",
                "captain": "Mehidy Hasan Miraz",
                "vice_captain": "Mustafizur Rahman",
                "unspent_credits": 16.0,
                "uniqueness": 99.9,
                "strategy": "Contrarian script backing Bangladesh spinners and cutters on Sharjah's two-paced afternoon pitch.",
                "players": [
                    {
                        "name": "Jaker Ali",
                        "role": "WK",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Towhid Hridoy",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Soumya Sarkar",
                        "role": "BAT",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Hashmatullah Shahidi",
                        "role": "BAT",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mehidy Hasan Miraz",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Mohammad Nabi",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Azmatullah Omarzai",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mustafizur Rahman",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Taskin Ahmed",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Nasum Ahmed",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Nangeyalia Kharote",
                        "role": "BOWL",
                        "credits": 6.5,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            },
            {
                "name": "Team 3 \u2022 Low-Scoring Bowlers Carnage",
                "scenario_tag": "DUAL_COLLAPSE_DEFENSE",
                "captain": "Fazalhaq Farooqi",
                "vice_captain": "AM Ghazanfar",
                "unspent_credits": 17.0,
                "uniqueness": 99.9,
                "strategy": "Anticipates sub-200 score where both top orders fail and bowlers accumulate 16+ wickets.",
                "players": [
                    {
                        "name": "Rahmanullah Gurbaz",
                        "role": "WK",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mahmudullah",
                        "role": "BAT",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Azmatullah Omarzai",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mehidy Hasan Miraz",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Rashid Khan",
                        "role": "BOWL",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Fazalhaq Farooqi",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "AM Ghazanfar",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Mustafizur Rahman",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Shoriful Islam",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Noor Ahmad",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Rishad Hossain",
                        "role": "BOWL",
                        "credits": 6.5,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            },
            {
                "name": "Team 4 \u2022 Omarzai All-Round Dominance",
                "scenario_tag": "ALL_ROUNDER_MAX_CEILING",
                "captain": "Azmatullah Omarzai",
                "vice_captain": "Rashid Khan",
                "unspent_credits": 14.5,
                "uniqueness": 99.8,
                "strategy": "Omarzai bowls 10 death overs and bats at #5 for high ceiling floor fantasy output.",
                "players": [
                    {
                        "name": "Rahmanullah Gurbaz",
                        "role": "WK",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Towhid Hridoy",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Rahmat Shah",
                        "role": "BAT",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Azmatullah Omarzai",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Mehidy Hasan Miraz",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Rashid Khan",
                        "role": "BOWL",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "AM Ghazanfar",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Fazalhaq Farooqi",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Taskin Ahmed",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mustafizur Rahman",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Tanzeem Hasan Sakib",
                        "role": "BOWL",
                        "credits": 6.5,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Towhid Hridoy",
                "bowler": "Rashid Khan",
                "runs": 28,
                "balls": 34,
                "dism": 2,
                "sr": 82.4,
                "adv": "Bowler Dominant"
            },
            {
                "batter": "Najmul Hossain Shanto",
                "bowler": "Fazalhaq Farooqi",
                "runs": 31,
                "balls": 39,
                "dism": 3,
                "sr": 79.5,
                "adv": "Bowler Dominant"
            },
            {
                "batter": "Rahmanullah Gurbaz",
                "bowler": "Mustafizur Rahman",
                "runs": 45,
                "balls": 32,
                "dism": 1,
                "sr": 140.6,
                "adv": "Batter Advantage"
            },
            {
                "batter": "Hashmatullah Shahidi",
                "bowler": "Mehidy Hasan Miraz",
                "runs": 64,
                "balls": 78,
                "dism": 1,
                "sr": 82.1,
                "adv": "Neutral Anchor"
            },
            {
                "batter": "Azmatullah Omarzai",
                "bowler": "Taskin Ahmed",
                "runs": 41,
                "balls": 26,
                "dism": 0,
                "sr": 157.7,
                "adv": "Batter Dominant"
            }
        ],
        "matchups": [
            {
                "batter": "Towhid Hridoy",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Rashid Khan",
                "bowler_arm": "Right-Arm Legbreak (LB)",
                "speed": "96.4 km/h",
                "runs": 28,
                "balls": 34,
                "dism": 2,
                "sr": 82.4,
                "dots": 55.8,
                "fours": 2,
                "sixes": 0,
                "venue_factor": "Sharjah dust & cracks provide 3.8\u00b0 turn into RHB pad",
                "adv": "Bowler Dominant (LBW & Clean Bowled Risk)"
            },
            {
                "batter": "Najmul Hossain Shanto",
                "batter_hand": "Left-Hand Bat (LHB)",
                "bowler": "Fazalhaq Farooqi",
                "bowler_arm": "Left-Arm Fast-Medium (LAP)",
                "speed": "136.2 km/h",
                "runs": 31,
                "balls": 39,
                "dism": 3,
                "sr": 79.5,
                "dots": 58.9,
                "fours": 3,
                "sixes": 0,
                "venue_factor": "Farooqi late outswing to LHB induces outside edge to slips",
                "adv": "Bowler Trap (3 Dismissals in Powerplay)"
            },
            {
                "batter": "Rahmanullah Gurbaz",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Mustafizur Rahman",
                "bowler_arm": "Left-Arm Fast-Medium Cutters (LAP)",
                "speed": "128.5 km/h",
                "runs": 45,
                "balls": 32,
                "dism": 1,
                "sr": 140.6,
                "dots": 37.5,
                "fours": 5,
                "sixes": 2,
                "venue_factor": "Sharjah small square boundaries allow aerial pull shots",
                "adv": "Batter Advantage (Attacks Mustafizur Angle)"
            },
            {
                "batter": "Hashmatullah Shahidi",
                "batter_hand": "Left-Hand Bat (LHB)",
                "bowler": "Mehidy Hasan Miraz",
                "bowler_arm": "Right-Arm Offbreak (OB)",
                "speed": "88.6 km/h",
                "runs": 64,
                "balls": 78,
                "dism": 1,
                "sr": 82.1,
                "dots": 48.7,
                "fours": 4,
                "sixes": 0,
                "venue_factor": "Slow turn into LHB hip, worked for singles into midwicket",
                "adv": "Neutral Anchor (Low Wicket Hazard)"
            },
            {
                "batter": "Azmatullah Omarzai",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Taskin Ahmed",
                "bowler_arm": "Right-Arm Fast (RAF)",
                "speed": "142.1 km/h",
                "runs": 41,
                "balls": 26,
                "dism": 0,
                "sr": 157.7,
                "dots": 34.6,
                "fours": 4,
                "sixes": 2,
                "venue_factor": "True bounce in evening dew clears straight 62m boundary",
                "adv": "Batter Dominant (+155 SR vs High Pace)"
            },
            {
                "batter": "Mahmudullah",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "AM Ghazanfar",
                "bowler_arm": "Right-Arm Mystery Offbreak (OB)",
                "speed": "93.0 km/h",
                "runs": 16,
                "balls": 22,
                "dism": 2,
                "sr": 72.7,
                "dots": 63.6,
                "fours": 1,
                "sixes": 0,
                "venue_factor": "Sharp carrom ball carves through middle gate",
                "adv": "Bowler Trap (Sub-75 SR & High Dot Pressure)"
            }
        ],
        "handedness_matrix": [
            {
                "batter": "Rahmanullah Gurbaz",
                "hand": "RHB",
                "vs_rap": "Avg 38.5 | SR 138.0",
                "vs_lap": "Avg 34.0 | SR 142.0",
                "vs_ob": "Avg 44.5 | SR 152.0",
                "vs_lb": "Avg 29.0 | SR 122.0",
                "vs_sla": "Avg 36.0 | SR 135.0",
                "weakness_speed": "Sharp legbreak pitching on leg and hitting off",
                "venue_fit": "9.5/10 (Powerplay boundary ramp)"
            },
            {
                "batter": "Towhid Hridoy",
                "hand": "RHB",
                "vs_rap": "Avg 36.0 | SR 128.5",
                "vs_lap": "Avg 32.0 | SR 118.0",
                "vs_ob": "Avg 39.0 | SR 134.0",
                "vs_lb": "Avg 22.0 | SR 98.0",
                "vs_sla": "Avg 40.0 | SR 130.0",
                "weakness_speed": "Rashid Khan quick googly 96 km/h",
                "venue_fit": "Vulnerable to spin collapse"
            },
            {
                "batter": "Najmul Hossain Shanto",
                "hand": "LHB",
                "vs_rap": "Avg 33.5 | SR 115.0",
                "vs_lap": "Avg 24.0 | SR 96.0",
                "vs_ob": "Avg 42.0 | SR 128.0",
                "vs_lb": "Avg 35.0 | SR 112.0",
                "vs_sla": "Avg 38.0 | SR 120.0",
                "weakness_speed": "Late outswing from left-arm angle 135 km/h",
                "venue_fit": "Early wicket hazard vs Farooqi"
            },
            {
                "batter": "Azmatullah Omarzai",
                "hand": "RHB",
                "vs_rap": "Avg 44.0 | SR 148.0",
                "vs_lap": "Avg 39.0 | SR 136.0",
                "vs_ob": "Avg 36.5 | SR 130.0",
                "vs_lb": "Avg 38.0 | SR 142.0",
                "vs_sla": "Avg 46.0 | SR 155.0",
                "weakness_speed": "Slower wide yorker 118 km/h",
                "venue_fit": "Top 1% ceiling floor ratio"
            }
        ],
        "venue_player_records": [
            {
                "player": "Rashid Khan",
                "team": "AFG",
                "role": "BOWL",
                "hand": "Right-Arm Legbreak (96 km/h)",
                "matches": 11,
                "runs_wkts": "26 wickets",
                "avg": "13.8",
                "sr_econ": "3.85 Econ",
                "fantasy_avg": "86.0 pts",
                "badge": "Sharjah King"
            },
            {
                "player": "Rahmanullah Gurbaz",
                "team": "AFG",
                "role": "WK",
                "hand": "RHB",
                "matches": 9,
                "runs_wkts": "382 runs",
                "avg": "42.4",
                "sr_econ": "138.5 SR",
                "fantasy_avg": "74.5 pts",
                "badge": "Powerplay Master"
            },
            {
                "player": "Fazalhaq Farooqi",
                "team": "AFG",
                "role": "BOWL",
                "hand": "LAP (136 km/h)",
                "matches": 7,
                "runs_wkts": "16 wickets",
                "avg": "16.1",
                "sr_econ": "4.45 Econ",
                "fantasy_avg": "68.0 pts",
                "badge": "Early Swing"
            },
            {
                "player": "AM Ghazanfar",
                "team": "AFG",
                "role": "BOWL",
                "hand": "Mystery Spin (93 km/h)",
                "matches": 4,
                "runs_wkts": "11 wickets",
                "avg": "10.2",
                "sr_econ": "3.60 Econ",
                "fantasy_avg": "72.0 pts",
                "badge": "Mystery Trap"
            },
            {
                "player": "Mehidy Hasan Miraz",
                "team": "BAN",
                "role": "AR",
                "hand": "RHB / Offbreak (89 km/h)",
                "matches": 8,
                "runs_wkts": "184 runs, 12 wkts",
                "avg": "26.2",
                "sr_econ": "4.20 Econ",
                "fantasy_avg": "64.0 pts",
                "badge": "Dual Equity"
            },
            {
                "player": "Mustafizur Rahman",
                "team": "BAN",
                "role": "BOWL",
                "hand": "LAP Cutters (128 km/h)",
                "matches": 9,
                "runs_wkts": "17 wickets",
                "avg": "19.4",
                "sr_econ": "4.75 Econ",
                "fantasy_avg": "59.0 pts",
                "badge": "Death Cutters"
            }
        ]
    },
    "147931": {
        "id": "147931",
        "aliases": [
            "rsa_vs_aus_test_durban"
        ],
        "title": "South Africa vs Australia, 2nd Test",
        "series": "Australia Tour of South Africa 2026",
        "date": "Today, Oct 24, 2026",
        "time": "1:30 PM IST (10:00 AM Local SAST)",
        "venue": "Kingsmead, Durban, South Africa",
        "countdown": "Live Day 2 \u2022 Sea Breeze Swing Active",
        "format": "TEST",
        "status": "LIVE NOW",
        "category": "INTERNATIONAL",
        "archetype": "GREEN_SEAM_SWING",
        "par_score": 268,
        "soil": "Coastal Sea Breeze Turf (Lush Green Grass Deck)",
        "seamMm": "4.2 mm",
        "turnDeg": "2.1\u00b0",
        "pacePct": 78,
        "spinPct": 22,
        "spin_pct": "22% Wkts (High Seam 4.2mm)",
        "toss_statement": "Kingsmead Day 2 Pitch: 8mm grass covering with high humidity and afternoon sea breeze. Bowlers receiving massive late swing and steep bounce.",
        "unspent_shield": "14.0 - 18.0 Cr Unspent",
        "narrative_shield": "100% Pace & Seam Aligned",
        "boundaries": {
            "straight": "74m",
            "sqLeg": "68m",
            "midWkt": "71m",
            "thirdMan": "65m",
            "cover": "69m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 Kingsmead Seam Carnage",
                "scenario_tag": "PACE_DOMINANCE_SURGE",
                "captain": "Kagiso Rabada",
                "vice_captain": "Pat Cummins",
                "unspent_credits": 16.5,
                "uniqueness": 99.9,
                "strategy": "Stacks elite pace spearheads exploiting 4.2mm seam movement under overcast Durban conditions.",
                "players": [
                    {
                        "name": "Alex Carey",
                        "role": "WK",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Steve Smith",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Aiden Markram",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Temba Bavuma",
                        "role": "BAT",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Marco Jansen",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Cameron Green",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Kagiso Rabada",
                        "role": "BOWL",
                        "credits": 9.0,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Pat Cummins",
                        "role": "BOWL",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Mitchell Starc",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Gerald Coetzee",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Nathan Lyon",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Steve Smith",
                "bowler": "Kagiso Rabada",
                "runs": 114,
                "balls": 182,
                "dism": 4,
                "sr": 62.6,
                "adv": "Bowler Strike"
            },
            {
                "batter": "Aiden Markram",
                "bowler": "Mitchell Starc",
                "runs": 88,
                "balls": 112,
                "dism": 3,
                "sr": 78.5,
                "adv": "Pace Trap"
            }
        ],
        "matchups": [
            {
                "batter": "Steve Smith",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Kagiso Rabada",
                "bowler_arm": "Right-Arm Fast (RAF)",
                "speed": "146.4 km/h",
                "runs": 114,
                "balls": 182,
                "dism": 4,
                "sr": 62.6,
                "dots": 68.2,
                "fours": 14,
                "sixes": 1,
                "venue_factor": "Kingsmead 4.2mm seam movement attacks off-stump channel",
                "adv": "Bowler Hazard (4 Test Dismissals)"
            },
            {
                "batter": "Travis Head",
                "batter_hand": "Left-Hand Bat (LHB)",
                "bowler": "Kagiso Rabada",
                "bowler_arm": "Right-Arm Fast (RAF)",
                "speed": "147.1 km/h",
                "runs": 78,
                "balls": 94,
                "dism": 2,
                "sr": 83.0,
                "dots": 54.3,
                "fours": 11,
                "sixes": 2,
                "venue_factor": "Aggressive counter-punching over point & cover boundary",
                "adv": "High Risk / High Reward (+83 SR vs Pace)"
            },
            {
                "batter": "Aiden Markram",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Mitchell Starc",
                "bowler_arm": "Left-Arm Fast (LAP)",
                "speed": "145.2 km/h",
                "runs": 88,
                "balls": 112,
                "dism": 3,
                "sr": 78.5,
                "dots": 61.2,
                "fours": 12,
                "sixes": 1,
                "venue_factor": "Starc left-arm in-swing with new red ball breaches defense",
                "adv": "Bowler Trap (3 Dismissals in First 10 Overs)"
            },
            {
                "batter": "Temba Bavuma",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Pat Cummins",
                "bowler_arm": "Right-Arm Fast (RAF)",
                "speed": "142.8 km/h",
                "runs": 96,
                "balls": 174,
                "dism": 2,
                "sr": 55.2,
                "dots": 69.5,
                "fours": 9,
                "sixes": 0,
                "venue_factor": "Cummins nagging back-of-length tests Bavuma patience",
                "adv": "Even Grinding Contest (Low Boundary Equity)"
            },
            {
                "batter": "Marnus Labuschagne",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Gerald Coetzee",
                "bowler_arm": "Right-Arm Express Fast (RAF)",
                "speed": "148.5 km/h",
                "runs": 48,
                "balls": 62,
                "dism": 1,
                "sr": 77.4,
                "dots": 58.0,
                "fours": 6,
                "sixes": 1,
                "venue_factor": "Express short balls directed at body with steep Durban bounce",
                "adv": "Competitive Clash (+148 km/h Bouncer Threat)"
            },
            {
                "batter": "Alex Carey",
                "batter_hand": "Left-Hand Bat (LHB)",
                "bowler": "Marco Jansen",
                "bowler_arm": "Left-Arm Fast (LAP)",
                "speed": "141.6 km/h",
                "runs": 42,
                "balls": 58,
                "dism": 2,
                "sr": 72.4,
                "dots": 60.3,
                "fours": 5,
                "sixes": 0,
                "venue_factor": "2.06m tall Jansen extracts awkward bounce angling across LHB",
                "adv": "Bowler Advantage (Steep Bounce Edge)"
            }
        ],
        "handedness_matrix": [
            {
                "batter": "Steve Smith",
                "hand": "RHB",
                "vs_rap": "Avg 58.4 | SR 54.2",
                "vs_lap": "Avg 46.0 | SR 51.5",
                "vs_ob": "Avg 62.0 | SR 58.0",
                "vs_lb": "Avg 51.2 | SR 56.4",
                "vs_sla": "Avg 49.5 | SR 52.0",
                "weakness_speed": "Nipping seam back into pads > 144 km/h",
                "venue_fit": "Test Wall (Grinds through seam movement)"
            },
            {
                "batter": "Travis Head",
                "hand": "LHB",
                "vs_rap": "Avg 42.0 | SR 82.5",
                "vs_lap": "Avg 31.5 | SR 74.0",
                "vs_ob": "Avg 35.0 | SR 88.0",
                "vs_lb": "Avg 44.0 | SR 85.0",
                "vs_sla": "Avg 48.2 | SR 92.0",
                "weakness_speed": "Short ball targeted at ribcage > 145 km/h",
                "venue_fit": "Ceiling Maximizer (Attacks square boundaries)"
            },
            {
                "batter": "Aiden Markram",
                "hand": "RHB",
                "vs_rap": "Avg 41.5 | SR 64.0",
                "vs_lap": "Avg 28.0 | SR 58.2",
                "vs_ob": "Avg 45.0 | SR 68.0",
                "vs_lb": "Avg 38.0 | SR 60.0",
                "vs_sla": "Avg 44.0 | SR 65.0",
                "weakness_speed": "Late swinging ball across right-hander 142 km/h",
                "venue_fit": "Home Condition Specialist"
            },
            {
                "batter": "Temba Bavuma",
                "hand": "RHB",
                "vs_rap": "Avg 38.2 | SR 48.5",
                "vs_lap": "Avg 40.0 | SR 52.0",
                "vs_ob": "Avg 36.0 | SR 50.0",
                "vs_lb": "Avg 42.0 | SR 54.0",
                "vs_sla": "Avg 45.0 | SR 55.0",
                "weakness_speed": "Fourth stump channel nibblers",
                "venue_fit": "Anchor (Durban Middle Order Stabilizer)"
            },
            {
                "batter": "Alex Carey",
                "hand": "LHB",
                "vs_rap": "Avg 34.0 | SR 62.0",
                "vs_lap": "Avg 26.5 | SR 55.0",
                "vs_ob": "Avg 39.0 | SR 70.0",
                "vs_lb": "Avg 32.0 | SR 64.0",
                "vs_sla": "Avg 41.0 | SR 75.0",
                "weakness_speed": "Extra bounce from left-arm angle > 140 km/h",
                "venue_fit": "Counter-attacking lower order"
            }
        ],
        "venue_player_records": [
            {
                "player": "Kagiso Rabada",
                "team": "RSA",
                "role": "BOWL",
                "hand": "Right-Arm Fast (146 km/h)",
                "matches": 6,
                "runs_wkts": "32 wickets",
                "avg": "18.4",
                "sr_econ": "3.10 Econ",
                "fantasy_avg": "94.0 pts",
                "badge": "Kingsmead Strike King"
            },
            {
                "player": "Steve Smith",
                "team": "AUS",
                "role": "BAT",
                "hand": "RHB",
                "matches": 3,
                "runs_wkts": "264 runs",
                "avg": "66.0",
                "sr_econ": "55.8 SR",
                "fantasy_avg": "82.5 pts",
                "badge": "Test Master"
            },
            {
                "player": "Mitchell Starc",
                "team": "AUS",
                "role": "BOWL",
                "hand": "LAP (145 km/h)",
                "matches": 4,
                "runs_wkts": "19 wickets",
                "avg": "21.2",
                "sr_econ": "3.45 Econ",
                "fantasy_avg": "76.0 pts",
                "badge": "New Ball Swing"
            },
            {
                "player": "Pat Cummins",
                "team": "AUS",
                "role": "BOWL",
                "hand": "RAF (143 km/h)",
                "matches": 4,
                "runs_wkts": "18 wickets",
                "avg": "22.5",
                "sr_econ": "2.85 Econ",
                "fantasy_avg": "74.0 pts",
                "badge": "Relentless Line"
            },
            {
                "player": "Aiden Markram",
                "team": "RSA",
                "role": "BAT",
                "hand": "RHB",
                "matches": 5,
                "runs_wkts": "342 runs",
                "avg": "42.7",
                "sr_econ": "68.2 SR",
                "fantasy_avg": "68.0 pts",
                "badge": "Home Dominance"
            },
            {
                "player": "Marco Jansen",
                "team": "RSA",
                "role": "AR",
                "hand": "LAP (141 km/h)",
                "matches": 4,
                "runs_wkts": "14 wkts, 128 runs",
                "avg": "24.1",
                "sr_econ": "3.20 Econ",
                "fantasy_avg": "72.0 pts",
                "badge": "Steep Bounce Dual Equity"
            }
        ]
    },
    "aus_w_vs_eng_w_sydney": {
        "id": "aus_w_vs_eng_w_sydney",
        "aliases": [
            "aus_w_eng_w"
        ],
        "title": "Australia Women vs England Women, 1st T20I",
        "series": "Women's Ashes Series 2026",
        "date": "Today, Oct 24, 2026",
        "time": "1:40 PM IST (7:10 PM AEDT)",
        "venue": "North Sydney Oval, Sydney, Australia",
        "countdown": "Starts in 18h 30m \u2022 Lock Deadline 1:40 PM IST",
        "format": "WT20I",
        "status": "UPCOMING",
        "category": "INTERNATIONAL",
        "archetype": "ROAD_HIGHWAY",
        "par_score": 185,
        "soil": "Bulli Soil Deck with 49m Short Square Boundaries",
        "seamMm": "1.8 mm",
        "turnDeg": "1.5\u00b0",
        "pacePct": 52,
        "spinPct": 48,
        "spin_pct": "48% Wkts (Tiny Boundaries 49m)",
        "toss_statement": "North Sydney Oval: 49m short square boundaries. True bounce and lightning fast outfield. Six-hitting rate is highest in women's cricket.",
        "unspent_shield": "13.0 - 17.0 Cr Unspent",
        "narrative_shield": "100% Boundary Ramp Aligned",
        "boundaries": {
            "straight": "62m",
            "sqLeg": "49m (Tiny)",
            "midWkt": "53m",
            "thirdMan": "48m",
            "cover": "52m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 North Sydney Six-Hitting Ramp",
                "scenario_tag": "SHORT_BOUNDARY_ASSAULT",
                "captain": "Beth Mooney",
                "vice_captain": "Nat Sciver-Brunt",
                "unspent_credits": 15.0,
                "uniqueness": 99.9,
                "strategy": "Targets short 49m boundary using left-hand / right-hand power pairings.",
                "players": [
                    {
                        "name": "Beth Mooney",
                        "role": "WK",
                        "credits": 9.0,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Alyssa Healy",
                        "role": "WK",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Danni Wyatt-Hodge",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Ellyse Perry",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Nat Sciver-Brunt",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Ashleigh Gardner",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Alice Capsey",
                        "role": "AR",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Sophie Ecclestone",
                        "role": "BOWL",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Megan Schutt",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Lauren Bell",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Annabel Sutherland",
                        "role": "AR",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Beth Mooney",
                "bowler": "Sophie Ecclestone",
                "runs": 62,
                "balls": 51,
                "dism": 1,
                "sr": 121.5,
                "adv": "Batter Edge"
            },
            {
                "batter": "Nat Sciver-Brunt",
                "bowler": "Megan Schutt",
                "runs": 48,
                "balls": 36,
                "dism": 2,
                "sr": 133.3,
                "adv": "Bowler Strike"
            }
        ],
        "matchups": [
            {
                "batter": "Beth Mooney",
                "batter_hand": "Left-Hand Bat (LHB)",
                "bowler": "Sophie Ecclestone",
                "bowler_arm": "Slow Left-Arm Orthodox (SLA)",
                "speed": "88.4 km/h",
                "runs": 62,
                "balls": 51,
                "dism": 1,
                "sr": 121.5,
                "dots": 35.2,
                "fours": 6,
                "sixes": 1,
                "venue_factor": "North Sydney short 49m square boundary targeted with sweeps",
                "adv": "Batter Advantage (Controls Spin Angle)"
            },
            {
                "batter": "Nat Sciver-Brunt",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Megan Schutt",
                "bowler_arm": "Right-Arm Medium Inswing (RAF)",
                "speed": "112.5 km/h",
                "runs": 48,
                "balls": 36,
                "dism": 2,
                "sr": 133.3,
                "dots": 38.8,
                "fours": 5,
                "sixes": 1,
                "venue_factor": "Schutt in-swinger challenges Sciver front pad LBW",
                "adv": "Bowler Strike Hazard (2 Dismissals in Powerplay)"
            },
            {
                "batter": "Alyssa Healy",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Lauren Bell",
                "bowler_arm": "Right-Arm Fast-Medium (RAF)",
                "speed": "118.2 km/h",
                "runs": 55,
                "balls": 31,
                "dism": 1,
                "sr": 177.4,
                "dots": 25.8,
                "fours": 8,
                "sixes": 2,
                "venue_factor": "Healy steps out to hit over extra cover on small ground",
                "adv": "Batter Dominant (+175 SR vs Pace)"
            },
            {
                "batter": "Danni Wyatt-Hodge",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Ashleigh Gardner",
                "bowler_arm": "Right-Arm Offbreak (OB)",
                "speed": "85.6 km/h",
                "runs": 39,
                "balls": 28,
                "dism": 2,
                "sr": 139.2,
                "dots": 39.2,
                "fours": 4,
                "sixes": 1,
                "venue_factor": "High risk lofted drives over long-on",
                "adv": "Bowler Trap (2 False Stroke Dismissals)"
            },
            {
                "batter": "Ellyse Perry",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Sarah Glenn",
                "bowler_arm": "Right-Arm Legbreak (LB)",
                "speed": "84.0 km/h",
                "runs": 46,
                "balls": 32,
                "dism": 0,
                "sr": 143.8,
                "dots": 28.1,
                "fours": 5,
                "sixes": 1,
                "venue_factor": "Uses feet to loft leg-spinner straight over 52m boundary",
                "adv": "Batter Dominant (Zero Dismissals)"
            },
            {
                "batter": "Heather Knight",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Alana King",
                "bowler_arm": "Right-Arm Legbreak (LB)",
                "speed": "83.5 km/h",
                "runs": 32,
                "balls": 29,
                "dism": 2,
                "sr": 110.3,
                "dots": 48.2,
                "fours": 3,
                "sixes": 0,
                "venue_factor": "King sharp legbreak grips Bulli soil deck",
                "adv": "Bowler Trap (Turn & Bounce Advantage)"
            }
        ],
        "handedness_matrix": [
            {
                "batter": "Beth Mooney",
                "hand": "LHB",
                "vs_rap": "Avg 46.5 | SR 136.0",
                "vs_lap": "Avg 42.0 | SR 130.0",
                "vs_ob": "Avg 38.0 | SR 125.0",
                "vs_lb": "Avg 44.0 | SR 134.0",
                "vs_sla": "Avg 48.5 | SR 140.0",
                "weakness_speed": "Tight fuller yorkers on middle stump",
                "venue_fit": "10/10 (Top scorer at North Sydney Oval)"
            },
            {
                "batter": "Nat Sciver-Brunt",
                "hand": "RHB",
                "vs_rap": "Avg 44.0 | SR 145.0",
                "vs_lap": "Avg 38.0 | SR 132.0",
                "vs_ob": "Avg 42.0 | SR 140.0",
                "vs_lb": "Avg 35.0 | SR 128.0",
                "vs_sla": "Avg 46.0 | SR 152.0",
                "weakness_speed": "In-swingers targeting knee roll 115 km/h",
                "venue_fit": "Elite Power Hitter"
            },
            {
                "batter": "Ellyse Perry",
                "hand": "RHB",
                "vs_rap": "Avg 48.0 | SR 148.0",
                "vs_lap": "Avg 39.5 | SR 135.0",
                "vs_ob": "Avg 44.0 | SR 142.0",
                "vs_lb": "Avg 41.0 | SR 138.0",
                "vs_sla": "Avg 50.0 | SR 155.0",
                "weakness_speed": "Short-pitched quick bouncer",
                "venue_fit": "Ground Record Holder (90+ avg at North Sydney)"
            },
            {
                "batter": "Danni Wyatt-Hodge",
                "hand": "RHB",
                "vs_rap": "Avg 32.0 | SR 142.0",
                "vs_lap": "Avg 28.5 | SR 128.0",
                "vs_ob": "Avg 29.0 | SR 134.0",
                "vs_lb": "Avg 34.0 | SR 145.0",
                "vs_sla": "Avg 38.0 | SR 150.0",
                "weakness_speed": "Offbreak sliding into leg stump",
                "venue_fit": "High Ceiling Powerplay Batter"
            }
        ],
        "venue_player_records": [
            {
                "player": "Ellyse Perry",
                "team": "AUS",
                "role": "AR",
                "hand": "RHB / RAF (116 km/h)",
                "matches": 8,
                "runs_wkts": "392 runs, 7 wkts",
                "avg": "65.3",
                "sr_econ": "146.8 SR",
                "fantasy_avg": "88.0 pts",
                "badge": "North Sydney Queen"
            },
            {
                "player": "Beth Mooney",
                "team": "AUS",
                "role": "WK",
                "hand": "LHB",
                "matches": 7,
                "runs_wkts": "340 runs",
                "avg": "56.6",
                "sr_econ": "141.2 SR",
                "fantasy_avg": "78.0 pts",
                "badge": "Run Machine"
            },
            {
                "player": "Nat Sciver-Brunt",
                "team": "ENG",
                "role": "AR",
                "hand": "RHB / RAF (116 km/h)",
                "matches": 5,
                "runs_wkts": "218 runs, 5 wkts",
                "avg": "43.6",
                "sr_econ": "138.5 SR",
                "fantasy_avg": "74.5 pts",
                "badge": "All-Round Engine"
            },
            {
                "player": "Sophie Ecclestone",
                "team": "ENG",
                "role": "BOWL",
                "hand": "SLA (88 km/h)",
                "matches": 5,
                "runs_wkts": "9 wickets",
                "avg": "15.2",
                "sr_econ": "5.80 Econ",
                "fantasy_avg": "68.0 pts",
                "badge": "Spin Lockdown"
            },
            {
                "player": "Ashleigh Gardner",
                "team": "AUS",
                "role": "AR",
                "hand": "RHB / OB (85 km/h)",
                "matches": 6,
                "runs_wkts": "184 runs, 6 wkts",
                "avg": "36.8",
                "sr_econ": "152.0 SR",
                "fantasy_avg": "66.0 pts",
                "badge": "Power Surge"
            }
        ]
    },
    "nz_w_vs_aus_w_hagley": {
        "id": "nz_w_vs_aus_w_hagley",
        "aliases": [
            "nz_w_aus_w"
        ],
        "title": "New Zealand Women vs Australia Women, 2nd ODI",
        "series": "Trans-Tasman Trophy 2026",
        "date": "Friday, Oct 23, 2026",
        "time": "6:30 AM IST (2:00 PM NZDT)",
        "venue": "Hagley Oval, Christchurch, New Zealand",
        "countdown": "Starts Oct 24 \u2022 Morning Swing & True Bounce",
        "format": "WODI",
        "status": "UPCOMING",
        "category": "INTERNATIONAL",
        "archetype": "GREEN_SEAM_SWING",
        "par_score": 242,
        "soil": "Canterbury Silt Loam with Overcast Sea Breeze",
        "seamMm": "3.8 mm",
        "turnDeg": "1.8\u00b0",
        "pacePct": 70,
        "spinPct": 30,
        "spin_pct": "30% Wkts (Canterbury Swing)",
        "toss_statement": "Hagley Oval pitch: Crisp Christchurch morning with dew. Lateral movement of 3.8mm in first 15 overs. Pacers enjoy steep bounce.",
        "unspent_shield": "13.5 - 17.5 Cr Unspent",
        "narrative_shield": "100% Swing & Seam Aligned",
        "boundaries": {
            "straight": "68m",
            "sqLeg": "60m",
            "midWkt": "64m",
            "thirdMan": "58m",
            "cover": "62m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 Hagley Morning Seam Exploiter",
                "scenario_tag": "NEW_BALL_SWING_BLITZ",
                "captain": "Lea Tahuhu",
                "vice_captain": "Ellyse Perry",
                "unspent_credits": 16.0,
                "uniqueness": 99.8,
                "strategy": "Harnesses Christchurch green seamer for early wickets before middle-order consolidation.",
                "players": [
                    {
                        "name": "Beth Mooney",
                        "role": "WK",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Suzie Bates",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Meg Lanning",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Sophie Devine",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Ellyse Perry",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Amelia Kerr",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Lea Tahuhu",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Megan Schutt",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Jess Kerr",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Alana King",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Hannah Rowe",
                        "role": "BOWL",
                        "credits": 7.0,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Suzie Bates",
                "bowler": "Megan Schutt",
                "runs": 72,
                "balls": 94,
                "dism": 3,
                "sr": 76.6,
                "adv": "Bowler Trap"
            },
            {
                "batter": "Sophie Devine",
                "bowler": "Alana King",
                "runs": 55,
                "balls": 41,
                "dism": 1,
                "sr": 134.1,
                "adv": "Batter Dominant"
            }
        ],
        "matchups": [],
        "handedness_matrix": [],
        "venue_player_records": []
    },
    "163671": {
        "id": "163671",
        "aliases": [
            "kar_vs_saur_ranji"
        ],
        "title": "Karnataka vs Saurashtra, Elite Group B",
        "series": "Ranji Trophy Elite 2026-27",
        "date": "Today, Oct 24, 2026",
        "time": "9:30 AM IST (4:00 AM GMT)",
        "venue": "M. Chinnaswamy Stadium, Bengaluru, India",
        "countdown": "Live Day 3 \u2022 Spin Turning into Rough",
        "format": "FIRST_CLASS",
        "status": "LIVE NOW",
        "category": "DOMESTIC",
        "archetype": "HIGH_STAKES_PARITY",
        "par_score": 315,
        "soil": "Red Soil with Footmark Roughs (Day 3 Spin Break)",
        "seamMm": "2.4 mm",
        "turnDeg": "3.5\u00b0",
        "pacePct": 45,
        "spinPct": 55,
        "spin_pct": "55% Wkts (Day 3 Rough)",
        "toss_statement": "Chinnaswamy Day 3: Footmarks outside off-stump creating puff of dust. Left-arm spin and off-break extracting sharp turn.",
        "unspent_shield": "12.0 - 16.0 Cr Unspent",
        "narrative_shield": "100% Spin Rough Aligned",
        "boundaries": {
            "straight": "68m",
            "sqLeg": "62m",
            "midWkt": "65m",
            "thirdMan": "58m",
            "cover": "64m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 Day 3 Spin Dominance",
                "scenario_tag": "RED_SOIL_ROUGH_COLLAPSE",
                "captain": "Dharmendrasinh Jadeja",
                "vice_captain": "Mayank Agarwal",
                "unspent_credits": 14.5,
                "uniqueness": 99.8,
                "strategy": "Leverages Saurashtra's left-arm spinner into Karnataka's right-hand heavy order on Day 3 rough.",
                "players": [
                    {
                        "name": "Mayank Agarwal",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Devdutt Padikkal",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Cheteshwar Pujara",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Arpit Vasavada",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Shreyas Gopal",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Prerak Mankad",
                        "role": "AR",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Dharmendrasinh Jadeja",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Vyshak Vijaykumar",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Jaydev Unadkat",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Vidwath Kaverappa",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Sujit Gowda",
                        "role": "BAT",
                        "credits": 7.0,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Mayank Agarwal",
                "bowler": "Jaydev Unadkat",
                "runs": 92,
                "balls": 140,
                "dism": 2,
                "sr": 65.7,
                "adv": "Balanced"
            },
            {
                "batter": "Cheteshwar Pujara",
                "bowler": "Vyshak Vijaykumar",
                "runs": 74,
                "balls": 160,
                "dism": 1,
                "sr": 46.2,
                "adv": "Batter Wall"
            }
        ],
        "matchups": [],
        "handedness_matrix": [],
        "venue_player_records": []
    },
    "170723": {
        "id": "170723",
        "aliases": [
            "pak_vs_eng_odi_karachi"
        ],
        "title": "Pakistan vs England, 2nd ODI",
        "series": "Pakistan ODI Tri-Series 2026",
        "date": "Today, Oct 24, 2026",
        "time": "3:00 PM IST (9:30 AM GMT)",
        "venue": "National Stadium, Karachi, Pakistan",
        "countdown": "Starts Tomorrow \u2022 High-Scoring Highway",
        "format": "ODI",
        "status": "UPCOMING",
        "category": "INTERNATIONAL",
        "archetype": "ROAD_HIGHWAY",
        "par_score": 298,
        "soil": "Flat Batting Concrete Deck (High Batting True Bounce)",
        "seamMm": "1.7 mm",
        "turnDeg": "1.9\u00b0",
        "pacePct": 56,
        "spinPct": 44,
        "spin_pct": "44% Wkts (Flat Track 298 Par)",
        "toss_statement": "Karachi pitch: Complete batting paradise. Very little seam movement under lights. Chasing team has high advantage due to heavy evening dew.",
        "unspent_shield": "13.0 - 17.0 Cr Unspent",
        "narrative_shield": "100% Batting Highway Aligned",
        "boundaries": {
            "straight": "72m",
            "sqLeg": "64m",
            "midWkt": "68m",
            "thirdMan": "60m",
            "cover": "66m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 Karachi 320+ Run Festival",
                "scenario_tag": "HIGH_TOTAL_BATTING_SURGE",
                "captain": "Babar Azam",
                "vice_captain": "Harry Brook",
                "unspent_credits": 15.0,
                "uniqueness": 99.9,
                "strategy": "Packs top-order stroke-makers to exploit the flat Karachi wicket and rapid outfield.",
                "players": [
                    {
                        "name": "Jos Buttler",
                        "role": "WK",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mohammad Rizwan",
                        "role": "WK",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Babar Azam",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Harry Brook",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Fakhar Zaman",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Liam Livingstone",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Agha Salman",
                        "role": "AR",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Shaheen Shah Afridi",
                        "role": "BOWL",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Jofra Archer",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Haris Rauf",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Adil Rashid",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Babar Azam",
                "bowler": "Jofra Archer",
                "runs": 66,
                "balls": 74,
                "dism": 1,
                "sr": 89.1,
                "adv": "Batter Solid"
            },
            {
                "batter": "Jos Buttler",
                "bowler": "Shaheen Shah Afridi",
                "runs": 48,
                "balls": 38,
                "dism": 2,
                "sr": 126.3,
                "adv": "Bowler Strike"
            }
        ],
        "matchups": [
            {
                "batter": "Babar Azam",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Jofra Archer",
                "bowler_arm": "Right-Arm Fast (RAF)",
                "speed": "148.6 km/h",
                "runs": 66,
                "balls": 74,
                "dism": 1,
                "sr": 89.1,
                "dots": 52.7,
                "fours": 8,
                "sixes": 0,
                "venue_factor": "Karachi true bounce allows Babar backfoot punch through point",
                "adv": "Batter Solid (Controlled Mastery vs 148 km/h Pace)"
            },
            {
                "batter": "Jos Buttler",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Shaheen Shah Afridi",
                "bowler_arm": "Left-Arm Fast (LAP)",
                "speed": "142.4 km/h",
                "runs": 48,
                "balls": 38,
                "dism": 2,
                "sr": 126.3,
                "dots": 44.7,
                "fours": 5,
                "sixes": 2,
                "venue_factor": "New ball swing into Buttler pads under Karachi floodlights",
                "adv": "Bowler Strike Hazard (2 Powerplay Dismissals)"
            },
            {
                "batter": "Harry Brook",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Haris Rauf",
                "bowler_arm": "Right-Arm Express Fast (RAF)",
                "speed": "147.8 km/h",
                "runs": 58,
                "balls": 34,
                "dism": 1,
                "sr": 170.6,
                "dots": 29.4,
                "fours": 7,
                "sixes": 3,
                "venue_factor": "Brook capitalizes on high pace to clear midwicket (68m)",
                "adv": "Batter Dominant (+170 SR vs Express Pace)"
            },
            {
                "batter": "Fakhar Zaman",
                "batter_hand": "Left-Hand Bat (LHB)",
                "bowler": "Adil Rashid",
                "bowler_arm": "Right-Arm Legbreak (LB)",
                "speed": "86.5 km/h",
                "runs": 44,
                "balls": 38,
                "dism": 2,
                "sr": 115.8,
                "dots": 47.3,
                "fours": 4,
                "sixes": 1,
                "venue_factor": "Rashid googly slipping under Fakhar slog sweep",
                "adv": "Bowler Trap (Googly Hazard)"
            },
            {
                "batter": "Mohammad Rizwan",
                "batter_hand": "Right-Hand Bat (RHB)",
                "bowler": "Mark Wood",
                "bowler_arm": "Right-Arm Express Fast (RAF)",
                "speed": "151.2 km/h",
                "runs": 36,
                "balls": 31,
                "dism": 1,
                "sr": 116.1,
                "dots": 48.3,
                "fours": 4,
                "sixes": 0,
                "venue_factor": "150+ km/h bouncers force hurried pull shots",
                "adv": "High Pace Stress Test"
            }
        ],
        "handedness_matrix": [
            {
                "batter": "Babar Azam",
                "hand": "RHB",
                "vs_rap": "Avg 54.0 | SR 92.0",
                "vs_lap": "Avg 46.5 | SR 88.0",
                "vs_ob": "Avg 58.0 | SR 95.0",
                "vs_lb": "Avg 48.0 | SR 89.0",
                "vs_sla": "Avg 52.0 | SR 94.0",
                "weakness_speed": "Fifth stump away movement at 140+ km/h",
                "venue_fit": "10/10 (Highest ODI run getter in Karachi)"
            },
            {
                "batter": "Jos Buttler",
                "hand": "RHB",
                "vs_rap": "Avg 42.0 | SR 138.0",
                "vs_lap": "Avg 33.0 | SR 122.0",
                "vs_ob": "Avg 44.0 | SR 135.0",
                "vs_lb": "Avg 38.0 | SR 128.0",
                "vs_sla": "Avg 46.0 | SR 142.0",
                "weakness_speed": "In-swinging toe-crusher yorker 142 km/h",
                "venue_fit": "Elite Chasing Impact"
            },
            {
                "batter": "Harry Brook",
                "hand": "RHB",
                "vs_rap": "Avg 48.0 | SR 142.0",
                "vs_lap": "Avg 41.0 | SR 130.0",
                "vs_ob": "Avg 45.0 | SR 136.0",
                "vs_lb": "Avg 36.0 | SR 118.0",
                "vs_sla": "Avg 50.0 | SR 155.0",
                "weakness_speed": "Deceptive slower balls outside off",
                "venue_fit": "Huge ceiling at National Stadium"
            },
            {
                "batter": "Fakhar Zaman",
                "hand": "LHB",
                "vs_rap": "Avg 44.0 | SR 125.0",
                "vs_lap": "Avg 38.0 | SR 112.0",
                "vs_ob": "Avg 48.0 | SR 136.0",
                "vs_lb": "Avg 32.0 | SR 105.0",
                "vs_sla": "Avg 52.0 | SR 145.0",
                "weakness_speed": "Sharp wrong-un from wrist spinners",
                "venue_fit": "Powerplay boundary clearer"
            }
        ],
        "venue_player_records": [
            {
                "player": "Babar Azam",
                "team": "PAK",
                "role": "BAT",
                "hand": "RHB",
                "matches": 12,
                "runs_wkts": "784 runs",
                "avg": "71.2",
                "sr_econ": "94.5 SR",
                "fantasy_avg": "86.0 pts",
                "badge": "Karachi King"
            },
            {
                "player": "Mohammad Rizwan",
                "team": "PAK",
                "role": "WK",
                "hand": "RHB",
                "matches": 10,
                "runs_wkts": "542 runs",
                "avg": "60.2",
                "sr_econ": "91.8 SR",
                "fantasy_avg": "76.5 pts",
                "badge": "Anchor Pillar"
            },
            {
                "player": "Shaheen Shah Afridi",
                "team": "PAK",
                "role": "BOWL",
                "hand": "LAP (142 km/h)",
                "matches": 8,
                "runs_wkts": "18 wickets",
                "avg": "21.4",
                "sr_econ": "5.10 Econ",
                "fantasy_avg": "68.0 pts",
                "badge": "First Over Strike"
            },
            {
                "player": "Harry Brook",
                "team": "ENG",
                "role": "BAT",
                "hand": "RHB",
                "matches": 4,
                "runs_wkts": "268 runs",
                "avg": "67.0",
                "sr_econ": "148.0 SR",
                "fantasy_avg": "82.0 pts",
                "badge": "Highway Destroyer"
            },
            {
                "player": "Jofra Archer",
                "team": "ENG",
                "role": "BOWL",
                "hand": "RAF (148 km/h)",
                "matches": 3,
                "runs_wkts": "7 wickets",
                "avg": "19.5",
                "sr_econ": "4.85 Econ",
                "fantasy_avg": "64.0 pts",
                "badge": "Express Threat"
            }
        ]
    },
    "173411": {
        "id": "173411",
        "aliases": [
            "dol_vs_war_csa_t20"
        ],
        "title": "Dolphins vs Warriors, Pool A",
        "series": "CSA T20 Challenge 2026",
        "date": "Today, Oct 24, 2026",
        "time": "9:30 PM IST (6:00 PM Local)",
        "venue": "St George's Park, Gqeberha, South Africa",
        "countdown": "Starts in 2h 15m \u2022 High Coastal Wind Factor",
        "format": "T20",
        "status": "UPCOMING",
        "category": "DOMESTIC",
        "archetype": "GREEN_SEAM_SWING",
        "par_score": 158,
        "soil": "Slow Coastal Seamer with Strong Wind Gusts",
        "seamMm": "3.5 mm",
        "turnDeg": "2.2\u00b0",
        "pacePct": 65,
        "spinPct": 35,
        "spin_pct": "35% Wkts (Coastal Wind Seam)",
        "toss_statement": "St George's Park: Stiff cross-breeze blowing from Algoa Bay. New ball swings significantly. Par score is 155-160.",
        "unspent_shield": "14.0 - 18.0 Cr Unspent",
        "narrative_shield": "100% Wind & Seam Aligned",
        "boundaries": {
            "straight": "70m",
            "sqLeg": "64m",
            "midWkt": "68m",
            "thirdMan": "58m",
            "cover": "65m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 Windy Gqeberha Swing Assault",
                "scenario_tag": "COASTAL_SEAM_HEDGE",
                "captain": "Andile Simelane",
                "vice_captain": "Matthew Breetzke",
                "unspent_credits": 16.0,
                "uniqueness": 99.8,
                "strategy": "Takes advantage of coastal crosswind swinging deliveries away from opening batters.",
                "players": [
                    {
                        "name": "Matthew Breetzke",
                        "role": "WK",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Grant Roelofsen",
                        "role": "WK",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Jordan Hermann",
                        "role": "BAT",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Khaya Zondo",
                        "role": "BAT",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Andile Simelane",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Patrick Kruger",
                        "role": "AR",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Prenelan Subrayen",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Ottniel Baartman",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Beyers Swanepoel",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Daryn Dupavillon",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Siya Simetu",
                        "role": "BOWL",
                        "credits": 7.0,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Matthew Breetzke",
                "bowler": "Ottniel Baartman",
                "runs": 32,
                "balls": 24,
                "dism": 1,
                "sr": 133.3,
                "adv": "Competitive"
            }
        ],
        "matchups": [],
        "handedness_matrix": [],
        "venue_player_records": []
    },
    "173941": {
        "id": "173941",
        "aliases": [
            "uga_vs_zmb_t20"
        ],
        "title": "Uganda vs Zambia, 1st Match",
        "series": "ICC Men's T20 World Cup Africa Qualifier C 2026",
        "date": "Today, Oct 24, 2026",
        "time": "4:30 PM IST (2:00 PM Local EAT)",
        "venue": "Gymkhana Club Ground, Nairobi, Kenya",
        "countdown": "Live 2nd Innings \u2022 Low-Scoring Spin Minefield",
        "format": "T20I",
        "status": "LIVE NOW",
        "category": "INTERNATIONAL",
        "archetype": "SPIN_CHOKE_MINEFIELD",
        "par_score": 128,
        "soil": "Slow Low Nairobi Track (Low Bounce, Extreme Turn)",
        "seamMm": "2.2 mm",
        "turnDeg": "4.1\u00b0",
        "pacePct": 30,
        "spinPct": 70,
        "spin_pct": "70% Wkts (4.1\u00b0 Spin Choke)",
        "toss_statement": "Nairobi Gymkhana: Abrasive dry surface. Very low bounce with spinners getting 4+ degrees of grip. 130 is a defending total.",
        "unspent_shield": "15.0 - 19.0 Cr Unspent",
        "narrative_shield": "100% Spin Choke Aligned",
        "boundaries": {
            "straight": "62m",
            "sqLeg": "56m",
            "midWkt": "60m",
            "thirdMan": "54m",
            "cover": "58m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 Uganda Spin Web Choke",
                "scenario_tag": "SPIN_WEB_CHOKE",
                "captain": "Alpesh Ramjani",
                "vice_captain": "Henry Ssenyondo",
                "unspent_credits": 17.5,
                "uniqueness": 99.9,
                "strategy": "Exploits 4.1 degree turn on dry Nairobi pitch with Uganda's slow left-arm duo.",
                "players": [
                    {
                        "name": "Simon Ssesazi",
                        "role": "WK",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Robinson Obuya",
                        "role": "BAT",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Riazat Ali Shah",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Alpesh Ramjani",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Dinesh Nakrani",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Juma Miyagi",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Henry Ssenyondo",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Cosmas Kyewuta",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Frank Nsubuga",
                        "role": "BOWL",
                        "credits": 7.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Zambia Pacer 1",
                        "role": "BOWL",
                        "credits": 6.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Zambia Spinner 2",
                        "role": "BOWL",
                        "credits": 6.0,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Robinson Obuya",
                "bowler": "Alpesh Ramjani",
                "runs": 14,
                "balls": 19,
                "dism": 2,
                "sr": 73.7,
                "adv": "Bowler Dominant"
            }
        ],
        "matchups": [],
        "handedness_matrix": [],
        "venue_player_records": []
    },
    "174953": {
        "id": "174953",
        "aliases": [
            "nam_vs_ire_odi"
        ],
        "title": "Namibia vs Ireland, 1st ODI",
        "series": "Ireland Tour of Namibia 2026",
        "date": "Today, Oct 24, 2026",
        "time": "1:00 PM IST (9:30 AM Local)",
        "venue": "Wanderers Cricket Ground, Windhoek, Namibia",
        "countdown": "High Altitude Thin Air \u2022 Big Hitting Value",
        "format": "ODI",
        "status": "LIVE NOW",
        "category": "INTERNATIONAL",
        "archetype": "ROAD_HIGHWAY",
        "par_score": 282,
        "soil": "High Altitude Hard Clay (Ball Flies Rapidly)",
        "seamMm": "2.0 mm",
        "turnDeg": "1.7\u00b0",
        "pacePct": 60,
        "spinPct": 40,
        "spin_pct": "40% Wkts (Windhoek Altitude 282 Par)",
        "toss_statement": "Windhoek Wanderers: 1,700m above sea level. Reduced air resistance causes maximum boundary distances. Fast hard pitch.",
        "unspent_shield": "13.5 - 17.5 Cr Unspent",
        "narrative_shield": "100% Thin Air Altitude Aligned",
        "boundaries": {
            "straight": "68m",
            "sqLeg": "60m",
            "midWkt": "64m",
            "thirdMan": "56m",
            "cover": "62m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 Windhoek Altitude Sixes",
                "scenario_tag": "ALTITUDE_POWERPLAY_SURGE",
                "captain": "Harry Tector",
                "vice_captain": "Gerhard Erasmus",
                "unspent_credits": 15.5,
                "uniqueness": 99.8,
                "strategy": "Picks maximum boundary power hitters who benefit from Windhoek's 1,700m thin air.",
                "players": [
                    {
                        "name": "Lorcan Tucker",
                        "role": "WK",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Paul Stirling",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Harry Tector",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Gerhard Erasmus",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Curtis Campher",
                        "role": "AR",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Jan Frylinck",
                        "role": "AR",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Mark Adair",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Ruben Trumpelmann",
                        "role": "BOWL",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Joshua Little",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Bernard Scholtz",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Craig Young",
                        "role": "BOWL",
                        "credits": 7.0,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Paul Stirling",
                "bowler": "Ruben Trumpelmann",
                "runs": 36,
                "balls": 28,
                "dism": 1,
                "sr": 128.6,
                "adv": "Even"
            }
        ],
        "matchups": [],
        "handedness_matrix": [],
        "venue_player_records": []
    },
    "ind_w_vs_zim_w_2026_03": {
        "id": "ind_w_vs_zim_w_2026_03",
        "aliases": [
            "155541"
        ],
        "title": "India Women vs Zimbabwe Women, 3rd T20I",
        "series": "Zimbabwe Women Tour of India 2026",
        "date": "Oct 20, 2026 (Completed)",
        "time": "7:00 PM IST (1:30 PM GMT)",
        "venue": "Shaheed Veer Narayan Singh Stadium, Raipur, India",
        "countdown": "Result: IND-W Won by 92 Runs (Harman 91*)",
        "format": "WT20I",
        "status": "COMPLETED",
        "category": "INTERNATIONAL",
        "archetype": "ASYMMETRIC_MISMATCH",
        "par_score": 178,
        "soil": "Red Clay Deck with Medium Bounce",
        "seamMm": "3.1 mm",
        "turnDeg": "2.4\u00b0",
        "pacePct": 55,
        "spinPct": 45,
        "spin_pct": "45% Wkts (2.4\u00b0 Turn)",
        "toss_statement": "Raipur pitch report: Even bounce and fast outfield. India batting depth gave massive 195 total.",
        "unspent_shield": "14.5 - 19.0 Cr Unspent",
        "narrative_shield": "100% Indian Dominance Aligned",
        "boundaries": {
            "straight": "68m",
            "sqLeg": "60m",
            "midWkt": "64m",
            "thirdMan": "58m",
            "cover": "62m"
        },
        "lineups": [
            {
                "name": "Team 1 \u2022 Harmanpreet Power Surge",
                "scenario_tag": "SOLO_EQUITY_BLITZ",
                "captain": "Harmanpreet Kaur",
                "vice_captain": "Smriti Mandhana",
                "unspent_credits": 16.5,
                "uniqueness": 99.9,
                "strategy": "Capitalizes on Indian top-order dominance against Zimbabwe bowling lineup.",
                "players": [
                    {
                        "name": "Richa Ghosh",
                        "role": "WK",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Smriti Mandhana",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": True
                    },
                    {
                        "name": "Harmanpreet Kaur",
                        "role": "BAT",
                        "credits": 9.0,
                        "is_c": True,
                        "is_vc": False
                    },
                    {
                        "name": "Shafali Verma",
                        "role": "BAT",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Deepti Sharma",
                        "role": "AR",
                        "credits": 9.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Pooja Vastrakar",
                        "role": "AR",
                        "credits": 8.0,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Renuka Singh Thakur",
                        "role": "BOWL",
                        "credits": 8.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Radha Yadav",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Shreyanka Patil",
                        "role": "BOWL",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Kelis Ndhlovu",
                        "role": "AR",
                        "credits": 7.5,
                        "is_c": False,
                        "is_vc": False
                    },
                    {
                        "name": "Nomvelo Sibanda",
                        "role": "BOWL",
                        "credits": 6.0,
                        "is_c": False,
                        "is_vc": False
                    }
                ]
            }
        ],
        "battles": [
            {
                "batter": "Smriti Mandhana",
                "bowler": "Nomvelo Sibanda",
                "runs": 34,
                "balls": 18,
                "dism": 0,
                "sr": 188.9,
                "adv": "Batter Dominant"
            }
        ],
        "matchups": [],
        "handedness_matrix": [],
        "venue_player_records": []
    }
}
