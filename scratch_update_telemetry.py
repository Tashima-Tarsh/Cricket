import json
from pathlib import Path

file_path = Path("gl_engine/data/ind_wi_match.json")
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 1. Update Match & Contest Info
data["match_info"]["contest"] = {
    "platform": "Dream11 (Come)",
    "type": "Mega Contest (Guaranteed plus+)",
    "entry_fee": 49,
    "current_prize_pool": 19600000,
    "max_prize_pool": 58800000,
    "current_first_prize": 3000000,
    "max_first_prize": 10800000,
    "current_spots": 500000,
    "max_spots": 1500000,
    "spots_left": 300761,
    "current_winners": 260000,
    "max_winners": 900000,
    "winners_pct": 52.0,
    "prize_distribution": [
        {"rank": "#1", "winnings": 3000000},
        {"rank": "#2", "winnings": 1100000},
        {"rank": "#3", "winnings": 550000},
        {"rank": "#4", "winnings": 280000},
        {"rank": "#5", "winnings": 140000},
        {"rank": "#6", "winnings": 70000},
        {"rank": "#7", "winnings": 45000},
        {"rank": "#8", "winnings": 25000},
        {"rank": "#9", "winnings": 15000},
        {"rank": "#10", "winnings": 10000},
        {"rank": "#11-15", "winnings": 4000},
        {"rank": "#16-25", "winnings": 3000},
        {"rank": "#26-40", "winnings": 1500},
        {"rank": "#41-70", "winnings": 1000},
        {"rank": "#71-125", "winnings": 700},
        {"rank": "#126-320", "winnings": 400},
        {"rank": "#321-1200", "winnings": 200},
        {"rank": "#1201-9000", "winnings": 100},
        {"rank": "#9001-90000", "winnings": 60},
        {"rank": "#90001-260000", "winnings": 49}
    ]
}

data["match_info"]["venue"] = {
    "name": "M. Chinnaswamy Stadium, Bengaluru",
    "city": "Bengaluru",
    "format": "T20",
    "pitch_nature": "Balanced surface. Good for Pacers. Overcast/rain conditions offer early seam and movement.",
    "pitch": "Balanced",
    "good_for": "Pacers",
    "weather": "Rain / Overcast",
    "avg_first_innings_score": 148,
    "avg_second_innings_score": 154,
    "avg_score": 151,
    "total_wickets_last_10": 104,
    "pace_wickets": 62,
    "pace_wickets_pct": 59.6,
    "spin_wickets": 42,
    "spin_wickets_pct": 40.4,
    "chasing_win_pct": 60.0,
    "boundary_dimensions": "Square 60m, Straight 70m"
}

data["match_info"]["weather"] = {
    "condition": "Rain / Overcast",
    "temperature_c": 23.0,
    "humidity_pct": 84.0,
    "rain_probability_pct": 65.0,
    "dew_expected": True,
    "wind_kmh": 14.0,
    "impact": "Early seam assistance for 145+ km/h pacers; rain forecast makes high-strike finishers and pacers vital."
}

data["match_info"]["recent_form"] = {
    "IND": ["L", "W", "L", "W", "L"],
    "WI": ["W", "L", "W", "L", "W"]
}

