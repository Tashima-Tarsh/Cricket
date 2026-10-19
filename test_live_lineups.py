import sys
import json
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from gl_engine.models import Player
from gl_engine.ortools_optimizer import ORToolsCricketOptimizer

with open("gl_engine/data/ind_wi_match.json", "r", encoding="utf-8") as f:
    d = json.load(f)

players = [Player(**p) for p in d["players"]]
venue = d["match_info"]["venue"]

opt = ORToolsCricketOptimizer(players)

print("=" * 70)
print("  LIVE GRAND LEAGUE PORTFOLIO: 79-85 CR ANTI-CHALK STRATEGY")
print("  Venue: M. Chinnaswamy (59.6% Pacer Wickets, Rain/Overcast)")
print("  Field: 500,000 - 1,500,000 Spots | Entry: ₹49 | 1st Prize: ₹30L - ₹1.08 Cr")
print("=" * 70)

lineups_85 = opt.generate_grand_league_portfolio(
    num_teams=5,
    min_differentials_per_team=3,
    max_overlap_between_teams=8,
    spots=500000,
    credit_strategy="79-85",
    venue_conditions=venue
)

for idx, l in enumerate(lineups_85, 1):
    c_pct = getattr(l.captain, "captain_percentage", 0.0)
    vc_pct = getattr(l.vice_captain, "captain_percentage", 0.0)
    c_dt = getattr(l.captain, "dream_team_percentage", 0.0)
    vc_dt = getattr(l.vice_captain, "dream_team_percentage", 0.0)
    
    print(f"\n--- TEAM #{idx}: {l.team_name} [{l.scenario_tag}] ---")
    print(f"Total Credits: {l.total_credits:.1f} / 100.0 Cr | 🔥 Unspent Budget: {100.0 - l.total_credits:.1f} Cr (Zero Field Collision)")
    print(f"Captain (2.0x): {l.captain.name} ({l.captain.credits} Cr | {c_pct}% C | {l.captain.projected_ownership}% Sel | {c_dt}% DT)")
    print(f"Vice-Captain (1.5x): {l.vice_captain.name} ({l.vice_captain.credits} Cr | {vc_pct}% C | {l.vice_captain.projected_ownership}% Sel | {vc_dt}% DT)")
    print("11-Player Selection:")
    for p in l.players:
        is_c = " [C]" if p.id == l.captain.id else (" [VC]" if p.id == l.vice_captain.id else "")
        dt_val = getattr(p, "dream_team_percentage", 0.0)
        c_val = getattr(p, "captain_percentage", 0.0)
        gem_tag = " [LOW-CR GEM]" if p.credits <= 7.5 else ""
        print(f"  • {p.name:<20} {p.team} | {p.role:<4} | {p.credits:4.1f} Cr | {p.projected_ownership:5.1f}% Sel | {dt_val:4.0f}% DT{is_c}{gem_tag}")

print("\n" + "=" * 70)
print("  LIVE GRAND LEAGUE PORTFOLIO: 87-89 CR ANTI-CHALK STRATEGY")
print("=" * 70)

lineups_89 = opt.generate_grand_league_portfolio(
    num_teams=3,
    min_differentials_per_team=3,
    max_overlap_between_teams=8,
    spots=500000,
    credit_strategy="87-89",
    venue_conditions=venue
)

for idx, l in enumerate(lineups_89, 1):
    c_pct = getattr(l.captain, "captain_percentage", 0.0)
    vc_pct = getattr(l.vice_captain, "captain_percentage", 0.0)
    c_dt = getattr(l.captain, "dream_team_percentage", 0.0)
    vc_dt = getattr(l.vice_captain, "dream_team_percentage", 0.0)
    
    print(f"\n--- TEAM #{idx}: {l.team_name} [{l.scenario_tag}] ---")
    print(f"Total Credits: {l.total_credits:.1f} / 100.0 Cr | 🔥 Unspent Budget: {100.0 - l.total_credits:.1f} Cr")
    print(f"Captain (2.0x): {l.captain.name} ({l.captain.credits} Cr | {c_pct}% C | {l.captain.projected_ownership}% Sel | {c_dt}% DT)")
    print(f"Vice-Captain (1.5x): {l.vice_captain.name} ({l.vice_captain.credits} Cr | {vc_pct}% C | {l.vice_captain.projected_ownership}% Sel | {vc_dt}% DT)")
    print("11-Player Selection:")
    for p in l.players:
        is_c = " [C]" if p.id == l.captain.id else (" [VC]" if p.id == l.vice_captain.id else "")
        dt_val = getattr(p, "dream_team_percentage", 0.0)
        gem_tag = " [LOW-CR GEM]" if p.credits <= 7.5 else ""
        print(f"  • {p.name:<20} {p.team} | {p.role:<4} | {p.credits:4.1f} Cr | {p.projected_ownership:5.1f}% Sel | {dt_val:4.0f}% DT{is_c}{gem_tag}")
