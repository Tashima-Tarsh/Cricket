import sys
import json
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('gl_engine/data/ten_scenarios.json', 'r', encoding='utf-8') as f:
    scenarios = json.load(f)

with open('gl_engine/data/ind_wi_match.json', 'r', encoding='utf-8') as f:
    match_data = json.load(f)

# Payout structure
prizes = [
    (1, 3000000), (1, 1100000), (1, 550000), (1, 280000), (1, 140000),
    (1, 70000), (1, 45000), (1, 25000), (1, 15000), (1, 10000),
    (5, 4000), (10, 3000), (15, 1500), (30, 1000), (55, 700),
    (195, 400), (880, 200), (7800, 100), (81000, 60), (170000, 49)
]

FIELD_SIZE = 500000
N_TRIALS = 100000
np.random.seed(42)

results = {}

for name, team in scenarios.items():
    players = team['players']
    c_id = team['captain']['id']
    vc_id = team['vice_captain']['id']
    
    # Simulate 100k match trials
    # Vectorized player score sampling
    team_scores = np.zeros(N_TRIALS)
    
    avg_own = np.mean([p['projected_ownership'] for p in players])
    
    for p in players:
        mean_p = p.get('projected_points', p['stats']['avg_fantasy_pts'])
        ceil_p = p.get('ceiling_score', mean_p * 1.6)
        floor_p = p.get('floor_score', mean_p * 0.3)
        scale = max(8.0, (ceil_p - floor_p) / 3.29) # ~90th percentile ceiling
        
        # Gamma/LogNormal shaped distribution for cricket fantasy points (right-skewed)
        shape = max(1.5, (mean_p / scale) ** 2)
        scale_param = mean_p / shape
        sampled = np.random.gamma(shape=shape, scale=scale_param, size=N_TRIALS)
        
        mult = 1.0
        if p['id'] == c_id:
            mult = 2.0
        elif p['id'] == vc_id:
            mult = 1.5
            
        team_scores += sampled * mult

    mean_val = float(np.mean(team_scores))
    median_val = float(np.median(team_scores))
    p75 = float(np.percentile(team_scores, 75))
    p90 = float(np.percentile(team_scores, 90))
    p95 = float(np.percentile(team_scores, 95))
    p99 = float(np.percentile(team_scores, 99))
    p99_9 = float(np.percentile(team_scores, 99.9))
    
    p_gt_600 = float(np.mean(team_scores >= 600)) * 100
    p_gt_700 = float(np.mean(team_scores >= 700)) * 100
    p_gt_800 = float(np.mean(team_scores >= 800)) * 100
    
    # Duplication factor against public field of 500k entries
    # If lineup has heavy chalk (>60% avg own) and 98-100 credits, duplicates explode
    credits_left = round(100.0 - team['total_credits'], 1)
    if credits_left >= 14.0:
        dupes = 0
    elif credits_left >= 10.0:
        dupes = max(0, int(round((avg_own / 60.0)**4 * 12)))
    else:
        dupes = max(1, int(round((avg_own / 50.0)**5 * 380)))
        
    # Public field baseline: mean ~ 490 pts, std ~ 65 pts
    # Probability of beating field 99.9th percentile (~720 pts)
    p_top_01 = float(np.mean(team_scores >= 720.0))
    p_rank_1 = p_top_01 / max(1, (dupes + 1)) * (1.0 / 500.0) # Estimated P(1st)
    
    # Cash rate (Rank <= 260,000, i.e., top 52%)
    # Field 52nd percentile score is ~ 485 pts
    p_in_money = float(np.mean(team_scores >= 485.0)) * 100
    p_loss = 100.0 - p_in_money
    
    # Expected monetary return (EV)
    # Simple expected payout calculation based on percentile ranks
    # Top 0.0002% (Rank 1): 3,000,000 / (dupes + 1)
    # Top 0.002% (Ranks 2-10): avg 250,000
    # Top 0.01% (Ranks 11-50): avg 2,000
    # Top 0.2% (Ranks 51-1000): avg 250
    # Top 1.8% (Ranks 1001-9000): 100
    # Top 18% (Ranks 9001-90000): 60
    # Top 52% (Ranks 90001-260000): 49
    ev = 0.0
    ev += float(np.mean(team_scores >= p99_9)) * (3000000.0 / max(1, dupes + 1) * 0.002)
    ev += float(np.mean((team_scores >= p99) & (team_scores < p99_9))) * 350.0
    ev += float(np.mean((team_scores >= p95) & (team_scores < p99))) * 120.0
    ev += float(np.mean((team_scores >= p75) & (team_scores < p95))) * 60.0
    ev += float(np.mean((team_scores >= 485.0) & (team_scores < p75))) * 49.0
    
    results[name] = {
        'mean': round(mean_val, 1),
        'median': round(median_val, 1),
        'p75': round(p75, 1),
        'p90': round(p90, 1),
        'p95': round(p95, 1),
        'p99': round(p99, 1),
        'p_gt_600': round(p_gt_600, 2),
        'p_gt_700': round(p_gt_700, 2),
        'p_gt_800': round(p_gt_800, 2),
        'projected_duplicates': dupes,
        'p_in_money_pct': round(p_in_money, 2),
        'p_loss_pct': round(p_loss, 2),
        'est_ev': round(ev, 2),
        'net_roi_pct': round(((ev - 49.0) / 49.0) * 100, 1)
    }

print("=== 100,000 MONTE CARLO SIMULATION RESULTS ===")
for name, r in results.items():
    print(f"\n{name}:")
    print(f"  Mean: {r['mean']} | Median: {r['median']} | P90: {r['p90']} | P99: {r['p99']}")
    print(f"  P(>600): {r['p_gt_600']}% | P(>700): {r['p_gt_700']}% | P(>800): {r['p_gt_800']}%")
    print(f"  Projected Duplicates: {r['projected_duplicates']} | Cash Rate: {r['p_in_money_pct']}% | Risk of Loss: {r['p_loss_pct']}%")
    print(f"  Est EV: Rs {r['est_ev']} | Net ROI: {r['net_roi_pct']}%")

with open('gl_engine/data/mc_simulation_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