# 2. Update India Players with exact live telemetry
ind_updates = {
    "ind_samson": {"name": "Sanju Samson", "role": "WK", "credits": 8.0, "projected_ownership": 74.75, "captain_percentage": 10.95, "dream_team_percentage": 40.0, "differential_tag": "Powerplay Opener WK (74.8% Sel, 11% C, 40% DT)"},
    "ind_abhishek": {"name": "Abhishek Sharma", "role": "BAT", "credits": 9.0, "projected_ownership": 85.84, "captain_percentage": 26.06, "dream_team_percentage": 80.0, "differential_tag": "Mega Chalk Opener (85.8% Sel, 26.1% C, 80% DT)"},
    "ind_ishan": {"name": "Ishan Kishan", "role": "WK", "credits": 8.0, "projected_ownership": 78.43, "captain_percentage": 12.62, "dream_team_percentage": 80.0, "differential_tag": "In-Form Top-Order WK (78.4% Sel, 12.6% C, 80% DT)"},
    "ind_shreyas": {"name": "Shreyas Iyer", "role": "BAT", "credits": 8.0, "projected_ownership": 64.33, "captain_percentage": 5.61, "dream_team_percentage": 40.0, "differential_tag": "Middle-Overs Anchor (64.3% Sel, 5.6% C, 40% DT)"},
    "ind_tilak": {"name": "Tilak Varma", "role": "BAT", "credits": 7.5, "projected_ownership": 41.94, "captain_percentage": 1.23, "dream_team_percentage": 80.0, "differential_tag": "High-DT Leverage Batter (80% DT Rate, 7.5 Cr, 41.9% Sel, 1.2% C)"},
    "ind_naman": {"name": "Naman Dhir", "role": "AR", "credits": 8.5, "projected_ownership": 27.41, "captain_percentage": 0.65, "dream_team_percentage": 50.0, "differential_tag": "Sub-30% Differential AR (27.4% Sel, 50% DT Rate, 0.65% C)"},
    "ind_reddy": {"name": "Nitish Kumar Reddy", "role": "AR", "credits": 7.5, "projected_ownership": 41.26, "captain_percentage": 0.69, "dream_team_percentage": 50.0, "differential_tag": "Dual-Equity All-Rounder (7.5 Cr, 50% DT Rate, 41.3% Sel, 0.69% C)"},
    "ind_axar": {"name": "Axar Patel", "role": "AR", "credits": 7.0, "projected_ownership": 49.45, "captain_percentage": 1.22, "dream_team_percentage": 40.0, "differential_tag": "Low-Credit AR (7.0 Cr, 49.5% Sel, 1.22% C, 40% DT)"},
    "ind_arshdeep": {"name": "Arshdeep Singh", "role": "BOWL", "credits": 8.5, "projected_ownership": 63.19, "captain_percentage": 0.95, "dream_team_percentage": 40.0, "differential_tag": "Death Overs Pacer (8.5 Cr, 63.2% Sel, 59.6% Pacer Pitch)"},
    "ind_prince": {"name": "Prince Yadav", "role": "BOWL", "credits": 7.0, "projected_ownership": 24.28, "captain_percentage": 0.30, "dream_team_percentage": 0.0, "differential_tag": "Golden Differential Pacer (7.0 Cr, 24.3% Sel, 0.30% C)"},
    "ind_mayank": {"name": "Mayank Yadav", "role": "BOWL", "credits": 8.0, "projected_ownership": 26.84, "captain_percentage": 0.36, "dream_team_percentage": 25.0, "differential_tag": "155kph Express Strike Pacer (8.0 Cr, 26.8% Sel, 0.36% C)"}
}

# 3. Update West Indies Players with exact live telemetry
wi_updates = {
    "wi_hope": {"name": "Shai Hope", "role": "WK", "credits": 8.5, "projected_ownership": 86.25, "captain_percentage": 23.82, "dream_team_percentage": 60.0, "differential_tag": "Heavy Chalk Opener (86.3% Sel, 23.8% C, 60% DT)"},
    "wi_andrew": {"name": "Jewel Andrew", "role": "WK", "credits": 6.0, "projected_ownership": 27.68, "captain_percentage": 1.91, "dream_team_percentage": 20.0, "differential_tag": "Ultra Low-Credit WK Enabler (6.0 Cr, 27.7% Sel, 1.91% C)"},
    "wi_hetmyer": {"name": "Shimron Hetmyer", "role": "BAT", "credits": 9.0, "projected_ownership": 69.26, "captain_percentage": 2.01, "dream_team_percentage": 60.0, "differential_tag": "Power Hitter (9.0 Cr, 69.3% Sel, 2.01% C, 60% DT)"},
    "wi_powell": {"name": "Rovman Powell", "role": "BAT", "credits": 8.5, "projected_ownership": 24.11, "captain_percentage": 0.63, "dream_team_percentage": 60.0, "differential_tag": "Sub-25% Power Finisher Differential (8.5 Cr, 24.1% Sel, 60% DT)"},
    "wi_rutherford": {"name": "Sherfane Rutherford", "role": "BAT", "credits": 8.0, "projected_ownership": 74.98, "captain_percentage": 3.75, "dream_team_percentage": 80.0, "differential_tag": "In-Form Finisher (8.0 Cr, 75.0% Sel, 3.75% C, 80% DT)"},
    "wi_shepherd": {"name": "Romario Shepherd", "role": "AR", "credits": 8.5, "projected_ownership": 30.18, "captain_percentage": 0.57, "dream_team_percentage": 20.0, "differential_tag": "Death Overs Pacer & Finisher (8.5 Cr, 30.2% Sel, 0.57% C)"},
    "wi_paul": {"name": "Keemo Paul", "role": "AR", "credits": 6.5, "projected_ownership": 47.57, "captain_percentage": 1.04, "dream_team_percentage": 25.0, "differential_tag": "Slower Cutters Specialist (6.5 Cr, 47.6% Sel, 1.04% C)"},
    "wi_springer": {"name": "Shamar Springer", "role": "AR", "credits": 6.0, "projected_ownership": 44.25, "captain_percentage": 0.98, "dream_team_percentage": 40.0, "differential_tag": "Ultra Low-Credit Dual-Equity AR (6.0 Cr, 44.3% Sel, 40% DT)"},
    "wi_chase": {"name": "Roston Chase", "role": "AR", "credits": 8.0, "projected_ownership": 53.00, "captain_percentage": 1.17, "dream_team_percentage": 80.0, "differential_tag": "80% DT Rate Multi-Role AR (8.0 Cr, 53.0% Sel, 1.17% C)"},
    "wi_motie": {"name": "Gudakesh Motie", "role": "BOWL", "credits": 7.5, "projected_ownership": 19.01, "captain_percentage": 0.14, "dream_team_percentage": 20.0, "differential_tag": "Sub-20% Spin Differential (7.5 Cr, 19.0% Sel, 0.14% C)"},
    "wi_joseph": {"name": "Shamar Joseph", "role": "BOWL", "credits": 7.0, "projected_ownership": 14.60, "captain_percentage": 0.17, "dream_team_percentage": 40.0, "differential_tag": "Super Differential Strike Pacer (7.0 Cr, 14.6% Sel, 40% DT, 59.6% Pacer Pitch)"}
}

updated_players = []
for p in data["players"]:
    pid = p["id"]
    if pid == "ind_bishnoi":
        pid = "ind_arshdeep"
        p["id"] = "ind_arshdeep"
        p["name"] = "Arshdeep Singh"
        p["role"] = "BOWL"
        p["bowling_style"] = "Left-arm medium-fast"
        p["stats"]["death_overs_rate"] = 0.45

    if pid in ind_updates:
        u = ind_updates[pid]
        p["name"] = u["name"]
        p["role"] = u["role"]
        p["credits"] = u["credits"]
        p["projected_ownership"] = u["projected_ownership"]
        p["captain_percentage"] = u["captain_percentage"]
        p["dream_team_percentage"] = u["dream_team_percentage"]
        p["differential_tag"] = u["differential_tag"]
        p["is_confirmed_xi"] = True
    elif pid in wi_updates:
        u = wi_updates[pid]
        p["name"] = u["name"]
        p["role"] = u["role"]
        p["credits"] = u["credits"]
        p["projected_ownership"] = u["projected_ownership"]
        p["captain_percentage"] = u["captain_percentage"]
        p["dream_team_percentage"] = u["dream_team_percentage"]
        p["differential_tag"] = u["differential_tag"]
        p["is_confirmed_xi"] = True
    updated_players.append(p)

data["players"] = updated_players

# Save back to file
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Successfully updated ind_wi_match.json with exact live match telemetry!")

